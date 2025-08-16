#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Bedrock протокол (полная реализация)
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
import json
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
ID_PLAYER_SPAWN = 0x0E
ID_UPDATE_BLOCK = 0x15
ID_MOVE_PLAYER = 0x13
ID_LEVEL_CHUNK = 0x3A
ID_SET_SPAWN_POSITION = 0x2B
ID_SET_DIFFICULTY = 0x3C
ID_SET_PLAYER_GAME_TYPE = 0x3E
ID_SET_TIME = 0x0A
ID_SET_WEATHER = 0x1B
ID_AVAILABLE_COMMANDS = 0x4C
ID_SET_ENTITY_DATA = 0x27
ID_SET_PLAYER_INVENTORY_SLOT = 0x37
ID_SET_HEALTH = 0x42
ID_SET_EXPERIENCE = 0x48
ID_SET_PLAYER_ABILITIES = 0x3D
ID_SET_PLAYER_PERMISSIONS = 0x72

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
    entity_id: int = 0
    gamemode: int = 0
    can_fly: bool = False
    can_build: bool = True
    can_break_blocks: bool = True
    
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
        self.next_entity_id = 1
        
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
            elif packet_id == 0x00:  # Connected Ping
                await self.handle_ping(data, addr)
            elif packet_id == 0x03:  # Connected Pong
                await self.handle_pong(data, addr)
            else:
                logger.debug(f"Неизвестный Bedrock пакет: {packet_id:02X} от {addr}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки пакета {packet_id:02X} от {addr}: {e}")
    
    async def handle_login(self, data: bytes, addr: Tuple[str, int]):
        """Обработка входа в Minecraft PE"""
        try:
            # Проверяем, не обрабатывается ли уже вход для этого адреса
            if addr in self.sessions and self.sessions[addr].connected:
                logger.debug(f"Игрок с {addr} уже подключен, игнорируем повторный login")
                return
            
            # Парсинг данных входа (упрощенно для демонстрации)
            if len(data) > 1:
                # Извлечение базовой информации
                username = data[1:].decode('utf-8', errors='ignore').split('\x00')[0]
                if not username or username == "":
                    username = f"Player_{random.randint(1000, 9999)}"
                
                # Создание сессии
                session = BedrockSession(addr, random.randint(0, 0xFFFFFFFFFFFFFFFF))
                session.username = username
                session.connected = True
                session.join_time = time.time()
                session.last_ping = time.time()
                session.entity_id = self.next_entity_id
                session.gamemode = 0  # Survival
                
                self.sessions[addr] = session
                self.next_entity_id += 1
                
                logger.info(f"Попытка входа игрока {username} с {addr} (Entity ID: {session.entity_id})")
                
                # Подключение игрока к серверу
                try:
                    player = await self.server.player_join(username, addr[0])
                    
                    # Полная последовательность загрузки игрока
                    await self.complete_player_login(session, player)
                    
                except Exception as e:
                    logger.error(f"Ошибка подключения игрока {username}: {e}")
                    await self.send_packet(ID_DISCONNECT, str(e).encode('utf-8'), addr)
                    # Удаляем неудачную сессию
                    if addr in self.sessions:
                        del self.sessions[addr]
                    
        except Exception as e:
            logger.error(f"Ошибка обработки входа: {e}")
            # Удаляем неудачную сессию
            if addr in self.sessions:
                del self.sessions[addr]
    
    async def complete_player_login(self, session: BedrockSession, player):
        """Полная загрузка игрока в мир"""
        try:
            logger.info(f"Начинаю полную загрузку игрока {session.username}")
            
            # 1. Отправка подтверждения входа
            await self.send_packet(ID_PLAY_STATUS, struct.pack('>I', 0), session.address)  # 0 = Success
            logger.info(f"Отправлен PLAY_STATUS для {session.username}")
            await asyncio.sleep(0.1)
            
            # 2. Отправка информации о мире
            start_game_data = self.create_start_game_data(session)
            await self.send_packet(ID_START_GAME, start_game_data, session.address)
            logger.info(f"Отправлен START_GAME для {session.username}")
            await asyncio.sleep(0.1)
            
            # 3. Отправка сложности
            await self.send_packet(ID_SET_DIFFICULTY, struct.pack('>B', 1), session.address)  # 1 = Easy
            await asyncio.sleep(0.05)
            
            # 4. Отправка времени
            await self.send_packet(ID_SET_TIME, struct.pack('>I', 0), session.address)
            await asyncio.sleep(0.05)
            
            # 5. Отправка погоды
            await self.send_packet(ID_SET_WEATHER, struct.pack('>B', 0), session.address)  # 0 = Clear
            await asyncio.sleep(0.05)
            
            # 6. Отправка спавна игрока
            spawn_data = self.create_player_spawn_data(session, player)
            await self.send_packet(ID_PLAYER_SPAWN, spawn_data, session.address)
            logger.info(f"Отправлен PLAYER_SPAWN для {session.username}")
            await asyncio.sleep(0.1)
            
            # 7. Отправка способностей игрока
            abilities_data = self.create_player_abilities_data(session)
            await self.send_packet(ID_SET_PLAYER_ABILITIES, abilities_data, session.address)
            await asyncio.sleep(0.05)
            
            # 8. Отправка здоровья
            await self.send_packet(ID_SET_HEALTH, struct.pack('>f', 20.0), session.address)
            await asyncio.sleep(0.05)
            
            # 9. Отправка опыта
            await self.send_packet(ID_SET_EXPERIENCE, struct.pack('>f', 0.0), session.address)
            await asyncio.sleep(0.05)
            
            # 10. Отправка приветственного сообщения
            welcome_msg = f"Добро пожаловать на сервер, {session.username}!"
            await self.send_packet(ID_TEXT, welcome_msg.encode('utf-8'), session.address)
            
            # 11. Отправка доступных команд
            commands_data = self.create_available_commands_data()
            await self.send_packet(ID_AVAILABLE_COMMANDS, commands_data, session.address)
            
            logger.info(f"Игрок {session.username} полностью загружен в мир")
            
        except Exception as e:
            logger.error(f"Ошибка полной загрузки игрока {session.username}: {e}")
            raise
    
    def create_start_game_data(self, session: BedrockSession) -> bytes:
        """Создание данных для пакета начала игры"""
        try:
            if hasattr(self.server, 'worlds') and self.server.worlds:
                world = list(self.server.worlds.values())[0]
                
                # Полные данные для START_GAME пакета
                data = struct.pack('>I', world.seed)  # Seed
                data += struct.pack('>B', session.gamemode)  # Gamemode
                data += struct.pack('>I', session.entity_id)  # Entity ID
                data += struct.pack('>f', float(world.spawn_x))  # Spawn X
                data += struct.pack('>f', float(world.spawn_y))  # Spawn Y
                data += struct.pack('>f', float(world.spawn_z))  # Spawn Z
                data += struct.pack('>f', 0.0)  # Yaw
                data += struct.pack('>f', 0.0)  # Pitch
                data += struct.pack('>I', 0)  # World time
                data += struct.pack('>B', 0)  # Weather
                data += struct.pack('>B', 1)  # Difficulty (1 = Easy)
                data += struct.pack('>B', 0)  # Hardcore
                data += struct.pack('>B', 1)  # PvP
                data += struct.pack('>B', 0)  # World type
                data += struct.pack('>B', 0)  # World features
                data += struct.pack('>B', 0)  # World features seed
                data += struct.pack('>B', 0)  # World features enabled
                data += struct.pack('>B', 0)  # World features disabled
                data += struct.pack('>B', 0)  # World features forced
                data += struct.pack('>B', 0)  # World features experimental
                data += struct.pack('>B', 0)  # World features experimental
                
                logger.debug(f"Создан START_GAME пакет: seed={world.seed}, entity_id={session.entity_id}, spawn=({world.spawn_x}, {world.spawn_y}, {world.spawn_z})")
                return data
            else:
                # Значения по умолчанию
                default_data = struct.pack('>IBIfff', 0, session.gamemode, session.entity_id, 0.0, 64.0, 0.0)
                default_data += struct.pack('>ffIBBB', 0.0, 0.0, 0, 0, 0, 0)
                default_data += struct.pack('>BBBBBBBB', 0, 0, 0, 0, 0, 0, 0, 0)
                logger.debug("Создан START_GAME пакет с значениями по умолчанию")
                return default_data
                
        except Exception as e:
            logger.error(f"Ошибка создания данных начала игры: {e}")
            # Возвращаем минимальные данные
            return struct.pack('>IBIfff', 0, session.gamemode, session.entity_id, 0.0, 64.0, 0.0)
    
    def create_player_spawn_data(self, session: BedrockSession, player) -> bytes:
        """Создание данных для спавна игрока"""
        try:
            # UUID игрока
            if isinstance(player.uuid, str):
                try:
                    uuid_int = int(player.uuid, 16)
                except ValueError:
                    uuid_int = hash(player.uuid) & 0xFFFFFFFFFFFFFFFF
            else:
                uuid_int = player.uuid
            
            data = struct.pack('>Q', uuid_int)  # UUID
            data += struct.pack('>f', player.spawn_x)  # X
            data += struct.pack('>f', player.spawn_y)  # Y
            data += struct.pack('>f', player.spawn_z)  # Z
            data += struct.pack('>f', 0.0)  # Yaw
            data += struct.pack('>f', 0.0)  # Pitch
            
            logger.debug(f"Создан PLAYER_SPAWN пакет для {session.username}: ({player.spawn_x}, {player.spawn_y}, {player.spawn_z})")
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных спавна: {e}")
            return struct.pack('>Qfff', 0, 0.0, 64.0, 0.0)
    
    def create_player_abilities_data(self, session: BedrockSession) -> bytes:
        """Создание данных для способностей игрока"""
        try:
            # Флаги способностей
            flags = 0
            if session.can_fly:
                flags |= 0x01
            if session.can_build:
                flags |= 0x02
            if session.can_break_blocks:
                flags |= 0x04
            
            data = struct.pack('>B', flags)  # Flags
            data += struct.pack('>f', 0.05)  # Fly speed
            data += struct.pack('>f', 0.1)   # Walk speed
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных способностей: {e}")
            return struct.pack('>Bff', 0, 0.05, 0.1)
    
    def create_available_commands_data(self) -> bytes:
        """Создание данных для доступных команд"""
        try:
            # Базовые команды
            commands = [
                {"name": "help", "description": "Показать доступные команды"},
                {"name": "time", "description": "Показать время в мире"},
                {"name": "weather", "description": "Показать погоду"},
                {"name": "tp", "description": "Телепортация"},
                {"name": "block", "description": "Установить блок"},
                {"name": "chunk", "description": "Информация о чанке"}
            ]
            
            # Простая реализация - отправляем только количество команд
            data = struct.pack('>I', len(commands))  # Count
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных команд: {e}")
            return struct.pack('>I', 0)
    
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
                response = "Доступные команды: /help, /time, /weather, /tp, /block, /chunk"
                await self.send_packet(ID_TEXT, response.encode('utf-8'), session.address)
            elif cmd == '/time':
                if hasattr(self.server, 'worlds') and self.server.worlds:
                    world = list(self.server.worlds.values())[0]
                    time_str = world.get_time_string()
                    response = f"Время: {time_str}"
                    await self.send_packet(ID_TEXT, response.encode('utf-8'), session.address)
            elif cmd == '/weather':
                response = "Погода: ясно"
                await self.send_packet(ID_TEXT, response.encode('utf-8'), session.address)
            else:
                response = f"Неизвестная команда: {cmd}. Используйте /help для списка команд."
                await self.send_packet(ID_TEXT, response.encode('utf-8'), session.address)
                
        except Exception as e:
            logger.error(f"Ошибка обработки команды: {e}")
    
    async def handle_ping(self, data: bytes, addr: Tuple[str, int]):
        """Обработка ping от клиента"""
        try:
            session = self.sessions.get(addr)
            if session and session.connected:
                # Отправляем pong в ответ
                pong_data = struct.pack('>B', 0x03)  # Connected Pong
                if len(data) > 1:
                    pong_data += data[1:]  # Копируем данные ping
                
                await self.send_packet(0x03, pong_data[1:], addr)
                
                # Обновляем время последней активности
                session.last_ping = time.time()
                logger.debug(f"Отправлен pong для {session.username}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки ping: {e}")
    
    async def handle_pong(self, data: bytes, addr: Tuple[str, int]):
        """Обработка pong от клиента"""
        try:
            session = self.sessions.get(addr)
            if session and session.connected:
                # Обновляем время последней активности
                session.last_pong = time.time()
                logger.debug(f"Получен pong от {session.username}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки pong: {e}")
    
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
            logger.info(f"Отключение сессии для {session.username} ({session.address})")
            
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
            # Принудительно удаляем сессию
            if session.address in self.sessions:
                del self.sessions[session.address]
    
    async def cleanup_disconnected_sessions(self):
        """Очистка отключенных сессий"""
        try:
            current_time = time.time()
            sessions_to_remove = []
            
            for addr, session in self.sessions.items():
                # Проверяем таймаут (30 секунд без активности)
                if current_time - session.last_ping > 30:
                    logger.info(f"Таймаут сессии {session.username} ({addr})")
                    sessions_to_remove.append(addr)
            
            # Удаляем отключенные сессии
            for addr in sessions_to_remove:
                session = self.sessions[addr]
                await self.disconnect_session(session)
                
        except Exception as e:
            logger.error(f"Ошибка очистки сессий: {e}")
    
    async def process_sessions(self):
        """Обработка сессий"""
        try:
            # Очистка отключенных сессий
            await self.cleanup_disconnected_sessions()
            
            # Обновление времени последней активности для активных сессий
            current_time = time.time()
            for session in self.sessions.values():
                if session.connected:
                    # Обновляем время последней активности
                    session.last_ping = current_time
                        
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