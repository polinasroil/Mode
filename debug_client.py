#!/usr/bin/env python3
"""
Debug client for testing Minecraft Bedrock Server connection
"""

import socket
import struct
import time
import logging
import random

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DebugClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        self.client_guid = random.randint(1000000, 9999999)
        self.protocol_version = 662
        
    def connect(self):
        """Create UDP socket"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
            logger.info(f"Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            return False
    
    def send_packet(self, data: bytes):
        """Send packet to server"""
        try:
            self.socket.sendto(data, (self.host, self.port))
            logger.debug(f"Sent packet: {data.hex()}")
            return True
        except Exception as e:
            logger.error(f"Failed to send packet: {e}")
            return False
    
    def receive_packet(self):
        """Receive packet from server"""
        try:
            data, addr = self.socket.recvfrom(4096)
            logger.debug(f"Received packet from {addr}: {data.hex()}")
            return data
        except socket.timeout:
            logger.warning("Timeout waiting for packet")
            return None
        except Exception as e:
            logger.error(f"Failed to receive packet: {e}")
            return None
    
    def test_ping(self):
        """Test unconnected ping"""
        logger.info("=== Testing Ping ===")
        
        # Create ping packet
        ping_data = bytearray()
        ping_data.append(0x01)  # Unconnected ping
        ping_data.extend(struct.pack('<Q', int(time.time() * 1000)))
        ping_data.extend(b'\x00' * 16)  # Magic
        
        if self.send_packet(bytes(ping_data)):
            response = self.receive_packet()
            if response:
                logger.info("✅ Ping successful")
                return True
            else:
                logger.error("❌ No ping response")
                return False
        return False
    
    def test_connection_handshake(self):
        """Test full connection handshake"""
        logger.info("=== Testing Connection Handshake ===")
        
        # Step 1: Open connection request 1
        logger.info("Step 1: Sending open connection request 1")
        req1_data = bytearray()
        req1_data.append(0x05)  # Open connection request 1
        req1_data.extend(struct.pack('<H', self.protocol_version))
        req1_data.extend(b'\x00' * 16)  # Padding
        
        if not self.send_packet(bytes(req1_data)):
            return False
        
        response1 = self.receive_packet()
        if not response1:
            logger.error("❌ No response to open connection request 1")
            return False
        
        if response1[0] == 0x06:  # Open connection reply 1
            logger.info("✅ Received open connection reply 1")
            server_guid = struct.unpack('<Q', response1[1:9])[0]
            logger.info(f"Server GUID: {server_guid}")
        else:
            logger.error(f"❌ Unexpected response: {response1[0]:02X}")
            return False
        
        # Step 2: Open connection request 2
        logger.info("Step 2: Sending open connection request 2")
        req2_data = bytearray()
        req2_data.append(0x07)  # Open connection request 2
        req2_data.extend(b'\x00' * 16)  # Server address
        req2_data.extend(struct.pack('<H', self.port))  # Port
        req2_data.extend(struct.pack('<H', 1492))  # MTU size
        req2_data.extend(struct.pack('<Q', self.client_guid))  # Client GUID
        
        if not self.send_packet(bytes(req2_data)):
            return False
        
        response2 = self.receive_packet()
        if not response2:
            logger.error("❌ No response to open connection request 2")
            return False
        
        if response2[0] == 0x08:  # Open connection reply 2
            logger.info("✅ Received open connection reply 2")
        else:
            logger.error(f"❌ Unexpected response: {response2[0]:02X}")
            return False
        
        # Step 3: Connection request
        logger.info("Step 3: Sending connection request")
        conn_req_data = bytearray()
        conn_req_data.append(0x09)  # Connection request
        conn_req_data.extend(struct.pack('<Q', self.client_guid))
        conn_req_data.extend(struct.pack('<Q', int(time.time() * 1000)))
        conn_req_data.extend(b'\x00' * 8)  # Security
        
        if not self.send_packet(bytes(conn_req_data)):
            return False
        
        response3 = self.receive_packet()
        if not response3:
            logger.error("❌ No response to connection request")
            return False
        
        if response3[0] == 0x10:  # Connection request accepted
            logger.info("✅ Received connection request accepted")
        else:
            logger.error(f"❌ Unexpected response: {response3[0]:02X}")
            return False
        
        # Step 4: New incoming connection
        logger.info("Step 4: Sending new incoming connection")
        new_conn_data = bytearray()
        new_conn_data.append(0x13)  # New incoming connection
        new_conn_data.extend(struct.pack('<Q', self.client_guid))
        new_conn_data.extend(b'\x00' * 16)  # System address
        new_conn_data.extend(struct.pack('<H', 0))  # Port
        new_conn_data.extend(struct.pack('<H', 1))  # System addresses count
        new_conn_data.extend(b'\x00' * 16)  # Address
        new_conn_data.extend(struct.pack('<H', 0))  # Port
        
        if not self.send_packet(bytes(new_conn_data)):
            return False
        
        logger.info("✅ Connection handshake completed")
        return True
    
    def test_minecraft_packets(self):
        """Test Minecraft game packets"""
        logger.info("=== Testing Minecraft Packets ===")
        
        # Send a simple text packet
        text_data = bytearray()
        text_data.append(0x09)  # Text packet
        text_data.append(0x01)  # Message type
        text_data.extend(struct.pack('<H', 0))  # XUID length
        text_data.extend(struct.pack('<H', 0))  # Platform chat ID length
        message = "Hello from debug client!"
        text_data.extend(struct.pack('<H', len(message)))
        text_data.extend(message.encode('utf-8'))
        
        if self.send_packet(bytes(text_data)):
            logger.info("✅ Sent text packet")
            return True
        else:
            logger.error("❌ Failed to send text packet")
            return False
    
    def close(self):
        """Close connection"""
        if self.socket:
            self.socket.close()
            logger.info("Connection closed")

def main():
    client = DebugClient("127.0.0.1", 19132)
    
    if not client.connect():
        return
    
    try:
        # Test ping
        if not client.test_ping():
            logger.error("❌ Ping test failed")
            return
        
        # Test connection handshake
        if not client.test_connection_handshake():
            logger.error("❌ Connection handshake failed")
            return
        
        # Test Minecraft packets
        if not client.test_minecraft_packets():
            logger.warning("⚠️ Minecraft packets test had issues")
        
        logger.info("🎉 All tests completed!")
        
    finally:
        client.close()

if __name__ == "__main__":
    main()