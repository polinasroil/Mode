#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Основной сервер
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import asyncio
import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Set

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

# Импорт модулей
try:
    from .raknet import RakNetProtocol
    from .world import World, WorldGenerator
except ImportError:
    from raknet import RakNetProtocol
    from world import World, WorldGenerator

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Player:
    """Класс игрока"""
    username: str
    uuid: str
    ip_address: str
    join_time: datetime
    last_seen: datetime
    gamemode: str = "survival"
    health: float = 20.0
    hunger: float = 20.0
    experience: int = 0
    level: int = 0
    permissions: List[str] = None
    online: bool = True
    spawn_x: float = 0.0
    spawn_y: float = 64.0
    spawn_z: float = 0.0
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = ["player"]

class MinecraftPEServer:
    """Основной класс сервера Minecraft PE"""
    
    def __init__(self, config_path: str = "config/server.properties"):
        self.config_path = config_path
        self.config = self.load_config()
        self.running = False
        self.players: Dict[str, Player] = {}
        self.worlds: Dict[str, World] = {}
        self.plugins: List[str] = []
        self.start_time = None
        
        # Преобразование строковых значений в правильные типы
        self.max_players = int(self.config.get('max-players', '20'))
        self.server_name = self.config.get('server-name', 'Minecraft PE Server')
        self.server_port = int(self.config.get('server-port', '19132'))
        
        # Статистика сервера
        self.stats = {
            'total_players': 0,
            'peak_players': 0,
            'uptime': 0,
            'tps': 20.0,
            'memory_usage': 0,
            'cpu_usage': 0
        }
        
        # Инициализация мира по умолчанию
        self.init_default_world()
        
        # Загрузка плагинов
        self.load_plugins()
        
        # Инициализация RakNet протокола
        self.network = RakNetProtocol(self)
        
        logger.info(f"Сервер {self.server_name} инициализирован")
    
    def load_config(self) -> Dict:
        """Загрузка конфигурации сервера"""
        try:
            config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip()] = value.strip()
            
            # Значения по умолчанию
            defaults = {
                'server-name': 'Minecraft PE Server',
                'server-port': '19132',
                'max-players': '20',
                'gamemode': 'survival',
                'difficulty': 'normal',
                'level-name': 'world',
                'level-type': 'default',
                'level-seed': '0',
                'spawn-protection': '16',
                'hardcore': 'false',
                'pvp': 'true'
            }
            
            # Применение значений по умолчанию для отсутствующих ключей
            for key, value in defaults.items():
                if key not in config:
                    config[key] = value
            
            logger.info("Конфигурация загружена успешно")
            return config
        except Exception as e:
            logger.error(f"Ошибка загрузки конфигурации: {e}")
            # Возвращаем значения по умолчанию при ошибке
            return {
                'server-name': 'Minecraft PE Server',
                'server-port': '19132',
                'max-players': '20',
                'gamemode': 'survival',
                'difficulty': 'normal',
                'level-name': 'world',
                'level-type': 'default',
                'level-seed': '0',
                'spawn-protection': '16',
                'hardcore': 'false',
                'pvp': 'true'
            }
    
    def init_default_world(self):
        """Инициализация мира по умолчанию"""
        try:
            world_name = self.config.get('level-name', 'world')
            world_seed = int(self.config.get('level-seed', '0'))
            world_type = self.config.get('level-type', 'default')
            difficulty = self.config.get('difficulty', 'normal')
            gamemode = self.config.get('gamemode', 'survival')
            hardcore = self.config.get('hardcore', 'false').lower() == 'true'
            pvp = self.config.get('pvp', 'true').lower() == 'true'
            
            # Создание мира с новой системой
            default_world = World(
                name=world_name,
                seed=world_seed,
                world_type=world_type
            )
            
            # Установка дополнительных параметров
            default_world.difficulty = difficulty
            default_world.gamemode = gamemode
            default_world.hardcore = hardcore
            default_world.pvp = pvp
            
            self.worlds[default_world.name] = default_world
            logger.info(f"Мир '{default_world.name}' инициализирован")
            
        except Exception as e:
            logger.error(f"Ошибка инициализации мира: {e}")
            # Создаем мир по умолчанию при ошибке
            default_world = World(
                name='world',
                seed=0,
                world_type='default'
            )
            self.worlds[default_world.name] = default_world
    
    def load_plugins(self):
        """Загрузка плагинов"""
        try:
            plugins_dir = Path("plugins")
            if plugins_dir.exists():
                for plugin_file in plugins_dir.glob("*.py"):
                    try:
                        plugin_name = plugin_file.stem
                        self.plugins.append(plugin_name)
                        logger.info(f"Плагин '{plugin_name}' загружен")
                    except Exception as e:
                        logger.error(f"Ошибка загрузки плагина {plugin_file}: {e}")
        except Exception as e:
            logger.error(f"Ошибка загрузки плагинов: {e}")
    
    async def start(self):
        """Запуск сервера"""
        if self.running:
            logger.warning("Сервер уже запущен")
            return
        
        self.running = True
        self.start_time = datetime.now()
        logger.info(f"Сервер {self.server_name} запускается...")
        
        # Загрузка/генерация миров
        await self.load_worlds()
        
        # Запуск RakNet протокола
        try:
            await self.network.start(port=self.server_port)
            logger.info(f"RakNet протокол запущен на порту {self.server_port}")
        except Exception as e:
            logger.error(f"Ошибка запуска RakNet протокола: {e}")
            raise
        
        # Запуск основных задач
        tasks = [
            asyncio.create_task(self.server_loop()),
            asyncio.create_task(self.monitoring_loop()),
            asyncio.create_task(self.backup_loop()),
            asyncio.create_task(self.cleanup_inactive_players()),
            asyncio.create_task(self.world_maintenance_loop())
        ]
        
        try:
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            logger.info("Получен сигнал остановки")
        finally:
            await self.stop()
    
    async def load_worlds(self):
        """Загрузка всех миров"""
        logger.info("Загрузка миров...")
        
        for world_name, world in self.worlds.items():
            try:
                await world.load_world()
                logger.info(f"Мир '{world_name}' загружен")
            except Exception as e:
                logger.error(f"Ошибка загрузки мира '{world_name}': {e}")
                # Попытка генерации нового мира
                try:
                    await world.generate_world()
                    logger.info(f"Мир '{world_name}' сгенерирован заново")
                except Exception as e2:
                    logger.error(f"Критическая ошибка генерации мира '{world_name}': {e2}")
    
    async def stop(self):
        """Остановка сервера"""
        if not self.running:
            return
        
        logger.info("Остановка сервера...")
        self.running = False
        
        # Остановка RakNet протокола
        try:
            await self.network.stop()
        except Exception as e:
            logger.error(f"Ошибка остановки RakNet протокола: {e}")
        
        # Отключение всех игроков
        for player in list(self.players.values()):
            await self.disconnect_player(player)
        
        # Сохранение миров
        await self.save_worlds()
        
        # Сохранение статистики
        await self.save_stats()
        
        logger.info("Сервер остановлен")
    
    async def server_loop(self):
        """Основной цикл сервера"""
        tick_rate = 1.0 / 20.0  # 20 TPS
        
        while self.running:
            start_time = time.time()
            
            try:
                # Обновление игроков
                await self.update_players()
                
                # Обновление миров
                await self.update_worlds()
                
                # Обновление плагинов
                await self.update_plugins()
                
                # Обновление статистики
                self.update_stats()
                
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
            
            # Поддержание TPS
            elapsed = time.time() - start_time
            if elapsed < tick_rate:
                await asyncio.sleep(tick_rate - elapsed)
    
    async def monitoring_loop(self):
        """Цикл мониторинга"""
        while self.running:
            try:
                # Мониторинг ресурсов
                self.monitor_resources()
                
                # Проверка состояния сервера
                await self.health_check()
                
                await asyncio.sleep(30)  # Каждые 30 секунд
                
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
    
    async def backup_loop(self):
        """Цикл резервного копирования"""
        backup_interval = int(self.config.get('backup-interval', '3600'))
        
        while self.running:
            try:
                await asyncio.sleep(backup_interval)
                
                if self.running:
                    await self.create_backup()
                    
            except Exception as e:
                logger.error(f"Ошибка в цикле резервного копирования: {e}")
    
    async def world_maintenance_loop(self):
        """Цикл обслуживания миров"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Каждые 5 минут
                
                # Автосохранение миров
                await self.auto_save_worlds()
                
                # Очистка неиспользуемых чанков
                await self.cleanup_unused_chunks()
                
            except Exception as e:
                logger.error(f"Ошибка в цикле обслуживания миров: {e}")
    
    async def cleanup_inactive_players(self):
        """Очистка неактивных игроков"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Каждую минуту
                
                current_time = datetime.now()
                inactive_players = []
                
                for username, player in self.players.items():
                    # Проверяем активность игрока (5 минут)
                    if (current_time - player.last_seen).total_seconds() > 300:
                        inactive_players.append(username)
                
                # Отключаем неактивных игроков
                for username in inactive_players:
                    logger.info(f"Отключение неактивного игрока {username}")
                    await self.player_leave(username)
                    
            except Exception as e:
                logger.error(f"Ошибка в цикле очистки игроков: {e}")
    
    async def update_players(self):
        """Обновление состояния игроков"""
        current_time = datetime.now()
        
        for player in self.players.values():
            # Обновление времени последней активности
            player.last_seen = current_time
            
            # Проверка здоровья и голода
            if player.health <= 0:
                await self.player_death(player)
    
    async def update_worlds(self):
        """Обновление миров"""
        for world in self.worlds.values():
            # Обновление времени
            world.update_time()
            
            # Обновление погоды
            if world.time % 12000 == 0:  # Каждые 10 минут
                world.weather = self.get_random_weather()
    
    async def update_plugins(self):
        """Обновление плагинов"""
        # Здесь будет логика обновления плагинов
        pass
    
    def update_stats(self):
        """Обновление статистики сервера"""
        if self.start_time:
            self.stats['uptime'] = (datetime.now() - self.start_time).total_seconds()
        
        self.stats['total_players'] = len(self.players)
        
        if len(self.players) > self.stats['peak_players']:
            self.stats['peak_players'] = len(self.players)
    
    def monitor_resources(self):
        """Мониторинг ресурсов системы"""
        try:
            import psutil
            
            process = psutil.Process()
            self.stats['memory_usage'] = process.memory_info().rss / 1024 / 1024  # MB
            self.stats['cpu_usage'] = process.cpu_percent()
            
        except ImportError:
            # psutil не установлен
            pass
    
    async def health_check(self):
        """Проверка состояния сервера"""
        # Проверка доступности портов
        # Проверка свободного места на диске
        # Проверка состояния сети
        pass
    
    async def create_backup(self):
        """Создание резервной копии"""
        try:
            backup_dir = Path("backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            
            # Создание резервной копии миров
            for world_name, world in self.worlds.items():
                world_backup_dir = backup_dir / backup_name / world_name
                world_backup_dir.mkdir(parents=True, exist_ok=True)
                
                # Копирование файлов мира
                if world.world_file.exists():
                    import shutil
                    shutil.copy2(world.world_file, world_backup_dir)
                
                # Копирование чанков
                if world.chunks_dir.exists():
                    shutil.copytree(world.chunks_dir, world_backup_dir / "chunks", dirs_exist_ok=True)
            
            logger.info(f"Резервная копия '{backup_name}' создана")
            
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
    
    async def auto_save_worlds(self):
        """Автоматическое сохранение миров"""
        for world_name, world in self.worlds.items():
            try:
                await world.save_world()
                logger.debug(f"Мир '{world_name}' автосохранен")
            except Exception as e:
                logger.error(f"Ошибка автосохранения мира '{world_name}': {e}")
    
    async def cleanup_unused_chunks(self):
        """Очистка неиспользуемых чанков"""
        for world_name, world in self.worlds.items():
            try:
                # Удаляем чанки, которые не загружены более 30 минут
                current_time = datetime.now()
                chunks_to_remove = []
                
                for chunk_coords, chunk in world.chunks.items():
                    if chunk_coords not in world.loaded_chunks:
                        # Проверяем время последнего использования
                        if (current_time - chunk.last_modified).total_seconds() > 1800:
                            chunks_to_remove.append(chunk_coords)
                
                # Удаляем неиспользуемые чанки
                for chunk_coords in chunks_to_remove:
                    del world.chunks[chunk_coords]
                
                if chunks_to_remove:
                    logger.debug(f"Удалено {len(chunks_to_remove)} неиспользуемых чанков в мире '{world_name}'")
                    
            except Exception as e:
                logger.error(f"Ошибка очистки чанков в мире '{world_name}': {e}")
    
    async def player_join(self, username: str, ip_address: str) -> Player:
        """Подключение игрока к серверу"""
        if len(self.players) >= self.max_players:
            raise Exception("Сервер переполнен")
        
        if username in self.players:
            raise Exception("Игрок уже подключен")
        
        # Получаем координаты спавна из мира
        world = list(self.worlds.values())[0]
        
        player = Player(
            username=username,
            uuid=self.generate_uuid(username),
            ip_address=ip_address,
            join_time=datetime.now(),
            last_seen=datetime.now(),
            online=True,
            spawn_x=float(world.spawn_x),
            spawn_y=float(world.spawn_y),
            spawn_z=float(world.spawn_z)
        )
        
        self.players[username] = player
        logger.info(f"Игрок {username} подключился к серверу")
        
        return player
    
    async def player_leave(self, username: str):
        """Отключение игрока от сервера"""
        if username in self.players:
            player = self.players[username]
            await self.disconnect_player(player)
            del self.players[username]
            logger.info(f"Игрок {username} отключился от сервера")
    
    async def disconnect_player(self, player: Player):
        """Отключение игрока"""
        # Сохранение данных игрока
        await self.save_player_data(player)
        
        # Уведомление плагинов
        await self.notify_plugins('player_disconnect', player)
    
    async def player_death(self, player: Player):
        """Смерть игрока"""
        # Сброс здоровья и голода
        player.health = 20.0
        player.hunger = 20.0
        
        # Телепортация на спавн
        world = list(self.worlds.values())[0]  # Первый мир
        player.spawn_x = float(world.spawn_x)
        player.spawn_y = float(world.spawn_y)
        player.spawn_z = float(world.spawn_z)
        
        logger.info(f"Игрок {player.username} умер и возродился")
    
    def generate_uuid(self, username: str) -> str:
        """Генерация UUID для игрока"""
        import hashlib
        hash_obj = hashlib.md5(username.encode())
        return hash_obj.hexdigest()
    
    def get_random_weather(self) -> str:
        """Получение случайной погоды"""
        import random
        weathers = ["clear", "rain", "thunder"]
        return random.choice(weathers)
    
    async def save_worlds(self):
        """Сохранение всех миров"""
        for world_name, world in self.worlds.items():
            try:
                await world.save_world()
                logger.info(f"Мир '{world_name}' сохранен")
            except Exception as e:
                logger.error(f"Ошибка сохранения мира '{world_name}': {e}")
    
    async def save_player_data(self, player: Player):
        """Сохранение данных игрока"""
        try:
            # Здесь будет логика сохранения данных игрока
            pass
        except Exception as e:
            logger.error(f"Ошибка сохранения данных игрока {player.username}: {e}")
    
    async def save_stats(self):
        """Сохранение статистики"""
        try:
            stats_file = Path("server_stats.json")
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Ошибка сохранения статистики: {e}")
    
    async def notify_plugins(self, event: str, data: any):
        """Уведомление плагинов о событиях"""
        # Здесь будет логика уведомления плагинов
        pass
    
    def get_server_info(self) -> Dict:
        """Получение информации о сервере"""
        worlds_info = {}
        for world_name, world in self.worlds.items():
            worlds_info[world_name] = world.get_world_info()
        
        # Добавление информации о RakNet
        network_info = self.network.get_server_info() if hasattr(self, 'network') else {}
        
        return {
            'name': self.server_name,
            'version': '1.0.0',
            'players': {
                'online': len(self.players),
                'max': self.max_players,
                'list': [p.username for p in self.players.values()]
            },
            'worlds': worlds_info,
            'plugins': self.plugins,
            'stats': self.stats,
            'uptime': self.stats['uptime'],
            'network': network_info
        }
    
    async def broadcast_message(self, message: str):
        """Отправка сообщения всем игрокам"""
        if hasattr(self, 'network'):
            await self.network.broadcast_message(message)
    
    async def send_message_to_player(self, username: str, message: str):
        """Отправка сообщения конкретному игроку"""
        if hasattr(self, 'network'):
            # Находим клиента по имени пользователя
            for session in self.network.sessions.values():
                if session.state == "connected":
                    # Здесь нужно найти сессию по IP игрока
                    for player in self.players.values():
                        if player.username == username and player.ip_address == session.address[0]:
                            await self.network.send_minecraft_packet(0x09, message.encode('utf-8'), session)
                            break
    
    def get_world(self, world_name: str = None) -> Optional[World]:
        """Получение мира по имени"""
        if world_name is None:
            # Возвращаем первый мир
            return list(self.worlds.values())[0] if self.worlds else None
        return self.worlds.get(world_name)
    
    def get_block(self, x: int, y: int, z: int, world_name: str = None) -> Optional[any]:
        """Получение блока в мире"""
        world = self.get_world(world_name)
        if world:
            return world.get_block(x, y, z)
        return None
    
    def set_block(self, x: int, y: int, z: int, block_id: int, metadata: int = 0, world_name: str = None):
        """Установка блока в мире"""
        world = self.get_world(world_name)
        if world:
            world.set_block(x, y, z, block_id, metadata)
    
    def remove_block(self, x: int, y: int, z: int, world_name: str = None):
        """Удаление блока из мира"""
        world = self.get_world(world_name)
        if world:
            world.remove_block(x, y, z)

async def main():
    """Главная функция"""
    # Обработка сигналов
    def signal_handler(signum, frame):
        logger.info(f"Получен сигнал {signum}")
        asyncio.get_event_loop().stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создание и запуск сервера
    server = MinecraftPEServer()
    
    try:
        await server.start()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        sys.exit(1)