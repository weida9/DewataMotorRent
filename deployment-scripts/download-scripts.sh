#!/bin/bash

# Download All Deployment Scripts for Dewata Motor
# This script downloads all deployment-related scripts to current directory

set -e

REPO_URL="https://raw.githubusercontent.com/weida9/DewataMotorRent/main/deployment-scripts"
SCRIPTS_DIR="dewata-deployment-scripts"

echo "🏍️ Dewata Motor Deployment Scripts Downloader"
echo "============================================="

# Create directory
mkdir -p "$SCRIPTS_DIR"
cd "$SCRIPTS_DIR"

echo "📁 Created directory: $SCRIPTS_DIR"
echo "⬇️  Downloading deployment scripts..."

# Download all scripts
scripts=(
    "deploy.py"
    "deploy-quick.sh"
    "update-app.py"
    "health-check.py"
    "README.md"
    "DEPLOYMENT.md"
)

for script in "${scripts[@]}"; do
    echo "   Downloading $script..."
    if wget -q "$REPO_URL/$script" -O "$script"; then
        echo "   ✅ $script downloaded successfully"
    else
        echo "   ❌ Failed to download $script"
    fi
done

# Make scripts executable
chmod +x *.py *.sh 2>/dev/null || true

echo ""
echo "✅ All scripts downloaded to: $(pwd)"
echo ""
echo "🚀 Usage Examples:"
echo "   Full deployment:     sudo python3 deploy.py"
echo "   Quick deployment:    sudo bash deploy-quick.sh"
echo "   Update application:  sudo python3 update-app.py --backup"
echo "   Health check:        sudo python3 health-check.py"
echo ""
echo "📚 Read README.md and DEPLOYMENT.md for detailed instructions"
echo ""
echo "Happy deploying! 🏍️✨" 