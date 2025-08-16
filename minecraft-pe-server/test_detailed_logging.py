#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест подробного логирования для Minecraft PE Server
"""

import sys
import os
import asyncio
import traceback

# Добавляем путь к модулям
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_detailed_logging():
    """Тест системы подробного логирования"""
    print("🧪 Тестирование подробного логирования...")
    
    try:
        # Тест 1: Импорт модулей
        print("1. Тест импорта модулей...")
        from server.detailed_logger import detailed_logger
        print("   ✅ DetailedLogger импортирован")
        
        # Тест 2: Создание логгера
        print("2. Тест создания логгера...")
        logger = detailed_logger
        print("   ✅ Логгер создан")
        
        # Тест 3: Тестирование методов логирования
        print("3. Тест методов логирования...")
        
        # Тест подключения
        logger.log_connection_attempt(('127.0.0.1', 12345), 100)
        print("   ✅ log_connection_attempt работает")
        
        # Тест пакетов
        logger.log_packet_received(0x01, ('127.0.0.1', 12345), 50)
        logger.log_packet_sent(0x02, ('127.0.0.1', 12345), 75)
        print("   ✅ log_packet_received/sent работают")
        
        # Тест входа игрока
        logger.log_player_login_start("TestPlayer", ('127.0.0.1', 12345), 1)
        logger.log_player_login_step("TestPlayer", "TEST_STEP", "тестовый шаг")
        logger.log_player_login_complete("TestPlayer")
        print("   ✅ log_player_login_* работают")
        
        # Тест мира
        logger.log_world_generation(0, 0, 256)
        logger.log_chunk_sent("TestPlayer", 0, 0, 1024)
        print("   ✅ log_world_* работают")
        
        # Тест ошибок
        logger.log_error("TEST_ERROR", "Тестовая ошибка", "traceback info")
        print("   ✅ log_error работает")
        
        # Тест отладки
        logger.log_debug_info("TEST_DEBUG", "Тестовая отладочная информация")
        print("   ✅ log_debug_info работает")
        
        print("\n🎉 ВСЕ ТЕСТЫ ЛОГИРОВАНИЯ ПРОШЛИ УСПЕШНО!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования логирования: {e}")
        traceback.print_exc()
        return False

def test_bedrock_protocol():
    """Тест Bedrock протокола"""
    print("\n🔧 Тестирование Bedrock протокола...")
    
    try:
        # Тест 1: Импорт протокола
        print("1. Тест импорта протокола...")
        from server.bedrock_protocol_v2 import BedrockProtocolV2, BedrockSession
        print("   ✅ BedrockProtocolV2 импортирован")
        
        # Тест 2: Создание протокола
        print("2. Тест создания протокола...")
        protocol = BedrockProtocolV2(None)
        print("   ✅ Протокол создан")
        
        # Тест 3: Проверка методов
        print("3. Тест методов протокола...")
        required_methods = [
            'send_packet',
            'send_packet_compressed',
            'create_start_game_data_v2',
            'create_player_spawn_data_v2',
            'create_spawn_position_data_v2',
            'create_player_abilities_data_v2',
            'create_health_data_v2',
            'create_experience_data_v2',
            'create_empty_inventory_data_v2',
            'create_entity_data_v2',
            'create_player_attributes_data_v2',
            'create_available_commands_data_v2',
            'send_world_chunks',
            'process_sessions',
            'broadcast_world_updates',
            'handle_raknet_connection',
            'handle_raknet_data'
        ]
        
        for method in required_methods:
            if hasattr(protocol, method):
                print(f"   ✅ Метод {method} найден")
            else:
                print(f"   ❌ Метод {method} НЕ найден")
                return False
        
        # Тест 4: Создание сессии
        print("4. Тест создания сессии...")
        session = BedrockSession(('127.0.0.1', 12345), 0)
        session.username = "TestPlayer"
        print(f"   ✅ Сессия создана: {session.username}")
        
        print("\n🎉 ВСЕ ТЕСТЫ ПРОТОКОЛА ПРОШЛИ УСПЕШНО!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования протокола: {e}")
        traceback.print_exc()
        return False

async def test_async_methods():
    """Тест асинхронных методов"""
    print("\n⚡ Тестирование асинхронных методов...")
    
    try:
        from server.bedrock_protocol_v2 import BedrockProtocolV2, BedrockSession
        
        # Создаем протокол
        protocol = BedrockProtocolV2(None)
        
        # Создаем сессию
        session = BedrockSession(('127.0.0.1', 12345), 0)
        session.username = "TestPlayer"
        
        # Тест 1: Создание данных пакетов
        print("1. Тест создания данных пакетов...")
        
        start_game_data = protocol.create_start_game_data_v2(session)
        print(f"   ✅ START_GAME данные: {len(start_game_data)} байт")
        
        spawn_data = protocol.create_player_spawn_data_v2(session, None)
        print(f"   ✅ PLAYER_SPAWN данные: {len(spawn_data)} байт")
        
        health_data = protocol.create_health_data_v2(session)
        print(f"   ✅ HEALTH данные: {len(health_data)} байт")
        
        # Тест 2: Обработка сессий
        print("2. Тест обработки сессий...")
        await protocol.process_sessions()
        print("   ✅ process_sessions работает")
        
        # Тест 3: Обновления мира
        print("3. Тест обновлений мира...")
        await protocol.broadcast_world_updates()
        print("   ✅ broadcast_world_updates работает")
        
        print("\n🎉 ВСЕ АСИНХРОННЫЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования асинхронных методов: {e}")
        traceback.print_exc()
        return False

def main():
    """Главная функция тестирования"""
    print("🚀 ЗАПУСК ТЕСТОВ MINECRAFT PE SERVER v2.0.2")
    print("=" * 50)
    
    # Тест 1: Логирование
    test1_success = test_detailed_logging()
    
    # Тест 2: Протокол
    test2_success = test_bedrock_protocol()
    
    # Тест 3: Асинхронные методы
    test3_success = asyncio.run(test_async_methods())
    
    # Итоговый результат
    print("\n" + "=" * 50)
    print("📊 ИТОГИ ТЕСТИРОВАНИЯ:")
    print(f"   Логирование: {'✅ ПРОШЕЛ' if test1_success else '❌ ПРОВАЛЕН'}")
    print(f"   Протокол: {'✅ ПРОШЕЛ' if test2_success else '❌ ПРОВАЛЕН'}")
    print(f"   Асинхронность: {'✅ ПРОШЕЛ' if test3_success else '❌ ПРОВАЛЕН'}")
    
    if all([test1_success, test2_success, test3_success]):
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Сервер готов к работе с подробным логированием!")
        return 0
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        print("🔧 Требуется дополнительная отладка!")
        return 1

if __name__ == "__main__":
    sys.exit(main())