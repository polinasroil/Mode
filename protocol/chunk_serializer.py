"""
Chunk serializer for Minecraft Bedrock
Handles chunk data serialization for network transmission
"""

import struct
from typing import Dict, List, Tuple

class ChunkSerializer:
    """Serializer for Minecraft Bedrock chunks"""
    
    @staticmethod
    def serialize_chunk(chunk_data: Dict) -> bytes:
        """Serialize chunk data for network transmission"""
        data = bytearray()
        
        # Chunk coordinates
        data.extend(struct.pack('<i', chunk_data.get('x', 0)))
        data.extend(struct.pack('<i', chunk_data.get('z', 0)))
        
        # Sub chunk count (16 for full height)
        data.extend(struct.pack('<I', 16))
        
        # Serialize sub chunks
        for y in range(16):
            sub_chunk_data = ChunkSerializer.serialize_sub_chunk(chunk_data, y)
            data.extend(sub_chunk_data)
        
        # Biome data (simplified)
        biome_data = ChunkSerializer.serialize_biome_data(chunk_data)
        data.extend(biome_data)
        
        # Border blocks
        data.extend(struct.pack('<I', 0))  # No border blocks
        
        # Block entities
        data.extend(struct.pack('<I', 0))  # No block entities
        
        return bytes(data)
    
    @staticmethod
    def serialize_sub_chunk(chunk_data: Dict, y: int) -> bytes:
        """Serialize a sub chunk at given Y level"""
        data = bytearray()
        
        # Sub chunk version
        data.append(8)  # Version 8 (Bedrock 1.20+)
        
        # Layer count
        data.append(1)  # Single layer
        
        # Layer data
        layer_data = ChunkSerializer.serialize_layer(chunk_data, y)
        data.extend(layer_data)
        
        return bytes(data)
    
    @staticmethod
    def serialize_layer(chunk_data: Dict, y: int) -> bytes:
        """Serialize a layer within a sub chunk"""
        data = bytearray()
        
        # Block storage version
        data.append(1)  # Version 1
        
        # Palette size
        palette_size = 1
        data.extend(struct.pack('<H', palette_size))
        
        # Palette entries (simplified - just air and stone)
        data.extend(struct.pack('<I', 0))  # Air
        data.extend(struct.pack('<I', 1))  # Stone
        
        # Block data (16x16x16 = 4096 blocks)
        # Simplified: all blocks are stone except top layer which is grass
        for x in range(16):
            for z in range(16):
                if y == 15:  # Top layer
                    data.append(2)  # Grass
                else:
                    data.append(1)  # Stone
        
        return bytes(data)
    
    @staticmethod
    def serialize_biome_data(chunk_data: Dict) -> bytes:
        """Serialize biome data"""
        data = bytearray()
        
        # Biome storage version
        data.append(1)  # Version 1
        
        # Biome palette size
        data.extend(struct.pack('<H', 1))
        
        # Biome palette (Plains)
        data.extend(struct.pack('<I', 1))  # Plains biome
        
        # Biome data (16x16 = 256 biomes)
        for _ in range(256):
            data.append(0)  # All plains
        
        return bytes(data)
    
    @staticmethod
    def create_empty_chunk(x: int, z: int) -> bytes:
        """Create an empty chunk with basic terrain"""
        chunk_data = {
            'x': x,
            'z': z,
            'blocks': {},
            'biome': 1  # Plains
        }
        
        # Generate basic flat world
        for cx in range(16):
            for cz in range(16):
                # Grass layer
                chunk_data['blocks'][(cx, 63, cz)] = 2  # Grass
                # Dirt layers
                for y in range(62, 60, -1):
                    chunk_data['blocks'][(cx, y, cz)] = 3  # Dirt
                # Stone layers
                for y in range(59, 0, -1):
                    chunk_data['blocks'][(cx, y, cz)] = 1  # Stone
        
        return ChunkSerializer.serialize_chunk(chunk_data)
    
    @staticmethod
    def create_flat_world_chunk(x: int, z: int, height: int = 64) -> bytes:
        """Create a flat world chunk"""
        chunk_data = {
            'x': x,
            'z': z,
            'blocks': {},
            'biome': 1  # Plains
        }
        
        # Generate flat world
        for cx in range(16):
            for cz in range(16):
                # Grass layer
                chunk_data['blocks'][(cx, height - 1, cz)] = 2  # Grass
                # Dirt layers
                for y in range(height - 2, height - 4, -1):
                    chunk_data['blocks'][(cx, y, cz)] = 3  # Dirt
                # Stone layers
                for y in range(height - 4, 0, -1):
                    chunk_data['blocks'][(cx, y, cz)] = 1  # Stone
        
        return ChunkSerializer.serialize_chunk(chunk_data)