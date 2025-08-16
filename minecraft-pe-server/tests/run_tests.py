#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт запуска тестов для Minecraft PE Server
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import sys
import subprocess
import os
from pathlib import Path

def run_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов Minecraft PE Server")
    print("=" * 50)
    
    # Переход в директорию проекта
    project_dir = Path(__file__).parent.parent
    os.chdir(project_dir)
    
    # Проверка наличия pytest
    try:
        import pytest
        print("✅ pytest найден")
    except ImportError:
        print("❌ pytest не найден. Устанавливаем...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-asyncio"], check=True)
        print("✅ pytest установлен")
    
    # Проверка виртуального окружения
    if not Path("venv").exists():
        print("⚠️  Виртуальное окружение не найдено. Создаем...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Виртуальное окружение создано")
    
    # Активация виртуального окружения
    if os.name == 'nt':  # Windows
        activate_script = "venv\\Scripts\\activate"
    else:  # Linux/Mac
        activate_script = "venv/bin/activate"
    
    # Установка зависимостей
    print("📦 Устанавливаем зависимости...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("✅ Зависимости установлены")
    
    # Запуск тестов
    print("\n🚀 Запуск тестов...")
    print("-" * 30)
    
    try:
        # Запуск pytest с подробным выводом
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--tb=short",
            "--color=yes"
        ], check=False)
        
        if result.returncode == 0:
            print("\n🎉 Все тесты прошли успешно!")
        else:
            print(f"\n❌ Некоторые тесты не прошли (код выхода: {result.returncode})")
            
    except subprocess.CalledProcessError as e:
        print(f"\n💥 Ошибка запуска тестов: {e}")
        return False
    
    return True

def run_specific_test(test_name):
    """Запуск конкретного теста"""
    print(f"🎯 Запуск теста: {test_name}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            f"tests/{test_name}",
            "-v",
            "--tb=short",
            "--color=yes"
        ], check=False)
        
        if result.returncode == 0:
            print(f"\n✅ Тест {test_name} прошел успешно!")
        else:
            print(f"\n❌ Тест {test_name} не прошел")
            
    except subprocess.CalledProcessError as e:
        print(f"\n💥 Ошибка запуска теста: {e}")
        return False
    
    return True

def run_tests_with_coverage():
    """Запуск тестов с покрытием кода"""
    print("📊 Запуск тестов с покрытием кода")
    print("=" * 50)
    
    # Установка pytest-cov если не установлен
    try:
        import pytest_cov
        print("✅ pytest-cov найден")
    except ImportError:
        print("📦 Устанавливаем pytest-cov...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest-cov"], check=True)
        print("✅ pytest-cov установлен")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "tests/",
            "--cov=server",
            "--cov=web_panel",
            "--cov-report=html",
            "--cov-report=term-missing",
            "-v"
        ], check=False)
        
        if result.returncode == 0:
            print("\n🎉 Тесты с покрытием завершены!")
            print("📁 Отчет о покрытии сохранен в htmlcov/")
        else:
            print(f"\n❌ Некоторые тесты не прошли")
            
    except subprocess.CmdError as e:
        print(f"\n💥 Ошибка запуска тестов с покрытием: {e}")
        return False
    
    return True

def list_tests():
    """Список доступных тестов"""
    print("📋 Доступные тесты:")
    print("=" * 30)
    
    tests_dir = Path("tests")
    if tests_dir.exists():
        for test_file in tests_dir.glob("test_*.py"):
            print(f"  📄 {test_file.stem}")
            
            # Попытка импорта и получения списка тестов
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(test_file.stem, test_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Поиск тестовых методов
                for attr_name in dir(module):
                    if attr_name.startswith('test_'):
                        print(f"    🧪 {attr_name}")
                        
            except Exception as e:
                print(f"    ⚠️  Ошибка анализа: {e}")
    else:
        print("  ❌ Директория tests не найдена")

def main():
    """Главная функция"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            list_tests()
        elif command == "coverage":
            run_tests_with_coverage()
        elif command == "specific":
            if len(sys.argv) > 2:
                test_name = sys.argv[2]
                run_specific_test(test_name)
            else:
                print("❌ Укажите имя теста: python run_tests.py specific test_name")
        elif command == "help":
            print_help()
        else:
            print(f"❌ Неизвестная команда: {command}")
            print_help()
    else:
        # Запуск всех тестов по умолчанию
        run_tests()

def print_help():
    """Вывод справки"""
    print("🧪 Скрипт запуска тестов Minecraft PE Server")
    print("=" * 50)
    print("Использование:")
    print("  python run_tests.py              - Запуск всех тестов")
    print("  python run_tests.py list         - Список доступных тестов")
    print("  python run_tests.py coverage     - Тесты с покрытием кода")
    print("  python run_tests.py specific <test> - Запуск конкретного теста")
    print("  python run_tests.py help         - Эта справка")
    print("\nПримеры:")
    print("  python run_tests.py specific test_server.py")
    print("  python run_tests.py coverage")

if __name__ == "__main__":
    main()