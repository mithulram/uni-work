#!/usr/bin/env python3
"""
Network Utilities for ASOA MITM Attack
"""

import socket
import subprocess
import platform
import logging
from typing import Optional, Dict, List, Any
import netifaces

def get_default_gateway() -> Optional[str]:
    """
    Get default gateway IP address
    """
    try:
        if platform.system() == "Linux":
            # Use ip route command
            result = subprocess.run(['ip', 'route', 'show', 'default'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'default via' in line:
                        return line.split('default via ')[1].split(' ')[0]
        elif platform.system() == "Darwin":  # macOS
            # Use route command
            result = subprocess.run(['route', '-n', 'get', 'default'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'gateway:' in line:
                        return line.split('gateway:')[1].strip()
        elif platform.system() == "Windows":
            # Use route print command
            result = subprocess.run(['route', 'print'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if '0.0.0.0' in line and '0.0.0.0' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            return parts[2]
        
        return None
        
    except Exception as e:
        logging.error(f"Failed to get default gateway: {e}")
        return None

def get_interface_ip(interface_name: str = None) -> Optional[str]:
    """
    Get IP address of specified interface or default interface
    """
    try:
        if interface_name:
            # Get IP for specific interface
            addrs = netifaces.ifaddresses(interface_name)
            if netifaces.AF_INET in addrs:
                return addrs[netifaces.AF_INET][0]['addr']
        else:
            # Get IP for default interface
            gateways = netifaces.gateways()
            if 'default' in gateways and netifaces.AF_INET in gateways['default']:
                default_interface = gateways['default'][netifaces.AF_INET][1]
                addrs = netifaces.ifaddresses(default_interface)
                if netifaces.AF_INET in addrs:
                    return addrs[netifaces.AF_INET][0]['addr']
        
        return None
        
    except Exception as e:
        logging.error(f"Failed to get interface IP: {e}")
        return None

def get_interface_mac(interface_name: str) -> Optional[str]:
    """
    Get MAC address of specified interface
    """
    try:
        addrs = netifaces.ifaddresses(interface_name)
        if netifaces.AF_LINK in addrs:
            return addrs[netifaces.AF_LINK][0]['addr']
        return None
        
    except Exception as e:
        logging.error(f"Failed to get interface MAC: {e}")
        return None

def get_network_interfaces() -> Dict[str, Dict[str, Any]]:
    """
    Get all network interfaces with their information
    """
    interfaces = {}
    
    try:
        for interface in netifaces.interfaces():
            interface_info = {
                'name': interface,
                'ip_address': None,
                'mac_address': None,
                'netmask': None,
                'status': 'unknown'
            }
            
            try:
                addrs = netifaces.ifaddresses(interface)
                
                # Get IP address
                if netifaces.AF_INET in addrs:
                    interface_info['ip_address'] = addrs[netifaces.AF_INET][0]['addr']
                    interface_info['netmask'] = addrs[netifaces.AF_INET][0]['netmask']
                    interface_info['status'] = 'up'
                
                # Get MAC address
                if netifaces.AF_LINK in addrs:
                    interface_info['mac_address'] = addrs[netifaces.AF_LINK][0]['addr']
                
                interfaces[interface] = interface_info
                
            except Exception as e:
                logging.debug(f"Failed to get info for interface {interface}: {e}")
                continue
        
        return interfaces
        
    except Exception as e:
        logging.error(f"Failed to get network interfaces: {e}")
        return {}

def is_ip_reachable(ip: str, timeout: int = 3) -> bool:
    """
    Check if IP address is reachable
    """
    try:
        # Try TCP connection to port 80 (common)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, 80))
        sock.close()
        return result == 0
        
    except Exception as e:
        logging.debug(f"Failed to check IP reachability for {ip}: {e}")
        return False

def scan_port(ip: str, port: int, timeout: int = 3) -> bool:
    """
    Scan specific port on IP address
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
        
    except Exception as e:
        logging.debug(f"Failed to scan port {port} on {ip}: {e}")
        return False

def get_local_ip() -> Optional[str]:
    """
    Get local IP address
    """
    try:
        # Connect to external address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
        
    except Exception as e:
        logging.error(f"Failed to get local IP: {e}")
        return None

def get_network_range(ip: str, netmask: str = "255.255.255.0") -> str:
    """
    Get network range in CIDR notation
    """
    try:
        # Convert IP and netmask to integers
        ip_parts = [int(x) for x in ip.split('.')]
        mask_parts = [int(x) for x in netmask.split('.')]
        
        # Calculate network address
        network = []
        for i in range(4):
            network.append(ip_parts[i] & mask_parts[i])
        
        # Calculate CIDR prefix
        cidr = sum(bin(x).count('1') for x in mask_parts)
        
        return f"{'.'.join(map(str, network))}/{cidr}"
        
    except Exception as e:
        logging.error(f"Failed to calculate network range: {e}")
        return f"{ip}/24"  # Default to /24

def resolve_hostname(hostname: str) -> Optional[str]:
    """
    Resolve hostname to IP address
    """
    try:
        return socket.gethostbyname(hostname)
    except Exception as e:
        logging.debug(f"Failed to resolve hostname {hostname}: {e}")
        return None

def get_hostname(ip: str) -> Optional[str]:
    """
    Get hostname for IP address
    """
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception as e:
        logging.debug(f"Failed to get hostname for {ip}: {e}")
        return None

def validate_ip_address(ip: str) -> bool:
    """
    Validate IP address format
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def validate_port(port: int) -> bool:
    """
    Validate port number
    """
    return 1 <= port <= 65535

def get_available_ports(start_port: int = 1024, end_port: int = 65535, count: int = 10) -> List[int]:
    """
    Get list of available ports in specified range
    """
    available_ports = []
    
    try:
        for port in range(start_port, end_port + 1):
            if len(available_ports) >= count:
                break
                
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result != 0:  # Port is available
                available_ports.append(port)
        
        return available_ports
        
    except Exception as e:
        logging.error(f"Failed to get available ports: {e}")
        return []

def create_socket(port: int, socket_type: str = "TCP") -> Optional[socket.socket]:
    """
    Create and bind socket to specified port
    """
    try:
        if socket_type.upper() == "TCP":
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:  # UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        sock.bind(('', port))
        return sock
        
    except Exception as e:
        logging.error(f"Failed to create socket on port {port}: {e}")
        return None
