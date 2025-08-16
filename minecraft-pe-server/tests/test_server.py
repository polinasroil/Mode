#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для Minecraft PE Server
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Добавление пути к модулям сервера
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.main import MinecraftPEServer, Player, World

class TestPlayer:
    """Тесты для класса Player"""
    
    def test_player_creation(self):
        """Тест создания игрока"""
        player = Player(
            username="TestPlayer",
            uuid="test-uuid-123",
            ip_address="192.168.1.100",
            join_time=None,
            last_seen=None
        )
        
        assert player.username == "TestPlayer"
        assert player.uuid == "test-uuid-123"
        assert player.ip_address == "192.168.1.100"
        assert player.gamemode == "survival"
        assert player.health == 20.0
        assert player.hunger == 20.0
        assert player.experience == 0
        assert player.level == 0
        assert player.permissions == ["player"]
    
    def test_player_defaults(self):
        """Тест значений по умолчанию для игрока"""
        player = Player(
            username="TestPlayer",
            uuid="test-uuid",
            ip_address="192.168.1.100",
            join_time=None,
            last_seen=None,
            gamemode="creative",
            health=15.0,
            hunger=18.0,
            experience=100,
            level=5
        )
        
        assert player.gamemode == "creative"
        assert player.health == 15.0
        assert player.hunger == 18.0
        assert player.experience == 100
        assert player.level == 5

class TestWorld:
    """Тесты для класса World"""
    
    def test_world_creation(self):
        """Тест создания мира"""
        world = World(
            name="test_world",
            seed=12345,
            world_type="default"
        )
        
        assert world.name == "test_world"
        assert world.seed == 12345
        assert world.world_type == "default"
        assert world.spawn_x == 0
        assert world.spawn_y == 64
        assert world.spawn_z == 0
        assert world.time == 0
        assert world.weather == "clear"
        assert world.difficulty == "normal"
        assert world.gamemode == "survival"
        assert world.hardcore == False
        assert world.pvp == True
    
    def test_world_custom_values(self):
        """Тест создания мира с пользовательскими значениями"""
        world = World(
            name="custom_world",
            seed=54321,
            world_type="flat",
            spawn_x=100,
            spawn_y=80,
            spawn_z=200,
            time=12000,
            weather="rain",
            difficulty="hard",
            gamemode="creative",
            hardcore=True,
            pvp=False
        )
        
        assert world.name == "custom_world"
        assert world.seed == 54321
        assert world.world_type == "flat"
        assert world.spawn_x == 100
        assert world.spawn_y == 80
        assert world.spawn_z == 200
        assert world.time == 12000
        assert world.weather == "rain"
        assert world.difficulty == "hard"
        assert world.gamemode == "creative"
        assert world.hardcore == True
        assert world.pvp == False

class TestMinecraftPEServer:
    """Тесты для основного класса сервера"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Создание временной директории для конфигурации"""
        temp_dir = tempfile.mkdtemp()
        config_file = Path(temp_dir) / "server.properties"
        
        # Создание тестового конфигурационного файла
        config_content = """
# Test configuration
server-name=Test Server
server-port=19132
max-players=10
gamemode=survival
difficulty=normal
level-name=test_world
        """.strip()
        
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        yield str(config_file)
        
        # Очистка
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def server(self, temp_config_dir):
        """Создание экземпляра сервера для тестирования"""
        return MinecraftPEServer(temp_config_dir)
    
    def test_server_initialization(self, server):
        """Тест инициализации сервера"""
        assert server.config_path is not None
        assert server.running == False
        assert len(server.players) == 0
        assert len(server.worlds) == 1  # Один мир по умолчанию
        assert server.max_players == 10
        assert server.server_name == "Test Server"
        assert server.server_port == 19132
    
    def test_load_config(self, server):
        """Тест загрузки конфигурации"""
        config = server.config
        
        assert 'server-name' in config
        assert 'server-port' in config
        assert 'max-players' in config
        assert 'gamemode' in config
        assert 'difficulty' in config
        assert 'level-name' in config
        
        assert config['server-name'] == 'Test Server'
        assert config['server-port'] == '19132'
        assert config['max-players'] == '10'
        assert config['gamemode'] == 'survival'
        assert config['difficulty'] == 'normal'
        assert config['level-name'] == 'test_world'
    
    def test_init_default_world(self, server):
        """Тест инициализации мира по умолчанию"""
        assert len(server.worlds) == 1
        
        world = list(server.worlds.values())[0]
        assert world.name == "test_world"
        assert world.world_type == "default"
        assert world.difficulty == "normal"
        assert world.gamemode == "survival"
        assert world.hardcore == False
    
    def test_generate_uuid(self, server):
        """Тест генерации UUID"""
        uuid1 = server.generate_uuid("Player1")
        uuid2 = server.generate_uuid("Player2")
        uuid3 = server.generate_uuid("Player1")  # Тот же игрок
        
        assert uuid1 != uuid2  # Разные игроки - разные UUID
        assert uuid1 == uuid3  # Один игрок - один UUID
        assert len(uuid1) == 32  # MD5 hash длина
    
    def test_get_random_weather(self, server):
        """Тест получения случайной погоды"""
        weathers = set()
        
        # Получаем несколько значений погоды
        for _ in range(10):
            weather = server.get_random_weather()
            weathers.add(weather)
        
        # Проверяем, что все значения из допустимого списка
        valid_weathers = {"clear", "rain", "thunder"}
        assert weathers.issubset(valid_weathers)
    
    @pytest.mark.asyncio
    async def test_player_join_success(self, server):
        """Тест успешного подключения игрока"""
        player = await server.player_join("TestPlayer", "192.168.1.100")
        
        assert player.username == "TestPlayer"
        assert player.ip_address == "192.168.1.100"
        assert player.username in server.players
        assert len(server.players) == 1
    
    @pytest.mark.asyncio
    async def test_player_join_duplicate(self, server):
        """Тест подключения дублирующегося игрока"""
        # Первое подключение
        await server.player_join("TestPlayer", "192.168.1.100")
        
        # Попытка повторного подключения
        with pytest.raises(Exception, match="Игрок уже подключен"):
            await server.player_join("TestPlayer", "192.168.1.101")
    
    @pytest.mark.asyncio
    async def test_player_join_server_full(self, server):
        """Тест подключения при полном сервере"""
        # Заполняем сервер
        for i in range(10):
            await server.player_join(f"Player{i}", f"192.168.1.{i}")
        
        # Попытка подключения 11-го игрока
        with pytest.raises(Exception, match="Сервер переполнен"):
            await server.player_join("Player11", "192.168.1.11")
    
    @pytest.mark.asyncio
    async def test_player_leave(self, server):
        """Тест отключения игрока"""
        # Подключаем игрока
        await server.player_join("TestPlayer", "192.168.1.100")
        assert len(server.players) == 1
        
        # Отключаем игрока
        await server.player_leave("TestPlayer")
        assert len(server.players) == 0
    
    @pytest.mark.asyncio
    async def test_player_death(self, server):
        """Тест смерти игрока"""
        # Подключаем игрока
        player = await server.player_join("TestPlayer", "192.168.1.100")
        
        # Устанавливаем низкое здоровье
        player.health = 0
        
        # Вызываем смерть
        await server.player_death(player)
        
        # Проверяем, что здоровье восстановлено
        assert player.health == 20.0
        assert player.hunger == 20.0
    
    def test_get_server_info(self, server):
        """Тест получения информации о сервере"""
        info = server.get_server_info()
        
        assert 'name' in info
        assert 'version' in info
        assert 'players' in info
        assert 'worlds' in info
        assert 'plugins' in info
        assert 'stats' in info
        
        assert info['name'] == "Test Server"
        assert info['version'] == "1.0.0"
        assert info['players']['online'] == 0
        assert info['players']['max'] == 10
        assert len(info['worlds']) == 1
    
    @pytest.mark.asyncio
    async def test_server_start_stop(self, server):
        """Тест запуска и остановки сервера"""
        # Запуск сервера
        await server.start()
        assert server.running == True
        assert server.start_time is not None
        
        # Остановка сервера
        await server.stop()
        assert server.running == False
    
    def test_update_stats(self, server):
        """Тест обновления статистики"""
        # Инициализируем время запуска
        server.start_time = None
        
        # Обновляем статистику
        server.update_stats()
        
        assert server.stats['total_players'] == 0
        assert server.stats['peak_players'] == 0
        
        # Добавляем игрока
        server.players["TestPlayer"] = Mock()
        server.update_stats()
        
        assert server.stats['total_players'] == 1
        assert server.stats['peak_players'] == 1

# Тесты для проверки совместимости
class TestCompatibility:
    """Тесты совместимости"""
    
    def test_python_version(self):
        """Тест версии Python"""
        import sys
        version = sys.version_info
        
        # Проверяем, что Python 3.8+
        assert version.major == 3
        assert version.minor >= 8
    
    def test_required_modules(self):
        """Тест наличия необходимых модулей"""
        required_modules = [
            'asyncio',
            'json',
            'logging',
            'os',
            'signal',
            'sys',
            'time',
            'pathlib',
            'typing',
            'dataclasses',
            'datetime'
        ]
        
        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError:
                pytest.fail(f"Модуль {module_name} не найден")

# Тесты производительности
class TestPerformance:
    """Тесты производительности"""
    
    @pytest.mark.asyncio
    async def test_player_join_performance(self):
        """Тест производительности подключения игроков"""
        server = MinecraftPEServer()
        
        import time
        start_time = time.time()
        
        # Подключаем 100 игроков
        for i in range(100):
            await server.player_join(f"Player{i}", f"192.168.1.{i}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Проверяем, что подключение 100 игроков занимает менее 1 секунды
        assert duration < 1.0
        assert len(server.players) == 100
    
    def test_memory_usage(self):
        """Тест использования памяти"""
        server = MinecraftPEServer()
        
        # Проверяем, что сервер не потребляет слишком много памяти
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        # Сервер должен потреблять менее 100MB памяти
        assert memory_mb < 100

if __name__ == "__main__":
    # Запуск тестов
    pytest.main([__file__, "-v"])