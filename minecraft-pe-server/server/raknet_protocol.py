#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - RakNet протокол
Автор: Minecraft PE Server Team
Версия: 1.0.0
Основано на официальной спецификации RakNet для Minecraft Bedrock
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

# RakNet константы
RAKNET_PROTOCOL_VERSION = 11
RAKNET_MAX_MTU_SIZE = 1492
RAKNET_MIN_MTU_SIZE = 400

# RakNet пакеты
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
ID_ACK = 0xC0
ID_NACK = 0xA0

@dataclass
class RakNetSession:
    """RakNet сессия"""
    address: Tuple[str, int]
    guid: int
    mtu_size: int = RAKNET_MIN_MTU_SIZE
    connected: bool = False
    connection_time: float = 0
    last_ping: float = 0
    last_pong: float = 0
    sequence_number: int = 0
    reliable_frame_index: int = 0
    split_packet_id: int = 0
    split_packets: Dict[int, Dict[int, bytes]] = None
    
    def __post_init__(self):
        if self.split_packets is None:
            self.split_packets = {}

class RakNetProtocol:
    """Реализация RakNet протокола для Minecraft Bedrock"""
    
    def __init__(self, server):
        self.server = server
        self.socket = None
        self.running = False
        self.sessions: Dict[Tuple[str, int], RakNetSession] = {}
        self.server_guid = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        self.next_split_packet_id = 1
        
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
        """Цикл обработки пакетов"""
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
            elif packet_id == ID_NEW_INCOMING_CONNECTION:
                await self.handle_new_incoming_connection(data, addr)
            elif packet_id == ID_CONNECTED_PING:
                await self.handle_connected_ping(data, addr)
            elif packet_id == ID_CONNECTED_PONG:
                await self.handle_connected_pong(data, addr)
            elif packet_id == ID_DISCONNECTION_NOTIFICATION:
                await self.handle_disconnection_notification(data, addr)
            elif packet_id >= ID_DATA_PACKET_0 and packet_id <= ID_DATA_PACKET_F:
                await self.handle_data_packet(data, addr)
            elif packet_id == ID_ACK:
                await self.handle_ack(data, addr)
            elif packet_id == ID_NACK:
                await self.handle_nack(data, addr)
            else:
                logger.debug(f"Неизвестный RakNet пакет: {packet_id:02X} от {addr}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки пакета {packet_id:02X} от {addr}: {e}")
    
    async def handle_unconnected_ping(self, data: bytes, addr: Tuple[str, int]):
        """Обработка unconnected ping (сервер discovery)"""
        try:
            if len(data) >= 9:
                ping_time = struct.unpack('>Q', data[1:9])[0]
                
                # Создание pong ответа
                pong_data = struct.pack('>B', ID_UNCONNECTED_PONG)
                pong_data += struct.pack('>Q', ping_time)  # Ping time
                pong_data += struct.pack('>Q', self.server_guid)  # Server GUID
                pong_data += b"MCPE;"  # Magic
                pong_data += b"Minecraft PE Server;"  # Game name
                pong_data += b"1.20.50;"  # Protocol version
                pong_data += b"1.20.50;"  # Game version
                pong_data += b"0;"  # Player count
                pong_data += b"20;"  # Max players
                pong_data += b"Server;"  # Server name
                pong_data += b"Survival;"  # Game mode
                pong_data += b"1;"  # Game mode numeric
                pong_data += b"0;"  # Port IPv4
                pong_data += b"0;"  # Port IPv6
                
                # Отправка pong
                await self.send_packet(pong_data, addr)
                logger.debug(f"Отправлен unconnected pong для {addr}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки unconnected ping: {e}")
    
    async def handle_open_connection_request_1(self, data: bytes, addr: Tuple[str, int]):
        """Обработка первого запроса на открытие соединения"""
        try:
            if len(data) >= 17:
                protocol_version = struct.unpack('>B', data[1:2])[0]
                mtu_size = len(data) + 28  # Размер пакета + overhead
                
                if protocol_version != RAKNET_PROTOCOL_VERSION:
                    # Несовместимая версия протокола
                    reply_data = struct.pack('>B', ID_INCOMPATIBLE_PROTOCOL_VERSION)
                    reply_data += struct.pack('>B', RAKNET_PROTOCOL_VERSION)
                    await self.send_packet(reply_data, addr)
                    logger.warning(f"Несовместимая версия протокола {protocol_version} от {addr}")
                    return
                
                # Создание ответа
                reply_data = struct.pack('>B', ID_OPEN_CONNECTION_REPLY_1)
                reply_data += struct.pack('>Q', self.server_guid)  # Server GUID
                reply_data += b'\x00'  # Security
                reply_data += struct.pack('>H', mtu_size)  # MTU size
                
                await self.send_packet(reply_data, addr)
                logger.debug(f"Отправлен open connection reply 1 для {addr} (MTU: {mtu_size})")
                
        except Exception as e:
            logger.error(f"Ошибка обработки open connection request 1: {e}")
    
    async def handle_open_connection_request_2(self, data: bytes, addr: Tuple[str, int]):
        """Обработка второго запроса на открытие соединения"""
        try:
            if len(data) >= 21:
                server_address = data[1:17]  # Server address
                mtu_size = struct.unpack('>H', data[17:19])[0]  # MTU size
                client_guid = struct.unpack('>Q', data[19:27])[0]  # Client GUID
                
                # Ограничение MTU
                if mtu_size > RAKNET_MAX_MTU_SIZE:
                    mtu_size = RAKNET_MAX_MTU_SIZE
                elif mtu_size < RAKNET_MIN_MTU_SIZE:
                    mtu_size = RAKNET_MIN_MTU_SIZE
                
                # Создание ответа
                reply_data = struct.pack('>B', ID_OPEN_CONNECTION_REPLY_2)
                reply_data += struct.pack('>Q', self.server_guid)  # Server GUID
                reply_data += server_address  # Client address
                reply_data += struct.pack('>H', mtu_size)  # MTU size
                reply_data += b'\x00'  # Security
                
                await self.send_packet(reply_data, addr)
                logger.debug(f"Отправлен open connection reply 2 для {addr} (MTU: {mtu_size})")
                
        except Exception as e:
            logger.error(f"Ошибка обработки open connection request 2: {e}")
    
    async def handle_connection_request(self, data: bytes, addr: Tuple[str, int]):
        """Обработка запроса на соединение"""
        try:
            if len(data) >= 9:
                client_guid = struct.unpack('>Q', data[1:9])[0]
                timestamp = time.time()
                
                # Создание сессии
                session = RakNetSession(addr, client_guid)
                session.connection_time = timestamp
                session.last_ping = timestamp
                session.last_pong = timestamp
                
                self.sessions[addr] = session
                
                # Создание ответа
                reply_data = struct.pack('>B', ID_CONNECTION_REQUEST_ACCEPTED)
                reply_data += struct.pack('>Q', client_guid)  # Client GUID
                reply_data += struct.pack('>Q', self.server_guid)  # Server GUID
                reply_data += struct.pack('>H', 0)  # System address count
                reply_data += struct.pack('>Q', timestamp)  # Timestamp
                
                await self.send_packet(reply_data, addr)
                logger.info(f"Создана RakNet сессия для {addr} (GUID: {client_guid})")
                
        except Exception as e:
            logger.error(f"Ошибка обработки connection request: {e}")
    
    async def handle_new_incoming_connection(self, data: bytes, addr: Tuple[str, int]):
        """Обработка нового входящего соединения"""
        try:
            if len(data) >= 25:
                client_guid = struct.unpack('>Q', data[1:9])[0]
                server_address = data[9:25]  # Server address
                
                session = self.sessions.get(addr)
                if session and session.guid == client_guid:
                    session.connected = True
                    
                    # Отправка подтверждения
                    reply_data = struct.pack('>B', ID_NEW_INCOMING_CONNECTION)
                    reply_data += struct.pack('>Q', client_guid)  # Client GUID
                    reply_data += server_address  # Server address
                    
                    await self.send_packet(reply_data, addr)
                    logger.info(f"RakNet соединение установлено для {addr}")
                    
                    # Передача управления Bedrock протоколу
                    if hasattr(self.server, 'bedrock_protocol'):
                        await self.server.bedrock_protocol.handle_raknet_connection(session)
                
        except Exception as e:
            logger.error(f"Ошибка обработки new incoming connection: {e}")
    
    async def handle_connected_ping(self, data: bytes, addr: Tuple[str, int]):
        """Обработка connected ping"""
        try:
            if len(data) >= 9:
                ping_time = struct.unpack('>Q', data[1:9])[0]
                
                session = self.sessions.get(addr)
                if session and session.connected:
                    session.last_ping = time.time()
                    
                    # Создание pong ответа
                    pong_data = struct.pack('>B', ID_CONNECTED_PONG)
                    pong_data += struct.pack('>Q', ping_time)  # Ping time
                    
                    await self.send_packet(pong_data, addr)
                    logger.debug(f"Отправлен connected pong для {addr}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки connected ping: {e}")
    
    async def handle_connected_pong(self, data: bytes, addr: Tuple[str, int]):
        """Обработка connected pong"""
        try:
            if len(data) >= 9:
                pong_time = struct.unpack('>Q', data[1:9])[0]
                
                session = self.sessions.get(addr)
                if session and session.connected:
                    session.last_pong = time.time()
                    logger.debug(f"Получен connected pong от {addr}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки connected pong: {e}")
    
    async def handle_disconnection_notification(self, data: bytes, addr: Tuple[str, int]):
        """Обработка уведомления об отключении"""
        try:
            session = self.sessions.get(addr)
            if session:
                await self.disconnect_session(session)
                logger.info(f"RakNet соединение разорвано для {addr}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки disconnection notification: {e}")
    
    async def handle_data_packet(self, data: bytes, addr: Tuple[str, int]):
        """Обработка пакета данных"""
        try:
            session = self.sessions.get(addr)
            if not session or not session.connected:
                return
            
            # Извлечение данных
            if len(data) >= 3:
                sequence_number = struct.unpack('>H', data[1:3])[0]
                payload = data[3:]
                
                # Обработка последовательности
                if sequence_number > session.sequence_number:
                    session.sequence_number = sequence_number
                    
                    # Отправка ACK
                    ack_data = struct.pack('>B', ID_ACK)
                    ack_data += struct.pack('>H', 1)  # Count
                    ack_data += struct.pack('>H', sequence_number)  # Sequence number
                    await self.send_packet(ack_data, addr)
                    
                    # Передача данных Bedrock протоколу
                    if hasattr(self.server, 'bedrock_protocol'):
                        await self.server.bedrock_protocol.handle_raknet_data(payload, session)
                    
                    logger.debug(f"Обработан пакет данных {sequence_number} от {addr}")
                else:
                    # Дублированный пакет, отправляем ACK
                    ack_data = struct.pack('>B', ID_ACK)
                    ack_data += struct.pack('>H', 1)  # Count
                    ack_data += struct.pack('>H', sequence_number)  # Sequence number
                    await self.send_packet(ack_data, addr)
                
        except Exception as e:
            logger.error(f"Ошибка обработки пакета данных: {e}")
    
    async def handle_ack(self, data: bytes, addr: Tuple[str, int]):
        """Обработка ACK"""
        try:
            # ACK подтверждает получение пакетов
            # Здесь можно добавить логику подтверждения отправленных пакетов
            pass
            
        except Exception as e:
            logger.error(f"Ошибка обработки ACK: {e}")
    
    async def handle_nack(self, data: bytes, addr: Tuple[str, int]):
        """Обработка NACK"""
        try:
            # NACK указывает на потерю пакетов
            # Здесь можно добавить логику повторной отправки
            pass
            
        except Exception as e:
            logger.error(f"Ошибка обработки NACK: {e}")
    
    async def send_packet(self, data: bytes, addr: Tuple[str, int]):
        """Отправка пакета"""
        try:
            self.socket.sendto(data, addr)
        except Exception as e:
            logger.error(f"Ошибка отправки пакета: {e}")
    
    async def send_data_packet(self, data: bytes, session: RakNetSession, reliable: bool = False):
        """Отправка пакета данных через RakNet"""
        try:
            if not session.connected:
                return False
            
            # Создание заголовка пакета данных
            packet_data = struct.pack('>B', ID_DATA_PACKET_0)  # Используем первый канал
            packet_data += struct.pack('>H', session.sequence_number)  # Sequence number
            
            if reliable:
                packet_data += struct.pack('>I', session.reliable_frame_index)  # Reliable frame index
                session.reliable_frame_index += 1
            
            packet_data += data
            
            # Отправка пакета
            await self.send_packet(packet_data, session.address)
            session.sequence_number += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки пакета данных: {e}")
            return False
    
    async def disconnect_session(self, session: RakNetSession):
        """Отключение сессии"""
        try:
            if session.connected:
                # Отправка уведомления об отключении
                disconnect_data = struct.pack('>B', ID_DISCONNECTION_NOTIFICATION)
                await self.send_packet(disconnect_data, session.address)
            
            # Удаление сессии
            if session.address in self.sessions:
                del self.sessions[session.address]
                
        except Exception as e:
            logger.error(f"Ошибка отключения сессии: {e}")
            # Принудительно удаляем сессию
            if session.address in self.sessions:
                del self.sessions[session.address]
    
    async def process_sessions(self):
        """Обработка сессий"""
        try:
            current_time = time.time()
            sessions_to_remove = []
            
            for addr, session in self.sessions.items():
                # Проверка таймаута (30 секунд без активности)
                if current_time - session.last_ping > 30:
                    logger.info(f"Таймаут RakNet сессии {addr}")
                    sessions_to_remove.append(addr)
            
            # Удаление отключенных сессий
            for addr in sessions_to_remove:
                session = self.sessions[addr]
                await self.disconnect_session(session)
                
        except Exception as e:
            logger.error(f"Ошибка обработки сессий: {e}")
    
    def get_session_count(self) -> int:
        """Получение количества активных сессий"""
        return len([s for s in self.sessions.values() if s.connected])
    
    def get_server_info(self) -> Dict:
        """Получение информации о сервере"""
        return {
            'protocol_version': RAKNET_PROTOCOL_VERSION,
            'server_guid': self.server_guid,
            'active_sessions': self.get_session_count(),
            'total_sessions': len(self.sessions)
        }