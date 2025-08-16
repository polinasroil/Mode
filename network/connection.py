"""
Connection class for managing individual RakNet connections
Handles packet queuing, reliability, and flow control
"""

import asyncio
import logging
import socket
import struct
import time
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

class Connection:
    """Represents a single RakNet connection"""
    
    def __init__(self, address: Tuple[str, int], socket_obj: socket.socket):
        self.address = address
        self.socket = socket_obj
        self.connected = True
        self.mtu_size = 1492
        self.reliable_frame_index = 0
        self.split_packet_id = 0
        
        # Packet queues
        self.received_packets: List[bytes] = []
        self.sent_packets: List[Tuple[int, bytes]] = []  # (frame_index, packet_data)
        self.ack_queue: List[int] = []
        self.nak_queue: List[int] = []
        
        # Flow control
        self.window_size = 2048
        self.reliable_window_start = 0
        self.reliable_window_end = 0
        
        # Statistics
        self.bytes_sent = 0
        self.bytes_received = 0
        self.packets_sent = 0
        self.packets_received = 0
        self.last_activity = time.time()
        
        logger.debug(f"Created connection for {address}")
    
    def receive_packet(self, data: bytes):
        """Receive a packet from the client"""
        if not self.connected:
            return
        
        self.bytes_received += len(data)
        self.packets_received += 1
        self.last_activity = time.time()
        
        # Handle different packet types
        packet_id = data[0]
        
        if packet_id >= 0x80 and packet_id <= 0x8F:  # Data packets
            self.handle_data_packet(data)
        elif packet_id == 0xC0:  # ACK
            self.handle_ack(data)
        elif packet_id == 0xA0:  # NAK
            self.handle_nak(data)
        else:
            # Direct packet (no reliability)
            self.received_packets.append(data)
    
    def handle_data_packet(self, data: bytes):
        """Handle a data packet with reliability"""
        try:
            # Parse packet header
            if len(data) < 4:
                return
            
            packet_id = data[0]
            reliability = (packet_id & 0xE0) >> 5
            has_split = bool(packet_id & 0x10)
            
            # Extract sequence number
            sequence_number = struct.unpack('<H', data[1:3])[0]
            
            # Handle split packets
            if has_split:
                self.handle_split_packet(data)
            else:
                # Single packet
                payload = data[3:]
                self.received_packets.append(payload)
                
                # Send ACK for reliable packets
                if reliability in [2, 3, 4, 6, 7]:  # Reliable types
                    self.ack_queue.append(sequence_number)
        
        except Exception as e:
            logger.error(f"Error handling data packet: {e}")
    
    def handle_split_packet(self, data: bytes):
        """Handle split packet reassembly"""
        # Simplified split packet handling
        # In a full implementation, this would reassemble split packets
        logger.debug("Split packet received (not fully implemented)")
    
    def handle_ack(self, data: bytes):
        """Handle ACK packet"""
        try:
            if len(data) < 3:
                return
            
            count = struct.unpack('<H', data[1:3])[0]
            offset = 3
            
            for i in range(count):
                if offset + 2 <= len(data):
                    sequence_number = struct.unpack('<H', data[offset:offset+2])[0]
                    self.ack_queue.append(sequence_number)
                    offset += 2
                    
                    # Remove acknowledged packet from sent queue
                    self.sent_packets = [(idx, pkt) for idx, pkt in self.sent_packets if idx != sequence_number]
        
        except Exception as e:
            logger.error(f"Error handling ACK: {e}")
    
    def handle_nak(self, data: bytes):
        """Handle NAK packet"""
        try:
            if len(data) < 3:
                return
            
            count = struct.unpack('<H', data[1:3])[0]
            offset = 3
            
            for i in range(count):
                if offset + 2 <= len(data):
                    sequence_number = struct.unpack('<H', data[offset:offset+2])[0]
                    self.nak_queue.append(sequence_number)
                    offset += 2
        
        except Exception as e:
            logger.error(f"Error handling NAK: {e}")
    
    async def send_packet(self, data: bytes):
        """Send a packet to the client"""
        if not self.connected:
            return
        
        try:
            # Create reliable packet
            packet = self.create_reliable_packet(data)
            
            # Add to sent queue
            self.sent_packets.append((self.reliable_frame_index, packet))
            self.reliable_frame_index = (self.reliable_frame_index + 1) % 65536
            
            # Send packet
            loop = asyncio.get_event_loop()
            await loop.sock_sendto(self.socket, packet, self.address)
            
            self.bytes_sent += len(packet)
            self.packets_sent += 1
            self.last_activity = time.time()
            
        except Exception as e:
            logger.error(f"Error sending packet to {self.address}: {e}")
            self.connected = False
    
    def create_reliable_packet(self, data: bytes) -> bytes:
        """Create a reliable packet with sequence number"""
        packet = bytearray()
        
        # Packet ID (reliable ordered)
        packet.append(0x84)  # Reliable ordered data packet
        
        # Sequence number
        packet.extend(struct.pack('<H', self.reliable_frame_index))
        
        # Payload
        packet.extend(data)
        
        return bytes(packet)
    
    async def get_packets(self) -> List[bytes]:
        """Get all received packets and clear the queue"""
        packets = self.received_packets.copy()
        self.received_packets.clear()
        return packets
    
    def is_connected(self) -> bool:
        """Check if connection is still active"""
        if not self.connected:
            return False
        
        # Check for timeout
        if time.time() - self.last_activity > 30:  # 30 second timeout
            self.connected = False
            return False
        
        return True
    
    def close(self):
        """Close the connection"""
        self.connected = False
        logger.debug(f"Connection closed for {self.address}")
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            'address': self.address,
            'connected': self.connected,
            'bytes_sent': self.bytes_sent,
            'bytes_received': self.bytes_received,
            'packets_sent': self.packets_sent,
            'packets_received': self.packets_received,
            'last_activity': self.last_activity,
            'mtu_size': self.mtu_size,
            'reliable_frame_index': self.reliable_frame_index
        }
    
    def __str__(self) -> str:
        return f"Connection({self.address[0]}:{self.address[1]})"
    
    def __repr__(self) -> str:
        return self.__str__()