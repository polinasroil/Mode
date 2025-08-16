#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Быстрый запуск
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        print(f"   Текущая версия: {sys.version}")
        return False
    return True

def check_dependencies():
    """Проверка зависимостей"""
    required_packages = ['flask', 'psutil']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Отсутствуют зависимости: {', '.join(missing_packages)}")
        print("   Установите их командой: pip install -r requirements.txt")
        return False
    
    return True

def setup_environment():
    """Настройка окружения"""
    print("🔧 Настройка окружения...")
    
    # Создание необходимых директорий
    directories = ['logs', 'backups', 'worlds', 'plugins', 'data']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    # Создание базовой конфигурации если не существует
    config_file = Path("config/server.properties")
    if not config_file.exists():
        print("   Создание базовой конфигурации...")
        config_file.parent.mkdir(exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("""# Minecraft PE Server - Базовая конфигурация
server-name=Minecraft PE Server
server-port=19132
max-players=20
gamemode=survival
difficulty=normal
level-name=world
""")
    
    print("✅ Окружение настроено")

def start_server():
    """Запуск сервера"""
    print("🚀 Запуск Minecraft PE Server...")
    
    try:
        # Запуск основного сервера
        server_process = subprocess.Popen([
            sys.executable, "server/main.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Сервер запущен (PID: {})".format(server_process.pid))
        
        # Ожидание запуска сервера
        time.sleep(3)
        
        # Запуск веб-панели
        print("🌐 Запуск веб-панели...")
        web_panel_process = subprocess.Popen([
            sys.executable, "web-panel/app.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("✅ Веб-панель запущена (PID: {})".format(web_panel_process.pid))
        
        print("\n🎉 Minecraft PE Server успешно запущен!")
        print("📱 Сервер Minecraft PE: localhost:19132")
        print("🌐 Веб-панель: http://localhost:8080")
        print("👤 Логин: admin / admin123")
        print("\n💡 Для остановки нажмите Ctrl+C")
        
        try:
            # Ожидание завершения процессов
            server_process.wait()
            web_panel_process.wait()
        except KeyboardInterrupt:
            print("\n⏹️  Остановка сервера...")
            server_process.terminate()
            web_panel_process.terminate()
            
            # Ожидание завершения
            server_process.wait()
            web_panel_process.wait()
            
            print("✅ Сервер остановлен")
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return False
    
    return True

def main():
    """Главная функция"""
    print("🎮 Minecraft PE Server - Быстрый запуск")
    print("=" * 50)
    
    # Проверки
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        print("\n💡 Для установки зависимостей выполните:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Настройка окружения
    setup_environment()
    
    # Запуск сервера
    if not start_server():
        sys.exit(1)

if __name__ == "__main__":
    main()