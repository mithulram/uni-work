#!/usr/bin/env python3
"""
ucdr Handler - microCDR Serialization for ASOA Protocol
Handles ucdr (microCDR) serialized data structures used in ASOA communication
"""

import struct
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import time

@dataclass
class UCDRField:
    """Represents a field in ucdr serialized data"""
    name: str
    data_type: str
    offset: int
    size: int
    value: Any
    alignment: int = 4

class UCDRHandler:
    """
    Advanced ucdr (microCDR) Serialization Handler
    Handles ASOA's microCDR serialization format
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.data_types = {
            'float32': {'size': 4, 'alignment': 4, 'unpack': '<f', 'pack': '<f'},
            'float64': {'size': 8, 'alignment': 8, 'unpack': '<d', 'pack': '<d'},
            'int32': {'size': 4, 'alignment': 4, 'unpack': '<i', 'pack': '<i'},
            'uint32': {'size': 4, 'alignment': 4, 'unpack': '<I', 'pack': '<I'},
            'int16': {'size': 2, 'alignment': 2, 'unpack': '<h', 'pack': '<h'},
            'uint16': {'size': 2, 'alignment': 2, 'unpack': '<H', 'pack': '<H'},
            'int8': {'size': 1, 'alignment': 1, 'unpack': '<b', 'pack': '<b'},
            'uint8': {'size': 1, 'alignment': 1, 'unpack': '<B', 'pack': '<B'},
            'string': {'size': -1, 'alignment': 4, 'unpack': None, 'pack': None}
        }
        
    def parse_ucdr_data(self, data: bytes, schema: Dict[str, str]) -> Dict[str, UCDRField]:
        """
        Parse ucdr serialized data according to schema
        """
        fields = {}
        offset = 0
        
        try:
            for field_name, field_type in schema.items():
                if field_type not in self.data_types:
                    self.logger.warning(f"Unknown data type: {field_type}")
                    continue
                
                type_info = self.data_types[field_type]
                
                # Handle alignment
                if type_info['alignment'] > 1:
                    offset = self._align_offset(offset, type_info['alignment'])
                
                # Handle string type (variable length)
                if field_type == 'string':
                    if offset + 4 <= len(data):
                        string_length = struct.unpack('<I', data[offset:offset+4])[0]
                        offset += 4
                        if offset + string_length <= len(data):
                            string_value = data[offset:offset+string_length].decode('utf-8', errors='ignore')
                            fields[field_name] = UCDRField(
                                name=field_name,
                                data_type=field_type,
                                offset=offset - 4,  # Include length field
                                size=4 + string_length,
                                value=string_value,
                                alignment=type_info['alignment']
                            )
                            offset += string_length
                else:
                    # Handle fixed-size types
                    if offset + type_info['size'] <= len(data):
                        value = struct.unpack(type_info['unpack'], data[offset:offset+type_info['size']])[0]
                        fields[field_name] = UCDRField(
                            name=field_name,
                            data_type=field_type,
                            offset=offset,
                            size=type_info['size'],
                            value=value,
                            alignment=type_info['alignment']
                        )
                        offset += type_info['size']
            
            return fields
            
        except Exception as e:
            self.logger.error(f"Failed to parse ucdr data: {e}")
            return {}
    
    def serialize_ucdr_data(self, fields: Dict[str, UCDRField]) -> bytes:
        """
        Serialize fields back to ucdr format
        """
        try:
            # Sort fields by offset
            sorted_fields = sorted(fields.values(), key=lambda x: x.offset)
            
            # Calculate total size
            total_size = 0
            for field in sorted_fields:
                if field.data_type == 'string':
                    total_size += 4 + len(field.value.encode('utf-8'))
                else:
                    total_size += field.size
                total_size = self._align_offset(total_size, field.alignment)
            
            # Create buffer
            buffer = bytearray(total_size)
            offset = 0
            
            for field in sorted_fields:
                # Handle alignment
                if field.alignment > 1:
                    offset = self._align_offset(offset, field.alignment)
                
                # Serialize field
                if field.data_type == 'string':
                    # Write string length
                    string_bytes = field.value.encode('utf-8')
                    struct.pack_into('<I', buffer, offset, len(string_bytes))
                    offset += 4
                    # Write string data
                    buffer[offset:offset+len(string_bytes)] = string_bytes
                    offset += len(string_bytes)
                else:
                    type_info = self.data_types[field.data_type]
                    struct.pack_into(type_info['pack'], buffer, offset, field.value)
                    offset += field.size
            
            return bytes(buffer)
            
        except Exception as e:
            self.logger.error(f"Failed to serialize ucdr data: {e}")
            return b''
    
    def modify_temperature_in_ucdr(self, data: bytes, new_temperature: float) -> Optional[bytes]:
        """
        Modify temperature value in ucdr serialized data
        """
        try:
            # ASOA temperature schema based on t_simple.hpp
            temperature_schema = {
                'topic_id': 'uint32',
                'topic_name': 'string',
                'temperature_value': 'float32',
                'accuracy': 'float32'
            }
            
            # Parse the data
            fields = self.parse_ucdr_data(data, temperature_schema)
            
            if 'temperature_value' in fields:
                # Modify temperature value
                fields['temperature_value'].value = new_temperature
                
                # Reserialize
                return self.serialize_ucdr_data(fields)
            else:
                # Try to find temperature data in raw bytes
                return self._find_and_modify_temperature_raw(data, new_temperature)
                
        except Exception as e:
            self.logger.error(f"Failed to modify temperature in ucdr: {e}")
            return None
    
    def _find_and_modify_temperature_raw(self, data: bytes, new_temperature: float) -> Optional[bytes]:
        """
        Find and modify temperature value in raw bytes
        """
        try:
            # Look for temperature topic ID (15) followed by float value
            temp_topic_id = 15
            modified_data = bytearray(data)
            
            for i in range(len(data) - 8):
                if i + 4 <= len(data):
                    potential_topic_id = struct.unpack('<I', data[i:i+4])[0]
                    if potential_topic_id == temp_topic_id:
                        # Found temperature data, modify the value
                        if i + 8 <= len(data):
                            temp_bytes = struct.pack('<f', new_temperature)
                            modified_data[i+4:i+8] = temp_bytes
                            self.logger.info(f"Modified temperature at offset {i+4}: {new_temperature}°C")
                            return bytes(modified_data)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to find and modify temperature raw: {e}")
            return None
    
    def extract_temperature_from_ucdr(self, data: bytes) -> Optional[float]:
        """
        Extract temperature value from ucdr serialized data
        """
        try:
            # For the test data we created, the temperature is at a specific offset
            # In real ASOA data, we need to parse the ucdr structure properly
            
            # Try structured parsing first
            temperature_schema = {
                'topic_id': 'uint32',
                'topic_name': 'string',
                'temperature_value': 'float32',
                'accuracy': 'float32'
            }
            
            fields = self.parse_ucdr_data(data, temperature_schema)
            if 'temperature_value' in fields:
                return fields['temperature_value'].value
            
            # Fallback to raw search for temperature topic ID (15)
            temp_topic_id = 15
            for i in range(len(data) - 8):
                if i + 4 <= len(data):
                    potential_topic_id = struct.unpack('<I', data[i:i+4])[0]
                    if potential_topic_id == temp_topic_id:
                        if i + 8 <= len(data):
                            return struct.unpack('<f', data[i+4:i+8])[0]
            
            # If we created the data ourselves, temperature should be at offset 12 (after topic_id and name)
            if len(data) >= 16:
                # Skip topic_id (4 bytes) and name length + name
                offset = 4
                if offset + 4 <= len(data):
                    name_length = struct.unpack('<I', data[offset:offset+4])[0]
                    offset += 4 + name_length
                    if offset + 4 <= len(data):
                        return struct.unpack('<f', data[offset:offset+4])[0]
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract temperature from ucdr: {e}")
            return None
    
    def validate_ucdr_integrity(self, data: bytes, schema: Dict[str, str]) -> bool:
        """
        Validate ucdr serialized data integrity
        """
        try:
            fields = self.parse_ucdr_data(data, schema)
            
            # Check if all required fields are present
            for field_name in schema.keys():
                if field_name not in fields:
                    self.logger.warning(f"Missing required field: {field_name}")
                    return False
            
            # Check for reasonable values
            for field_name, field in fields.items():
                if field.data_type == 'float32' or field.data_type == 'float64':
                    if not (-1000.0 <= field.value <= 1000.0):  # Reasonable range for temperature
                        self.logger.warning(f"Temperature value out of reasonable range: {field.value}")
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to validate ucdr integrity: {e}")
            return False
    
    def _align_offset(self, offset: int, alignment: int) -> int:
        """
        Align offset to specified alignment boundary
        """
        if alignment <= 1:
            return offset
        return (offset + alignment - 1) & ~(alignment - 1)
    
    def get_ucdr_size(self, schema: Dict[str, str]) -> int:
        """
        Calculate size of ucdr serialized data for given schema
        """
        total_size = 0
        
        for field_type in schema.values():
            if field_type in self.data_types:
                type_info = self.data_types[field_type]
                if type_info['size'] > 0:  # Fixed size
                    total_size = self._align_offset(total_size, type_info['alignment'])
                    total_size += type_info['size']
                else:  # Variable size (string)
                    total_size = self._align_offset(total_size, type_info['alignment'])
                    total_size += 4  # Length field
        
        return total_size
    
    def create_temperature_ucdr(self, temperature: float, accuracy: float = 0.1) -> bytes:
        """
        Create ucdr serialized temperature data
        """
        try:
            # Create temperature data structure
            topic_id = 15
            topic_name = "Temp"
            
            # Calculate sizes
            name_bytes = topic_name.encode('utf-8')
            name_length = len(name_bytes)
            
            # Total size: topic_id(4) + name_length(4) + name + temperature(4) + accuracy(4)
            total_size = 4 + 4 + name_length + 4 + 4
            
            # Create buffer
            buffer = bytearray(total_size)
            offset = 0
            
            # Write topic_id
            struct.pack_into('<I', buffer, offset, topic_id)
            offset += 4
            
            # Write name length and name
            struct.pack_into('<I', buffer, offset, name_length)
            offset += 4
            buffer[offset:offset+name_length] = name_bytes
            offset += name_length
            
            # Write temperature value
            struct.pack_into('<f', buffer, offset, temperature)
            offset += 4
            
            # Write accuracy
            struct.pack_into('<f', buffer, offset, accuracy)
            
            return bytes(buffer)
            
        except Exception as e:
            self.logger.error(f"Failed to create temperature ucdr: {e}")
            return b''
