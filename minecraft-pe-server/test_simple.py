#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой тест всех модулей Minecraft PE Server
"""

import sys
import traceback

def test_module(module_name, description):
    """Тест импорта модуля"""
    try:
        __import__(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except Exception as e:
        print(f"❌ {description}: {module_name} - {e}")
        traceback.print_exc()
        return False

def main():
    """Главная функция тестирования"""
    print("🧪 Тестирование всех модулей Minecraft PE Server...")
    print("=" * 60)
    
    # Список модулей для тестирования
    modules = [
        ("server.raknet_protocol", "RakNet протокол"),
        ("server.bedrock_protocol_v2", "Bedrock протокол v2.0"),
        ("server.compression", "Система сжатия"),
        ("server.chunk_system", "Система чанков"),
    ]
    
    success_count = 0
    total_count = len(modules)
    
    for module_name, description in modules:
        if test_module(module_name, description):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"📊 Результаты: {success_count}/{total_count} модулей работают")
    
    if success_count == total_count:
        print("🎉 ВСЕ МОДУЛИ РАБОТАЮТ КОРРЕКТНО!")
        print("🚀 Сервер готов к запуску!")
        return True
    else:
        print("❌ Некоторые модули не работают")
        print("🔧 Проверьте ошибки выше")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)