"""
Player class for Minecraft Bedrock Server
Handles player data, position, and state
"""

import logging
import random
import string
import time
from typing import Optional

from network.connection import Connection

logger = logging.getLogger(__name__)

class Player:
    """Represents a connected player"""
    
    def __init__(self, connection: Connection):
        self.connection = connection
        self.guid = self._generate_guid()
        self.username = f"Player_{self.guid[:8]}"
        self.x = 0.0
        self.y = 64.0  # Spawn height
        self.z = 0.0
        self.yaw = 0.0
        self.pitch = 0.0
        self.on_ground = True
        self.health = 20.0
        self.max_health = 20.0
        self.hunger = 20
        self.experience = 0
        self.level = 0
        self.game_mode = 0  # Survival
        self.can_fly = False
        self.is_flying = False
        self.creative_mode = False
        
        # Connection state
        self.connected = True
        self.last_ping = time.time()
        self.ping_time = 0
        
        # Player state
        self.spawned = False
        self.inventory = []
        self.selected_slot = 0
        
        logger.info(f"Created player {self.username} with GUID {self.guid}")
    
    def _generate_guid(self) -> str:
        """Generate a unique GUID for the player"""
        return ''.join(random.choices(string.hexdigits.lower(), k=16))
    
    def update_position(self, x: float, y: float, z: float, yaw: float = 0.0, pitch: float = 0.0):
        """Update player position"""
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
    
    def get_position(self) -> tuple:
        """Get current position as tuple"""
        return (self.x, self.y, self.z, self.yaw, self.pitch)
    
    def is_online(self) -> bool:
        """Check if player is still connected"""
        return self.connected and self.connection.is_connected()
    
    def disconnect(self):
        """Disconnect the player"""
        self.connected = False
        self.connection.close()
        logger.info(f"Player {self.username} disconnected")
    
    def send_packet(self, packet_data: bytes):
        """Send a packet to this player"""
        if self.is_online():
            try:
                import asyncio
                asyncio.create_task(self.connection.send_packet(packet_data))
            except Exception as e:
                logger.error(f"Error sending packet to {self.username}: {e}")
                self.disconnect()
    
    def update_ping(self, ping_time: int):
        """Update player ping time"""
        self.ping_time = ping_time
        self.last_ping = time.time()
    
    def get_ping(self) -> int:
        """Get current ping time in milliseconds"""
        return self.ping_time
    
    def set_game_mode(self, game_mode: int):
        """Set player game mode"""
        self.game_mode = game_mode
        self.creative_mode = (game_mode == 1)  # Creative
        self.can_fly = self.creative_mode
    
    def set_health(self, health: float):
        """Set player health"""
        self.health = max(0.0, min(health, self.max_health))
    
    def damage(self, amount: float):
        """Damage the player"""
        self.set_health(self.health - amount)
        if self.health <= 0:
            self.respawn()
    
    def heal(self, amount: float):
        """Heal the player"""
        self.set_health(self.health + amount)
    
    def respawn(self):
        """Respawn the player at spawn point"""
        self.x = 0.0
        self.y = 64.0
        self.z = 0.0
        self.health = self.max_health
        self.hunger = 20
        logger.info(f"Player {self.username} respawned")
    
    def get_display_name(self) -> str:
        """Get player display name"""
        return self.username
    
    def has_permission(self, permission: str) -> bool:
        """Check if player has permission (simplified)"""
        # For now, all players have basic permissions
        return True
    
    def is_op(self) -> bool:
        """Check if player is operator (simplified)"""
        return False
    
    def to_dict(self) -> dict:
        """Convert player to dictionary for serialization"""
        return {
            'guid': self.guid,
            'username': self.username,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'yaw': self.yaw,
            'pitch': self.pitch,
            'health': self.health,
            'max_health': self.max_health,
            'hunger': self.hunger,
            'experience': self.experience,
            'level': self.level,
            'game_mode': self.game_mode,
            'ping': self.ping_time
        }
    
    def from_dict(self, data: dict):
        """Load player from dictionary"""
        self.guid = data.get('guid', self.guid)
        self.username = data.get('username', self.username)
        self.x = data.get('x', 0.0)
        self.y = data.get('y', 64.0)
        self.z = data.get('z', 0.0)
        self.yaw = data.get('yaw', 0.0)
        self.pitch = data.get('pitch', 0.0)
        self.health = data.get('health', 20.0)
        self.max_health = data.get('max_health', 20.0)
        self.hunger = data.get('hunger', 20)
        self.experience = data.get('experience', 0)
        self.level = data.get('level', 0)
        self.game_mode = data.get('game_mode', 0)
        self.ping_time = data.get('ping', 0)
    
    def __str__(self) -> str:
        return f"Player({self.username}, {self.guid[:8]})"
    
    def __repr__(self) -> str:
        return self.__str__()