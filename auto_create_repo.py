#!/usr/bin/env python3
"""
Automated GitHub Repository Creation Script
"""

import os
import subprocess
import sys
import time

def check_repo_exists():
    """Check if the repository exists"""
    try:
        result = subprocess.run([
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
            "https://github.com/mithulram/uni-work"
        ], capture_output=True, text=True)
        return "200" in result.stdout
    except:
        return False

def create_repo_with_gh():
    """Try to create repository using GitHub CLI"""
    try:
        result = subprocess.run([
            "gh", "repo", "create", "uni-work", 
            "--description", "ASOA MITM Attack Demonstration - Automotive Security Research",
            "--public", "--source=."
        ], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def push_code():
    """Push code to GitHub"""
    try:
        result = subprocess.run([
            "git", "push", "-u", "origin", "main"
        ], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def main():
    print("🚀 Automated GitHub Repository Creation")
    print("=" * 50)
    
    # Check if repository exists
    print("📡 Checking if repository exists...")
    if check_repo_exists():
        print("✅ Repository already exists!")
    else:
        print("❌ Repository doesn't exist yet.")
        print("\n🔧 Creating repository...")
        
        # Try GitHub CLI first
        if create_repo_with_gh():
            print("✅ Repository created successfully with GitHub CLI!")
        else:
            print("❌ Could not create repository automatically.")
            print("\n📋 Please create it manually:")
            print("1. Go to: https://github.com/mithulram")
            print("2. Click 'New' or '+' button")
            print("3. Repository name: uni-work")
            print("4. Description: ASOA MITM Attack Demonstration")
            print("5. Make it Public")
            print("6. DO NOT initialize with README")
            print("7. Click 'Create repository'")
            print("\n⏳ Waiting 30 seconds for you to create it...")
            time.sleep(30)
    
    # Try to push code
    print("\n📤 Pushing code to GitHub...")
    if push_code():
        print("🎉 SUCCESS! Code pushed to GitHub!")
        print("📋 Repository URL: https://github.com/mithulram/uni-work")
        print("\n📥 To clone on your Mac:")
        print("   git clone https://github.com/mithulram/uni-work.git")
        print("   cd uni-work")
        print("\n🚀 Ready to run the MITM demonstration!")
    else:
        print("❌ Failed to push code.")
        print("Please create the repository manually and try again.")

if __name__ == "__main__":
    main()
