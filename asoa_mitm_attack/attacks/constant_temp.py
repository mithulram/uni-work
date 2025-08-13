#!/usr/bin/env python3
"""
Constant Temperature Attack
Forces all temperature readings to a specific constant value
"""

from .base_attack import BaseAttack

class ConstantTemperatureAttack(BaseAttack):
    def __init__(self, target_temperature):
        super().__init__(
            name="Constant Temperature Attack",
            description=f"Forces all temperature readings to {target_temperature}°C"
        )
        self.target_temperature = float(target_temperature)
        
    def modify_temperature(self, original_temp):
        """Force temperature to constant value"""
        return self.target_temperature
        
    def get_attack_parameters(self):
        """Get attack parameters"""
        return {
            'target_temperature': self.target_temperature,
            'type': 'constant'
        }
        
    def validate_parameters(self):
        """Validate target temperature"""
        try:
            temp = float(self.target_temperature)
            
            # Check for reasonable temperature range
            if temp < -50 or temp > 150:
                self.logger.warning(f"⚠️ Target temperature {temp}°C is outside normal range")
                
            return True
            
        except (ValueError, TypeError):
            self.logger.error(f"❌ Invalid target temperature: {self.target_temperature}")
            return False
            
    def get_attack_description(self):
        """Get detailed attack description"""
        return f"Constant Temperature Attack: All temperature readings will be forced to {self.target_temperature}°C"
