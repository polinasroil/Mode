#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Скрипт запуска (Bedrock протокол для телефона)
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_banner():
    """Вывод баннера сервера"""
    print("🎮" + "="*60 + "🎮")
    print("    Minecraft PE Server - Bedrock протокол для телефона")
    print("    Версия: 1.0.0")
    print("    Автор: Minecraft PE Server Team")
    print("🎮" + "="*60 + "🎮")
    print()

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Ошибка: Требуется Python 3.8 или выше")
        print(f"   Текущая версия: {sys.version}")
        return False
    
    print(f"✅ Python версия: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Проверка зависимостей"""
    required_modules = ['asyncio', 'socket', 'struct', 'logging', 'json', 'pathlib']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Отсутствуют модули: {', '.join(missing_modules)}")
        return False
    
    print("✅ Все необходимые модули доступны")
    return True

def check_ports():
    """Проверка доступности портов"""
    import socket
    
    # Проверка порта сервера (19132)
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_sock.bind(('0.0.0.0', 19132))
        test_sock.close()
        print("✅ Порт 19132 (сервер) доступен")
    except OSError:
        print("❌ Порт 19132 (сервер) занят")
        return False
    
    # Проверка порта веб-панели (8080)
    try:
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_sock.bind(('0.0.0.0', 8080))
        test_sock.close()
        print("✅ Порт 8080 (веб-панель) доступен")
    except OSError:
        print("❌ Порт 8080 (веб-панель) занят")
        return False
    
    return True

def check_directories():
    """Проверка и создание необходимых директорий"""
    required_dirs = ['config', 'worlds', 'logs', 'backups', 'plugins', 'web-panel']
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"📁 Создана директория: {dir_name}")
        else:
            print(f"📁 Директория существует: {dir_name}")
    
    return True

def check_config():
    """Проверка конфигурации"""
    config_file = Path("config/server.properties")
    
    if not config_file.exists():
        print("❌ Файл конфигурации не найден")
        print("   Создаю конфигурацию по умолчанию...")
        
        # Создание конфигурации по умолчанию
        default_config = """# Minecraft PE Server Configuration (Bedrock протокол для телефона)
# Автор: Minecraft PE Server Team
# Версия: 1.0.0

# Основные настройки сервера
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
auto-save=true
auto-save-interval=300

# Bedrock протокол (Minecraft PE на телефоне)
bedrock-protocol-version=662
bedrock-game-version=1.20.50
bedrock-allow-cheats=false
bedrock-texturepack-required=false

# Настройки производительности
tps=20
chunk-load-distance=8
max-chunk-loads-per-tick=4

# Настройки логирования
log-level=INFO
log-file=server.log
"""
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(default_config)
        
        print("✅ Конфигурация создана")
    else:
        print("✅ Файл конфигурации найден")
    
    return True

def start_server():
    """Запуск основного сервера"""
    print("\n🚀 Запуск Minecraft PE сервера...")
    
    try:
        # Импорт и запуск сервера
        from server.main import MinecraftPEServer
        import asyncio
        
        server = MinecraftPEServer()
        asyncio.run(server.start())
        
    except KeyboardInterrupt:
        print("\n⏹️ Сервер остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска сервера: {e}")
        return False
    
    return True

def start_web_panel():
    """Запуск веб-панели"""
    print("\n🌐 Запуск веб-панели...")
    
    try:
        web_panel_path = Path("web-panel/app.py")
        if web_panel_path.exists():
            # Запуск веб-панели в отдельном процессе
            subprocess.Popen([sys.executable, str(web_panel_path)], 
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ Веб-панель запущена на http://localhost:8080")
            return True
        else:
            print("⚠️ Веб-панель не найдена")
            return False
    except Exception as e:
        print(f"❌ Ошибка запуска веб-панели: {e}")
        return False

def main():
    """Главная функция"""
    print_banner()
    
    print("🔍 Проверка системы...")
    
    # Проверка версии Python
    if not check_python_version():
        sys.exit(1)
    
    # Проверка зависимостей
    if not check_dependencies():
        sys.exit(1)
    
    # Проверка портов
    if not check_ports():
        print("\n💡 Решение:")
        print("   - Остановите другие сервисы, использующие порты 19132 или 8080")
        print("   - Или измените порты в конфигурации")
        sys.exit(1)
    
    # Проверка директорий
    if not check_directories():
        sys.exit(1)
    
    # Проверка конфигурации
    if not check_config():
        sys.exit(1)
    
    print("\n✅ Все проверки пройдены успешно!")
    
    # Запуск веб-панели
    start_web_panel()
    
    # Небольшая задержка для запуска веб-панели
    time.sleep(2)
    
    # Запуск основного сервера
    start_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Запуск прерван пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)