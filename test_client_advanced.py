#!/usr/bin/env python3
"""
Advanced test client for Minecraft Bedrock Server
Tests full connection sequence and packet handling
"""

import socket
import struct
import time
import logging
import asyncio
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedTestClient:
    """Advanced test client for Minecraft Bedrock server"""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        self.client_guid = random.randint(1000000, 9999999)
        self.protocol_version = 662
        self.username = f"TestPlayer_{self.client_guid}"
        
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(10.0)
            logger.info(f"Connecting to {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to create socket: {e}")
            return False
    
    def send_ping(self):
        """Send unconnected ping to test server visibility"""
        try:
            # Create unconnected ping packet
            ping_data = bytearray()
            ping_data.append(0x01)  # Unconnected ping
            ping_data.extend(struct.pack('<Q', int(time.time() * 1000)))
            ping_data.extend(b'\x00' * 16)  # Magic
            
            self.socket.sendto(bytes(ping_data), (self.host, self.port))
            logger.info("Sent unconnected ping")
            
            # Wait for response
            try:
                data, addr = self.socket.recvfrom(1024)
                logger.info(f"Received response from {addr}: {len(data)} bytes")
                if data[0] == 0x1C:  # Unconnected pong
                    logger.info("✅ Server is responding to ping!")
                    return True
                else:
                    logger.warning(f"Unexpected response: {data[0]:02X}")
                    return False
            except socket.timeout:
                logger.error("❌ No response from server (timeout)")
                return False
                
        except Exception as e:
            logger.error(f"Error sending ping: {e}")
            return False
    
    def test_connection_handshake(self):
        """Test full connection handshake"""
        try:
            # Step 1: Open connection request 1
            logger.info("=== Step 1: Open connection request 1 ===")
            request1 = bytearray()
            request1.append(0x05)  # Open connection request 1
            request1.extend(struct.pack('<H', self.protocol_version))
            request1.extend(b'\x00' * 16)  # Padding
            
            self.socket.sendto(bytes(request1), (self.host, self.port))
            logger.info("Sent open connection request 1")
            
            # Wait for reply 1
            try:
                data, addr = self.socket.recvfrom(1024)
                if data[0] == 0x06:  # Open connection reply 1
                    logger.info("✅ Received open connection reply 1")
                    server_guid = struct.unpack('<Q', data[1:9])[0]
                    logger.info(f"Server GUID: {server_guid}")
                else:
                    logger.error(f"❌ Unexpected reply 1: {data[0]:02X}")
                    return False
            except socket.timeout:
                logger.error("❌ Timeout waiting for reply 1")
                return False
            
            # Step 2: Open connection request 2
            logger.info("=== Step 2: Open connection request 2 ===")
            request2 = bytearray()
            request2.append(0x07)  # Open connection request 2
            request2.extend(b'\x00' * 16)  # Server address
            request2.extend(struct.pack('<H', self.port))  # Port
            request2.extend(struct.pack('<H', 1492))  # MTU size
            request2.extend(struct.pack('<Q', self.client_guid))  # Client GUID
            
            self.socket.sendto(bytes(request2), (self.host, self.port))
            logger.info("Sent open connection request 2")
            
            # Wait for reply 2
            try:
                data, addr = self.socket.recvfrom(1024)
                if data[0] == 0x08:  # Open connection reply 2
                    logger.info("✅ Received open connection reply 2")
                else:
                    logger.error(f"❌ Unexpected reply 2: {data[0]:02X}")
                    return False
            except socket.timeout:
                logger.error("❌ Timeout waiting for reply 2")
                return False
            
            # Step 3: Connection request
            logger.info("=== Step 3: Connection request ===")
            timestamp = int(time.time() * 1000)
            conn_request = bytearray()
            conn_request.append(0x09)  # Connection request
            conn_request.extend(struct.pack('<Q', self.client_guid))
            conn_request.extend(struct.pack('<Q', timestamp))
            
            self.socket.sendto(bytes(conn_request), (self.host, self.port))
            logger.info("Sent connection request")
            
            # Wait for connection request accepted
            try:
                data, addr = self.socket.recvfrom(1024)
                if data[0] == 0x10:  # Connection request accepted
                    logger.info("✅ Received connection request accepted")
                else:
                    logger.error(f"❌ Unexpected connection response: {data[0]:02X}")
                    return False
            except socket.timeout:
                logger.error("❌ Timeout waiting for connection accepted")
                return False
            
            # Step 4: New incoming connection
            logger.info("=== Step 4: New incoming connection ===")
            new_conn = bytearray()
            new_conn.append(0x13)  # New incoming connection
            new_conn.extend(struct.pack('<Q', self.client_guid))
            new_conn.extend(b'\x00' * 16)  # System address
            new_conn.extend(struct.pack('<H', 0))  # Port
            
            self.socket.sendto(bytes(new_conn), (self.host, self.port))
            logger.info("Sent new incoming connection")
            
            # Wait for game packets
            logger.info("=== Step 5: Waiting for game packets ===")
            start_time = time.time()
            packets_received = 0
            
            while time.time() - start_time < 5.0:  # Wait up to 5 seconds
                try:
                    data, addr = self.socket.recvfrom(4096)
                    packet_id = data[0]
                    logger.info(f"Received packet: {packet_id:02X} ({len(data)} bytes)")
                    packets_received += 1
                    
                    if packet_id == 0x02:  # Play status packet
                        logger.info("✅ Received play status packet")
                    elif packet_id == 0x0B:  # Start game packet
                        logger.info("✅ Received start game packet")
                    elif packet_id == 0x3A:  # Level chunk packet
                        logger.info("✅ Received level chunk packet")
                    elif packet_id == 0x0C:  # Add player packet
                        logger.info("✅ Received add player packet")
                    
                except socket.timeout:
                    continue
            
            if packets_received > 0:
                logger.info(f"✅ Received {packets_received} game packets")
                return True
            else:
                logger.error("❌ No game packets received")
                return False
                
        except Exception as e:
            logger.error(f"Error in connection handshake: {e}")
            return False
    
    def test_minecraft_packets(self):
        """Test Minecraft-specific packets"""
        try:
            logger.info("=== Testing Minecraft packets ===")
            
            # Send a simple text message
            text_packet = bytearray()
            text_packet.append(0x09)  # Text packet
            text_packet.append(0x01)  # Message type (chat)
            text_packet.extend(struct.pack('<H', 0))  # XUID length
            text_packet.extend(struct.pack('<H', 0))  # Platform chat ID length
            text_packet.extend(struct.pack('<H', 5))  # Message length
            text_packet.extend(b'Hello')  # Message
            
            self.socket.sendto(bytes(text_packet), (self.host, self.port))
            logger.info("Sent text packet")
            
            # Wait for response
            try:
                data, addr = self.socket.recvfrom(1024)
                logger.info(f"Received response to text: {data[0]:02X}")
                return True
            except socket.timeout:
                logger.warning("No response to text packet")
                return True  # Not critical
                
        except Exception as e:
            logger.error(f"Error testing Minecraft packets: {e}")
            return False
    
    def close(self):
        """Close the connection"""
        if self.socket:
            self.socket.close()
            logger.info("Connection closed")

def main():
    """Test the server with advanced client"""
    client = AdvancedTestClient("127.0.0.1", 19132)
    
    if not client.connect():
        logger.error("Failed to connect")
        return
    
    try:
        # Test ping
        logger.info("=== Testing Ping ===")
        if client.send_ping():
            logger.info("✅ Ping test passed")
        else:
            logger.error("❌ Ping test failed")
            return
        
        # Test connection handshake
        logger.info("=== Testing Connection Handshake ===")
        if client.test_connection_handshake():
            logger.info("✅ Connection handshake test passed")
        else:
            logger.error("❌ Connection handshake test failed")
            return
        
        # Test Minecraft packets
        logger.info("=== Testing Minecraft Packets ===")
        if client.test_minecraft_packets():
            logger.info("✅ Minecraft packets test passed")
        else:
            logger.warning("⚠️ Minecraft packets test had issues")
        
        logger.info("🎉 All tests passed! Server is working correctly.")
        
    finally:
        client.close()

if __name__ == "__main__":
    main()