# Mac Setup Commands for ASOA MITM Demonstration

## 🚀 **EXACT COMMANDS TO RUN ON YOUR MAC:**

### **Step 1: Clone the Repository**
```bash
cd ~/Desktop
git clone https://github.com/mithulram/uni-work.git
cd uni-work
```

### **Step 2: Install Dependencies**
```bash
# Install Python dependencies for MITM attack
cd asoa_mitm_attack
pip3 install -r requirements.txt

# Install additional dependencies if needed
pip3 install scapy netfilterqueue
```

### **Step 3: Test the MITM Attack Code**
```bash
# Test syntax
python3 -c "import main; print('✅ MITM code syntax OK')"

# Check available attacks
python3 main.py --help
```

### **Step 4: Get Pi's IP Address**
The Pi's IP address is: `132.231.14.163`

### **Step 5: Run the 3-Terminal Demonstration**

#### **Terminal 1 (Pi) - Sensor:**
```bash
# On Pi
cd asoa_demo_my_machine_setup
g++ -o standalone_sensor standalone_sensor.cpp
./standalone_sensor
```

#### **Terminal 2 (Pi) - Dashboard:**
```bash
# On Pi (in new terminal)
cd asoa_demo_my_machine_setup
g++ -o standalone_dashboard standalone_dashboard.cpp
./standalone_dashboard
```

#### **Terminal 3 (Mac) - MITM Attack:**
```bash
# On Mac
cd uni-work/asoa_mitm_attack
sudo python3 main.py --attack constant --target-temp 999.9 --target-ip 132.231.14.163
```

## 🎯 **Expected Results:**

### **Sensor Terminal (Pi):**
```
🚀 Standalone Temperature Sensor Starting...
📡 Will generate random temperatures between 10-30°C every second
[S] Temperature Sensor: 23.4°C (packet sent to MITM)
[S] Temperature Sensor: 18.7°C (packet sent to MITM)
```

### **Dashboard Terminal (Pi):**
```
🚀 Standalone Dashboard Starting...
📡 Listening for temperature data on UDP port 7400
[R] Dashboard received: 999.9°C (packet #1)
[R] Dashboard received: 999.9°C (packet #2)
```

### **MITM Attack Terminal (Mac):**
```
🎯 Starting MITM Attack...
📦 Intercepted packet #1 from (132.231.14.163, 12345)
🌡️ Original temperature: 23.4°C
💉 Modified to 999.9°C and forwarded
```

## 🔧 **Troubleshooting:**

### **If MITM attack fails:**
1. Check Pi's IP: `ping 132.231.14.163`
2. Check firewall settings
3. Try different attack modes: `--attack bias` or `--attack random`

### **If compilation fails:**
```bash
# Install g++ on Pi if needed
sudo apt update && sudo apt install g++ -y
```

## 📋 **Quick Test Commands:**

### **Test Pi Connectivity:**
```bash
# On Mac
ping -c 3 132.231.14.163
```

### **Test Git Repository:**
```bash
# On Mac
git clone https://github.com/mithulram/uni-work.git
ls -la uni-work/
```

## 🎉 **Success Indicators:**
- ✅ Repository cloned successfully
- ✅ MITM code runs without syntax errors
- ✅ Pi responds to ping
- ✅ Dashboard shows 999.9°C during attack
- ✅ Real-time temperature modification visible

**Ready to demonstrate the MITM attack!** 🚀
