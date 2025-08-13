#!/bin/bash

echo "🚀 Setting up ASOA on Raspberry Pi..."

# Step 1: Install dependencies
echo "📦 Installing dependencies..."
sudo apt update
sudo apt install -y build-essential cmake git libreadline-dev

# Step 2: Create development directory
echo "📁 Creating development directory..."
mkdir -p /home/pi/Documents/Development
cd /home/pi/Documents/Development

# Step 3: Clone and build ASOA
echo "🔨 Building ASOA core framework..."
git clone --recursive https://git.rwth-aachen.de/unicaragil/asoa.git
cd asoa
./build.sh aarch64 nocross deb

# Step 4: Install packages
echo "📦 Installing ASOA packages..."
cd build/aarch64/sec/release
sudo dpkg -i --force-architecture *.deb

# Step 5: Fix missing headers
echo "🔧 Fixing missing headers..."
sudo ln -sf /usr/include/asoa_security-0.4.0/globals.h /usr/include/asoa_core-0.4.0/globals.h
sudo ln -sf /usr/include/asoa_security-0.4.0/configuration.h /usr/include/asoa_security-0.4.0/asoa_security_middleware/config/configuration.h

# Step 6: Build examples
echo "🔨 Building ASOA Linux examples..."
cd /home/pi/Documents/Development
cp asoa/build/aarch64/sec/release/asoa_linux_examples-0.4.0.tar.gz .
tar -xvzf asoa_linux_examples-0.4.0.tar.gz
mkdir build && cd build
cmake ..
make -j4

echo "✅ ASOA setup complete!"
echo "🎯 Test with: ./main_a"
