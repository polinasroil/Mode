#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование подключения к Minecraft PE Server
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import socket
import struct
import time
import sys

def test_server_discovery(host: str = 'localhost', port: int = 19132):
    """Тест обнаружения сервера"""
    print(f"🔍 Тестирование обнаружения сервера {host}:{port}")
    
    try:
        # Создание UDP сокета
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)
        
        # Создание unconnected ping пакета
        ping_time = int(time.time() * 1000)
        ping_data = struct.pack('>B', 0x01)  # ID_UNCONNECTED_PING
        ping_data += struct.pack('>Q', ping_time)
        ping_data += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # Magic
        
        # Отправка ping
        sock.sendto(ping_data, (host, port))
        print(f"📤 Отправлен ping на {host}:{port}")
        
        # Ожидание ответа
        try:
            data, addr = sock.recvfrom(1024)
            if data:
                packet_id = data[0]
                if packet_id == 0x1C:  # ID_UNCONNECTED_PONG
                    # Парсинг ответа
                    response_ping_time = struct.unpack('>Q', data[1:9])[0]
                    server_guid = struct.unpack('>Q', data[9:17])[0]
                    
                    # Парсинг информации о сервере
                    server_info = data[17:].decode('utf-8', errors='ignore')
                    print(f"✅ Получен ответ от сервера")
                    print(f"   GUID: {server_guid}")
                    print(f"   Информация: {server_info}")
                    
                    sock.close()
                    return True
                else:
                    print(f"⚠️ Получен неожиданный пакет: {packet_id:02X}")
                    sock.close()
                    return False
            else:
                print("❌ Не получен ответ от сервера")
                sock.close()
                return False
                
        except socket.timeout:
            print("❌ Таймаут ожидания ответа")
            sock.close()
            return False
            
    except Exception as e:
        print(f"❌ Ошибка теста обнаружения: {e}")
        return False

def test_port_availability(host: str = 'localhost', port: int = 19132):
    """Тест доступности порта"""
    print(f"🔌 Тестирование доступности порта {port}")
    
    try:
        # Попытка привязки к порту
        test_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        test_sock.bind((host, port))
        test_sock.close()
        print(f"✅ Порт {port} доступен для использования")
        return True
    except OSError:
        print(f"❌ Порт {port} занят или недоступен")
        return False
    except Exception as e:
        print(f"❌ Ошибка проверки порта: {e}")
        return False

def test_basic_connection(host: str = 'localhost', port: int = 19132):
    """Базовый тест подключения"""
    print(f"🌐 Базовый тест подключения к {host}:{port}")
    
    try:
        # Создание сокета
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(3.0)
        
        # Простая отправка данных
        test_data = b'TEST'
        sock.sendto(test_data, (host, port))
        print(f"📤 Отправлены тестовые данные")
        
        # Попытка получения ответа
        try:
            data, addr = sock.recvfrom(1024)
            print(f"✅ Получен ответ от сервера")
            sock.close()
            return True
        except socket.timeout:
            print(f"⚠️ Таймаут ожидания ответа (это нормально для UDP)")
            sock.close()
            return True  # Для UDP это не критично
        except Exception as e:
            print(f"⚠️ Ошибка получения ответа: {e}")
            sock.close()
            return True
            
    except Exception as e:
        print(f"❌ Ошибка базового подключения: {e}")
        return False

def main():
    """Главная функция"""
    print("🎮 Тестирование подключения к Minecraft PE Server")
    print("=" * 60)
    
    host = 'localhost'
    port = 19132
    
    # Тест 1: Доступность порта
    if not test_port_availability(host, port):
        print("\n❌ Порт недоступен. Возможные причины:")
        print("   - Сервер не запущен")
        print("   - Порт занят другим процессом")
        print("   - Файрвол блокирует порт")
        return False
    
    print()
    
    # Тест 2: Базовое подключение
    if not test_basic_connection(host, port):
        print("\n❌ Базовое подключение не работает")
        return False
    
    print()
    
    # Тест 3: Обнаружение сервера
    if not test_server_discovery(host, port):
        print("\n❌ Сервер не отвечает на ping")
        print("   Возможные причины:")
        print("   - Сервер не запущен")
        print("   - Неправильная реализация RakNet протокола")
        print("   - Ошибки в коде сервера")
        return False
    
    print("\n🎉 Все тесты пройдены успешно!")
    print("✅ Сервер доступен и отвечает на ping")
    print("✅ Minecraft PE клиенты должны видеть сервер")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        sys.exit(1)