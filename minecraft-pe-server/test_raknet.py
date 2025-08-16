#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование RakNet протокола для Minecraft PE
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import asyncio
import socket
import struct
import time
import logging
from typing import Optional, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RakNetTestClient:
    """Тестовый клиент для проверки RakNet протокола"""
    
    def __init__(self, host: str = 'localhost', port: int = 19132):
        self.host = host
        self.port = port
        self.socket = None
        self.server_guid = None
        self.mtu_size = 1492
        self.connected = False
        
    async def test_server_discovery(self) -> bool:
        """Тест обнаружения сервера (unconnected ping)"""
        try:
            logger.info("🔍 Тестирование обнаружения сервера...")
            
            # Создание UDP сокета
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            
            # Создание unconnected ping пакета
            ping_time = int(time.time() * 1000)
            ping_data = struct.pack('>B', 0x01)  # ID_UNCONNECTED_PING
            ping_data += struct.pack('>Q', ping_time)
            ping_data += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # Magic
            
            # Отправка ping
            self.socket.sendto(ping_data, (self.host, self.port))
            logger.info(f"📤 Отправлен ping на {self.host}:{self.port}")
            
            # Ожидание ответа
            try:
                data, addr = self.socket.recvfrom(1024)
                if data:
                    packet_id = data[0]
                    if packet_id == 0x1C:  # ID_UNCONNECTED_PONG
                        # Парсинг ответа
                        response_ping_time = struct.unpack('>Q', data[1:9])[0]
                        self.server_guid = struct.unpack('>Q', data[9:17])[0]
                        
                        # Парсинг информации о сервере
                        server_info = data[17:].decode('utf-8', errors='ignore')
                        logger.info(f"✅ Получен ответ от сервера")
                        logger.info(f"   GUID: {self.server_guid}")
                        logger.info(f"   Информация: {server_info}")
                        
                        return True
                    else:
                        logger.warning(f"⚠️ Получен неожиданный пакет: {packet_id:02X}")
                        return False
                else:
                    logger.error("❌ Не получен ответ от сервера")
                    return False
                    
            except socket.timeout:
                logger.error("❌ Таймаут ожидания ответа")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка теста обнаружения: {e}")
            return False
    
    async def test_connection_handshake(self) -> bool:
        """Тест handshake соединения"""
        try:
            if not self.server_guid:
                logger.error("❌ Сначала нужно обнаружить сервер")
                return False
            
            logger.info("🤝 Тестирование handshake соединения...")
            
            # Шаг 1: Отправка OPEN_CONNECTION_REQUEST_1
            request1_data = struct.pack('>B', 0x05)  # ID_OPEN_CONNECTION_REQUEST_1
            request1_data += struct.pack('>B', 11)   # Protocol version
            request1_data += b'\x00' * 16  # Padding
            
            self.socket.sendto(request1_data, (self.host, self.port))
            logger.info("📤 Отправлен OPEN_CONNECTION_REQUEST_1")
            
            # Ожидание ответа
            try:
                data, addr = self.socket.recvfrom(1024)
                if data and data[0] == 0x06:  # ID_OPEN_CONNECTION_REPLY_1
                    logger.info("✅ Получен OPEN_CONNECTION_REPLY_1")
                    
                    # Шаг 2: Отправка OPEN_CONNECTION_REQUEST_2
                    client_guid = 123456789
                    request2_data = struct.pack('>B', 0x07)  # ID_OPEN_CONNECTION_REQUEST_2
                    request2_data += struct.pack('>4sH', socket.inet_aton(self.host), self.port)  # Client address
                    request2_data += struct.pack('>H', self.mtu_size)  # MTU size
                    request2_data += struct.pack('>Q', client_guid)  # Client GUID
                    
                    self.socket.sendto(request2_data, (self.host, self.port))
                    logger.info("📤 Отправлен OPEN_CONNECTION_REQUEST_2")
                    
                    # Ожидание ответа
                    data, addr = self.socket.recvfrom(1024)
                    if data and data[0] == 0x08:  # ID_OPEN_CONNECTION_REPLY_2
                        logger.info("✅ Получен OPEN_CONNECTION_REPLY_2")
                        
                        # Шаг 3: Отправка CONNECTION_REQUEST
                        conn_request = struct.pack('>B', 0x09)  # ID_CONNECTION_REQUEST
                        conn_request += struct.pack('>Q', client_guid)
                        conn_request += struct.pack('>Q', time.time() * 1000)
                        
                        self.socket.sendto(conn_request, (self.host, self.port))
                        logger.info("📤 Отправлен CONNECTION_REQUEST")
                        
                        # Ожидание подтверждения
                        data, addr = self.socket.recvfrom(1024)
                        if data and data[0] == 0x10:  # ID_CONNECTION_REQUEST_ACCEPTED
                            logger.info("✅ Получен CONNECTION_REQUEST_ACCEPTED")
                            
                            # Ожидание NEW_INCOMING_CONNECTION
                            data, addr = self.socket.recvfrom(1024)
                            if data and data[0] == 0x13:  # ID_NEW_INCOMING_CONNECTION
                                logger.info("✅ Получен NEW_INCOMING_CONNECTION")
                                self.connected = True
                                return True
                            else:
                                logger.warning("⚠️ Не получен NEW_INCOMING_CONNECTION")
                                return False
                        else:
                            logger.warning("⚠️ Не получен CONNECTION_REQUEST_ACCEPTED")
                            return False
                    else:
                        logger.warning("⚠️ Не получен OPEN_CONNECTION_REPLY_2")
                        return False
                else:
                    logger.warning("⚠️ Не получен OPEN_CONNECTION_REPLY_1")
                    return False
                    
            except socket.timeout:
                logger.error("❌ Таймаут ожидания ответа")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка handshake: {e}")
            return False
    
    async def test_minecraft_login(self) -> bool:
        """Тест входа в Minecraft PE"""
        try:
            if not self.connected:
                logger.error("❌ Сначала нужно установить соединение")
                return False
            
            logger.info("🎮 Тестирование входа в Minecraft PE...")
            
            # Создание пакета входа
            username = "TestPlayer"
            login_data = struct.pack('>B', 0x01)  # MC_LOGIN
            login_data += username.encode('utf-8')
            
            # Создание RakNet пакета
            raknet_data = struct.pack('>B', 0x80)  # ID_DATA_PACKET_0 (reliable)
            raknet_data += struct.pack('>H', 0)    # Sequence number
            raknet_data += login_data
            
            # Отправка пакета
            self.socket.sendto(raknet_data, (self.host, self.port))
            logger.info(f"📤 Отправлен пакет входа для {username}")
            
            # Ожидание ответа
            try:
                data, addr = self.socket.recvfrom(1024)
                if data:
                    packet_id = data[0]
                    if packet_id == 0x80:  # Data packet
                        logger.info("✅ Получен ответ на вход")
                        return True
                    elif packet_id == 0x05:  # MC_DISCONNECT
                        reason = data[1:].decode('utf-8', errors='ignore')
                        logger.warning(f"⚠️ Сервер отклонил вход: {reason}")
                        return False
                    else:
                        logger.warning(f"⚠️ Получен неожиданный пакет: {packet_id:02X}")
                        return False
                else:
                    logger.error("❌ Не получен ответ на вход")
                    return False
                    
            except socket.timeout:
                logger.error("❌ Таймаут ожидания ответа на вход")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка теста входа: {e}")
            return False
    
    async def test_ping_pong(self) -> bool:
        """Тест ping/pong"""
        try:
            if not self.connected:
                logger.error("❌ Сначала нужно установить соединение")
                return False
            
            logger.info("🏓 Тестирование ping/pong...")
            
            # Отправка ping
            ping_time = int(time.time() * 1000)
            ping_data = struct.pack('>B', 0x00)  # ID_CONNECTED_PING
            ping_data += struct.pack('>Q', ping_time)
            
            self.socket.sendto(ping_data, (self.host, self.port))
            logger.info("📤 Отправлен ping")
            
            # Ожидание pong
            try:
                data, addr = self.socket.recvfrom(1024)
                if data and data[0] == 0x03:  # ID_CONNECTED_PONG
                    response_time = struct.unpack('>Q', data[1:9])[0]
                    if response_time == ping_time:
                        logger.info("✅ Получен корректный pong")
                        return True
                    else:
                        logger.warning("⚠️ Получен некорректный pong")
                        return False
                else:
                    logger.warning("⚠️ Не получен pong")
                    return False
                    
            except socket.timeout:
                logger.error("❌ Таймаут ожидания pong")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка теста ping/pong: {e}")
            return False
    
    def disconnect(self):
        """Отключение от сервера"""
        if self.connected and self.socket:
            try:
                # Отправка уведомления об отключении
                disconnect_data = struct.pack('>B', 0x15)  # ID_DISCONNECTION_NOTIFICATION
                self.socket.sendto(disconnect_data, (self.host, self.port))
                logger.info("📤 Отправлено уведомление об отключении")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления об отключении: {e}")
        
        if self.socket:
            self.socket.close()
        
        self.connected = False
        logger.info("🔌 Отключен от сервера")

async def test_raknet_protocol():
    """Тест RakNet протокола"""
    logger.info("🚀 Тестирование RakNet протокола для Minecraft PE")
    logger.info("=" * 60)
    
    client = RakNetTestClient()
    
    try:
        # Тест 1: Обнаружение сервера
        if not await client.test_server_discovery():
            logger.error("❌ Тест обнаружения сервера провален")
            return False
        
        # Тест 2: Handshake соединения
        if not await client.test_connection_handshake():
            logger.error("❌ Тест handshake соединения провален")
            return False
        
        # Тест 3: Вход в Minecraft PE
        if not await client.test_minecraft_login():
            logger.error("❌ Тест входа в Minecraft PE провален")
            return False
        
        # Тест 4: Ping/Pong
        if not await client.test_ping_pong():
            logger.error("❌ Тест ping/pong провален")
            return False
        
        logger.info("🎉 Все тесты RakNet протокола пройдены успешно!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка тестирования: {e}")
        return False
    finally:
        client.disconnect()

async def main():
    """Главная функция"""
    try:
        success = await test_raknet_protocol()
        if success:
            logger.info("✅ RakNet протокол работает корректно")
        else:
            logger.error("❌ RakNet протокол имеет проблемы")
            return 1
        return 0
        
    except KeyboardInterrupt:
        logger.info("⏹️ Тестирование прервано пользователем")
        return 1
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("⏹️ Тестирование остановлено")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)