#!/bin/bash

# ASOA MITM Attack Setup for macOS
# Installs all dependencies and prepares the system

echo "🚀 Setting up ASOA MITM Attack for macOS..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

# Install Homebrew if not present
if ! command -v brew &> /dev/null; then
    echo "📦 Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
brew install python3 scapy tcpdump dsniff

# Install Python packages
echo "🐍 Installing Python packages..."
pip3 install scapy

echo "✅ Setup complete!"
echo ""
echo "🎯 To run the MITM attack:"
echo "   sudo python3 simple_mitm_attack.py 192.168.1.101 999.9"
echo ""
echo "📡 To monitor network traffic:"
echo "   sudo tcpdump -i any -n udp port 7400"
