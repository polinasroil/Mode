"""
Packet definitions and handlers for Minecraft Bedrock Server
Contains packet IDs and basic packet structures
"""

import struct
from typing import Dict, Any

# Minecraft Bedrock Packet IDs
class PacketID:
    """Packet IDs for Minecraft Bedrock protocol"""
    
    # Login packets
    LOGIN_PACKET = 0x01
    PLAY_STATUS_PACKET = 0x02
    DISCONNECT_PACKET = 0x05
    RESOURCE_PACKS_INFO_PACKET = 0x06
    RESOURCE_PACK_STACK_PACKET = 0x07
    RESOURCE_PACK_CLIENT_RESPONSE_PACKET = 0x08
    TEXT_PACKET = 0x09
    SET_TIME_PACKET = 0x0A
    START_GAME_PACKET = 0x0B
    MOVE_PLAYER_PACKET = 0x0C
    PLAYER_AUTH_INPUT_PACKET = 0x0D
    LEVEL_CHUNK_PACKET = 0x3A
    UPDATE_BLOCK_PACKET = 0x1C
    PLAYER_ACTION_PACKET = 0x1B
    BATCH_PACKET = 0xFE

class PacketHandler:
    """Base class for packet handlers"""
    
    @staticmethod
    def create_login_packet(username: str, protocol_version: int, client_guid: int) -> bytes:
        """Create a login packet"""
        packet = bytearray()
        packet.append(PacketID.LOGIN_PACKET)
        
        # Protocol version
        packet.extend(struct.pack('<I', protocol_version))
        
        # Login data (simplified)
        login_data = f"username={username};protocol={protocol_version};client_guid={client_guid}"
        packet.extend(struct.pack('<H', len(login_data)))
        packet.extend(login_data.encode('utf-8'))
        
        return bytes(packet)
    
    @staticmethod
    def create_play_status_packet(status: int) -> bytes:
        """Create a play status packet"""
        packet = bytearray()
        packet.append(PacketID.PLAY_STATUS_PACKET)
        packet.extend(struct.pack('<I', status))
        return bytes(packet)
    
    @staticmethod
    def create_start_game_packet(world_data: Dict[str, Any]) -> bytes:
        """Create a start game packet"""
        packet = bytearray()
        packet.append(PacketID.START_GAME_PACKET)
        
        # Entity ID
        packet.extend(struct.pack('<Q', world_data.get('entity_id', 1)))
        
        # Runtime entity ID
        packet.extend(struct.pack('<Q', world_data.get('runtime_entity_id', 1)))
        
        # Player game type
        packet.extend(struct.pack('<I', world_data.get('game_type', 0)))
        
        # Player position
        packet.extend(struct.pack('<f', world_data.get('x', 0.0)))
        packet.extend(struct.pack('<f', world_data.get('y', 64.0)))
        packet.extend(struct.pack('<f', world_data.get('z', 0.0)))
        
        # Player rotation
        packet.extend(struct.pack('<f', world_data.get('yaw', 0.0)))
        packet.extend(struct.pack('<f', world_data.get('pitch', 0.0)))
        
        # Seed
        packet.extend(struct.pack('<Q', world_data.get('seed', 0)))
        
        # Biome type
        packet.extend(struct.pack('<I', world_data.get('biome_type', 1)))
        
        # World name
        world_name = world_data.get('world_name', 'PythonBedrockWorld')
        packet.extend(struct.pack('<H', len(world_name)))
        packet.extend(world_name.encode('utf-8'))
        
        # Game version
        game_version = world_data.get('game_version', '1.20.15')
        packet.extend(struct.pack('<H', len(game_version)))
        packet.extend(game_version.encode('utf-8'))
        
        # Player permissions
        packet.extend(struct.pack('<I', world_data.get('player_permissions', 0)))
        
        # World game mode
        packet.extend(struct.pack('<I', world_data.get('world_game_mode', 0)))
        
        # Difficulty
        packet.extend(struct.pack('<I', world_data.get('difficulty', 1)))
        
        # Spawn position
        packet.extend(struct.pack('<I', world_data.get('spawn_x', 0)))
        packet.extend(struct.pack('<I', world_data.get('spawn_y', 64)))
        packet.extend(struct.pack('<I', world_data.get('spawn_z', 0)))
        
        # Has achievements disabled
        packet.extend(struct.pack('<?', world_data.get('achievements_disabled', False)))
        
        # Day cycle stop time
        packet.extend(struct.pack('<I', world_data.get('day_cycle_stop_time', 0)))
        
        # Education edition offer
        packet.extend(struct.pack('<I', world_data.get('education_edition_offer', 0)))
        
        # Education features enabled
        packet.extend(struct.pack('<?', world_data.get('education_features_enabled', False)))
        
        # Education product ID
        education_product_id = world_data.get('education_product_id', '')
        packet.extend(struct.pack('<H', len(education_product_id)))
        packet.extend(education_product_id.encode('utf-8'))
        
        # Rain level
        packet.extend(struct.pack('<f', world_data.get('rain_level', 0.0)))
        
        # Lightning level
        packet.extend(struct.pack('<f', world_data.get('lightning_level', 0.0)))
        
        # Confirmed platform locked content
        packet.extend(struct.pack('<?', world_data.get('platform_locked_content', False)))
        
        # Multiplayer game
        packet.extend(struct.pack('<?', world_data.get('multiplayer_game', True)))
        
        # LAN broadcast
        packet.extend(struct.pack('<?', world_data.get('lan_broadcast', True)))
        
        # XBL broadcast mode
        packet.extend(struct.pack('<I', world_data.get('xbl_broadcast_mode', 2)))
        
        # Platform broadcast mode
        packet.extend(struct.pack('<I', world_data.get('platform_broadcast_mode', 2)))
        
        # Commands enabled
        packet.extend(struct.pack('<?', world_data.get('commands_enabled', True)))
        
        # Text filtering enabled
        packet.extend(struct.pack('<?', world_data.get('text_filtering_enabled', False)))
        
        # Server authoritative movement
        packet.extend(struct.pack('<?', world_data.get('server_authoritative_movement', True)))
        
        # Player movement settings
        packet.extend(struct.pack('<I', world_data.get('player_movement_settings', 0)))
        
        # Time
        packet.extend(struct.pack('<I', world_data.get('time', 0)))
        
        # Enchantment seed
        packet.extend(struct.pack('<I', world_data.get('enchantment_seed', 0)))
        
        # Custom blocks
        packet.extend(struct.pack('<I', world_data.get('custom_blocks', 0)))
        
        # Item palette
        packet.extend(struct.pack('<I', world_data.get('item_palette', 0)))
        
        # Multiplayer correlation ID
        correlation_id = world_data.get('multiplayer_correlation_id', '')
        packet.extend(struct.pack('<H', len(correlation_id)))
        packet.extend(correlation_id.encode('utf-8'))
        
        # World template ID
        world_template_id = world_data.get('world_template_id', '')
        packet.extend(struct.pack('<H', len(world_template_id)))
        packet.extend(world_template_id.encode('utf-8'))
        
        # Client side generation
        packet.extend(struct.pack('<?', world_data.get('client_side_generation', False)))
        
        # Block network IDs
        packet.extend(struct.pack('<I', world_data.get('block_network_ids', 0)))
        
        # Server block state cheat
        packet.extend(struct.pack('<?', world_data.get('server_block_state_cheat', False)))
        
        # Player movement settings
        packet.extend(struct.pack('<I', world_data.get('player_movement_settings', 0)))
        
        # Server authoritative sound
        packet.extend(struct.pack('<?', world_data.get('server_authoritative_sound', True)))
        
        # Player permission level
        packet.extend(struct.pack('<I', world_data.get('player_permission_level', 0)))
        
        # Custom command permission level
        packet.extend(struct.pack('<I', world_data.get('custom_command_permission_level', 0)))
        
        # Player abilities
        packet.extend(struct.pack('<I', world_data.get('player_abilities', 0)))
        
        # Player user ID
        packet.extend(struct.pack('<I', world_data.get('player_user_id', 0)))
        
        # Player permissions
        packet.extend(struct.pack('<I', world_data.get('player_permissions', 0)))
        
        # World game mode
        packet.extend(struct.pack('<I', world_data.get('world_game_mode', 0)))
        
        # Player game mode
        packet.extend(struct.pack('<I', world_data.get('player_game_mode', 0)))
        
        return bytes(packet)
    
    @staticmethod
    def create_move_player_packet(entity_id: int, x: float, y: float, z: float, yaw: float, pitch: float, head_yaw: float, mode: int, on_ground: bool, tick: int) -> bytes:
        """Create a move player packet"""
        packet = bytearray()
        packet.append(PacketID.MOVE_PLAYER_PACKET)
        
        # Entity ID
        packet.extend(struct.pack('<Q', entity_id))
        
        # Position
        packet.extend(struct.pack('<f', x))
        packet.extend(struct.pack('<f', y))
        packet.extend(struct.pack('<f', z))
        
        # Rotation
        packet.extend(struct.pack('<f', pitch))
        packet.extend(struct.pack('<f', yaw))
        packet.extend(struct.pack('<f', head_yaw))
        
        # Mode
        packet.extend(struct.pack('<B', mode))
        
        # On ground
        packet.extend(struct.pack('<?', on_ground))
        
        # Tick
        packet.extend(struct.pack('<I', tick))
        
        return bytes(packet)
    
    @staticmethod
    def create_level_chunk_packet(chunk_x: int, chunk_z: int, chunk_data: bytes) -> bytes:
        """Create a level chunk packet"""
        packet = bytearray()
        packet.append(PacketID.LEVEL_CHUNK_PACKET)
        
        # Chunk coordinates
        packet.extend(struct.pack('<I', chunk_x))
        packet.extend(struct.pack('<I', chunk_z))
        
        # Chunk data
        packet.extend(struct.pack('<I', len(chunk_data)))
        packet.extend(chunk_data)
        
        return bytes(packet)
    
    @staticmethod
    def create_update_block_packet(x: int, y: int, z: int, block_id: int, flags: int) -> bytes:
        """Create an update block packet"""
        packet = bytearray()
        packet.append(PacketID.UPDATE_BLOCK_PACKET)
        
        # Block coordinates
        packet.extend(struct.pack('<I', x))
        packet.extend(struct.pack('<I', y))
        packet.extend(struct.pack('<I', z))
        
        # Block ID and flags
        packet.extend(struct.pack('<I', block_id))
        packet.extend(struct.pack('<I', flags))
        
        return bytes(packet)
    
    @staticmethod
    def create_text_packet(message: str, message_type: int = 1) -> bytes:
        """Create a text packet"""
        packet = bytearray()
        packet.append(PacketID.TEXT_PACKET)
        
        # Message type
        packet.extend(struct.pack('<B', message_type))
        
        # Message
        packet.extend(struct.pack('<H', len(message)))
        packet.extend(message.encode('utf-8'))
        
        return bytes(packet)
    
    @staticmethod
    def create_batch_packet(packets: list) -> bytes:
        """Create a batch packet containing multiple packets"""
        packet = bytearray()
        packet.append(PacketID.BATCH_PACKET)
        
        # Combine all packets
        combined_data = b''.join(packets)
        
        # Compress data (simplified - just store as-is)
        packet.extend(struct.pack('<I', len(combined_data)))
        packet.extend(combined_data)
        
        return bytes(packet)

# Play status values
class PlayStatus:
    """Play status values for Minecraft Bedrock"""
    LOGIN_SUCCESS = 0
    LOGIN_FAILED_CLIENT = 1
    LOGIN_FAILED_SERVER = 2
    PLAYER_SPAWN = 3
    LOGIN_FAILED_INVALID_TENANT = 4
    LOGIN_FAILED_VANILLA_EDU = 5
    LOGIN_FAILED_EDU_VANILLA = 6
    LOGIN_FAILED_SERVER_FULL = 7

# Game modes
class GameMode:
    """Game mode values for Minecraft Bedrock"""
    SURVIVAL = 0
    CREATIVE = 1
    ADVENTURE = 2
    SPECTATOR = 3

# Block IDs (simplified)
class BlockID:
    """Common block IDs for Minecraft Bedrock"""
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