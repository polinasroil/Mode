#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - RakNet протокол (исправленная версия)
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

# RakNet константы (согласно документации)
RAKNET_PROTOCOL_VERSION = 11
MINECRAFT_PROTOCOL_VERSION = 662

# RakNet пакеты (правильные ID)
ID_UNCONNECTED_PING = 0x01
ID_UNCONNECTED_PONG = 0x1C
ID_OPEN_CONNECTION_REQUEST_1 = 0x05
ID_OPEN_CONNECTION_REPLY_1 = 0x06
ID_OPEN_CONNECTION_REQUEST_2 = 0x07
ID_OPEN_CONNECTION_REPLY_2 = 0x08
ID_CONNECTION_REQUEST = 0x09
ID_CONNECTION_REQUEST_ACCEPTED = 0x10
ID_NEW_INCOMING_CONNECTION = 0x13
ID_DISCONNECTION_NOTIFICATION = 0x15
ID_INCOMPATIBLE_PROTOCOL_VERSION = 0x19
ID_CONNECTED_PING = 0x00
ID_CONNECTED_PONG = 0x03
ID_DATA_PACKET_0 = 0x80
ID_DATA_PACKET_1 = 0x81
ID_DATA_PACKET_2 = 0x82
ID_DATA_PACKET_3 = 0x83
ID_DATA_PACKET_4 = 0x84
ID_DATA_PACKET_5 = 0x85
ID_DATA_PACKET_6 = 0x86
ID_DATA_PACKET_7 = 0x87
ID_DATA_PACKET_8 = 0x88
ID_DATA_PACKET_9 = 0x89
ID_DATA_PACKET_A = 0x8A
ID_DATA_PACKET_B = 0x8B
ID_DATA_PACKET_C = 0x8C
ID_DATA_PACKET_D = 0x8D
ID_DATA_PACKET_E = 0x8E
ID_DATA_PACKET_F = 0x8F

# Minecraft PE пакеты (правильные ID)
MC_LOGIN = 0x01
MC_PLAY_STATUS = 0x02
MC_DISCONNECT = 0x05
MC_TEXT = 0x09
MC_START_GAME = 0x0B
MC_ADD_PLAYER = 0x0C
MC_REMOVE_PLAYER = 0x0D
MC_MOVE_PLAYER = 0x13
MC_LEVEL_CHUNK = 0x3A

@dataclass
class RakNetSession:
    """Сессия RakNet"""
    address: Tuple[str, int]
    guid: int
    mtu_size: int
    state: str = "connecting"  # connecting, connected, disconnected
    last_ping: float = 0
    last_pong: float = 0
    reliable_frame_index: int = 0
    sequence_number: int = 0
    split_packet_id: int = 0
    split_packets: Dict[int, List[bytes]] = None
    username: str = ""
    
    def __post_init__(self):
        if self.split_packets is None:
            self.split_packets = {}
        if not self.guid:
            self.guid = random.randint(0, 0xFFFFFFFFFFFFFFFF)

class RakNetProtocol:
    """Реализация RakNet протокола для Minecraft PE (исправленная)"""
    
    def __init__(self, server):
        self.server = server
        self.socket = None
        self.running = False
        self.sessions: Dict[Tuple[str, int], RakNetSession] = {}
        self.server_guid = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        self.mtu_size = 1492  # Стандартный MTU для RakNet
        
        # Minecraft PE данные
        self.game_packets: Dict[int, bytes] = {}
        
        logger.info(f"RakNet протокол инициализирован (GUID: {self.server_guid})")
    
    async def start(self, host: str = '0.0.0.0', port: int = 19132):
        """Запуск RakNet протокола"""
        self.running = True
        logger.info(f"Запуск RakNet протокола на {host}:{port}")
        
        try:
            # Создание UDP сокета
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket.bind((host, port))
            
            # Установка неблокирующего режима
            self.socket.setblocking(False)
            
            logger.info(f"RakNet сокет создан и привязан к {host}:{port}")
            
            # Запуск обработчика пакетов в фоне
            asyncio.create_task(self.packet_handler_loop())
            
        except Exception as e:
            logger.error(f"Ошибка запуска RakNet протокола: {e}")
            raise
    
    async def stop(self):
        """Остановка RakNet протокола"""
        self.running = False
        
        # Отключение всех сессий
        for session in list(self.sessions.values()):
            await self.disconnect_session(session)
        
        if self.socket:
            self.socket.close()
        
        logger.info("RakNet протокол остановлен")
    
    async def packet_handler_loop(self):
        """Цикл обработки пакетов (неблокирующий)"""
        logger.info("Запуск цикла обработки пакетов RakNet")
        
        while self.running:
            try:
                # Обработка входящих пакетов
                await self.handle_incoming_packets()
                
                # Обработка сессий
                await self.process_sessions()
                
                # Небольшая задержка
                await asyncio.sleep(0.001)  # 1ms
                
            except Exception as e:
                logger.error(f"Ошибка в цикле обработки пакетов RakNet: {e}")
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
            
            # Обработка RakNet пакетов
            if packet_id == ID_UNCONNECTED_PING:
                await self.handle_unconnected_ping(data, addr)
            elif packet_id == ID_OPEN_CONNECTION_REQUEST_1:
                await self.handle_open_connection_request_1(data, addr)
            elif packet_id == ID_OPEN_CONNECTION_REQUEST_2:
                await self.handle_open_connection_request_2(data, addr)
            elif packet_id == ID_CONNECTION_REQUEST:
                await self.handle_connection_request(data, addr)
            elif packet_id == ID_CONNECTED_PING:
                await self.handle_connected_ping(data, addr)
            elif packet_id == ID_DISCONNECTION_NOTIFICATION:
                await self.handle_disconnection_notification(data, addr)
            elif packet_id >= ID_DATA_PACKET_0 and packet_id <= ID_DATA_PACKET_F:
                await self.handle_data_packet(data, addr)
            else:
                logger.debug(f"Неизвестный RakNet пакет: {packet_id:02X} от {addr}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки пакета {packet_id:02X} от {addr}: {e}")
    
    async def handle_unconnected_ping(self, data: bytes, addr: Tuple[str, int]):
        """Обработка unconnected ping (для обнаружения сервера)"""
        try:
            if len(data) < 25:
                return
            
            # Извлечение данных ping
            ping_time = struct.unpack('>Q', data[1:9])[0]
            magic = data[9:25]
            
            # Проверка magic bytes
            expected_magic = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
            if magic != expected_magic:
                return
            
            # Создание ответа pong
            pong_data = struct.pack('>B', ID_UNCONNECTED_PONG)
            pong_data += struct.pack('>Q', ping_time)
            pong_data += struct.pack('>Q', self.server_guid)
            
            # Добавление информации о сервере (правильный формат MCPE)
            server_info = f"MCPE;{self.server.server_name};{MINECRAFT_PROTOCOL_VERSION};1.20.50;0;{len([s for s in self.sessions.values() if s.state == 'connected'])};{self.server.max_players};{self.server_guid};{self.server.config.get('level-name', 'world')};{self.server.config.get('gamemode', 'survival')};{self.server.config.get('difficulty', 'normal')}"
            pong_data += server_info.encode('utf-8')
            
            # Отправка pong
            self.socket.sendto(pong_data, addr)
            logger.debug(f"Отправлен pong клиенту {addr}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки unconnected ping: {e}")
    
    async def handle_open_connection_request_1(self, data: bytes, addr: Tuple[str, int]):
        """Обработка первого запроса на открытие соединения"""
        try:
            if len(data) < 18:
                return
            
            # Извлечение данных
            protocol_version = data[1:2]
            mtu_size = len(data) + 28  # Размер пакета + заголовок
            
            # Проверка версии протокола
            if protocol_version[0] != RAKNET_PROTOCOL_VERSION:
                # Отправка ошибки несовместимости
                error_data = struct.pack('>B', ID_INCOMPATIBLE_PROTOCOL_VERSION)
                error_data += struct.pack('>B', RAKNET_PROTOCOL_VERSION)
                self.socket.sendto(error_data, addr)
                logger.warning(f"Несовместимая версия протокола от {addr}: {protocol_version[0]}")
                return
            
            # Создание ответа
            reply_data = struct.pack('>B', ID_OPEN_CONNECTION_REPLY_1)
            reply_data += struct.pack('>Q', self.server_guid)
            reply_data += struct.pack('>B', 0)  # Security
            reply_data += struct.pack('>H', mtu_size)
            
            # Отправка ответа
            self.socket.sendto(reply_data, addr)
            logger.debug(f"Отправлен ответ на connection request 1 клиенту {addr}")
            
        except Exception as e:
            logger.error(f"Ошибка обработки connection request 1: {e}")
    
    async def handle_open_connection_request_2(self, data: bytes, addr: Tuple[str, int]):
        """Обработка второго запроса на открытие соединения"""
        try:
            if len(data) < 35:
                return
            
            # Извлечение данных
            client_address = data[1:7]  # IP + порт
            mtu_size = struct.unpack('>H', data[7:9])[0]
            client_guid = struct.unpack('>Q', data[9:17])[0]
            
            # Создание сессии
            session = RakNetSession(addr, client_guid)
            session.mtu_size = min(mtu_size, self.mtu_size)
            self.sessions[addr] = session
            
            # Создание ответа
            reply_data = struct.pack('>B', ID_OPEN_CONNECTION_REPLY_2)
            reply_data += struct.pack('>Q', self.server_guid)
            reply_data += struct.pack('>H', session.mtu_size)
            reply_data += struct.pack('>B', 0)  # Security
            
            # Отправка ответа
            self.socket.sendto(reply_data, addr)
            logger.info(f"Создана сессия для клиента {addr} (GUID: {client_guid})")
            
        except Exception as e:
            logger.error(f"Ошибка обработки connection request 2: {e}")
    
    async def handle_connection_request(self, data: bytes, addr: Tuple[str, int]):
        """Обработка запроса на соединение"""
        try:
            if len(data) < 9:
                return
            
            # Извлечение данных
            client_guid = struct.unpack('>Q', data[1:9])[0]
            
            # Поиск сессии
            session = self.sessions.get(addr)
            if not session or session.guid != client_guid:
                return
            
            # Создание ответа
            reply_data = struct.pack('>B', ID_CONNECTION_REQUEST_ACCEPTED)
            reply_data += struct.pack('>Q', client_guid)
            reply_data += struct.pack('>Q', self.server_guid)
            
            # Добавление адресов
            reply_data += struct.pack('>B', 0)  # System address count
            reply_data += struct.pack('>B', 0)  # System address index
            
            # Отправка ответа
            self.socket.sendto(reply_data, addr)
            
            # Отправка подтверждения нового соединения
            new_conn_data = struct.pack('>B', ID_NEW_INCOMING_CONNECTION)
            new_conn_data += struct.pack('>Q', client_guid)
            new_conn_data += struct.pack('>Q', self.server_guid)
            
            self.socket.sendto(new_conn_data, addr)
            
            # Обновление состояния сессии
            session.state = "connected"
            logger.info(f"Клиент {addr} подключен")
            
        except Exception as e:
            logger.error(f"Ошибка обработки connection request: {e}")
    
    async def handle_connected_ping(self, data: bytes, addr: Tuple[str, int]):
        """Обработка ping от подключенного клиента"""
        try:
            if len(data) < 9:
                return
            
            # Извлечение времени ping
            ping_time = struct.unpack('>Q', data[1:9])[0]
            
            # Создание ответа pong
            pong_data = struct.pack('>B', ID_CONNECTED_PONG)
            pong_data += struct.pack('>Q', ping_time)
            
            # Отправка pong
            self.socket.sendto(pong_data, addr)
            
            # Обновление времени последнего ping
            session = self.sessions.get(addr)
            if session:
                session.last_ping = time.time()
                
        except Exception as e:
            logger.error(f"Ошибка обработки connected ping: {e}")
    
    async def handle_disconnection_notification(self, data: bytes, addr: Tuple[str, int]):
        """Обработка уведомления об отключении"""
        try:
            session = self.sessions.get(addr)
            if session:
                await self.disconnect_session(session)
                logger.info(f"Клиент {addr} отключился")
                
        except Exception as e:
            logger.error(f"Ошибка обработки disconnection notification: {e}")
    
    async def handle_data_packet(self, data: bytes, addr: Tuple[str, int]):
        """Обработка пакета с данными"""
        try:
            session = self.sessions.get(addr)
            if not session or session.state != "connected":
                return
            
            # Извлечение Minecraft PE пакета
            if len(data) < 3:
                return
            
            # Парсинг RakNet заголовка
            packet_id = data[0]
            reliability = (packet_id & 0xE0) >> 5
            is_fragmented = bool(packet_id & 0x10)
            
            if is_fragmented:
                # Обработка фрагментированного пакета
                await self.handle_fragmented_packet(data, session)
            else:
                # Обработка обычного пакета
                await self.handle_minecraft_packet(data[3:], session)
                
        except Exception as e:
            logger.error(f"Ошибка обработки data packet: {e}")
    
    async def handle_fragmented_packet(self, data: bytes, session: RakNetSession):
        """Обработка фрагментированного пакета"""
        try:
            # Извлечение информации о фрагментах
            split_count = struct.unpack('>H', data[3:5])[0]
            split_id = struct.unpack('>H', data[5:7])[0]
            split_index = struct.unpack('>H', data[7:9])[0]
            
            # Сохранение фрагмента
            if split_id not in session.split_packets:
                session.split_packets[split_id] = [None] * split_count
            
            session.split_packets[split_id][split_index] = data[9:]
            
            # Проверка полноты пакета
            if all(fragment is not None for fragment in session.split_packets[split_id]):
                # Сборка полного пакета
                full_packet = b''.join(session.split_packets[split_id])
                await self.handle_minecraft_packet(full_packet, session)
                
                # Очистка фрагментов
                del session.split_packets[split_id]
                
        except Exception as e:
            logger.error(f"Ошибка обработки фрагментированного пакета: {e}")
    
    async def handle_minecraft_packet(self, data: bytes, session: RakNetSession):
        """Обработка Minecraft PE пакета"""
        try:
            if len(data) < 1:
                return
            
            packet_id = data[0]
            
            # Обработка Minecraft PE пакетов
            if packet_id == MC_LOGIN:
                await self.handle_minecraft_login(data, session)
            elif packet_id == MC_TEXT:
                await self.handle_minecraft_text(data, session)
            elif packet_id == MC_MOVE_PLAYER:
                await self.handle_minecraft_move_player(data, session)
            else:
                logger.debug(f"Неизвестный Minecraft PE пакет: {packet_id:02X}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки Minecraft PE пакета: {e}")
    
    async def handle_minecraft_login(self, data: bytes, session: RakNetSession):
        """Обработка входа в Minecraft PE"""
        try:
            # Парсинг данных входа (упрощенно)
            if len(data) > 1:
                username = data[1:].decode('utf-8', errors='ignore').split('\x00')[0]
                session.username = username
                
                logger.info(f"Попытка входа игрока {username} с {session.address}")
                
                # Подключение игрока к серверу
                try:
                    player = await self.server.player_join(username, session.address[0])
                    
                    # Отправка подтверждения входа
                    await self.send_minecraft_packet(MC_PLAY_STATUS, struct.pack('>I', MINECRAFT_PROTOCOL_VERSION), session)
                    
                    # Отправка информации о мире
                    await self.send_minecraft_packet(MC_START_GAME, self.create_start_game_data(), session)
                    
                    logger.info(f"Игрок {username} успешно подключился")
                    
                except Exception as e:
                    logger.error(f"Ошибка подключения игрока {username}: {e}")
                    await self.send_minecraft_packet(MC_DISCONNECT, str(e).encode('utf-8'), session)
                    
        except Exception as e:
            logger.error(f"Ошибка обработки входа: {e}")
    
    async def handle_minecraft_text(self, data: bytes, session: RakNetSession):
        """Обработка текстового сообщения"""
        try:
            if len(data) > 1:
                message = data[1:].decode('utf-8', errors='ignore')
                logger.info(f"Сообщение от {session.username or session.address}: {message}")
                
                # Обработка команд
                if message.startswith('/'):
                    await self.handle_command(message, session)
                else:
                    # Отправка сообщения всем игрокам
                    await self.broadcast_message(f"<{session.username or 'Player'}> {message}")
                    
        except Exception as e:
            logger.error(f"Ошибка обработки текста: {e}")
    
    async def handle_minecraft_move_player(self, data: bytes, session: RakNetSession):
        """Обработка движения игрока"""
        try:
            if len(data) >= 13:
                x, y, z = struct.unpack('>fff', data[1:13])
                
                # Обновление позиции игрока
                if hasattr(self.server, 'players'):
                    for username, player in self.server.players.items():
                        if player.ip_address == session.address[0]:
                            player.spawn_x = x
                            player.spawn_y = y
                            player.spawn_z = z
                            break
                            
        except Exception as e:
            logger.error(f"Ошибка обработки движения: {e}")
    
    async def handle_command(self, command: str, session: RakNetSession):
        """Обработка команд"""
        try:
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == '/help':
                response = "Доступные команды: /help, /time, /weather"
                await self.send_minecraft_packet(MC_TEXT, response.encode('utf-8'), session)
            elif cmd == '/time':
                if hasattr(self.server, 'worlds') and self.server.worlds:
                    world = list(self.server.worlds.values())[0]
                    time_str = world.get_time_string()
                    response = f"Время: {time_str}"
                    await self.send_minecraft_packet(MC_TEXT, response.encode('utf-8'), session)
            else:
                response = f"Неизвестная команда: {cmd}"
                await self.send_minecraft_packet(MC_TEXT, response.encode('utf-8'), session)
                
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
    
    async def send_minecraft_packet(self, packet_id: int, data: bytes, session: RakNetSession):
        """Отправка Minecraft PE пакета"""
        try:
            # Создание RakNet пакета
            raknet_data = struct.pack('>B', packet_id) + data
            
            # Отправка пакета
            await self.send_reliable_packet(raknet_data, session)
            
        except Exception as e:
            logger.error(f"Ошибка отправки Minecraft PE пакета: {e}")
    
    async def send_reliable_packet(self, data: bytes, session: RakNetSession):
        """Отправка надежного пакета"""
        try:
            # Создание RakNet заголовка
            packet_id = ID_DATA_PACKET_0 | 0x20  # Reliable
            header = struct.pack('>B', packet_id)
            header += struct.pack('>H', session.sequence_number)
            
            # Обновление номера последовательности
            session.sequence_number = (session.sequence_number + 1) % 65536
            
            # Создание полного пакета
            full_packet = header + data
            
            # Отправка пакета
            self.socket.sendto(full_packet, session.address)
            
        except Exception as e:
            logger.error(f"Ошибка отправки надежного пакета: {e}")
    
    async def broadcast_message(self, message: str):
        """Отправка сообщения всем игрокам"""
        try:
            message_data = message.encode('utf-8')
            
            for session in self.sessions.values():
                if session.state == "connected":
                    await self.send_minecraft_packet(MC_TEXT, message_data, session)
                    
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения всем игрокам: {e}")
    
    async def disconnect_session(self, session: RakNetSession):
        """Отключение сессии"""
        try:
            # Отправка уведомления об отключении
            disconnect_data = struct.pack('>B', ID_DISCONNECTION_NOTIFICATION)
            self.socket.sendto(disconnect_data, session.address)
            
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
                if session.state == "connected":
                    if current_time - session.last_ping > 30:  # 30 секунд без ping
                        logger.warning(f"Таймаут сессии {session.address}")
                        await self.disconnect_session(session)
                        
        except Exception as e:
            logger.error(f"Ошибка обработки сессий: {e}")
    
    def get_session_count(self) -> int:
        """Получение количества активных сессий"""
        return len([s for s in self.sessions.values() if s.state == "connected"])
    
    def get_server_info(self) -> Dict:
        """Получение информации о сервере"""
        return {
            'raknet_version': RAKNET_PROTOCOL_VERSION,
            'minecraft_version': MINECRAFT_PROTOCOL_VERSION,
            'server_guid': self.server_guid,
            'active_sessions': self.get_session_count(),
            'total_sessions': len(self.sessions),
            'mtu_size': self.mtu_size
        }