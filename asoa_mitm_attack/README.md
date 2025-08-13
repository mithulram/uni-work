# ASOA MITM Attack System

A comprehensive Man-in-the-Middle (MITM) attack system designed to intercept and modify UDP temperature packets in Automotive Service-Oriented Architecture (ASOA) networks.

## 🎯 Overview

This system demonstrates how an attacker can intercept UDP packets containing temperature data between ASOA ECUs (Electronic Control Units) and modify the values in real-time. The attack targets the communication between SensorModule and Dashboard ECUs on port 7400.

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   MacBook   │    │  Raspberry  │    │   Router    │
│  (Attacker) │◄──►│     Pi      │◄──►│  (Gateway)  │
│             │    │  (Target)   │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │                   │                   │
       └───── ARP Spoof ───┘                   │
       │                   │                   │
       └───── UDP 7400 ────┘                   │
       │                   │                   │
       └─── Intercept & ───┘                   │
           Modify Packets
```

## 📋 Requirements

### System Requirements
- **macOS** (primary) or **Linux** (Raspberry Pi)
- Python 3.7+
- Root/Administrator privileges
- Network access to target devices

### Network Setup
- Attacker (MacBook) and Target (Raspberry Pi) on same network
- Both devices connected via Ethernet to same router/switch
- UDP port 7400 open on target device

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd asoa_mitm_attack
```

### 2. Install Dependencies
```bash
# Install Python dependencies
pip3 install -r requirements.txt

# macOS: Install additional tools (if needed)
brew install pfctl

# Linux: Install additional tools (if needed)
sudo apt-get install iptables netfilter-queue
```

### 3. Verify Installation
```bash
# Check if all dependencies are installed
python3 -c "import scapy, netifaces, psutil; print('✅ Dependencies OK')"
```

## 🎮 Usage

### Basic Usage

#### Constant Temperature Attack
Force all temperature readings to a specific value:
```bash
sudo python3 main.py --attack constant --target-temp 99.9
```

#### Bias Attack
Add a constant offset to all temperature readings:
```bash
sudo python3 main.py --attack bias --bias 10.0
```

#### Manual Target Specification
Specify target IP manually:
```bash
sudo python3 main.py --attack constant --target-ip 192.168.1.100 --target-temp 99.9
```

### Advanced Usage

#### Custom Network Interface
```bash
sudo python3 main.py --attack bias --bias 5.0 --interface en1
```

#### Verbose Logging
```bash
sudo python3 main.py --attack constant --target-temp 99.9 --verbose
```

## 📊 Attack Types

### 1. Constant Temperature Attack
- **Purpose**: Force all temperature readings to a fixed value
- **Use Case**: Demonstrate sensor spoofing
- **Example**: `--attack constant --target-temp 99.9`

### 2. Bias Attack
- **Purpose**: Add/subtract a constant value from all readings
- **Use Case**: Demonstrate sensor calibration tampering
- **Example**: `--attack bias --bias 10.0`

## 🔧 Technical Details

### Packet Format
- **Protocol**: UDP
- **Port**: 7400
- **Data Format**: 4-byte little-endian float (temperature)
- **Example**: `25.3°C` = `0x00 0x00 0xCA 0x41`

### Attack Methods

#### macOS Implementation
- **ARP Spoofing**: Scapy-based ARP cache poisoning
- **Packet Interception**: PF (Packet Filter) redirect to local proxy
- **Packet Modification**: UDP proxy with temperature modification
- **Packet Forwarding**: Modified packets sent to original destination

#### Linux Implementation
- **ARP Spoofing**: Same as macOS
- **Packet Interception**: iptables + NFQUEUE inline modification
- **Packet Modification**: Direct packet modification in kernel space
- **Packet Forwarding**: Automatic forwarding after modification

### Network Discovery
- **Automatic**: Scans network for devices with UDP port 7400 open
- **Raspberry Pi Detection**: Hostname and MAC address pattern matching
- **Manual Override**: `--target-ip` parameter

## 📁 File Structure

```
asoa_mitm_attack/
├── main.py                    # Main attack controller
├── network_discovery.py       # Target discovery module
├── platform_detector.py       # OS detection and requirements
├── mitm_macos.py             # macOS-specific MITM implementation
├── mitm_linux.py             # Linux-specific MITM implementation
├── arp_spoof.py              # ARP spoofing module
├── packet_handler.py         # Packet modification logic
├── attacks/                  # Attack type implementations
│   ├── __init__.py
│   ├── base_attack.py        # Abstract attack base class
│   ├── constant_temp.py      # Constant temperature attack
│   └── bias_attack.py        # Bias attack
├── utils/                    # Utility modules
│   ├── __init__.py
│   ├── logger.py             # Logging utilities
│   └── network_utils.py      # Network helper functions
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔍 Monitoring and Logging

### Real-time Monitoring
The system provides real-time feedback on:
- Network discovery progress
- ARP spoofing status
- Packet interception and modification
- Attack statistics

### Log Files
Logs are automatically created in the `logs/` directory:
- `asoa_mitm_network_*.log` - Network discovery logs
- `asoa_mitm_packets_*.log` - Packet processing logs
- `asoa_mitm_attack_*.log` - Attack-specific logs

### Statistics
```bash
# View attack statistics
python3 -c "
from main import ASOAMITMAttack
attack = ASOAMITMAttack(args)
attack.packet_handler.print_statistics()
"
```

## 🛡️ Security Considerations

### Legal and Ethical Use
⚠️ **WARNING**: This tool is for educational and research purposes only.

- Only use on networks you own or have explicit permission to test
- Do not use against production systems without authorization
- Comply with local laws and regulations
- Use responsibly and ethically

### Safety Features
- Automatic cleanup on exit (Ctrl+C)
- ARP table restoration
- Firewall rule cleanup
- Graceful error handling

## 🐛 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Ensure you're running with root privileges
sudo python3 main.py --attack constant --target-temp 99.9
```

#### Target Not Found
```bash
# Check if target is on the network
ping 192.168.1.100

# Verify UDP port 7400 is open
nc -zu 192.168.1.100 7400
```

#### Dependencies Missing
```bash
# Reinstall dependencies
pip3 install -r requirements.txt

# macOS: Install Scapy
pip3 install scapy

# Linux: Install netfilterqueue
sudo apt-get install python3-netfilterqueue
```

#### Network Interface Issues
```bash
# List available interfaces
ifconfig  # macOS
ip addr   # Linux

# Use specific interface
sudo python3 main.py --attack constant --target-temp 99.9 --interface en0
```

### Debug Mode
```bash
# Enable verbose logging
sudo python3 main.py --attack constant --target-temp 99.9 --verbose
```

## 📈 Performance

### Benchmarks
- **Packet Processing**: ~1000 packets/second
- **Network Discovery**: ~30 seconds for /24 network
- **ARP Spoofing**: Continuous updates every 2 seconds
- **Memory Usage**: ~50MB typical

### Optimization Tips
- Use wired Ethernet for better performance
- Close unnecessary network applications
- Monitor system resources during attack

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd asoa_mitm_attack

# Install development dependencies
pip3 install -r requirements.txt
pip3 install pytest black flake8

# Run tests
pytest tests/

# Format code
black .

# Lint code
flake8 .
```

### Adding New Attack Types
1. Create new attack class in `attacks/` directory
2. Inherit from `BaseAttack`
3. Implement required methods
4. Add to `attacks/__init__.py`
5. Update main.py argument parser

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- ASOA research community
- Scapy development team
- Network security researchers
- Automotive cybersecurity community

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Contact the development team
- Check the troubleshooting section

---

**Remember**: Use this tool responsibly and only for authorized testing purposes! 🔒
