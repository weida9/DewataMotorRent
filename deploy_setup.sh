#!/bin/bash

# Dewata Motor Rental - Ubuntu Server Setup Script
# This script installs MySQL, phpMyAdmin, Python, Apache and other dependencies

set -e  # Exit on any error

echo "=========================================="
echo "  Dewata Motor Rental - Server Setup"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   print_warning "Please run as a regular user with sudo privileges"
   exit 1
fi

# Check if user has sudo privileges
if ! sudo -n true 2>/dev/null; then
    print_error "This script requires sudo privileges"
    exit 1
fi

print_status "Starting Ubuntu server setup for Dewata Motor Rental..."

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
print_status "Installing essential packages..."
sudo apt install -y curl wget git unzip software-properties-common apt-transport-https ca-certificates

# Install Python 3 and pip
print_status "Installing Python 3 and pip..."
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install MySQL Server
print_status "Installing MySQL Server..."
sudo apt install -y mysql-server

# Secure MySQL installation
print_status "Securing MySQL installation..."
print_warning "Please follow the prompts to secure your MySQL installation"
sudo mysql_secure_installation

# Install Apache2
print_status "Installing Apache2 web server..."
sudo apt install -y apache2

# Install PHP and required modules for phpMyAdmin
print_status "Installing PHP and required modules..."
sudo apt install -y php php-mysql php-mbstring php-zip php-gd php-json php-curl libapache2-mod-php

# Install phpMyAdmin
print_status "Installing phpMyAdmin..."
sudo apt install -y phpmyadmin

print_warning "During phpMyAdmin installation:"
print_warning "1. Select 'apache2' as the web server"
print_warning "2. Choose 'Yes' to configure database for phpMyAdmin with dbconfig-common"
print_warning "3. Enter a password for the phpMyAdmin application"

# Enable Apache modules
print_status "Enabling Apache modules..."
sudo a2enmod rewrite
sudo a2enmod php7.4 2>/dev/null || sudo a2enmod php8.1 2>/dev/null || sudo a2enmod php

# Create Apache virtual host for the application
print_status "Creating Apache virtual host..."
sudo tee /etc/apache2/sites-available/dewata-motor.conf > /dev/null <<EOF
<VirtualHost *:80>
    ServerName localhost
    DocumentRoot /var/www/dewata-motor
    
    WSGIDaemonProcess dewata-motor python-path=/var/www/dewata-motor python-home=/var/www/dewata-motor/venv
    WSGIProcessGroup dewata-motor
    WSGIScriptAlias / /var/www/dewata-motor/dewata-motor.wsgi
    
    <Directory /var/www/dewata-motor>
        WSGIApplicationGroup %{GLOBAL}
        Require all granted
    </Directory>
    
    Alias /static /var/www/dewata-motor/static
    <Directory /var/www/dewata-motor/static>
        Require all granted
    </Directory>
    
    ErrorLog \${APACHE_LOG_DIR}/dewata-motor_error.log
    CustomLog \${APACHE_LOG_DIR}/dewata-motor_access.log combined
</VirtualHost>
EOF

# Install mod_wsgi for Flask
print_status "Installing mod_wsgi for Flask applications..."
sudo apt install -y libapache2-mod-wsgi-py3

# Enable the site
print_status "Enabling Apache site..."
sudo a2ensite dewata-motor.conf
sudo a2dissite 000-default.conf

# Create application directory
print_status "Creating application directory..."
sudo mkdir -p /var/www/dewata-motor
sudo chown -R $USER:www-data /var/www/dewata-motor
sudo chmod -R 755 /var/www/dewata-motor

# Create Python virtual environment
print_status "Creating Python virtual environment..."
cd /var/www/dewata-motor
python3 -m venv venv
source venv/bin/activate

# Upgrade pip in virtual environment
print_status "Upgrading pip in virtual environment..."
pip install --upgrade pip

# Install Python requirements
print_status "Installing Python requirements..."
pip install Flask==2.3.3 PyMySQL==1.1.0 Werkzeug==2.3.7 gunicorn

# Create WSGI file
print_status "Creating WSGI configuration file..."
cat > /var/www/dewata-motor/dewata-motor.wsgi <<EOF
#!/usr/bin/python3
import sys
import os

# Add your project directory to sys.path
sys.path.insert(0, "/var/www/dewata-motor/")

# Activate virtual environment
activate_this = '/var/www/dewata-motor/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), dict(__file__=activate_this))

from app import app as application

if __name__ == "__main__":
    application.run()
EOF

# Set proper permissions
print_status "Setting proper permissions..."
sudo chown -R $USER:www-data /var/www/dewata-motor
sudo chmod -R 755 /var/www/dewata-motor
sudo chmod +x /var/www/dewata-motor/dewata-motor.wsgi

# Create uploads directory
mkdir -p /var/www/dewata-motor/static/uploads
sudo chown -R www-data:www-data /var/www/dewata-motor/static/uploads
sudo chmod -R 755 /var/www/dewata-motor/static/uploads

# Setup MySQL database
print_status "Setting up MySQL database..."
print_warning "Please enter your MySQL root password when prompted"

# Create database setup script
cat > /tmp/setup_database.sql <<EOF
CREATE DATABASE IF NOT EXISTS motordewata;
CREATE USER IF NOT EXISTS 'dewata_user'@'localhost' IDENTIFIED BY 'dewata_password_2024';
GRANT ALL PRIVILEGES ON motordewata.* TO 'dewata_user'@'localhost';
FLUSH PRIVILEGES;
EOF

mysql -u root -p < /tmp/setup_database.sql
rm /tmp/setup_database.sql

print_status "Database 'motordewata' created successfully"
print_warning "Database user: dewata_user"
print_warning "Database password: dewata_password_2024"
print_warning "Please change this password in production!"

# Configure UFW firewall
print_status "Configuring UFW firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Apache Full'
sudo ufw allow 3306  # MySQL
sudo ufw --force enable

# Restart services
print_status "Restarting services..."
sudo systemctl restart apache2
sudo systemctl restart mysql
sudo systemctl enable apache2
sudo systemctl enable mysql

# Create deployment script
print_status "Creating deployment helper script..."
cat > /var/www/dewata-motor/deploy.sh <<EOF
#!/bin/bash
# Deployment helper script for Dewata Motor Rental

echo "Deploying Dewata Motor Rental application..."

# Activate virtual environment
source /var/www/dewata-motor/venv/bin/activate

# Install/update requirements
pip install -r requirements.txt

# Set permissions
sudo chown -R $USER:www-data /var/www/dewata-motor
sudo chmod -R 755 /var/www/dewata-motor
sudo chown -R www-data:www-data /var/www/dewata-motor/static/uploads

# Restart Apache
sudo systemctl restart apache2

echo "Deployment completed!"
EOF

chmod +x /var/www/dewata-motor/deploy.sh

# Create backup script
print_status "Creating database backup script..."
cat > /var/www/dewata-motor/backup_database.sh <<EOF
#!/bin/bash
# Database backup script for Dewata Motor Rental

BACKUP_DIR="/var/www/dewata-motor/backups"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="motordewata_backup_\$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p \$BACKUP_DIR

# Create backup
mysqldump -u dewata_user -p dewata_password_2024 motordewata > \$BACKUP_DIR/\$BACKUP_FILE

# Compress backup
gzip \$BACKUP_DIR/\$BACKUP_FILE

echo "Database backup created: \$BACKUP_DIR/\$BACKUP_FILE.gz"

# Clean up old backups (keep only last 7 days)
find \$BACKUP_DIR -name "*.gz" -type f -mtime +7 -delete
EOF

chmod +x /var/www/dewata-motor/backup_database.sh

print_status "=========================================="
print_status "  Setup completed successfully!"
print_status "=========================================="

echo ""
print_status "Next steps:"
echo "1. Copy your application files to: /var/www/dewata-motor/"
echo "2. Import your database schema: mysql -u dewata_user -p motordewata < database_schema.sql"
echo "3. Update app.py database configuration:"
echo "   - HOST: 'localhost'"
echo "   - USER: 'dewata_user'"
echo "   - PASSWORD: 'dewata_password_2024'"
echo "   - DATABASE: 'motordewata'"
echo "4. Run: ./deploy.sh"
echo ""
print_status "Access your application:"
echo "- Application: http://your-server-ip/"
echo "- phpMyAdmin: http://your-server-ip/phpmyadmin/"
echo ""
print_status "Useful commands:"
echo "- Check Apache status: sudo systemctl status apache2"
echo "- Check MySQL status: sudo systemctl status mysql"
echo "- View Apache logs: sudo tail -f /var/log/apache2/dewata-motor_error.log"
echo "- Create database backup: ./backup_database.sh"
echo ""
print_warning "Security recommendations:"
echo "1. Change default database password"
echo "2. Configure SSL/HTTPS"
echo "3. Set up regular backups"
echo "4. Update system regularly"
echo "5. Configure fail2ban for additional security"

print_status "Setup script completed!" 