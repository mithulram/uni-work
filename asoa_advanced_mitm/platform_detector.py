#!/usr/bin/env python3
"""
Platform Detector - Cross-Platform ASOA MITM Support
Detects operating system and provides platform-specific packet interception methods
"""

import platform
import subprocess
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import os
import sys

@dataclass
class PlatformInfo:
    """Platform information for ASOA MITM"""
    os_name: str
    os_version: str
    architecture: str
    kernel_version: str
    packet_filter_method: str
    requires_root: bool
    supported_features: List[str]

class PlatformDetector:
    """
    Cross-Platform Detection for ASOA MITM
    Detects OS and provides platform-specific capabilities
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.platform_info = None
        self._detect_platform()
        
    def _detect_platform(self):
        """
        Detect current platform and capabilities
        """
        try:
            system = platform.system()
            version = platform.version()
            arch = platform.machine()
            kernel = platform.release()
            
            if system == "Darwin":  # macOS
                self.platform_info = PlatformInfo(
                    os_name="macOS",
                    os_version=version,
                    architecture=arch,
                    kernel_version=kernel,
                    packet_filter_method="PF",
                    requires_root=True,
                    supported_features=["PF_Redirect", "ARP_Spoofing", "ASOA_Proxy"]
                )
            elif system == "Linux":
                self.platform_info = PlatformInfo(
                    os_name="Linux",
                    os_version=version,
                    architecture=arch,
                    kernel_version=kernel,
                    packet_filter_method="NFQUEUE",
                    requires_root=True,
                    supported_features=["NFQUEUE", "ARP_Spoofing", "ASOA_Inline"]
                )
            elif system == "Windows":
                self.platform_info = PlatformInfo(
                    os_name="Windows",
                    os_version=version,
                    architecture=arch,
                    kernel_version=kernel,
                    packet_filter_method="WinDivert",
                    requires_root=True,
                    supported_features=["WinDivert", "ARP_Spoofing", "ASOA_Proxy"]
                )
            else:
                self.platform_info = PlatformInfo(
                    os_name=system,
                    os_version=version,
                    architecture=arch,
                    kernel_version=kernel,
                    packet_filter_method="Unknown",
                    requires_root=True,
                    supported_features=[]
                )
            
            self.logger.info(f"Detected platform: {self.platform_info.os_name} {self.platform_info.os_version}")
            self.logger.info(f"Packet filter method: {self.platform_info.packet_filter_method}")
            
        except Exception as e:
            self.logger.error(f"Failed to detect platform: {e}")
            self.platform_info = PlatformInfo(
                os_name="Unknown",
                os_version="Unknown",
                architecture="Unknown",
                kernel_version="Unknown",
                packet_filter_method="Unknown",
                requires_root=True,
                supported_features=[]
            )
    
    def get_platform_info(self) -> PlatformInfo:
        """
        Get current platform information
        """
        return self.platform_info
    
    def is_macos(self) -> bool:
        """
        Check if running on macOS
        """
        return self.platform_info.os_name == "macOS"
    
    def is_linux(self) -> bool:
        """
        Check if running on Linux
        """
        return self.platform_info.os_name == "Linux"
    
    def is_windows(self) -> bool:
        """
        Check if running on Windows
        """
        return self.platform_info.os_name == "Windows"
    
    def is_raspberry_pi(self) -> bool:
        """
        Check if running on Raspberry Pi
        """
        if not self.is_linux():
            return False
        
        try:
            # Check for Raspberry Pi specific files
            if os.path.exists("/proc/device-tree/model"):
                with open("/proc/device-tree/model", "r") as f:
                    model = f.read().strip()
                    return "Raspberry Pi" in model
            return False
        except Exception:
            return False
    
    def check_root_privileges(self) -> bool:
        """
        Check if running with root privileges
        """
        try:
            if self.is_windows():
                # Windows: Check for admin privileges
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                # Unix-like systems: Check if EUID is 0
                return os.geteuid() == 0
        except Exception as e:
            self.logger.error(f"Failed to check root privileges: {e}")
            return False
    
    def get_network_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available network interfaces
        """
        interfaces = {}
        
        try:
            if self.is_macos():
                interfaces = self._get_macos_interfaces()
            elif self.is_linux():
                interfaces = self._get_linux_interfaces()
            elif self.is_windows():
                interfaces = self._get_windows_interfaces()
            
            self.logger.info(f"Found {len(interfaces)} network interfaces")
            return interfaces
            
        except Exception as e:
            self.logger.error(f"Failed to get network interfaces: {e}")
            return {}
    
    def _get_macos_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """
        Get network interfaces on macOS
        """
        interfaces = {}
        
        try:
            # Use ifconfig command
            result = subprocess.run(['ifconfig'], capture_output=True, text=True)
            if result.returncode == 0:
                current_interface = None
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Interface name
                    if not line.startswith('\t'):
                        current_interface = line.split(':')[0]
                        interfaces[current_interface] = {
                            'name': current_interface,
                            'ip_address': None,
                            'mac_address': None,
                            'status': 'down'
                        }
                    elif current_interface and line.startswith('\t'):
                        # Parse interface details
                        if 'inet ' in line:
                            ip = line.split('inet ')[1].split(' ')[0]
                            interfaces[current_interface]['ip_address'] = ip
                        elif 'ether ' in line:
                            mac = line.split('ether ')[1].split(' ')[0]
                            interfaces[current_interface]['mac_address'] = mac
                        elif 'status: active' in line:
                            interfaces[current_interface]['status'] = 'up'
            
            return interfaces
            
        except Exception as e:
            self.logger.error(f"Failed to get macOS interfaces: {e}")
            return {}
    
    def _get_linux_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """
        Get network interfaces on Linux
        """
        interfaces = {}
        
        try:
            # Use ip command
            result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
            if result.returncode == 0:
                current_interface = None
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Interface number and name
                    if line[0].isdigit():
                        parts = line.split(': ')
                        if len(parts) >= 2:
                            current_interface = parts[1].split('@')[0]  # Remove @alias
                            interfaces[current_interface] = {
                                'name': current_interface,
                                'ip_address': None,
                                'mac_address': None,
                                'status': 'down'
                            }
                    elif current_interface and 'link/ether' in line:
                        mac = line.split('link/ether ')[1].split(' ')[0]
                        interfaces[current_interface]['mac_address'] = mac
                    elif current_interface and 'inet ' in line:
                        ip = line.split('inet ')[1].split('/')[0]
                        interfaces[current_interface]['ip_address'] = ip
                        interfaces[current_interface]['status'] = 'up'
            
            return interfaces
            
        except Exception as e:
            self.logger.error(f"Failed to get Linux interfaces: {e}")
            return {}
    
    def _get_windows_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """
        Get network interfaces on Windows
        """
        interfaces = {}
        
        try:
            # Use ipconfig command
            result = subprocess.run(['ipconfig', '/all'], capture_output=True, text=True)
            if result.returncode == 0:
                current_interface = None
                
                for line in result.stdout.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Interface name
                    if 'adapter' in line.lower() and ':' in line:
                        current_interface = line.split(':')[0].strip()
                        interfaces[current_interface] = {
                            'name': current_interface,
                            'ip_address': None,
                            'mac_address': None,
                            'status': 'down'
                        }
                    elif current_interface and 'IPv4' in line and ':' in line:
                        ip = line.split(':')[1].strip()
                        if ip and ip != '(Preferred)':
                            interfaces[current_interface]['ip_address'] = ip
                            interfaces[current_interface]['status'] = 'up'
                    elif current_interface and 'Physical Address' in line and ':' in line:
                        mac = line.split(':')[1].strip()
                        interfaces[current_interface]['mac_address'] = mac
            
            return interfaces
            
        except Exception as e:
            self.logger.error(f"Failed to get Windows interfaces: {e}")
            return {}
    
    def get_default_gateway(self) -> Optional[str]:
        """
        Get default gateway IP address
        """
        try:
            if self.is_macos():
                return self._get_macos_gateway()
            elif self.is_linux():
                return self._get_linux_gateway()
            elif self.is_windows():
                return self._get_windows_gateway()
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get default gateway: {e}")
            return None
    
    def _get_macos_gateway(self) -> Optional[str]:
        """
        Get default gateway on macOS
        """
        try:
            result = subprocess.run(['route', '-n', 'get', 'default'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'gateway:' in line:
                        return line.split('gateway:')[1].strip()
            return None
        except Exception:
            return None
    
    def _get_linux_gateway(self) -> Optional[str]:
        """
        Get default gateway on Linux
        """
        try:
            result = subprocess.run(['ip', 'route', 'show', 'default'], capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'default via' in line:
                        return line.split('default via ')[1].split(' ')[0]
            return None
        except Exception:
            return None
    
    def _get_windows_gateway(self) -> Optional[str]:
        """
        Get default gateway on Windows
        """
        try:
            result = subprocess.run(['route', 'print'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for i, line in enumerate(lines):
                    if '0.0.0.0' in line and '0.0.0.0' in line:
                        parts = line.split()
                        if len(parts) >= 4:
                            return parts[2]
            return None
        except Exception:
            return None
    
    def check_packet_filter_support(self) -> bool:
        """
        Check if packet filtering is supported on current platform
        """
        try:
            if self.is_macos():
                # Check if PF is available
                result = subprocess.run(['pfctl', '-s', 'info'], capture_output=True)
                return result.returncode == 0
            elif self.is_linux():
                # Check if iptables and NFQUEUE are available
                result1 = subprocess.run(['iptables', '--version'], capture_output=True)
                result2 = subprocess.run(['modprobe', 'nfnetlink_queue'], capture_output=True)
                return result1.returncode == 0 and result2.returncode == 0
            elif self.is_windows():
                # Check if WinDivert is available (would need to be installed)
                return False  # WinDivert not included by default
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check packet filter support: {e}")
            return False
    
    def get_platform_capabilities(self) -> Dict[str, Any]:
        """
        Get comprehensive platform capabilities
        """
        capabilities = {
            'platform': self.platform_info.os_name,
            'version': self.platform_info.os_version,
            'architecture': self.platform_info.architecture,
            'packet_filter_method': self.platform_info.packet_filter_method,
            'requires_root': self.platform_info.requires_root,
            'has_root_privileges': self.check_root_privileges(),
            'supports_packet_filtering': self.check_packet_filter_support(),
            'is_raspberry_pi': self.is_raspberry_pi(),
            'supported_features': self.platform_info.supported_features,
            'network_interfaces': len(self.get_network_interfaces()),
            'default_gateway': self.get_default_gateway()
        }
        
        return capabilities
    
    def validate_platform_for_asoa_mitm(self) -> Tuple[bool, List[str]]:
        """
        Validate if current platform supports ASOA MITM
        """
        issues = []
        
        # Check root privileges
        if not self.check_root_privileges():
            issues.append("Root privileges required")
        
        # Check platform-specific requirements
        if self.is_macos():
            # macOS can use scapy for packet manipulation without PF
            pass
        elif self.is_linux():
            # Check packet filtering support for Linux
            if not self.check_packet_filter_support():
                issues.append("Packet filtering not supported on Linux")
        elif self.is_windows():
            issues.append("Windows support not implemented")
        else:
            issues.append(f"Unsupported platform: {self.platform_info.os_name}")
        
        return len(issues) == 0, issues
