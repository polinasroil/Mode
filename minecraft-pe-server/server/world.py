#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Система миров
Автор: Minecraft PE Server Team
Версия: 1.0.0
"""

import json
import logging
import math
import random
import struct
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class Block:
    """Блок в мире"""
    x: int
    y: int
    z: int
    block_id: int
    metadata: int = 0
    light_level: int = 15
    
    def __post_init__(self):
        self.coordinates = (self.x, self.y, self.z)
    
    def distance_to(self, other: 'Block') -> float:
        """Расстояние до другого блока"""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return math.sqrt(dx*dx + dy*dy + dz*dz)

@dataclass
class Chunk:
    """Чанк мира"""
    x: int
    z: int
    blocks: Dict[Tuple[int, int, int], Block] = None
    entities: List[Dict] = None
    tile_entities: List[Dict] = None
    last_modified: datetime = None
    
    def __post_init__(self):
        if self.blocks is None:
            self.blocks = {}
        if self.entities is None:
            self.entities = []
        if self.tile_entities is None:
            self.tile_entities = []
        if self.last_modified is None:
            self.last_modified = datetime.now()
    
    def get_block(self, x: int, y: int, z: int) -> Optional[Block]:
        """Получение блока по координатам"""
        return self.blocks.get((x, y, z))
    
    def set_block(self, x: int, y: int, z: int, block_id: int, metadata: int = 0):
        """Установка блока"""
        block = Block(x, y, z, block_id, metadata)
        self.blocks[(x, y, z)] = block
        self.last_modified = datetime.now()
    
    def remove_block(self, x: int, y: int, z: int):
        """Удаление блока"""
        if (x, y, z) in self.blocks:
            del self.blocks[(x, y, z)]
            self.last_modified = datetime.now()
    
    def get_chunk_data(self) -> bytes:
        """Получение данных чанка для отправки клиенту"""
        try:
            # Создание заголовка чанка
            header = struct.pack('>ii', self.x, self.z)
            
            # Данные блоков
            blocks_data = b''
            for (x, y, z), block in self.blocks.items():
                block_data = struct.pack('>BBBB', x, y, z, block.block_id)
                blocks_data += block_data
            
            # Данные сущностей
            entities_data = json.dumps(self.entities).encode('utf-8')
            
            # Объединение всех данных
            chunk_data = header + struct.pack('>I', len(blocks_data)) + blocks_data + \
                        struct.pack('>I', len(entities_data)) + entities_data
            
            return chunk_data
            
        except Exception as e:
            logger.error(f"Ошибка создания данных чанка: {e}")
            return b''

class WorldGenerator:
    """Генератор миров Minecraft PE"""
    
    # Блоки Minecraft PE
    BLOCKS = {
        'air': 0,
        'stone': 1,
        'grass': 2,
        'dirt': 3,
        'cobblestone': 4,
        'planks': 5,
        'sapling': 6,
        'bedrock': 7,
        'water': 9,
        'lava': 11,
        'sand': 12,
        'gravel': 13,
        'gold_ore': 14,
        'iron_ore': 15,
        'coal_ore': 16,
        'log': 17,
        'leaves': 18,
        'sponge': 19,
        'glass': 20,
        'red_wool': 35,
        'orange_wool': 35,
        'yellow_wool': 35,
        'lime_wool': 35,
        'light_blue_wool': 35,
        'cyan_wool': 35,
        'blue_wool': 35,
        'purple_wool': 35,
        'magenta_wool': 35,
        'pink_wool': 35,
        'white_wool': 35,
        'light_gray_wool': 35,
        'gray_wool': 35,
        'black_wool': 35,
        'brown_wool': 35,
        'green_wool': 35,
        'red_wool': 35
    }
    
    def __init__(self, seed: int = 0):
        self.seed = seed
        self.random = random.Random(seed)
        
    def generate_world(self, world_name: str, world_type: str = "default") -> Dict[str, Chunk]:
        """Генерация мира"""
        logger.info(f"Генерация мира '{world_name}' типа '{world_type}' с сидом {self.seed}")
        
        chunks = {}
        
        # Генерация базовых чанков (16x16 чанков)
        for chunk_x in range(-8, 8):
            for chunk_z in range(-8, 8):
                chunk = self.generate_chunk(chunk_x, chunk_z, world_type)
                chunks[(chunk_x, chunk_z)] = chunk
        
        logger.info(f"Сгенерировано {len(chunks)} чанков")
        return chunks
    
    def generate_chunk(self, chunk_x: int, chunk_z: int, world_type: str) -> Chunk:
        """Генерация отдельного чанка"""
        chunk = Chunk(chunk_x, chunk_z)
        
        if world_type == "default":
            self.generate_default_chunk(chunk)
        elif world_type == "flat":
            self.generate_flat_chunk(chunk)
        elif world_type == "desert":
            self.generate_desert_chunk(chunk)
        elif world_type == "forest":
            self.generate_forest_chunk(chunk)
        elif world_type == "mountain":
            self.generate_mountain_chunk(chunk)
        else:
            self.generate_default_chunk(chunk)
        
        return chunk
    
    def generate_default_chunk(self, chunk: Chunk):
        """Генерация стандартного чанка"""
        # Базовый ландшафт
        for x in range(16):
            for z in range(16):
                # Координаты в мире
                world_x = chunk.x * 16 + x
                world_z = chunk.z * 16 + z
                
                # Генерация высоты
                height = self.generate_height(world_x, world_z)
                
                # Установка блоков
                for y in range(height + 1):
                    if y == 0:
                        # Бедрок
                        chunk.set_block(x, y, z, self.BLOCKS['bedrock'])
                    elif y == height:
                        # Поверхность
                        if height > 62:  # Выше уровня моря
                            chunk.set_block(x, y, z, self.BLOCKS['grass'])
                        else:
                            chunk.set_block(x, y, z, self.BLOCKS['sand'])
                    elif y > height - 4:
                        # Верхние слои
                        chunk.set_block(x, y, z, self.BLOCKS['dirt'])
                    else:
                        # Камень
                        chunk.set_block(x, y, z, self.BLOCKS['stone'])
                
                # Генерация руд
                self.generate_ores(chunk, x, height, z)
                
                # Генерация деревьев
                if self.random.random() < 0.02:  # 2% шанс дерева
                    self.generate_tree(chunk, x, height + 1, z)
    
    def generate_flat_chunk(self, chunk: Chunk):
        """Генерация плоского чанка"""
        for x in range(16):
            for z in range(16):
                # Бедрок
                chunk.set_block(x, 0, z, self.BLOCKS['bedrock'])
                
                # Слои
                chunk.set_block(x, 1, z, self.BLOCKS['stone'])
                chunk.set_block(x, 2, z, self.BLOCKS['stone'])
                chunk.set_block(x, 3, z, self.BLOCKS['dirt'])
                chunk.set_block(x, 4, z, self.BLOCKS['grass'])
    
    def generate_desert_chunk(self, chunk: Chunk):
        """Генерация пустынного чанка"""
        for x in range(16):
            for z in range(16):
                world_x = chunk.x * 16 + x
                world_z = chunk.z * 16 + z
                
                height = self.generate_height(world_x, world_z, biome="desert")
                
                for y in range(height + 1):
                    if y == 0:
                        chunk.set_block(x, y, z, self.BLOCKS['bedrock'])
                    elif y == height:
                        chunk.set_block(x, y, z, self.BLOCKS['sand'])
                    else:
                        chunk.set_block(x, y, z, self.BLOCKS['sand'])
                
                # Кактусы
                if self.random.random() < 0.01:
                    self.generate_cactus(chunk, x, height + 1, z)
    
    def generate_forest_chunk(self, chunk: Chunk):
        """Генерация лесного чанка"""
        for x in range(16):
            for z in range(16):
                world_x = chunk.x * 16 + x
                world_z = chunk.z * 16 + z
                
                height = self.generate_height(world_x, world_z, biome="forest")
                
                for y in range(height + 1):
                    if y == 0:
                        chunk.set_block(x, y, z, self.BLOCKS['bedrock'])
                    elif y == height:
                        chunk.set_block(x, y, z, self.BLOCKS['grass'])
                    elif y > height - 4:
                        chunk.set_block(x, y, z, self.BLOCKS['dirt'])
                    else:
                        chunk.set_block(x, y, z, self.BLOCKS['stone'])
                
                # Больше деревьев в лесу
                if self.random.random() < 0.08:
                    self.generate_tree(chunk, x, height + 1, z)
    
    def generate_mountain_chunk(self, chunk: Chunk):
        """Генерация горного чанка"""
        for x in range(16):
            for z in range(16):
                world_x = chunk.x * 16 + x
                world_z = chunk.z * 16 + z
                
                height = self.generate_height(world_x, world_z, biome="mountain")
                
                for y in range(height + 1):
                    if y == 0:
                        chunk.set_block(x, y, z, self.BLOCKS['bedrock'])
                    elif y == height:
                        chunk.set_block(x, y, z, self.BLOCKS['stone'])
                    else:
                        chunk.set_block(x, y, z, self.BLOCKS['stone'])
                
                # Снег на вершинах
                if height > 80:
                    chunk.set_block(x, height + 1, z, self.BLOCKS['white_wool'])
    
    def generate_height(self, x: int, z: int, biome: str = "default") -> int:
        """Генерация высоты ландшафта"""
        # Базовый шум
        noise = self.simplex_noise(x * 0.01, z * 0.01)
        
        # Модификация для разных биомов
        if biome == "desert":
            height = int(noise * 20 + 60)  # Плоская пустыня
        elif biome == "forest":
            height = int(noise * 30 + 65)  # Лесистые холмы
        elif biome == "mountain":
            height = int(noise * 50 + 80)  # Высокие горы
        else:
            height = int(noise * 25 + 64)  # Стандартный ландшафт
        
        # Ограничение высоты
        return max(1, min(127, height))
    
    def simplex_noise(self, x: float, z: float) -> float:
        """Упрощенный шум для генерации ландшафта"""
        # Простая реализация шума
        return (math.sin(x * 2.5) * math.cos(z * 1.8) + 
                math.sin(x * 1.2) * math.cos(z * 2.3)) * 0.5
    
    def generate_ores(self, chunk: Chunk, x: int, height: int, z: int):
        """Генерация руд"""
        # Уголь (часто)
        if self.random.random() < 0.3:
            ore_y = self.random.randint(1, height - 1)
            chunk.set_block(x, ore_y, z, self.BLOCKS['coal_ore'])
        
        # Железо (средне)
        if self.random.random() < 0.1:
            ore_y = self.random.randint(1, height - 5)
            chunk.set_block(x, ore_y, z, self.BLOCKS['iron_ore'])
        
        # Золото (редко)
        if self.random.random() < 0.02:
            ore_y = self.random.randint(1, height - 10)
            chunk.set_block(x, ore_y, z, self.BLOCKS['gold_ore'])
    
    def generate_tree(self, chunk: Chunk, x: int, y: int, z: int):
        """Генерация дерева"""
        tree_height = self.random.randint(4, 7)
        
        # Ствол
        for tree_y in range(tree_height):
            if 0 <= y + tree_y < 128:
                chunk.set_block(x, y + tree_y, z, self.BLOCKS['log'])
        
        # Листва
        for leaf_y in range(tree_height - 2, tree_height + 1):
            for leaf_x in range(-2, 3):
                for leaf_z in range(-2, 3):
                    if (abs(leaf_x) + abs(leaf_z) <= 2 and 
                        0 <= x + leaf_x < 16 and 0 <= z + leaf_z < 16 and
                        0 <= y + leaf_y < 128):
                        chunk.set_block(x + leaf_x, y + leaf_y, z + leaf_z, self.BLOCKS['leaves'])
    
    def generate_cactus(self, chunk: Chunk, x: int, y: int, z: int):
        """Генерация кактуса"""
        cactus_height = self.random.randint(2, 4)
        
        for cactus_y in range(cactus_height):
            if 0 <= y + cactus_y < 128:
                chunk.set_block(x, y + cactus_y, z, self.BLOCKS['log'])

class World:
    """Класс мира Minecraft PE"""
    
    def __init__(self, name: str, seed: int, world_type: str = "default"):
        self.name = name
        self.seed = seed
        self.world_type = world_type
        self.spawn_x = 0
        self.spawn_y = 64
        self.spawn_z = 0
        self.time = 0
        self.weather = "clear"
        self.difficulty = "normal"
        self.gamemode = "survival"
        self.hardcore = False
        self.pvp = True
        
        # Система чанков
        self.chunks: Dict[Tuple[int, int], Chunk] = {}
        self.loaded_chunks: Set[Tuple[int, int]] = set()
        
        # Генератор мира
        self.generator = WorldGenerator(seed)
        
        # Файл мира
        self.world_file = Path(f"worlds/{name}/world.dat")
        self.chunks_dir = Path(f"worlds/{name}/chunks")
        
        # Создание директорий
        self.world_file.parent.mkdir(parents=True, exist_ok=True)
        self.chunks_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Мир '{name}' инициализирован")
    
    async def generate_world(self):
        """Генерация мира"""
        logger.info(f"Начинаю генерацию мира '{self.name}'...")
        
        try:
            # Генерация базовых чанков
            self.chunks = self.generator.generate_world(self.name, self.world_type)
            
            # Установка точки спавна
            self.set_spawn_point()
            
            # Сохранение мира
            await self.save_world()
            
            logger.info(f"Мир '{self.name}' успешно сгенерирован")
            
        except Exception as e:
            logger.error(f"Ошибка генерации мира: {e}")
            raise
    
    def set_spawn_point(self):
        """Установка точки спавна"""
        # Поиск подходящего места для спавна
        for chunk_x in range(-2, 3):
            for chunk_z in range(-2, 3):
                chunk = self.chunks.get((chunk_x, chunk_z))
                if chunk:
                    # Поиск блока травы
                    for x in range(16):
                        for z in range(16):
                            for y in range(60, 80):
                                block = chunk.get_block(x, y, z)
                                if block and block.block_id == self.generator.BLOCKS['grass']:
                                    # Найдена трава, устанавливаем спавн
                                    self.spawn_x = chunk_x * 16 + x
                                    self.spawn_y = y + 1
                                    self.spawn_z = chunk_z * 16 + z
                                    logger.info(f"Точка спавна установлена: {self.spawn_x}, {self.spawn_y}, {self.spawn_z}")
                                    return
        
        # Если не найдена трава, используем центр мира
        self.spawn_x = 0
        self.spawn_y = 64
        self.spawn_z = 0
        logger.info("Точка спавна установлена в центре мира")
    
    def get_chunk(self, chunk_x: int, chunk_z: int) -> Optional[Chunk]:
        """Получение чанка"""
        chunk_coords = (chunk_x, chunk_z)
        
        if chunk_coords in self.chunks:
            return self.chunks[chunk_coords]
        
        # Генерация нового чанка если не существует
        if chunk_coords not in self.loaded_chunks:
            chunk = self.generator.generate_chunk(chunk_x, chunk_z, self.world_type)
            self.chunks[chunk_coords] = chunk
            self.loaded_chunks.add(chunk_coords)
            logger.debug(f"Сгенерирован новый чанк: {chunk_x}, {chunk_z}")
        
        return self.chunks.get(chunk_coords)
    
    def get_block(self, x: int, y: int, z: int) -> Optional[Block]:
        """Получение блока по координатам мира"""
        chunk_x = x // 16
        chunk_z = z // 16
        local_x = x % 16
        local_z = z % 16
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk:
            return chunk.get_block(local_x, y, local_z)
        return None
    
    def set_block(self, x: int, y: int, z: int, block_id: int, metadata: int = 0):
        """Установка блока в мире"""
        chunk_x = x // 16
        chunk_z = z // 16
        local_x = x % 16
        local_z = z % 16
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk:
            chunk.set_block(local_x, y, local_z, block_id, metadata)
    
    def remove_block(self, x: int, y: int, z: int):
        """Удаление блока из мира"""
        chunk_x = x // 16
        chunk_z = z // 16
        local_x = x % 16
        local_z = z % 16
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        if chunk:
            chunk.remove_block(local_x, y, local_z)
    
    async def save_world(self):
        """Сохранение мира"""
        try:
            # Сохранение метаданных мира
            world_data = {
                'name': self.name,
                'seed': self.seed,
                'world_type': self.world_type,
                'spawn_x': self.spawn_x,
                'spawn_y': self.spawn_y,
                'spawn_z': self.spawn_z,
                'time': self.time,
                'weather': self.weather,
                'difficulty': self.difficulty,
                'gamemode': self.gamemode,
                'hardcore': self.hardcore,
                'pvp': self.pvp,
                'last_saved': datetime.now().isoformat()
            }
            
            with open(self.world_file, 'w', encoding='utf-8') as f:
                json.dump(world_data, f, indent=2, ensure_ascii=False)
            
            # Сохранение чанков
            for (chunk_x, chunk_z), chunk in self.chunks.items():
                await self.save_chunk(chunk_x, chunk_z, chunk)
            
            logger.info(f"Мир '{self.name}' сохранен")
            
        except Exception as e:
            logger.error(f"Ошибка сохранения мира: {e}")
            raise
    
    async def save_chunk(self, chunk_x: int, chunk_z: int, chunk: Chunk):
        """Сохранение чанка"""
        try:
            chunk_file = self.chunks_dir / f"chunk_{chunk_x}_{chunk_z}.dat"
            
            chunk_data = {
                'x': chunk_x,
                'z': chunk_z,
                'blocks': {},
                'entities': chunk.entities,
                'tile_entities': chunk.tile_entities,
                'last_modified': chunk.last_modified.isoformat()
            }
            
            # Сохранение блоков
            for (x, y, z), block in chunk.blocks.items():
                chunk_data['blocks'][f"{x}_{y}_{z}"] = {
                    'block_id': block.block_id,
                    'metadata': block.metadata,
                    'light_level': block.light_level
                }
            
            with open(chunk_file, 'w', encoding='utf-8') as f:
                json.dump(chunk_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Ошибка сохранения чанка {chunk_x}, {chunk_z}: {e}")
    
    async def load_world(self):
        """Загрузка мира"""
        try:
            if self.world_file.exists():
                with open(self.world_file, 'r', encoding='utf-8') as f:
                    world_data = json.load(f)
                
                # Загрузка метаданных
                self.spawn_x = world_data.get('spawn_x', 0)
                self.spawn_y = world_data.get('spawn_y', 64)
                self.spawn_z = world_data.get('spawn_z', 0)
                self.time = world_data.get('time', 0)
                self.weather = world_data.get('weather', 'clear')
                self.difficulty = world_data.get('difficulty', 'normal')
                self.gamemode = world_data.get('gamemode', 'survival')
                self.hardcore = world_data.get('hardcore', False)
                self.pvp = world_data.get('pvp', True)
                
                # Загрузка чанков
                await self.load_chunks()
                
                logger.info(f"Мир '{self.name}' загружен")
            else:
                # Создание нового мира
                await self.generate_world()
                
        except Exception as e:
            logger.error(f"Ошибка загрузки мира: {e}")
            # Создание нового мира при ошибке
            await self.generate_world()
    
    async def load_chunks(self):
        """Загрузка чанков"""
        try:
            for chunk_file in self.chunks_dir.glob("chunk_*.dat"):
                # Парсинг имени файла
                parts = chunk_file.stem.split('_')
                if len(parts) == 3:
                    chunk_x = int(parts[1])
                    chunk_z = int(parts[2])
                    
                    # Загрузка чанка
                    chunk = await self.load_chunk(chunk_x, chunk_z, chunk_file)
                    if chunk:
                        self.chunks[(chunk_x, chunk_z)] = chunk
                        self.loaded_chunks.add((chunk_x, chunk_z))
            
            logger.info(f"Загружено {len(self.loaded_chunks)} чанков")
            
        except Exception as e:
            logger.error(f"Ошибка загрузки чанков: {e}")
    
    async def load_chunk(self, chunk_x: int, chunk_z: int, chunk_file: Path) -> Optional[Chunk]:
        """Загрузка отдельного чанка"""
        try:
            with open(chunk_file, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
            
            chunk = Chunk(chunk_x, chunk_z)
            chunk.entities = chunk_data.get('entities', [])
            chunk.tile_entities = chunk_data.get('tile_entities', [])
            
            # Загрузка блоков
            for block_key, block_data in chunk_data.get('blocks', {}).items():
                x, y, z = map(int, block_key.split('_'))
                block = Block(
                    x, y, z,
                    block_data['block_id'],
                    block_data.get('metadata', 0),
                    block_data.get('light_level', 15)
                )
                chunk.blocks[(x, y, z)] = block
            
            return chunk
            
        except Exception as e:
            logger.error(f"Ошибка загрузки чанка {chunk_x}, {chunk_z}: {e}")
            return None
    
    def update_time(self):
        """Обновление времени в мире"""
        self.time = (self.time + 1) % 24000
    
    def get_time_string(self) -> str:
        """Получение времени в читаемом виде"""
        hours = (self.time // 1000) % 24
        minutes = (self.time % 1000) * 60 // 1000
        
        if hours < 6:
            time_of_day = "Ночь"
        elif hours < 12:
            time_of_day = "Утро"
        elif hours < 18:
            time_of_day = "День"
        else:
            time_of_day = "Вечер"
        
        return f"{time_of_day} ({hours:02d}:{minutes:02d})"
    
    def get_weather_string(self) -> str:
        """Получение погоды в читаемом виде"""
        weather_names = {
            "clear": "Ясно",
            "rain": "Дождь",
            "thunder": "Гроза"
        }
        return weather_names.get(self.weather, self.weather)
    
    def get_world_info(self) -> Dict:
        """Получение информации о мире"""
        return {
            'name': self.name,
            'seed': self.seed,
            'world_type': self.world_type,
            'spawn': {
                'x': self.spawn_x,
                'y': self.spawn_y,
                'z': self.spawn_z
            },
            'time': self.time,
            'time_string': self.get_time_string(),
            'weather': self.weather,
            'weather_string': self.get_weather_string(),
            'difficulty': self.difficulty,
            'gamemode': self.gamemode,
            'hardcore': self.hardcore,
            'pvp': self.pvp,
            'chunks_loaded': len(self.loaded_chunks),
            'total_chunks': len(self.chunks)
        }