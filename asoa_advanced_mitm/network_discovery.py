#!/usr/bin/env python3
"""
Network Discovery - Advanced ASOA Service Discovery
Discovers ASOA services on the network and identifies communication patterns
"""

import socket
import threading
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
import subprocess
import platform
import ipaddress
import struct
import netifaces

@dataclass
class ASOAService:
    """Represents a discovered ASOA service"""
    ip_address: str
    port: int
    service_name: str
    service_id: int
    mac_address: str
    hostname: str
    last_seen: float
    communication_patterns: List[str]
    temperature_flows: bool

class ASOANetworkDiscovery:
    """
    Advanced ASOA Network Discovery
    Discovers ASOA services and analyzes communication patterns
    """
    
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.discovered_services = {}
        self.scan_results = {}
        self.scan_threads = []
        self.running = False
        
        # ASOA-specific service mappings
        self.asoa_service_ports = {
            7400: "ASOA Internal Communication",
            7400: "ASOA Main Communication (UDP)",
            4452: "ASOA Service Discovery",
            4453: "ASOA Monitoring"
        }
        
        # Known ASOA service patterns
        self.asoa_service_patterns = {
            "SensorModule": ["temperature", "sensor", "fusion"],
            "Dashboard": ["display", "gui", "visualization"],
            "Cerebrum": ["orchestrator", "brain", "control"],
            "DynamicModule": ["dynamic", "rpm", "speed"],
            "Radar": ["radar", "obstacle", "detection"]
        }
        
    def discover_asoa_services(self, network_range: str = None, timeout: int = 30) -> Dict[str, ASOAService]:
        """
        Discover ASOA services on the network
        """
        try:
            self.logger.info("🔍 Starting ASOA service discovery...")
            self.running = True
            
            # Determine network range
            if not network_range:
                network_range = self._get_default_network_range()
            
            self.logger.info(f"Scanning network range: {network_range}")
            
            # First scan localhost for local ASOA services
            self.logger.info("🔍 Scanning localhost for ASOA services...")
            self._scan_localhost()
            
            # Start discovery threads
            self._start_discovery_threads(network_range, timeout)
            
            # Wait for discovery to complete
            start_time = time.time()
            while time.time() - start_time < timeout and self.running:
                time.sleep(1)
            
            self.running = False
            
            # Analyze discovered services
            # self._analyze_discovered_services()  # This method is not needed for basic functionality
            
            self.logger.info(f"✅ Discovery complete. Found {len(self.discovered_services)} ASOA services")
            return self.discovered_services.copy()
            
        except Exception as e:
            self.logger.error(f"Failed to discover ASOA services: {e}")
            return {}
    
    def _get_default_network_range(self) -> str:
        """
        Get default network range for scanning
        """
        try:
            # Get local network interface
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            
            # Extract network prefix
            ip_parts = local_ip.split('.')
            network_range = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0/24"
            
            return network_range
            
        except Exception as e:
            self.logger.warning(f"Failed to get default network range: {e}")
            return "192.168.1.0/24"
    
    def _scan_localhost(self):
        """
        Scan localhost for ASOA services
        """
        try:
            localhost_ips = ["127.0.0.1", "localhost", "::1"]
            
            for ip in localhost_ips:
                for port in self.asoa_service_ports.keys():
                    if self._check_asoa_port(ip, port, 5):  # 5 second timeout for localhost
                        self._analyze_asoa_service(ip, port)
                        
        except Exception as e:
            self.logger.error(f"Failed to scan localhost: {e}")
    
    def _start_discovery_threads(self, network_range: str, timeout: int):
        """
        Start multiple discovery threads for parallel scanning
        """
        try:
            network = ipaddress.IPv4Network(network_range, strict=False)
            ip_list = list(network.hosts())
            
            # Split IPs into chunks for threads
            chunk_size = max(1, len(ip_list) // 10)  # 10 threads max
            chunks = [ip_list[i:i + chunk_size] for i in range(0, len(ip_list), chunk_size)]
            
            for i, chunk in enumerate(chunks):
                thread = threading.Thread(
                    target=self._scan_ip_chunk,
                    args=(chunk, timeout),
                    name=f"ASOA-Scanner-{i}"
                )
                thread.daemon = True
                thread.start()
                self.scan_threads.append(thread)
                
        except Exception as e:
            self.logger.error(f"Failed to start discovery threads: {e}")
    
    def _scan_ip_chunk(self, ip_list: List[ipaddress.IPv4Address], timeout: int):
        """
        Scan a chunk of IP addresses for ASOA services
        """
        for ip in ip_list:
            if not self.running:
                break
                
            ip_str = str(ip)
            
            # Check for ASOA ports
            for port in self.asoa_service_ports.keys():
                if self._check_asoa_port(ip_str, port, timeout):
                    self._analyze_asoa_service(ip_str, port)
    
    def _check_asoa_port(self, ip: str, port: int, timeout: int) -> bool:
        """
        Check if an IP has an ASOA service on the specified port
        """
        try:
            # Check for UDP services (ASOA uses UDP)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(timeout / 10)
            
            # Try to bind to the port to see if it's in use
            try:
                sock.bind((ip, port))
                sock.close()
                return False  # Port is available, no service
            except socket.error:
                # Port is in use, likely an ASOA service
                sock.close()
                self.logger.debug(f"Found ASOA service on {ip}:{port} (UDP)")
                return True
                
        except Exception as e:
            self.logger.debug(f"Connection test failed for {ip}:{port} - {e}")
            return False
    
    def _analyze_asoa_service(self, ip: str, port: int):
        """
        Analyze discovered ASOA service
        """
        try:
            service_key = f"{ip}:{port}"
            
            # Get additional information
            mac_address = self._get_mac_address(ip)
            hostname = self._get_hostname(ip)
            service_info = self._identify_asoa_service(ip, port)
            
            # Check for temperature communication patterns
            has_temperature_flows = self._check_temperature_flows(ip, port)
            
            service = ASOAService(
                ip_address=ip,
                port=port,
                service_name=service_info.get('name', 'Unknown'),
                service_id=service_info.get('id', 0),
                mac_address=mac_address,
                hostname=hostname,
                last_seen=time.time(),
                communication_patterns=service_info.get('patterns', []),
                temperature_flows=has_temperature_flows
            )
            
            self.discovered_services[service_key] = service
            self.logger.info(f"📡 Discovered ASOA service: {service.service_name} at {ip}:{port}")
            
        except Exception as e:
            self.logger.error(f"Failed to analyze ASOA service {ip}:{port}: {e}")
    
    def _get_mac_address(self, ip: str) -> str:
        """
        Get MAC address for IP (requires ARP table)
        """
        try:
            if platform.system() == "Linux":
                # Use arp command
                result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 3:
                            return parts[2]
            elif platform.system() == "Darwin":  # macOS
                # Use arp command on macOS
                result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        parts = lines[1].split()
                        if len(parts) >= 2:
                            return parts[1]
            
            return "Unknown"
            
        except Exception as e:
            self.logger.debug(f"Failed to get MAC address for {ip}: {e}")
            return "Unknown"
    
    def _get_hostname(self, ip: str) -> str:
        """
        Get hostname for IP
        """
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except Exception as e:
            self.logger.debug(f"Failed to get hostname for {ip}: {e}")
            return "Unknown"
    
    def _identify_asoa_service(self, ip: str, port: int) -> Dict[str, Any]:
        """
        Identify specific ASOA service type
        """
        try:
            # Try to connect and analyze service behavior
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            if sock.connect_ex((ip, port)) == 0:
                # Send ASOA service discovery probe
                probe_data = self._create_asoa_probe()
                sock.send(probe_data)
                
                # Wait for response
                sock.settimeout(2)
                try:
                    response = sock.recv(1024)
                    service_info = self._parse_asoa_response(response)
                    sock.close()
                    return service_info
                except socket.timeout:
                    sock.close()
                    return self._guess_service_type(ip, port)
            
            sock.close()
            return self._guess_service_type(ip, port)
            
        except Exception as e:
            self.logger.debug(f"Failed to identify ASOA service {ip}:{port}: {e}")
            return self._guess_service_type(ip, port)
    
    def _create_asoa_probe(self) -> bytes:
        """
        Create ASOA service discovery probe
        """
        try:
            # ASOA service discovery packet
            probe = bytearray(32)
            
            # Magic bytes
            probe[0:4] = b'ASOA'
            
            # Version
            probe[4] = 1
            
            # Message type (service discovery)
            probe[5] = 0x01
            
            # Service ID (discovery)
            probe[6:8] = struct.pack('<H', 0)
            
            # Target ID (broadcast)
            probe[8:10] = struct.pack('<H', 0xFFFF)
            
            # Sequence number
            probe[10:14] = struct.pack('<I', int(time.time()))
            
            # Payload length
            probe[14:18] = struct.pack('<I', 0)
            
            # Checksum
            probe[18:22] = struct.pack('<I', 0)
            
            # Timestamp
            probe[22:30] = struct.pack('<Q', int(time.time() * 1000000))
            
            return bytes(probe)
            
        except Exception as e:
            self.logger.error(f"Failed to create ASOA probe: {e}")
            return b''
    
    def _parse_asoa_response(self, response: bytes) -> Dict[str, Any]:
        """
        Parse ASOA service response
        """
        try:
            if len(response) < 32:
                return self._guess_service_type("", 0)
            
            # Parse ASOA header
            magic = response[0:4]
            if magic != b'ASOA':
                return self._guess_service_type("", 0)
            
            service_id = struct.unpack('<H', response[6:8])[0]
            message_type = response[5]
            
            # Map service ID to known services
            service_mapping = {
                1: "SensorModule",
                2: "Dashboard",
                3: "Cerebrum",
                4: "DynamicModule",
                5: "Radar"
            }
            
            service_name = service_mapping.get(service_id, f"Unknown-{service_id}")
            patterns = self.asoa_service_patterns.get(service_name, [])
            
            return {
                'name': service_name,
                'id': service_id,
                'patterns': patterns,
                'message_type': message_type
            }
            
        except Exception as e:
            self.logger.debug(f"Failed to parse ASOA response: {e}")
            return self._guess_service_type("", 0)
    
    def _guess_service_type(self, ip: str, port: int) -> Dict[str, Any]:
        """
        Guess service type based on port and network behavior
        """
        try:
            # Default mapping based on port
            if port == 7400:
                return {
                    'name': 'ASOA-Core',
                    'id': 0,
                    'patterns': ['communication', 'messaging']
                }
            elif port == 4452:
                return {
                    'name': 'ASOA-Discovery',
                    'id': 0,
                    'patterns': ['discovery', 'registration']
                }
            else:
                return {
                    'name': 'ASOA-Unknown',
                    'id': 0,
                    'patterns': []
                }
                
        except Exception as e:
            self.logger.debug(f"Failed to guess service type: {e}")
            return {'name': 'Unknown', 'id': 0, 'patterns': []}
    
    def _check_temperature_flows(self, ip: str, port: int) -> bool:
        """
        Check if service has temperature communication flows
        """
        try:
            # This would require deeper analysis of traffic patterns
                    # ASOA uses UDP port 7400 for main communication
        return port == 7400
            
        except Exception as e:
            self.logger.debug(f"Failed to check temperature flows: {e}")
            return False
    
    def get_temperature_services(self) -> List[ASOAService]:
        """
        Get services that likely handle temperature data
        """
        return [
            service for service in self.discovered_services.values()
            if service.temperature_flows or 'temperature' in service.service_name.lower()
        ]
    
    def get_service_by_name(self, service_name: str) -> Optional[ASOAService]:
        """
        Get service by name
        """
        for service in self.discovered_services.values():
            if service.service_name.lower() == service_name.lower():
                return service
        return None
    
    def get_service_by_ip(self, ip: str) -> Optional[ASOAService]:
        """
        Get service by IP address
        """
        for service in self.discovered_services.values():
            if service.ip_address == ip:
                return service
        return None
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """
        Get summary of discovery results
        """
        total_services = len(self.discovered_services)
        temperature_services = len(self.get_temperature_services())
        
        service_types = {}
        for service in self.discovered_services.values():
            service_type = service.service_name
            if service_type not in service_types:
                service_types[service_type] = 0
            service_types[service_type] += 1
        
        return {
            'total_services': total_services,
            'temperature_services': temperature_services,
            'service_types': service_types,
            'discovery_time': time.time(),
            'network_range': self._get_default_network_range()
        }
    
    def get_network_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all network interfaces with their information
        """
        interfaces = {}
        
        try:
            for interface in netifaces.interfaces():
                interface_info = {
                    'name': interface,
                    'ip_address': None,
                    'mac_address': None,
                    'netmask': None,
                    'status': 'unknown'
                }
                
                try:
                    addrs = netifaces.ifaddresses(interface)
                    
                    # Get IP address
                    if netifaces.AF_INET in addrs:
                        interface_info['ip_address'] = addrs[netifaces.AF_INET][0]['addr']
                        interface_info['netmask'] = addrs[netifaces.AF_INET][0]['netmask']
                        interface_info['status'] = 'up'
                    
                    # Get MAC address
                    if netifaces.AF_LINK in addrs:
                        interface_info['mac_address'] = addrs[netifaces.AF_LINK][0]['addr']
                    
                    interfaces[interface] = interface_info
                    
                except Exception as e:
                    self.logger.debug(f"Failed to get info for interface {interface}: {e}")
                    continue
            
            return interfaces
            
        except Exception as e:
            self.logger.error(f"Failed to get network interfaces: {e}")
            return {}
    
    def stop_discovery(self):
        """
        Stop discovery process
        """
        self.running = False
        for thread in self.scan_threads:
            if thread.is_alive():
                thread.join(timeout=1)
