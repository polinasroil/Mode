#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование подключения к Minecraft PE Server
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import asyncio
import socket
import time
import sys
import os
from pathlib import Path

# Добавление пути к модулям
sys.path.insert(0, str(Path(__file__).parent))

def test_server_port(host: str = 'localhost', port: int = 19132) -> bool:
    """Тест доступности порта сервера"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2.0)
        
        # Попытка подключения
        result = sock.connect_ex((host, port))
        sock.close()
        
        return result == 0
    except Exception:
        return False

def test_web_panel_port(host: str = 'localhost', port: int = 8080) -> bool:
    """Тест доступности веб-панели"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        
        # Попытка подключения
        result = sock.connect_ex((host, port))
        sock.close()
        
        return result == 0
    except Exception:
        return False

async def test_basic_connection():
    """Базовый тест подключения"""
    print("🔍 Тестирование базового подключения...")
    
    # Проверка порта сервера
    if test_server_port():
        print("✅ Порт сервера 19132 доступен")
    else:
        print("❌ Порт сервера 19132 недоступен")
        return False
    
    # Проверка веб-панели
    if test_web_panel_port():
        print("✅ Веб-панель на порту 8080 доступна")
    else:
        print("❌ Веб-панель на порту 8080 недоступна")
    
    return True

async def test_network_protocol():
    """Тест сетевого протокола"""
    print("\n🌐 Тестирование сетевого протокола...")
    
    try:
        from tests.test_client import TestMinecraftPEClient
        
        client = TestMinecraftPEClient()
        
        # Тест подключения
        if await client.connect():
            print("✅ Подключение к серверу успешно")
            
            # Тест отправки сообщения
            if await client.send_message("Тестовое сообщение"):
                print("✅ Отправка сообщения успешна")
            
            # Тест движения
            if await client.send_move_packet(0.0, 64.0, 0.0):
                print("✅ Отправка движения успешна")
            
            # Отключение
            client.disconnect()
            print("✅ Отключение от сервера успешно")
            return True
        else:
            print("❌ Подключение к серверу не удалось")
            return False
            
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать тестовый клиент: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования протокола: {e}")
        return False

async def test_server_functionality():
    """Тест функциональности сервера"""
    print("\n⚙️ Тестирование функциональности сервера...")
    
    try:
        from server.main import MinecraftPEServer
        
        # Создание экземпляра сервера
        server = MinecraftPEServer()
        
        # Проверка инициализации
        if server.config and server.worlds:
            print("✅ Сервер инициализирован корректно")
        else:
            print("❌ Ошибка инициализации сервера")
            return False
        
        # Проверка конфигурации
        required_config = ['server-name', 'server-port', 'max-players']
        for key in required_config:
            if key in server.config:
                print(f"✅ Конфигурация {key}: {server.config[key]}")
            else:
                print(f"❌ Отсутствует конфигурация {key}")
                return False
        
        # Проверка миров
        if len(server.worlds) > 0:
            world = list(server.worlds.values())[0]
            print(f"✅ Мир '{world.name}' загружен")
        else:
            print("❌ Миры не загружены")
            return False
        
        return True
        
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать сервер: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования функциональности: {e}")
        return False

async def test_web_panel():
    """Тест веб-панели"""
    print("\n🌐 Тестирование веб-панели...")
    
    try:
        from web_panel.app import app
        
        # Проверка создания приложения
        if app:
            print("✅ Веб-приложение создано")
        else:
            print("❌ Ошибка создания веб-приложения")
            return False
        
        # Проверка маршрутов
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        required_routes = ['/login', '/dashboard', '/players']
        
        for route in required_routes:
            if route in routes:
                print(f"✅ Маршрут {route} найден")
            else:
                print(f"❌ Маршрут {route} не найден")
        
        return True
        
    except ImportError as e:
        print(f"⚠️ Не удалось импортировать веб-панель: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка тестирования веб-панели: {e}")
        return False

async def run_performance_test():
    """Запуск теста производительности"""
    print("\n🚀 Тест производительности...")
    
    try:
        from tests.test_client import TestMinecraftPEClient
        
        clients = []
        max_clients = 10
        success_count = 0
        
        start_time = time.time()
        
        # Создание клиентов
        for i in range(max_clients):
            client = TestMinecraftPEClient()
            client.username = f"PerfPlayer{i+1}"
            
            if await client.connect():
                clients.append(client)
                success_count += 1
                print(f"✅ Клиент {i+1} подключен")
            else:
                print(f"❌ Клиент {i+1} не подключился")
            
            await asyncio.sleep(0.1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n📊 Результаты теста производительности:")
        print(f"Подключено: {success_count}/{max_clients} клиентов")
        print(f"Время: {duration:.2f} секунд")
        print(f"Скорость: {success_count/duration:.2f} подключений/сек")
        
        # Отключение клиентов
        for client in clients:
            client.disconnect()
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Ошибка теста производительности: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("🎮 Тестирование Minecraft PE Server")
    print("=" * 50)
    
    results = []
    
    try:
        # Базовый тест подключения
        result = await test_basic_connection()
        results.append(("Базовое подключение", result))
        
        # Тест функциональности сервера
        result = await test_server_functionality()
        results.append(("Функциональность сервера", result))
        
        # Тест веб-панели
        result = await test_web_panel()
        results.append(("Веб-панель", result))
        
        # Тест сетевого протокола
        result = await test_network_protocol()
        results.append(("Сетевой протокол", result))
        
        # Тест производительности
        result = await run_performance_test()
        results.append(("Производительность", result))
        
        # Вывод результатов
        print("\n" + "=" * 50)
        print("📋 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
        passed = 0
        total = len(results)
        
        for test_name, result in results:
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            print(f"{test_name}: {status}")
            if result:
                passed += 1
        
        print(f"\nИтого: {passed}/{total} тестов пройдено")
        
        if passed == total:
            print("🎉 Все тесты пройдены успешно!")
        elif passed > total / 2:
            print("⚠️ Большинство тестов пройдено, есть проблемы")
        else:
            print("❌ Много тестов провалено, требуется исправление")
        
        return passed == total
        
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
        return False
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование остановлено")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)