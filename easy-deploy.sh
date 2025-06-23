#!/bin/bash

# 🚀 DEWATA MOTOR - EASY DEPLOYMENT SCRIPT
# Script deployment super mudah untuk server Ubuntu
# Author: Dewata Motor Team
# Repository: https://github.com/weida9/DewataMotorRent

echo "🚀 ==============================================="
echo "   DEWATA MOTOR - EASY DEPLOYMENT SCRIPT"
echo "   Motorcycle Rental Management System"
echo "==============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Script ini harus dijalankan sebagai root (gunakan sudo)"
    exit 1
fi

print_info "Memulai deployment Dewata Motor..."
echo ""

# Check Ubuntu version
print_info "Checking system requirements..."
if ! lsb_release -d | grep -q "Ubuntu"; then
    print_error "Script ini hanya untuk Ubuntu 20.04+ LTS"
    exit 1
fi

print_success "Ubuntu detected"

# Check internet connection
print_info "Checking internet connection..."
if ! ping -c 1 google.com &> /dev/null; then
    print_error "Tidak ada koneksi internet"
    exit 1
fi

print_success "Internet connection OK"

# Install Python3 if not exists
print_info "Checking Python3..."
if ! command -v python3 &> /dev/null; then
    print_info "Installing Python3..."
    apt update
    apt install -y python3 python3-pip
fi

print_success "Python3 ready"

# Download and run main deployment script
print_info "Downloading main deployment script..."
DEPLOY_URL="https://raw.githubusercontent.com/weida9/DewataMotorRent/main/deployment-scripts/deploy.py"

# Create temporary directory
TEMP_DIR="/tmp/dewata-deploy"
mkdir -p $TEMP_DIR
cd $TEMP_DIR

# Download deployment script
if wget -q "$DEPLOY_URL" -O deploy.py; then
    print_success "Deployment script downloaded"
else
    print_error "Gagal download deployment script"
    print_info "Cek koneksi internet dan repository URL"
    exit 1
fi

# Run deployment
print_info "Starting main deployment process..."
echo ""
print_warning "Deployment akan memakan waktu 10-20 menit"
print_warning "Jangan close terminal sampai selesai!"
echo ""

# Run the main deployment script
python3 deploy.py

# Check if deployment was successful
if [ $? -eq 0 ]; then
    echo ""
    print_success "🎉 DEPLOYMENT BERHASIL!"
    echo ""
    echo "🌐 Akses aplikasi di: http://$(curl -s ifconfig.me)"
    echo "🔐 phpMyAdmin di: http://$(curl -s ifconfig.me)/phpmyadmin"
    echo ""
    echo "👤 Default Login:"
    echo "   Superadmin: superadmin / admin123"
    echo "   Admin: admin / admin123"
    echo ""
    print_warning "PENTING: Ganti password default setelah login!"
    echo ""
    print_info "Credentials lengkap tersimpan di: /opt/dewata-motor/CREDENTIALS.json"
    echo ""
else
    echo ""
    print_error "Deployment gagal!"
    print_info "Cek log error di atas untuk troubleshooting"
    exit 1
fi

# Cleanup
cd /
rm -rf $TEMP_DIR

print_success "Cleanup completed"
echo ""
echo "🎉 DEWATA MOTOR SIAP DIGUNAKAN!"
echo "📖 Dokumentasi: https://github.com/weida9/DewataMotorRent"
echo "" 