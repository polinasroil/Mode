#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Система чанков мира
Автор: Minecraft PE Server Team
Версия: 1.0.0
Основано на официальной спецификации чанков Minecraft Bedrock
"""

import asyncio
import logging
import struct
import time
import random
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Константы чанков
CHUNK_SIZE = 16  # 16x16 блоков
CHUNK_HEIGHT = 256  # Высота мира
SUBCHUNK_SIZE = 16  # Размер подчанка
MAX_SUBCHUNKS = CHUNK_HEIGHT // SUBCHUNK_SIZE

# Типы блоков (базовые) - ИСПРАВЛЕНО
BLOCK_AIR = 0
BLOCK_STONE = 1
BLOCK_GRASS = 2
BLOCK_DIRT = 3
BLOCK_COBBLESTONE = 4
BLOCK_PLANK = 5
BLOCK_SAPLING = 6
BLOCK_BEDROCK = 7
BLOCK_WATER = 8
BLOCK_WATER_STILL = 9
BLOCK_LAVA = 10
BLOCK_LAVA_STILL = 11
BLOCK_SAND = 12
BLOCK_GRAVEL = 13
BLOCK_GOLD_ORE = 14
BLOCK_IRON_ORE = 15
BLOCK_COAL_ORE = 16
BLOCK_LOG = 17
BLOCK_LEAVES = 18
BLOCK_SPONGE = 19
BLOCK_GLASS = 20
BLOCK_LAPIS_ORE = 21
BLOCK_LAPIS_BLOCK = 22
BLOCK_DISPENSER = 23
BLOCK_SANDSTONE = 24
BLOCK_NOTE_BLOCK = 25
BLOCK_BED = 26
BLOCK_POWERED_RAIL = 27
BLOCK_DETECTOR_RAIL = 28
BLOCK_STICKY_PISTON = 29
BLOCK_COBWEB = 30
BLOCK_TALL_GRASS = 31
BLOCK_DEAD_BUSH = 32
BLOCK_PISTON = 33
BLOCK_PISTON_HEAD = 34
BLOCK_WOOL = 35
BLOCK_DANDELION = 37
BLOCK_POPPY = 38
BLOCK_BROWN_MUSHROOM = 39
BLOCK_RED_MUSHROOM = 40
BLOCK_GOLD_BLOCK = 41
BLOCK_IRON_BLOCK = 42
BLOCK_DOUBLE_STONE_SLAB = 43
BLOCK_STONE_SLAB = 44
BLOCK_BRICK_BLOCK = 45
BLOCK_TNT = 46
BLOCK_BOOKSHELF = 47
BLOCK_MOSS_STONE = 48
BLOCK_OBSIDIAN = 49
BLOCK_TORCH = 50
BLOCK_FIRE = 51
BLOCK_MOB_SPAWNER = 52
BLOCK_OAK_STAIRS = 53
BLOCK_CHEST = 54
BLOCK_REDSTONE_WIRE = 55
BLOCK_DIAMOND_ORE = 56
BLOCK_DIAMOND_BLOCK = 57
BLOCK_CRAFTING_TABLE = 58
BLOCK_WHEAT = 59
BLOCK_FARMLAND = 60
BLOCK_FURNACE = 61
BLOCK_LIT_FURNACE = 62
BLOCK_STANDING_SIGN = 63
BLOCK_WOODEN_DOOR = 64
BLOCK_LADDER = 65
BLOCK_RAIL = 66
BLOCK_STONE_STAIRS = 67
BLOCK_WALL_SIGN = 68
BLOCK_LEVER = 69
BLOCK_STONE_PRESSURE_PLATE = 70
BLOCK_IRON_DOOR = 71
BLOCK_WOODEN_PRESSURE_PLATE = 72
BLOCK_REDSTONE_ORE = 73
BLOCK_LIT_REDSTONE_ORE = 74
BLOCK_UNLIT_REDSTONE_TORCH = 75
BLOCK_LIT_REDSTONE_TORCH = 76
BLOCK_STONE_BUTTON = 77
BLOCK_SNOW_LAYER = 78
BLOCK_ICE = 79
BLOCK_SNOW = 80
BLOCK_CACTUS = 81
BLOCK_CLAY = 82
BLOCK_REEDS = 83
BLOCK_JUKEBOX = 84
BLOCK_FENCE = 85
BLOCK_PUMPKIN = 86
BLOCK_NETHERRACK = 87
BLOCK_SOUL_SAND = 88
BLOCK_GLOWSTONE = 89
BLOCK_PORTAL = 90
BLOCK_LIT_PUMPKIN = 91
BLOCK_CAKE = 92
BLOCK_UNPOWERED_REPEATER = 93
BLOCK_POWERED_REPEATER = 94
BLOCK_INVISIBLE_BEDROCK = 95
BLOCK_TRAPDOOR = 96
BLOCK_MONSTER_EGG = 97
BLOCK_STONE_BRICK = 98
BLOCK_BROWN_MUSHROOM_BLOCK = 99
BLOCK_RED_MUSHROOM_BLOCK = 100
BLOCK_IRON_BARS = 101
BLOCK_GLASS_PANE = 102
BLOCK_MELON_BLOCK = 103
BLOCK_PUMPKIN_STEM = 104
BLOCK_MELON_STEM = 105
BLOCK_VINE = 106
BLOCK_FENCE_GATE = 107
BLOCK_BRICK_STAIRS = 108
BLOCK_STONE_BRICK_STAIRS = 109
BLOCK_MYCELIUM = 110
BLOCK_WATERLILY = 111
BLOCK_NETHER_BRICK = 112
BLOCK_NETHER_BRICK_FENCE = 113
BLOCK_NETHER_BRICK_STAIRS = 114
BLOCK_NETHER_WART = 115
BLOCK_ENCHANTING_TABLE = 116
BLOCK_BREWING_STAND = 117
BLOCK_CAULDRON = 118
BLOCK_END_PORTAL = 119
BLOCK_END_PORTAL_FRAME = 120
BLOCK_END_STONE = 121
BLOCK_DRAGON_EGG = 122  # ИСПРАВЛЕНО: было BLLOCK_DRAGON_EGG
BLOCK_REDSTONE_LAMP = 123
BLOCK_LIT_REDSTONE_LAMP = 124
BLOCK_DROPPER = 125
BLOCK_ACTIVATOR_RAIL = 126
BLOCK_COCOA = 127
BLOCK_SANDSTONE_STAIRS = 128
BLOCK_EMERALD_ORE = 129
BLOCK_ENDER_CHEST = 130
BLOCK_TRIPWIRE_HOOK = 131
BLOCK_TRIPWIRE = 132
BLOCK_EMERALD_BLOCK = 133
BLOCK_SPRUCE_STAIRS = 134
BLOCK_BIRCH_STAIRS = 135
BLOCK_JUNGLE_STAIRS = 136
BLOCK_COMMAND_BLOCK = 137
BLOCK_BEACON = 138
BLOCK_COBBLESTONE_WALL = 139
BLOCK_FLOWER_POT = 140
BLOCK_CARROTS = 141
BLOCK_POTATOES = 142
BLOCK_WOODEN_BUTTON = 143
BLOCK_SKULL = 144
BLOCK_ANVIL = 145
BLOCK_TRAPPED_CHEST = 146
BLOCK_LIGHT_WEIGHTED_PRESSURE_PLATE = 147
BLOCK_HEAVY_WEIGHTED_PRESSURE_PLATE = 148
BLOCK_UNPOWERED_COMPARATOR = 149
BLOCK_POWERED_COMPARATOR = 150
BLOCK_DAYLIGHT_DETECTOR = 151
BLOCK_REDSTONE_BLOCK = 152
BLOCK_QUARTZ_ORE = 153
BLOCK_HOPPER = 154
BLOCK_QUARTZ_BLOCK = 155
BLOCK_QUARTZ_STAIRS = 156
BLOCK_DOUBLE_WOODEN_SLAB = 157
BLOCK_WOODEN_SLAB = 158
BLOCK_STAINED_GLASS = 159
BLOCK_STAINED_GLASS_PANE = 160
BLOCK_LOG2 = 161
BLOCK_LEAVES2 = 162
BLOCK_ACACIA_STAIRS = 163
BLOCK_DARK_OAK_STAIRS = 164
BLOCK_SLIME = 165
BLOCK_BARRIER = 166
BLOCK_IRON_TRAPDOOR = 167
BLOCK_PRISMARINE = 168
BLOCK_SEA_LANTERN = 169
BLOCK_HAY_BLOCK = 170
BLOCK_CARPET = 171
BLOCK_HARDENED_CLAY = 172
BLOCK_COAL_BLOCK = 173
BLOCK_PACKED_ICE = 174
BLOCK_DOUBLE_PLANT = 175
BLOCK_STANDING_BANNER = 176
BLOCK_WALL_BANNER = 177
BLOCK_DAYLIGHT_DETECTOR_INVERTED = 178
BLOCK_RED_SANDSTONE = 179
BLOCK_RED_SANDSTONE_STAIRS = 180
BLOCK_DOUBLE_STONE_SLAB2 = 181
BLOCK_STONE_SLAB2 = 182
BLOCK_SPRUCE_FENCE_GATE = 183
BLOCK_BIRCH_FENCE_GATE = 184
BLOCK_JUNGLE_FENCE_GATE = 185
BLOCK_DARK_OAK_FENCE_GATE = 186
BLOCK_ACACIA_FENCE_GATE = 187
BLOCK_REPEATING_COMMAND_BLOCK = 188
BLOCK_CHAIN_COMMAND_BLOCK = 189
BLOCK_HARD_GLASS_PANE = 190
BLOCK_HARD_STAINED_GLASS_PANE = 191
BLOCK_CHEMICAL_HEAT = 192
BLOCK_SPRUCE_DOOR = 193
BLOCK_BIRCH_DOOR = 194
BLOCK_JUNGLE_DOOR = 195
BLOCK_ACACIA_DOOR = 196
BLOCK_DARK_OAK_DOOR = 197
BLOCK_GRASS_PATH = 198
BLOCK_FRAME = 199
BLOCK_CHORUS_FLOWER = 200
BLOCK_PURPUR_BLOCK = 201
BLOCK_COLORED_TORCH_RG = 202
BLOCK_PURPUR_STAIRS = 203
BLOCK_COLORED_TORCH_BP = 204
BLOCK_UNDYED_SHULKER_BOX = 205
BLOCK_END_ROD = 206
BLOCK_END_GATEWAY = 207
BLOCK_ALLOW = 208
BLOCK_DENY = 209
BLOCK_BORDER_BLOCK = 210
BLOCK_MAGMA = 211
BLOCK_NETHER_WART_BLOCK = 212
BLOCK_RED_NETHER_BRICK = 213
BLOCK_BONE_BLOCK = 214
BLOCK_STRUCTURE_VOID = 215
BLOCK_SHULKER_BOX = 216
BLOCK_GLAZE = 218
BLOCK_CONCRETE = 236
BLOCK_CONCRETE_POWDER = 237
BLOCK_CHEMISTRY_TABLE = 238
BLOCK_UNDERWATER_TORCH = 239
BLOCK_CHORUS_PLANT = 240
BLOCK_STAINED_GLASS2 = 241
BLOCK_PODZOL = 243
BLOCK_BEETROOT = 244
BLOCK_STONECUTTER = 245
BLOCK_GLOWING_OBSIDIAN = 246
BLOCK_NETHER_REACTOR = 247
BLOCK_INFO_UPDATE = 248
BLOCK_INFO_UPDATE2 = 249
BLOCK_PISTON_EXTENSION = 250
BLOCK_OBSERVER = 251
BLOCK_STRUCTURE_BLOCK = 252
BLOCK_HARD_STAINED_GLASS = 253
BLOCK_RESERVED6 = 255

@dataclass
class Block:
    """Блок в мире"""
    x: int
    y: int
    z: int
    block_id: int
    metadata: int = 0
    light_level: int = 15
    sky_light: int = 15
    
    def __post_init__(self):
        if self.light_level > 15:
            self.light_level = 15
        if self.sky_light > 15:
            self.sky_light = 15

@dataclass
class SubChunk:
    """Подчанк (16x16x16 блоков)"""
    x: int
    y: int
    z: int
    blocks: Dict[Tuple[int, int, int], Block] = None
    light_data: bytes = None
    sky_light_data: bytes = None
    
    def __post_init__(self):
        if self.blocks is None:
            self.blocks = {}
        if self.light_data is None:
            self.light_data = b'\x00' * (CHUNK_SIZE * CHUNK_SIZE * SUBCHUNK_SIZE // 2)
        if self.sky_light_data is None:
            self.sky_light_data = b'\xff' * (CHUNK_SIZE * CHUNK_SIZE * SUBCHUNK_SIZE // 2)
    
    def get_block(self, x: int, y: int, z: int) -> Optional[Block]:
        """Получение блока в подчанке"""
        return self.blocks.get((x, y, z))
    
    def set_block(self, x: int, y: int, z: int, block_id: int, metadata: int = 0):
        """Установка блока в подчанке"""
        if 0 <= x < CHUNK_SIZE and 0 <= y < SUBCHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            self.blocks[(x, y, z)] = Block(x, y, z, block_id, metadata)
    
    def remove_block(self, x: int, y: int, z: int):
        """Удаление блока из подчанка"""
        if (x, y, z) in self.blocks:
            del self.blocks[(x, y, z)]
    
    def get_light_level(self, x: int, y: int, z: int) -> int:
        """Получение уровня освещения"""
        if 0 <= x < CHUNK_SIZE and 0 <= y < SUBCHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            index = (y * CHUNK_SIZE * CHUNK_SIZE + z * CHUNK_SIZE + x) // 2
            byte = self.light_data[index]
            if x % 2 == 0:
                return byte & 0x0F
            else:
                return (byte >> 4) & 0x0F
        return 0
    
    def set_light_level(self, x: int, y: int, z: int, level: int):
        """Установка уровня освещения"""
        if 0 <= x < CHUNK_SIZE and 0 <= y < SUBCHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            if level > 15:
                level = 15
            elif level < 0:
                level = 0
            
            index = (y * CHUNK_SIZE * CHUNK_SIZE + z * CHUNK_SIZE + x) // 2
            byte = self.light_data[index]
            
            if x % 2 == 0:
                byte = (byte & 0xF0) | level
            else:
                byte = (byte & 0x0F) | (level << 4)
            
            # Обновление данных освещения
            light_data = bytearray(self.light_data)
            light_data[index] = byte
            self.light_data = bytes(light_data)
    
    def get_sky_light(self, x: int, y: int, z: int) -> int:
        """Получение небесного освещения"""
        if 0 <= x < CHUNK_SIZE and 0 <= y < SUBCHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            index = (y * CHUNK_SIZE * CHUNK_SIZE + z * CHUNK_SIZE + x) // 2
            byte = self.sky_light_data[index]
            if x % 2 == 0:
                return byte & 0x0F
            else:
                return (byte >> 4) & 0x0F
        return 15
    
    def set_sky_light(self, x: int, y: int, z: int, level: int):
        """Установка небесного освещения"""
        if 0 <= x < CHUNK_SIZE and 0 <= y < SUBCHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            if level > 15:
                level = 15
            elif level < 0:
                level = 0
            
            index = (y * CHUNK_SIZE * CHUNK_SIZE + z * CHUNK_SIZE + x) // 2
            byte = self.sky_light_data[index]
            
            if x % 2 == 0:
                byte = (byte & 0xF0) | level
            else:
                byte = (byte & 0x0F) | (level << 4)
            
            # Обновление данных небесного освещения
            sky_light_data = bytearray(self.sky_light_data)
            sky_light_data[index] = byte
            self.sky_light_data = bytes(sky_light_data)
    
    def serialize(self) -> bytes:
        """Сериализация подчанка для отправки клиенту"""
        try:
            data = b''
            
            # Версия подчанка
            data += struct.pack('>B', 1)  # Version
            
            # Количество слоев
            data += struct.pack('>B', 1)  # Layer count
            
            # Данные слоя
            layer_data = b''
            
            # Блоки
            for y in range(SUBCHUNK_SIZE):
                for z in range(CHUNK_SIZE):
                    for x in range(CHUNK_SIZE):
                        block = self.get_block(x, y, z)
                        if block:
                            layer_data += struct.pack('>H', block.block_id)
                        else:
                            layer_data += struct.pack('>H', BLOCK_AIR)
            
            # Размер данных слоя
            data += struct.pack('>I', len(layer_data))
            data += layer_data
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка сериализации подчанка: {e}")
            return b''

@dataclass
class Chunk:
    """Чанк мира (16x16 блоков)"""
    x: int
    z: int
    subchunks: Dict[int, SubChunk] = None
    biomes: bytes = None
    height_map: bytes = None
    last_updated: float = 0
    
    def __post_init__(self):
        if self.subchunks is None:
            self.subchunks = {}
        if self.biomes is None:
            self.biomes = b'\x00' * (CHUNK_SIZE * CHUNK_SIZE)
        if self.height_map is None:
            self.height_map = b'\x00' * (CHUNK_SIZE * CHUNK_SIZE)
        self.last_updated = time.time()
    
    def get_subchunk(self, y: int) -> SubChunk:
        """Получение подчанка по Y координате"""
        if y not in self.subchunks:
            self.subchunks[y] = SubChunk(self.x, y, self.z)
        return self.subchunks[y]
    
    def get_block(self, x: int, y: int, z: int) -> Optional[Block]:
        """Получение блока в чанке"""
        if 0 <= x < CHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            subchunk_y = y // SUBCHUNK_SIZE
            subchunk = self.get_subchunk(subchunk_y)
            local_y = y % SUBCHUNK_SIZE
            return subchunk.get_block(x, local_y, z)
        return None
    
    def set_block(self, x: int, y: int, z: int, block_id: int, metadata: int = 0):
        """Установка блока в чанке"""
        if 0 <= x < CHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            subchunk_y = y // SUBCHUNK_SIZE
            subchunk = self.get_subchunk(subchunk_y)
            local_y = y % SUBCHUNK_SIZE
            subchunk.set_block(x, local_y, z, block_id, metadata)
            self.last_updated = time.time()
    
    def remove_block(self, x: int, y: int, z: int):
        """Удаление блока из чанка"""
        if 0 <= x < CHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            subchunk_y = y // SUBCHUNK_SIZE
            subchunk = self.get_subchunk(subchunk_y)
            local_y = y % SUBCHUNK_SIZE
            subchunk.remove_block(x, local_y, z)
            self.last_updated = time.time()
    
    def get_height(self, x: int, z: int) -> int:
        """Получение высоты в точке"""
        if 0 <= x < CHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            index = z * CHUNK_SIZE + x
            return self.height_map[index]
        return 0
    
    def set_height(self, x: int, z: int, height: int):
        """Установка высоты в точке"""
        if 0 <= x < CHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            if height > 255:
                height = 255
            elif height < 0:
                height = 0
            
            index = z * CHUNK_SIZE + x
            height_map = bytearray(self.height_map)
            height_map[index] = height
            self.height_map = bytes(height_map)
    
    def get_biome(self, x: int, z: int) -> int:
        """Получение биома в точке"""
        if 0 <= x < CHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            index = z * CHUNK_SIZE + x
            return self.biomes[index]
        return 0
    
    def set_biome(self, x: int, z: int, biome: int):
        """Установка биома в точке"""
        if 0 <= x < CHUNK_SIZE and 0 <= z < CHUNK_SIZE:
            if biome > 255:
                biome = 255
            elif biome < 0:
                biome = 0
            
            index = z * CHUNK_SIZE + x
            biomes = bytearray(self.biomes)
            biomes[index] = biome
            self.biomes = bytes(biomes)
    
    def serialize(self) -> bytes:
        """Сериализация чанка для отправки клиенту"""
        try:
            data = b''
            
            # Координаты чанка
            data += struct.pack('>I', self.x)
            data += struct.pack('>I', self.z)
            
            # Количество подчанков
            subchunk_count = len(self.subchunks)
            data += struct.pack('>I', subchunk_count)
            
            # Данные подчанков
            for y in sorted(self.subchunks.keys()):
                subchunk_data = self.subchunks[y].serialize()
                data += subchunk_data
            
            # Карта высот
            data += self.height_map
            
            # Биомы
            data += self.biomes
            
            return data
            
        except Exception as e:
            logger.error(f"Ошибка сериализации чанка: {e}")
            return b''

class ChunkManager:
    """Менеджер чанков мира"""
    
    def __init__(self, world_seed: int = 0):
        self.world_seed = world_seed
        self.chunks: Dict[Tuple[int, int], Chunk] = {}
        self.loaded_chunks: Set[Tuple[int, int]] = set()
        self.chunk_generators = {}
        
        logger.info(f"Менеджер чанков инициализирован (seed: {world_seed})")
    
    def get_chunk(self, x: int, z: int) -> Chunk:
        """Получение чанка (создание если не существует)"""
        chunk_key = (x, z)
        
        if chunk_key not in self.chunks:
            # Создание нового чанка
            chunk = Chunk(x, z)
            self.chunks[chunk_key] = chunk
            
            # Генерация чанка
            self._generate_chunk(chunk)
            
            logger.debug(f"Создан чанк ({x}, {z})")
        
        return self.chunks[chunk_key]
    
    def _generate_chunk(self, chunk: Chunk):
        """Генерация содержимого чанка"""
        try:
            # Простая генерация ландшафта
            for x in range(CHUNK_SIZE):
                for z in range(CHUNK_SIZE):
                    # Высота на основе шума
                    height = self._get_height_at(x + chunk.x * CHUNK_SIZE, z + chunk.z * CHUNK_SIZE)
                    chunk.set_height(x, z, height)
                    
                    # Генерация блоков
                    for y in range(height + 1):
                        if y == 0:
                            # Бедрок внизу
                            chunk.set_block(x, y, z, BLOCK_BEDROCK)
                        elif y == height:
                            # Поверхность
                            if height > 62:
                                chunk.set_block(x, y, z, BLOCK_GRASS)
                            else:
                                chunk.set_block(x, y, z, BLOCK_SAND)
                        elif y > height - 4:
                            # Подповерхностные слои
                            chunk.set_block(x, y, z, BLOCK_DIRT)
                        else:
                            # Камень
                            chunk.set_block(x, y, z, BLOCK_STONE)
                    
                    # Установка биома
                    biome = self._get_biome_at(x + chunk.x * CHUNK_SIZE, z + chunk.z * CHUNK_SIZE)
                    chunk.set_biome(x, z, biome)
            
            logger.debug(f"Чанк ({chunk.x}, {chunk.z}) сгенерирован")
            
        except Exception as e:
            logger.error(f"Ошибка генерации чанка ({chunk.x}, {chunk.z}): {e}")
    
    def _get_height_at(self, x: int, z: int) -> int:
        """Получение высоты в точке (простой шум)"""
        # Простая реализация шума для демонстрации
        noise = (x * 0.1 + z * 0.1) % 1.0
        height = int(64 + noise * 32)
        return max(1, min(255, height))
    
    def _get_biome_at(self, x: int, z: int) -> int:
        """Получение биома в точке"""
        # Простая реализация биомов для демонстрации
        if x % 100 < 50 and z % 100 < 50:
            return 1  # Plains
        elif x % 100 < 75 and z % 100 < 75:
            return 2  # Desert
        else:
            return 0  # Ocean
    
    def load_chunk(self, x: int, z: int):
        """Загрузка чанка в память"""
        chunk_key = (x, z)
        if chunk_key not in self.loaded_chunks:
            self.get_chunk(x, z)  # Создание/загрузка чанка
            self.loaded_chunks.add(chunk_key)
            logger.debug(f"Чанк ({x}, {z}) загружен")
    
    def unload_chunk(self, x: int, z: int):
        """Выгрузка чанка из памяти"""
        chunk_key = (x, z)
        if chunk_key in self.loaded_chunks:
            self.loaded_chunks.remove(chunk_key)
            logger.debug(f"Чанк ({x}, {z}) выгружен")
    
    def get_chunks_in_radius(self, center_x: int, center_z: int, radius: int) -> List[Chunk]:
        """Получение чанков в радиусе от центра"""
        chunks = []
        for x in range(center_x - radius, center_x + radius + 1):
            for z in range(center_z - radius, center_z + radius + 1):
                if (x - center_x) ** 2 + (z - center_z) ** 2 <= radius ** 2:
                    chunk = self.get_chunk(x, z)
                    chunks.append(chunk)
        return chunks
    
    def save_chunk(self, x: int, z: int):
        """Сохранение чанка на диск"""
        try:
            chunk = self.chunks.get((x, z))
            if chunk:
                # Здесь можно добавить логику сохранения в файл
                logger.debug(f"Чанк ({x}, {z}) сохранен")
        except Exception as e:
            logger.error(f"Ошибка сохранения чанка ({x}, {z}): {e}")
    
    def get_chunk_info(self) -> dict:
        """Получение информации о чанках"""
        return {
            'total_chunks': len(self.chunks),
            'loaded_chunks': len(self.loaded_chunks),
            'world_seed': self.world_seed
        }