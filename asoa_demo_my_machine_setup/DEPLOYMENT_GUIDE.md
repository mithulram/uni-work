# ASOA MITM Test System - Deployment Guide

## 🚀 Plug-and-Play Setup for Any Raspberry Pi

This guide makes the ASOA MITM test system completely plug-and-play on any new Raspberry Pi.

## 📦 What You Get

After running the setup script, you'll have:

1. **Automated Installation**: All dependencies installed automatically
2. **Pre-built ECUs**: All services compiled and ready to run
3. **Service Management**: Start/stop/status scripts
4. **Network Monitoring**: Built-in traffic monitoring
5. **MITM Ready**: System configured for UDP port 7400 attacks

## 🔧 One-Time Setup (On New Pi)

### Step 1: Copy Files
```bash
# Copy the entire asoa_demo_my_machine_setup folder to new Pi
scp -r asoa_demo_my_machine_setup/ pi@NEW_PI_IP:/home/pi/Documents/Development/
```

### Step 2: Run Setup Script
```bash
cd ~/Documents/Development/asoa_demo_my_machine_setup
chmod +x install_and_run.sh
./install_and_run.sh
```

### Step 3: Verify Installation
```bash
./status_asoa_system.sh
```

## 🎯 Daily Usage (After Setup)

### Start System
```bash
./start_asoa_system.sh
```

### Check Status
```bash
./status_asoa_system.sh
```

### Test MITM Attack
```bash
./test_mitm_attack.sh
```

### Stop System
```bash
./stop_asoa_system.sh
```

## 🌐 Network Configuration

### Automatic Detection
The system automatically:
- Detects your Pi's IP address
- Configures UDP port 7400
- Sets up service communication

### MITM Attack Parameters
- **Protocol**: UDP (not TCP)
- **Port**: 7400 (not 4451)
- **Target**: Your Pi's IP address
- **Services**: Temperature sensor → Dashboard

## 📊 Monitoring

### Logs Location
```
~/Documents/Development/asoa_demo_my_machine_setup/logs/
├── orchestrator.log
├── SensorModule.log
├── Dashboard.log
├── Radar.log
├── Cerebrum.log
└── DynamicModule.log
```

### Network Activity
```bash
# Monitor UDP traffic
sudo tcpdump -i any -n udp port 7400

# Check active services
sudo netstat -tulpn | grep 7400
```

## 🔍 Troubleshooting

### If Services Don't Start
```bash
# Check logs
tail -f logs/orchestrator.log
tail -f logs/SensorModule.log

# Restart system
./stop_asoa_system.sh
./start_asoa_system.sh
```

### If No Network Activity
```bash
# Check if services are running
./status_asoa_system.sh

# Check firewall
sudo ufw status
```

### If MITM Attack Doesn't Work
1. Verify protocol is UDP (not TCP)
2. Verify port is 7400 (not 4451)
3. Check target IP is correct
4. Ensure both Pi and Mac are on same network

## 📋 Complete Deployment Checklist

- [ ] Copy `asoa_demo_my_machine_setup/` to new Pi
- [ ] Run `./install_and_run.sh`
- [ ] Verify `./status_asoa_system.sh` shows all services
- [ ] Test `./test_mitm_attack.sh` shows UDP traffic
- [ ] Configure MITM attack on Mac for UDP port 7400
- [ ] Test temperature modification

## 🎉 Success Indicators

✅ **System Running**: All 5 ECUs + Orchestrator active
✅ **Network Active**: UDP traffic on port 7400
✅ **Temperature Flowing**: Random values (10-30°C) in logs
✅ **MITM Ready**: Traffic visible in `test_mitm_attack.sh`

## 🔄 Quick Reset

If something goes wrong:
```bash
./stop_asoa_system.sh
pkill -f "asoa_orchestrator"
pkill -f "main"
./start_asoa_system.sh
```

## 📞 Support

If you encounter issues:
1. Check logs in `logs/` directory
2. Run `./status_asoa_system.sh`
3. Verify network connectivity
4. Ensure ASOA libraries are installed

---

**🎯 Result**: Any Raspberry Pi can now run the ASOA MITM test system with just 2 commands!
