#!/usr/bin/env python3
"""
Network Discovery Module
Automatically finds Raspberry Pi targets on the network
"""

import socket
import threading
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.logger import setup_logger
import sys

class NetworkDiscovery:
    def __init__(self):
        self.logger = setup_logger('network_discovery', level='INFO')
        self.target_port = 7400  # ASOA UDP port
        self.scan_timeout = 2
        self.max_workers = 50
        
    def get_network_range(self):
        """Get the local network range to scan"""
        try:
            # Get local IP and determine network range
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Extract network prefix (assuming /24)
            ip_parts = local_ip.split('.')
            network_prefix = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}"
            
            return network_prefix
            
        except Exception as e:
            self.logger.error(f"Failed to get network range: {e}")
            return "192.168.1"  # Fallback
            
    def scan_ip(self, ip):
        """Scan a single IP for UDP port 7400"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.scan_timeout)
            
            # Try to connect to UDP port 7400
            result = sock.connect_ex((ip, self.target_port))
            sock.close()
            
            if result == 0:
                return ip
            return None
            
        except Exception:
            return None
            
    def find_raspberry_pi(self):
        """Find Raspberry Pi devices on the network"""
        self.logger.info("🔍 Scanning network for Raspberry Pi devices...")
        
        network_prefix = self.get_network_range()
        self.logger.info(f"🌐 Scanning network: {network_prefix}.0/24")
        
        # Scan IP range
        candidates = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            
            for i in range(1, 255):
                ip = f"{network_prefix}.{i}"
                future = executor.submit(self.scan_ip, ip)
                futures.append((ip, future))
            
            # Collect results
            for ip, future in futures:
                try:
                    result = future.result(timeout=self.scan_timeout + 1)
                    if result:
                        candidates.append(result)
                        self.logger.info(f"✅ Found device with UDP 7400: {result}")
                except Exception:
                    pass
                    
        if not candidates:
            self.logger.warning("⚠️ No devices found with UDP port 7400 open")
            return None
            
        # Try to identify Raspberry Pi among candidates
        raspberry_pi = self._identify_raspberry_pi(candidates)
        
        if raspberry_pi:
            self.logger.info(f"🎯 Identified Raspberry Pi: {raspberry_pi}")
        else:
            self.logger.info(f"📱 Using first candidate: {candidates[0]}")
            raspberry_pi = candidates[0]
            
        return raspberry_pi
        
    def _identify_raspberry_pi(self, candidates):
        """Try to identify which device is actually a Raspberry Pi"""
        for ip in candidates:
            if self._is_raspberry_pi(ip):
                return ip
        return None
        
    def _is_raspberry_pi(self, ip):
        """Check if an IP belongs to a Raspberry Pi"""
        try:
            # Method 1: Check for common Raspberry Pi hostnames
            hostname = socket.gethostbyaddr(ip)[0].lower()
            pi_indicators = ['raspberry', 'raspberrypi', 'pi', 'raspbian']
            
            for indicator in pi_indicators:
                if indicator in hostname:
                    self.logger.info(f"🍓 Found Raspberry Pi by hostname: {hostname}")
                    return True
                    
            # Method 2: Check for common Raspberry Pi MAC prefixes
            mac = self._get_mac_address(ip)
            if mac:
                pi_mac_prefixes = [
                    'b8:27:eb',  # Raspberry Pi Foundation
                    'dc:a6:32',  # Raspberry Pi Foundation (newer)
                    'e4:5f:01',  # Raspberry Pi Foundation
                    '28:cd:c1',  # Raspberry Pi Foundation
                ]
                
                for prefix in pi_mac_prefixes:
                    if mac.lower().startswith(prefix):
                        self.logger.info(f"🍓 Found Raspberry Pi by MAC: {mac}")
                        return True
                        
        except Exception as e:
            self.logger.debug(f"Error identifying device {ip}: {e}")
            
        return False
        
    def _get_mac_address(self, ip):
        """Get MAC address for an IP using ARP"""
        try:
            if sys.platform == "darwin":  # macOS
                cmd = f"arp -n {ip}"
            else:  # Linux
                cmd = f"arp -n {ip}"
                
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ip in line:
                        parts = line.split()
                        for part in parts:
                            if ':' in part and len(part) == 17:  # MAC address format
                                return part
                                
        except Exception:
            pass
            
        return None
        
    def test_connection(self, ip):
        """Test if we can actually communicate with the target"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            
            # Send a test packet
            test_data = b'\x00\x00\x00\x00'  # 4-byte zero temperature
            sock.sendto(test_data, (ip, self.target_port))
            
            # Try to receive response (optional)
            try:
                sock.settimeout(1)
                data, addr = sock.recvfrom(1024)
                self.logger.info(f"📡 Received response from {addr}")
            except socket.timeout:
                self.logger.info(f"📡 No response from {ip} (this is normal)")
                
            sock.close()
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Connection test failed for {ip}: {e}")
            return False
