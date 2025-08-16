#!/usr/bin/env python3
"""
Simple test client for Minecraft Bedrock Server
Tests basic connectivity and packet handling
"""

import socket
import struct
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestClient:
    """Simple test client for Minecraft Bedrock server"""
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.socket = None
        
    def connect(self):
        """Connect to the server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(5.0)
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
        """Test connection handshake"""
        try:
            # Open connection request 1
            request1 = bytearray()
            request1.append(0x05)  # Open connection request 1
            request1.extend(struct.pack('<H', 662))  # Protocol version
            request1.extend(b'\x00' * 16)  # Padding
            
            self.socket.sendto(bytes(request1), (self.host, self.port))
            logger.info("Sent open connection request 1")
            
            # Wait for reply
            try:
                data, addr = self.socket.recvfrom(1024)
                if data[0] == 0x06:  # Open connection reply 1
                    logger.info("✅ Received open connection reply 1")
                    
                    # Parse server GUID
                    server_guid = struct.unpack('<Q', data[1:9])[0]
                    logger.info(f"Server GUID: {server_guid}")
                    
                    # Send open connection request 2
                    request2 = bytearray()
                    request2.append(0x07)  # Open connection request 2
                    request2.extend(b'\x00' * 16)  # Server address
                    request2.extend(struct.pack('<H', self.port))  # Port
                    request2.extend(struct.pack('<H', 1492))  # MTU size
                    request2.extend(struct.pack('<Q', 12345))  # Client GUID
                    
                    self.socket.sendto(bytes(request2), (self.host, self.port))
                    logger.info("Sent open connection request 2")
                    
                    # Wait for reply 2
                    data, addr = self.socket.recvfrom(1024)
                    if data[0] == 0x08:  # Open connection reply 2
                        logger.info("✅ Received open connection reply 2")
                        return True
                    else:
                        logger.warning(f"Unexpected reply 2: {data[0]:02X}")
                        return False
                        
                else:
                    logger.warning(f"Unexpected reply 1: {data[0]:02X}")
                    return False
                    
            except socket.timeout:
                logger.error("❌ Timeout waiting for connection reply")
                return False
                
        except Exception as e:
            logger.error(f"Error in connection handshake: {e}")
            return False
    
    def close(self):
        """Close the connection"""
        if self.socket:
            self.socket.close()
            logger.info("Connection closed")

def main():
    """Test the server"""
    client = TestClient("127.0.0.1", 19132)
    
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
        
        logger.info("🎉 All tests passed! Server is working correctly.")
        
    finally:
        client.close()

if __name__ == "__main__":
    main()