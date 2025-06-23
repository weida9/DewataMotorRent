#!/bin/bash

# Quick Deployment Script for Dewata Motor
# This script downloads and runs the Python deployment script

set -e

echo "🏍️ Dewata Motor Quick Deployment Script"
echo "========================================"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)" 
   exit 1
fi

# Update system first
echo "📦 Updating system packages..."
apt update

# Install Python3 if not available
if ! command -v python3 &> /dev/null; then
    echo "🐍 Installing Python3..."
    apt install -y python3 python3-pip
fi

# Download and run deployment script
echo "⬇️  Downloading deployment script..."
cd /tmp
wget -O deploy.py https://raw.githubusercontent.com/weida9/DewataMotorRent/main/deployment-scripts/deploy.py

echo "🚀 Starting deployment..."
python3 deploy.py

echo "✅ Quick deployment completed!"
echo "📋 Check the deployment summary above for important information." 