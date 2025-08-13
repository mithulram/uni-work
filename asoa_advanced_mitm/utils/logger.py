#!/usr/bin/env python3
"""
Advanced Logging System for ASOA MITM Attack
"""

import logging
import logging.handlers
import os
import sys
from typing import Optional
from datetime import datetime

def setup_logger(name: str, level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Setup comprehensive logging for ASOA MITM attack system
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)  # Always log everything to file
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Failed to setup file logging: {e}")
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

class ASOAMITMLogger:
    """
    Specialized logger for ASOA MITM attack events
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.attack_start_time = None
        self.packet_count = 0
        self.modification_count = 0
        
    def log_attack_start(self, attack_type: str, target: str):
        """
        Log attack start event
        """
        self.attack_start_time = datetime.now()
        self.logger.info(f"🚀 ASOA MITM Attack Started")
        self.logger.info(f"   Type: {attack_type}")
        self.logger.info(f"   Target: {target}")
        self.logger.info(f"   Time: {self.attack_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    def log_attack_stop(self):
        """
        Log attack stop event
        """
        if self.attack_start_time:
            duration = datetime.now() - self.attack_start_time
            self.logger.info(f"🛑 ASOA MITM Attack Stopped")
            self.logger.info(f"   Duration: {duration}")
            self.logger.info(f"   Packets Processed: {self.packet_count}")
            self.logger.info(f"   Modifications: {self.modification_count}")
        
    def log_packet_intercepted(self, packet_type: str, source: str, destination: str):
        """
        Log packet interception event
        """
        self.packet_count += 1
        self.logger.debug(f"📦 Packet Intercepted: {packet_type} | {source} → {destination}")
        
    def log_packet_modified(self, modification_type: str, original_value: str, new_value: str):
        """
        Log packet modification event
        """
        self.modification_count += 1
        self.logger.info(f"🔧 Packet Modified: {modification_type}")
        self.logger.info(f"   Original: {original_value}")
        self.logger.info(f"   Modified: {new_value}")
        
    def log_service_discovered(self, service_name: str, ip: str, port: int):
        """
        Log service discovery event
        """
        self.logger.info(f"📡 Service Discovered: {service_name} at {ip}:{port}")
        
    def log_temperature_flow(self, source: str, temperature: float):
        """
        Log temperature data flow
        """
        self.logger.info(f"🌡️  Temperature Flow: {source} → {temperature}°C")
        
    def log_error(self, error_type: str, error_message: str):
        """
        Log error event
        """
        self.logger.error(f"❌ Error: {error_type} - {error_message}")
        
    def log_warning(self, warning_type: str, warning_message: str):
        """
        Log warning event
        """
        self.logger.warning(f"⚠️  Warning: {warning_type} - {warning_message}")
        
    def log_success(self, success_type: str, success_message: str):
        """
        Log success event
        """
        self.logger.info(f"✅ Success: {success_type} - {success_message}")
        
    def get_attack_stats(self) -> dict:
        """
        Get attack statistics
        """
        return {
            'packets_processed': self.packet_count,
            'modifications_made': self.modification_count,
            'attack_duration': str(datetime.now() - self.attack_start_time) if self.attack_start_time else 'N/A'
        }
