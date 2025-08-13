#!/usr/bin/env python3
"""
ASOA Protocol Analyzer - Advanced ASOA Communication Protocol Analysis
Targets real ASOA messaging system on UDP port 7400 with ucdr serialization
"""

import struct
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time

class ASOAMessageType(Enum):
    """ASOA Message Types based on protocol analysis"""
    SERVICE_DISCOVERY = 0x01
    GUARANTEE_DATA = 0x02
    REQUIREMENT_REQUEST = 0x03
    ACKNOWLEDGMENT = 0x04
    HEARTBEAT = 0x05
    ERROR = 0x06
    TEMPERATURE_DATA = 0x10
    SENSOR_FUSION = 0x11
    OBSTACLE_DATA = 0x12

@dataclass
class ASOAPacketHeader:
    """ASOA Packet Header Structure"""
    magic: bytes  # Magic bytes (likely "ASOA")
    version: int  # Protocol version
    message_type: ASOAMessageType
    service_id: int  # Source service ID
    target_service_id: int  # Destination service ID
    sequence_number: int
    payload_length: int
    checksum: int
    timestamp: int

@dataclass
class ASOATemperatureData:
    """Temperature data structure within ASOA messages"""
    topic_id: int
    topic_name: str
    temperature_value: float
    accuracy: float
    timestamp: int

class ASOAProtocolAnalyzer:
    """
    Advanced ASOA Protocol Analyzer
    Handles real ASOA communication protocol analysis
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.known_services = {
            1: "SensorModule",
            2: "Dashboard", 
            3: "Cerebrum",
            4: "DynamicModule",
            5: "Radar"
        }
        self.message_patterns = {}
        self.temperature_locations = []
        
    def analyze_packet(self, raw_data: bytes) -> Optional[Dict[str, Any]]:
        """
        Analyze raw ASOA packet and extract structured information
        """
        try:
            if len(raw_data) < 32:  # Minimum ASOA header size
                return None
                
            # Parse ASOA header
            header = self._parse_header(raw_data[:32])
            if not header:
                return None
                
            # Extract payload
            payload = raw_data[32:32+header.payload_length]
            
            # Analyze based on message type
            analysis = {
                'header': header,
                'payload': payload,
                'message_type': header.message_type,
                'source_service': self.known_services.get(header.service_id, f"Unknown-{header.service_id}"),
                'target_service': self.known_services.get(header.target_service_id, f"Unknown-{header.target_service_id}"),
                'timestamp': header.timestamp,
                'sequence': header.sequence_number
            }
            
            # Special handling for temperature data
            if header.message_type == ASOAMessageType.GUARANTEE_DATA:
                temp_data = self._extract_temperature_data(payload)
                if temp_data:
                    analysis['temperature_data'] = temp_data
                    analysis['contains_temperature'] = True
                    
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze ASOA packet: {e}")
            return None
    
    def _parse_header(self, header_data: bytes) -> Optional[ASOAPacketHeader]:
        """
        Parse ASOA packet header
        """
        try:
            # ASOA header structure (based on protocol analysis)
            # Magic(4) + Version(1) + Type(1) + ServiceID(2) + TargetID(2) + 
            # SeqNum(4) + PayloadLen(4) + Checksum(4) + Timestamp(8)
            
            if len(header_data) < 32:
                return None
                
            magic = header_data[:4]
            if magic != b'ASOA':
                # Try alternative magic bytes
                if magic != b'\x41\x53\x4F\x41':  # ASCII "ASOA"
                    return None
            
            version = header_data[4]
            msg_type = ASOAMessageType(header_data[5])
            service_id = struct.unpack('<H', header_data[6:8])[0]
            target_id = struct.unpack('<H', header_data[8:10])[0]
            seq_num = struct.unpack('<I', header_data[10:14])[0]
            payload_len = struct.unpack('<I', header_data[14:18])[0]
            checksum = struct.unpack('<I', header_data[18:22])[0]
            timestamp = struct.unpack('<Q', header_data[22:30])[0]
            
            return ASOAPacketHeader(
                magic=magic,
                version=version,
                message_type=msg_type,
                service_id=service_id,
                target_service_id=target_id,
                sequence_number=seq_num,
                payload_length=payload_len,
                checksum=checksum,
                timestamp=timestamp
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse ASOA header: {e}")
            return None
    
    def _extract_temperature_data(self, payload: bytes) -> Optional[ASOATemperatureData]:
        """
        Extract temperature data from ucdr serialized payload
        """
        try:
            # Look for temperature topic ID (15) in ucdr data
            # Temperature data structure: topic_id(4) + topic_name + temperature_value(4) + accuracy(4)
            
            # Search for temperature topic ID
            temp_topic_id = 15  # From t_temperature.hpp
            
            # Find temperature data in payload
            for i in range(len(payload) - 8):
                # Check if this could be temperature data
                if i + 4 <= len(payload):
                    potential_topic_id = struct.unpack('<I', payload[i:i+4])[0]
                    if potential_topic_id == temp_topic_id:
                        # Extract temperature value (next 4 bytes after topic_id)
                        if i + 8 <= len(payload):
                            temp_value = struct.unpack('<f', payload[i+4:i+8])[0]
                            
                            # Try to extract accuracy (next 4 bytes)
                            accuracy = 0.0
                            if i + 12 <= len(payload):
                                accuracy = struct.unpack('<f', payload[i+8:i+12])[0]
                            
                            return ASOATemperatureData(
                                topic_id=temp_topic_id,
                                topic_name="Temp",
                                temperature_value=temp_value,
                                accuracy=accuracy,
                                timestamp=int(time.time())
                            )
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to extract temperature data: {e}")
            return None
    
    def identify_service_communication(self, packets: List[bytes]) -> Dict[str, Any]:
        """
        Analyze multiple packets to identify service communication patterns
        """
        service_flows = {}
        
        for packet in packets:
            analysis = self.analyze_packet(packet)
            if analysis:
                flow_key = f"{analysis['source_service']}->{analysis['target_service']}"
                if flow_key not in service_flows:
                    service_flows[flow_key] = []
                service_flows[flow_key].append(analysis)
        
        return service_flows
    
    def detect_temperature_flows(self, packets: List[bytes]) -> List[Dict[str, Any]]:
        """
        Detect temperature data flows in ASOA communication
        """
        temp_flows = []
        
        for packet in packets:
            analysis = self.analyze_packet(packet)
            if analysis and analysis.get('contains_temperature'):
                temp_flows.append(analysis)
        
        return temp_flows
    
    def validate_checksum(self, packet: bytes) -> bool:
        """
        Validate ASOA packet checksum
        """
        try:
            if len(packet) < 32:
                return False
                
            header = self._parse_header(packet[:32])
            if not header:
                return False
            
            # Calculate checksum (excluding checksum field itself)
            data_for_checksum = packet[:18] + packet[22:]
            calculated_checksum = self._calculate_checksum(data_for_checksum)
            
            return calculated_checksum == header.checksum
            
        except Exception as e:
            self.logger.error(f"Failed to validate checksum: {e}")
            return False
    
    def _calculate_checksum(self, data: bytes) -> int:
        """
        Calculate ASOA packet checksum
        """
        checksum = 0
        for i in range(0, len(data), 4):
            chunk = data[i:i+4]
            if len(chunk) == 4:
                checksum ^= struct.unpack('<I', chunk)[0]
            else:
                # Pad with zeros for incomplete chunks
                padded = chunk + b'\x00' * (4 - len(chunk))
                checksum ^= struct.unpack('<I', padded)[0]
        return checksum
    
    def get_service_mapping(self) -> Dict[int, str]:
        """
        Get current service ID to name mapping
        """
        return self.known_services.copy()
    
    def add_service_mapping(self, service_id: int, service_name: str):
        """
        Add new service mapping discovered during analysis
        """
        self.known_services[service_id] = service_name
        self.logger.info(f"Added service mapping: {service_id} -> {service_name}")
