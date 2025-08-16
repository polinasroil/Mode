# Minecraft Bedrock Edition Packet IDs and Constants
# Based on protocol version 1.20.15+

# Packet IDs
PACKET_IDS = {
    # Connection packets
    'LOGIN_PACKET': 0x01,
    'PLAY_STATUS_PACKET': 0x02,
    'DISCONNECT_PACKET': 0x05,
    'START_GAME_PACKET': 0x0B,
    'LEVEL_CHUNK_PACKET': 0x3A,
    'MOVE_PLAYER_PACKET': 0x13,
    'PLAYER_ACTION_PACKET': 0x1C,
    'UPDATE_BLOCK_PACKET': 0x15,
    'TEXT_PACKET': 0x09,
    'BATCH_PACKET': 0x90,
    
    # RakNet packets
    'UNCONNECTED_PING': 0x01,
    'UNCONNECTED_PONG': 0x1C,
    'OPEN_CONNECTION_REQUEST_1': 0x05,
    'OPEN_CONNECTION_REPLY_1': 0x06,
    'OPEN_CONNECTION_REQUEST_2': 0x07,
    'OPEN_CONNECTION_REPLY_2': 0x08,
    'CONNECTION_REQUEST': 0x09,
    'CONNECTION_REQUEST_ACCEPTED': 0x10,
    'NEW_INCOMING_CONNECTION': 0x13,
    'DISCONNECTION_NOTIFICATION': 0x15,
    'CONNECTION_LOST': 0x16,
    'CONNECTED_PING': 0x00,
    'CONNECTED_PONG': 0x03,
}

# Block IDs
BLOCK_IDS = {
    'AIR': 0,
    'STONE': 1,
    'GRASS': 2,
    'DIRT': 3,
    'COBBLESTONE': 4,
    'WOOD': 5,
    'SAPLING': 6,
    'BEDROCK': 7,
    'WATER': 9,
    'SAND': 12,
    'GRAVEL': 13,
    'GOLD_ORE': 14,
    'IRON_ORE': 15,
    'COAL_ORE': 16,
    'LOG': 17,
    'LEAVES': 18,
    'SPONGE': 19,
    'GLASS': 20,
    'REDSTONE_ORE': 73,
    'DIAMOND_ORE': 56,
    'EMERALD_ORE': 129,
}

# Game modes
GAME_MODES = {
    'SURVIVAL': 0,
    'CREATIVE': 1,
    'ADVENTURE': 2,
    'SPECTATOR': 3,
}

# Biomes
BIOMES = {
    'PLAINS': 1,
    'FOREST': 4,
    'DESERT': 2,
    'MOUNTAINS': 3,
    'OCEAN': 0,
}

# Protocol version
PROTOCOL_VERSION = 662  # 1.20.15
GAME_VERSION = "1.20.15"