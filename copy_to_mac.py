#!/usr/bin/env python3
"""
Script to copy MITM attack files to Mac
"""

import os
import subprocess
import sys

def copy_files_to_mac():
    """Copy MITM attack files to Mac"""
    
    # Source directory (Pi)
    source_dir = "/home/pi/Documents/Development/asoa_mitm_attack"
    
    # Target directory (Mac) - adjust this path
    target_dir = "/Users/mithul/Desktop/ASOA_Projects/asoa_mitm_attack"
    
    print("🚀 Starting file copy from Pi to Mac...")
    print(f"Source: {source_dir}")
    print(f"Target: {target_dir}")
    
    try:
        # Create tar file
        print("📦 Creating tar file...")
        subprocess.run([
            "tar", "-czf", "mitm_attack_working.tar.gz", 
            "-C", "/home/pi/Documents/Development", "asoa_mitm_attack"
        ], check=True)
        
        print("✅ Tar file created successfully!")
        print("\n📋 Now run these commands on your Mac:")
        print("=" * 50)
        print("1. Copy the tar file:")
        print(f"   scp pi@192.168.1.101:/home/pi/Documents/Development/mitm_attack_working.tar.gz ~/Desktop/")
        print("\n2. Extract the files:")
        print("   cd ~/Desktop")
        print("   tar -xzf mitm_attack_working.tar.gz")
        print("   mv asoa_mitm_attack /Users/mithul/Desktop/ASOA_Projects/")
        print("\n3. Test the files:")
        print("   cd /Users/mithul/Desktop/ASOA_Projects/asoa_mitm_attack")
        print("   python3 -c \"import main; print('Syntax OK')\"")
        print("\n4. Run the attack:")
        print("   sudo python3 main.py --attack constant --target-temp 999.9 --target-ip 192.168.1.101")
        print("=" * 50)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating tar file: {e}")
        return False
    
    return True

if __name__ == "__main__":
    copy_files_to_mac()
