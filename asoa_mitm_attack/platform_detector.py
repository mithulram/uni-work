#!/usr/bin/env python3
"""
Platform Detection Module
Detects and handles different operating systems (macOS, Linux)
"""

import sys
import platform
import subprocess
from utils.logger import setup_logger

class PlatformDetector:
    def __init__(self):
        self.logger = setup_logger('platform_detector', level='INFO')
        self._platform = None
        self._detect_platform()
        
    def _detect_platform(self):
        """Detect the current platform"""
        system = platform.system().lower()
        
        if system == "darwin":
            self._platform = "macos"
        elif system == "linux":
            self._platform = "linux"
        else:
            self._platform = "unknown"
            
        self.logger.debug(f"Detected platform: {self._platform}")
        
    def get_platform(self):
        """Get the detected platform"""
        return self._platform
        
    def is_macos(self):
        """Check if running on macOS"""
        return self._platform == "macos"
        
    def is_linux(self):
        """Check if running on Linux"""
        return self._platform == "linux"
        
    def is_supported(self):
        """Check if the platform is supported"""
        return self._platform in ["macos", "linux"]
        
    def get_interface_name(self):
        """Get the default network interface name for the platform"""
        if self.is_macos():
            return "en0"  # Default macOS interface
        elif self.is_linux():
            return "eth0"  # Default Linux interface
        else:
            return "eth0"  # Fallback
            
    def check_requirements(self):
        """Check if platform-specific requirements are met"""
        if self.is_macos():
            return self._check_macos_requirements()
        elif self.is_linux():
            return self._check_linux_requirements()
        else:
            return False, "Unsupported platform"
            
    def _check_macos_requirements(self):
        """Check macOS-specific requirements"""
        try:
            # Check if PF (Packet Filter) is available
            result = subprocess.run(
                ["pfctl", "-s", "info"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                return False, "PF (Packet Filter) not available"
                
            # Check if we can modify PF rules
            result = subprocess.run(
                ["pfctl", "-s", "rules"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                return False, "Cannot access PF rules (need root privileges)"
                
            return True, "macOS requirements met"
            
        except FileNotFoundError:
            return False, "PF (Packet Filter) not found"
        except Exception as e:
            return False, f"macOS requirement check failed: {e}"
            
    def _check_linux_requirements(self):
        """Check Linux-specific requirements"""
        try:
            # Check if iptables is available
            result = subprocess.run(
                ["iptables", "--version"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode != 0:
                return False, "iptables not available"
                
            # Check if NFQUEUE is available
            result = subprocess.run(
                ["iptables", "-A", "INPUT", "-j", "NFQUEUE", "--queue-num", "1"], 
                capture_output=True, 
                text=True
            )
            
            # Clean up the test rule
            subprocess.run(
                ["iptables", "-D", "INPUT", "-j", "NFQUEUE", "--queue-num", "1"], 
                capture_output=True
            )
            
            if result.returncode != 0:
                return False, "NFQUEUE not available"
                
            return True, "Linux requirements met"
            
        except FileNotFoundError:
            return False, "iptables not found"
        except Exception as e:
            return False, f"Linux requirement check failed: {e}"
            
    def get_packet_filter_method(self):
        """Get the appropriate packet filtering method for the platform"""
        if self.is_macos():
            return "pf_redirect"  # macOS uses PF redirect
        elif self.is_linux():
            return "nfqueue"  # Linux uses NFQUEUE
        else:
            return "unknown"
            
    def get_arp_spoof_method(self):
        """Get the appropriate ARP spoofing method for the platform"""
        # Both platforms can use Scapy for ARP spoofing
        return "scapy"
        
    def get_network_interface_info(self):
        """Get information about network interfaces"""
        try:
            if self.is_macos():
                return self._get_macos_interface_info()
            elif self.is_linux():
                return self._get_linux_interface_info()
            else:
                return {}
        except Exception as e:
            self.logger.error(f"Failed to get interface info: {e}")
            return {}
            
    def _get_macos_interface_info(self):
        """Get network interface information on macOS"""
        try:
            result = subprocess.run(
                ["ifconfig"], 
                capture_output=True, 
                text=True
            )
            
            interfaces = {}
            current_interface = None
            
            for line in result.stdout.split('\n'):
                if line and not line.startswith('\t'):
                    current_interface = line.split(':')[0]
                    interfaces[current_interface] = {}
                elif current_interface and line.strip().startswith('inet '):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        interfaces[current_interface]['ip'] = parts[1]
                        
            return interfaces
            
        except Exception as e:
            self.logger.error(f"Failed to get macOS interface info: {e}")
            return {}
            
    def _get_linux_interface_info(self):
        """Get network interface information on Linux"""
        try:
            result = subprocess.run(
                ["ip", "addr", "show"], 
                capture_output=True, 
                text=True
            )
            
            interfaces = {}
            current_interface = None
            
            for line in result.stdout.split('\n'):
                if line.strip().startswith('inet '):
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        ip = parts[1].split('/')[0]
                        if current_interface:
                            interfaces[current_interface] = {'ip': ip}
                elif ':' in line and not line.startswith(' '):
                    current_interface = line.split(':')[1].strip()
                    
            return interfaces
            
        except Exception as e:
            self.logger.error(f"Failed to get Linux interface info: {e}")
            return {}
