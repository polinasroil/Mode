"""
Packet definitions and handlers for Minecraft Bedrock Server
Contains packet IDs and complete packet structures
"""

import struct
import time
from typing import Dict, Any, List, Optional

from protocol.serializer import PacketSerializer, PacketDeserializer

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
    SET_ENTITY_DATA_PACKET = 0x27
    SET_PLAYER_GAME_TYPE_PACKET = 0x3E
    ADD_PLAYER_PACKET = 0x0C
    REMOVE_PLAYER_PACKET = 0x0E
    SET_SPAWN_POSITION_PACKET = 0x2D
    SET_DIFFICULTY_PACKET = 0x3C
    SET_GAME_RULES_PACKET = 0x46
    SET_COMMANDS_ENABLED_PACKET = 0x3F
    SET_PLAYER_PERMISSIONS_PACKET = 0x3D
    NETWORK_STACK_LATENCY_PACKET = 0x4E
    RESOURCE_PACKS_INFO_PACKET = 0x06
    RESOURCE_PACK_STACK_PACKET = 0x07
    SET_SPAWN_POSITION_PACKET = 0x2D
    SET_TIME_PACKET = 0x0A
    SET_GAME_RULES_PACKET = 0x46
    SET_COMMANDS_ENABLED_PACKET = 0x3F
    ADD_PLAYER_PACKET = 0x0C
    REMOVE_PLAYER_PACKET = 0x0E
    DISCONNECT_PACKET = 0x05

class PacketHandler:
    """Complete packet handler for Minecraft Bedrock"""
    
    @staticmethod
    def create_login_packet(username: str, protocol_version: int, client_guid: int, identity_public_key: str = "") -> bytes:
        """Create a complete login packet"""
        packet = bytearray()
        packet.append(PacketID.LOGIN_PACKET)
        
        # Protocol version
        packet.extend(PacketSerializer.write_int(protocol_version))
        
        # Login data
        login_data = {
            "username": username,
            "protocol": protocol_version,
            "client_guid": client_guid,
            "identity_public_key": identity_public_key,
            "client_data": {
                "client_random_id": client_guid,
                "device_model": "Python Bedrock Server",
                "device_os": "Python",
                "game_version": "1.20.15",
                "gui_scale": 0,
                "language_code": "en_US",
                "skin_data": "",
                "skin_id": "",
                "premium_skin": False,
                "persona_pieces": [],
                "piece_tint_colors": [],
                "is_editor_mode": False,
                "is_third_party_cape": False,
                "cape_data": "",
                "cape_id": "",
                "cape_on_classic": False,
                "is_third_party_cape": False,
                "arm_size": "slim",
                "skin_color": "#0",
                "personal_pieces": [],
                "piece_tint_colors": []
            }
        }
        
        import json
        login_json = json.dumps(login_data)
        packet.extend(PacketSerializer.write_string(login_json))
        
        return bytes(packet)
    
    @staticmethod
    def create_play_status_packet(status: int) -> bytes:
        """Create a play status packet"""
        packet = bytearray()
        packet.append(PacketID.PLAY_STATUS_PACKET)
        packet.extend(PacketSerializer.write_int(status))
        return bytes(packet)
    
    @staticmethod
    def create_start_game_packet(world_data: Dict[str, Any]) -> bytes:
        """Create a complete start game packet"""
        packet = bytearray()
        packet.append(PacketID.START_GAME_PACKET)
        
        # Entity ID
        packet.extend(PacketSerializer.write_ulong(world_data.get('entity_id', 1)))
        
        # Runtime entity ID
        packet.extend(PacketSerializer.write_ulong(world_data.get('runtime_entity_id', 1)))
        
        # Player game type
        packet.extend(PacketSerializer.write_int(world_data.get('game_type', 0)))
        
        # Player position
        packet.extend(PacketSerializer.write_vector3f(
            world_data.get('x', 0.0),
            world_data.get('y', 64.0),
            world_data.get('z', 0.0)
        ))
        
        # Player rotation
        packet.extend(PacketSerializer.write_float(world_data.get('yaw', 0.0)))
        packet.extend(PacketSerializer.write_float(world_data.get('pitch', 0.0)))
        
        # Seed
        packet.extend(PacketSerializer.write_long(world_data.get('seed', 0)))
        
        # Biome type
        packet.extend(PacketSerializer.write_int(world_data.get('biome_type', 1)))
        
        # World name
        packet.extend(PacketSerializer.write_string(world_data.get('world_name', 'PythonBedrockWorld')))
        
        # Game version
        packet.extend(PacketSerializer.write_string(world_data.get('game_version', '1.20.15')))
        
        # Player permissions
        packet.extend(PacketSerializer.write_int(world_data.get('player_permissions', 0)))
        
        # World game mode
        packet.extend(PacketSerializer.write_int(world_data.get('world_game_mode', 0)))
        
        # Difficulty
        packet.extend(PacketSerializer.write_int(world_data.get('difficulty', 1)))
        
        # Spawn position
        packet.extend(PacketSerializer.write_position(
            world_data.get('spawn_x', 0),
            world_data.get('spawn_y', 64),
            world_data.get('spawn_z', 0)
        ))
        
        # Has achievements disabled
        packet.extend(PacketSerializer.write_bool(world_data.get('achievements_disabled', False)))
        
        # Day cycle stop time
        packet.extend(PacketSerializer.write_int(world_data.get('day_cycle_stop_time', 0)))
        
        # Education edition offer
        packet.extend(PacketSerializer.write_int(world_data.get('education_edition_offer', 0)))
        
        # Education features enabled
        packet.extend(PacketSerializer.write_bool(world_data.get('education_features_enabled', False)))
        
        # Education product ID
        packet.extend(PacketSerializer.write_string(world_data.get('education_product_id', '')))
        
        # Rain level
        packet.extend(PacketSerializer.write_float(world_data.get('rain_level', 0.0)))
        
        # Lightning level
        packet.extend(PacketSerializer.write_float(world_data.get('lightning_level', 0.0)))
        
        # Confirmed platform locked content
        packet.extend(PacketSerializer.write_bool(world_data.get('platform_locked_content', False)))
        
        # Multiplayer game
        packet.extend(PacketSerializer.write_bool(world_data.get('multiplayer_game', True)))
        
        # LAN broadcast
        packet.extend(PacketSerializer.write_bool(world_data.get('lan_broadcast', True)))
        
        # XBL broadcast mode
        packet.extend(PacketSerializer.write_int(world_data.get('xbl_broadcast_mode', 2)))
        
        # Platform broadcast mode
        packet.extend(PacketSerializer.write_int(world_data.get('platform_broadcast_mode', 2)))
        
        # Commands enabled
        packet.extend(PacketSerializer.write_bool(world_data.get('commands_enabled', True)))
        
        # Text filtering enabled
        packet.extend(PacketSerializer.write_bool(world_data.get('text_filtering_enabled', False)))
        
        # Server authoritative movement
        packet.extend(PacketSerializer.write_bool(world_data.get('server_authoritative_movement', True)))
        
        # Player movement settings
        packet.extend(PacketSerializer.write_int(world_data.get('player_movement_settings', 0)))
        
        # Time
        packet.extend(PacketSerializer.write_int(world_data.get('time', 0)))
        
        # Enchantment seed
        packet.extend(PacketSerializer.write_int(world_data.get('enchantment_seed', 0)))
        
        # Custom blocks
        packet.extend(PacketSerializer.write_int(world_data.get('custom_blocks', 0)))
        
        # Item palette
        packet.extend(PacketSerializer.write_int(world_data.get('item_palette', 0)))
        
        # Multiplayer correlation ID
        packet.extend(PacketSerializer.write_string(world_data.get('multiplayer_correlation_id', '')))
        
        # World template ID
        packet.extend(PacketSerializer.write_string(world_data.get('world_template_id', '')))
        
        # Client side generation
        packet.extend(PacketSerializer.write_bool(world_data.get('client_side_generation', False)))
        
        # Block network IDs
        packet.extend(PacketSerializer.write_int(world_data.get('block_network_ids', 0)))
        
        # Server block state cheat
        packet.extend(PacketSerializer.write_bool(world_data.get('server_block_state_cheat', False)))
        
        # Player movement settings
        packet.extend(PacketSerializer.write_int(world_data.get('player_movement_settings', 0)))
        
        # Server authoritative sound
        packet.extend(PacketSerializer.write_bool(world_data.get('server_authoritative_sound', True)))
        
        # Player permission level
        packet.extend(PacketSerializer.write_int(world_data.get('player_permission_level', 0)))
        
        # Custom command permission level
        packet.extend(PacketSerializer.write_int(world_data.get('custom_command_permission_level', 0)))
        
        # Player abilities
        packet.extend(PacketSerializer.write_int(world_data.get('player_abilities', 0)))
        
        # Player user ID
        packet.extend(PacketSerializer.write_int(world_data.get('player_user_id', 0)))
        
        # Player permissions
        packet.extend(PacketSerializer.write_int(world_data.get('player_permissions', 0)))
        
        # World game mode
        packet.extend(PacketSerializer.write_int(world_data.get('world_game_mode', 0)))
        
        # Player game mode
        packet.extend(PacketSerializer.write_int(world_data.get('player_game_mode', 0)))
        
        return bytes(packet)
    
    @staticmethod
    def create_move_player_packet(entity_id: int, x: float, y: float, z: float, yaw: float, pitch: float, head_yaw: float, mode: int, on_ground: bool, tick: int) -> bytes:
        """Create a move player packet"""
        packet = bytearray()
        packet.append(PacketID.MOVE_PLAYER_PACKET)
        
        # Entity ID
        packet.extend(PacketSerializer.write_runtime_entity_id(entity_id))
        
        # Position
        packet.extend(PacketSerializer.write_vector3f(x, y, z))
        
        # Rotation
        packet.extend(PacketSerializer.write_float(pitch))
        packet.extend(PacketSerializer.write_float(yaw))
        packet.extend(PacketSerializer.write_float(head_yaw))
        
        # Mode
        packet.extend(PacketSerializer.write_ubyte(mode))
        
        # On ground
        packet.extend(PacketSerializer.write_bool(on_ground))
        
        # Tick
        packet.extend(PacketSerializer.write_uint(tick))
        
        return bytes(packet)
    
    @staticmethod
    def create_level_chunk_packet(chunk_x: int, chunk_z: int, chunk_data: bytes, sub_chunk_count: int = 16) -> bytes:
        """Create a level chunk packet"""
        packet = bytearray()
        packet.append(PacketID.LEVEL_CHUNK_PACKET)
        
        # Chunk coordinates
        packet.extend(PacketSerializer.write_int(chunk_x))
        packet.extend(PacketSerializer.write_int(chunk_z))
        
        # Sub chunk count
        packet.extend(PacketSerializer.write_uint(sub_chunk_count))
        
        # Chunk data
        packet.extend(PacketSerializer.write_uint(len(chunk_data)))
        packet.extend(chunk_data)
        
        return bytes(packet)
    
    @staticmethod
    def create_update_block_packet(x: int, y: int, z: int, block_id: int, flags: int) -> bytes:
        """Create an update block packet"""
        packet = bytearray()
        packet.append(PacketID.UPDATE_BLOCK_PACKET)
        
        # Block coordinates
        packet.extend(PacketSerializer.write_position(x, y, z))
        
        # Block ID and flags
        packet.extend(PacketSerializer.write_uint(block_id))
        packet.extend(PacketSerializer.write_uint(flags))
        
        return bytes(packet)
    
    @staticmethod
    def create_text_packet(message: str, message_type: int = 1, xuid: str = "", platform_chat_id: str = "") -> bytes:
        """Create a text packet"""
        packet = bytearray()
        packet.append(PacketID.TEXT_PACKET)
        
        # Message type
        packet.extend(PacketSerializer.write_ubyte(message_type))
        
        # XUID
        packet.extend(PacketSerializer.write_string(xuid))
        
        # Platform chat ID
        packet.extend(PacketSerializer.write_string(platform_chat_id))
        
        # Message
        packet.extend(PacketSerializer.write_string(message))
        
        return bytes(packet)
    
    @staticmethod
    def create_set_time_packet(time: int) -> bytes:
        """Create a set time packet"""
        packet = bytearray()
        packet.append(PacketID.SET_TIME_PACKET)
        packet.extend(PacketSerializer.write_int(time))
        return bytes(packet)
    
    @staticmethod
    def create_set_spawn_position_packet(spawn_type: int, x: int, y: int, z: int, dimension: int = 0) -> bytes:
        """Create a set spawn position packet"""
        packet = bytearray()
        packet.append(PacketID.SET_SPAWN_POSITION_PACKET)
        
        packet.extend(PacketSerializer.write_int(spawn_type))
        packet.extend(PacketSerializer.write_position(x, y, z))
        packet.extend(PacketSerializer.write_int(dimension))
        
        return bytes(packet)
    
    @staticmethod
    def create_set_difficulty_packet(difficulty: int) -> bytes:
        """Create a set difficulty packet"""
        packet = bytearray()
        packet.append(PacketID.SET_DIFFICULTY_PACKET)
        packet.extend(PacketSerializer.write_uint(difficulty))
        return bytes(packet)
    
    @staticmethod
    def create_set_commands_enabled_packet(enabled: bool) -> bytes:
        """Create a set commands enabled packet"""
        packet = bytearray()
        packet.append(PacketID.SET_COMMANDS_ENABLED_PACKET)
        packet.extend(PacketSerializer.write_bool(enabled))
        return bytes(packet)
    
    @staticmethod
    def create_set_player_permissions_packet(permission_level: int) -> bytes:
        """Create a set player permissions packet"""
        packet = bytearray()
        packet.append(PacketID.SET_PLAYER_PERMISSIONS_PACKET)
        packet.extend(PacketSerializer.write_uint(permission_level))
        return bytes(packet)
    
    @staticmethod
    def create_network_stack_latency_packet(timestamp: int) -> bytes:
        """Create a network stack latency packet"""
        packet = bytearray()
        packet.append(PacketID.NETWORK_STACK_LATENCY_PACKET)
        packet.extend(PacketSerializer.write_ulong(timestamp))
        return bytes(packet)
    
    @staticmethod
    def parse_move_player_packet(data: bytes) -> Dict[str, Any]:
        """Parse a move player packet"""
        if len(data) < 1 or data[0] != PacketID.MOVE_PLAYER_PACKET:
            return {}
        
        deserializer = PacketDeserializer(data[1:])
        
        try:
            entity_id = deserializer.read_runtime_entity_id()
            position = deserializer.read_vector3f()
            pitch = deserializer.read_float()
            yaw = deserializer.read_float()
            head_yaw = deserializer.read_float()
            mode = deserializer.read_ubyte()
            on_ground = deserializer.read_bool()
            tick = deserializer.read_uint()
            
            return {
                'entity_id': entity_id,
                'x': position[0],
                'y': position[1],
                'z': position[2],
                'pitch': pitch,
                'yaw': yaw,
                'head_yaw': head_yaw,
                'mode': mode,
                'on_ground': on_ground,
                'tick': tick
            }
        except Exception:
            return {}
    
    @staticmethod
    def parse_player_action_packet(data: bytes) -> Dict[str, Any]:
        """Parse a player action packet"""
        if len(data) < 1 or data[0] != PacketID.PLAYER_ACTION_PACKET:
            return {}
        
        deserializer = PacketDeserializer(data[1:])
        
        try:
            entity_id = deserializer.read_runtime_entity_id()
            action = deserializer.read_int()
            position = deserializer.read_position()
            face = deserializer.read_block_face()
            
            return {
                'entity_id': entity_id,
                'action': action,
                'x': position[0],
                'y': position[1],
                'z': position[2],
                'face': face
            }
        except Exception:
            return {}
    
    @staticmethod
    def parse_update_block_packet(data: bytes) -> Dict[str, Any]:
        """Parse an update block packet"""
        if len(data) < 1 or data[0] != PacketID.UPDATE_BLOCK_PACKET:
            return {}
        
        deserializer = PacketDeserializer(data[1:])
        
        try:
            position = deserializer.read_position()
            block_id = deserializer.read_uint()
            flags = deserializer.read_uint()
            
            return {
                'x': position[0],
                'y': position[1],
                'z': position[2],
                'block_id': block_id,
                'flags': flags
            }
        except Exception:
            return {}
    
    @staticmethod
    def parse_text_packet(data: bytes) -> Dict[str, Any]:
        """Parse a text packet"""
        if len(data) < 1 or data[0] != PacketID.TEXT_PACKET:
            return {}
        
        deserializer = PacketDeserializer(data[1:])
        
        try:
            message_type = deserializer.read_ubyte()
            xuid = deserializer.read_string()
            platform_chat_id = deserializer.read_string()
            message = deserializer.read_string()
            
            return {
                'message_type': message_type,
                'xuid': xuid,
                'platform_chat_id': platform_chat_id,
                'message': message
            }
        except Exception:
            return {}

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

# Player actions
class PlayerAction:
    """Player action values"""
    START_BREAK = 0
    ABORT_BREAK = 1
    STOP_BREAK = 2
    GET_UPDATED_BLOCK = 3
    DROP_ITEM = 4
    START_SLEEPING = 5
    STOP_SLEEPING = 6
    RESPAWN = 7
    JUMP = 8
    START_SPRINT = 9
    STOP_SPRINT = 10
    START_SNEAK = 11
    STOP_SNEAK = 12
    DIMENSION_CHANGE_REQUEST = 13
    DIMENSION_CHANGE_ACK = 14
    START_GLIDE = 15
    STOP_GLIDE = 16
    BUILD_DENIED = 17
    CONTINUE_BREAK = 18
    CHANGE_SKIN = 19
    SET_ENCHANTMENT_SEED = 20
    START_SWIMMING = 21
    STOP_SWIMMING = 22
    START_SPIN_ATTACK = 23
    STOP_SPIN_ATTACK = 24
    INTERACT_WITH_BLOCK = 25
    PREDICT_BREAK = 26
    CONTINUE_FISHING = 27
    TELEPORT_TO_ENTITY = 28
    TELEPORT_TO_POSITION = 29
    TELEPORT_TO_POSITION_AND_ROTATION = 30
    TELEPORT_TO_ROTATION = 31
    TELEPORT_TO_ROTATION_AND_POSITION = 32
    TELEPORT_TO_POSITION_AND_ROTATION_AND_DIMENSION = 33
    TELEPORT_TO_POSITION_AND_ROTATION_AND_DIMENSION_AND_FACE = 34
    TELEPORT_TO_POSITION_AND_ROTATION_AND_DIMENSION_AND_FACE_AND_HEAD_Y = 35
    TELEPORT_TO_POSITION_AND_ROTATION_AND_DIMENSION_AND_FACE_AND_HEAD_Y_AND_ON_GROUND = 36
    TELEPORT_TO_POSITION_AND_ROTATION_AND_DIMENSION_AND_FACE_AND_HEAD_Y_AND_ON_GROUND_AND_TICK = 37
    TELEPORT_TO_POSITION_AND_ROTATION_AND_DIMENSION_AND_FACE_AND_HEAD_Y_AND_ON_GROUND_AND_TICK_AND_CAUSE = 38
    TELEPORT_TO_POSITION_AND_ROTATION_AND_DIMENSION_AND_FACE_AND_HEAD_Y_AND_ON_GROUND_AND_TICK_AND_CAUSE_AND_ENTITY_TYPE = 39
    TELEPORT_TO_POSITION_AND_ROTATION_AND_DIMENSION_AND_FACE_AND_HEAD_Y_AND_ON_GROUND_AND_TICK_AND_CAUSE_AND_ENTITY_TYPE_AND_TARGET_ENTITY_TYPE = 40

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