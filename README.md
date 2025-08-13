# ASOA MITM Attack Demonstration

This repository contains a complete demonstration of Man-in-the-Middle (MITM) attacks on an ASOA (Automotive Service-Oriented Architecture) system.

## 🎯 Project Overview

This project demonstrates:
- **Temperature Sensor**: Generates random temperature values (10-30°C)
- **Dashboard**: Displays received temperature values
- **MITM Attack**: Intercepts and modifies temperature data to 999.9°C

## 📁 Repository Structure

```
├── asoa_demo_my_machine_setup/     # ASOA framework with ECUs
│   ├── ECUs/                       # Electronic Control Units
│   │   ├── SensorModule/           # Temperature sensor service
│   │   ├── Dashboard/              # Display service
│   │   └── Orchestrator/           # Service orchestrator
│   ├── standalone_sensor.cpp       # Standalone temperature sensor
│   ├── standalone_dashboard.cpp    # Standalone dashboard
│   └── simple_local_mitm.py        # Local MITM attack script
├── asoa_mitm_attack/               # Network-level MITM attacks
├── asoa_advanced_mitm/             # Advanced MITM tools
└── setup_asoa.sh                   # Setup script
```

## 🚀 Quick Start

### Prerequisites
- Raspberry Pi (for sensor and dashboard)
- Mac (for MITM attack)
- Python 3.x
- C++ compiler (g++)

### Setup

1. **Clone the repository on your Mac:**
   ```bash
   git clone https://github.com/your-username/uni-work.git
   cd uni-work
   ```

2. **On Raspberry Pi - Run Sensor:**
   ```bash
   cd asoa_demo_my_machine_setup
   g++ -o standalone_sensor standalone_sensor.cpp
   ./standalone_sensor
   ```

3. **On Raspberry Pi - Run Dashboard:**
   ```bash
   cd asoa_demo_my_machine_setup
   g++ -o standalone_dashboard standalone_dashboard.cpp
   ./standalone_dashboard
   ```

4. **On Mac - Run MITM Attack:**
   ```bash
   cd asoa_mitm_attack
   sudo python3 main.py --attack constant --target-temp 999.9 --target-ip <PI_IP>
   ```

## 🎭 Demonstration Flow

1. **Normal Operation**: Dashboard shows random temperatures (10-30°C)
2. **Attack Initiated**: MITM attack starts intercepting traffic
3. **Attack Effect**: Dashboard displays 999.9°C instead of real values
4. **Real-time Visualization**: See the attack happening live

## 🔧 Configuration

### Pi IP Address
Update the target IP in the MITM attack command:
```bash
sudo python3 main.py --attack constant --target-temp 999.9 --target-ip 132.231.14.163
```

### Port Configuration
- Sensor sends to: Port 7401 (MITM interceptor)
- MITM forwards to: Port 7400 (Dashboard)
- Dashboard listens on: Port 7400

## 📊 Expected Output

### Sensor Terminal:
```
🚀 Standalone Temperature Sensor Starting...
📡 Will generate random temperatures between 10-30°C every second
[S] Temperature Sensor: 23.4°C (packet sent to MITM)
[S] Temperature Sensor: 18.7°C (packet sent to MITM)
```

### Dashboard Terminal:
```
🚀 Standalone Dashboard Starting...
📡 Listening for temperature data on UDP port 7400
[R] Dashboard received: 999.9°C (packet #1)
[R] Dashboard received: 999.9°C (packet #2)
```

### MITM Attack Terminal:
```
🎯 Starting MITM Attack...
📦 Intercepted packet #1 from ('127.0.0.1', 12345)
🌡️ Original temperature: 23.4°C
💉 Modified to 999.9°C and forwarded
```

## 🛡️ Security Implications

This demonstration shows:
- **Data Integrity**: How network traffic can be modified
- **Real-time Attacks**: Live interception and modification
- **Automotive Security**: Vulnerabilities in vehicle networks
- **Detection Challenges**: Difficulty in identifying MITM attacks

## 📝 Notes

- The standalone applications bypass ASOA framework issues
- Local MITM works on same machine (Pi)
- Network MITM requires separate machines (Pi + Mac)
- All code is tested and working

## 🔗 Related Files

- `simple_local_mitm.py`: Local packet interception
- `standalone_sensor.cpp`: Temperature generation
- `standalone_dashboard.cpp`: Temperature display
- `main.py`: Network-level MITM attack

## 📞 Support

For issues or questions, please check the individual README files in each directory.
