#!/usr/bin/env python3
"""
Bias Attack
Adds a constant bias to all temperature readings
"""

from .base_attack import BaseAttack

class BiasAttack(BaseAttack):
    def __init__(self, bias_value):
        super().__init__(
            name="Bias Attack",
            description=f"Adds {bias_value}°C to all temperature readings"
        )
        self.bias_value = float(bias_value)
        
    def modify_temperature(self, original_temp):
        """Add bias to temperature"""
        return original_temp + self.bias_value
        
    def get_attack_parameters(self):
        """Get attack parameters"""
        return {
            'bias_value': self.bias_value,
            'type': 'bias'
        }
        
    def validate_parameters(self):
        """Validate bias value"""
        try:
            bias = float(self.bias_value)
            
            # Check for reasonable bias range
            if abs(bias) > 100:
                self.logger.warning(f"⚠️ Bias value {bias}°C is very large")
                
            return True
            
        except (ValueError, TypeError):
            self.logger.error(f"❌ Invalid bias value: {self.bias_value}")
            return False
            
    def get_attack_description(self):
        """Get detailed attack description"""
        if self.bias_value > 0:
            return f"Bias Attack: All temperature readings will be increased by {self.bias_value}°C"
        else:
            return f"Bias Attack: All temperature readings will be decreased by {abs(self.bias_value)}°C"
