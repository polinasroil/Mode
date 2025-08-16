#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Bedrock протокол (правильная версия для телефона)
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import asyncio
import socket
import struct
import logging
import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

# Minecraft Bedrock (PE) константы
BEDROCK_PROTOCOL_VERSION = 662  # Minecraft PE 1.20.50
BEDROCK_GAME_VERSION = "1.20.50"

# Bedrock пакеты (правильные ID для Minecraft PE)
ID_LOGIN = 0x01
ID_PLAY_STATUS = 0x02
ID_DISCONNECT = 0x05
ID_TEXT = 0x09
ID_START_GAME = 0x0B
ID_ADD_PLAYER = 0x0C
ID_REMOVE_PLAYER = 0x0D
ID_MOVE_PLAYER = 0x13
ID_LEVEL_CHUNK = 0x3A
ID_PLAYER_SPAWN = 0x0E
ID_UPDATE_BLOCK = 0x15

@dataclass
class BedrockSession:
    """Сессия Minecraft Bedrock"""
    address: Tuple[str, int]
    client_guid: int
    username: str = ""
    xuid: str = ""
    identity_public_key: str = ""
    client_random_id: int = 0
    device_os: str = ""
    game_version: str = ""
    language_code: str = "en_US"
    connected: bool = False
    join_time: float = 0
    last_ping: float = 0
    
    def __post_init__(self):
        if not self.client_guid:
            self.client_guid = random.randint(0, 0xFFFFFFFFFFFFFFFF)

class BedrockProtocol:
    """Реализация Bedrock протокола для Minecraft PE"""
    
    def __init__(self, server):
        self.server = server
        self.socket = None
        self.running = False
        self.sessions: Dict[Tuple[str, int], BedrockSession] = {}
        self.server_guid = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        
        logger.info(f"Bedrock протокол инициализирован (GUID: {self.server_guid})")
    
    async def start(self, host: str = '0.0.0.0', port: int = 19132):
        """Запуск Bedrock протокола"""
        self.running = True
        logger.info(f"Запуск Bedrock протокола на {host}:{port}")
        
        try:
            # Создание UDP сокета
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket.bind((host, port))
            
            # Установка неблокирующего режима
            self.socket.setblocking(False)
            
            logger.info(f"Bedrock сокет создан и привязан к {host}:{port}")
            
            # Запуск обработчика пакетов в фоне
            asyncio.create_task(self.packet_handler_loop())
            
        except Exception as e:
            logger.error(f"Ошибка запуска Bedrock протокола: {e}")
            raise
    
    async def stop(self):
        """Остановка Bedrock протокола"""
        self.running = False
        
        # Отключение всех сессий
        for session in list(self.sessions.values()):
            await self.disconnect_session(session)
        
        if self.socket:
            self.socket.close()
        
        logger.info("Bedrock протокол остановлен")
    
    async def packet_handler_loop(self):
        """Цикл обработки пакетов (неблокирующий)"""
        logger.info("Запуск цикла обработки пакетов Bedrock")
        
        while self.running:
            try:
                # Обработка входящих пакетов
                await self.handle_incoming_packets()
                
                # Обработка сессий
                await self.process_sessions()
                
                # Небольшая задержка
                await asyncio.sleep(0.001)  # 1ms
                
            except Exception as e:
                logger.error(f"Ошибка в цикле обработки пакетов Bedrock: {e}")
                await asyncio.sleep(0.1)
    
    async def handle_incoming_packets(self):
        """Обработка входящих пакетов"""
        try:
            while True:
                try:
                    data, addr = self.socket.recvfrom(4096)
                    if data:
                        await self.handle_packet(data, addr)
                except BlockingIOError:
                    # Нет данных для чтения
                    break
                except Exception as e:
                    logger.error(f"Ошибка чтения пакета: {e}")
                    break
        except Exception as e:
            logger.error(f"Ошибка обработки входящих пакетов: {e}")
    
    async def handle_packet(self, data: bytes, addr: Tuple[str, int]):
        """Обработка отдельного пакета"""
        try:
            if len(data) < 1:
                return
            
            packet_id = data[0]
            
            # Обработка Bedrock пакетов
            if packet_id == ID_LOGIN:
                await self.handle_login(data, addr)
            elif packet_id == ID_TEXT:
                await self.handle_text(data, addr)
            elif packet_id == ID_MOVE_PLAYER:
                await self.handle_move_player(data, addr)
            elif packet_id == ID_DISCONNECT:
                await self.handle_disconnect(data, addr)
            else:
                logger.debug(f"Неизвестный Bedrock пакет: {packet_id:02X} от {addr}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки пакета {packet_id:02X} от {addr}: {e}")
    
    async def handle_login(self, data: bytes, addr: Tuple[str, int]):
        """Обработка входа в Minecraft PE"""
        try:
            # Парсинг данных входа (упрощенно для демонстрации)
            if len(data) > 1:
                # Извлечение базовой информации
                username = data[1:].decode('utf-8', errors='ignore').split('\x00')[0]
                
                # Создание сессии
                session = BedrockSession(addr, random.randint(0, 0xFFFFFFFFFFFFFFFF))
                session.username = username
                session.connected = True
                session.join_time = time.time()
                session.last_ping = time.time()
                
                self.sessions[addr] = session
                
                logger.info(f"Попытка входа игрока {username} с {addr}")
                
                # Подключение игрока к серверу
                try:
                    player = await self.server.player_join(username, addr[0])
                    
                    # Отправка подтверждения входа
                    await self.send_packet(ID_PLAY_STATUS, struct.pack('>I', 0), addr)  # 0 = Success
                    
                    # Отправка информации о мире
                    await self.send_packet(ID_START_GAME, self.create_start_game_data(), addr)
                    
                    # Отправка спавна игрока
                    await self.send_packet(ID_PLAYER_SPAWN, self.create_player_spawn_data(player), addr)
                    
                    logger.info(f"Игрок {username} успешно подключился")
                    
                except Exception as e:
                    logger.error(f"Ошибка подключения игрока {username}: {e}")
                    await self.send_packet(ID_DISCONNECT, str(e).encode('utf-8'), addr)
                    
        except Exception as e:
            logger.error(f"Ошибка обработки входа: {e}")
    
    async def handle_text(self, data: bytes, addr: Tuple[str, int]):
        """Обработка текстового сообщения"""
        try:
            session = self.sessions.get(addr)
            if not session or not session.connected:
                return
                
            if len(data) > 1:
                message = data[1:].decode('utf-8', errors='ignore')
                logger.info(f"Сообщение от {session.username}: {message}")
                
                # Обработка команд
                if message.startswith('/'):
                    await self.handle_command(message, session)
                else:
                    # Отправка сообщения всем игрокам
                    await self.broadcast_message(f"<{session.username}> {message}")
                    
        except Exception as e:
            logger.error(f"Ошибка обработки текста: {e}")
    
    async def handle_move_player(self, data: bytes, addr: Tuple[str, int]):
        """Обработка движения игрока"""
        try:
            session = self.sessions.get(addr)
            if not session or not session.connected:
                return
                
            if len(data) >= 13:
                x, y, z = struct.unpack('>fff', data[1:13])
                
                # Обновление позиции игрока
                if hasattr(self.server, 'players'):
                    for username, player in self.server.players.items():
                        if player.ip_address == addr[0]:
                            player.spawn_x = x
                            player.spawn_y = y
                            player.spawn_z = z
                            break
                            
        except Exception as e:
            logger.error(f"Ошибка обработки движения: {e}")
    
    async def handle_disconnect(self, data: bytes, addr: Tuple[str, int]):
        """Обработка отключения"""
        try:
            session = self.sessions.get(addr)
            if session:
                await self.disconnect_session(session)
                logger.info(f"Клиент {addr} отключился")
                
        except Exception as e:
            logger.error(f"Ошибка обработки отключения: {e}")
    
    async def handle_command(self, command: str, session: BedrockSession):
        """Обработка команд"""
        try:
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == '/help':
                response = "Доступные команды: /help, /time, /weather"
                await self.send_packet(ID_TEXT, response.encode('utf-8'), session.address)
            elif cmd == '/time':
                if hasattr(self.server, 'worlds') and self.server.worlds:
                    world = list(self.server.worlds.values())[0]
                    time_str = world.get_time_string()
                    response = f"Время: {time_str}"
                    await self.send_packet(ID_TEXT, response.encode('utf-8'), session.address)
            else:
                response = f"Неизвестная команда: {cmd}"
                await self.send_packet(ID_TEXT, response.encode('utf-8'), session.address)
                
        except Exception as e:
            logger.error(f"Ошибка обработки команды: {e}")
    
    def create_start_game_data(self) -> bytes:
        """Создание данных для пакета начала игры"""
        try:
            if hasattr(self.server, 'worlds') and self.server.worlds:
                world = list(self.server.worlds.values())[0]
                
                data = struct.pack('>I', world.seed)  # Seed
                data += struct.pack('>B', 0)  # Gamemode
                data += struct.pack('>B', 0)  # Entity ID
                data += struct.pack('>f', float(world.spawn_x))  # Spawn X
                data += struct.pack('>f', float(world.spawn_y))  # Spawn Y
                data += struct.pack('>f', float(world.spawn_z))  # Spawn Z
                
                return data
            else:
                # Значения по умолчанию
                return struct.pack('>IBBfff', 0, 0, 0, 0.0, 64.0, 0.0)
                
        except Exception as e:
            logger.error(f"Ошибка создания данных начала игры: {e}")
            return struct.pack('>IBBfff', 0, 0, 0, 0.0, 64.0, 0.0)
    
    def create_player_spawn_data(self, player) -> bytes:
        """Создание данных для спавна игрока"""
        try:
            data = struct.pack('>Q', int(player.uuid, 16) if isinstance(player.uuid, str) else player.uuid)  # UUID
            data += struct.pack('>f', player.spawn_x)  # X
            data += struct.pack('>f', player.spawn_y)  # Y
            data += struct.pack('>f', player.spawn_z)  # Z
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных спавна: {e}")
            return struct.pack('>Qfff', 0, 0.0, 64.0, 0.0)
    
    async def send_packet(self, packet_id: int, data: bytes, addr: Tuple[str, int]):
        """Отправка пакета"""
        try:
            # Создание пакета
            packet = struct.pack('>B', packet_id) + data
            
            # Отправка пакета
            self.socket.sendto(packet, addr)
            
        except Exception as e:
            logger.error(f"Ошибка отправки пакета: {e}")
    
    async def broadcast_message(self, message: str):
        """Отправка сообщения всем игрокам"""
        try:
            message_data = message.encode('utf-8')
            
            for session in self.sessions.values():
                if session.connected:
                    await self.send_packet(ID_TEXT, message_data, session.address)
                    
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения всем игрокам: {e}")
    
    async def disconnect_session(self, session: BedrockSession):
        """Отключение сессии"""
        try:
            # Отправка уведомления об отключении
            await self.send_packet(ID_DISCONNECT, b"Disconnected", session.address)
            
            # Удаление сессии
            if session.address in self.sessions:
                del self.sessions[session.address]
            
            # Отключение игрока от сервера
            if hasattr(self.server, 'players'):
                for username, player in list(self.server.players.items()):
                    if player.ip_address == session.address[0]:
                        await self.server.player_leave(username)
                        break
                        
        except Exception as e:
            logger.error(f"Ошибка отключения сессии: {e}")
    
    async def process_sessions(self):
        """Обработка сессий"""
        try:
            current_time = time.time()
            
            for session in list(self.sessions.values()):
                # Проверка таймаута
                if session.connected:
                    if current_time - session.last_ping > 30:  # 30 секунд без активности
                        logger.warning(f"Таймаут сессии {session.address}")
                        await self.disconnect_session(session)
                        
        except Exception as e:
            logger.error(f"Ошибка обработки сессий: {e}")
    
    def get_session_count(self) -> int:
        """Получение количества активных сессий"""
        return len([s for s in self.sessions.values() if s.connected])
    
    def get_server_info(self) -> Dict:
        """Получение информации о сервере"""
        return {
            'protocol_version': BEDROCK_PROTOCOL_VERSION,
            'game_version': BEDROCK_GAME_VERSION,
            'server_guid': self.server_guid,
            'active_sessions': self.get_session_count(),
            'total_sessions': len(self.sessions)
        }