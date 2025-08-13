#!/usr/bin/env python3
"""
Logging Utility Module
Provides centralized logging functionality for the ASOA MITM attack system
"""

import logging
import sys
import os
from datetime import datetime

def setup_logger(name, level='INFO', log_file=None):
    """
    Setup a logger with consistent formatting
    
    Args:
        name (str): Logger name
        level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Optional log file path
        
    Returns:
        logging.Logger: Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
        
    # Set log level
    logger.setLevel(getattr(logging, level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        try:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
        except Exception as e:
            logger.warning(f"Could not setup file logging: {e}")
            
    return logger

def get_log_file_path(component_name):
    """
    Get a standardized log file path for a component
    
    Args:
        component_name (str): Name of the component
        
    Returns:
        str: Log file path
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    return os.path.join(log_dir, f"asoa_mitm_{component_name}_{timestamp}.log")

def setup_attack_logger(attack_name):
    """
    Setup a logger specifically for attack components
    
    Args:
        attack_name (str): Name of the attack
        
    Returns:
        logging.Logger: Configured logger instance
    """
    log_file = get_log_file_path(attack_name)
    return setup_logger(f"attack_{attack_name}", level='INFO', log_file=log_file)

def setup_network_logger():
    """
    Setup a logger for network-related operations
    
    Returns:
        logging.Logger: Configured logger instance
    """
    log_file = get_log_file_path("network")
    return setup_logger("network", level='INFO', log_file=log_file)

def setup_packet_logger():
    """
    Setup a logger for packet processing
    
    Returns:
        logging.Logger: Configured logger instance
    """
    log_file = get_log_file_path("packets")
    return setup_logger("packets", level='DEBUG', log_file=log_file)

def log_attack_event(logger, event_type, details):
    """
    Log an attack event with standardized format
    
    Args:
        logger (logging.Logger): Logger instance
        event_type (str): Type of event (start, stop, packet, error, etc.)
        details (dict): Event details
    """
    timestamp = datetime.now().isoformat()
    event_data = {
        'timestamp': timestamp,
        'event_type': event_type,
        'details': details
    }
    
    logger.info(f"ATTACK_EVENT: {event_data}")

def log_packet_modification(logger, original_temp, modified_temp, attack_type):
    """
    Log a packet modification event
    
    Args:
        logger (logging.Logger): Logger instance
        original_temp (float): Original temperature
        modified_temp (float): Modified temperature
        attack_type (str): Type of attack performed
    """
    logger.info(f"PACKET_MODIFIED: {original_temp:.1f}°C → {modified_temp:.1f}°C ({attack_type})")

def log_network_discovery(logger, target_ip, method):
    """
    Log network discovery events
    
    Args:
        logger (logging.Logger): Logger instance
        target_ip (str): Discovered target IP
        method (str): Discovery method used
    """
    logger.info(f"TARGET_DISCOVERED: {target_ip} (method: {method})")

def log_error_with_context(logger, error, context):
    """
    Log an error with additional context
    
    Args:
        logger (logging.Logger): Logger instance
        error (Exception): The error that occurred
        context (dict): Additional context information
    """
    logger.error(f"ERROR: {error} | Context: {context}")

def setup_verbose_logging():
    """
    Setup verbose logging for debugging
    
    Returns:
        dict: Dictionary of loggers for different components
    """
    loggers = {}
    
    # Setup loggers for different components
    loggers['main'] = setup_logger('main', level='DEBUG')
    loggers['network'] = setup_logger('network', level='DEBUG')
    loggers['arp'] = setup_logger('arp', level='DEBUG')
    loggers['packets'] = setup_logger('packets', level='DEBUG')
    loggers['mitm'] = setup_logger('mitm', level='DEBUG')
    
    return loggers
