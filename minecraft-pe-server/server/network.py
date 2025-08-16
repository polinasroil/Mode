#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Сетевой модуль
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import asyncio
import socket
import struct
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Packet:
    """Базовый класс для пакетов Minecraft PE"""
    packet_id: int
    data: bytes
    
    def encode(self) -> bytes:
        """Кодирование пакета"""
        return struct.pack('>B', self.packet_id) + self.data
    
    @classmethod
    def decode(cls, data: bytes) -> 'Packet':
        """Декодирование пакета"""
        if len(data) < 1:
            raise ValueError("Недостаточно данных для декодирования пакета")
        
        packet_id = data[0]
        packet_data = data[1:]
        
        return cls(packet_id, packet_data)

class MinecraftPENetworkProtocol:
    """Протокол сетевого взаимодействия Minecraft PE"""
    
    # Константы протокола
    PROTOCOL_VERSION = 662  # Minecraft PE 1.20.50
    RAKNET_PROTOCOL_VERSION = 11
    
    # Типы пакетов
    PACKET_LOGIN = 0x01
    PACKET_PLAY_STATUS = 0x02
    PACKET_DISCONNECT = 0x05
    PACKET_TEXT = 0x09
    PACKET_START_GAME = 0x0B
    PACKET_ADD_PLAYER = 0x0C
    PACKET_REMOVE_PLAYER = 0x0D
    PACKET_MOVE_PLAYER = 0x13
    PACKET_LEVEL_CHUNK = 0x3A
    PACKET_SET_ENTITY_DATA = 0x27
    PACKET_PLAYER_SPAWN = 0x0E
    PACKET_UPDATE_BLOCK = 0x15
    
    def __init__(self, server):
        self.server = server
        self.clients: Dict[str, 'MinecraftPEClient'] = {}
        self.running = False
        
    async def start(self, host: str = '0.0.0.0', port: int = 19132):
        """Запуск сетевого протокола"""
        self.running = True
        logger.info(f"Запуск сетевого протокола на {host}:{port}")
        
        try:
            # Создание UDP сокета
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((host, port))
            
            # Запуск обработчика пакетов
            await self.packet_handler()
            
        except Exception as e:
            logger.error(f"Ошибка запуска сетевого протокола: {e}")
            raise
    
    async def stop(self):
        """Остановка сетевого протокола"""
        self.running = False
        
        # Отключение всех клиентов
        for client in list(self.clients.values()):
            await self.disconnect_client(client)
        
        if hasattr(self, 'socket'):
            self.socket.close()
        
        logger.info("Сетевой протокол остановлен")
    
    async def packet_handler(self):
        """Обработчик входящих пакетов"""
        while self.running:
            try:
                # Неблокирующее чтение данных
                self.socket.setblocking(False)
                
                try:
                    data, addr = self.socket.recvfrom(4096)
                    if data:
                        await self.handle_packet(data, addr)
                except BlockingIOError:
                    # Нет данных для чтения
                    await asyncio.sleep(0.001)  # 1ms
                except Exception as e:
                    logger.error(f"Ошибка чтения данных: {e}")
                
            except Exception as e:
                logger.error(f"Ошибка в обработчике пакетов: {e}")
                await asyncio.sleep(0.1)
    
    async def handle_packet(self, data: bytes, addr: Tuple[str, int]):
        """Обработка входящего пакета"""
        try:
            # Определение типа пакета
            if len(data) < 1:
                return
            
            packet_type = data[0]
            
            if packet_type == self.PACKET_LOGIN:
                await self.handle_login(data, addr)
            elif packet_type == self.PACKET_TEXT:
                await self.handle_text(data, addr)
            elif packet_type == self.PACKET_MOVE_PLAYER:
                await self.handle_move_player(data, addr)
            elif packet_type == self.PACKET_UPDATE_BLOCK:
                await self.handle_update_block(data, addr)
            else:
                # Логирование неизвестного пакета
                logger.debug(f"Неизвестный пакет типа {packet_type} от {addr}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки пакета от {addr}: {e}")
    
    async def handle_login(self, data: bytes, addr: Tuple[str, int]):
        """Обработка пакета входа"""
        try:
            # Парсинг данных входа
            username = self.parse_login_data(data)
            ip_address = addr[0]
            
            logger.info(f"Попытка входа игрока {username} с {ip_address}")
            
            # Создание клиента
            client = MinecraftPEClient(username, ip_address, addr)
            self.clients[username] = client
            
            # Подключение игрока к серверу
            player = await self.server.player_join(username, ip_address)
            
            # Отправка подтверждения входа
            await self.send_login_success(client)
            
            # Отправка информации о мире
            await self.send_start_game(client)
            
            # Отправка точки спавна
            await self.send_player_spawn(client)
            
            # Отправка ближайших чанков
            await self.send_nearby_chunks(client)
            
            # Уведомление других игроков
            await self.broadcast_player_join(username)
            
            logger.info(f"Игрок {username} успешно подключился")
            
        except Exception as e:
            logger.error(f"Ошибка обработки входа: {e}")
            # Отправка ошибки клиенту
            await self.send_disconnect(addr, str(e))
    
    def parse_login_data(self, data: bytes) -> str:
        """Парсинг данных входа из пакета"""
        try:
            # Простая реализация парсинга
            # В реальном протоколе здесь будет более сложная логика
            if len(data) > 1:
                # Извлекаем имя пользователя (упрощенно)
                username_data = data[1:]
                username = username_data.decode('utf-8', errors='ignore').split('\x00')[0]
                return username
            else:
                return "UnknownPlayer"
        except Exception as e:
            logger.error(f"Ошибка парсинга данных входа: {e}")
            return "UnknownPlayer"
    
    async def handle_text(self, data: bytes, addr: Tuple[str, int]):
        """Обработка текстового сообщения"""
        try:
            # Находим клиента по адресу
            client = self.find_client_by_addr(addr)
            if not client:
                return
            
            # Парсинг сообщения
            message = self.parse_text_data(data)
            logger.info(f"Сообщение от {client.username}: {message}")
            
            # Обработка команд
            if message.startswith('/'):
                await self.handle_command(client, message)
            else:
                # Отправка сообщения всем игрокам
                await self.broadcast_message(f"<{client.username}> {message}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки текста: {e}")
    
    def parse_text_data(self, data: bytes) -> str:
        """Парсинг текстовых данных"""
        try:
            if len(data) > 1:
                text_data = data[1:]
                return text_data.decode('utf-8', errors='ignore')
            else:
                return ""
        except Exception as e:
            logger.error(f"Ошибка парсинга текста: {e}")
            return ""
    
    async def handle_move_player(self, data: bytes, addr: Tuple[str, int]):
        """Обработка движения игрока"""
        try:
            client = self.find_client_by_addr(addr)
            if not client:
                return
            
            # Парсинг координат
            x, y, z = self.parse_move_data(data)
            
            # Обновление позиции игрока
            if client.username in self.server.players:
                player = self.server.players[client.username]
                player.spawn_x = x
                player.spawn_y = y
                player.spawn_z = z
                
                # Отправка обновления другим игрокам
                await self.broadcast_player_move(client.username, x, y, z)
                
        except Exception as e:
            logger.error(f"Ошибка обработки движения: {e}")
    
    async def handle_update_block(self, data: bytes, addr: Tuple[str, int]):
        """Обработка обновления блока"""
        try:
            client = self.find_client_by_addr(addr)
            if not client:
                return
            
            # Парсинг данных блока
            if len(data) >= 13:
                x = struct.unpack('>i', data[1:5])[0]
                y = struct.unpack('>B', data[5:6])[0]
                z = struct.unpack('>i', data[6:10])[0]
                block_id = struct.unpack('>B', data[10:11])[0]
                metadata = struct.unpack('>B', data[11:12])[0]
                
                # Обновление блока в мире
                if hasattr(self.server, 'worlds') and self.server.worlds:
                    world = list(self.server.worlds.values())[0]
                    world.set_block(x, y, z, block_id, metadata)
                    
                    # Отправка обновления всем игрокам
                    await self.broadcast_block_update(x, y, z, block_id, metadata)
                    
                    logger.debug(f"Блок обновлен: {x}, {y}, {z} -> {block_id}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки обновления блока: {e}")
    
    def parse_move_data(self, data: bytes) -> Tuple[float, float, float]:
        """Парсинг данных движения"""
        try:
            if len(data) >= 13:  # Минимальный размер для координат
                x = struct.unpack('>f', data[1:5])[0]
                y = struct.unpack('>f', data[5:9])[0]
                z = struct.unpack('>f', data[9:13])[0]
                return x, y, z
            else:
                return 0.0, 64.0, 0.0
        except Exception as e:
            logger.error(f"Ошибка парсинга движения: {e}")
            return 0.0, 64.0, 0.0
    
    async def handle_command(self, client: 'MinecraftPEClient', command: str):
        """Обработка команд"""
        try:
            parts = command.split()
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            if cmd == '/help':
                await self.send_message(client, "Доступные команды: /help, /time, /weather, /tp, /block, /chunk")
            elif cmd == '/time':
                if hasattr(self.server, 'worlds') and self.server.worlds:
                    world = list(self.server.worlds.values())[0]
                    time_str = world.get_time_string()
                    await self.send_message(client, f"Время: {time_str}")
            elif cmd == '/weather':
                if hasattr(self.server, 'worlds') and self.server.worlds:
                    world = list(self.server.worlds.values())[0]
                    weather_str = world.get_weather_string()
                    await self.send_message(client, f"Погода: {weather_str}")
            elif cmd == '/tp' and len(args) >= 3:
                try:
                    x, y, z = map(float, args[:3])
                    # Телепортация игрока
                    await self.send_message(client, f"Телепортация на координаты {x}, {y}, {z}")
                except ValueError:
                    await self.send_message(client, "Неверные координаты")
            elif cmd == '/block' and len(args) >= 4:
                try:
                    x, y, z, block_id = map(int, args[:4])
                    metadata = int(args[4]) if len(args) > 4 else 0
                    
                    # Установка блока
                    if hasattr(self.server, 'worlds') and self.server.worlds:
                        world = list(self.server.worlds.values())[0]
                        world.set_block(x, y, z, block_id, metadata)
                        await self.broadcast_block_update(x, y, z, block_id, metadata)
                        await self.send_message(client, f"Блок установлен: {x}, {y}, {z} -> {block_id}")
                except ValueError:
                    await self.send_message(client, "Неверные параметры блока")
            elif cmd == '/chunk':
                if hasattr(self.server, 'worlds') and self.server.worlds:
                    world = list(self.server.worlds.values())[0]
                    chunk_info = f"Загружено чанков: {len(world.loaded_chunks)}"
                    await self.send_message(client, chunk_info)
            else:
                await self.send_message(client, f"Неизвестная команда: {cmd}")
                
        except Exception as e:
            logger.error(f"Ошибка обработки команды: {e}")
            await self.send_message(client, "Ошибка выполнения команды")
    
    async def send_login_success(self, client: 'MinecraftPEClient'):
        """Отправка подтверждения входа"""
        try:
            # Создание пакета подтверждения
            packet_data = struct.pack('>I', self.PROTOCOL_VERSION)
            packet = Packet(self.PACKET_PLAY_STATUS, packet_data)
            
            await self.send_packet(client.addr, packet)
            
        except Exception as e:
            logger.error(f"Ошибка отправки подтверждения входа: {e}")
    
    async def send_start_game(self, client: 'MinecraftPEClient'):
        """Отправка информации о начале игры"""
        try:
            if hasattr(self.server, 'worlds') and self.server.worlds:
                world = list(self.server.worlds.values())[0]
                
                # Создание пакета начала игры
                packet_data = struct.pack('>I', world.seed)
                packet_data += struct.pack('>B', 0)  # Gamemode
                packet_data += struct.pack('>B', 0)  # Entity ID
                packet_data += struct.pack('>f', float(world.spawn_x))
                packet_data += struct.pack('>f', float(world.spawn_y))
                packet_data += struct.pack('>f', float(world.spawn_z))
                
                packet = Packet(self.PACKET_START_GAME, packet_data)
                await self.send_packet(client.addr, packet)
            
        except Exception as e:
            logger.error(f"Ошибка отправки начала игры: {e}")
    
    async def send_player_spawn(self, client: 'MinecraftPEClient'):
        """Отправка точки спавна игрока"""
        try:
            if hasattr(self.server, 'worlds') and self.server.worlds:
                world = list(self.server.worlds.values())[0]
                
                # Пакет спавна игрока
                packet_data = struct.pack('>f', float(world.spawn_x))
                packet_data += struct.pack('>f', float(world.spawn_y))
                packet_data += struct.pack('>f', float(world.spawn_z))
                
                packet = Packet(self.PACKET_PLAYER_SPAWN, packet_data)
                await self.send_packet(client.addr, packet)
                
        except Exception as e:
            logger.error(f"Ошибка отправки спавна игрока: {e}")
    
    async def send_nearby_chunks(self, client: 'MinecraftPEClient'):
        """Отправка ближайших чанков"""
        try:
            if hasattr(self.server, 'worlds') and self.server.worlds:
                world = list(self.server.worlds.values())[0]
                
                # Отправка чанков в радиусе 2 от спавна
                spawn_chunk_x = world.spawn_x // 16
                spawn_chunk_z = world.spawn_z // 16
                
                for chunk_x in range(spawn_chunk_x - 2, spawn_chunk_x + 3):
                    for chunk_z in range(spawn_chunk_z - 2, spawn_chunk_z + 3):
                        chunk = world.get_chunk(chunk_x, chunk_z)
                        if chunk:
                            await self.send_chunk(client, chunk)
                            
        except Exception as e:
            logger.error(f"Ошибка отправки чанков: {e}")
    
    async def send_chunk(self, client: 'MinecraftPEClient', chunk):
        """Отправка чанка клиенту"""
        try:
            chunk_data = chunk.get_chunk_data()
            if chunk_data:
                packet = Packet(self.PACKET_LEVEL_CHUNK, chunk_data)
                await self.send_packet(client.addr, packet)
                
        except Exception as e:
            logger.error(f"Ошибка отправки чанка: {e}")
    
    async def send_disconnect(self, addr: Tuple[str, int], reason: str):
        """Отправка отключения"""
        try:
            packet_data = reason.encode('utf-8')
            packet = Packet(self.PACKET_DISCONNECT, packet_data)
            await self.send_packet(addr, packet)
            
        except Exception as e:
            logger.error(f"Ошибка отправки отключения: {e}")
    
    async def send_message(self, client: 'MinecraftPEClient', message: str):
        """Отправка сообщения клиенту"""
        try:
            packet_data = message.encode('utf-8')
            packet = Packet(self.PACKET_TEXT, packet_data)
            await self.send_packet(client.addr, packet)
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
    
    async def broadcast_message(self, message: str):
        """Отправка сообщения всем игрокам"""
        for client in self.clients.values():
            await self.send_message(client, message)
    
    async def broadcast_player_join(self, username: str):
        """Уведомление о подключении игрока"""
        message = f"§e{username} присоединился к игре"
        await self.broadcast_message(message)
    
    async def broadcast_player_move(self, username: str, x: float, y: float, z: float):
        """Уведомление о движении игрока"""
        # В реальной реализации здесь будет отправка пакета движения
        pass
    
    async def broadcast_block_update(self, x: int, y: int, z: int, block_id: int, metadata: int):
        """Уведомление об обновлении блока"""
        try:
            # Создание пакета обновления блока
            packet_data = struct.pack('>i', x)
            packet_data += struct.pack('>B', y)
            packet_data += struct.pack('>i', z)
            packet_data += struct.pack('>B', block_id)
            packet_data += struct.pack('>B', metadata)
            
            packet = Packet(self.PACKET_UPDATE_BLOCK, packet_data)
            
            # Отправка всем клиентам
            for client in self.clients.values():
                await self.send_packet(client.addr, packet)
                
        except Exception as e:
            logger.error(f"Ошибка отправки обновления блока: {e}")
    
    async def send_packet(self, addr: Tuple[str, int], packet: Packet):
        """Отправка пакета клиенту"""
        try:
            data = packet.encode()
            self.socket.sendto(data, addr)
            
        except Exception as e:
            logger.error(f"Ошибка отправки пакета: {e}")
    
    def find_client_by_addr(self, addr: Tuple[str, int]) -> Optional['MinecraftPEClient']:
        """Поиск клиента по адресу"""
        for client in self.clients.values():
            if client.addr == addr:
                return client
        return None
    
    async def disconnect_client(self, client: 'MinecraftPEClient'):
        """Отключение клиента"""
        try:
            # Отправка пакета отключения
            await self.send_disconnect(client.addr, "Отключение от сервера")
            
            # Удаление из списка клиентов
            if client.username in self.clients:
                del self.clients[client.username]
            
            # Отключение игрока от сервера
            await self.server.player_leave(client.username)
            
            # Уведомление других игроков
            await self.broadcast_message(f"§e{client.username} покинул игру")
            
            logger.info(f"Клиент {client.username} отключен")
            
        except Exception as e:
            logger.error(f"Ошибка отключения клиента: {e}")

class MinecraftPEClient:
    """Клиент Minecraft PE"""
    
    def __init__(self, username: str, ip_address: str, addr: Tuple[str, int]):
        self.username = username
        self.ip_address = ip_address
        self.addr = addr
        self.connected_at = datetime.now()
        self.last_activity = datetime.now()
        self.ping = 0
        
    def update_activity(self):
        """Обновление времени последней активности"""
        self.last_activity = datetime.now()
    
    def is_active(self, timeout_seconds: int = 300) -> bool:
        """Проверка активности клиента"""
        return (datetime.now() - self.last_activity).total_seconds() < timeout_seconds