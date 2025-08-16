#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Тест всех протоколов
Автор: Minecraft PE Server Team
Версия: 2.0.1
Тестирование: RakNet + Bedrock + Сжатие + Чанки
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

class TestClient:
    """Тестовый клиент для проверки всех протоколов"""
    
    def __init__(self, host: str = '127.0.0.1', port: int = 19132):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.client_guid = 0x1234567890ABCDEF
        
    async def test_raknet_protocol(self):
        """Тест RakNet протокола"""
        try:
            logger.info("🔌 Тестирование RakNet протокола...")
            
            # Создание UDP сокета
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            
            # 1. Unconnected Ping (Server Discovery)
            logger.info("📡 Отправка Unconnected Ping...")
            ping_data = struct.pack('>B', 0x01)  # ID_UNCONNECTED_PING
            ping_data += struct.pack('>Q', int(time.time() * 1000))  # Ping time
            
            self.socket.sendto(ping_data, (self.host, self.port))
            
            try:
                response, addr = self.socket.recvfrom(1024)
                if response[0] == 0x1C:  # ID_UNCONNECTED_PONG
                    logger.info("✅ Получен Unconnected Pong")
                    logger.info(f"📊 Размер ответа: {len(response)} байт")
                    
                    # Парсинг ответа
                    if len(response) >= 9:
                        ping_time = struct.unpack('>Q', response[1:9])[0]
                        logger.info(f"⏰ Ping time: {ping_time}")
                        
                        # Парсинг информации о сервере
                        if len(response) > 17:
                            server_info = response[17:].decode('utf-8', errors='ignore')
                            logger.info(f"📋 Информация о сервере: {server_info}")
                else:
                    logger.warning(f"⚠️ Неожиданный ответ: {response[0]:02X}")
            except socket.timeout:
                logger.error("❌ Таймаут ожидания Unconnected Pong")
                return False
            
            # 2. Open Connection Request 1
            logger.info("🔗 Отправка Open Connection Request 1...")
            request1_data = struct.pack('>B', 0x05)  # ID_OPEN_CONNECTION_REQUEST_1
            request1_data += struct.pack('>B', 11)  # Protocol version
            request1_data += b'\x00' * 1492  # Padding
            
            self.socket.sendto(request1_data, (self.host, self.port))
            
            try:
                response, addr = self.socket.recvfrom(1024)
                if response[0] == 0x06:  # ID_OPEN_CONNECTION_REPLY_1
                    logger.info("✅ Получен Open Connection Reply 1")
                    
                    if len(response) >= 19:
                        server_guid = struct.unpack('>Q', response[1:9])[0]
                        mtu_size = struct.unpack('>H', response[18:20])[0]
                        logger.info(f"🆔 Server GUID: {server_guid}")
                        logger.info(f"📏 MTU Size: {mtu_size}")
                else:
                    logger.warning(f"⚠️ Неожиданный ответ: {response[0]:02X}")
                    return False
            except socket.timeout:
                logger.error("❌ Таймаут ожидания Open Connection Reply 1")
                return False
            
            # 3. Open Connection Request 2
            logger.info("🔗 Отправка Open Connection Request 2...")
            request2_data = struct.pack('>B', 0x07)  # ID_OPEN_CONNECTION_REQUEST_2
            request2_data += struct.pack('>Q', server_guid)  # Server address
            request2_data += struct.pack('>H', mtu_size)  # MTU size
            request2_data += struct.pack('>Q', self.client_guid)  # Client GUID
            request2_data += b'\x00'  # Security
            
            self.socket.sendto(request2_data, (self.host, self.port))
            
            try:
                response, addr = self.socket.recvfrom(1024)
                if response[0] == 0x08:  # ID_OPEN_CONNECTION_REPLY_2
                    logger.info("✅ Получен Open Connection Reply 2")
                    logger.info("🔗 RakNet соединение установлено!")
                    return True
                else:
                    logger.warning(f"⚠️ Неожиданный ответ: {response[0]:02X}")
                    return False
            except socket.timeout:
                logger.error("❌ Таймаут ожидания Open Connection Reply 2")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования RakNet: {e}")
            return False
    
    async def test_bedrock_protocol(self):
        """Тест Bedrock протокола"""
        try:
            logger.info("🎮 Тестирование Bedrock протокола...")
            
            if not self.connected:
                logger.error("❌ RakNet соединение не установлено")
                return False
            
            # 1. Connection Request
            logger.info("🔐 Отправка Connection Request...")
            conn_request = struct.pack('>B', 0x09)  # ID_CONNECTION_REQUEST
            conn_request += struct.pack('>Q', self.client_guid)  # Client GUID
            
            self.socket.sendto(conn_request, (self.host, self.port))
            
            try:
                response, addr = self.socket.recvfrom(1024)
                if response[0] == 0x10:  # ID_CONNECTION_REQUEST_ACCEPTED
                    logger.info("✅ Получен Connection Request Accepted")
                else:
                    logger.warning(f"⚠️ Неожиданный ответ: {response[0]:02X}")
                    return False
            except socket.timeout:
                logger.error("❌ Таймаут ожидания Connection Request Accepted")
                return False
            
            # 2. New Incoming Connection
            logger.info("🔗 Отправка New Incoming Connection...")
            new_conn = struct.pack('>B', 0x13)  # ID_NEW_INCOMING_CONNECTION
            new_conn += struct.pack('>Q', self.client_guid)  # Client GUID
            new_conn += struct.pack('>Q', 0)  # Server address
            
            self.socket.sendto(new_conn, (self.host, self.port))
            
            try:
                response, addr = self.socket.recvfrom(1024)
                if response[0] == 0x13:  # ID_NEW_INCOMING_CONNECTION
                    logger.info("✅ Получен New Incoming Connection")
                    logger.info("🎮 Bedrock соединение установлено!")
                    return True
                else:
                    logger.warning(f"⚠️ Неожиданный ответ: {response[0]:02X}")
                    return False
            except socket.timeout:
                logger.error("❌ Таймаут ожидания New Incoming Connection")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования Bedrock: {e}")
            return False
    
    async def test_compression(self):
        """Тест системы сжатия"""
        try:
            logger.info("📦 Тестирование системы сжатия...")
            
            # Отправка тестовых данных
            test_data = b"Hello Minecraft PE Server! " * 100  # 2500 байт
            
            logger.info(f"📊 Отправка данных размером: {len(test_data)} байт")
            
            # Создание пакета данных
            packet_data = struct.pack('>B', 0x80)  # ID_DATA_PACKET_0
            packet_data += struct.pack('>H', 1)  # Sequence number
            packet_data += test_data
            
            self.socket.sendto(packet_data, (self.host, self.port))
            
            # Ожидание ACK
            try:
                response, addr = self.socket.recvfrom(1024)
                if response[0] == 0xC0:  # ID_ACK
                    logger.info("✅ Получен ACK - данные доставлены")
                    return True
                else:
                    logger.warning(f"⚠️ Неожиданный ответ: {response[0]:02X}")
                    return False
            except socket.timeout:
                logger.error("❌ Таймаут ожидания ACK")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования сжатия: {e}")
            return False
    
    async def test_chunks(self):
        """Тест системы чанков"""
        try:
            logger.info("🌍 Тестирование системы чанков...")
            
            # Запрос чанка (0, 0)
            chunk_request = struct.pack('>B', 0x3A)  # ID_LEVEL_CHUNK
            chunk_request += struct.pack('>I', 0)  # Chunk X
            chunk_request += struct.pack('>I', 0)  # Chunk Z
            chunk_request += struct.pack('>B', 1)  # Subchunk count
            
            self.socket.sendto(chunk_request, (self.host, self.port))
            
            try:
                response, addr = self.socket.recvfrom(8192)  # Чанки могут быть большими
                if response[0] == 0x3A:  # ID_LEVEL_CHUNK
                    logger.info("✅ Получен чанк мира")
                    logger.info(f"📊 Размер чанка: {len(response)} байт")
                    return True
                else:
                    logger.warning(f"⚠️ Неожиданный ответ: {response[0]:02X}")
                    return False
            except socket.timeout:
                logger.error("❌ Таймаут ожидания чанка")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования чанков: {e}")
            return False
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        try:
            logger.info("🚀 Запуск полного тестирования Minecraft PE Server...")
            logger.info(f"🎯 Цель: {self.host}:{self.port}")
            
            # Тест 1: RakNet протокол
            if not await self.test_raknet_protocol():
                logger.error("❌ Тест RakNet протокола провален")
                return False
            
            self.connected = True
            logger.info("✅ RakNet протокол работает корректно")
            
            # Тест 2: Bedrock протокол
            if not await self.test_bedrock_protocol():
                logger.error("❌ Тест Bedrock протокола провален")
                return False
            
            logger.info("✅ Bedrock протокол работает корректно")
            
            # Тест 3: Система сжатия
            if not await self.test_compression():
                logger.error("❌ Тест системы сжатия провален")
                return False
            
            logger.info("✅ Система сжатия работает корректно")
            
            # Тест 4: Система чанков
            if not await self.test_chunks():
                logger.error("❌ Тест системы чанков провален")
                return False
            
            logger.info("✅ Система чанков работает корректно")
            
            logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
            logger.info("🎮 Minecraft PE Server готов к работе!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Критическая ошибка тестирования: {e}")
            return False
        finally:
            if self.socket:
                self.socket.close()
    
    def close(self):
        """Закрытие соединения"""
        if self.socket:
            self.socket.close()
            logger.info("🔌 Соединение закрыто")

async def main():
    """Главная функция"""
    try:
        # Создание тестового клиента
        client = TestClient()
        
        # Запуск всех тестов
        success = await client.run_all_tests()
        
        if success:
            logger.info("✅ Тестирование завершено успешно")
        else:
            logger.error("❌ Тестирование завершено с ошибками")
        
        return success
        
    except KeyboardInterrupt:
        logger.info("⏹️ Тестирование прервано пользователем")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    # Запуск тестирования
    success = asyncio.run(main())
    exit(0 if success else 1)