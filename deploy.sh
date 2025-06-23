#!/bin/bash

# Dewata Motor Deployment Script for Ubuntu Server
# Author: Dewata Motor Team
# Version: 1.0.0

set -e  # Exit on any error

# Configuration
REPO_URL="git@github.com:weida9/DewataMotorRent.git"
PROJECT_NAME="DewataMotorRent"
APP_USER="dewatamotor"
APP_DIR="/var/www/dewatamotor"
DOMAIN="your-domain.com"  # Change this to your actual domain
DB_NAME="motordewata"
DB_USER="dewatamotor"
PYTHON_VERSION="3.8"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root. Please run as regular user with sudo privileges."
    fi
}

# Check Ubuntu version
check_ubuntu() {
    if ! grep -q "Ubuntu" /etc/os-release; then
        error "This script is designed for Ubuntu. Other distributions may not work correctly."
    fi
    
    UBUNTU_VERSION=$(lsb_release -rs)
    log "Detected Ubuntu version: $UBUNTU_VERSION"
}

# Update system packages
update_system() {
    log "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y curl wget git software-properties-common apt-transport-https ca-certificates gnupg lsb-release
}

# Install Python and dependencies
install_python() {
    log "Installing Python $PYTHON_VERSION and dependencies..."
    
    # Add deadsnakes PPA for newer Python versions
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    
    # Install Python and related packages
    sudo apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-dev python${PYTHON_VERSION}-venv python3-pip
    
    # Install additional packages
    sudo apt install -y build-essential libssl-dev libffi-dev python3-dev
    
    # Create symlink if needed
    if ! command -v python3 &> /dev/null; then
        sudo ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python3
    fi
}

# Install and configure MySQL
install_mysql() {
    log "Installing and configuring MySQL..."
    
    # Install MySQL Server
    sudo apt install -y mysql-server mysql-client
    
    # Start and enable MySQL
    sudo systemctl start mysql
    sudo systemctl enable mysql
    
    # Secure MySQL installation (automated)
    log "Securing MySQL installation..."
    sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Bambang0912';"
    sudo mysql -e "DELETE FROM mysql.user WHERE User='';"
    sudo mysql -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');"
    sudo mysql -e "DROP DATABASE IF EXISTS test;"
    sudo mysql -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';"
    sudo mysql -e "FLUSH PRIVILEGES;"
    
    # Create application database and user
    log "Creating application database and user..."
    sudo mysql -u root -p'Bambang0912' -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME};"
    sudo mysql -u root -p'Bambang0912' -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY 'Bambang0912';"
    sudo mysql -u root -p'Bambang0912' -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';"
    sudo mysql -u root -p'Bambang0912' -e "FLUSH PRIVILEGES;"
}

# Install Nginx
install_nginx() {
    log "Installing and configuring Nginx..."
    
    sudo apt install -y nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    # Allow Nginx through firewall
    sudo ufw allow 'Nginx Full'
}

# Create application user
create_app_user() {
    log "Creating application user: $APP_USER..."
    
    if ! id "$APP_USER" &>/dev/null; then
        sudo adduser --system --group --home $APP_DIR --shell /bin/bash $APP_USER
        sudo usermod -aG www-data $APP_USER
    else
        log "User $APP_USER already exists"
    fi
}

# Clone and setup application
setup_application() {
    log "Setting up application from repository..."
    
    # Create application directory
    sudo mkdir -p $APP_DIR
    
    # Clone repository
    if [ -d "$APP_DIR/$PROJECT_NAME" ]; then
        log "Repository already exists, pulling latest changes..."
        cd $APP_DIR/$PROJECT_NAME
        sudo -u $APP_USER git pull origin main
    else
        log "Cloning repository..."
        sudo -u $APP_USER git clone $REPO_URL $APP_DIR/$PROJECT_NAME
    fi
    
    cd $APP_DIR/$PROJECT_NAME
    
    # Create virtual environment
    log "Creating Python virtual environment..."
    sudo -u $APP_USER python3 -m venv venv
    
    # Install Python dependencies
    log "Installing Python dependencies..."
    sudo -u $APP_USER ./venv/bin/pip install --upgrade pip
    sudo -u $APP_USER ./venv/bin/pip install -r requirements.txt
    
    # Set proper permissions
    sudo chown -R $APP_USER:www-data $APP_DIR
    sudo chmod -R 755 $APP_DIR
    
    # Create uploads directory with proper permissions
    sudo mkdir -p $APP_DIR/$PROJECT_NAME/static/uploads
    sudo chown -R $APP_USER:www-data $APP_DIR/$PROJECT_NAME/static/uploads
    sudo chmod -R 775 $APP_DIR/$PROJECT_NAME/static/uploads
}

# Setup database
setup_database() {
    log "Setting up database schema..."
    
    cd $APP_DIR/$PROJECT_NAME
    
    # Import database schema
    if [ -f "database_schema.sql" ]; then
        sudo mysql -u root -p'Bambang0912' $DB_NAME < database_schema.sql
        log "Database schema imported successfully"
    else
        warning "database_schema.sql not found, skipping database setup"
    fi
}

# Create systemd service
create_systemd_service() {
    log "Creating systemd service..."
    
    sudo tee /etc/systemd/system/dewatamotor.service > /dev/null <<EOF
[Unit]
Description=Dewata Motor Flask Application
After=network.target mysql.service
Requires=mysql.service

[Service]
Type=exec
User=$APP_USER
Group=www-data
WorkingDirectory=$APP_DIR/$PROJECT_NAME
Environment=PATH=$APP_DIR/$PROJECT_NAME/venv/bin
Environment=FLASK_APP=app.py
Environment=FLASK_ENV=production
ExecStart=$APP_DIR/$PROJECT_NAME/venv/bin/python app.py
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and start service
    sudo systemctl daemon-reload
    sudo systemctl enable dewatamotor
    sudo systemctl start dewatamotor
}

# Configure Nginx
configure_nginx() {
    log "Configuring Nginx..."
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/dewatamotor > /dev/null <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Static files
    location /static {
        alias $APP_DIR/$PROJECT_NAME/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Upload files
    location /static/uploads {
        alias $APP_DIR/$PROJECT_NAME/static/uploads;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Security
    location ~ /\. {
        deny all;
    }
    
    # File size limit
    client_max_body_size 10M;
}
EOF

    # Enable site
    sudo ln -sf /etc/nginx/sites-available/dewatamotor /etc/nginx/sites-enabled/
    
    # Remove default site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    sudo nginx -t
    
    # Restart Nginx
    sudo systemctl reload nginx
}

# Setup SSL with Let's Encrypt
setup_ssl() {
    log "Setting up SSL with Let's Encrypt..."
    
    # Install Certbot
    sudo apt install -y certbot python3-certbot-nginx
    
    # Get SSL certificate
    warning "Please make sure your domain $DOMAIN points to this server before continuing."
    read -p "Continue with SSL setup? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email admin@$DOMAIN
        
        # Setup auto-renewal
        sudo systemctl enable certbot.timer
        sudo systemctl start certbot.timer
    else
        log "Skipping SSL setup. You can run 'sudo certbot --nginx' manually later."
    fi
}

# Setup firewall
setup_firewall() {
    log "Configuring UFW firewall..."
    
    # Enable UFW
    sudo ufw --force enable
    
    # Allow SSH
    sudo ufw allow ssh
    
    # Allow HTTP and HTTPS
    sudo ufw allow 'Nginx Full'
    
    # Allow MySQL only from localhost
    sudo ufw allow from 127.0.0.1 to any port 3306
    
    log "Firewall configured successfully"
}

# Setup log rotation
setup_logs() {
    log "Setting up log rotation..."
    
    # Create log directory
    sudo mkdir -p /var/log/dewatamotor
    sudo chown $APP_USER:www-data /var/log/dewatamotor
    
    # Setup logrotate
    sudo tee /etc/logrotate.d/dewatamotor > /dev/null <<EOF
/var/log/dewatamotor/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $APP_USER www-data
    postrotate
        systemctl reload dewatamotor
    endscript
}
EOF
}

# Create backup script
create_backup_script() {
    log "Creating backup script..."
    
    sudo tee /usr/local/bin/backup-dewatamotor.sh > /dev/null <<'EOF'
#!/bin/bash

# Dewata Motor Backup Script
BACKUP_DIR="/var/backups/dewatamotor"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/var/www/dewatamotor/DewataMotorRent"
DB_NAME="motordewata"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u root -p'Bambang0912' $DB_NAME > $BACKUP_DIR/database_$DATE.sql

# Backup uploaded files
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz -C $APP_DIR/static uploads/

# Backup application files (excluding venv)
tar --exclude='venv' --exclude='__pycache__' --exclude='.git' \
    -czf $BACKUP_DIR/app_$DATE.tar.gz -C /var/www/dewatamotor DewataMotorRent/

# Remove old backups (keep last 30 days)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

    sudo chmod +x /usr/local/bin/backup-dewatamotor.sh
    
    # Setup daily backup cron job
    echo "0 2 * * * root /usr/local/bin/backup-dewatamotor.sh >> /var/log/dewatamotor-backup.log 2>&1" | sudo tee -a /etc/crontab > /dev/null
}

# Final checks and status
final_checks() {
    log "Performing final checks..."
    
    # Check service status
    if sudo systemctl is-active --quiet dewatamotor; then
        log "✅ Dewata Motor service is running"
    else
        error "❌ Dewata Motor service is not running"
    fi
    
    # Check Nginx status
    if sudo systemctl is-active --quiet nginx; then
        log "✅ Nginx is running"
    else
        error "❌ Nginx is not running"
    fi
    
    # Check MySQL status
    if sudo systemctl is-active --quiet mysql; then
        log "✅ MySQL is running"
    else
        error "❌ MySQL is not running"
    fi
    
    # Check application response
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200\|302"; then
        log "✅ Application is responding"
    else
        warning "⚠️  Application might not be responding correctly"
    fi
}

# Display final information
show_final_info() {
    log "🎉 Deployment completed successfully!"
    echo
    echo "=================================================="
    echo "           DEWATA MOTOR DEPLOYMENT INFO"
    echo "=================================================="
    echo "Application URL: http://$DOMAIN"
    echo "Application Directory: $APP_DIR/$PROJECT_NAME"
    echo "Service Name: dewatamotor"
    echo "Database Name: $DB_NAME"
    echo "Database User: $DB_USER"
    echo "Nginx Config: /etc/nginx/sites-available/dewatamotor"
    echo "Service Status: sudo systemctl status dewatamotor"
    echo "Application Logs: sudo journalctl -u dewatamotor -f"
    echo "Nginx Logs: sudo tail -f /var/log/nginx/access.log"
    echo "Backup Script: /usr/local/bin/backup-dewatamotor.sh"
    echo "=================================================="
    echo
    echo "Default Login Credentials:"
    echo "Superadmin: superadmin / admin123"
    echo "Admin: admin / admin123"
    echo
    echo "Useful Commands:"
    echo "- Restart app: sudo systemctl restart dewatamotor"
    echo "- View logs: sudo journalctl -u dewatamotor -f"
    echo "- Update app: cd $APP_DIR/$PROJECT_NAME && git pull && sudo systemctl restart dewatamotor"
    echo "- Manual backup: sudo /usr/local/bin/backup-dewatamotor.sh"
    echo
    echo "⚠️  IMPORTANT SECURITY NOTES:"
    echo "1. Change default database passwords immediately"
    echo "2. Update default application login credentials"
    echo "3. Configure proper domain name in $DOMAIN"
    echo "4. Setup SSL certificate with: sudo certbot --nginx"
    echo "5. Review and customize firewall rules as needed"
    echo
    log "Happy coding! 🚀"
}

# Main deployment function
main() {
    log "🏍️  Starting Dewata Motor deployment on Ubuntu..."
    
    check_root
    check_ubuntu
    
    # Ask for domain name
    read -p "Enter your domain name (default: localhost): " domain_input
    if [ ! -z "$domain_input" ]; then
        DOMAIN="$domain_input"
    else
        DOMAIN="localhost"
    fi
    
    log "Deploying for domain: $DOMAIN"
    
    # Run deployment steps
    update_system
    install_python
    install_mysql
    install_nginx
    create_app_user
    setup_application
    setup_database
    create_systemd_service
    configure_nginx
    setup_firewall
    setup_logs
    create_backup_script
    
    # Optional SSL setup
    if [ "$DOMAIN" != "localhost" ]; then
        setup_ssl
    fi
    
    final_checks
    show_final_info
}

# Run main function
main "$@" 