#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Основной файл (исправленная версия)
Автор: Minecraft PE Server Team
Версия: 2.0.1
Интеграция всех протоколов: RakNet + Bedrock + Сжатие + Чанки
"""

import asyncio
import logging
import time
import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Импорт всех модулей
from server.raknet_protocol import RakNetProtocol
from server.bedrock_protocol_v2 import BedrockProtocolV2
from server.compression import AdaptiveCompression
from server.chunk_system import ChunkManager

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Player:
    """Игрок на сервере"""
    username: str
    uuid: str
    ip_address: str
    join_time: datetime
    last_seen: datetime
    gamemode: str
    spawn_x: float
    spawn_y: float
    spawn_z: float
    health: float = 20.0
    food: float = 20.0
    experience: float = 0.0
    level: int = 0
    
    def to_dict(self):
        return asdict(self)

@dataclass
class World:
    """Мир Minecraft"""
    name: str
    seed: int
    spawn_x: float
    spawn_y: float
    spawn_z: float
    time: int = 0
    weather: int = 0
    difficulty: str = "easy"
    
    def to_dict(self):
        return {
            'name': self.name,
            'seed': self.seed,
            'spawn_x': self.spawn_x,
            'spawn_y': self.spawn_y,
            'spawn_z': self.spawn_z,
            'time': self.time,
            'weather': self.weather,
            'difficulty': self.difficulty
        }

class MinecraftPEServer:
    """Основной сервер Minecraft PE"""
    
    def __init__(self, config_path: str = 'config/server.properties'):
        self.config_path = config_path
        self.config = {}
        self.players: Dict[str, Player] = {}
        self.max_players = 20
        self.worlds: Dict[str, World] = {}  # Изменено на World объекты
        self.running = False
        
        # Инициализация протоколов
        self.raknet_protocol = None
        self.bedrock_protocol = None
        self.compression = None
        self.chunk_manager = None
        
        logger.info("Minecraft PE Server инициализируется...")
    
    async def start(self):
        """Запуск сервера"""
        try:
            # Загрузка конфигурации
            await self.load_config()
            
            # Инициализация систем
            await self.initialize_systems()
            
            # Запуск протоколов
            await self.start_protocols()
            
            self.running = True
            logger.info("✅ Minecraft PE Server успешно запущен!")
            
            # Основной цикл сервера
            await self.main_loop()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска сервера: {e}")
            raise
    
    async def load_config(self):
        """Загрузка конфигурации"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                self.config[key.strip()] = value.strip()
            
            # Значения по умолчанию
            defaults = {
                'server-name': 'Minecraft PE Server v2.0',
                'server-port': '19132',
                'max-players': '20',
                'gamemode': 'survival',
                'difficulty': 'easy',
                'level-seed': '0',
                'level-type': 'default',
                'bedrock-protocol-version': '662',
                'bedrock-game-version': '1.20.50'
            }
            
            for key, value in defaults.items():
                if key not in self.config:
                    self.config[key] = value
            
            # Создание конфигурации если файл не существует
            if not os.path.exists(self.config_path):
                await self.create_default_config()
            
            logger.info("✅ Конфигурация загружена успешно")
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки конфигурации: {e}")
            raise
    
    async def create_default_config(self):
        """Создание конфигурации по умолчанию"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            config_content = """# Minecraft PE Server Configuration
# Автоматически создано

server-name=Minecraft PE Server v2.0
server-port=19132
max-players=20
gamemode=survival
difficulty=easy
level-seed=0
level-type=default
bedrock-protocol-version=662
bedrock-game-version=1.20.50

# Дополнительные настройки
enable-command-block=true
allow-flight=false
spawn-protection=16
view-distance=10
tick-rate=20
"""
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            logger.info("✅ Создана конфигурация по умолчанию")
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания конфигурации: {e}")
    
    async def initialize_systems(self):
        """Инициализация всех систем"""
        try:
            # Система сжатия
            self.compression = AdaptiveCompression()
            logger.info("✅ Система сжатия инициализирована")
            
            # Менеджер чанков
            world_seed = int(self.config.get('level-seed', '0'))
            self.chunk_manager = ChunkManager(world_seed)
            logger.info("✅ Менеджер чанков инициализирован")
            
            # Создание мира
            await self.create_world()
            logger.info("✅ Мир создан")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации систем: {e}")
            raise
    
    async def create_world(self):
        """Создание мира"""
        try:
            world_name = 'world'
            world_seed = int(self.config.get('level-seed', '0'))
            
            # Создание мира с чанками
            world = World(
                name=world_name,
                seed=world_seed,
                spawn_x=0.0,
                spawn_y=64.0,
                spawn_z=0.0,
                time=0,
                weather=0,
                difficulty=self.config.get('difficulty', 'easy')
            )
            
            self.worlds[world_name] = world
            
            # Загрузка начальных чанков
            self.chunk_manager.load_chunk(0, 0)  # Центральный чанк
            self.chunk_manager.load_chunk(-1, 0)  # Соседние чанки
            self.chunk_manager.load_chunk(1, 0)
            self.chunk_manager.load_chunk(0, -1)
            self.chunk_manager.load_chunk(0, 1)
            
            logger.info(f"✅ Мир '{world_name}' инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания мира: {e}")
            raise
    
    async def start_protocols(self):
        """Запуск всех протоколов"""
        try:
            # RakNet протокол
            self.raknet_protocol = RakNetProtocol(self)
            await self.raknet_protocol.start(port=int(self.config.get('server-port', '19132')))
            logger.info("✅ RakNet протокол запущен")
            
            # Bedrock протокол
            self.bedrock_protocol = BedrockProtocolV2(self)
            await self.bedrock_protocol.start(port=int(self.config.get('server-port', '19132')))
            logger.info("✅ Bedrock протокол запущен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска протоколов: {e}")
            raise
    
    async def main_loop(self):
        """Основной цикл сервера"""
        try:
            logger.info("🔄 Основной цикл сервера запущен")
            
            while self.running:
                try:
                    # Обновление времени мира
                    await self.update_world_time()
                    
                    # Обработка игроков
                    await self.process_players()
                    
                    # Очистка отключенных игроков
                    await self.cleanup_disconnected_players()
                    
                    # Небольшая задержка
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка в основном цикле: {e}")
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            logger.info("⏹️ Получен сигнал остановки")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка в основном цикле: {e}")
        finally:
            await self.stop()
    
    async def update_world_time(self):
        """Обновление времени мира"""
        try:
            for world in self.worlds.values():
                world.time = (world.time + 1) % 24000
                
        except Exception as e:
            logger.error(f"❌ Ошибка обновления времени мира: {e}")
    
    async def process_players(self):
        """Обработка игроков"""
        try:
            current_time = time.time()
            
            for player in self.players.values():
                # Обновление времени последнего появления
                player.last_seen = datetime.fromtimestamp(current_time)
                
                # Проверка активности
                if current_time - player.join_time.timestamp() > 300:  # 5 минут
                    logger.info(f"Игрок {player.username} неактивен более 5 минут")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки игроков: {e}")
    
    async def cleanup_disconnected_players(self):
        """Очистка отключенных игроков"""
        try:
            current_time = time.time()
            players_to_remove = []
            
            for username, player in self.players.items():
                # Проверка таймаута (10 минут без активности)
                if current_time - player.last_seen.timestamp() > 600:
                    players_to_remove.append(username)
            
            # Удаление отключенных игроков
            for username in players_to_remove:
                await self.player_leave(username)
                logger.info(f"Игрок {username} удален из-за неактивности")
                
        except Exception as e:
            logger.error(f"❌ Ошибка очистки игроков: {e}")
    
    async def player_join(self, username: str, ip_address: str) -> Player:
        """Подключение игрока к серверу"""
        try:
            # Проверяем, не подключен ли уже игрок с таким IP
            for existing_player in self.players.values():
                if existing_player.ip_address == ip_address:
                    # Отключаем существующего игрока
                    logger.info(f"Отключаем существующего игрока {existing_player.username} для нового подключения")
                    await self.player_leave(existing_player.username)
                    break
            
            if len(self.players) >= self.max_players:
                raise Exception("Сервер переполнен")
            
            if username in self.players:
                # Если имя пользователя занято, добавляем случайный суффикс
                import random
                username = f"{username}_{random.randint(1000, 9999)}"
                logger.info(f"Имя пользователя изменено на: {username}")
            
            # Получаем координаты спавна из мира
            world = list(self.worlds.values())[0]
            player = Player(
                username=username,
                uuid=str(hash(username)),  # Простой UUID
                ip_address=ip_address,
                join_time=datetime.now(),
                last_seen=datetime.now(),
                gamemode=self.config.get('gamemode', 'survival'),
                spawn_x=world.spawn_x,
                spawn_y=world.spawn_y,
                spawn_z=world.spawn_z
            )
            
            self.players[username] = player
            logger.info(f"✅ Игрок {username} подключился к серверу (IP: {ip_address})")
            
            return player
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения игрока {username}: {e}")
            raise
    
    async def player_leave(self, username: str):
        """Отключение игрока от сервера"""
        try:
            if username in self.players:
                player = self.players[username]
                logger.info(f"👋 Игрок {username} отключился от сервера")
                
                # Удаление игрока
                del self.players[username]
                
        except Exception as e:
            logger.error(f"❌ Ошибка отключения игрока {username}: {e}")
    
    async def send_message_to_player(self, username: str, message: str):
        """Отправка сообщения игроку"""
        try:
            if username in self.players:
                player = self.players[username]
                
                # Отправка через Bedrock протокол
                if self.bedrock_protocol:
                    # Находим сессию игрока
                    for session in self.bedrock_protocol.sessions.values():
                        if session.username == username:
                            await self.bedrock_protocol.send_packet(
                                0x09,  # ID_TEXT
                                message.encode('utf-8'),
                                session.address
                            )
                            break
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения игроку {username}: {e}")
    
    async def broadcast_message(self, message: str):
        """Отправка сообщения всем игрокам"""
        try:
            for username in list(self.players.keys()):
                await self.send_message_to_player(username, message)
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения всем игрокам: {e}")
    
    async def stop(self):
        """Остановка сервера"""
        try:
            self.running = False
            
            # Остановка протоколов
            if self.raknet_protocol:
                await self.raknet_protocol.stop()
            
            if self.bedrock_protocol:
                await self.bedrock_protocol.stop()
            
            logger.info("🛑 Minecraft PE Server остановлен")
            
        except Exception as e:
            logger.error(f"❌ Ошибка остановки сервера: {e}")
    
    def get_server_info(self) -> dict:
        """Получение информации о сервере"""
        try:
            return {
                'server_name': self.config.get('server-name', 'Unknown'),
                'server_port': self.config.get('server-port', '19132'),
                'max_players': self.max_players,
                'current_players': len(self.players),
                'worlds': len(self.worlds),
                'chunks': self.chunk_manager.get_chunk_info() if self.chunk_manager else {},
                'compression': self.compression.get_compression_stats() if self.compression else {},
                'raknet': self.raknet_protocol.get_server_info() if self.raknet_protocol else {},
                'bedrock': self.bedrock_protocol.get_server_info() if self.bedrock_protocol else {},
                'uptime': time.time() - getattr(self, '_start_time', time.time())
            }
        except Exception as e:
            logger.error(f"❌ Ошибка получения информации о сервере: {e}")
            return {}

async def main():
    """Главная функция"""
    try:
        # Создание и запуск сервера
        server = MinecraftPEServer()
        server._start_time = time.time()
        
        # Запуск сервера
        await server.start()
        
    except KeyboardInterrupt:
        logger.info("⏹️ Сервер остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    # Запуск сервера
    asyncio.run(main())