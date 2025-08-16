"""
Simplified NBT (Named Binary Tag) implementation for Minecraft Bedrock
"""

import struct
from typing import Any, Dict, List, Union

class NBTType:
    """NBT tag types"""
    TAG_END = 0
    TAG_BYTE = 1
    TAG_SHORT = 2
    TAG_INT = 3
    TAG_LONG = 4
    TAG_FLOAT = 5
    TAG_DOUBLE = 6
    TAG_BYTE_ARRAY = 7
    TAG_STRING = 8
    TAG_LIST = 9
    TAG_COMPOUND = 10
    TAG_INT_ARRAY = 11
    TAG_LONG_ARRAY = 12

class NBTWriter:
    """NBT writer for serializing NBT data"""
    
    def __init__(self):
        self.data = bytearray()
    
    def write_byte(self, value: int):
        """Write a byte"""
        self.data.extend(struct.pack('<b', value))
    
    def write_short(self, value: int):
        """Write a short"""
        self.data.extend(struct.pack('<h', value))
    
    def write_int(self, value: int):
        """Write an int"""
        self.data.extend(struct.pack('<i', value))
    
    def write_long(self, value: int):
        """Write a long"""
        self.data.extend(struct.pack('<q', value))
    
    def write_float(self, value: float):
        """Write a float"""
        self.data.extend(struct.pack('<f', value))
    
    def write_double(self, value: float):
        """Write a double"""
        self.data.extend(struct.pack('<d', value))
    
    def write_string(self, value: str):
        """Write a string"""
        data = value.encode('utf-8')
        self.data.extend(struct.pack('<H', len(data)))
        self.data.extend(data)
    
    def write_byte_array(self, value: bytes):
        """Write a byte array"""
        self.data.extend(struct.pack('<i', len(value)))
        self.data.extend(value)
    
    def write_int_array(self, value: List[int]):
        """Write an int array"""
        self.data.extend(struct.pack('<i', len(value)))
        for item in value:
            self.data.extend(struct.pack('<i', item))
    
    def write_compound(self, value: Dict[str, Any]):
        """Write a compound tag"""
        for key, val in value.items():
            if isinstance(val, int):
                if -128 <= val <= 127:
                    self.data.append(NBTType.TAG_BYTE)
                    self.write_string(key)
                    self.write_byte(val)
                elif -32768 <= val <= 32767:
                    self.data.append(NBTType.TAG_SHORT)
                    self.write_string(key)
                    self.write_short(val)
                else:
                    self.data.append(NBTType.TAG_INT)
                    self.write_string(key)
                    self.write_int(val)
            elif isinstance(val, float):
                self.data.append(NBTType.TAG_FLOAT)
                self.write_string(key)
                self.write_float(val)
            elif isinstance(val, str):
                self.data.append(NBTType.TAG_STRING)
                self.write_string(key)
                self.write_string(val)
            elif isinstance(val, bytes):
                self.data.append(NBTType.TAG_BYTE_ARRAY)
                self.write_string(key)
                self.write_byte_array(val)
            elif isinstance(val, list):
                if val and isinstance(val[0], int):
                    self.data.append(NBTType.TAG_INT_ARRAY)
                    self.write_string(key)
                    self.write_int_array(val)
                else:
                    # Simplified list handling
                    self.data.append(NBTType.TAG_LIST)
                    self.write_string(key)
                    self.data.append(NBTType.TAG_STRING)
                    self.data.extend(struct.pack('<i', len(val)))
                    for item in val:
                        self.write_string(str(item))
            elif isinstance(val, dict):
                self.data.append(NBTType.TAG_COMPOUND)
                self.write_string(key)
                self.write_compound(val)
        
        # End compound
        self.data.append(NBTType.TAG_END)
    
    def get_data(self) -> bytes:
        """Get the serialized data"""
        return bytes(self.data)

class NBTReader:
    """NBT reader for deserializing NBT data"""
    
    def __init__(self, data: bytes):
        self.data = data
        self.offset = 0
    
    def read_byte(self) -> int:
        """Read a byte"""
        value = struct.unpack('<b', self.data[self.offset:self.offset+1])[0]
        self.offset += 1
        return value
    
    def read_short(self) -> int:
        """Read a short"""
        value = struct.unpack('<h', self.data[self.offset:self.offset+2])[0]
        self.offset += 2
        return value
    
    def read_int(self) -> int:
        """Read an int"""
        value = struct.unpack('<i', self.data[self.offset:self.offset+4])[0]
        self.offset += 4
        return value
    
    def read_long(self) -> int:
        """Read a long"""
        value = struct.unpack('<q', self.data[self.offset:self.offset+8])[0]
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
    
    def read_string(self) -> str:
        """Read a string"""
        length = struct.unpack('<H', self.data[self.offset:self.offset+2])[0]
        self.offset += 2
        value = self.data[self.offset:self.offset+length].decode('utf-8')
        self.offset += length
        return value
    
    def read_byte_array(self) -> bytes:
        """Read a byte array"""
        length = self.read_int()
        value = self.data[self.offset:self.offset+length]
        self.offset += length
        return value
    
    def read_int_array(self) -> List[int]:
        """Read an int array"""
        length = self.read_int()
        value = []
        for _ in range(length):
            value.append(self.read_int())
        return value
    
    def read_compound(self) -> Dict[str, Any]:
        """Read a compound tag"""
        result = {}
        while True:
            tag_type = self.data[self.offset]
            self.offset += 1
            
            if tag_type == NBTType.TAG_END:
                break
            
            name = self.read_string()
            
            if tag_type == NBTType.TAG_BYTE:
                result[name] = self.read_byte()
            elif tag_type == NBTType.TAG_SHORT:
                result[name] = self.read_short()
            elif tag_type == NBTType.TAG_INT:
                result[name] = self.read_int()
            elif tag_type == NBTType.TAG_LONG:
                result[name] = self.read_long()
            elif tag_type == NBTType.TAG_FLOAT:
                result[name] = self.read_float()
            elif tag_type == NBTType.TAG_DOUBLE:
                result[name] = self.read_double()
            elif tag_type == NBTType.TAG_STRING:
                result[name] = self.read_string()
            elif tag_type == NBTType.TAG_BYTE_ARRAY:
                result[name] = self.read_byte_array()
            elif tag_type == NBTType.TAG_INT_ARRAY:
                result[name] = self.read_int_array()
            elif tag_type == NBTType.TAG_COMPOUND:
                result[name] = self.read_compound()
            else:
                # Skip unknown tags
                pass
        
        return result

def write_nbt(data: Dict[str, Any]) -> bytes:
    """Write NBT data to bytes"""
    writer = NBTWriter()
    writer.write_compound(data)
    return writer.get_data()

def read_nbt(data: bytes) -> Dict[str, Any]:
    """Read NBT data from bytes"""
    reader = NBTReader(data)
    return reader.read_compound()