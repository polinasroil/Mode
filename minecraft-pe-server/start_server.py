#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Скрипт запуска
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import asyncio
import logging
import os
import sys
import time
from pathlib import Path

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

async def check_dependencies():
    """Проверка зависимостей"""
    logger.info("🔍 Проверка зависимостей...")
    
    required_modules = [
        'asyncio',
        'socket',
        'struct',
        'json',
        'pathlib',
        'datetime'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"❌ Отсутствуют модули: {', '.join(missing_modules)}")
        return False
    
    logger.info("✅ Все зависимости доступны")
    return True

async def check_ports():
    """Проверка доступности портов"""
    logger.info("🔍 Проверка портов...")
    
    import socket
    
    ports_to_check = [
        ('server_port', 19132),
        ('web_panel_port', 8080)
    ]
    
    for port_name, port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('0.0.0.0', port))
            sock.close()
            logger.info(f"✅ Порт {port} ({port_name}) доступен")
        except OSError:
            logger.warning(f"⚠️ Порт {port} ({port_name}) занят")
    
    return True

async def check_directories():
    """Проверка и создание необходимых директорий"""
    logger.info("🔍 Проверка директорий...")
    
    directories = [
        'config',
        'worlds',
        'logs',
        'backups',
        'plugins'
    ]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Создана директория: {directory}")
        else:
            logger.debug(f"📁 Директория существует: {directory}")
    
    return True

async def check_config():
    """Проверка конфигурации"""
    logger.info("🔍 Проверка конфигурации...")
    
    config_file = Path("config/server.properties")
    
    if not config_file.exists():
        logger.warning("⚠️ Файл конфигурации не найден, создаю по умолчанию...")
        
        default_config = """# Minecraft PE Server Configuration
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

# Основные настройки
server-name=Minecraft PE Server
server-port=19132
max-players=20

# Настройки мира
level-name=world
level-type=default
level-seed=0
gamemode=survival
difficulty=normal
spawn-protection=16

# Игровые настройки
hardcore=false
pvp=true

# Системные настройки
backup-interval=3600
"""
        
        config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(default_config)
        
        logger.info("✅ Файл конфигурации создан")
    else:
        logger.info("✅ Файл конфигурации найден")
    
    return True

async def start_server():
    """Запуск сервера"""
    logger.info("🚀 Запуск Minecraft PE Server...")
    
    try:
        # Импорт основного сервера
        from server.main import MinecraftPEServer
        
        # Создание экземпляра сервера
        server = MinecraftPEServer()
        
        # Запуск сервера
        await server.start()
        
    except ImportError as e:
        logger.error(f"❌ Ошибка импорта модулей: {e}")
        logger.error("Убедитесь, что все файлы сервера находятся в правильных местах")
        return False
    except Exception as e:
        logger.error(f"❌ Критическая ошибка запуска сервера: {e}")
        return False
    
    return True

async def start_web_panel():
    """Запуск веб-панели"""
    logger.info("🌐 Запуск веб-панели...")
    
    try:
        # Проверка наличия веб-панели
        web_panel_path = Path("web-panel/app.py")
        if not web_panel_path.exists():
            logger.warning("⚠️ Веб-панель не найдена, пропускаю запуск")
            return True
        
        # Запуск веб-панели в отдельном процессе
        import subprocess
        
        web_process = subprocess.Popen([
            sys.executable, str(web_panel_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        logger.info(f"✅ Веб-панель запущена (PID: {web_process.pid})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска веб-панели: {e}")
        return False

async def main():
    """Главная функция"""
    logger.info("🎮 Minecraft PE Server - Запуск")
    logger.info("=" * 50)
    
    try:
        # Проверки перед запуском
        if not await check_dependencies():
            return 1
        
        if not await check_directories():
            return 1
        
        if not await check_config():
            return 1
        
        if not await check_ports():
            logger.warning("⚠️ Некоторые порты заняты, но продолжаю запуск")
        
        # Запуск веб-панели в фоне
        web_panel_task = asyncio.create_task(start_web_panel())
        
        # Небольшая задержка для запуска веб-панели
        await asyncio.sleep(2)
        
        # Запуск основного сервера
        if not await start_server():
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("⏹️ Запуск прерван пользователем")
        return 1
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return 1

if __name__ == "__main__":
    try:
        # Проверка версии Python
        if sys.version_info < (3, 8):
            logger.error("❌ Требуется Python 3.8 или выше")
            sys.exit(1)
        
        # Запуск
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("⏹️ Запуск остановлен")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)