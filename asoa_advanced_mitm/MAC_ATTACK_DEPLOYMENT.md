# ASOA MITM Attack - macOS Plug-and-Play

## 🎯 One-Command Attack System

This makes the MITM attack completely plug-and-play on any Mac.

## 🚀 Quick Start

### Step 1: Copy Attack Files to Mac
```bash
# Copy the attack folder to your Mac
scp -r asoa_advanced_mitm/ user@MAC_IP:/Users/user/Desktop/
```

### Step 2: Run Setup (One-time)
```bash
cd ~/Desktop/asoa_advanced_mitm
sudo ./macos_mitm_plug_and_play.sh
```

### Step 3: Attack (Daily Usage)
```bash
# Quick attack with 999.9°C
./quick_attack.sh

# Attack with custom temperature
./quick_attack.sh 500.0
./quick_attack.sh 1234.5
```

## 🎯 What the Script Does

### Automatic Setup:
✅ **Installs Homebrew** (if needed)
✅ **Installs dependencies** (scapy, tcpdump, dsniff)
✅ **Creates Python virtual environment**
✅ **Installs Python packages** (scapy, netifaces, etc.)
✅ **Scans network** for ASOA devices
✅ **Auto-detects target** Raspberry Pi
✅ **Creates attack scripts**

### Attack Features:
✅ **ARP Spoofing** - Intercepts traffic between Pi and gateway
✅ **UDP Port 7400** - Targets correct ASOA protocol
✅ **Temperature Modification** - Spoofs temperature values
✅ **Packet Injection** - Sends modified packets
✅ **Auto-recovery** - Restores ARP tables on exit

## 📡 Network Discovery

The script automatically:
1. **Scans your network** for devices with UDP port 7400 open
2. **Identifies ASOA devices** (Raspberry Pi)
3. **Sets target IP** automatically
4. **Falls back to manual input** if auto-detection fails

## 🎯 Attack Configuration

- **Protocol**: UDP (correct for ASOA)
- **Port**: 7400 (correct ASOA port)
- **Target**: Auto-detected Raspberry Pi
- **Method**: ARP spoofing + packet modification
- **Payload**: Temperature value spoofing

## 📊 Expected Output

```
🎯 Quick ASOA MITM Attack
Target: 192.168.1.101
Spoofed Temperature: 999.9°C

🎯 Target: 192.168.1.101
🌐 Gateway: 192.168.1.1
🌡️ Spoofed Temperature: 999.9°C
🔄 Starting ARP spoofing...
📡 Starting packet sniffing on UDP port 7400...
📡 Intercepted ASOA packet #1: 192.168.1.101:12345 -> 192.168.1.101:7400
🌡️ Found temperature value: 15.3°C
🌡️ Temperature modified to 999.9°C
💉 Sent modified packet to 192.168.1.101:7400
```

## 🔧 Manual Commands

If you prefer manual control:

```bash
# Activate environment
source mitm_env/bin/activate

# Run attack manually
python3 asoa_mitm_attack.py 192.168.1.101 999.9

# Monitor network
sudo tcpdump -i any -n udp port 7400
```

## 🛑 Stopping the Attack

- **Ctrl+C** - Gracefully stops attack and restores ARP tables
- **Auto-recovery** - ARP tables automatically restored on exit

## 🔍 Troubleshooting

### If No Devices Found:
```bash
# Manual target specification
./quick_attack.sh
# Enter IP when prompted
```

### If Attack Doesn't Work:
1. **Check network**: Ensure Mac and Pi are on same network
2. **Check ASOA**: Ensure Pi is running ASOA services
3. **Check firewall**: Disable Mac firewall temporarily
4. **Check permissions**: Run with sudo

### If No Packets Intercepted:
1. **Verify protocol**: ASOA uses UDP, not TCP
2. **Verify port**: ASOA uses 7400, not 4451
3. **Check traffic**: Run `sudo tcpdump -i any -n udp port 7400`

## 📋 Complete Workflow

### On Raspberry Pi:
```bash
./start_asoa_system.sh
```

### On Mac:
```bash
./quick_attack.sh
```

### Result:
- Pi Dashboard shows original temperatures (10-30°C)
- MITM attack modifies to spoofed temperature (999.9°C)
- Dashboard displays modified temperature

## 🎉 Success Indicators

✅ **Setup Complete**: All dependencies installed
✅ **Target Found**: ASOA device detected
✅ **Attack Running**: ARP spoofing active
✅ **Packets Intercepted**: UDP traffic captured
✅ **Temperature Modified**: Values changed to spoofed temp
✅ **Dashboard Updated**: Pi shows modified values

---

**🎯 Result**: MITM attack is now **one command** on any Mac! 🚀
