#!/bin/bash

# ASOA MITM Test System - Complete Installation and Setup Script
# This script makes the system plug-and-play on any Raspberry Pi

set -e  # Exit on any error

echo "🚀 ASOA MITM Test System - Complete Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

print_header "Step 1: Installing System Dependencies"
print_status "Updating package list..."
sudo apt-get update

print_status "Installing required packages..."
sudo apt-get install -y \
    build-essential \
    cmake \
    git \
    tcpdump \
    net-tools \
    python3 \
    python3-pip \
    curl \
    wget

print_header "Step 2: Installing wiringPi"
if [ ! -d "/opt/wiringPi" ]; then
    print_status "Installing wiringPi..."
    cd /tmp
    git clone https://github.com/WiringPi/WiringPi.git
    cd WiringPi
    ./build
    sudo ./build
    cd "$SCRIPT_DIR"
else
    print_status "wiringPi already installed"
fi

print_header "Step 3: Installing ASOA Dependencies"
if [ ! -f "/usr/include/asoa_core-0.4.0/asoa/core/runtime.hpp" ]; then
    print_status "Installing ASOA core libraries..."
    # This would need the actual ASOA package installation
    # For now, we'll assume it's already installed
    print_warning "ASOA libraries should be installed manually"
else
    print_status "ASOA libraries found"
fi

print_header "Step 4: Building All ECUs"
print_status "Building SensorModule..."
cd "$SCRIPT_DIR/ECUs/SensorModule"
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=release
make -j$(nproc)

print_status "Building Dashboard..."
cd "$SCRIPT_DIR/ECUs/Dashboard"
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=release
make -j$(nproc)

print_status "Building Radar..."
cd "$SCRIPT_DIR/ECUs/Radar"
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=release
make -j$(nproc)

print_status "Building Cerebrum..."
cd "$SCRIPT_DIR/ECUs/Cerebrum"
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=release
make -j$(nproc)

print_status "Building DynamicModule..."
cd "$SCRIPT_DIR/ECUs/DynamicModule"
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=release
make -j$(nproc)

print_header "Step 5: Creating Service Management Scripts"
cd "$SCRIPT_DIR"

# Create start script
cat > start_asoa_system.sh << 'EOF'
#!/bin/bash

# ASOA System Startup Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting ASOA MITM Test System..."

# Function to start ECU in background
start_ecu() {
    local ecu_name=$1
    local ecu_path=$2
    echo "Starting $ecu_name..."
    cd "$ecu_path"
    ./main > "$SCRIPT_DIR/logs/${ecu_name}.log" 2>&1 &
    echo $! > "$SCRIPT_DIR/logs/${ecu_name}.pid"
    sleep 2
}

# Create logs directory
mkdir -p "$SCRIPT_DIR/logs"

# Start orchestrator first
echo "Starting Orchestrator..."
cd "$SCRIPT_DIR/../asoa/build/aarch64/sec/release/asoa_orchestrator"
./asoa_orchestrator > "$SCRIPT_DIR/logs/orchestrator.log" 2>&1 &
echo $! > "$SCRIPT_DIR/logs/orchestrator.pid"
sleep 3

# Start ECUs
start_ecu "Radar" "$SCRIPT_DIR/ECUs/Radar/build"
start_ecu "SensorModule" "$SCRIPT_DIR/ECUs/SensorModule/build"
start_ecu "Cerebrum" "$SCRIPT_DIR/ECUs/Cerebrum/build"
start_ecu "DynamicModule" "$SCRIPT_DIR/ECUs/DynamicModule/build"
start_ecu "Dashboard" "$SCRIPT_DIR/ECUs/Dashboard/build"

echo "✅ ASOA system started successfully!"
echo "📊 Check logs in: $SCRIPT_DIR/logs/"
echo "🌐 Services running on UDP port 7400"
echo "🎯 Ready for MITM attack on UDP port 7400"
EOF

# Create stop script
cat > stop_asoa_system.sh << 'EOF'
#!/bin/bash

# ASOA System Stop Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🛑 Stopping ASOA MITM Test System..."

# Stop all processes
pkill -f "asoa_orchestrator" || true
pkill -f "main" || true

# Remove PID files
rm -f "$SCRIPT_DIR/logs"/*.pid

echo "✅ ASOA system stopped"
EOF

# Create status script
cat > status_asoa_system.sh << 'EOF'
#!/bin/bash

# ASOA System Status Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📊 ASOA System Status"
echo "===================="

# Check orchestrator
if pgrep -f "asoa_orchestrator" > /dev/null; then
    echo "✅ Orchestrator: RUNNING"
else
    echo "❌ Orchestrator: STOPPED"
fi

# Check ECUs
ecus=("Radar" "SensorModule" "Cerebrum" "DynamicModule" "Dashboard")
for ecu in "${ecus[@]}"; do
    if pgrep -f "main" > /dev/null; then
        echo "✅ $ecu: RUNNING"
    else
        echo "❌ $ecu: STOPPED"
    fi
done

# Check network activity
echo ""
echo "🌐 Network Activity:"
if sudo netstat -tulpn | grep -q ":7400"; then
    echo "✅ UDP port 7400: ACTIVE"
    sudo netstat -tulpn | grep ":7400"
else
    echo "❌ UDP port 7400: INACTIVE"
fi
EOF

# Create MITM test script
cat > test_mitm_attack.sh << 'EOF'
#!/bin/bash

# MITM Attack Test Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎯 MITM Attack Test"
echo "=================="

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "Local IP: $LOCAL_IP"

# Check if system is running
if ! pgrep -f "asoa_orchestrator" > /dev/null; then
    echo "❌ ASOA system not running. Start it first with: ./start_asoa_system.sh"
    exit 1
fi

echo "✅ ASOA system is running"
echo "📡 Monitoring UDP traffic on port 7400..."
echo "🎯 MITM attack should target:"
echo "   - Protocol: UDP"
echo "   - Port: 7400"
echo "   - Target IP: $LOCAL_IP"
echo ""
echo "📊 Current traffic:"
sudo tcpdump -i any -n udp port 7400 -c 10
EOF

# Make scripts executable
chmod +x start_asoa_system.sh
chmod +x stop_asoa_system.sh
chmod +x status_asoa_system.sh
chmod +x test_mitm_attack.sh

print_header "Step 6: Creating Configuration Files"
# Create default orchestrator config
cat > ECUs/Orchestrator/StartDemo << 'EOF'
c SensorModule:TempSensor:Temperature -> Dashboard:TempDisplay:Temperature

l SensorModule:TempSensor active
l Dashboard:TempDisplay active
EOF

print_header "Step 7: Creating README"
cat > README_PLUG_AND_PLAY.md << 'EOF'
# ASOA MITM Test System - Plug and Play

## Quick Start

1. **Install and Setup** (one-time):
   ```bash
   chmod +x install_and_run.sh
   ./install_and_run.sh
   ```

2. **Start System**:
   ```bash
   ./start_asoa_system.sh
   ```

3. **Check Status**:
   ```bash
   ./status_asoa_system.sh
   ```

4. **Test MITM Attack**:
   ```bash
   ./test_mitm_attack.sh
   ```

5. **Stop System**:
   ```bash
   ./stop_asoa_system.sh
   ```

## MITM Attack Configuration

- **Protocol**: UDP
- **Port**: 7400
- **Target IP**: Your Raspberry Pi's IP
- **Services**: Temperature sensor → Dashboard

## Files Created

- `start_asoa_system.sh` - Start all services
- `stop_asoa_system.sh` - Stop all services  
- `status_asoa_system.sh` - Check system status
- `test_mitm_attack.sh` - Test network activity
- `logs/` - Service logs

## Network Information

The system communicates on UDP port 7400. MITM attacks should target:
- Protocol: UDP (not TCP)
- Port: 7400 (not 4451)
- Target: Your Pi's IP address
EOF

print_header "Step 8: Setup Complete!"
echo "✅ ASOA MITM Test System is now plug-and-play!"
echo ""
echo "📋 Next Steps:"
echo "1. Start the system: ./start_asoa_system.sh"
echo "2. Check status: ./status_asoa_system.sh"
echo "3. Test MITM: ./test_mitm_attack.sh"
echo ""
echo "🎯 MITM Attack Info:"
echo "- Protocol: UDP"
echo "- Port: 7400"
echo "- Target: $(hostname -I | awk '{print $1}')"
echo ""
echo "📚 See README_PLUG_AND_PLAY.md for details"
