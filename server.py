"""
Minecraft Bedrock Server - Main server class
Handles connections, players, and server management
"""

import asyncio
import json
import logging
import socket
import threading
import time
from typing import Dict, List, Optional

from network.raknet_improved import RakNetImproved
from player import Player
from world import World
from packets import PacketHandler, PacketID, PlayStatus, PlayerAction, BlockID
from player_manager import PlayerManager
from world_generator import WorldGenerator

logger = logging.getLogger(__name__)

class MinecraftServer:
    """Main Minecraft Bedrock server class"""
    
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 19132
        self.max_players = 20
        self.motd = "Python Bedrock Server"
        self.game_mode = 0  # Survival
        self.difficulty = 1  # Easy
        
        # Server components
        self.raknet = RakNetImproved(self.host, self.port)
        self.world = World()
        self.player_manager = PlayerManager(self)
        self.world_generator = WorldGenerator()
        self.running = False
        
        # Command system
        from commands import CommandManager
        self.command_manager = CommandManager()
    
    async def start(self):
        """Start the Minecraft server"""
        self.running = True
        
        # Load world
        await self.world.load()
        
        # Start RakNet server
        await self.raknet.start()
        
        logger.info(f"Server started on {self.host}:{self.port}")
        logger.info(f"Max players: {self.max_players}")
        logger.info(f"MOTD: {self.motd}")
        
        # Main server loop
        try:
            while self.running:
                # Handle new connections
                await self.handle_new_connections()
                
                # Handle player packets
                await self.handle_player_packets()
                
                # Save world periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    await self.world.save()
                
                await asyncio.sleep(0.05)  # 20 TPS
                
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            await self.shutdown()
    
    async def handle_new_connections(self):
        """Handle new player connections"""
        new_connections = await self.raknet.get_new_connections()
        
        for connection in new_connections:
            try:
                # Handle new connection with player manager
                player = await self.player_manager.handle_new_connection(connection)
                if player:
                    logger.info(f"Player {player.username} connected from {connection.address}")
                
            except Exception as e:
                logger.error(f"Error handling new connection: {e}")
    
    async def handle_player_packets(self):
        """Handle incoming packets from all players"""
        for player in list(self.player_manager.players.values()):
            try:
                if not player.connection.is_connected():
                    await self.player_manager.disconnect_player(player, "Connection lost")
                    continue
                
                # Process player packets
                packets = await player.connection.get_packets()
                for packet in packets:
                    await self.handle_packet(player, packet)
                    
            except Exception as e:
                logger.error(f"Error handling packets for {player.username}: {e}")
                await self.remove_player(player)
    
    async def handle_packet(self, player: Player, packet_data: bytes):
        """Handle a single packet from a player"""
        try:
            packet_id = packet_data[0] if packet_data else 0
            
            if packet_id == PacketID.MOVE_PLAYER_PACKET:
                await self.handle_move_player(player, packet_data)
            elif packet_id == PacketID.PLAYER_ACTION_PACKET:
                await self.handle_player_action(player, packet_data)
            elif packet_id == PacketID.UPDATE_BLOCK_PACKET:
                await self.handle_update_block(player, packet_data)
            elif packet_id == PacketID.TEXT_PACKET:
                await self.handle_text(player, packet_data)
            elif packet_id == PacketID.PLAYER_AUTH_INPUT_PACKET:
                await self.handle_player_auth_input(player, packet_data)
            elif packet_id == PacketID.NETWORK_STACK_LATENCY_PACKET:
                await self.handle_network_latency(player, packet_data)
            elif packet_id == PacketID.BATCH_PACKET:
                await self.handle_batch_packet(player, packet_data)
            else:
                logger.debug(f"Unhandled packet ID: {packet_id:02X} from {player.username}")
                
        except Exception as e:
            logger.error(f"Error handling packet {packet_id:02X} from {player.username}: {e}")
    
    async def handle_move_player(self, player: Player, packet_data: bytes):
        """Handle player movement"""
        try:
            parsed = PacketHandler.parse_move_player_packet(packet_data)
            if parsed:
                player.x = parsed['x']
                player.y = parsed['y']
                player.z = parsed['z']
                player.yaw = parsed['yaw']
                player.pitch = parsed['pitch']
                player.on_ground = parsed['on_ground']
                
                # Broadcast movement to other players
                await self.broadcast_move_player(player)
        except Exception as e:
            logger.error(f"Error handling move player: {e}")
    
    async def handle_player_action(self, player: Player, packet_data: bytes):
        """Handle player actions (break/place blocks)"""
        try:
            parsed = PacketHandler.parse_player_action_packet(packet_data)
            if parsed:
                action = parsed['action']
                x, y, z = parsed['x'], parsed['y'], parsed['z']
                face = parsed['face']
                
                if action == PlayerAction.START_BREAK:
                    # Player started breaking a block
                    block_id = self.world.get_block(x, y, z)
                    if block_id != BlockID.AIR:
                        # Remove block
                        self.world.set_block(x, y, z, BlockID.AIR)
                        # Broadcast block update
                        await self.broadcast_block_update(x, y, z, BlockID.AIR)
                        logger.info(f"Player {player.username} broke block at ({x}, {y}, {z})")
                
                elif action == PlayerAction.STOP_BREAK:
                    # Player stopped breaking a block
                    pass
                    
        except Exception as e:
            logger.error(f"Error handling player action: {e}")
    
    async def handle_update_block(self, player: Player, packet_data: bytes):
        """Handle block updates"""
        try:
            parsed = PacketHandler.parse_update_block_packet(packet_data)
            if parsed:
                x, y, z = parsed['x'], parsed['y'], parsed['z']
                block_id = parsed['block_id']
                flags = parsed['flags']
                
                # Update block in world
                self.world.set_block(x, y, z, block_id)
                
                # Broadcast to other players
                await self.broadcast_block_update(x, y, z, block_id)
                
                logger.info(f"Player {player.username} placed block {block_id} at ({x}, {y}, {z})")
                
        except Exception as e:
            logger.error(f"Error handling update block: {e}")
    
    async def handle_text(self, player: Player, packet_data: bytes):
        """Handle chat messages"""
        try:
            parsed = PacketHandler.parse_text_packet(packet_data)
            if parsed and parsed['message']:
                message = parsed['message']
                await self.broadcast_message(f"<{player.username}> {message}")
                logger.info(f"Chat: {player.username}: {message}")
        except Exception as e:
            logger.error(f"Error handling text packet: {e}")
    
    async def handle_player_auth_input(self, player: Player, packet_data: bytes):
        """Handle player input (movement, actions)"""
        # Simplified input handling
        pass
    
    async def handle_network_latency(self, player: Player, packet_data: bytes):
        """Handle network latency packet"""
        try:
            # Parse timestamp and send back
            if len(packet_data) >= 9:
                timestamp = int.from_bytes(packet_data[1:9], 'little')
                # Send back the same timestamp
                response = PacketHandler.create_network_stack_latency_packet(timestamp)
                await player.connection.send_packet(response)
        except Exception as e:
            logger.error(f"Error handling network latency: {e}")
    
    async def handle_batch_packet(self, player: Player, packet_data: bytes):
        """Handle batch packet (multiple packets compressed)"""
        try:
            from protocol.serializer import BatchPacket
            packets = BatchPacket.decompress_packets(packet_data)
            for packet in packets:
                await self.handle_packet(player, packet)
        except Exception as e:
            logger.error(f"Error handling batch packet: {e}")
    
    async def send_login_success(self, player: Player):
        """Send login success packet to player"""
        packet = PacketHandler.create_play_status_packet(PlayStatus.LOGIN_SUCCESS)
        await player.connection.send_packet(packet)
    
    async def send_start_game(self, player: Player):
        """Send start game packet to player"""
        world_data = {
            'entity_id': player.entity_id,
            'runtime_entity_id': player.entity_id,
            'game_type': self.game_mode,
            'x': player.x,
            'y': player.y,
            'z': player.z,
            'yaw': player.yaw,
            'pitch': player.pitch,
            'seed': self.world.seed,
            'biome_type': 1,  # Plains
            'world_name': self.world.world_name,
            'game_version': '1.20.15',
            'player_permissions': 0,
            'world_game_mode': self.game_mode,
            'difficulty': self.difficulty,
            'spawn_x': self.world.spawn_x,
            'spawn_y': self.world.spawn_y,
            'spawn_z': self.world.spawn_z,
            'time': self.world.time,
            'player_game_mode': self.game_mode
        }
        
        packet = PacketHandler.create_start_game_packet(world_data)
        await player.connection.send_packet(packet)
    
    async def send_spawn_chunks(self, player: Player):
        """Send spawn chunks to player"""
        # Send a few chunks around spawn
        for x in range(-1, 2):
            for z in range(-1, 2):
                chunk_data = await self.world.get_chunk_data(x, z)
                if chunk_data:
                    packet = PacketHandler.create_level_chunk_packet(x, z, chunk_data)
                    await player.connection.send_packet(packet)
    
    async def broadcast_move_player(self, player: Player):
        """Broadcast player movement to other players"""
        for other_player in self.players.values():
            if other_player.guid != player.guid:
                # Send MovePlayerPacket to other players
                packet = PacketHandler.create_move_player_packet(
                    player.entity_id,
                    player.x, player.y, player.z,
                    player.yaw, player.pitch, player.yaw,
                    0, player.on_ground, 0
                )
                await other_player.connection.send_packet(packet)
    
    async def broadcast_block_update(self, x: int, y: int, z: int, block_id: int):
        """Broadcast block update to all players"""
        packet = PacketHandler.create_update_block_packet(x, y, z, block_id, 0)
        for player in self.players.values():
            await player.connection.send_packet(packet)
    
    async def broadcast_message(self, message: str):
        """Broadcast message to all players"""
        packet = PacketHandler.create_text_packet(message, 1)
        for player in self.players.values():
            await player.connection.send_packet(packet)
    
    async def remove_player(self, player: Player):
        """Remove a player from the server"""
        if player.guid in self.players:
            del self.players[player.guid]
            await self.broadcast_message(f"§e{player.username} left the game")
            logger.info(f"Player {player.username} disconnected")
    
    def console_loop(self):
        """Console command loop"""
        while self.running:
            try:
                command = input("> ").strip()
                if command:
                    self.execute_command(command)
            except (EOFError, KeyboardInterrupt):
                break
            except Exception as e:
                logger.error(f"Console error: {e}")
    
    def execute_command(self, command: str):
        """Execute a console command"""
        # Create a dummy player for console commands
        class ConsolePlayer:
            def __init__(self):
                self.username = "Console"
                self.is_op = lambda: True
        
        console_player = ConsolePlayer()
        asyncio.create_task(self.command_manager.execute_command(self, console_player, command))
    

    
    async def shutdown(self):
        """Shutdown the server"""
        logger.info("Shutting down server...")
        
        # Save world
        await self.world.save()
        
        # Disconnect all players
        for player in list(self.players.values()):
            await self.remove_player(player)
        
        # Stop RakNet
        await self.raknet.stop()
        
        logger.info("Server shutdown complete")