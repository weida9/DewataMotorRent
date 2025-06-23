#!/bin/bash

# Quick Deploy Script for Dewata Motor
# Simple one-command deployment for Ubuntu

set -e

REPO_URL="git@github.com:weida9/DewataMotorRent.git"
APP_DIR="/var/www/dewatamotor"

echo "🏍️ Quick Deploy Dewata Motor to Ubuntu Server"
echo "=============================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv mysql-server nginx git curl

# Start services
echo "🚀 Starting services..."
sudo systemctl start mysql nginx
sudo systemctl enable mysql nginx

# Setup MySQL
echo "🗄️ Setting up MySQL..."
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Bambang0912';" || true
sudo mysql -u root -p'Bambang0912' -e "CREATE DATABASE IF NOT EXISTS motordewata;"
sudo mysql -u root -p'Bambang0912' -e "CREATE USER IF NOT EXISTS 'dewatamotor'@'localhost' IDENTIFIED BY 'Bambang0912';" || true
sudo mysql -u root -p'Bambang0912' -e "GRANT ALL PRIVILEGES ON motordewata.* TO 'dewatamotor'@'localhost';"
sudo mysql -u root -p'Bambang0912' -e "FLUSH PRIVILEGES;"

# Create app user
echo "👤 Creating application user..."
sudo adduser --system --group --home $APP_DIR --shell /bin/bash dewatamotor || true

# Clone repository
echo "📥 Cloning repository..."
sudo mkdir -p $APP_DIR
if [ -d "$APP_DIR/DewataMotorRent" ]; then
    cd $APP_DIR/DewataMotorRent
    sudo -u dewatamotor git pull origin main
else
    sudo -u dewatamotor git clone $REPO_URL $APP_DIR/DewataMotorRent
fi

cd $APP_DIR/DewataMotorRent

# Setup Python environment
echo "🐍 Setting up Python environment..."
sudo -u dewatamotor python3 -m venv venv
sudo -u dewatamotor ./venv/bin/pip install --upgrade pip
sudo -u dewatamotor ./venv/bin/pip install -r requirements.txt

# Setup database
echo "🗄️ Setting up database..."
sudo mysql -u root -p'Bambang0912' motordewata < database_schema.sql

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R dewatamotor:www-data $APP_DIR
sudo chmod -R 755 $APP_DIR
sudo mkdir -p $APP_DIR/DewataMotorRent/static/uploads
sudo chmod -R 775 $APP_DIR/DewataMotorRent/static/uploads

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/dewatamotor.service > /dev/null <<EOF
[Unit]
Description=Dewata Motor Flask Application
After=network.target mysql.service

[Service]
Type=exec
User=dewatamotor
Group=www-data
WorkingDirectory=$APP_DIR/DewataMotorRent
Environment=PATH=$APP_DIR/DewataMotorRent/venv/bin
ExecStart=$APP_DIR/DewataMotorRent/venv/bin/python app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable dewatamotor
sudo systemctl start dewatamotor

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/dewatamotor > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    location /static {
        alias $APP_DIR/DewataMotorRent/static;
        expires 1y;
    }
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    client_max_body_size 10M;
}
EOF

sudo ln -sf /etc/nginx/sites-available/dewatamotor /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# Setup basic firewall
echo "🔥 Setting up firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo "Application URL: http://$(hostname -I | awk '{print $1}')"
echo "Default Login: superadmin / admin123"
echo ""
echo "Service Commands:"
echo "- Status: sudo systemctl status dewatamotor"
echo "- Restart: sudo systemctl restart dewatamotor"
echo "- Logs: sudo journalctl -u dewatamotor -f"
echo ""
echo "Next Steps:"
echo "1. Configure your domain name"
echo "2. Setup SSL with: sudo certbot --nginx"
echo "3. Change default passwords"
echo ""
echo "🚀 Dewata Motor is now running!" 