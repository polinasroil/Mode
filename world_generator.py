"""
Advanced world generator for Minecraft Bedrock Server
Supports multiple biomes, structures, and terrain generation
"""

import random
import math
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class Biome:
    """Biome definitions"""
    OCEAN = 0
    PLAINS = 1
    DESERT = 2
    MOUNTAINS = 3
    FOREST = 4
    TAIGA = 5
    SWAMP = 6
    RIVER = 7
    NETHER = 8
    THE_END = 9
    FROZEN_OCEAN = 10
    FROZEN_RIVER = 11
    SNOWY_TUNDRA = 12
    SNOWY_TAIGA = 13
    MUSHROOM_FIELDS = 14
    MUSHROOM_FIELD_SHORE = 15
    BEACH = 16
    DESERT_HILLS = 17
    WOODED_HILLS = 18
    TAIGA_HILLS = 19
    MOUNTAIN_EDGE = 20
    JUNGLE = 21
    JUNGLE_HILLS = 22
    JUNGLE_EDGE = 23
    DEEP_OCEAN = 24
    STONE_SHORE = 25
    SNOWY_BEACH = 26
    BIRCH_FOREST = 27
    BIRCH_FOREST_HILLS = 28
    DARK_FOREST = 29
    SNOWY_TAIGA_HILLS = 30
    GIANT_TREE_TAIGA = 31
    GIANT_TREE_TAIGA_HILLS = 32
    WOODED_MOUNTAINS = 33
    SAVANNA = 34
    SAVANNA_PLATEAU = 35
    BADLANDS = 36
    WOODED_BADLANDS_PLATEAU = 37
    BADLANDS_PLATEAU = 38
    SMALL_END_ISLANDS = 39
    END_MIDLANDS = 40
    END_HIGHLANDS = 41
    END_BARRENS = 42
    WARM_OCEAN = 43
    LUKEWARM_OCEAN = 44
    COLD_OCEAN = 45
    DEEP_WARM_OCEAN = 46
    DEEP_LUKEWARM_OCEAN = 47
    DEEP_COLD_OCEAN = 48
    DEEP_FROZEN_OCEAN = 49
    THE_VOID = 50
    SUNFLOWER_PLAINS = 51
    DESERT_LAKES = 52
    GRAVELLY_MOUNTAINS = 53
    FLOWER_FOREST = 54
    TAIGA_MOUNTAINS = 55
    SWAMP_HILLS = 56
    ICE_SPIKES = 57
    MODIFIED_JUNGLE = 58
    MODIFIED_JUNGLE_EDGE = 59
    TALL_BIRCH_FOREST = 60
    TALL_BIRCH_HILLS = 61
    DARK_FOREST_HILLS = 62
    SNOWY_TAIGA_MOUNTAINS = 63
    GIANT_SPRUCE_TAIGA = 64
    GIANT_SPRUCE_TAIGA_HILLS = 65
    MODIFIED_GRAVELLY_MOUNTAINS = 66
    SHATTERED_SAVANNA = 67
    SHATTERED_SAVANNA_PLATEAU = 68
    ERODED_BADLANDS = 69
    MODIFIED_WOODED_BADLANDS_PLATEAU = 70
    MODIFIED_BADLANDS_PLATEAU = 71
    BAMBOO_JUNGLE = 72
    BAMBOO_JUNGLE_HILLS = 73
    SOUL_SAND_VALLEY = 74
    CRIMSON_FOREST = 75
    WARPED_FOREST = 76
    BASALT_DELTAS = 77
    DRIPSTONE_CAVES = 78
    LUSH_CAVES = 79
    DEEP_DARK = 80
    NETHER_WASTES = 81
    WARPED_FOREST = 82
    CRIMSON_FOREST = 83
    SOUL_SAND_VALLEY = 84
    BASALT_DELTAS = 85

class BlockType:
    """Block type definitions"""
    AIR = 0
    STONE = 1
    GRASS = 2
    DIRT = 3
    COBBLESTONE = 4
    PLANKS = 5
    SAPLING = 6
    BEDROCK = 7
    WATER = 9
    LAVA = 11
    SAND = 12
    GRAVEL = 13
    GOLD_ORE = 14
    IRON_ORE = 15
    COAL_ORE = 16
    LOG = 17
    LEAVES = 18
    SPONGE = 19
    GLASS = 20
    LAPIS_ORE = 21
    LAPIS_BLOCK = 22
    DISPENSER = 23
    SANDSTONE = 24
    NOTEBLOCK = 25
    BED = 26
    GOLDEN_RAIL = 27
    DETECTOR_RAIL = 28
    STICKY_PISTON = 29
    WEB = 30
    TALLGRASS = 31
    DEADBUSH = 32
    PISTON = 33
    PISTONARMCOLLISION = 34
    WOOL = 35
    YELLOW_FLOWER = 37
    RED_FLOWER = 38
    BROWN_MUSHROOM = 39
    RED_MUSHROOM = 40
    GOLD_BLOCK = 41
    IRON_BLOCK = 42
    DOUBLE_STONE_SLAB = 43
    STONE_SLAB = 44
    BRICK_BLOCK = 45
    TNT = 46
    BOOKSHELF = 47
    MOSSY_COBBLESTONE = 48
    OBSIDIAN = 49
    TORCH = 50
    FIRE = 51
    MOB_SPAWNER = 52
    OAK_STAIRS = 53
    CHEST = 54
    REDSTONE_WIRE = 55
    DIAMOND_ORE = 56
    DIAMOND_BLOCK = 57
    CRAFTING_TABLE = 58
    WHEAT = 59
    FARMLAND = 60
    FURNACE = 61
    LIT_FURNACE = 62
    STANDING_SIGN = 63
    WOODEN_DOOR = 64
    LADDER = 65
    RAIL = 66
    STONE_STAIRS = 67
    WALL_SIGN = 68
    LEVER = 69
    STONE_PRESSURE_PLATE = 70
    IRON_DOOR = 71
    WOODEN_PRESSURE_PLATE = 72
    REDSTONE_ORE = 73
    LIT_REDSTONE_ORE = 74
    UNLIT_REDSTONE_TORCH = 75
    LIT_REDSTONE_TORCH = 76
    STONE_BUTTON = 77
    SNOW_LAYER = 78
    ICE = 79
    SNOW = 80
    CACTUS = 81
    CLAY = 82
    REEDS = 83
    JUKEBOX = 84
    FENCE = 85
    PUMPKIN = 86
    NETHERRACK = 87
    SOUL_SAND = 88
    GLOWSTONE = 89
    PORTAL = 90
    LIT_PUMPKIN = 91
    CAKE = 92
    UNPOWERED_REPEATER = 93
    POWERED_REPEATER = 94
    INVISIBLEBEDROCK = 95
    TRAPDOOR = 96
    MONSTER_EGG = 97
    STONEBRICK = 98
    BROWN_MUSHROOM_BLOCK = 99
    RED_MUSHROOM_BLOCK = 100
    IRON_BARS = 101
    GLASS_PANE = 102
    MELON_BLOCK = 103
    PUMPKIN_STEM = 104
    MELON_STEM = 105
    VINE = 106
    FENCE_GATE = 107
    BRICK_STAIRS = 108
    STONE_BRICK_STAIRS = 109
    MYCELIUM = 110
    WATERLILY = 111
    NETHER_BRICK = 112
    NETHER_BRICK_FENCE = 113
    NETHER_BRICK_STAIRS = 114
    NETHER_WART = 115
    ENCHANTING_TABLE = 116
    BREWING_STAND = 117
    CAULDRON = 118
    END_PORTAL = 119
    END_PORTAL_FRAME = 120
    END_STONE = 121
    DRAGON_EGG = 122
    REDSTONE_LAMP = 123
    LIT_REDSTONE_LAMP = 124
    DROPPER = 125
    ACTIVATOR_RAIL = 126
    COCOA = 127
    SANDSTONE_STAIRS = 128
    EMERALD_ORE = 129
    ENDER_CHEST = 130
    TRIPWIRE_HOOK = 131
    TRIPWIRE = 132
    EMERALD_BLOCK = 133
    SPRUCE_STAIRS = 134
    BIRCH_STAIRS = 135
    JUNGLE_STAIRS = 136
    COMMAND_BLOCK = 137
    BEACON = 138
    COBBLESTONE_WALL = 139
    FLOWER_POT = 140
    CARROTS = 141
    POTATOES = 142
    WOODEN_BUTTON = 143
    SKULL = 144
    ANVIL = 145
    TRAPPED_CHEST = 146
    LIGHT_WEIGHTED_PRESSURE_PLATE = 147
    HEAVY_WEIGHTED_PRESSURE_PLATE = 148
    UNPOWERED_COMPARATOR = 149
    POWERED_COMPARATOR = 150
    DAYLIGHT_DETECTOR = 151
    REDSTONE_BLOCK = 152
    QUARTZ_ORE = 153
    HOPPER = 154
    QUARTZ_BLOCK = 155
    QUARTZ_STAIRS = 156
    DOUBLE_WOODEN_SLAB = 157
    WOODEN_SLAB = 158
    STAINED_HARDENED_CLAY = 159
    STAINED_GLASS_PANE = 160
    LEAVES2 = 161
    LOG2 = 162
    ACACIA_STAIRS = 163
    DARK_OAK_STAIRS = 164
    SLIME = 165
    BARRIER = 166
    IRON_TRAPDOOR = 167
    PRISMARINE = 168
    SEA_LANTERN = 169
    HAY_BLOCK = 170
    CARPET = 171
    HARDENED_CLAY = 172
    COAL_BLOCK = 173
    PACKED_ICE = 174
    DOUBLE_PLANT = 175
    STANDING_BANNER = 176
    WALL_BANNER = 177
    DAYLIGHT_DETECTOR_INVERTED = 178
    RED_SANDSTONE = 179
    RED_SANDSTONE_STAIRS = 180
    DOUBLE_STONE_SLAB2 = 181
    STONE_SLAB2 = 182
    SPRUCE_FENCE_GATE = 183
    BIRCH_FENCE_GATE = 184
    JUNGLE_FENCE_GATE = 185
    DARK_OAK_FENCE_GATE = 186
    ACACIA_FENCE_GATE = 187
    REPEATING_COMMAND_BLOCK = 188
    CHAIN_COMMAND_BLOCK = 189
    HARD_GLASS_PANE = 190
    HARD_STAINED_GLASS_PANE = 191
    CHEMICAL_HEAT = 192
    SPRUCE_DOOR = 193
    BIRCH_DOOR = 194
    JUNGLE_DOOR = 195
    ACACIA_DOOR = 196
    DARK_OAK_DOOR = 197
    GRASS_PATH = 198
    FRAME = 199
    CHORUS_FLOWER = 200
    PURPUR_BLOCK = 201
    COLORED_TORCH_RG = 202
    PURPUR_STAIRS = 203
    COLORED_TORCH_BP = 204
    UNDYED_SHULKER_BOX = 205
    END_BRICKS = 206
    FROSTED_ICE = 207
    END_ROD = 208
    END_GATEWAY = 209
    ALLOW = 210
    DENY = 211
    BORDER_BLOCK = 212
    MAGMA = 213
    NETHER_WART_BLOCK = 214
    RED_NETHER_BRICK = 215
    BONE_BLOCK = 216
    STRUCTURE_VOID = 217
    SHULKER_BOX = 218
    PURPLE_GLAZED_TERRACOTTA = 219
    WHITE_GLAZED_TERRACOTTA = 220
    ORANGE_GLAZED_TERRACOTTA = 221
    MAGENTA_GLAZED_TERRACOTTA = 222
    LIGHT_BLUE_GLAZED_TERRACOTTA = 223
    YELLOW_GLAZED_TERRACOTTA = 224
    LIME_GLAZED_TERRACOTTA = 225
    PINK_GLAZED_TERRACOTTA = 226
    GRAY_GLAZED_TERRACOTTA = 227
    SILVER_GLAZED_TERRACOTTA = 228
    CYAN_GLAZED_TERRACOTTA = 229
    BLUE_GLAZED_TERRACOTTA = 230
    BROWN_GLAZED_TERRACOTTA = 231
    GREEN_GLAZED_TERRACOTTA = 232
    RED_GLAZED_TERRACOTTA = 233
    BLACK_GLAZED_TERRACOTTA = 234
    CONCRETE = 235
    CONCRETE_POWDER = 236
    CHEMISTRY_TABLE = 237
    UNDERWATER_TORCH = 238
    CHORUS_PLANT = 239
    STAINED_GLASS = 240
    CAMERA = 241
    PODZOL = 243
    BEETROOT = 244
    STONECUTTER = 245
    GLOWING_OBSIDIAN = 246
    NETHER_REACTOR = 247
    INFO_UPDATE = 248
    INFO_UPDATE2 = 249
    MOVING_BLOCK = 250
    OBSERVER = 251
    STRUCTURE_BLOCK = 252
    HARD_GLASS = 253
    HARD_STAINED_GLASS = 254
    RESERVED6 = 255

class WorldGenerator:
    """Advanced world generator with multiple biomes and structures"""
    
    def __init__(self, seed: int = None):
        self.seed = seed if seed is not None else random.randint(1, 1000000)
        self.random = random.Random(self.seed)
        
        # Biome configuration
        self.biome_config = {
            Biome.PLAINS: {
                'surface_block': BlockType.GRASS,
                'subsurface_block': BlockType.DIRT,
                'deep_block': BlockType.STONE,
                'surface_height': 64,
                'tree_chance': 0.02,
                'flower_chance': 0.1,
                'tall_grass_chance': 0.3
            },
            Biome.FOREST: {
                'surface_block': BlockType.GRASS,
                'subsurface_block': BlockType.DIRT,
                'deep_block': BlockType.STONE,
                'surface_height': 65,
                'tree_chance': 0.15,
                'flower_chance': 0.05,
                'tall_grass_chance': 0.2
            },
            Biome.DESERT: {
                'surface_block': BlockType.SAND,
                'subsurface_block': BlockType.SAND,
                'deep_block': BlockType.SANDSTONE,
                'surface_height': 62,
                'tree_chance': 0.0,
                'flower_chance': 0.0,
                'tall_grass_chance': 0.0,
                'cactus_chance': 0.1
            },
            Biome.MOUNTAINS: {
                'surface_block': BlockType.STONE,
                'subsurface_block': BlockType.STONE,
                'deep_block': BlockType.STONE,
                'surface_height': 80,
                'tree_chance': 0.05,
                'flower_chance': 0.02,
                'tall_grass_chance': 0.1
            },
            Biome.SWAMP: {
                'surface_block': BlockType.GRASS,
                'subsurface_block': BlockType.DIRT,
                'deep_block': BlockType.STONE,
                'surface_height': 62,
                'tree_chance': 0.1,
                'flower_chance': 0.0,
                'tall_grass_chance': 0.0,
                'lily_pad_chance': 0.3
            }
        }
        
        logger.info(f"World generator initialized with seed: {self.seed}")
    
    def get_biome(self, x: int, z: int) -> int:
        """Get biome at coordinates using noise"""
        # Simple biome generation using noise
        noise_x = self.noise(x * 0.01, 0, z * 0.01)
        noise_z = self.noise(x * 0.02, 0, z * 0.02)
        
        if noise_x < -0.3:
            return Biome.DESERT
        elif noise_x > 0.3:
            return Biome.MOUNTAINS
        elif noise_z > 0.2:
            return Biome.FOREST
        elif noise_z < -0.2:
            return Biome.SWAMP
        else:
            return Biome.PLAINS
    
    def noise(self, x: float, y: float, z: float) -> float:
        """Simple 3D noise function"""
        # Simple hash-based noise
        n = int(x * 73856093) ^ int(y * 19349663) ^ int(z * 83492791)
        return (n & 0x7fffffff) / 0x7fffffff * 2 - 1
    
    def get_height(self, x: int, z: int, biome: int) -> int:
        """Get terrain height at coordinates"""
        config = self.biome_config.get(biome, self.biome_config[Biome.PLAINS])
        base_height = config['surface_height']
        
        # Add noise for terrain variation
        noise_val = self.noise(x * 0.05, 0, z * 0.05)
        height_variation = int(noise_val * 8)
        
        return base_height + height_variation
    
    def generate_chunk(self, chunk_x: int, chunk_z: int) -> Dict:
        """Generate a complete chunk with terrain and structures"""
        chunk_data = {
            'x': chunk_x,
            'z': chunk_z,
            'blocks': {},
            'biome': Biome.PLAINS
        }
        
        # Generate terrain for each block in chunk
        for x in range(16):
            for z in range(16):
                world_x = chunk_x * 16 + x
                world_z = chunk_z * 16 + z
                
                # Get biome and height
                biome = self.get_biome(world_x, world_z)
                height = self.get_height(world_x, world_z, biome)
                config = self.biome_config.get(biome, self.biome_config[Biome.PLAINS])
                
                # Generate terrain layers
                for y in range(128):
                    if y == 0:
                        # Bedrock layer
                        chunk_data['blocks'][(x, y, z)] = BlockType.BEDROCK
                    elif y < height - 4:
                        # Deep stone layer
                        chunk_data['blocks'][(x, y, z)] = config['deep_block']
                    elif y < height:
                        # Subsurface layer
                        chunk_data['blocks'][(x, y, z)] = config['subsurface_block']
                    elif y == height:
                        # Surface layer
                        chunk_data['blocks'][(x, y, z)] = config['surface_block']
                        
                        # Add surface features
                        self.add_surface_features(chunk_data, x, y, z, biome, config)
        
        # Add structures
        self.add_structures(chunk_data, chunk_x, chunk_z)
        
        return chunk_data
    
    def add_surface_features(self, chunk_data: Dict, x: int, y: int, z: int, biome: int, config: Dict):
        """Add surface features like trees, flowers, etc."""
        world_x = chunk_data['x'] * 16 + x
        world_z = chunk_data['z'] * 16 + z
        
        # Trees
        if self.random.random() < config.get('tree_chance', 0):
            self.generate_tree(chunk_data, x, y, z, biome)
        
        # Flowers
        if self.random.random() < config.get('flower_chance', 0):
            flower_type = BlockType.YELLOW_FLOWER if self.random.random() < 0.5 else BlockType.RED_FLOWER
            chunk_data['blocks'][(x, y + 1, z)] = flower_type
        
        # Tall grass
        if self.random.random() < config.get('tall_grass_chance', 0):
            chunk_data['blocks'][(x, y + 1, z)] = BlockType.TALLGRASS
        
        # Cactus (desert)
        if biome == Biome.DESERT and self.random.random() < config.get('cactus_chance', 0):
            self.generate_cactus(chunk_data, x, y, z)
        
        # Lily pads (swamp)
        if biome == Biome.SWAMP and self.random.random() < config.get('lily_pad_chance', 0):
            chunk_data['blocks'][(x, y + 1, z)] = BlockType.WATERLILY
    
    def generate_tree(self, chunk_data: Dict, x: int, y: int, z: int, biome: int):
        """Generate a tree at the specified location"""
        tree_height = self.random.randint(4, 6)
        
        # Generate trunk
        for i in range(tree_height):
            chunk_data['blocks'][(x, y + 1 + i, z)] = BlockType.LOG
        
        # Generate leaves
        leaf_y = y + tree_height
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                for dy in range(0, 3):
                    if abs(dx) + abs(dz) <= 2:  # Diamond shape
                        leaf_x = x + dx
                        leaf_z = z + dz
                        leaf_y_pos = leaf_y + dy
                        
                        if 0 <= leaf_x < 16 and 0 <= leaf_z < 16 and leaf_y_pos < 128:
                            chunk_data['blocks'][(leaf_x, leaf_y_pos, leaf_z)] = BlockType.LEAVES
    
    def generate_cactus(self, chunk_data: Dict, x: int, y: int, z: int):
        """Generate a cactus at the specified location"""
        cactus_height = self.random.randint(2, 4)
        
        for i in range(cactus_height):
            chunk_data['blocks'][(x, y + 1 + i, z)] = BlockType.CACTUS
    
    def add_structures(self, chunk_data: Dict, chunk_x: int, chunk_z: int):
        """Add structures to the chunk"""
        # Simple house generation (1% chance per chunk)
        if self.random.random() < 0.01:
            self.generate_house(chunk_data)
        
        # Cave generation
        self.generate_caves(chunk_data)
    
    def generate_house(self, chunk_data: Dict):
        """Generate a simple house"""
        # House position within chunk
        house_x = self.random.randint(2, 12)
        house_z = self.random.randint(2, 12)
        
        # Find ground level
        ground_y = 64
        for y in range(128):
            if (house_x, y, house_z) in chunk_data['blocks']:
                ground_y = y
                break
        
        # House dimensions
        width = 5
        depth = 5
        height = 4
        
        # Generate house walls
        for x in range(house_x, house_x + width):
            for z in range(house_z, house_z + depth):
                for y in range(ground_y + 1, ground_y + height):
                    if (x == house_x or x == house_x + width - 1 or 
                        z == house_z or z == house_z + depth - 1):
                        chunk_data['blocks'][(x, y, z)] = BlockType.PLANKS
        
        # Generate roof
        for x in range(house_x, house_x + width):
            for z in range(house_z, house_z + depth):
                chunk_data['blocks'][(x, ground_y + height, z)] = BlockType.PLANKS
        
        # Generate door
        chunk_data['blocks'][(house_x + width // 2, ground_y + 1, house_z)] = BlockType.WOODEN_DOOR
        chunk_data['blocks'][(house_x + width // 2, ground_y + 2, house_z)] = BlockType.WOODEN_DOOR
    
    def generate_caves(self, chunk_data: Dict):
        """Generate simple cave systems"""
        # Simple cave generation using noise
        for x in range(16):
            for z in range(16):
                for y in range(10, 60):
                    cave_noise = self.noise(x * 0.1, y * 0.1, z * 0.1)
                    if cave_noise > 0.7:
                        chunk_data['blocks'][(x, y, z)] = BlockType.AIR
    
    def get_spawn_position(self) -> Tuple[int, int, int]:
        """Get a suitable spawn position"""
        # Find a flat area near origin
        for radius in range(1, 10):
            for x in range(-radius, radius + 1):
                for z in range(-radius, radius + 1):
                    if abs(x) == radius or abs(z) == radius:
                        biome = self.get_biome(x, z)
                        if biome == Biome.PLAINS:
                            height = self.get_height(x, z, biome)
                            return (x, height + 1, z)
        
        # Fallback to origin
        return (0, 65, 0)