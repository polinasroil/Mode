#!/usr/bin/env python3
"""
Server launcher for Minecraft Bedrock Server
Allows choosing between different server versions
"""

import os
import sys
import subprocess
import time
import signal
import threading

def print_banner():
    """Print server banner"""
    print("=" * 60)
    print("🎮 MINECRAFT BEDROCK SERVER LAUNCHER")
    print("=" * 60)
    print("Выберите версию сервера для запуска:")
    print()

def print_menu():
    """Print server menu"""
    print("1. 🚀 Основная версия (main.py) - Рекомендуется")
    print("2. 🔧 Исправленная версия (fixed_server.py) - Для тестирования")
    print("3. 🧪 Упрощенная версия (simple_server.py) - Для отладки")
    print("4. 🧪 Запустить тестовый клиент")
    print("5. 📖 Показать демонстрацию")
    print("6. 📋 Показать README")
    print("7. ❌ Выход")
    print()

def check_file_exists(filename):
    """Check if file exists"""
    return os.path.exists(filename)

def run_server(server_file):
    """Run the selected server"""
    if not check_file_exists(server_file):
        print(f"❌ Файл {server_file} не найден!")
        return None
    
    print(f"🚀 Запуск сервера: {server_file}")
    print("Нажмите Ctrl+C для остановки сервера")
    print()
    
    try:
        # Start server process
        process = subprocess.Popen([sys.executable, server_file])
        
        # Wait for process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n⏹️ Остановка сервера...")
        if process:
            process.terminate()
            process.wait()
        print("✅ Сервер остановлен")
    except Exception as e:
        print(f"❌ Ошибка запуска сервера: {e}")

def run_test_client():
    """Run test client"""
    if not check_file_exists("test_client_advanced.py"):
        print("❌ Файл test_client_advanced.py не найден!")
        return
    
    print("🧪 Запуск тестового клиента...")
    try:
        subprocess.run([sys.executable, "test_client_advanced.py"])
    except Exception as e:
        print(f"❌ Ошибка запуска тестового клиента: {e}")

def show_demo():
    """Show demo"""
    if not check_file_exists("final_demo.py"):
        print("❌ Файл final_demo.py не найден!")
        return
    
    print("📖 Запуск демонстрации...")
    try:
        subprocess.run([sys.executable, "final_demo.py"])
    except Exception as e:
        print(f"❌ Ошибка запуска демонстрации: {e}")

def show_readme():
    """Show README"""
    readme_files = ["README_FIXED.md", "README.md"]
    
    for readme_file in readme_files:
        if check_file_exists(readme_file):
            print(f"📋 Показ {readme_file}...")
            try:
                with open(readme_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(content)
                return
            except Exception as e:
                print(f"❌ Ошибка чтения {readme_file}: {e}")
    
    print("❌ Файл README не найден!")

def check_requirements():
    """Check system requirements"""
    print("🔍 Проверка требований системы...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 11):
        print(f"❌ Требуется Python 3.11+, установлена версия {python_version.major}.{python_version.minor}")
        return False
    else:
        print(f"✅ Python версия: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required files
    required_files = [
        "main.py",
        "server.py",
        "player.py",
        "world.py",
        "packets.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not check_file_exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    else:
        print("✅ Все необходимые файлы найдены")
    
    # Check port availability
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', 19132))
        sock.close()
        print("✅ Порт 19132 доступен")
    except Exception as e:
        print(f"⚠️ Порт 19132 может быть занят: {e}")
        print("Попробуйте остановить другие серверы или изменить порт")
    
    print()
    return True

def main():
    """Main function"""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("❌ Система не соответствует требованиям!")
        return
    
    while True:
        print_menu()
        
        try:
            choice = input("Введите номер выбора (1-7): ").strip()
            
            if choice == "1":
                run_server("main.py")
            elif choice == "2":
                run_server("fixed_server.py")
            elif choice == "3":
                run_server("simple_server.py")
            elif choice == "4":
                run_test_client()
            elif choice == "5":
                show_demo()
            elif choice == "6":
                show_readme()
            elif choice == "7":
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор! Введите число от 1 до 7")
            
            print()
            input("Нажмите Enter для продолжения...")
            print()
            
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()