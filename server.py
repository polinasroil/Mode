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

from network.raknet import RakNetServer
from player import Player
from world import World

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
        self.raknet = RakNetServer(self.host, self.port)
        self.world = World()
        self.players: Dict[str, Player] = {}
        self.running = False
        
        # Console commands
        self.commands = {
            'stop': self.stop_server,
            'say': self.say_command,
            'kick': self.kick_command,
            'list': self.list_command,
            'help': self.help_command
        }
    
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
                # Create new player
                player = Player(connection)
                self.players[player.guid] = player
                
                logger.info(f"Player {player.username} connected from {connection.address}")
                
                # Send login success
                await self.send_login_success(player)
                
                # Send start game packet
                await self.send_start_game(player)
                
                # Send spawn chunks
                await self.send_spawn_chunks(player)
                
                # Broadcast player join
                await self.broadcast_message(f"§e{player.username} joined the game")
                
            except Exception as e:
                logger.error(f"Error handling new connection: {e}")
    
    async def handle_player_packets(self):
        """Handle incoming packets from all players"""
        for player in list(self.players.values()):
            try:
                if not player.connection.is_connected():
                    await self.remove_player(player)
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
            
            if packet_id == 0x0C:  # MovePlayerPacket
                await self.handle_move_player(player, packet_data)
            elif packet_id == 0x1B:  # PlayerActionPacket
                await self.handle_player_action(player, packet_data)
            elif packet_id == 0x1C:  # UpdateBlockPacket
                await self.handle_update_block(player, packet_data)
            elif packet_id == 0x09:  # TextPacket
                await self.handle_text(player, packet_data)
            elif packet_id == 0x0D:  # PlayerAuthInputPacket
                await self.handle_player_auth_input(player, packet_data)
                
        except Exception as e:
            logger.error(f"Error handling packet {packet_id:02X} from {player.username}: {e}")
    
    async def handle_move_player(self, player: Player, packet_data: bytes):
        """Handle player movement"""
        # Parse position from packet (simplified)
        if len(packet_data) >= 13:
            x = int.from_bytes(packet_data[1:5], 'little', signed=True) / 32
            y = int.from_bytes(packet_data[5:9], 'little', signed=True) / 32
            z = int.from_bytes(packet_data[9:13], 'little', signed=True) / 32
            
            player.x, player.y, player.z = x, y, z
            
            # Broadcast movement to other players
            await self.broadcast_move_player(player)
    
    async def handle_player_action(self, player: Player, packet_data: bytes):
        """Handle player actions (break/place blocks)"""
        # Simplified block action handling
        pass
    
    async def handle_update_block(self, player: Player, packet_data: bytes):
        """Handle block updates"""
        # Simplified block update handling
        pass
    
    async def handle_text(self, player: Player, packet_data: bytes):
        """Handle chat messages"""
        # Parse chat message (simplified)
        if len(packet_data) > 1:
            message = packet_data[1:].decode('utf-8', errors='ignore')
            await self.broadcast_message(f"<{player.username}> {message}")
    
    async def handle_player_auth_input(self, player: Player, packet_data: bytes):
        """Handle player input (movement, actions)"""
        # Simplified input handling
        pass
    
    async def send_login_success(self, player: Player):
        """Send login success packet to player"""
        packet = b'\x02' + player.guid.encode() + b'\x00'  # Simplified
        await player.connection.send_packet(packet)
    
    async def send_start_game(self, player: Player):
        """Send start game packet to player"""
        # Simplified StartGamePacket
        packet = b'\x0B' + b'\x00' * 100  # Placeholder
        await player.connection.send_packet(packet)
    
    async def send_spawn_chunks(self, player: Player):
        """Send spawn chunks to player"""
        # Send a few chunks around spawn
        for x in range(-1, 2):
            for z in range(-1, 2):
                chunk_data = await self.world.get_chunk(x, z)
                if chunk_data:
                    packet = b'\x3A' + chunk_data  # LevelChunkPacket
                    await player.connection.send_packet(packet)
    
    async def broadcast_move_player(self, player: Player):
        """Broadcast player movement to other players"""
        for other_player in self.players.values():
            if other_player.guid != player.guid:
                # Send MovePlayerPacket to other players
                packet = b'\x0C' + player.guid.encode() + b'\x00' * 12
                await other_player.connection.send_packet(packet)
    
    async def broadcast_message(self, message: str):
        """Broadcast message to all players"""
        packet = b'\x09' + message.encode('utf-8')
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
        parts = command.split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd in self.commands:
            try:
                self.commands[cmd](args)
            except Exception as e:
                logger.error(f"Command error: {e}")
        else:
            logger.info(f"Unknown command: {cmd}. Type 'help' for available commands.")
    
    def stop_server(self, args):
        """Stop the server"""
        logger.info("Stopping server...")
        self.running = False
    
    def say_command(self, args):
        """Say command - broadcast message"""
        if args:
            message = " ".join(args)
            asyncio.create_task(self.broadcast_message(f"[Server] {message}"))
            logger.info(f"Server: {message}")
        else:
            logger.info("Usage: say <message>")
    
    def kick_command(self, args):
        """Kick a player"""
        if args:
            username = args[0]
            for player in self.players.values():
                if player.username.lower() == username.lower():
                    asyncio.create_task(self.remove_player(player))
                    logger.info(f"Kicked player: {username}")
                    return
            logger.info(f"Player not found: {username}")
        else:
            logger.info("Usage: kick <username>")
    
    def list_command(self, args):
        """List online players"""
        if self.players:
            player_list = ", ".join([p.username for p in self.players.values()])
            logger.info(f"Online players ({len(self.players)}): {player_list}")
        else:
            logger.info("No players online")
    
    def help_command(self, args):
        """Show help"""
        logger.info("Available commands:")
        logger.info("  stop - Stop the server")
        logger.info("  say <message> - Broadcast message")
        logger.info("  kick <username> - Kick a player")
        logger.info("  list - List online players")
        logger.info("  help - Show this help")
    
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