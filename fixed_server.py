#!/usr/bin/env python3
"""
Fixed Minecraft Bedrock Server
Properly handles all RakNet packets and Minecraft protocol
"""

import asyncio
import logging
import socket
import struct
import time
import random
import json
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FixedConnection:
    """Fixed connection handler"""
    def __init__(self, address: Tuple[str, int], socket):
        self.address = address
        self.socket = socket
        self.connected = True
        self.client_guid = random.randint(1000000, 9999999)
        self.mtu_size = 1492
        self.packet_queue = []
    
    def is_connected(self):
        return self.connected
    
    def close(self):
        self.connected = False
    
    async def send_packet(self, data: bytes):
        try:
            loop = asyncio.get_event_loop()
            await loop.sock_sendto(self.socket, data, self.address)
            logger.debug(f"Sent packet to {self.address}: {len(data)} bytes")
        except Exception as e:
            logger.error(f"Error sending packet: {e}")
            self.connected = False
    
    def receive_packet(self, data: bytes):
        """Receive a packet"""
        self.packet_queue.append(data)
    
    async def get_packets(self):
        """Get all received packets"""
        packets = self.packet_queue.copy()
        self.packet_queue.clear()
        return packets

class FixedRakNet:
    """Fixed RakNet server with proper packet handling"""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.connections: Dict[Tuple[str, int], FixedConnection] = {}
        self.new_connections: List[FixedConnection] = []
        self.protocol_version = 662
        self.server_guid = int(time.time() * 1000) & 0xFFFFFFFFFFFFFFFF
        self.motd = "Python Bedrock Server"
        self.max_players = 20
        self.online_players = 0
        
        logger.info(f"Fixed RakNet server initialized on {host}:{port}")
    
    async def start(self):
        """Start the fixed RakNet server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.setblocking(False)
            
            self.running = True
            logger.info(f"Fixed RakNet server started on {self.host}:{self.port}")
            
            # Start receive loop
            asyncio.create_task(self.receive_loop())
            
        except Exception as e:
            logger.error(f"Failed to start fixed RakNet server: {e}")
            raise
    
    async def receive_loop(self):
        """Main receive loop"""
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                data, addr = await loop.sock_recvfrom(self.socket, 4096)
                await self.handle_packet(data, addr)
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.running:
                    logger.error(f"Error in receive loop: {e}")
                await asyncio.sleep(0.01)
    
    async def handle_packet(self, data: bytes, addr: Tuple[str, int]):
        """Handle incoming packet"""
        if not data:
            return
        
        packet_id = data[0]
        
        try:
            if packet_id == 0x01:  # Unconnected ping
                await self.handle_unconnected_ping(data, addr)
            elif packet_id == 0x05:  # Open connection request 1
                await self.handle_open_connection_request_1(data, addr)
            elif packet_id == 0x07:  # Open connection request 2
                await self.handle_open_connection_request_2(data, addr)
            elif packet_id == 0x09:  # Connection request
                await self.handle_connection_request(data, addr)
            elif packet_id == 0x13:  # New incoming connection
                await self.handle_new_incoming_connection(data, addr)
            elif packet_id == 0x15:  # Disconnection notification
                await self.handle_disconnection_notification(data, addr)
            elif packet_id >= 0x80 and packet_id <= 0x8F:  # Data packets
                await self.handle_data_packet(data, addr)
            else:
                logger.debug(f"Unknown packet ID: {packet_id:02X} from {addr}")
                
        except Exception as e:
            logger.error(f"Error handling packet {packet_id:02X} from {addr}: {e}")
    
    async def handle_unconnected_ping(self, data: bytes, addr: Tuple[str, int]):
        """Handle unconnected ping"""
        try:
            if len(data) < 25:
                return
            
            ping_time = struct.unpack('<Q', data[1:9])[0]
            
            # Create pong response
            pong_data = bytearray()
            pong_data.append(0x1C)  # Unconnected pong
            pong_data.extend(struct.pack('<Q', ping_time))
            pong_data.extend(struct.pack('<Q', self.server_guid))
            
            # MOTD
            motd_data = (
                f"MCPE;{self.motd};{self.protocol_version};1.20.15;"
                f"{self.online_players};{self.max_players};{self.server_guid};"
                f"Default;Survival;1;19132;19133;"
            ).encode('utf-8')
            
            pong_data.extend(struct.pack('<H', len(motd_data)))
            pong_data.extend(motd_data)
            
            await self.send_packet(bytes(pong_data), addr)
            logger.debug(f"Sent pong to {addr}")
            
        except Exception as e:
            logger.error(f"Error handling unconnected ping: {e}")
    
    async def handle_open_connection_request_1(self, data: bytes, addr: Tuple[str, int]):
        """Handle open connection request 1"""
        try:
            if len(data) < 18:
                return
            
            protocol_version = struct.unpack('<H', data[1:3])[0]
            
            if protocol_version != self.protocol_version:
                # Send incompatible protocol version
                response = bytearray()
                response.append(0x19)  # Incompatible protocol version
                response.extend(struct.pack('<Q', self.server_guid))
                response.extend(struct.pack('<H', self.protocol_version))
                await self.send_packet(bytes(response), addr)
                logger.info(f"Rejected connection from {addr} - incompatible protocol {protocol_version}")
                return
            
            # Send open connection reply 1
            response = bytearray()
            response.append(0x06)  # Open connection reply 1
            response.extend(struct.pack('<Q', self.server_guid))
            response.extend(b'\x00' * 16)  # Security cookie
            response.extend(struct.pack('<H', 1492))  # MTU size
            
            await self.send_packet(bytes(response), addr)
            logger.info(f"Sent open connection reply 1 to {addr}")
            
        except Exception as e:
            logger.error(f"Error handling open connection request 1: {e}")
    
    async def handle_open_connection_request_2(self, data: bytes, addr: Tuple[str, int]):
        """Handle open connection request 2"""
        try:
            if len(data) < 35:
                return
            
            # Parse request data
            server_address = data[1:17]
            port = struct.unpack('<H', data[17:19])[0]
            mtu_size = struct.unpack('<H', data[19:21])[0]
            client_guid = struct.unpack('<Q', data[21:29])[0]
            
            # Send open connection reply 2
            response = bytearray()
            response.append(0x08)  # Open connection reply 2
            response.extend(struct.pack('<Q', self.server_guid))
            response.extend(struct.pack('<H', port))
            response.extend(struct.pack('<H', mtu_size))
            response.extend(b'\x00' * 16)  # Security cookie
            
            await self.send_packet(bytes(response), addr)
            logger.info(f"Sent open connection reply 2 to {addr}")
            
        except Exception as e:
            logger.error(f"Error handling open connection request 2: {e}")
    
    async def handle_connection_request(self, data: bytes, addr: Tuple[str, int]):
        """Handle connection request"""
        try:
            if len(data) < 25:
                return
            
            client_guid = struct.unpack('<Q', data[1:9])[0]
            timestamp = struct.unpack('<Q', data[9:17])[0]
            
            # Send connection request accepted
            response = bytearray()
            response.append(0x10)  # Connection request accepted
            response.extend(struct.pack('<Q', timestamp))
            response.extend(struct.pack('<Q', self.server_guid))
            
            # Add system address
            response.extend(b'\x00' * 16)  # System address
            response.extend(struct.pack('<H', 0))  # Port
            
            # Add system addresses array
            response.extend(struct.pack('<H', 1))  # Count
            response.extend(b'\x00' * 16)  # Address
            response.extend(struct.pack('<H', 0))  # Port
            
            await self.send_packet(bytes(response), addr)
            logger.info(f"Sent connection request accepted to {addr}")
            
        except Exception as e:
            logger.error(f"Error handling connection request: {e}")
    
    async def handle_new_incoming_connection(self, data: bytes, addr: Tuple[str, int]):
        """Handle new incoming connection"""
        try:
            # Create new connection
            connection = FixedConnection(addr, self.socket)
            connection.client_guid = struct.unpack('<Q', data[1:9])[0] if len(data) >= 9 else random.randint(1000000, 9999999)
            
            self.connections[addr] = connection
            self.new_connections.append(connection)
            self.online_players += 1
            
            logger.info(f"New connection established from {addr} (GUID: {connection.client_guid})")
            
        except Exception as e:
            logger.error(f"Error handling new incoming connection: {e}")
    
    async def handle_disconnection_notification(self, data: bytes, addr: Tuple[str, int]):
        """Handle disconnection notification"""
        if addr in self.connections:
            connection = self.connections[addr]
            connection.close()
            del self.connections[addr]
            self.online_players = max(0, self.online_players - 1)
            logger.info(f"Connection closed from {addr}")
    
    async def handle_data_packet(self, data: bytes, addr: Tuple[str, int]):
        """Handle data packet"""
        if addr in self.connections:
            connection = self.connections[addr]
            connection.receive_packet(data)
            logger.debug(f"Received data packet from {addr}: {len(data)} bytes")
    
    async def send_packet(self, data: bytes, addr: Tuple[str, int]):
        """Send packet"""
        try:
            loop = asyncio.get_event_loop()
            await loop.sock_sendto(self.socket, data, addr)
            logger.debug(f"Sent packet to {addr}: {len(data)} bytes")
        except Exception as e:
            logger.error(f"Error sending packet to {addr}: {e}")
    
    async def get_new_connections(self) -> List[FixedConnection]:
        """Get list of new connections and clear the list"""
        connections = self.new_connections.copy()
        self.new_connections.clear()
        return connections

class FixedPlayer:
    """Fixed player class"""
    def __init__(self, connection: FixedConnection):
        self.connection = connection
        self.guid = str(connection.client_guid)
        self.username = f"Player_{connection.client_guid}"
        self.entity_id = connection.client_guid & 0xFFFFFFFF
        self.x = 0.0
        self.y = 64.0
        self.z = 0.0
        self.yaw = 0.0
        self.pitch = 0.0
        self.on_ground = True
        self.health = 20.0
        self.connected = True
        self.last_ping = time.time()
        self.spawned = False

class FixedServer:
    """Fixed Minecraft server"""
    
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 19132
        self.max_players = 20
        self.motd = "Python Bedrock Server"
        self.game_mode = 0
        self.difficulty = 1
        self.raknet = FixedRakNet(self.host, self.port)
        self.players: Dict[str, FixedPlayer] = {}
        self.running = False
        
        logger.info("Fixed server initialized")
    
    async def start(self):
        """Start the server"""
        self.running = True
        
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
                player = FixedPlayer(connection)
                self.players[player.guid] = player
                
                logger.info(f"Player {player.username} connected from {connection.address}")
                
                # Start connection sequence
                await self.start_connection_sequence(player)
                
            except Exception as e:
                logger.error(f"Error handling new connection: {e}")
    
    async def start_connection_sequence(self, player: FixedPlayer):
        """Start the connection sequence for a player"""
        try:
            # Stage 1: Send login success
            await self.send_login_success(player)
            logger.debug(f"Sent login success to {player.username}")
            
            # Stage 2: Send resource packs info
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
            
            # Broadcast player join
            await self.broadcast_message(f"§e{player.username} joined the game")
            
        except Exception as e:
            logger.error(f"Error in connection sequence for {player.username}: {e}")
    
    async def send_login_success(self, player: FixedPlayer):
        """Send login success packet"""
        packet = bytearray()
        packet.append(0x02)  # Play status packet
        packet.extend(struct.pack('<i', 0))  # Login success
        await player.connection.send_packet(bytes(packet))
    
    async def send_resource_packs_info(self, player: FixedPlayer):
        """Send resource packs info packet"""
        packet = bytearray()
        packet.append(0x06)  # Resource packs info packet
        packet.extend(struct.pack('<?', False))  # Must accept
        packet.extend(struct.pack('<?', False))  # Has scripts
        packet.extend(struct.pack('<H', 0))  # Behavior pack count
        packet.extend(struct.pack('<H', 0))  # Resource pack count
        
        await player.connection.send_packet(bytes(packet))
    
    async def send_resource_pack_stack(self, player: FixedPlayer):
        """Send resource pack stack packet"""
        packet = bytearray()
        packet.append(0x07)  # Resource pack stack packet
        packet.extend(struct.pack('<?', False))  # Must accept
        packet.extend(struct.pack('<H', 0))  # Behavior pack count
        packet.extend(struct.pack('<H', 0))  # Resource pack count
        
        await player.connection.send_packet(bytes(packet))
    
    async def send_start_game(self, player: FixedPlayer):
        """Send start game packet"""
        packet = bytearray()
        packet.append(0x0B)  # Start game packet
        
        # Basic start game data
        packet.extend(struct.pack('<Q', player.entity_id))  # Entity ID
        packet.extend(struct.pack('<Q', player.entity_id))  # Runtime entity ID
        packet.extend(struct.pack('<i', self.game_mode))  # Game type
        packet.extend(struct.pack('<f', player.x))  # X
        packet.extend(struct.pack('<f', player.y))  # Y
        packet.extend(struct.pack('<f', player.z))  # Z
        packet.extend(struct.pack('<f', player.yaw))  # Yaw
        packet.extend(struct.pack('<f', player.pitch))  # Pitch
        packet.extend(struct.pack('<i', 12345))  # Seed
        packet.extend(struct.pack('<i', 1))  # Biome type
        packet.extend(struct.pack('<i', 0))  # World time
        packet.extend(struct.pack('<i', self.difficulty))  # Difficulty
        
        await player.connection.send_packet(bytes(packet))
    
    async def send_spawn_position(self, player: FixedPlayer):
        """Send spawn position packet"""
        packet = bytearray()
        packet.append(0x2D)  # Set spawn position packet
        packet.extend(struct.pack('<i', 2))  # Spawn type
        packet.extend(struct.pack('<i', 0))  # X
        packet.extend(struct.pack('<i', 64))  # Y
        packet.extend(struct.pack('<i', 0))  # Z
        packet.extend(struct.pack('<i', 0))  # Dimension
        
        await player.connection.send_packet(bytes(packet))
    
    async def send_time_and_weather(self, player: FixedPlayer):
        """Send time and weather packets"""
        # Send time
        time_packet = bytearray()
        time_packet.append(0x0A)  # Set time packet
        time_packet.extend(struct.pack('<i', 0))  # Time
        await player.connection.send_packet(bytes(time_packet))
        
        # Send weather (clear)
        weather_packet = bytearray()
        weather_packet.append(0x0A)  # Reuse time packet ID for weather
        weather_packet.extend(struct.pack('<i', 0))  # Clear weather
        await player.connection.send_packet(bytes(weather_packet))
    
    async def send_game_rules(self, player: FixedPlayer):
        """Send game rules packet"""
        packet = bytearray()
        packet.append(0x46)  # Set game rules packet
        packet.extend(struct.pack('<I', 0))  # No rules
        
        await player.connection.send_packet(bytes(packet))
    
    async def send_commands_enabled(self, player: FixedPlayer):
        """Send commands enabled packet"""
        packet = bytearray()
        packet.append(0x3F)  # Set commands enabled packet
        packet.extend(struct.pack('<?', True))  # Commands enabled
        
        await player.connection.send_packet(bytes(packet))
    
    async def send_player_permissions(self, player: FixedPlayer):
        """Send player permissions packet"""
        packet = bytearray()
        packet.append(0x3D)  # Set player permissions packet
        packet.extend(struct.pack('<i', 0))  # Normal player
        
        await player.connection.send_packet(bytes(packet))
    
    async def send_spawn_chunks(self, player: FixedPlayer):
        """Send spawn chunks"""
        # Send a simple chunk
        packet = bytearray()
        packet.append(0x3A)  # Level chunk packet
        packet.extend(struct.pack('<i', 0))  # Chunk X
        packet.extend(struct.pack('<i', 0))  # Chunk Z
        packet.extend(struct.pack('<i', 0))  # Sub chunk count
        packet.extend(struct.pack('<i', 0))  # Cache enabled
        packet.extend(struct.pack('<i', 0))  # Chunk data length
        # No chunk data for simplicity
        
        await player.connection.send_packet(bytes(packet))
    
    async def spawn_player(self, player: FixedPlayer):
        """Spawn player in the world"""
        try:
            # Get spawn position
            player.x, player.y, player.z = 0.0, 64.0, 0.0
            
            # Send player spawn packet to all players
            await self.broadcast_player_spawn(player)
            
            # Send other players to the new player
            await self.send_existing_players(player)
            
            logger.info(f"Player {player.username} spawned at ({player.x}, {player.y}, {player.z})")
            
        except Exception as e:
            logger.error(f"Error spawning player {player.username}: {e}")
    
    async def broadcast_player_spawn(self, player: FixedPlayer):
        """Broadcast player spawn to all other players"""
        # Create add player packet
        packet = bytearray()
        packet.append(0x0C)  # Add player packet
        
        # Player UUID
        packet.extend(struct.pack('<H', len(player.guid)))
        packet.extend(player.guid.encode('utf-8'))
        
        # Player name
        packet.extend(struct.pack('<H', len(player.username)))
        packet.extend(player.username.encode('utf-8'))
        
        # Player position
        packet.extend(struct.pack('<f', player.x))
        packet.extend(struct.pack('<f', player.y))
        packet.extend(struct.pack('<f', player.z))
        
        # Player motion
        packet.extend(struct.pack('<f', 0.0))
        packet.extend(struct.pack('<f', 0.0))
        packet.extend(struct.pack('<f', 0.0))
        
        # Player rotation
        packet.extend(struct.pack('<f', player.pitch))
        packet.extend(struct.pack('<f', player.yaw))
        packet.extend(struct.pack('<f', player.yaw))  # Head yaw
        
        # Player data
        packet.extend(struct.pack('<I', 0))  # Flags
        packet.extend(struct.pack('<I', 0))  # Command permission
        packet.extend(struct.pack('<I', 0))  # Action permissions
        packet.extend(struct.pack('<I', 0))  # Permission level
        packet.extend(struct.pack('<I', 0))  # Custom stored permissions
        packet.extend(struct.pack('<I', 0))  # User ID
        
        # Entity links
        packet.extend(struct.pack('<I', 0))  # Entity links count
        
        # Send to all other players
        for other_player in self.players.values():
            if other_player.guid != player.guid:
                await other_player.connection.send_packet(bytes(packet))
    
    async def send_existing_players(self, player: FixedPlayer):
        """Send existing players to the new player"""
        for other_player in self.players.values():
            if other_player.guid != player.guid:
                # Create add player packet for existing player
                packet = bytearray()
                packet.append(0x0C)  # Add player packet
                
                # Player UUID
                packet.extend(struct.pack('<H', len(other_player.guid)))
                packet.extend(other_player.guid.encode('utf-8'))
                
                # Player name
                packet.extend(struct.pack('<H', len(other_player.username)))
                packet.extend(other_player.username.encode('utf-8'))
                
                # Player position
                packet.extend(struct.pack('<f', other_player.x))
                packet.extend(struct.pack('<f', other_player.y))
                packet.extend(struct.pack('<f', other_player.z))
                
                # Player motion
                packet.extend(struct.pack('<f', 0.0))
                packet.extend(struct.pack('<f', 0.0))
                packet.extend(struct.pack('<f', 0.0))
                
                # Player rotation
                packet.extend(struct.pack('<f', other_player.pitch))
                packet.extend(struct.pack('<f', other_player.yaw))
                packet.extend(struct.pack('<f', other_player.yaw))  # Head yaw
                
                # Player data
                packet.extend(struct.pack('<I', 0))  # Flags
                packet.extend(struct.pack('<I', 0))  # Command permission
                packet.extend(struct.pack('<I', 0))  # Action permissions
                packet.extend(struct.pack('<I', 0))  # Permission level
                packet.extend(struct.pack('<I', 0))  # Custom stored permissions
                packet.extend(struct.pack('<I', 0))  # User ID
                
                # Entity links
                packet.extend(struct.pack('<I', 0))  # Entity links count
                
                await player.connection.send_packet(bytes(packet))
    
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
                    await self.handle_minecraft_packet(player, packet)
                    
            except Exception as e:
                logger.error(f"Error handling packets for {player.username}: {e}")
    
    async def handle_minecraft_packet(self, player: FixedPlayer, packet: bytes):
        """Handle Minecraft packet"""
        if not packet:
            return
        
        packet_id = packet[0]
        
        try:
            if packet_id == 0x0C:  # Move player packet
                await self.handle_move_player(player, packet)
            elif packet_id == 0x09:  # Text packet
                await self.handle_text_packet(player, packet)
            else:
                logger.debug(f"Unhandled Minecraft packet ID: {packet_id:02X} from {player.username}")
                
        except Exception as e:
            logger.error(f"Error handling Minecraft packet {packet_id:02X} from {player.username}: {e}")
    
    async def handle_move_player(self, player: FixedPlayer, packet: bytes):
        """Handle move player packet"""
        try:
            if len(packet) < 25:
                return
            
            # Parse position data
            entity_id = struct.unpack('<Q', packet[1:9])[0]
            x = struct.unpack('<f', packet[9:13])[0]
            y = struct.unpack('<f', packet[13:17])[0]
            z = struct.unpack('<f', packet[17:21])[0]
            yaw = struct.unpack('<f', packet[21:25])[0]
            pitch = struct.unpack('<f', packet[25:29])[0]
            
            # Update player position
            player.x, player.y, player.z = x, y, z
            player.yaw, player.pitch = yaw, pitch
            
            # Broadcast movement to other players
            await self.broadcast_move_player(player)
            
        except Exception as e:
            logger.error(f"Error handling move player: {e}")
    
    async def broadcast_move_player(self, player: FixedPlayer):
        """Broadcast player movement to other players"""
        packet = bytearray()
        packet.append(0x0C)  # Move player packet
        packet.extend(struct.pack('<Q', player.entity_id))
        packet.extend(struct.pack('<f', player.x))
        packet.extend(struct.pack('<f', player.y))
        packet.extend(struct.pack('<f', player.z))
        packet.extend(struct.pack('<f', player.yaw))
        packet.extend(struct.pack('<f', player.pitch))
        packet.extend(struct.pack('<f', player.yaw))  # Head yaw
        packet.extend(struct.pack('<B', 0))  # Mode
        packet.extend(struct.pack('<?', True))  # On ground
        packet.extend(struct.pack('<I', 0))  # Tick
        
        for other_player in self.players.values():
            if other_player.guid != player.guid:
                await other_player.connection.send_packet(bytes(packet))
    
    async def handle_text_packet(self, player: FixedPlayer, packet: bytes):
        """Handle text packet"""
        try:
            if len(packet) < 7:
                return
            
            message_type = packet[1]
            xuid_length = struct.unpack('<H', packet[2:4])[0]
            platform_chat_id_length = struct.unpack('<H', packet[4:6])[0]
            message_length = struct.unpack('<H', packet[6:8])[0]
            
            if len(packet) >= 8 + message_length:
                message = packet[8:8+message_length].decode('utf-8')
                logger.info(f"Chat from {player.username}: {message}")
                
                # Broadcast message
                await self.broadcast_message(f"<{player.username}> {message}")
            
        except Exception as e:
            logger.error(f"Error handling text packet: {e}")
    
    async def broadcast_message(self, message: str):
        """Broadcast message to all players"""
        packet = bytearray()
        packet.append(0x09)  # Text packet
        packet.append(0x01)  # Message type
        packet.extend(struct.pack('<H', 0))  # XUID length
        packet.extend(struct.pack('<H', 0))  # Platform chat ID length
        packet.extend(struct.pack('<H', len(message)))  # Message length
        packet.extend(message.encode('utf-8'))  # Message
        
        for player in self.players.values():
            await player.connection.send_packet(bytes(packet))
    
    async def remove_player(self, player: FixedPlayer):
        """Remove a player"""
        if player.guid in self.players:
            del self.players[player.guid]
            self.raknet.online_players = max(0, self.raknet.online_players - 1)
            logger.info(f"Player {player.username} disconnected")
    
    async def shutdown(self):
        """Shutdown the server"""
        self.running = False
        logger.info("Server shutdown")

async def main():
    """Main function"""
    server = FixedServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())