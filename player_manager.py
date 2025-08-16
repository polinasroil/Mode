"""
Advanced player manager for Minecraft Bedrock Server
Handles player connections, spawning, and world interaction
"""

import asyncio
import logging
import time
import random
from typing import Dict, List, Optional, Tuple

from player import Player
from packets import PacketHandler, PacketID, PlayStatus, GameMode, BlockID
from world_generator import WorldGenerator, Biome
from protocol.serializer import PacketSerializer

logger = logging.getLogger(__name__)

class PlayerManager:
    """Advanced player manager with full connection support"""
    
    def __init__(self, server):
        self.server = server
        self.players: Dict[str, Player] = {}
        self.player_entities: Dict[int, Player] = {}
        self.next_entity_id = 1
        self.world_generator = WorldGenerator()
        
        # Player states
        self.connecting_players: Dict[str, Dict] = {}
        self.spawning_players: List[Player] = []
        
        logger.info("Player manager initialized")
    
    async def handle_new_connection(self, connection) -> Optional[Player]:
        """Handle new player connection with full protocol"""
        try:
            # Create new player
            player = Player(connection)
            player.entity_id = self.next_entity_id
            self.next_entity_id += 1
            
            # Store player
            self.players[player.guid] = player
            self.player_entities[player.entity_id] = player
            
            # Set connecting state
            self.connecting_players[player.guid] = {
                'player': player,
                'stage': 'connecting',
                'timestamp': time.time()
            }
            
            logger.info(f"New player connecting: {player.username} (GUID: {player.guid})")
            
            # Start connection sequence
            await self.start_connection_sequence(player)
            
            return player
            
        except Exception as e:
            logger.error(f"Error handling new connection: {e}")
            return None
    
    async def start_connection_sequence(self, player: Player):
        """Start the full connection sequence for a player"""
        try:
            # Stage 1: Send login success
            await self.send_login_success(player)
            logger.debug(f"Sent login success to {player.username}")
            
            # Stage 2: Send resource packs info (simplified)
            await self.send_resource_packs_info(player)
            logger.debug(f"Sent resource packs info to {player.username}")
            
            # Stage 3: Send resource pack stack
            await self.send_resource_pack_stack(player)
            logger.debug(f"Sent resource pack stack to {player.username}")
            
            # Stage 4: Wait for client response
            await asyncio.sleep(0.1)
            
            # Stage 5: Send start game
            await self.send_start_game(player)
            logger.debug(f"Sent start game to {player.username}")
            
            # Stage 6: Send spawn position
            await self.send_spawn_position(player)
            logger.debug(f"Sent spawn position to {player.username}")
            
            # Stage 7: Send time and weather
            await self.send_time_and_weather(player)
            logger.debug(f"Sent time and weather to {player.username}")
            
            # Stage 8: Send game rules
            await self.send_game_rules(player)
            logger.debug(f"Sent game rules to {player.username}")
            
            # Stage 9: Send commands enabled
            await self.send_commands_enabled(player)
            logger.debug(f"Sent commands enabled to {player.username}")
            
            # Stage 10: Send player permissions
            await self.send_player_permissions(player)
            logger.debug(f"Sent player permissions to {player.username}")
            
            # Stage 11: Send spawn chunks
            await self.send_spawn_chunks(player)
            logger.debug(f"Sent spawn chunks to {player.username}")
            
            # Stage 12: Spawn player
            await self.spawn_player(player)
            logger.info(f"Player {player.username} fully connected and spawned")
            
            # Update state
            self.connecting_players[player.guid]['stage'] = 'connected'
            self.spawning_players.append(player)
            
            # Broadcast player join
            await self.broadcast_player_join(player)
            
        except Exception as e:
            logger.error(f"Error in connection sequence for {player.username}: {e}")
            await self.disconnect_player(player, "Connection error")
    
    async def send_login_success(self, player: Player):
        """Send login success packet"""
        packet = PacketHandler.create_play_status_packet(PlayStatus.LOGIN_SUCCESS)
        await player.connection.send_packet(packet)
    
    async def send_resource_packs_info(self, player: Player):
        """Send resource packs info packet"""
        # Simplified resource packs info
        packet = bytearray()
        packet.append(PacketID.RESOURCE_PACKS_INFO_PACKET)
        packet.extend(PacketSerializer.write_bool(False))  # Must accept
        packet.extend(PacketSerializer.write_bool(False))  # Has scripts
        packet.extend(PacketSerializer.write_ushort(0))  # Behavior pack count
        packet.extend(PacketSerializer.write_ushort(0))  # Resource pack count
        
        await player.connection.send_packet(bytes(packet))
    
    async def send_resource_pack_stack(self, player: Player):
        """Send resource pack stack packet"""
        # Simplified resource pack stack
        packet = bytearray()
        packet.append(PacketID.RESOURCE_PACK_STACK_PACKET)
        packet.extend(PacketSerializer.write_bool(False))  # Must accept
        packet.extend(PacketSerializer.write_ushort(0))  # Behavior pack count
        packet.extend(PacketSerializer.write_ushort(0))  # Resource pack count
        
        await player.connection.send_packet(bytes(packet))
    
    async def send_start_game(self, player: Player):
        """Send comprehensive start game packet"""
        world_data = {
            'entity_id': player.entity_id,
            'runtime_entity_id': player.entity_id,
            'game_type': self.server.game_mode,
            'x': player.x,
            'y': player.y,
            'z': player.z,
            'yaw': player.yaw,
            'pitch': player.pitch,
            'seed': self.server.world.seed,
            'biome_type': Biome.PLAINS,
            'world_name': self.server.world.world_name,
            'game_version': '1.20.15',
            'player_permissions': 0,
            'world_game_mode': self.server.game_mode,
            'difficulty': self.server.difficulty,
            'spawn_x': self.server.world.spawn_x,
            'spawn_y': self.server.world.spawn_y,
            'spawn_z': self.server.world.spawn_z,
            'time': self.server.world.time,
            'player_game_mode': self.server.game_mode,
            'multiplayer_game': True,
            'lan_broadcast': True,
            'commands_enabled': True,
            'text_filtering_enabled': False,
            'server_authoritative_movement': True,
            'player_movement_settings': 0,
            'server_authoritative_sound': True,
            'player_permission_level': 0,
            'custom_command_permission_level': 0,
            'player_abilities': 0,
            'player_user_id': 0,
            'player_permissions': 0,
            'world_game_mode': self.server.game_mode,
            'player_game_mode': self.server.game_mode
        }
        
        packet = PacketHandler.create_start_game_packet(world_data)
        await player.connection.send_packet(packet)
    
    async def send_spawn_position(self, player: Player):
        """Send spawn position packet"""
        packet = PacketHandler.create_set_spawn_position_packet(
            2,  # Spawn type (player spawn)
            self.server.world.spawn_x,
            self.server.world.spawn_y,
            self.server.world.spawn_z,
            0  # Dimension
        )
        await player.connection.send_packet(packet)
    
    async def send_time_and_weather(self, player: Player):
        """Send time and weather packets"""
        # Send time
        time_packet = PacketHandler.create_set_time_packet(self.server.world.time)
        await player.connection.send_packet(time_packet)
        
        # Send weather (clear)
        weather_packet = bytearray()
        weather_packet.append(PacketID.SET_TIME_PACKET)  # Reuse time packet ID for weather
        weather_packet.extend(PacketSerializer.write_int(0))  # Clear weather
        await player.connection.send_packet(bytes(weather_packet))
    
    async def send_game_rules(self, player: Player):
        """Send game rules packet"""
        # Simplified game rules
        packet = bytearray()
        packet.append(PacketID.SET_GAME_RULES_PACKET)
        packet.extend(PacketSerializer.write_uint(0))  # No rules
        
        await player.connection.send_packet(bytes(packet))
    
    async def send_commands_enabled(self, player: Player):
        """Send commands enabled packet"""
        packet = PacketHandler.create_set_commands_enabled_packet(True)
        await player.connection.send_packet(packet)
    
    async def send_player_permissions(self, player: Player):
        """Send player permissions packet"""
        packet = PacketHandler.create_set_player_permissions_packet(0)  # Normal player
        await player.connection.send_packet(packet)
    
    async def send_spawn_chunks(self, player: Player):
        """Send spawn chunks to player"""
        # Send chunks around spawn area
        spawn_chunk_x = self.server.world.spawn_x // 16
        spawn_chunk_z = self.server.world.spawn_z // 16
        
        for x in range(spawn_chunk_x - 2, spawn_chunk_x + 3):
            for z in range(spawn_chunk_z - 2, spawn_chunk_z + 3):
                chunk_data = await self.server.world.get_chunk_data(x, z)
                if chunk_data:
                    packet = PacketHandler.create_level_chunk_packet(x, z, chunk_data)
                    await player.connection.send_packet(packet)
                    await asyncio.sleep(0.01)  # Small delay between chunks
    
    async def spawn_player(self, player: Player):
        """Spawn player in the world"""
        try:
            # Get spawn position
            spawn_pos = self.world_generator.get_spawn_position()
            player.x, player.y, player.z = spawn_pos
            
            # Send player spawn packet to all players
            await self.broadcast_player_spawn(player)
            
            # Send other players to the new player
            await self.send_existing_players(player)
            
            logger.info(f"Player {player.username} spawned at {spawn_pos}")
            
        except Exception as e:
            logger.error(f"Error spawning player {player.username}: {e}")
    
    async def broadcast_player_spawn(self, player: Player):
        """Broadcast player spawn to all other players"""
        # Create add player packet
        packet = bytearray()
        packet.append(PacketID.ADD_PLAYER_PACKET)
        
        # Player UUID
        packet.extend(PacketSerializer.write_string(player.guid))
        
        # Player name
        packet.extend(PacketSerializer.write_string(player.username))
        
        # Player position
        packet.extend(PacketSerializer.write_vector3f(player.x, player.y, player.z))
        
        # Player motion
        packet.extend(PacketSerializer.write_vector3f(0.0, 0.0, 0.0))
        
        # Player rotation
        packet.extend(PacketSerializer.write_float(player.pitch))
        packet.extend(PacketSerializer.write_float(player.yaw))
        packet.extend(PacketSerializer.write_float(player.yaw))  # Head yaw
        
        # Player data
        packet.extend(PacketSerializer.write_uint(0))  # Flags
        packet.extend(PacketSerializer.write_uint(0))  # Command permission
        packet.extend(PacketSerializer.write_uint(0))  # Action permissions
        packet.extend(PacketSerializer.write_uint(0))  # Permission level
        packet.extend(PacketSerializer.write_uint(0))  # Custom stored permissions
        packet.extend(PacketSerializer.write_uint(0))  # User ID
        
        # Entity links
        packet.extend(PacketSerializer.write_uint(0))  # Entity links count
        
        # Send to all other players
        for other_player in self.players.values():
            if other_player.guid != player.guid:
                await other_player.connection.send_packet(bytes(packet))
    
    async def send_existing_players(self, player: Player):
        """Send existing players to the new player"""
        for other_player in self.players.values():
            if other_player.guid != player.guid:
                # Create add player packet for existing player
                packet = bytearray()
                packet.append(PacketID.ADD_PLAYER_PACKET)
                
                # Player UUID
                packet.extend(PacketSerializer.write_string(other_player.guid))
                
                # Player name
                packet.extend(PacketSerializer.write_string(other_player.username))
                
                # Player position
                packet.extend(PacketSerializer.write_vector3f(other_player.x, other_player.y, other_player.z))
                
                # Player motion
                packet.extend(PacketSerializer.write_vector3f(0.0, 0.0, 0.0))
                
                # Player rotation
                packet.extend(PacketSerializer.write_float(other_player.pitch))
                packet.extend(PacketSerializer.write_float(other_player.yaw))
                packet.extend(PacketSerializer.write_float(other_player.yaw))  # Head yaw
                
                # Player data
                packet.extend(PacketSerializer.write_uint(0))  # Flags
                packet.extend(PacketSerializer.write_uint(0))  # Command permission
                packet.extend(PacketSerializer.write_uint(0))  # Action permissions
                packet.extend(PacketSerializer.write_uint(0))  # Permission level
                packet.extend(PacketSerializer.write_uint(0))  # Custom stored permissions
                packet.extend(PacketSerializer.write_uint(0))  # User ID
                
                # Entity links
                packet.extend(PacketSerializer.write_uint(0))  # Entity links count
                
                await player.connection.send_packet(bytes(packet))
    
    async def broadcast_player_join(self, player: Player):
        """Broadcast player join message"""
        message = f"§e{player.username} joined the game"
        await self.server.broadcast_message(message)
    
    async def broadcast_player_leave(self, player: Player):
        """Broadcast player leave message"""
        message = f"§e{player.username} left the game"
        await self.server.broadcast_message(message)
    
    async def disconnect_player(self, player: Player, reason: str = "Disconnected"):
        """Disconnect a player"""
                try:
            # Send disconnect packet
            packet = bytearray()
            packet.append(PacketID.DISCONNECT_PACKET)
            packet.extend(PacketSerializer.write_string(reason))
            packet.extend(PacketSerializer.write_bool(False))  # Hide disconnect screen
            
            await player.connection.send_packet(bytes(packet))
            
            # Remove player from lists
            if player.guid in self.players:
                del self.players[player.guid]
            
            if player.entity_id in self.player_entities:
                del self.player_entities[player.entity_id]
            
            if player.guid in self.connecting_players:
                del self.connecting_players[player.guid]
            
            if player in self.spawning_players:
                self.spawning_players.remove(player)
            
            # Broadcast player leave
            await self.broadcast_player_leave(player)
            
            # Close connection
            player.connection.close()
            
            logger.info(f"Player {player.username} disconnected: {reason}")
            
        except Exception as e:
            logger.error(f"Error disconnecting player {player.username}: {e}")
    
    def get_player_by_guid(self, guid: str) -> Optional[Player]:
        """Get player by GUID"""
        return self.players.get(guid)
    
    def get_player_by_entity_id(self, entity_id: int) -> Optional[Player]:
        """Get player by entity ID"""
        return self.player_entities.get(entity_id)
    
    def get_online_players(self) -> List[Player]:
        """Get list of online players"""
        return list(self.players.values())
    
    def get_player_count(self) -> int:
        """Get number of online players"""
        return len(self.players)
    
    async def broadcast_to_players(self, packet: bytes, exclude_player: Player = None):
        """Broadcast packet to all players except excluded one"""
        for player in self.players.values():
            if player != exclude_player:
                await player.connection.send_packet(packet)
    
    async def update_player_position(self, player: Player, x: float, y: float, z: float, yaw: float, pitch: float):
        """Update player position and broadcast to others"""
        player.x, player.y, player.z = x, y, z
        player.yaw, player.pitch = yaw, pitch
        
        # Broadcast movement to other players
        packet = PacketHandler.create_move_player_packet(
            player.entity_id,
            x, y, z,
            yaw, pitch, yaw,  # Head yaw same as yaw
            0,  # Mode
            True,  # On ground
            0  # Tick
        )
        
        await self.broadcast_to_players(packet, player)
    
    async def handle_player_chat(self, player: Player, message: str):
        """Handle player chat message"""
        # Format chat message
        formatted_message = f"<{player.username}> {message}"
        
        # Create text packet
        packet = PacketHandler.create_text_packet(formatted_message, 1)
        
        # Broadcast to all players
        await self.broadcast_to_players(packet)
        
        logger.info(f"Chat: {player.username}: {message}")
    
    async def handle_block_break(self, player: Player, x: int, y: int, z: int):
        """Handle player breaking a block"""
        # Update world
        self.server.world.set_block(x, y, z, BlockID.AIR)
        
        # Broadcast block update
        packet = PacketHandler.create_update_block_packet(x, y, z, BlockID.AIR, 0)
        await self.broadcast_to_players(packet)
        
        logger.info(f"Player {player.username} broke block at ({x}, {y}, {z})")
    
    async def handle_block_place(self, player: Player, x: int, y: int, z: int, block_id: int):
        """Handle player placing a block"""
        # Update world
        self.server.world.set_block(x, y, z, block_id)
        
        # Broadcast block update
        packet = PacketHandler.create_update_block_packet(x, y, z, block_id, 0)
        await self.broadcast_to_players(packet)
        
        logger.info(f"Player {player.username} placed block {block_id} at ({x}, {y}, {z})")