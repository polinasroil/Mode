#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый клиент для Minecraft PE Server
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

class TestMinecraftPEClient:
    """Тестовый клиент для проверки сервера"""
    
    def __init__(self, host: str = 'localhost', port: int = 19132):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.username = "TestPlayer"
        
    async def connect(self) -> bool:
        """Подключение к серверу"""
        try:
            # Создание UDP сокета
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            
            # Отправка пакета входа
            login_packet = self.create_login_packet()
            self.socket.sendto(login_packet, (self.host, self.port))
            
            # Ожидание ответа
            try:
                data, addr = self.socket.recvfrom(1024)
                if data:
                    packet_type = data[0]
                    if packet_type == 0x02:  # PACKET_PLAY_STATUS
                        self.connected = True
                        logger.info(f"Успешно подключился к серверу {self.host}:{self.port}")
                        return True
                    else:
                        logger.warning(f"Получен неожиданный пакет: {packet_type}")
                        return False
                else:
                    logger.error("Не получен ответ от сервера")
                    return False
                    
            except socket.timeout:
                logger.error("Таймаут ожидания ответа от сервера")
                return False
                
        except Exception as e:
            logger.error(f"Ошибка подключения: {e}")
            return False
    
    def create_login_packet(self) -> bytes:
        """Создание пакета входа"""
        try:
            # Простой пакет входа (упрощенная версия)
            packet_id = 0x01  # PACKET_LOGIN
            username_data = self.username.encode('utf-8')
            
            # Создание пакета
            packet = struct.pack('>B', packet_id) + username_data
            return packet
            
        except Exception as e:
            logger.error(f"Ошибка создания пакета входа: {e}")
            return b''
    
    async def send_message(self, message: str) -> bool:
        """Отправка сообщения на сервер"""
        if not self.connected or not self.socket:
            logger.error("Клиент не подключен")
            return False
        
        try:
            # Создание текстового пакета
            packet_id = 0x09  # PACKET_TEXT
            message_data = message.encode('utf-8')
            
            packet = struct.pack('>B', packet_id) + message_data
            self.socket.sendto(packet, (self.host, self.port))
            
            logger.info(f"Отправлено сообщение: {message}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            return False
    
    async def send_move_packet(self, x: float, y: float, z: float) -> bool:
        """Отправка пакета движения"""
        if not self.connected or not self.socket:
            logger.error("Клиент не подключен")
            return False
        
        try:
            # Создание пакета движения
            packet_id = 0x13  # PACKET_MOVE_PLAYER
            move_data = struct.pack('>fff', x, y, z)
            
            packet = struct.pack('>B', packet_id) + move_data
            self.socket.sendto(packet, (self.host, self.port))
            
            logger.info(f"Отправлено движение: x={x}, y={y}, z={z}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки движения: {e}")
            return False
    
    async def listen_for_messages(self, duration: int = 10):
        """Прослушивание сообщений от сервера"""
        if not self.connected or not self.socket:
            logger.error("Клиент не подключен")
            return
        
        logger.info(f"Начинаю прослушивание сообщений на {duration} секунд...")
        
        start_time = time.time()
        self.socket.settimeout(1.0)  # 1 секунда таймаут
        
        while time.time() - start_time < duration:
            try:
                data, addr = self.socket.recvfrom(1024)
                if data:
                    await self.handle_server_packet(data)
                    
            except socket.timeout:
                # Таймаут - продолжаем
                continue
            except Exception as e:
                logger.error(f"Ошибка приема данных: {e}")
                break
    
    async def handle_server_packet(self, data: bytes):
        """Обработка пакета от сервера"""
        try:
            if len(data) < 1:
                return
            
            packet_type = data[0]
            packet_data = data[1:] if len(data) > 1 else b''
            
            if packet_type == 0x09:  # PACKET_TEXT
                message = packet_data.decode('utf-8', errors='ignore')
                logger.info(f"Получено сообщение от сервера: {message}")
                
            elif packet_type == 0x0B:  # PACKET_START_GAME
                logger.info("Получен пакет начала игры")
                
            elif packet_type == 0x05:  # PACKET_DISCONNECT
                reason = packet_data.decode('utf-8', errors='ignore')
                logger.warning(f"Сервер отключил клиента: {reason}")
                self.connected = False
                
            else:
                logger.debug(f"Получен пакет типа {packet_type}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки пакета: {e}")
    
    def disconnect(self):
        """Отключение от сервера"""
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Ошибка закрытия сокета: {e}")
        
        self.connected = False
        logger.info("Клиент отключен")

async def test_basic_connection():
    """Тест базового подключения"""
    logger.info("=== Тест базового подключения ===")
    
    client = TestMinecraftPEClient()
    
    try:
        # Подключение
        if await client.connect():
            logger.info("✅ Подключение успешно")
            
            # Отправка сообщения
            if await client.send_message("Привет, сервер!"):
                logger.info("✅ Сообщение отправлено")
            
            # Отправка движения
            if await client.send_move_packet(10.0, 64.0, 20.0):
                logger.info("✅ Пакет движения отправлен")
            
            # Прослушивание ответов
            await client.listen_for_messages(5)
            
        else:
            logger.error("❌ Подключение не удалось")
            
    except Exception as e:
        logger.error(f"❌ Ошибка теста: {e}")
    finally:
        client.disconnect()

async def test_multiple_connections():
    """Тест множественных подключений"""
    logger.info("=== Тест множественных подключений ===")
    
    clients = []
    max_clients = 5
    
    try:
        # Создание нескольких клиентов
        for i in range(max_clients):
            client = TestMinecraftPEClient()
            client.username = f"Player{i+1}"
            
            if await client.connect():
                clients.append(client)
                logger.info(f"✅ Клиент {i+1} подключен")
                await asyncio.sleep(0.1)  # Небольшая задержка
            else:
                logger.warning(f"⚠️ Клиент {i+1} не подключился")
        
        logger.info(f"Подключено клиентов: {len(clients)}")
        
        # Отправка сообщений от всех клиентов
        for i, client in enumerate(clients):
            message = f"Привет от Player{i+1}!"
            await client.send_message(message)
            await asyncio.sleep(0.1)
        
        # Ожидание
        await asyncio.sleep(2)
        
    except Exception as e:
        logger.error(f"❌ Ошибка теста множественных подключений: {e}")
    finally:
        # Отключение всех клиентов
        for client in clients:
            client.disconnect()
        logger.info("Все клиенты отключены")

async def test_stress_connection():
    """Тест стресс-подключений"""
    logger.info("=== Тест стресс-подключений ===")
    
    clients = []
    max_clients = 20
    success_count = 0
    
    try:
        start_time = time.time()
        
        # Быстрые подключения
        for i in range(max_clients):
            client = TestMinecraftPEClient()
            client.username = f"StressPlayer{i+1}"
            
            if await client.connect():
                clients.append(client)
                success_count += 1
            else:
                client.disconnect()
            
            # Небольшая задержка между подключениями
            await asyncio.sleep(0.05)
        
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info(f"Подключено: {success_count}/{max_clients} клиентов")
        logger.info(f"Время: {duration:.2f} секунд")
        logger.info(f"Скорость: {success_count/duration:.2f} подключений/сек")
        
        # Ожидание
        await asyncio.sleep(3)
        
    except Exception as e:
        logger.error(f"❌ Ошибка стресс-теста: {e}")
    finally:
        # Отключение всех клиентов
        for client in clients:
            client.disconnect()
        logger.info("Все клиенты отключены")

async def main():
    """Главная функция тестирования"""
    logger.info("🚀 Запуск тестов клиента Minecraft PE")
    
    try:
        # Тест базового подключения
        await test_basic_connection()
        await asyncio.sleep(1)
        
        # Тест множественных подключений
        await test_multiple_connections()
        await asyncio.sleep(1)
        
        # Тест стресс-подключений
        await test_stress_connection()
        
        logger.info("✅ Все тесты завершены")
        
    except KeyboardInterrupt:
        logger.info("Тестирование прервано пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Тестирование остановлено")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")