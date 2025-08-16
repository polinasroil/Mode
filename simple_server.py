#!/usr/bin/env python3
"""
Simplified Minecraft Bedrock Server for testing
Fixed version with proper packet handling
"""

import asyncio
import logging
import socket
import struct
import time
import random
from typing import Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleConnection:
    """Simple connection handler"""
    def __init__(self, address: Tuple[str, int], socket):
        self.address = address
        self.socket = socket
        self.connected = True
        self.client_guid = random.randint(1000000, 9999999)
        self.mtu_size = 1492
    
    def is_connected(self):
        return self.connected
    
    def close(self):
        self.connected = False
    
    async def send_packet(self, data: bytes):
        try:
            loop = asyncio.get_event_loop()
            await loop.sock_sendto(self.socket, data, self.address)
        except Exception as e:
            logger.error(f"Error sending packet: {e}")
            self.connected = False

class SimpleRakNet:
    """Simplified RakNet server with fixed packet handling"""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.connections: Dict[Tuple[str, int], SimpleConnection] = {}
        self.new_connections: List[SimpleConnection] = []
        self.protocol_version = 662
        self.server_guid = int(time.time() * 1000) & 0xFFFFFFFFFFFFFFFF
        self.motd = "Python Bedrock Server"
        self.max_players = 20
        self.online_players = 0
        
        logger.info(f"Simple RakNet server initialized on {host}:{port}")
    
    async def start(self):
        """Start the simplified RakNet server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.setblocking(False)
            
            self.running = True
            logger.info(f"Simple RakNet server started on {self.host}:{self.port}")
            
            # Start receive loop
            asyncio.create_task(self.receive_loop())
            
        except Exception as e:
            logger.error(f"Failed to start simple RakNet server: {e}")
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
                response.extend(struct.pack('<H', self.protocol_version))  # Fixed: use H instead of B
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
            logger.debug(f"Sent open connection reply 1 to {addr}")
            
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
            connection = SimpleConnection(addr, self.socket)
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
            # Process Minecraft packets here
            logger.debug(f"Received data packet from {addr}: {len(data)} bytes")
    
    async def send_packet(self, data: bytes, addr: Tuple[str, int]):
        """Send packet"""
        try:
            loop = asyncio.get_event_loop()
            await loop.sock_sendto(self.socket, data, addr)
            logger.debug(f"Sent packet to {addr}: {len(data)} bytes")
        except Exception as e:
            logger.error(f"Error sending packet to {addr}: {e}")
    
    async def get_new_connections(self) -> List[SimpleConnection]:
        """Get list of new connections and clear the list"""
        connections = self.new_connections.copy()
        self.new_connections.clear()
        return connections

class SimplePlayer:
    """Simple player class"""
    def __init__(self, connection: SimpleConnection):
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

class SimpleServer:
    """Simple Minecraft server"""
    
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 19132
        self.max_players = 20
        self.motd = "Python Bedrock Server"
        self.game_mode = 0
        self.difficulty = 1
        self.raknet = SimpleRakNet(self.host, self.port)
        self.players: Dict[str, SimplePlayer] = {}
        self.running = False
        
        logger.info("Simple server initialized")
    
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
                player = SimplePlayer(connection)
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
                    
            except Exception as e:
                logger.error(f"Error handling packets for {player.username}: {e}")
    
    async def send_login_success(self, player: SimplePlayer):
        """Send login success packet"""
        packet = bytearray()
        packet.append(0x02)  # Play status packet
        packet.extend(struct.pack('<i', 0))  # Login success
        await player.connection.send_packet(bytes(packet))
    
    async def send_start_game(self, player: SimplePlayer):
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
    
    async def send_spawn_chunks(self, player: SimplePlayer):
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
    
    async def remove_player(self, player: SimplePlayer):
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
    server = SimpleServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())