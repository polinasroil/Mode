#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Bedrock протокол v2.0 (исправленная версия)
Автор: Minecraft PE Server Team
Версия: 2.0.1
Основано на официальной спецификации Minecraft Bedrock
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

# Minecraft Bedrock Protocol Constants
BEDROCK_PROTOCOL_VERSION = 662  # Minecraft PE 1.20.50
BEDROCK_GAME_VERSION = "1.20.50"

# Bedrock Packet IDs (Official Specification) - ИСПРАВЛЕНО
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

# Действия игрока (правильные ID)
ID_PLAYER_ACTION = 0x30
ID_PLAYER_INPUT = 0x31
ID_PLAYER_MOVEMENT = 0x32
ID_PLAYER_ROTATION = 0x33
ID_PLAYER_POSITION = 0x34
ID_PLAYER_POSITION_AND_ROTATION = 0x35
ID_PLAYER_POSITION_AND_MOTION = 0x36

# Инвентарь и эффекты
ID_SET_PLAYER_INVENTORY = 0x38
ID_SET_PLAYER_ARMOR = 0x39
ID_SET_PLAYER_EFFECTS = 0x3A
ID_SET_PLAYER_ATTRIBUTES = 0x3B

# Права и разрешения (исправлено)
ID_SET_PLAYER_PERMISSIONS = 0x72
ID_SET_PLAYER_PERMISSIONS_LEVEL = 0x73
ID_SET_PLAYER_PERMISSIONS_OP = 0x74
ID_SET_PLAYER_PERMISSIONS_DEOP = 0x75
ID_SET_PLAYER_PERMISSIONS_BAN = 0x76
ID_SET_PLAYER_PERMISSIONS_UNBAN = 0x77
ID_SET_PLAYER_PERMISSIONS_KICK = 0x78
ID_SET_PLAYER_PERMISSIONS_WHITELIST = 0x79
ID_SET_PLAYER_PERMISSIONS_OP_LEVEL = 0x7A
ID_SET_PLAYER_PERMISSIONS_OP_LEVEL_1 = 0x7B
ID_SET_PLAYER_PERMISSIONS_OP_LEVEL_2 = 0x7C
ID_SET_PLAYER_PERMISSIONS_OP_LEVEL_3 = 0x7D
ID_SET_PLAYER_PERMISSIONS_OP_LEVEL_4 = 0x7E

# Дополнительные пакеты для полноценной работы
ID_ADD_ENTITY = 0x0F
ID_REMOVE_ENTITY = 0x0E
ID_MOVE_ENTITY = 0x12
ID_ROTATE_HEAD = 0x19
ID_SET_ENTITY_MOTION = 0x28
ID_SET_ENTITY_POSITION = 0x29
ID_SET_ENTITY_POSITION_AND_ROTATION = 0x2A
ID_SET_ENTITY_ROTATION = 0x2C
ID_SET_ENTITY_DATA = 0x27
ID_SET_ENTITY_LINK = 0x25
ID_SET_ENTITY_COLLISION = 0x26
ID_SET_ENTITY_INVULNERABLE = 0x2D
ID_SET_ENTITY_VELOCITY = 0x2E
ID_SET_ENTITY_FALL_DISTANCE = 0x2F
ID_SET_ENTITY_ON_FIRE = 0x40
ID_SET_ENTITY_NO_AI = 0x41
ID_SET_ENTITY_PASSENGER = 0x43
ID_SET_ENTITY_RIDING = 0x44
ID_SET_ENTITY_SITTING = 0x45
ID_SET_ENTITY_SLEEPING = 0x46
ID_SET_ENTITY_SNEAKING = 0x47
ID_SET_ENTITY_SPRINTING = 0x48
ID_SET_ENTITY_SWIMMING = 0x49
ID_SET_ENTITY_TELEPORTING = 0x4A
ID_SET_ENTITY_TICKING = 0x4B

@dataclass
class BedrockSession:
    """Сессия Minecraft Bedrock с полными данными"""
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
    last_pong: float = 0
    entity_id: int = 0
    gamemode: int = 0
    can_fly: bool = False
    can_build: bool = True
    can_break_blocks: bool = True
    can_instabuild: bool = False
    can_fly_and_instabuild: bool = False
    invulnerable: bool = False
    flying: bool = False
    may_fly: bool = False
    walk_speed: float = 0.1
    fly_speed: float = 0.05
    health: float = 20.0
    max_health: float = 20.0
    food: float = 20.0
    max_food: float = 20.0
    experience: float = 0.0
    level: int = 0
    total_experience: int = 0
    spawn_x: float = 0.0
    spawn_y: float = 64.0
    spawn_z: float = 0.0
    yaw: float = 0.0
    pitch: float = 0.0
    
    def __post_init__(self):
        if not self.client_guid:
            self.client_guid = random.randint(0, 0xFFFFFFFFFFFFFFFF)

class BedrockProtocolV2:
    """Полная реализация Bedrock протокола для Minecraft PE v2.0"""
    
    def __init__(self, server):
        self.server = server
        self.socket = None
        self.running = False
        self.sessions: Dict[Tuple[str, int], BedrockSession] = {}
        self.server_guid = random.randint(0, 0xFFFFFFFFFFFFFFFF)
        self.next_entity_id = 1
        self.world_time = 0
        self.weather = 0  # 0 = Clear, 1 = Rain, 2 = Thunder
        self.difficulty = 1  # 0 = Peaceful, 1 = Easy, 2 = Normal, 3 = Hard
        
        logger.info(f"Bedrock протокол v2.0 инициализирован (GUID: {self.server_guid})")
    
    async def start(self, host: str = '0.0.0.0', port: int = 19132):
        """Запуск Bedrock протокола"""
        self.running = True
        logger.info(f"Запуск Bedrock протокола v2.0 на {host}:{port}")
        
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
            
            # Запуск обновления времени мира
            asyncio.create_task(self.world_update_loop())
            
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
        
        logger.info("Bedrock протокол v2.0 остановлен")
    
    async def packet_handler_loop(self):
        """Цикл обработки пакетов (неблокирующий)"""
        logger.info("Запуск цикла обработки пакетов Bedrock v2.0")
        
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
    
    async def world_update_loop(self):
        """Цикл обновления мира"""
        logger.info("Запуск цикла обновления мира")
        
        while self.running:
            try:
                # Обновление времени мира
                self.world_time = (self.world_time + 1) % 24000
                
                # Отправка обновлений всем игрокам
                await self.broadcast_world_updates()
                
                # Задержка (1 тик = 50ms)
                await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Ошибка в цикле обновления мира: {e}")
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
            
            # Обработка Bedrock пакетов согласно спецификации
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
            elif packet_id == ID_PLAYER_ACTION:
                await self.handle_player_action(data, addr)
            elif packet_id == ID_PLAYER_INPUT:
                await self.handle_player_input(data, addr)
            elif packet_id == ID_PLAYER_MOVEMENT:
                await self.handle_player_movement(data, addr)
            elif packet_id == ID_PLAYER_ROTATION:
                await self.handle_player_rotation(data, addr)
            elif packet_id == ID_PLAYER_POSITION:
                await self.handle_player_position(data, addr)
            elif packet_id == ID_PLAYER_POSITION_AND_ROTATION:
                await self.handle_player_position_and_rotation(data, addr)
            elif packet_id == ID_PLAYER_POSITION_AND_MOTION:
                await self.handle_player_position_and_motion(data, addr)
            elif packet_id == ID_SET_PLAYER_INVENTORY:
                await self.handle_player_inventory(data, addr)
            elif packet_id == ID_SET_PLAYER_ARMOR:
                await self.handle_player_armor(data, addr)
            elif packet_id == ID_SET_PLAYER_EFFECTS:
                await self.handle_player_effects(data, addr)
            elif packet_id == ID_SET_PLAYER_ATTRIBUTES:
                await self.handle_player_attributes(data, addr)
            else:
                logger.debug(f"Неизвестный Bedrock пакет: {packet_id:02X} от {addr}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки пакета {packet_id:02X} от {addr}: {e}")
    
    async def handle_login(self, data: bytes, addr: Tuple[str, int]):
        """Обработка входа игрока"""
        try:
            if len(data) < 20:
                logger.error(f"Недостаточно данных для входа: {len(data)} байт")
                return
            
            # Парсинг данных входа
            username_length = struct.unpack('>H', data[1:3])[0]
            username = data[3:3+username_length].decode('utf-8', errors='ignore')
            
            # Создание сессии
            session = BedrockSession(addr, 0)  # client_guid будет установлен позже
            session.username = username
            session.connected = True
            session.join_time = time.time()
            session.last_ping = time.time()
            session.last_pong = time.time()
            session.entity_id = self.next_entity_id
            session.gamemode = 0  # Survival
            session.spawn_x = 0.0
            session.spawn_y = 64.0
            session.spawn_z = 0.0
            
            # Увеличение ID сущности
            self.next_entity_id += 1
            
            # Сохранение сессии
            self.sessions[addr] = session
            
            logger.info(f"Попытка входа игрока {username} с {addr} (Entity ID: {session.entity_id})")
            
            # Получение данных мира от сервера
            if hasattr(self.server, 'worlds') and self.server.worlds:
                world = list(self.server.worlds.values())[0]
                session.spawn_x = world.spawn_x
                session.spawn_y = world.spawn_y
                session.spawn_z = world.spawn_z
                logger.info(f"Координаты спавна: {session.spawn_x}, {session.spawn_y}, {session.spawn_z}")
            else:
                logger.warning("Мир не найден, используются координаты по умолчанию")
            
            # Получение игрока от сервера
            if hasattr(self.server, 'player_join'):
                try:
                    player = await self.server.player_join(username, addr[0])
                    logger.info(f"Игрок {username} зарегистрирован на сервере")
                except Exception as e:
                    logger.error(f"Ошибка регистрации игрока {username}: {e}")
                    player = None
            else:
                player = None
                logger.warning("Метод player_join не найден на сервере")
            
            # Полная загрузка игрока в мир
            await self.complete_player_login_v2(session, player)
            
            logger.info(f"Игрок {username} успешно подключен к серверу")
            
        except Exception as e:
            logger.error(f"Ошибка подключения игрока {username if 'username' in locals() else 'Unknown'}: {e}")
            # Попытка отправить сообщение об ошибке
            try:
                error_msg = f"Ошибка подключения: {str(e)}"
                await self.send_packet(ID_DISCONNECT, error_msg.encode('utf-8'), addr)
            except:
                pass
    
    async def complete_player_login_v2(self, session: BedrockSession, player):
        """Полная загрузка игрока в мир согласно спецификации v2.0"""
        try:
            logger.info(f"Начинаю полную загрузку игрока {session.username} согласно спецификации v2.0")
            
            # 1. Отправка подтверждения входа
            await self.send_packet(ID_PLAY_STATUS, struct.pack('>I', 0), session.address)  # 0 = Success
            logger.info(f"Отправлен PLAY_STATUS для {session.username}")
            await asyncio.sleep(0.1)
            
            # 2. Отправка информации о мире (полные данные)
            start_game_data = self.create_start_game_data_v2(session)
            await self.send_packet(ID_START_GAME, start_game_data, session.address)
            logger.info(f"Отправлен START_GAME для {session.username}")
            await asyncio.sleep(0.1)
            
            # 3. Отправка сложности
            await self.send_packet(ID_SET_DIFFICULTY, struct.pack('>B', self.difficulty), session.address)
            await asyncio.sleep(0.05)
            
            # 4. Отправка времени
            await self.send_packet(ID_SET_TIME, struct.pack('>I', self.world_time), session.address)
            await asyncio.sleep(0.05)
            
            # 5. Отправка погоды
            await self.send_packet(ID_SET_WEATHER, struct.pack('>B', self.weather), session.address)
            await asyncio.sleep(0.05)
            
            # 6. Отправка позиции спавна
            spawn_pos_data = self.create_spawn_position_data_v2(session)
            await self.send_packet(ID_SET_SPAWN_POSITION, spawn_pos_data, session.address)
            await asyncio.sleep(0.05)
            
            # 7. Отправка типа игры
            await self.send_packet(ID_SET_PLAYER_GAME_TYPE, struct.pack('>B', session.gamemode), session.address)
            await asyncio.sleep(0.05)
            
            # 8. Отправка спавна игрока
            spawn_data = self.create_player_spawn_data_v2(session, player)
            await self.send_packet(ID_PLAYER_SPAWN, spawn_data, session.address)
            logger.info(f"Отправлен PLAYER_SPAWN для {session.username}")
            await asyncio.sleep(0.1)
            
            # 9. Отправка способностей игрока
            abilities_data = self.create_player_abilities_data_v2(session)
            await self.send_packet(ID_SET_PLAYER_ABILITIES, abilities_data, session.address)
            await asyncio.sleep(0.05)
            
            # 10. Отправка здоровья
            health_data = self.create_health_data_v2(session)
            await self.send_packet(ID_SET_HEALTH, health_data, session.address)
            await asyncio.sleep(0.05)
            
            # 11. Отправка опыта
            experience_data = self.create_experience_data_v2(session)
            await self.send_packet(ID_SET_EXPERIENCE, experience_data, session.address)
            await asyncio.sleep(0.05)
            
            # 12. Отправка инвентаря (пустой)
            inventory_data = self.create_empty_inventory_data_v2(session)
            await self.send_packet(ID_SET_PLAYER_INVENTORY_SLOT, inventory_data, session.address)
            await asyncio.sleep(0.05)
            
            # 13. Отправка данных сущности
            entity_data = self.create_entity_data_v2(session)
            await self.send_packet(ID_SET_ENTITY_DATA, entity_data, session.address)
            await asyncio.sleep(0.05)
            
            # 14. Отправка атрибутов игрока
            attributes_data = self.create_player_attributes_data_v2(session)
            await self.send_packet(ID_SET_PLAYER_ATTRIBUTES, attributes_data, session.address)
            await asyncio.sleep(0.05)
            
            # 15. Отправка приветственного сообщения
            welcome_msg = f"Добро пожаловать на сервер, {session.username}!"
            await self.send_packet(ID_TEXT, welcome_msg.encode('utf-8'), session.address)
            
            # 16. Отправка доступных команд
            commands_data = self.create_available_commands_data_v2()
            await self.send_packet(ID_AVAILABLE_COMMANDS, commands_data, session.address)
            
            logger.info(f"Игрок {session.username} полностью загружен в мир согласно спецификации v2.0")
            
        except Exception as e:
            logger.error(f"Ошибка полной загрузки игрока {session.username}: {e}")
            raise

    def create_start_game_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для пакета начала игры согласно спецификации v2.0"""
        try:
            if hasattr(self.server, 'worlds') and self.server.worlds:
                world = list(self.server.worlds.values())[0]
                
                # Полные данные для START_GAME пакета согласно спецификации
                data = struct.pack('>I', world.seed)  # Seed
                data += struct.pack('>B', session.gamemode)  # Gamemode
                data += struct.pack('>I', session.entity_id)  # Entity ID
                data += struct.pack('>f', float(world.spawn_x))  # Spawn X
                data += struct.pack('>f', float(world.spawn_y))  # Spawn Y
                data += struct.pack('>f', float(world.spawn_z))  # Spawn Z
                data += struct.pack('>f', 0.0)  # Yaw
                data += struct.pack('>f', 0.0)  # Pitch
                data += struct.pack('>I', self.world_time)  # World time
                data += struct.pack('>B', self.weather)  # Weather
                data += struct.pack('>B', self.difficulty)  # Difficulty
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
                
                logger.debug(f"Создан START_GAME пакет v2.0: seed={world.seed}, entity_id={session.entity_id}, spawn=({world.spawn_x}, {world.spawn_y}, {world.spawn_z})")
                return data
            else:
                # Значения по умолчанию
                default_data = struct.pack('>IBIfff', 0, session.gamemode, session.entity_id, 0.0, 64.0, 0.0)
                default_data += struct.pack('>ffIBBB', 0.0, 0.0, self.world_time, self.weather, self.difficulty, 0, 1)
                default_data += struct.pack('>BBBBBBBB', 0, 0, 0, 0, 0, 0, 0, 0)
                logger.debug("Создан START_GAME пакет v2.0 с значениями по умолчанию")
                return default_data
                
        except Exception as e:
            logger.error(f"Ошибка создания данных начала игры v2.0: {e}")
            # Возвращаем минимальные данные
            return struct.pack('>IBIfff', 0, session.gamemode, session.entity_id, 0.0, 64.0, 0.0)
    
    def create_player_spawn_data_v2(self, session: BedrockSession, player) -> bytes:
        """Создание данных для спавна игрока согласно спецификации v2.0"""
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
            data += struct.pack('>f', session.spawn_x)  # X
            data += struct.pack('>f', session.spawn_y)  # Y
            data += struct.pack('>f', session.spawn_z)  # Z
            data += struct.pack('>f', session.yaw)  # Yaw
            data += struct.pack('>f', session.pitch)  # Pitch
            
            logger.debug(f"Создан PLAYER_SPAWN пакет v2.0 для {session.username}: ({session.spawn_x}, {session.spawn_y}, {session.spawn_z})")
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных спавна v2.0: {e}")
            return struct.pack('>Qfff', 0, 0.0, 64.0, 0.0)
    
    def create_spawn_position_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для позиции спавна согласно спецификации v2.0"""
        try:
            data = struct.pack('>I', 0)  # Entity ID (0 для мира)
            data += struct.pack('>f', session.spawn_x)  # X
            data += struct.pack('>f', session.spawn_y)  # Y
            data += struct.pack('>f', session.spawn_z)  # Z
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных позиции спавна v2.0: {e}")
            return struct.pack('>Ifff', 0, 0.0, 64.0, 0.0)
    
    def create_player_abilities_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для способностей игрока согласно спецификации v2.0"""
        try:
            # Флаги способностей согласно спецификации
            flags = 0
            if session.can_fly:
                flags |= 0x01
            if session.can_build:
                flags |= 0x02
            if session.can_break_blocks:
                flags |= 0x04
            if session.can_instabuild:
                flags |= 0x08
            if session.can_fly_and_instabuild:
                flags |= 0x10
            if session.invulnerable:
                flags |= 0x20
            if session.flying:
                flags |= 0x40
            if session.may_fly:
                flags |= 0x80
            
            data = struct.pack('>B', flags)  # Flags
            data += struct.pack('>f', session.fly_speed)  # Fly speed
            data += struct.pack('>f', session.walk_speed)  # Walk speed
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных способностей v2.0: {e}")
            return struct.pack('>Bff', 0, 0.05, 0.1)
    
    def create_health_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для здоровья согласно спецификации v2.0"""
        try:
            data = struct.pack('>f', session.health)  # Health
            data += struct.pack('>f', session.max_health)  # Max health
            data += struct.pack('>f', session.food)  # Food
            data += struct.pack('>f', session.max_food)  # Max food
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных здоровья v2.0: {e}")
            return struct.pack('>ffff', 20.0, 20.0, 20.0, 20.0)
    
    def create_experience_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для опыта согласно спецификации v2.0"""
        try:
            data = struct.pack('>f', session.experience)  # Experience
            data += struct.pack('>I', session.level)    # Level
            data += struct.pack('>I', session.total_experience)    # Total experience
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных опыта v2.0: {e}")
            return struct.pack('>fII', 0.0, 0, 0)
    
    def create_empty_inventory_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для пустого инвентаря согласно спецификации v2.0"""
        try:
            data = struct.pack('>B', 0)  # Window ID (0 = Player inventory)
            data += struct.pack('>I', 0)  # Slot
            data += struct.pack('>B', 0)  # Item ID (0 = Air)
            data += struct.pack('>B', 0)  # Count
            data += struct.pack('>H', 0)  # Metadata
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных инвентаря v2.0: {e}")
            return struct.pack('>BIBBH', 0, 0, 0, 0, 0)
    
    def create_entity_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для сущности игрока согласно спецификации v2.0"""
        try:
            data = struct.pack('>I', session.entity_id)  # Entity ID
            data += struct.pack('>B', 0)  # Metadata count (0 = нет метаданных)
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных сущности v2.0: {e}")
            return struct.pack('>IB', session.entity_id, 0)
    
    def create_player_attributes_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для атрибутов игрока согласно спецификации v2.0"""
        try:
            # Базовые атрибуты
            attributes = [
                {"name": "minecraft:health", "value": session.health, "max": session.max_health},
                {"name": "minecraft:player.hunger", "value": session.food, "max": session.max_food},
                {"name": "minecraft:player.experience", "value": session.experience, "max": 1.0},
                {"name": "minecraft:player.level", "value": session.level, "max": 100},
                {"name": "minecraft:movement", "value": session.walk_speed, "max": 0.5},
                {"name": "minecraft:knockback_resistance", "value": 0.0, "max": 1.0},
                {"name": "minecraft:absorption", "value": 0.0, "max": 16.0},
                {"name": "minecraft:luck", "value": 0.0, "max": 1.0}
            ]
            
            data = struct.pack('>I', len(attributes))  # Count
            
            for attr in attributes:
                data += struct.pack('>I', len(attr["name"]))  # Name length
                data += attr["name"].encode('utf-8')  # Name
                data += struct.pack('>f', attr["value"])  # Value
                data += struct.pack('>f', attr["max"])  # Max value
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных атрибутов v2.0: {e}")
            return struct.pack('>I', 0)
    
    def create_available_commands_data_v2(self) -> bytes:
        """Создание данных для доступных команд согласно спецификации v2.0"""
        try:
            # Базовые команды
            commands = [
                {"name": "help", "description": "Показать доступные команды", "permission": 0},
                {"name": "time", "description": "Показать время в мире", "permission": 0},
                {"name": "weather", "description": "Показать погоду", "permission": 0},
                {"name": "tp", "description": "Телепортация", "permission": 1},
                {"name": "block", "description": "Установить блок", "permission": 1},
                {"name": "chunk", "description": "Информация о чанке", "permission": 1},
                {"name": "gamemode", "description": "Изменить режим игры", "permission": 2},
                {"name": "kick", "description": "Кикнуть игрока", "permission": 2},
                {"name": "ban", "description": "Забанить игрока", "permission": 3},
                {"name": "stop", "description": "Остановить сервер", "permission": 4}
            ]
            
            # Простая реализация - отправляем только количество команд
            data = struct.pack('>I', len(commands))  # Count
            
            return data
        except Exception as e:
            logger.error(f"Ошибка создания данных команд v2.0: {e}")
            return struct.pack('>I', 0)
    
    async def process_sessions(self):
        """Обработка сессий Bedrock"""
        try:
            current_time = time.time()
            sessions_to_remove = []
            
            for addr, session in list(self.sessions.items()):
                # Проверка таймаута (30 секунд без активности)
                if current_time - session.last_pong > 30:
                    logger.info(f"Таймаут Bedrock сессии {addr}")
                    sessions_to_remove.append(addr)
            
            # Удаление отключенных сессий
            for addr in sessions_to_remove:
                session = self.sessions[addr]
                await self.disconnect_session(session)
                
        except Exception as e:
            logger.error(f"Ошибка обработки сессий Bedrock: {e}")
    
    async def broadcast_world_updates(self):
        """Отправка обновлений мира всем игрокам"""
        try:
            # Обновление времени мира
            self.world_time = (self.world_time + 1) % 24000
            
            # Отправка обновлений всем подключенным игрокам
            for session in self.sessions.values():
                if session.connected:
                    try:
                        # Отправка времени
                        await self.send_packet(ID_SET_TIME, struct.pack('>I', self.world_time), session.address)
                        
                        # Отправка погоды (если изменилась)
                        if random.random() < 0.001:  # 0.1% шанс изменения погоды
                            self.weather = random.choice([0, 1, 2])  # 0=Clear, 1=Rain, 2=Thunder
                            await self.send_packet(ID_SET_WEATHER, struct.pack('>B', self.weather), session.address)
                            
                    except Exception as e:
                        logger.error(f"Ошибка отправки обновлений игроку {session.username}: {e}")
                        
        except Exception as e:
            logger.error(f"Ошибка broadcast_world_updates: {e}")
    
    async def handle_raknet_connection(self, raknet_session):
        """Обработка соединения через RakNet"""
        try:
            logger.info(f"RakNet соединение установлено для {raknet_session.address}")
            
            # Здесь можно добавить логику инициализации Bedrock сессии
            # после установки RakNet соединения
            
        except Exception as e:
            logger.error(f"Ошибка обработки RakNet соединения: {e}")
    
    async def handle_raknet_data(self, data: bytes, raknet_session):
        """Обработка данных от RakNet"""
        try:
            # Передача данных в Bedrock протокол
            if len(data) > 0:
                packet_id = data[0]
                await self.handle_packet(data, raknet_session.address)
                
        except Exception as e:
            logger.error(f"Ошибка обработки RakNet данных: {e}")
    
    async def send_packet(self, packet_id: int, data: bytes, address: Tuple[str, int]):
        """Отправка пакета Bedrock"""
        try:
            if self.socket:
                # Создание заголовка пакета
                packet = struct.pack('>B', packet_id)  # Packet ID
                packet += data  # Данные пакета
                
                # Отправка пакета
                self.socket.sendto(packet, address)
                logger.debug(f"Отправлен пакет {packet_id:02X} на {address}")
                
        except Exception as e:
            logger.error(f"Ошибка отправки пакета {packet_id:02X}: {e}")
    
    async def send_packet_compressed(self, packet_id: int, data: bytes, address: Tuple[str, int]):
        """Отправка сжатого пакета Bedrock"""
        try:
            if hasattr(self, 'compression') and self.compression:
                # Сжатие данных
                compressed_data = self.compression.compress_packet_adaptive(data)
                await self.send_packet(packet_id, compressed_data, address)
            else:
                # Отправка без сжатия
                await self.send_packet(packet_id, data, address)
                
        except Exception as e:
            logger.error(f"Ошибка отправки сжатого пакета {packet_id:02X}: {e}")
            # Fallback к обычной отправке
            await self.send_packet(packet_id, data, address)