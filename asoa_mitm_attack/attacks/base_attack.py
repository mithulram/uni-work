#!/usr/bin/env python3
"""
Base Attack Class
Abstract base class for all MITM attacks
"""

from abc import ABC, abstractmethod
from utils.logger import setup_logger

class BaseAttack(ABC):
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.logger = setup_logger(f'attack_{name.lower()}', level='INFO')
        self.packets_processed = 0
        
    @abstractmethod
    def modify_temperature(self, original_temp):
        """Modify temperature value - must be implemented by subclasses"""
        pass
        
    @abstractmethod
    def get_attack_parameters(self):
        """Get attack-specific parameters - must be implemented by subclasses"""
        pass
        
    def process_packet(self, packet_data):
        """Process a packet and return modified data"""
        try:
            import struct
            
            if len(packet_data) < 4:
                self.logger.warning("⚠️ Packet too short, cannot modify")
                return packet_data
                
            # Extract original temperature (first 4 bytes, little-endian float)
            original_temp = struct.unpack('<f', packet_data[:4])[0]
            
            # Modify temperature using attack-specific logic
            modified_temp = self.modify_temperature(original_temp)
            
            # Create modified packet
            modified_packet = struct.pack('<f', modified_temp) + packet_data[4:]
            
            # Update statistics
            self.packets_processed += 1
            
            self.logger.debug(f"📦 {self.name}: {original_temp:.1f}°C → {modified_temp:.1f}°C")
            
            return modified_packet
            
        except Exception as e:
            self.logger.error(f"❌ Packet processing error: {e}")
            return packet_data
            
    def get_statistics(self):
        """Get attack statistics"""
        return {
            'name': self.name,
            'description': self.description,
            'packets_processed': self.packets_processed,
            'parameters': self.get_attack_parameters()
        }
        
    def reset_statistics(self):
        """Reset attack statistics"""
        self.packets_processed = 0
        self.logger.info(f"📊 {self.name} statistics reset")
        
    def print_statistics(self):
        """Print current attack statistics"""
        stats = self.get_statistics()
        
        self.logger.info(f"📊 {self.name} Statistics:")
        self.logger.info(f"   Description: {stats['description']}")
        self.logger.info(f"   Packets Processed: {stats['packets_processed']}")
        
        params = stats['parameters']
        if params:
            self.logger.info(f"   Parameters: {params}")
            
    def validate_parameters(self):
        """Validate attack parameters - can be overridden by subclasses"""
        return True
        
    def get_attack_info(self):
        """Get comprehensive attack information"""
        return {
            'name': self.name,
            'description': self.description,
            'parameters': self.get_attack_parameters(),
            'statistics': self.get_statistics(),
            'valid': self.validate_parameters()
        }
