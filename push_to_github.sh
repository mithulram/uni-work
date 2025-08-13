#!/bin/bash

echo "🚀 GitHub Repository Creation and Push Script"
echo "=============================================="

# Check if repository exists
echo "📡 Checking if repository exists..."
if curl -s -o /dev/null -w "%{http_code}" https://github.com/mithulram/uni-work | grep -q "200"; then
    echo "✅ Repository already exists!"
else
    echo "❌ Repository doesn't exist yet."
    echo ""
    echo "🔧 Please create the repository manually:"
    echo "1. Go to: https://github.com/mithulram"
    echo "2. Click 'New' or '+' button"
    echo "3. Repository name: uni-work"
    echo "4. Description: ASOA MITM Attack Demonstration"
    echo "5. Make it Public"
    echo "6. DO NOT initialize with README (we have one)"
    echo "7. Click 'Create repository'"
    echo ""
    echo "⏳ Waiting for repository creation..."
    echo "Press Enter when you've created the repository..."
    read -r
fi

# Push the code
echo ""
echo "📤 Pushing code to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Code pushed to GitHub!"
    echo "📋 Repository URL: https://github.com/mithulram/uni-work"
    echo ""
    echo "📥 To clone on your Mac:"
    echo "   git clone https://github.com/mithulram/uni-work.git"
    echo "   cd uni-work"
    echo ""
    echo "🚀 Ready to run the MITM demonstration!"
else
    echo ""
    echo "❌ Failed to push code. Please check:"
    echo "1. Repository exists on GitHub"
    echo "2. You have write access"
    echo "3. Network connection"
fi
