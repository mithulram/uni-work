#!/usr/bin/env python3
"""
Test script for ASOA MITM Attack
Verifies configuration and network setup
"""

import sys
import os
import subprocess
import netifaces
from scapy.all import *

def test_network_setup():
    """Test network configuration"""
    print("🌐 Testing Network Setup...")
    
    # Get local IP
    try:
        gws = netifaces.gateways()
        gateway_ip = gws['default'][netifaces.AF_INET][0]
        interface = gws['default'][netifaces.AF_INET][1]
        local_ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
        
        print(f"✅ Local IP: {local_ip}")
        print(f"✅ Gateway: {gateway_ip}")
        print(f"✅ Interface: {interface}")
        
        return True, local_ip, gateway_ip, interface
        
    except Exception as e:
        print(f"❌ Network setup failed: {e}")
        return False, None, None, None

def test_scapy():
    """Test scapy functionality"""
    print("\n📡 Testing Scapy...")
    
    try:
        # Test basic scapy functionality
        pkt = IP(dst="8.8.8.8")/ICMP()
        print("✅ Scapy IP/ICMP packet creation works")
        
        # Test ARP functionality
        arp_pkt = ARP(op=1, pdst="192.168.1.1")
        print("✅ Scapy ARP packet creation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Scapy test failed: {e}")
        return False

def test_udp_port_7400():
    """Test UDP port 7400 monitoring"""
    print("\n🎯 Testing UDP Port 7400...")
    
    try:
        # Test if we can create a filter for UDP port 7400
        filter_str = "udp port 7400"
        print(f"✅ UDP filter string: {filter_str}")
        
        # Test if we can sniff (just for a moment)
        print("📡 Testing packet sniffing (5 seconds)...")
        packets = sniff(filter=filter_str, timeout=5, store=1)
        print(f"✅ Sniffed {len(packets)} packets on UDP port 7400")
        
        return True
        
    except Exception as e:
        print(f"❌ UDP port 7400 test failed: {e}")
        return False

def test_arp_spoofing():
    """Test ARP spoofing capability"""
    print("\n🔄 Testing ARP Spoofing...")
    
    try:
        # Test ARP packet creation for spoofing
        target_ip = "192.168.1.100"  # Example target
        gateway_ip = "192.168.1.1"   # Example gateway
        
        # Create spoof packets
        target_to_gateway = ARP(op=2, psrc=gateway_ip, pdst=target_ip)
        gateway_to_target = ARP(op=2, psrc=target_ip, pdst=gateway_ip)
        
        print("✅ ARP spoofing packet creation works")
        print(f"   Target: {target_ip}")
        print(f"   Gateway: {gateway_ip}")
        
        return True
        
    except Exception as e:
        print(f"❌ ARP spoofing test failed: {e}")
        return False

def test_temperature_modification():
    """Test temperature packet modification"""
    print("\n🌡️ Testing Temperature Modification...")
    
    try:
        import struct
        
        # Create a sample temperature packet
        original_temp = 25.5
        spoofed_temp = 999.9
        
        # Pack temperatures as floats
        original_bytes = struct.pack('f', original_temp)
        spoofed_bytes = struct.pack('f', spoofed_temp)
        
        print(f"✅ Original temperature: {original_temp}°C -> {original_bytes.hex()}")
        print(f"✅ Spoofed temperature: {spoofed_temp}°C -> {spoofed_bytes.hex()}")
        
        # Test unpacking
        unpacked_original = struct.unpack('f', original_bytes)[0]
        unpacked_spoofed = struct.unpack('f', spoofed_bytes)[0]
        
        print(f"✅ Unpacked original: {unpacked_original}°C")
        print(f"✅ Unpacked spoofed: {unpacked_spoofed}°C")
        
        return True
        
    except Exception as e:
        print(f"❌ Temperature modification test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 ASOA MITM Attack Test Suite")
    print("=" * 40)
    
    tests = [
        ("Network Setup", test_network_setup),
        ("Scapy", test_scapy),
        ("UDP Port 7400", test_udp_port_7400),
        ("ARP Spoofing", test_arp_spoofing),
        ("Temperature Modification", test_temperature_modification)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_name == "Network Setup":
                success, local_ip, gateway_ip, interface = test_func()
                if success:
                    passed += 1
            else:
                if test_func():
                    passed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MITM attack should work.")
        print("\n🚀 Ready to run MITM attack:")
        print("   sudo python3 main.py --attack temperature-spoof --target-ip <PI_IP> --target-temp 999.9")
    else:
        print("⚠️ Some tests failed. Check the issues above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
