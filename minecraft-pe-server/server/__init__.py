#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minecraft PE Server - Пакет сервера
Автор: Minecraft PE Server Team
Версия: 2.0.1
"""

# Импорт основных классов
try:
    from .main_fixed import MinecraftPEServer, Player
    from .raknet_protocol import RakNetProtocol, RakNetSession
    from .bedrock_protocol_v2 import BedrockProtocolV2, BedrockSession
    from .compression import CompressionManager, AdaptiveCompression
    from .chunk_system import ChunkManager, Chunk, SubChunk, Block
    
    __all__ = [
        'MinecraftPEServer',
        'Player',
        'RakNetProtocol',
        'RakNetSession',
        'BedrockProtocolV2',
        'BedrockSession',
        'CompressionManager',
        'AdaptiveCompression',
        'ChunkManager',
        'Chunk',
        'SubChunk',
        'Block'
    ]
    
except ImportError as e:
    # Если модули не найдены, создаем заглушки
    print(f"⚠️ Предупреждение: Некоторые модули не найдены: {e}")
    print("💡 Убедитесь, что все файлы протоколов созданы")
    
    __all__ = []