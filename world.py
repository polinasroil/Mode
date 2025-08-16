"""
World class for Minecraft Bedrock Server
Handles world generation, chunks, and block management
"""

import json
import logging
import math
import random
import struct
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class Chunk:
    """Represents a 16x16x128 chunk in the world"""
    
    def __init__(self, x: int, z: int):
        self.x = x
        self.z = z
        self.blocks = {}  # (x, y, z) -> block_id
        self.biome = 1  # Plains biome
        self.generated = False
    
    def get_block(self, x: int, y: int, z: int) -> int:
        """Get block ID at position"""
        return self.blocks.get((x, y, z), 0)  # Air by default
    
    def set_block(self, x: int, y: int, z: int, block_id: int):
        """Set block at position"""
        if 0 <= x < 16 and 0 <= y < 128 and 0 <= z < 16:
            if block_id == 0:  # Air
                self.blocks.pop((x, y, z), None)
            else:
                self.blocks[(x, y, z)] = block_id
    
    def generate_flat_world(self):
        """Generate a flat world chunk"""
        if self.generated:
            return
        
        # Generate flat world: grass, dirt, stone
        for x in range(16):
            for z in range(16):
                # Grass layer
                self.set_block(x, 63, z, 2)  # Grass
                # Dirt layers
                for y in range(62, 60, -1):
                    self.set_block(x, y, z, 3)  # Dirt
                # Stone layers
                for y in range(59, 0, -1):
                    self.set_block(x, y, z, 1)  # Stone
        
        self.generated = True
    
    def serialize(self) -> bytes:
        """Serialize chunk to bytes for network transmission"""
        # Simplified chunk serialization
        data = bytearray()
        
        # Chunk header
        data.extend(struct.pack('<i', self.x))  # Chunk X
        data.extend(struct.pack('<i', self.z))  # Chunk Z
        
        # Block data (simplified - just store non-air blocks)
        block_count = len(self.blocks)
        data.extend(struct.pack('<H', block_count))
        
        for (x, y, z), block_id in self.blocks.items():
            data.extend(struct.pack('<BBB', x, y, z))
            data.extend(struct.pack('<H', block_id))
        
        return bytes(data)

class World:
    """Main world class for managing chunks and world data"""
    
    def __init__(self):
        self.chunks: Dict[Tuple[int, int], Chunk] = {}
        self.spawn_x = 0
        self.spawn_y = 64
        self.spawn_z = 0
        self.seed = random.randint(1, 1000000)
        self.time = 0
        self.weather = 0  # Clear
        self.world_name = "PythonBedrockWorld"
        self.save_file = "world.json"
        
        logger.info(f"Created world with seed: {self.seed}")
    
    def get_chunk(self, x: int, z: int) -> Optional[Chunk]:
        """Get or create a chunk at coordinates"""
        chunk_key = (x, z)
        
        if chunk_key not in self.chunks:
            chunk = Chunk(x, z)
            chunk.generate_flat_world()
            self.chunks[chunk_key] = chunk
            logger.debug(f"Generated chunk at ({x}, {z})")
        
        return self.chunks[chunk_key]
    
    def get_block(self, x: int, y: int, z: int) -> int:
        """Get block at world coordinates"""
        chunk_x = x // 16
        chunk_z = z // 16
        local_x = x % 16
        local_z = z % 16
        
        if local_x < 0:
            local_x += 16
        if local_z < 0:
            local_z += 16
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        return chunk.get_block(local_x, y, local_z)
    
    def set_block(self, x: int, y: int, z: int, block_id: int):
        """Set block at world coordinates"""
        chunk_x = x // 16
        chunk_z = z // 16
        local_x = x % 16
        local_z = z % 16
        
        if local_x < 0:
            local_x += 16
        if local_z < 0:
            local_z += 16
        
        chunk = self.get_chunk(chunk_x, chunk_z)
        chunk.set_block(local_x, y, local_z, block_id)
        
        logger.debug(f"Set block {block_id} at ({x}, {y}, {z})")
    
    def get_spawn_position(self) -> Tuple[int, int, int]:
        """Get world spawn position"""
        return (self.spawn_x, self.spawn_y, self.spawn_z)
    
    def set_spawn_position(self, x: int, y: int, z: int):
        """Set world spawn position"""
        self.spawn_x = x
        self.spawn_y = y
        self.spawn_z = z
        logger.info(f"Set spawn position to ({x}, {y}, {z})")
    
    def get_chunk_data(self, x: int, z: int) -> Optional[bytes]:
        """Get serialized chunk data for network transmission"""
        try:
            from protocol.chunk_serializer import ChunkSerializer
            return ChunkSerializer.create_flat_world_chunk(x, z, 64)
        except Exception as e:
            logger.error(f"Error serializing chunk ({x}, {z}): {e}")
            return None
    
    def get_loaded_chunks(self) -> List[Tuple[int, int]]:
        """Get list of loaded chunk coordinates"""
        return list(self.chunks.keys())
    
    def unload_chunk(self, x: int, z: int):
        """Unload a chunk from memory"""
        chunk_key = (x, z)
        if chunk_key in self.chunks:
            del self.chunks[chunk_key]
            logger.debug(f"Unloaded chunk at ({x}, {z})")
    
    def unload_distant_chunks(self, center_x: int, center_z: int, radius: int = 8):
        """Unload chunks that are too far from players"""
        chunks_to_unload = []
        
        for (chunk_x, chunk_z) in self.chunks.keys():
            distance = math.sqrt((chunk_x - center_x) ** 2 + (chunk_z - center_z) ** 2)
            if distance > radius:
                chunks_to_unload.append((chunk_x, chunk_z))
        
        for chunk_x, chunk_z in chunks_to_unload:
            self.unload_chunk(chunk_x, chunk_z)
    
    def generate_structures(self, x: int, z: int):
        """Generate structures in a chunk (simplified)"""
        chunk = self.get_chunk(x, z)
        if not chunk.generated:
            return
        
        # Simple tree generation (10% chance per chunk)
        if random.random() < 0.1:
            tree_x = random.randint(2, 13)
            tree_z = random.randint(2, 13)
            tree_y = 64  # Ground level
            
            # Check if there's grass here
            if chunk.get_block(tree_x, tree_y, tree_z) == 2:  # Grass
                # Generate simple tree
                # Trunk
                for y in range(tree_y + 1, tree_y + 4):
                    chunk.set_block(tree_x, y, tree_z, 17)  # Log
                
                # Leaves
                for dx in range(-2, 3):
                    for dz in range(-2, 3):
                        for dy in range(0, 3):
                            if abs(dx) + abs(dz) <= 2:  # Diamond shape
                                leaf_y = tree_y + 3 + dy
                                if 0 <= leaf_y < 128:
                                    chunk.set_block(tree_x + dx, leaf_y, tree_z + dz, 18)  # Leaves
    
    def update_time(self):
        """Update world time"""
        self.time = (self.time + 1) % 24000  # Minecraft day cycle
    
    def get_time(self) -> int:
        """Get current world time"""
        return self.time
    
    def set_time(self, time: int):
        """Set world time"""
        self.time = time % 24000
    
    def get_weather(self) -> int:
        """Get current weather"""
        return self.weather
    
    def set_weather(self, weather: int):
        """Set weather (0=clear, 1=rain, 2=thunder)"""
        self.weather = weather
    
    async def save(self):
        """Save world to file"""
        try:
            world_data = {
                'seed': self.seed,
                'spawn_x': self.spawn_x,
                'spawn_y': self.spawn_y,
                'spawn_z': self.spawn_z,
                'time': self.time,
                'weather': self.weather,
                'world_name': self.world_name,
                'chunks': {}
            }
            
            # Save chunk data
            for (chunk_x, chunk_z), chunk in self.chunks.items():
                chunk_key = f"{chunk_x},{chunk_z}"
                world_data['chunks'][chunk_key] = {
                    'x': chunk.x,
                    'z': chunk.z,
                    'biome': chunk.biome,
                    'generated': chunk.generated,
                    'blocks': {f"{x},{y},{z}": block_id for (x, y, z), block_id in chunk.blocks.items()}
                }
            
            with open(self.save_file, 'w') as f:
                json.dump(world_data, f, indent=2)
            
            logger.info(f"World saved to {self.save_file}")
            
        except Exception as e:
            logger.error(f"Error saving world: {e}")
    
    async def load(self):
        """Load world from file"""
        try:
            with open(self.save_file, 'r') as f:
                world_data = json.load(f)
            
            self.seed = world_data.get('seed', self.seed)
            self.spawn_x = world_data.get('spawn_x', 0)
            self.spawn_y = world_data.get('spawn_y', 64)
            self.spawn_z = world_data.get('spawn_z', 0)
            self.time = world_data.get('time', 0)
            self.weather = world_data.get('weather', 0)
            self.world_name = world_data.get('world_name', self.world_name)
            
            # Load chunks
            for chunk_key, chunk_data in world_data.get('chunks', {}).items():
                chunk_x = chunk_data['x']
                chunk_z = chunk_data['z']
                chunk = Chunk(chunk_x, chunk_z)
                chunk.biome = chunk_data.get('biome', 1)
                chunk.generated = chunk_data.get('generated', False)
                
                # Load blocks
                for block_key, block_id in chunk_data.get('blocks', {}).items():
                    x, y, z = map(int, block_key.split(','))
                    chunk.blocks[(x, y, z)] = block_id
                
                self.chunks[(chunk_x, chunk_z)] = chunk
            
            logger.info(f"World loaded from {self.save_file}")
            logger.info(f"Loaded {len(self.chunks)} chunks")
            
        except FileNotFoundError:
            logger.info("No world file found, starting with new world")
        except Exception as e:
            logger.error(f"Error loading world: {e}")
    
    def get_world_info(self) -> dict:
        """Get world information"""
        return {
            'name': self.world_name,
            'seed': self.seed,
            'spawn': (self.spawn_x, self.spawn_y, self.spawn_z),
            'time': self.time,
            'weather': self.weather,
            'loaded_chunks': len(self.chunks),
            'total_blocks': sum(len(chunk.blocks) for chunk in self.chunks.values())
        }