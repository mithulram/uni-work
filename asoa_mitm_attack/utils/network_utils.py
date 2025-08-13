#!/usr/bin/env python3
"""
Network Utilities Module
Provides network-related helper functions for the ASOA MITM attack system
"""

import socket
import subprocess
import platform
import netifaces
from utils.logger import setup_logger

def get_default_gateway():
    """
    Get the default gateway IP address
    
    Returns:
        str: Default gateway IP address
    """
    try:
        # Method 1: Use netifaces (most reliable)
        gws = netifaces.gateways()
        if 'default' in gws and netifaces.AF_INET in gws['default']:
            return gws['default'][netifaces.AF_INET][0]
            
    except ImportError:
        pass
        
    try:
        # Method 2: Use platform-specific commands
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ["route", "-n", "get", "default"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'gateway:' in line:
                        return line.split(':')[1].strip()
                        
        elif platform.system() == "Linux":
            result = subprocess.run(
                ["ip", "route", "show", "default"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'default via' in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == 'via':
                                return parts[i + 1]
                                
    except Exception as e:
        setup_logger('network_utils').error(f"Error getting default gateway: {e}")
        
    # Fallback: return common default gateway
    return "192.168.1.1"

def get_interface_ip(interface=None):
    """
    Get the IP address of a network interface
    
    Args:
        interface (str): Interface name (optional)
        
    Returns:
        str: IP address of the interface
    """
    try:
        # Method 1: Use netifaces
        if interface:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                return addrs[netifaces.AF_INET][0]['addr']
        else:
            # Get IP of default interface
            gws = netifaces.gateways()
            if 'default' in gws and netifaces.AF_INET in gws['default']:
                default_iface = gws['default'][netifaces.AF_INET][1]
                addrs = netifaces.ifaddresses(default_iface)
                if netifaces.AF_INET in addrs:
                    return addrs[netifaces.AF_INET][0]['addr']
                    
    except ImportError:
        pass
        
    try:
        # Method 2: Use socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
        
    except Exception as e:
        setup_logger('network_utils').error(f"Error getting interface IP: {e}")
        return "127.0.0.1"

def get_interface_mac(interface):
    """
    Get the MAC address of a network interface
    
    Args:
        interface (str): Interface name
        
    Returns:
        str: MAC address of the interface
    """
    try:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_LINK in addrs:
            return addrs[netifaces.AF_LINK][0]['addr']
    except Exception as e:
        setup_logger('network_utils').error(f"Error getting interface MAC: {e}")
        
    return None

def get_network_interfaces():
    """
    Get list of available network interfaces
    
    Returns:
        list: List of interface names
    """
    try:
        return netifaces.interfaces()
    except ImportError:
        # Fallback for systems without netifaces
        if platform.system() == "Darwin":  # macOS
            result = subprocess.run(
                ["ifconfig"], 
                capture_output=True, 
                text=True
            )
            
            interfaces = []
            for line in result.stdout.split('\n'):
                if line and not line.startswith('\t'):
                    interface_name = line.split(':')[0]
                    interfaces.append(interface_name)
            return interfaces
            
        elif platform.system() == "Linux":
            result = subprocess.run(
                ["ip", "link", "show"], 
                capture_output=True, 
                text=True
            )
            
            interfaces = []
            for line in result.stdout.split('\n'):
                if ':' in line and not line.startswith(' '):
                    interface_name = line.split(':')[1].strip()
                    interfaces.append(interface_name)
            return interfaces
            
    except Exception as e:
        setup_logger('network_utils').error(f"Error getting network interfaces: {e}")
        return []

def is_ip_reachable(ip, timeout=3):
    """
    Check if an IP address is reachable
    
    Args:
        ip (str): IP address to check
        timeout (int): Timeout in seconds
        
    Returns:
        bool: True if reachable, False otherwise
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((ip, 80))
        return True
    except:
        return False

def get_network_range(ip):
    """
    Get the network range for an IP address (assuming /24)
    
    Args:
        ip (str): IP address
        
    Returns:
        str: Network range (e.g., "192.168.1.0/24")
    """
    try:
        parts = ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    except:
        return "192.168.1.0/24"

def validate_ip_address(ip):
    """
    Validate an IP address format
    
    Args:
        ip (str): IP address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def get_local_ip():
    """
    Get the local IP address (simplified version)
    
    Returns:
        str: Local IP address
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def scan_port(ip, port, timeout=1):
    """
    Scan a specific port on an IP address
    
    Args:
        ip (str): IP address to scan
        port (int): Port to scan
        timeout (int): Timeout in seconds
        
    Returns:
        bool: True if port is open, False otherwise
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

def get_network_info():
    """
    Get comprehensive network information
    
    Returns:
        dict: Network information
    """
    info = {
        'local_ip': get_local_ip(),
        'default_gateway': get_default_gateway(),
        'interfaces': get_network_interfaces(),
        'network_range': get_network_range(get_local_ip())
    }
    
    return info
