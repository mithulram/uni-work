#!/usr/bin/env python3
"""
Test Script for ASOA Advanced MITM Attack System
Demonstrates the system working with real ASOA demo
"""

import sys
import time
import logging
from typing import Dict, Any

# Import ASOA MITM components
from asoa_protocol_analyzer import ASOAProtocolAnalyzer
from ucdr_handler import UCDRHandler
from asoa_message_modifier import ASOAMessageModifier
from network_discovery import ASOANetworkDiscovery
from platform_detector import PlatformDetector
from utils.logger import setup_logger

def test_platform_detection():
    """Test platform detection functionality"""
    print("🔍 Testing Platform Detection...")
    
    pd = PlatformDetector()
    platform_info = pd.get_platform_info()
    
    print(f"   Platform: {platform_info.os_name}")
    print(f"   Version: {platform_info.os_version}")
    print(f"   Architecture: {platform_info.architecture}")
    print(f"   Packet Filter Method: {platform_info.packet_filter_method}")
    print(f"   Is Raspberry Pi: {pd.is_raspberry_pi()}")
    print(f"   Has Root Privileges: {pd.check_root_privileges()}")
    
    # Validate platform for ASOA MITM
    is_valid, issues = pd.validate_platform_for_asoa_mitm()
    if is_valid:
        print("   ✅ Platform validation passed")
    else:
        print("   ❌ Platform validation failed:")
        for issue in issues:
            print(f"      - {issue}")
    
    return is_valid

def test_network_discovery():
    """Test network discovery functionality"""
    print("\n🔍 Testing Network Discovery...")
    
    nd = ASOANetworkDiscovery()
    
    # Get network interfaces
    interfaces = nd.get_network_interfaces()
    print(f"   Found {len(interfaces)} network interfaces")
    
    for name, info in interfaces.items():
        if info['status'] == 'up':
            print(f"   📡 {name}: {info['ip_address']} ({info['mac_address']})")
    
    # Test service discovery (quick scan)
    print("   Scanning for ASOA services...")
    services = nd.discover_asoa_services(timeout=10)
    
    if services:
        print(f"   ✅ Found {len(services)} ASOA services:")
        for service_key, service in services.items():
            print(f"      📡 {service.service_name} at {service.ip_address}:{service.port}")
            if service.temperature_flows:
                print(f"         🌡️  Temperature flows detected")
    else:
        print("   ⚠️  No ASOA services found (this is expected if ASOA demo is not running)")
    
    return len(services) > 0

def test_ucdr_handling():
    """Test ucdr serialization handling"""
    print("\n🔧 Testing ucdr Handling...")
    
    ucdr = UCDRHandler()
    
    # Create test temperature data
    test_temp = 25.5
    temp_data = ucdr.create_temperature_ucdr(test_temp)
    print(f"   Created temperature ucdr data: {len(temp_data)} bytes")
    
    # Extract temperature from data
    extracted_temp = ucdr.extract_temperature_from_ucdr(temp_data)
    print(f"   Extracted temperature: {extracted_temp}°C")
    
    # Modify temperature
    new_temp = 99.9
    modified_data = ucdr.modify_temperature_in_ucdr(temp_data, new_temp)
    print(f"   Modified temperature to: {new_temp}°C")
    
    # Verify modification
    final_temp = ucdr.extract_temperature_from_ucdr(modified_data)
    print(f"   Final temperature: {final_temp}°C")
    
    success = abs(final_temp - new_temp) < 0.1
    if success:
        print("   ✅ ucdr temperature modification successful")
    else:
        print("   ❌ ucdr temperature modification failed")
    
    return success

def test_asoa_protocol_analyzer():
    """Test ASOA protocol analyzer"""
    print("\n📦 Testing ASOA Protocol Analyzer...")
    
    analyzer = ASOAProtocolAnalyzer()
    
    # Create a mock ASOA packet
    mock_packet = create_mock_asoa_packet()
    print(f"   Created mock ASOA packet: {len(mock_packet)} bytes")
    
    # Analyze packet
    analysis = analyzer.analyze_packet(mock_packet)
    
    if analysis:
        print("   ✅ ASOA packet analysis successful")
        print(f"      Message Type: {analysis['message_type']}")
        print(f"      Source Service: {analysis['source_service']}")
        print(f"      Target Service: {analysis['target_service']}")
        print(f"      Contains Temperature: {analysis.get('contains_temperature', False)}")
        
        if analysis.get('contains_temperature'):
            temp_data = analysis['temperature_data']
            print(f"      Temperature: {temp_data.temperature_value}°C")
    else:
        print("   ❌ ASOA packet analysis failed")
    
    return analysis is not None

def create_mock_asoa_packet():
    """Create a mock ASOA packet for testing"""
    import struct
    
    # ASOA header (32 bytes)
    header = bytearray(32)
    
    # Magic bytes
    header[0:4] = b'ASOA'
    
    # Version
    header[4] = 1
    
    # Message type (GUARANTEE_DATA)
    header[5] = 0x02
    
    # Service ID (SensorModule)
    struct.pack_into('<H', header, 6, 1)
    
    # Target ID (Dashboard)
    struct.pack_into('<H', header, 8, 2)
    
    # Sequence number
    struct.pack_into('<I', header, 10, 12345)
    
    # Payload length (will be set after creating payload)
    payload_length = 0
    
    # Checksum (will be calculated)
    struct.pack_into('<I', header, 18, 0)
    
    # Timestamp
    struct.pack_into('<Q', header, 22, int(time.time() * 1000000))
    
    # Create temperature payload
    ucdr = UCDRHandler()
    payload = ucdr.create_temperature_ucdr(25.5)
    
    # Set payload length
    struct.pack_into('<I', header, 14, len(payload))
    
    # Calculate checksum
    checksum_data = bytes(header[:18]) + bytes(header[22:30]) + payload
    checksum = 0
    for i in range(0, len(checksum_data), 4):
        chunk = checksum_data[i:i+4]
        if len(chunk) == 4:
            checksum ^= struct.unpack('<I', chunk)[0]
        else:
            padded = chunk + b'\x00' * (4 - len(chunk))
            checksum ^= struct.unpack('<I', padded)[0]
    
    struct.pack_into('<I', header, 18, checksum)
    
    # Combine header and payload
    return bytes(header) + payload

def test_message_modifier():
    """Test ASOA message modifier"""
    print("\n🔧 Testing ASOA Message Modifier...")
    
    modifier = ASOAMessageModifier()
    
    # Create mock packet
    mock_packet = create_mock_asoa_packet()
    
    # Test temperature modification
    modified_packet = modifier.modify_asoa_packet(
        mock_packet, 
        'temperature-spoof', 
        target_temperature=99.9
    )
    
    if modified_packet:
        print("   ✅ Message modification successful")
        
        # Get stats
        stats = modifier.get_modification_stats()
        print(f"      Total Packets: {stats['total_packets']}")
        print(f"      Modified Packets: {stats['modified_packets']}")
        print(f"      Temperature Modifications: {stats['temperature_modifications']}")
        
        # Validate modified packet
        is_valid = modifier.validate_modified_packet(modified_packet)
        if is_valid:
            print("      ✅ Modified packet validation passed")
        else:
            print("      ❌ Modified packet validation failed")
    else:
        print("   ❌ Message modification failed")
    
    return modified_packet is not None

def main():
    """Main test function"""
    print("🚀 ASOA Advanced MITM Attack System - Test Suite")
    print("=" * 60)
    
    # Setup logging
    logger = setup_logger("ASOA-Test", "INFO")
    
    tests = [
        ("Platform Detection", test_platform_detection),
        ("Network Discovery", test_network_discovery),
        ("ucdr Handling", test_ucdr_handling),
        ("ASOA Protocol Analyzer", test_asoa_protocol_analyzer),
        ("Message Modifier", test_message_modifier),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n🧪 Running {test_name}...")
            result = test_func()
            results[test_name] = result
            print(f"   {'✅ PASSED' if result else '❌ FAILED'}")
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n   Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("   🎉 All tests passed! ASOA MITM system is ready.")
        print("\n   Next steps:")
        print("   1. Start your ASOA demo (SensorModule, Dashboard)")
        print("   2. Run: sudo python3 main.py --scan-asoa")
        print("   3. Run: sudo python3 main.py --attack temperature-spoof --target-temp 99.9")
    else:
        print("   ⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
