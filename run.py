#!/usr/bin/env python3
"""
Запуск Telegram бота "Орёл или решка"

Этот скрипт запускает бота с обработкой ошибок и логированием.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

try:
    from bot import main
    from config import BOT_TOKEN
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что все файлы проекта находятся в одной директории")
    sys.exit(1)

def setup_logging():
    """Настройка логирования"""
    # Создаем директорию для логов если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "bot.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_environment():
    """Проверка окружения"""
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не установлен!")
        print("Создайте файл .env и добавьте в него BOT_TOKEN=your_token_here")
        return False
    
    if BOT_TOKEN == "your_bot_token_here":
        print("❌ Ошибка: BOT_TOKEN не настроен!")
        print("Замените 'your_bot_token_here' на реальный токен бота в файле .env")
        return False
    
    return True

def main_wrapper():
    """Обертка для запуска бота с обработкой ошибок"""
    print("🚀 Запуск Telegram бота 'Орёл или решка'...")
    
    # Настраиваем логирование
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Проверяем окружение
    if not check_environment():
        sys.exit(1)
    
    logger.info("✅ Окружение проверено успешно")
    
    try:
        # Запускаем бота
        logger.info("🔄 Запуск бота...")
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
        print("\n👋 Бот остановлен. До свидания!")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}", exc_info=True)
        print(f"\n❌ Произошла ошибка: {e}")
        print("Проверьте логи в файле logs/bot.log")
        sys.exit(1)

if __name__ == "__main__":
    main_wrapper()