"""
Simplified RakNet implementation for Minecraft Bedrock Server
Handles basic UDP networking, ping responses, and connections
"""

import asyncio
import logging
import socket
import struct
import time
from typing import Dict, List, Optional, Tuple

from .connection import Connection

logger = logging.getLogger(__name__)

class RakNetServer:
    """Simplified RakNet server for Minecraft Bedrock"""
    
    # RakNet packet IDs
    ID_UNCONNECTED_PING = 0x01
    ID_UNCONNECTED_PONG = 0x1C
    ID_OPEN_CONNECTION_REQUEST_1 = 0x05
    ID_OPEN_CONNECTION_REPLY_1 = 0x06
    ID_OPEN_CONNECTION_REQUEST_2 = 0x07
    ID_OPEN_CONNECTION_REPLY_2 = 0x08
    ID_CONNECTION_REQUEST = 0x09
    ID_CONNECTION_REQUEST_ACCEPTED = 0x10
    ID_NEW_INCOMING_CONNECTION = 0x13
    ID_DISCONNECTION_NOTIFICATION = 0x15
    ID_INCOMPATIBLE_PROTOCOL_VERSION = 0x19
    ID_ACK = 0xC0
    ID_NAK = 0xA0
    ID_DATA_PACKET_0 = 0x80
    ID_DATA_PACKET_1 = 0x81
    ID_DATA_PACKET_2 = 0x82
    ID_DATA_PACKET_3 = 0x83
    ID_DATA_PACKET_4 = 0x84
    ID_DATA_PACKET_5 = 0x85
    ID_DATA_PACKET_6 = 0x86
    ID_DATA_PACKET_7 = 0x87
    ID_DATA_PACKET_8 = 0x88
    ID_DATA_PACKET_9 = 0x89
    ID_DATA_PACKET_A = 0x8A
    ID_DATA_PACKET_B = 0x8B
    ID_DATA_PACKET_C = 0x8C
    ID_DATA_PACKET_D = 0x8D
    ID_DATA_PACKET_E = 0x8E
    ID_DATA_PACKET_F = 0x8F
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.connections: Dict[Tuple[str, int], Connection] = {}
        self.new_connections: List[Connection] = []
        self.protocol_version = 662  # Minecraft Bedrock 1.20.15
        self.server_guid = int(time.time() * 1000) & 0xFFFFFFFFFFFFFFFF
        self.motd = "Python Bedrock Server"
        self.max_players = 20
        self.online_players = 0
        
        logger.info(f"RakNet server initialized on {host}:{port}")
    
    async def start(self):
        """Start the RakNet server"""
        try:
            # Create UDP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.setblocking(False)
            
            self.running = True
            logger.info(f"RakNet server started on {self.host}:{self.port}")
            
            # Start receive loop
            asyncio.create_task(self.receive_loop())
            
        except Exception as e:
            logger.error(f"Failed to start RakNet server: {e}")
            raise
    
    async def stop(self):
        """Stop the RakNet server"""
        self.running = False
        
        # Close all connections
        for connection in list(self.connections.values()):
            connection.close()
        
        # Close socket
        if self.socket:
            self.socket.close()
        
        logger.info("RakNet server stopped")
    
    async def receive_loop(self):
        """Main receive loop for handling incoming packets"""
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Use asyncio to handle non-blocking socket
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
            if packet_id == self.ID_UNCONNECTED_PING:
                await self.handle_unconnected_ping(data, addr)
            elif packet_id == self.ID_OPEN_CONNECTION_REQUEST_1:
                await self.handle_open_connection_request_1(data, addr)
            elif packet_id == self.ID_OPEN_CONNECTION_REQUEST_2:
                await self.handle_open_connection_request_2(data, addr)
                logger.info(f"Handled open connection request 2 from {addr}")
            elif packet_id == self.ID_CONNECTION_REQUEST:
                await self.handle_connection_request(data, addr)
            elif packet_id == self.ID_NEW_INCOMING_CONNECTION:
                await self.handle_new_incoming_connection(data, addr)
            elif packet_id == self.ID_DISCONNECTION_NOTIFICATION:
                await self.handle_disconnection_notification(data, addr)
            elif packet_id >= self.ID_DATA_PACKET_0 and packet_id <= self.ID_DATA_PACKET_F:
                await self.handle_data_packet(data, addr)
            elif packet_id == self.ID_ACK:
                await self.handle_ack(data, addr)
            elif packet_id == self.ID_NAK:
                await self.handle_nak(data, addr)
            else:
                logger.debug(f"Unknown packet ID: {packet_id:02X} from {addr}")
                
        except Exception as e:
            logger.error(f"Error handling packet {packet_id:02X} from {addr}: {e}")
    
    async def handle_unconnected_ping(self, data: bytes, addr: Tuple[str, int]):
        """Handle unconnected ping (server list ping)"""
        try:
            # Parse ping data
            if len(data) < 25:
                return
            
            ping_time = struct.unpack('<Q', data[1:9])[0]
            
            # Create pong response
            pong_data = bytearray()
            pong_data.append(self.ID_UNCONNECTED_PONG)
            pong_data.extend(struct.pack('<Q', ping_time))
            pong_data.extend(struct.pack('<Q', self.server_guid))
            
            # Add MOTD
            motd_data = f"MCPE;{self.motd};{self.protocol_version};1.20.15;{self.online_players};{self.max_players};{self.server_guid};Default;Survival;1;19132;19133;".encode('utf-8')
            pong_data.extend(struct.pack('<H', len(motd_data)))
            pong_data.extend(motd_data)
            
            # Send pong
            await self.send_packet(bytes(pong_data), addr)
            logger.debug(f"Sent pong to {addr}")
            
        except Exception as e:
            logger.error(f"Error handling unconnected ping: {e}")
    
    async def handle_open_connection_request_1(self, data: bytes, addr: Tuple[str, int]):
        """Handle open connection request 1"""
        try:
            # Check protocol version
            if len(data) < 18:
                return
            
            protocol_version = struct.unpack('<H', data[1:3])[0]
            
            if protocol_version != self.protocol_version:
                # Send incompatible protocol version
                response = bytearray()
                response.append(self.ID_INCOMPATIBLE_PROTOCOL_VERSION)
                response.extend(struct.pack('<Q', self.server_guid))
                response.extend(struct.pack('<B', self.protocol_version))
                await self.send_packet(bytes(response), addr)
                return
            
            # Send open connection reply 1
            response = bytearray()
            response.append(self.ID_OPEN_CONNECTION_REPLY_1)
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
            response.append(self.ID_OPEN_CONNECTION_REPLY_2)
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
            response.append(self.ID_CONNECTION_REQUEST_ACCEPTED)
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
            logger.debug(f"Sent connection request accepted to {addr}")
            
        except Exception as e:
            logger.error(f"Error handling connection request: {e}")
    
    async def handle_new_incoming_connection(self, data: bytes, addr: Tuple[str, int]):
        """Handle new incoming connection"""
        try:
            # Create new connection
            connection = Connection(addr, self.socket)
            self.connections[addr] = connection
            self.new_connections.append(connection)
            self.online_players += 1
            
            logger.info(f"New connection from {addr}")
            
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
    
    async def handle_ack(self, data: bytes, addr: Tuple[str, int]):
        """Handle ACK packet"""
        if addr in self.connections:
            connection = self.connections[addr]
            connection.handle_ack(data)
    
    async def handle_nak(self, data: bytes, addr: Tuple[str, int]):
        """Handle NAK packet"""
        if addr in self.connections:
            connection = self.connections[addr]
            connection.handle_nak(data)
    
    async def send_packet(self, data: bytes, addr: Tuple[str, int]):
        """Send packet to address"""
        try:
            loop = asyncio.get_event_loop()
            await loop.sock_sendto(self.socket, data, addr)
            logger.info(f"Sent packet to {addr}: {len(data)} bytes")
        except Exception as e:
            logger.error(f"Error sending packet to {addr}: {e}")
    
    async def get_new_connections(self) -> List[Connection]:
        """Get list of new connections and clear the list"""
        connections = self.new_connections.copy()
        self.new_connections.clear()
        return connections
    
    def get_connection_count(self) -> int:
        """Get number of active connections"""
        return len(self.connections)
    
    def get_online_players(self) -> int:
        """Get number of online players"""
        return self.online_players