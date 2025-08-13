# 🎯 FINAL ASOA MITM DEMONSTRATION COMMANDS

## ✅ **EVERYTHING IS READY!**

### **Repository**: https://github.com/mithulram/uni-work
### **Pi IP**: 132.231.14.163
### **Status**: All code compiled and ready

---

## 🚀 **3-TERMINAL DEMONSTRATION SETUP**

### **TERMINAL 1 (Pi) - Temperature Sensor:**
```bash
cd /home/pi/Documents/Development/asoa_demo_my_machine_setup
./standalone_sensor
```

### **TERMINAL 2 (Pi) - Dashboard:**
```bash
cd /home/pi/Documents/Development/asoa_demo_my_machine_setup
./standalone_dashboard
```

### **TERMINAL 3 (Mac) - MITM Attack:**
```bash
# First, clone the repository on Mac
cd ~/Desktop
git clone https://github.com/mithulram/uni-work.git
cd uni-work/asoa_mitm_attack

# Install dependencies
pip3 install -r requirements.txt

# Run the attack
sudo python3 main.py --attack constant --target-temp 999.9 --target-ip 132.231.14.163
```

---

## 📊 **EXPECTED OUTPUT**

### **Terminal 1 (Sensor):**
```
🚀 Standalone Temperature Sensor Starting...
📡 Will generate random temperatures between 10-30°C every second
🎯 Will send data to MITM interceptor on UDP port 7401
✅ Socket created successfully
📊 Starting temperature generation...
==========================================
[S] Temperature Sensor: 23.4°C (packet sent to MITM)
[S] Temperature Sensor: 18.7°C (packet sent to MITM)
[S] Temperature Sensor: 25.1°C (packet sent to MITM)
```

### **Terminal 2 (Dashboard):**
```
🚀 Standalone Dashboard Starting...
📡 Listening for temperature data on UDP port 7400
📊 Will display received temperature values
✅ Socket bound successfully to port 7400
📊 Waiting for temperature data...
==========================================
[R] Dashboard received: 999.9°C (packet #1)
[R] Dashboard received: 999.9°C (packet #2)
[R] Dashboard received: 999.9°C (packet #3)
```

### **Terminal 3 (MITM Attack):**
```
🎯 Starting MITM Attack...
🌡️ Target temperature: 999.9°C
📡 Intercepting UDP packets on port 7401...
📦 Intercepted packet #1 from ('127.0.0.1', 12345)
🌡️ Original temperature: 23.4°C
💉 Modified to 999.9°C and forwarded
---
📦 Intercepted packet #2 from ('127.0.0.1', 12346)
🌡️ Original temperature: 18.7°C
💉 Modified to 999.9°C and forwarded
---
```

---

## 🎉 **SUCCESS INDICATORS**

- ✅ **Sensor**: Generates random temperatures (10-30°C)
- ✅ **Dashboard**: Shows 999.9°C instead of real values
- ✅ **MITM**: Intercepts and modifies packets in real-time
- ✅ **Real-time**: See the attack happening live

---

## 🔧 **TROUBLESHOOTING**

### **If Mac can't reach Pi:**
```bash
# Test connectivity
ping -c 3 132.231.14.163
```

### **If MITM attack fails:**
```bash
# Try different attack modes
sudo python3 main.py --attack bias --target-temp 999.9 --target-ip 132.231.14.163
sudo python3 main.py --attack random --target-temp 999.9 --target-ip 132.231.14.163
```

### **If compilation fails:**
```bash
# On Pi
sudo apt update && sudo apt install g++ -y
```

---

## 📋 **QUICK START (All Commands)**

### **On Mac:**
```bash
cd ~/Desktop
git clone https://github.com/mithulram/uni-work.git
cd uni-work/asoa_mitm_attack
pip3 install -r requirements.txt
sudo python3 main.py --attack constant --target-temp 999.9 --target-ip 132.231.14.163
```

### **On Pi (Terminal 1):**
```bash
cd /home/pi/Documents/Development/asoa_demo_my_machine_setup
./standalone_sensor
```

### **On Pi (Terminal 2):**
```bash
cd /home/pi/Documents/Development/asoa_demo_my_machine_setup
./standalone_dashboard
```

---

## 🎯 **DEMONSTRATION GOAL ACHIEVED!**

**You will see:**
1. **Normal operation**: Dashboard shows random temperatures
2. **Attack initiated**: MITM starts intercepting
3. **Attack effect**: Dashboard shows 999.9°C
4. **Real-time visualization**: Live attack demonstration

**🚀 READY TO DEMONSTRATE THE MITM ATTACK!** 🎉
