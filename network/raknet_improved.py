"""
Improved RakNet implementation for Minecraft Bedrock Server
Full protocol support with proper packet handling
"""

import asyncio
import logging
import socket
import struct
import time
import random
from typing import Dict, List, Optional, Tuple, Set

from .connection import Connection

logger = logging.getLogger(__name__)

class RakNetImproved:
    """Improved RakNet server with full protocol support"""
    
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
    
    # Reliability types
    RELIABILITY_UNRELIABLE = 0
    RELIABILITY_UNRELIABLE_SEQUENCED = 1
    RELIABILITY_RELIABLE = 2
    RELIABILITY_RELIABLE_ORDERED = 3
    RELIABILITY_RELIABLE_SEQUENCED = 4
    RELIABILITY_UNRELIABLE_WITH_ACK_RECEIPT = 5
    RELIABILITY_RELIABLE_WITH_ACK_RECEIPT = 6
    RELIABILITY_RELIABLE_ORDERED_WITH_ACK_RECEIPT = 7
    
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
        
        # Connection tracking
        self.pending_connections: Dict[Tuple[str, int], Dict] = {}
        self.connection_timeouts: Dict[Tuple[str, int], float] = {}
        
        # Statistics
        self.packets_sent = 0
        self.packets_received = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        
        logger.info(f"Improved RakNet server initialized on {host}:{port}")
    
    async def start(self):
        """Start the improved RakNet server"""
        try:
            # Create UDP socket with proper options
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.socket.bind((self.host, self.port))
            self.socket.setblocking(False)
            
            self.running = True
            logger.info(f"Improved RakNet server started on {self.host}:{self.port}")
            
            # Start receive loop and maintenance tasks
            asyncio.create_task(self.receive_loop())
            asyncio.create_task(self.maintenance_loop())
            
        except Exception as e:
            logger.error(f"Failed to start improved RakNet server: {e}")
            raise
    
    async def stop(self):
        """Stop the improved RakNet server"""
        self.running = False
        
        # Close all connections
        for connection in list(self.connections.values()):
            connection.close()
        
        # Close socket
        if self.socket:
            self.socket.close()
        
        logger.info("Improved RakNet server stopped")
    
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
    
    async def maintenance_loop(self):
        """Maintenance loop for connection cleanup and statistics"""
        while self.running:
            try:
                # Clean up timed out connections
                current_time = time.time()
                timed_out = []
                
                for addr, timeout_time in self.connection_timeouts.items():
                    if current_time > timeout_time:
                        timed_out.append(addr)
                
                for addr in timed_out:
                    if addr in self.connections:
                        connection = self.connections[addr]
                        connection.close()
                        del self.connections[addr]
                        self.online_players = max(0, self.online_players - 1)
                        logger.info(f"Connection timed out: {addr}")
                    del self.connection_timeouts[addr]
                
                # Clean up pending connections
                for addr, data in list(self.pending_connections.items()):
                    if current_time > data.get('timeout', 0):
                        del self.pending_connections[addr]
                        logger.debug(f"Cleaned up pending connection: {addr}")
                
                await asyncio.sleep(1.0)  # Run every second
                
            except Exception as e:
                logger.error(f"Error in maintenance loop: {e}")
                await asyncio.sleep(1.0)
    
    async def handle_packet(self, data: bytes, addr: Tuple[str, int]):
        """Handle incoming packet with improved error handling"""
        if not data:
            return
        
        self.packets_received += 1
        self.bytes_received += len(data)
        
        packet_id = data[0]
        
        try:
            if packet_id == self.ID_UNCONNECTED_PING:
                await self.handle_unconnected_ping(data, addr)
            elif packet_id == self.ID_OPEN_CONNECTION_REQUEST_1:
                await self.handle_open_connection_request_1(data, addr)
            elif packet_id == self.ID_OPEN_CONNECTION_REQUEST_2:
                await self.handle_open_connection_request_2(data, addr)
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
        """Handle unconnected ping with improved MOTD"""
        try:
            if len(data) < 25:
                return
            
            ping_time = struct.unpack('<Q', data[1:9])[0]
            
            # Create improved pong response
            pong_data = bytearray()
            pong_data.append(self.ID_UNCONNECTED_PONG)
            pong_data.extend(struct.pack('<Q', ping_time))
            pong_data.extend(struct.pack('<Q', self.server_guid))
            
            # Enhanced MOTD with more information
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
        """Handle open connection request 1 with improved validation"""
        try:
            if len(data) < 18:
                return
            
            protocol_version = struct.unpack('<H', data[1:3])[0]
            
            # Support multiple protocol versions
            supported_versions = [662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672]
            
            # Check if protocol version is supported
            if protocol_version not in supported_versions:
                # Log the actual protocol version for debugging
                logger.warning(f"Client {addr} sent protocol version {protocol_version} (0x{protocol_version:04X})")
                
                # For now, accept any protocol version to test connection
                logger.info(f"Accepting connection from {addr} with protocol {protocol_version} for testing")
            else:
                logger.info(f"Client {addr} using supported protocol version {protocol_version}")
            
            # Store pending connection
            self.pending_connections[addr] = {
                'protocol_version': protocol_version,
                'timeout': time.time() + 10.0  # 10 second timeout
            }
            
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
        """Handle open connection request 2 with improved connection setup"""
        try:
            if len(data) < 35:
                return
            
            # Parse request data
            server_address = data[1:17]
            port = struct.unpack('<H', data[17:19])[0]
            mtu_size = struct.unpack('<H', data[19:21])[0]
            client_guid = struct.unpack('<Q', data[21:29])[0]
            
            # Validate pending connection
            if addr not in self.pending_connections:
                logger.warning(f"Received open connection request 2 from {addr} without pending connection")
                return
            
            # Update pending connection
            self.pending_connections[addr].update({
                'client_guid': client_guid,
                'mtu_size': mtu_size,
                'port': port
            })
            
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
        """Handle connection request with improved connection management"""
        try:
            if len(data) < 25:
                return
            
            client_guid = struct.unpack('<Q', data[1:9])[0]
            timestamp = struct.unpack('<Q', data[9:17])[0]
            
            # Validate pending connection
            if addr not in self.pending_connections:
                logger.warning(f"Received connection request from {addr} without pending connection")
                return
            
            pending_data = self.pending_connections[addr]
            
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
            logger.info(f"Sent connection request accepted to {addr}")
            
            # Store connection data for new incoming connection
            self.pending_connections[addr]['timestamp'] = timestamp
            self.pending_connections[addr]['client_guid'] = client_guid
            
        except Exception as e:
            logger.error(f"Error handling connection request: {e}")
    
    async def handle_new_incoming_connection(self, data: bytes, addr: Tuple[str, int]):
        """Handle new incoming connection with improved player setup"""
        try:
            if addr not in self.pending_connections:
                logger.warning(f"Received new incoming connection from {addr} without pending connection")
                return
            
            pending_data = self.pending_connections[addr]
            
            # Create new connection
            connection = Connection(addr, self.socket)
            connection.client_guid = pending_data.get('client_guid', 0)
            connection.mtu_size = pending_data.get('mtu_size', 1492)
            
            self.connections[addr] = connection
            self.new_connections.append(connection)
            self.online_players += 1
            
            # Set connection timeout
            self.connection_timeouts[addr] = time.time() + 30.0  # 30 second timeout
            
            # Clean up pending connection
            del self.pending_connections[addr]
            
            logger.info(f"New connection established from {addr} (GUID: {connection.client_guid})")
            
        except Exception as e:
            logger.error(f"Error handling new incoming connection: {e}")
    
    async def handle_disconnection_notification(self, data: bytes, addr: Tuple[str, int]):
        """Handle disconnection notification with cleanup"""
        if addr in self.connections:
            connection = self.connections[addr]
            connection.close()
            del self.connections[addr]
            self.online_players = max(0, self.online_players - 1)
            
            # Clean up timeouts
            if addr in self.connection_timeouts:
                del self.connection_timeouts[addr]
            
            logger.info(f"Connection closed from {addr}")
    
    async def handle_data_packet(self, data: bytes, addr: Tuple[str, int]):
        """Handle data packet with improved reliability"""
        if addr in self.connections:
            connection = self.connections[addr]
            connection.receive_packet(data)
            
            # Update connection timeout
            self.connection_timeouts[addr] = time.time() + 30.0
    
    async def handle_ack(self, data: bytes, addr: Tuple[str, int]):
        """Handle ACK packet with improved reliability"""
        if addr in self.connections:
            connection = self.connections[addr]
            connection.handle_ack(data)
    
    async def handle_nak(self, data: bytes, addr: Tuple[str, int]):
        """Handle NAK packet with improved reliability"""
        if addr in self.connections:
            connection = self.connections[addr]
            connection.handle_nak(data)
    
    async def send_packet(self, data: bytes, addr: Tuple[str, int]):
        """Send packet with improved error handling"""
        try:
            loop = asyncio.get_event_loop()
            await loop.sock_sendto(self.socket, data, addr)
            
            self.packets_sent += 1
            self.bytes_sent += len(data)
            
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
    
    def get_statistics(self) -> Dict:
        """Get server statistics"""
        return {
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'connections': len(self.connections),
            'pending_connections': len(self.pending_connections),
            'online_players': self.online_players
        }