#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft Bedrock Protocol v2.0 с подробным логированием
"""

import asyncio
import struct
import time
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from server.detailed_logger import detailed_logger

# Настройка логирования
logger = logging.getLogger(__name__)

# Packet IDs для Bedrock Protocol v2.0
ID_LOGIN = 0x01
ID_PLAY_STATUS = 0x02
ID_DISCONNECT = 0x05
ID_TEXT = 0x09
ID_START_GAME = 0x0B
ID_ADD_PLAYER = 0x0C
ID_REMOVE_PLAYER = 0x0D
ID_PLAYER_SPAWN = 0x0E
ID_UPDATE_BLOCK = 0x15
ID_MOVE_PLAYER = 0x16
ID_LEVEL_CHUNK = 0x3A
ID_SET_SPAWN_POSITION = 0x2B
ID_SET_DIFFICULTY = 0x3C
ID_SET_PLAYER_GAME_TYPE = 0x3E
ID_SET_TIME = 0x0A
ID_SET_WEATHER = 0x1B
ID_AVAILABLE_COMMANDS = 0x4F
ID_SET_ENTITY_DATA = 0x27
ID_SET_PLAYER_INVENTORY_SLOT = 0x37
ID_SET_HEALTH = 0x41
ID_SET_EXPERIENCE = 0x42
ID_SET_PLAYER_ABILITIES = 0x3F
ID_PLAYER_ACTION = 0x1C
ID_PLAYER_INPUT = 0x1D
ID_PLAYER_MOVEMENT = 0x1E
ID_PLAYER_ROTATION = 0x1F
ID_PLAYER_POSITION = 0x20
ID_PLAYER_POSITION_AND_ROTATION = 0x21
ID_PLAYER_POSITION_AND_MOTION = 0x22
ID_SET_PLAYER_INVENTORY = 0x38
ID_SET_PLAYER_ARMOR = 0x39
ID_SET_PLAYER_EFFECTS = 0x3A
ID_SET_PLAYER_ATTRIBUTES = 0x3B
ID_SET_PLAYER_PERMISSIONS = 0x3C
ID_ADD_ENTITY = 0x0D
ID_REMOVE_ENTITY = 0x0E
ID_MOVE_ENTITY = 0x0F
ID_ROTATE_HEAD = 0x10
ID_SET_ENTITY_MOTION = 0x11
ID_SET_ENTITY_POSITION = 0x12
ID_SET_ENTITY_POSITION_AND_ROTATION = 0x13
ID_SET_ENTITY_ROTATION = 0x14
ID_SET_ENTITY_LINK = 0x15
ID_SET_ENTITY_COLLISION = 0x16
ID_SET_ENTITY_INVULNERABLE = 0x17
ID_SET_ENTITY_VELOCITY = 0x18
ID_SET_ENTITY_FALL_DISTANCE = 0x19
ID_SET_ENTITY_ON_FIRE = 0x1A
ID_SET_ENTITY_NO_AI = 0x1B
ID_SET_ENTITY_PASSENGER = 0x1C
ID_SET_ENTITY_RIDING = 0x1D
ID_SET_ENTITY_SITTING = 0x1E
ID_SET_ENTITY_SLEEPING = 0x1F
ID_SET_ENTITY_SNEAKING = 0x20
ID_SET_ENTITY_SPRINTING = 0x21
ID_SET_ENTITY_SWIMMING = 0x22
ID_SET_ENTITY_TELEPORTING = 0x23
ID_SET_ENTITY_TICKING = 0x24

@dataclass
class BedrockSession:
    """Сессия Bedrock протокола"""
    address: Tuple[str, int]
    client_guid: int
    username: str = ""
    connected: bool = False
    join_time: float = 0.0
    last_ping: float = 0.0
    last_pong: float = 0.0
    entity_id: int = 0
    gamemode: int = 0
    spawn_x: float = 0.0
    spawn_y: float = 64.0
    spawn_z: float = 0.0
    health: float = 20.0
    max_health: float = 20.0
    experience: int = 0
    level: int = 0
    hunger: int = 20
    max_hunger: int = 20
    armor: int = 0
    permissions: int = 0
    abilities: int = 0
    attributes: Dict[str, float] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {
                'movement': 0.1,
                'jump': 0.42,
                'knockback': 0.0,
                'absorption': 0.0,
                'luck': 0.0
            }

class BedrockProtocolV2:
    """Bedrock Protocol v2.0 с подробным логированием"""
    
    def __init__(self, server):
        self.server = server
        self.sessions: Dict[Tuple[str, int], BedrockSession] = {}
        self.next_entity_id = 1
        self.world_time = 0
        self.weather = 0  # 0 = Clear, 1 = Rain, 2 = Thunder
        self.difficulty = 1  # 0 = Peaceful, 1 = Easy, 2 = Normal, 3 = Hard
        self.socket = None
        
        # Подробный логгер
        self.detailed_logger = detailed_logger
        
        logger.info("Bedrock Protocol v2.0 инициализирован с подробным логированием")
    
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
        """Обработка входа игрока с подробным логированием"""
        try:
            self.detailed_logger.log_connection_attempt(addr, len(data))
            
            if len(data) < 20:
                self.detailed_logger.log_error("LOGIN_DATA_TOO_SHORT", f"Недостаточно данных: {len(data)} байт")
                return
            
            # Парсинг данных входа
            username_length = struct.unpack('>H', data[1:3])[0]
            username = data[3:3+username_length].decode('utf-8', errors='ignore')
            
            # Создание сессии
            session = BedrockSession(addr, 0)
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
            
            self.detailed_logger.log_player_login_start(username, addr, session.entity_id)
            
            # Получение данных мира от сервера
            if hasattr(self.server, 'worlds') and self.server.worlds:
                world = list(self.server.worlds.values())[0]
                session.spawn_x = world.spawn_x
                session.spawn_y = world.spawn_y
                session.spawn_z = world.spawn_z
                self.detailed_logger.log_debug_info("WORLD_SPAWN", f"Координаты: {session.spawn_x}, {session.spawn_y}, {session.spawn_z}")
            else:
                self.detailed_logger.log_error("WORLD_NOT_FOUND", "Мир не найден, используются координаты по умолчанию")
            
            # Получение игрока от сервера
            if hasattr(self.server, 'player_join'):
                try:
                    player = await self.server.player_join(username, addr[0])
                    self.detailed_logger.log_player_login_step(username, "PLAYER_REGISTERED", "на сервере")
                except Exception as e:
                    self.detailed_logger.log_error("PLAYER_REGISTRATION_FAILED", f"Ошибка регистрации: {e}")
                    player = None
            else:
                player = None
                self.detailed_logger.log_error("PLAYER_JOIN_METHOD_MISSING", "Метод player_join не найден")
            
            # Полная загрузка игрока в мир
            await self.complete_player_login_v2(session, player)
            
            self.detailed_logger.log_player_login_complete(username)
            
        except Exception as e:
            import traceback
            self.detailed_logger.log_error("LOGIN_PROCESSING_FAILED", f"Ошибка подключения игрока {username if 'username' in locals() else 'Unknown'}: {e}", traceback.format_exc())
            
            # Попытка отправить сообщение об ошибке
            try:
                error_msg = f"Ошибка подключения: {str(e)}"
                await self.send_packet(ID_DISCONNECT, error_msg.encode('utf-8'), addr)
            except:
                pass
    
    async def complete_player_login_v2(self, session: BedrockSession, player):
        """Полная загрузка игрока в мир с подробным логированием"""
        try:
            username = session.username
            self.detailed_logger.log_player_login_step(username, "LOGIN_SEQUENCE_START", "начало последовательности")
            
            # 1. Отправка подтверждения входа
            self.detailed_logger.log_player_login_step(username, "SENDING_PLAY_STATUS", "подтверждение входа")
            await self.send_packet(ID_PLAY_STATUS, struct.pack('>I', 0), session.address)  # 0 = Success
            await asyncio.sleep(0.3)  # Увеличиваем задержку
            
            # 2. Отправка информации о мире
            self.detailed_logger.log_player_login_step(username, "SENDING_START_GAME", "информация о мире")
            start_game_data = self.create_start_game_data_v2(session)
            await self.send_packet(ID_START_GAME, start_game_data, session.address)
            await asyncio.sleep(0.5)  # Увеличиваем задержку
            
            # 3. Отправка сложности
            self.detailed_logger.log_player_login_step(username, "SENDING_DIFFICULTY", f"сложность: {self.difficulty}")
            await self.send_packet(ID_SET_DIFFICULTY, struct.pack('>B', self.difficulty), session.address)
            await asyncio.sleep(0.2)
            
            # 4. Отправка времени
            self.detailed_logger.log_player_login_step(username, "SENDING_TIME", f"время: {self.world_time}")
            await self.send_packet(ID_SET_TIME, struct.pack('>I', self.world_time), session.address)
            await asyncio.sleep(0.2)
            
            # 5. Отправка погоды
            self.detailed_logger.log_player_login_step(username, "SENDING_WEATHER", f"погода: {self.weather}")
            await self.send_packet(ID_SET_WEATHER, struct.pack('>B', self.weather), session.address)
            await asyncio.sleep(0.2)
            
            # 6. Отправка позиции спавна
            self.detailed_logger.log_player_login_step(username, "SENDING_SPAWN_POSITION", f"спавн: ({session.spawn_x}, {session.spawn_y}, {session.spawn_z})")
            spawn_pos_data = self.create_spawn_position_data_v2(session)
            await self.send_packet(ID_SET_SPAWN_POSITION, spawn_pos_data, session.address)
            await asyncio.sleep(0.2)
            
            # 7. Отправка типа игры
            self.detailed_logger.log_player_login_step(username, "SENDING_GAME_TYPE", f"тип игры: {session.gamemode}")
            await self.send_packet(ID_SET_PLAYER_GAME_TYPE, struct.pack('>B', session.gamemode), session.address)
            await asyncio.sleep(0.2)
            
            # 8. Отправка спавна игрока
            self.detailed_logger.log_player_login_step(username, "SENDING_PLAYER_SPAWN", "спавн игрока")
            spawn_data = self.create_player_spawn_data_v2(session, player)
            await self.send_packet(ID_PLAYER_SPAWN, spawn_data, session.address)
            await asyncio.sleep(0.3)
            
            # 9. Отправка способностей игрока
            self.detailed_logger.log_player_login_step(username, "SENDING_PLAYER_ABILITIES", "способности")
            abilities_data = self.create_player_abilities_data_v2(session)
            await self.send_packet(ID_SET_PLAYER_ABILITIES, abilities_data, session.address)
            await asyncio.sleep(0.2)
            
            # 10. Отправка здоровья
            self.detailed_logger.log_player_login_step(username, "SENDING_HEALTH", f"здоровье: {session.health}/{session.max_health}")
            health_data = self.create_health_data_v2(session)
            await self.send_packet(ID_SET_HEALTH, health_data, session.address)
            await asyncio.sleep(0.2)
            
            # 11. Отправка опыта
            self.detailed_logger.log_player_login_step(username, "SENDING_EXPERIENCE", f"опыт: {session.experience}, уровень: {session.level}")
            experience_data = self.create_experience_data_v2(session)
            await self.send_packet(ID_SET_EXPERIENCE, experience_data, session.address)
            await asyncio.sleep(0.2)
            
            # 12. Отправка инвентаря
            self.detailed_logger.log_player_login_step(username, "SENDING_INVENTORY", "инвентарь")
            inventory_data = self.create_empty_inventory_data_v2(session)
            await self.send_packet(ID_SET_PLAYER_INVENTORY_SLOT, inventory_data, session.address)
            await asyncio.sleep(0.2)
            
            # 13. Отправка данных сущности
            self.detailed_logger.log_player_login_step(username, "SENDING_ENTITY_DATA", "данные сущности")
            entity_data = self.create_entity_data_v2(session)
            await self.send_packet(ID_SET_ENTITY_DATA, entity_data, session.address)
            await asyncio.sleep(0.2)
            
            # 14. Отправка атрибутов игрока
            self.detailed_logger.log_player_login_step(username, "SENDING_PLAYER_ATTRIBUTES", "атрибуты")
            attributes_data = self.create_player_attributes_data_v2(session)
            await self.send_packet(ID_SET_PLAYER_ATTRIBUTES, attributes_data, session.address)
            await asyncio.sleep(0.2)
            
            # 15. Отправка приветственного сообщения
            self.detailed_logger.log_player_login_step(username, "SENDING_WELCOME_MESSAGE", "приветствие")
            welcome_msg = f"Добро пожаловать на сервер, {session.username}!"
            await self.send_packet(ID_TEXT, welcome_msg.encode('utf-8'), session.address)
            await asyncio.sleep(0.2)
            
            # 16. Отправка доступных команд
            self.detailed_logger.log_player_login_step(username, "SENDING_AVAILABLE_COMMANDS", "команды")
            commands_data = self.create_available_commands_data_v2()
            await self.send_packet(ID_AVAILABLE_COMMANDS, commands_data, session.address)
            await asyncio.sleep(0.2)
            
            # 17. Отправка чанков мира (ВАЖНО!)
            self.detailed_logger.log_player_login_step(username, "SENDING_WORLD_CHUNKS", "чанки мира")
            await self.send_world_chunks(session)
            
            self.detailed_logger.log_player_login_step(username, "LOGIN_SEQUENCE_COMPLETE", "последовательность завершена")
            
        except Exception as e:
            import traceback
            self.detailed_logger.log_error("LOGIN_SEQUENCE_FAILED", f"Ошибка полной загрузки игрока {session.username}: {e}", traceback.format_exc())
            raise
    
    async def send_world_chunks(self, session: BedrockSession):
        """Отправка чанков мира игроку"""
        try:
            logger.info(f"Отправка чанков мира для {session.username}")
            
            # Отправляем центральный чанк и соседние
            chunk_coords = [
                (0, 0),   # Центральный
                (-1, 0),  # Западный
                (1, 0),   # Восточный
                (0, -1),  # Северный
                (0, 1),   # Южный
            ]
            
            for chunk_x, chunk_z in chunk_coords:
                try:
                    # Получаем чанк от менеджера чанков
                    if hasattr(self.server, 'chunk_manager') and self.server.chunk_manager:
                        chunk = self.server.chunk_manager.get_chunk(chunk_x, chunk_z)
                        chunk_data = chunk.serialize()
                        
                        # Отправляем чанк
                        chunk_packet = struct.pack('>I', chunk_x)  # Chunk X
                        chunk_packet += struct.pack('>I', chunk_z)  # Chunk Z
                        chunk_packet += chunk_data
                        
                        await self.send_packet(ID_LEVEL_CHUNK, chunk_packet, session.address)
                        logger.info(f"Отправлен чанк ({chunk_x}, {chunk_z}) для {session.username}")
                        await asyncio.sleep(0.1)  # Небольшая задержка между чанками
                        
                except Exception as e:
                    logger.error(f"Ошибка отправки чанка ({chunk_x}, {chunk_z}): {e}")
            
            logger.info(f"Все чанки отправлены для {session.username}")
            
        except Exception as e:
            logger.error(f"Ошибка отправки чанков мира для {session.username}: {e}")
    
    def create_start_game_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для пакета начала игры"""
        try:
            if hasattr(self.server, 'worlds') and self.server.worlds:
                world = list(self.server.worlds.values())[0]
                
                # Основные данные мира
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
                
                # Минимальные флаги мира
                for _ in range(50):  # Упрощенная версия
                    data += struct.pack('>B', 0)
                
                return data
            else:
                self.detailed_logger.log_error("WORLD_NOT_FOUND", "Мир не найден для START_GAME")
                return struct.pack('>I', 0)
                
        except Exception as e:
            self.detailed_logger.log_error("START_GAME_DATA_CREATION_FAILED", f"Ошибка создания данных START_GAME: {e}")
            return struct.pack('>I', 0)
    
    def create_player_spawn_data_v2(self, session: BedrockSession, player) -> bytes:
        """Создание данных для спавна игрока"""
        try:
            data = struct.pack('>I', session.entity_id)  # Entity ID
            data += struct.pack('>f', session.spawn_x)  # X
            data += struct.pack('>f', session.spawn_y)  # Y
            data += struct.pack('>f', session.spawn_z)  # Z
            data += struct.pack('>f', 0.0)  # Yaw
            data += struct.pack('>f', 0.0)  # Pitch
            data += struct.pack('>B', 0)  # Flags
            
            return data
            
        except Exception as e:
            self.detailed_logger.log_error("PLAYER_SPAWN_DATA_CREATION_FAILED", f"Ошибка создания данных PLAYER_SPAWN: {e}")
            return struct.pack('>I', 0)
    
    def create_spawn_position_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для позиции спавна"""
        try:
            data = struct.pack('>I', 0)  # Spawn type
            data += struct.pack('>f', session.spawn_x)  # X
            data += struct.pack('>f', session.spawn_y)  # Y
            data += struct.pack('>f', session.spawn_z)  # Z
            data += struct.pack('>B', 0)  # Dimension
            
            return data
            
        except Exception as e:
            self.detailed_logger.log_error("SPAWN_POSITION_DATA_CREATION_FAILED", f"Ошибка создания данных SPAWN_POSITION: {e}")
            return struct.pack('>I', 0)
    
    def create_player_abilities_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для способностей игрока"""
        try:
            data = struct.pack('>B', 0)  # Flags
            data += struct.pack('>f', 0.1)  # Fly speed
            data += struct.pack('>f', 0.05)  # Walk speed
            
            return data
            
        except Exception as e:
            self.detailed_logger.log_error("PLAYER_ABILITIES_DATA_CREATION_FAILED", f"Ошибка создания данных PLAYER_ABILITIES: {e}")
            return struct.pack('>B', 0)
    
    def create_health_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для здоровья"""
        try:
            data = struct.pack('>f', session.health)  # Health
            data += struct.pack('>f', session.max_health)  # Max health
            data += struct.pack('>I', 0)  # Hunger
            data += struct.pack('>I', 20)  # Max hunger
            
            return data
            
        except Exception as e:
            self.detailed_logger.log_error("HEALTH_DATA_CREATION_FAILED", f"Ошибка создания данных HEALTH: {e}")
            return struct.pack('>f', 20.0)
    
    def create_experience_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для опыта"""
        try:
            data = struct.pack('>I', session.experience)  # Experience
            data += struct.pack('>I', session.level)  # Level
            data += struct.pack('>I', 0)  # Total experience
            
            return data
            
        except Exception as e:
            self.detailed_logger.log_error("EXPERIENCE_DATA_CREATION_FAILED", f"Ошибка создания данных EXPERIENCE: {e}")
            return struct.pack('>I', 0)
    
    def create_empty_inventory_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для пустого инвентаря"""
        try:
            data = struct.pack('>B', 0)  # Window ID
            data += struct.pack('>I', 0)  # Slot
            data += struct.pack('>B', 0)  # Item ID
            data += struct.pack('>B', 0)  # Count
            data += struct.pack('>H', 0)  # Metadata
            
            return data
            
        except Exception as e:
            self.detailed_logger.log_error("INVENTORY_DATA_CREATION_FAILED", f"Ошибка создания данных INVENTORY: {e}")
            return struct.pack('>B', 0)
    
    def create_entity_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для сущности"""
        try:
            data = struct.pack('>I', session.entity_id)  # Entity ID
            data += struct.pack('>B', 0)  # Metadata count
            
            return data
            
        except Exception as e:
            self.detailed_logger.log_error("ENTITY_DATA_CREATION_FAILED", f"Ошибка создания данных ENTITY: {e}")
            return struct.pack('>I', 0)
    
    def create_player_attributes_data_v2(self, session: BedrockSession) -> bytes:
        """Создание данных для атрибутов игрока"""
        try:
            data = struct.pack('>I', session.entity_id)  # Entity ID
            
            # Атрибуты
            attributes = [
                ('movement', 0.1),
                ('jump', 0.42),
                ('knockback', 0.0),
                ('absorption', 0.0),
                ('luck', 0.0)
            ]
            
            data += struct.pack('>I', len(attributes))  # Count
            
            for name, value in attributes:
                name_bytes = name.encode('utf-8')
                data += struct.pack('>H', len(name_bytes))  # Name length
                data += name_bytes  # Name
                data += struct.pack('>f', value)  # Value
                data += struct.pack('>f', value)  # Max value
            
            return data
            
        except Exception as e:
            self.detailed_logger.log_error("PLAYER_ATTRIBUTES_DATA_CREATION_FAILED", f"Ошибка создания данных PLAYER_ATTRIBUTES: {e}")
            return struct.pack('>I', 0)
    
    def create_available_commands_data_v2(self) -> bytes:
        """Создание данных для доступных команд"""
        try:
            data = struct.pack('>I', 0)  # Command count
            data += struct.pack('>I', 0)  # Unknown
            
            return data
            
        except Exception as e:
            self.detailed_logger.log_error("AVAILABLE_COMMANDS_DATA_CREATION_FAILED", f"Ошибка создания данных AVAILABLE_COMMANDS: {e}")
            return struct.pack('>I', 0)
    
    async def send_world_chunks(self, session: BedrockSession):
        """Отправка чанков мира игроку с подробным логированием"""
        try:
            username = session.username
            self.detailed_logger.log_player_login_step(username, "CHUNK_SENDING_START", "начало отправки чанков")
            
            # Отправляем центральный чанк и соседние
            chunk_coords = [
                (0, 0),   # Центральный
                (-1, 0),  # Западный
                (1, 0),   # Восточный
                (0, -1),  # Северный
                (0, 1),   # Южный
            ]
            
            for chunk_x, chunk_z in chunk_coords:
                try:
                    # Получаем чанк от менеджера чанков
                    if hasattr(self.server, 'chunk_manager') and self.server.chunk_manager:
                        chunk = self.server.chunk_manager.get_chunk(chunk_x, chunk_z)
                        chunk_data = chunk.serialize()
                        
                        # Отправляем чанк
                        chunk_packet = struct.pack('>I', chunk_x)  # Chunk X
                        chunk_packet += struct.pack('>I', chunk_z)  # Chunk Z
                        chunk_packet += chunk_data
                        
                        await self.send_packet(ID_LEVEL_CHUNK, chunk_packet, session.address)
                        
                        # Логирование
                        self.detailed_logger.log_chunk_sent(username, chunk_x, chunk_z, len(chunk_data))
                        self.detailed_logger.log_player_login_step(username, "CHUNK_SENT", f"чанк ({chunk_x}, {chunk_z})")
                        
                        await asyncio.sleep(0.1)  # Небольшая задержка между чанками
                        
                    else:
                        self.detailed_logger.log_error("CHUNK_MANAGER_MISSING", f"Менеджер чанков не найден для чанка ({chunk_x}, {chunk_z})")
                        
                except Exception as e:
                    self.detailed_logger.log_error("CHUNK_SEND_FAILED", f"Ошибка отправки чанка ({chunk_x}, {chunk_z}): {e}")
            
            self.detailed_logger.log_player_login_step(username, "CHUNK_SENDING_COMPLETE", "все чанки отправлены")
            
        except Exception as e:
            import traceback
            self.detailed_logger.log_error("WORLD_CHUNKS_SENDING_FAILED", f"Ошибка отправки чанков мира для {session.username}: {e}", traceback.format_exc())
    
    async def process_sessions(self):
        """Обработка сессий"""
        try:
            current_time = time.time()
            disconnected_sessions = []
            
            for addr, session in self.sessions.items():
                # Проверка таймаута
                if current_time - session.last_pong > 30:  # 30 секунд таймаут
                    disconnected_sessions.append(addr)
                    self.detailed_logger.log_debug_info("SESSION_TIMEOUT", f"Сессия {session.username} истекла")
                
                # Обновление времени мира
                if current_time - session.last_ping > 1:  # Каждую секунду
                    session.last_ping = current_time
                    self.world_time += 20  # 20 тиков = 1 секунда
            
            # Удаление отключенных сессий
            for addr in disconnected_sessions:
                session = self.sessions.pop(addr)
                self.detailed_logger.log_debug_info("SESSION_REMOVED", f"Сессия {session.username} удалена")
                
        except Exception as e:
            self.detailed_logger.log_error("SESSIONS_PROCESSING_FAILED", f"Ошибка обработки сессий: {e}")
    
    async def broadcast_world_updates(self):
        """Отправка обновлений мира всем игрокам"""
        try:
            if not self.sessions:
                return
            
            # Обновление времени
            for addr, session in self.sessions.items():
                try:
                    await self.send_packet(ID_SET_TIME, struct.pack('>I', self.world_time), addr)
                except Exception as e:
                    self.detailed_logger.log_error("TIME_UPDATE_FAILED", f"Ошибка обновления времени для {session.username}: {e}")
                    
        except Exception as e:
            self.detailed_logger.log_error("WORLD_UPDATES_BROADCAST_FAILED", f"Ошибка отправки обновлений мира: {e}")
    
    async def handle_raknet_connection(self, data: bytes, addr: Tuple[str, int]):
        """Обработка RakNet подключения"""
        try:
            self.detailed_logger.log_debug_info("RAKNET_CONNECTION", f"RakNet подключение от {addr}")
            # Здесь будет обработка RakNet пакетов
            pass
        except Exception as e:
            self.detailed_logger.log_error("RAKNET_CONNECTION_FAILED", f"Ошибка обработки RakNet подключения: {e}")
    
    async def handle_raknet_data(self, data: bytes, addr: Tuple[str, int]):
        """Обработка RakNet данных"""
        try:
            self.detailed_logger.log_debug_info("RAKNET_DATA", f"RakNet данные от {addr}, размер: {len(data)}")
            # Здесь будет обработка RakNet данных
            pass
        except Exception as e:
            self.detailed_logger.log_error("RAKNET_DATA_FAILED", f"Ошибка обработки RakNet данных: {e}")