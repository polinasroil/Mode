#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Скрипт запуска (исправленная версия)
Автор: Minecraft PE Server Team
Версия: 2.0.1
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Добавляем текущую директорию в путь Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

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

async def check_dependencies():
    """Проверка зависимостей"""
    try:
        logger.info("🔍 Проверка зависимостей...")
        
        # Проверяем наличие всех необходимых модулей
        required_modules = [
            'server.raknet_protocol',
            'server.bedrock_protocol_v2',
            'server.compression',
            'server.chunk_system'
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
                logger.info(f"✅ {module}")
            except ImportError as e:
                missing_modules.append(module)
                logger.error(f"❌ {module}: {e}")
        
        if missing_modules:
            logger.error("❌ Отсутствуют необходимые модули!")
            return False
        
        logger.info("✅ Все зависимости установлены")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка проверки зависимостей: {e}")
        return False

async def create_directories():
    """Создание необходимых директорий"""
    try:
        logger.info("📁 Создание директорий...")
        
        directories = [
            'config',
            'worlds',
            'logs',
            'backups',
            'plugins'
        ]
        
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            logger.info(f"✅ Создана директория: {directory}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка создания директорий: {e}")
        return False

async def start_server():
    """Запуск сервера"""
    try:
        logger.info("🚀 Запуск Minecraft PE Server v2.0.1...")
        
        # Проверка зависимостей
        if not await check_dependencies():
            logger.error("❌ Невозможно запустить сервер из-за отсутствующих зависимостей")
            return False
        
        # Создание директорий
        if not await create_directories():
            logger.error("❌ Невозможно создать необходимые директории")
            return False
        
        # Импорт и запуск сервера
        from server.main_fixed import MinecraftPEServer
        
        server = MinecraftPEServer()
        server._start_time = asyncio.get_event_loop().time()
        
        logger.info("✅ Сервер инициализирован, запуск...")
        await server.start()
        
        return True
        
    except KeyboardInterrupt:
        logger.info("⏹️ Сервер остановлен пользователем")
        return True
    except Exception as e:
        logger.error(f"❌ Критическая ошибка запуска сервера: {e}")
        return False

def main():
    """Главная функция"""
    try:
        # Проверка версии Python
        if sys.version_info < (3, 8):
            logger.error("❌ Требуется Python 3.8 или выше")
            sys.exit(1)
        
        logger.info(f"🐍 Python {sys.version}")
        logger.info(f"📂 Рабочая директория: {os.getcwd()}")
        
        # Запуск сервера
        success = asyncio.run(start_server())
        
        if success:
            logger.info("✅ Сервер завершил работу успешно")
            sys.exit(0)
        else:
            logger.error("❌ Сервер завершил работу с ошибкой")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()