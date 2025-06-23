#!/bin/bash

# 🚀 DEWATA MOTOR - ONE-CLICK INSTALLER
# Installer super mudah untuk server Ubuntu
# Repository: https://github.com/weida9/DewataMotorRent

clear
echo "🚀 DEWATA MOTOR - ONE-CLICK INSTALLER"
echo "======================================"
echo ""

# Check root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Jalankan dengan sudo: sudo bash install.sh"
    exit 1
fi

echo "📥 Downloading deployment script..."

# Download dan jalankan
curl -sSL https://raw.githubusercontent.com/weida9/DewataMotorRent/main/deployment-scripts/deploy-quick.sh | bash

echo ""
echo "🎉 INSTALASI SELESAI!"
echo ""
echo "🌐 Buka browser dan akses: http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR_SERVER_IP')"
echo "👤 Login: superadmin / admin123"
echo "" 