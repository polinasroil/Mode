"""
Packet serializer/deserializer for Minecraft Bedrock protocol
Handles binary data encoding and decoding
"""

import struct
import zlib
from typing import Any, Dict, List, Optional, Union

class PacketSerializer:
    """Serializer for Minecraft Bedrock packets"""
    
    @staticmethod
    def write_byte(value: int) -> bytes:
        """Write a signed byte"""
        return struct.pack('<b', value)
    
    @staticmethod
    def write_ubyte(value: int) -> bytes:
        """Write an unsigned byte"""
        return struct.pack('<B', value)
    
    @staticmethod
    def write_short(value: int) -> bytes:
        """Write a signed short"""
        return struct.pack('<h', value)
    
    @staticmethod
    def write_ushort(value: int) -> bytes:
        """Write an unsigned short"""
        return struct.pack('<H', value)
    
    @staticmethod
    def write_int(value: int) -> bytes:
        """Write a signed int"""
        return struct.pack('<i', value)
    
    @staticmethod
    def write_uint(value: int) -> bytes:
        """Write an unsigned int"""
        return struct.pack('<I', value)
    
    @staticmethod
    def write_long(value: int) -> bytes:
        """Write a signed long"""
        return struct.pack('<q', value)
    
    @staticmethod
    def write_ulong(value: int) -> bytes:
        """Write an unsigned long"""
        return struct.pack('<Q', value)
    
    @staticmethod
    def write_float(value: float) -> bytes:
        """Write a float"""
        return struct.pack('<f', value)
    
    @staticmethod
    def write_double(value: float) -> bytes:
        """Write a double"""
        return struct.pack('<d', value)
    
    @staticmethod
    def write_bool(value: bool) -> bytes:
        """Write a boolean"""
        return struct.pack('<?', value)
    
    @staticmethod
    def write_string(value: str) -> bytes:
        """Write a string with length prefix"""
        data = value.encode('utf-8')
        return struct.pack('<H', len(data)) + data
    
    @staticmethod
    def write_varint(value: int) -> bytes:
        """Write a variable-length integer"""
        data = bytearray()
        while True:
            byte = value & 0x7F
            value >>= 7
            if value:
                byte |= 0x80
            data.append(byte)
            if not value:
                break
        return bytes(data)
    
    @staticmethod
    def write_position(x: int, y: int, z: int) -> bytes:
        """Write a block position"""
        return struct.pack('<iii', x, y, z)
    
    @staticmethod
    def write_vector3f(x: float, y: float, z: float) -> bytes:
        """Write a 3D vector"""
        return struct.pack('<fff', x, y, z)
    
    @staticmethod
    def write_runtime_entity_id(entity_id: int) -> bytes:
        """Write a runtime entity ID"""
        return struct.pack('<Q', entity_id)
    
    @staticmethod
    def write_block_coordinates(x: int, y: int, z: int) -> bytes:
        """Write block coordinates"""
        return struct.pack('<iii', x, y, z)
    
    @staticmethod
    def write_block_face(face: int) -> bytes:
        """Write block face direction"""
        return struct.pack('<B', face)
    
    @staticmethod
    def write_item_stack(item_id: int, count: int, metadata: int = 0) -> bytes:
        """Write an item stack"""
        data = bytearray()
        data.extend(struct.pack('<H', item_id))
        data.extend(struct.pack('<B', count))
        data.extend(struct.pack('<H', metadata))
        return bytes(data)

class PacketDeserializer:
    """Deserializer for Minecraft Bedrock packets"""
    
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0
    
    def read_byte(self) -> int:
        """Read a signed byte"""
        value = struct.unpack('<b', self.data[self.offset:self.offset+1])[0]
        self.offset += 1
        return value
    
    def read_ubyte(self) -> int:
        """Read an unsigned byte"""
        value = struct.unpack('<B', self.data[self.offset:self.offset+1])[0]
        self.offset += 1
        return value
    
    def read_short(self) -> int:
        """Read a signed short"""
        value = struct.unpack('<h', self.data[self.offset:self.offset+2])[0]
        self.offset += 2
        return value
    
    def read_ushort(self) -> int:
        """Read an unsigned short"""
        value = struct.unpack('<H', self.data[self.offset:self.offset+2])[0]
        self.offset += 2
        return value
    
    def read_int(self) -> int:
        """Read a signed int"""
        value = struct.unpack('<i', self.data[self.offset:self.offset+4])[0]
        self.offset += 4
        return value
    
    def read_uint(self) -> int:
        """Read an unsigned int"""
        value = struct.unpack('<I', self.data[self.offset:self.offset+4])[0]
        self.offset += 4
        return value
    
    def read_long(self) -> int:
        """Read a signed long"""
        value = struct.unpack('<q', self.data[self.offset:self.offset+8])[0]
        self.offset += 8
        return value
    
    def read_ulong(self) -> int:
        """Read an unsigned long"""
        value = struct.unpack('<Q', self.data[self.offset:self.offset+8])[0]
        self.offset += 8
        return value
    
    def read_float(self) -> float:
        """Read a float"""
        value = struct.unpack('<f', self.data[self.offset:self.offset+4])[0]
        self.offset += 4
        return value
    
    def read_double(self) -> float:
        """Read a double"""
        value = struct.unpack('<d', self.data[self.offset:self.offset+8])[0]
        self.offset += 8
        return value
    
    def read_bool(self) -> bool:
        """Read a boolean"""
        value = struct.unpack('<?', self.data[self.offset:self.offset+1])[0]
        self.offset += 1
        return value
    
    def read_string(self) -> str:
        """Read a string with length prefix"""
        length = self.read_ushort()
        value = self.data[self.offset:self.offset+length].decode('utf-8')
        self.offset += length
        return value
    
    def read_varint(self) -> int:
        """Read a variable-length integer"""
        value = 0
        shift = 0
        while True:
            byte = self.data[self.offset]
            self.offset += 1
            value |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
        return value
    
    def read_position(self) -> tuple:
        """Read a block position"""
        x = self.read_int()
        y = self.read_int()
        z = self.read_int()
        return (x, y, z)
    
    def read_vector3f(self) -> tuple:
        """Read a 3D vector"""
        x = self.read_float()
        y = self.read_float()
        z = self.read_float()
        return (x, y, z)
    
    def read_runtime_entity_id(self) -> int:
        """Read a runtime entity ID"""
        return self.read_ulong()
    
    def read_block_coordinates(self) -> tuple:
        """Read block coordinates"""
        return self.read_position()
    
    def read_block_face(self) -> int:
        """Read block face direction"""
        return self.read_ubyte()
    
    def read_item_stack(self) -> tuple:
        """Read an item stack"""
        item_id = self.read_ushort()
        count = self.read_ubyte()
        metadata = self.read_ushort()
        return (item_id, count, metadata)
    
    def remaining(self) -> int:
        """Get remaining bytes to read"""
        return len(self.data) - self.offset
    
    def skip(self, count: int):
        """Skip bytes"""
        self.offset += count

class BatchPacket:
    """Batch packet for sending multiple packets efficiently"""
    
    @staticmethod
    def compress_packets(packets: List[bytes]) -> bytes:
        """Compress multiple packets into a batch packet"""
        # Combine all packets
        combined = b''.join(packets)
        
        # Compress using zlib
        compressed = zlib.compress(combined)
        
        # Create batch packet
        batch = bytearray()
        batch.append(0xFE)  # Batch packet ID
        batch.extend(struct.pack('<I', len(compressed)))
        batch.extend(compressed)
        
        return bytes(batch)
    
    @staticmethod
    def decompress_packets(data: bytes) -> List[bytes]:
        """Decompress a batch packet into individual packets"""
        if not data or data[0] != 0xFE:
            return [data]
        
        # Extract compressed data
        compressed_length = struct.unpack('<I', data[1:5])[0]
        compressed_data = data[5:5+compressed_length]
        
        # Decompress
        try:
            decompressed = zlib.decompress(compressed_data)
        except zlib.error:
            return []
        
        # Split into individual packets
        packets = []
        offset = 0
        while offset < len(decompressed):
            if offset + 3 > len(decompressed):
                break
            
            # Read packet length (varint)
            length = 0
            shift = 0
            while offset < len(decompressed):
                byte = decompressed[offset]
                offset += 1
                length |= (byte & 0x7F) << shift
                if not (byte & 0x80):
                    break
                shift += 7
            
            if offset + length > len(decompressed):
                break
            
            packet = decompressed[offset:offset+length]
            packets.append(packet)
            offset += length
        
        return packets