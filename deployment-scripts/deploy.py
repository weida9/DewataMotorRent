#!/usr/bin/env python3
"""
Dewata Motor Deployment Script for Ubuntu Server
Automatically installs and configures everything needed to run the application.

Usage: python3 deploy.py
Author: Dewata Motor Team
Version: 1.0.0
"""

import os
import sys
import subprocess
import getpass
import secrets
import string
import json
from pathlib import Path

# Configuration
GITHUB_REPO = "git@github.com:weida9/DewataMotorRent.git"
APP_NAME = "dewata-motor"
APP_USER = "dewata"
APP_DIR = f"/opt/{APP_NAME}"
DOMAIN = "your-domain.com"  # Change this to your domain
DB_NAME = "motordewata"
DB_USER = "dewata_user"

# Colors for output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKBLUE}ℹ️  {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def run_command(command, description="", check=True, capture_output=False, shell=True):
    """Run a shell command with error handling."""
    if description:
        print_info(f"{description}...")
    
    try:
        if capture_output:
            result = subprocess.run(command, shell=shell, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=shell, check=check)
            return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        if capture_output and e.stdout:
            print(f"Output: {e.stdout}")
        if capture_output and e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return None

def generate_password(length=16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def check_root():
    """Check if running as root."""
    if os.geteuid() != 0:
        print_error("This script must be run as root (use sudo)")
        sys.exit(1)

def update_system():
    """Update system packages."""
    print_header("UPDATING SYSTEM")
    run_command("apt update", "Updating package lists")
    run_command("apt upgrade -y", "Upgrading packages")
    print_success("System updated successfully")

def install_basic_packages():
    """Install basic required packages."""
    print_header("INSTALLING BASIC PACKAGES")
    
    packages = [
        "curl", "wget", "git", "unzip", "software-properties-common",
        "apt-transport-https", "ca-certificates", "gnupg", "lsb-release",
        "ufw", "fail2ban", "htop", "nano", "vim", "tree"
    ]
    
    package_list = " ".join(packages)
    run_command(f"apt install -y {package_list}", "Installing basic packages")
    print_success("Basic packages installed successfully")

def install_python():
    """Install Python and pip."""
    print_header("INSTALLING PYTHON")
    
    run_command("apt install -y python3 python3-pip python3-venv python3-dev", 
                "Installing Python 3 and pip")
    run_command("python3 -m pip install --upgrade pip", "Upgrading pip")
    print_success("Python installed successfully")

def install_mysql():
    """Install and configure MySQL."""
    print_header("INSTALLING MYSQL")
    
    # Set MySQL root password non-interactively
    mysql_root_password = generate_password()
    
    # Pre-configure MySQL installation
    run_command(f'echo "mysql-server mysql-server/root_password password {mysql_root_password}" | debconf-set-selections')
    run_command(f'echo "mysql-server mysql-server/root_password_again password {mysql_root_password}" | debconf-set-selections')
    
    run_command("apt install -y mysql-server mysql-client", "Installing MySQL Server")
    run_command("systemctl start mysql", "Starting MySQL service")
    run_command("systemctl enable mysql", "Enabling MySQL service")
    
    print_success("MySQL installed successfully")
    return mysql_root_password

def install_phpmyadmin():
    """Install phpMyAdmin."""
    print_header("INSTALLING PHPMYADMIN")
    
    # Pre-configure phpMyAdmin
    phpmyadmin_password = generate_password()
    
    run_command(f'echo "phpmyadmin phpmyadmin/dbconfig-install boolean true" | debconf-set-selections')
    run_command(f'echo "phpmyadmin phpmyadmin/app-password-confirm password {phpmyadmin_password}" | debconf-set-selections')
    run_command(f'echo "phpmyadmin phpmyadmin/mysql/admin-pass password" | debconf-set-selections')
    run_command(f'echo "phpmyadmin phpmyadmin/mysql/app-pass password {phpmyadmin_password}" | debconf-set-selections')
    run_command(f'echo "phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2" | debconf-set-selections')
    
    run_command("apt install -y phpmyadmin php-mbstring php-zip php-gd php-json php-curl", 
                "Installing phpMyAdmin")
    
    # Enable phpMyAdmin Apache configuration
    run_command("phpenmod mbstring", "Enabling PHP mbstring module")
    run_command("systemctl reload apache2", "Reloading Apache")
    
    print_success("phpMyAdmin installed successfully")
    return phpmyadmin_password

def install_apache():
    """Install and configure Apache."""
    print_header("INSTALLING APACHE")
    
    run_command("apt install -y apache2 libapache2-mod-wsgi-py3", "Installing Apache and mod_wsgi")
    run_command("systemctl start apache2", "Starting Apache service")
    run_command("systemctl enable apache2", "Enabling Apache service")
    
    # Enable required modules
    run_command("a2enmod wsgi", "Enabling WSGI module")
    run_command("a2enmod rewrite", "Enabling rewrite module")
    run_command("a2enmod ssl", "Enabling SSL module")
    run_command("a2enmod headers", "Enabling headers module")
    
    print_success("Apache installed successfully")

def create_app_user():
    """Create application user."""
    print_header("CREATING APPLICATION USER")
    
    # Check if user exists
    try:
        run_command(f"id {APP_USER}", capture_output=True)
        print_info(f"User {APP_USER} already exists")
    except:
        run_command(f"useradd -m -s /bin/bash {APP_USER}", f"Creating user {APP_USER}")
        run_command(f"usermod -aG www-data {APP_USER}", f"Adding {APP_USER} to www-data group")
        print_success(f"User {APP_USER} created successfully")

def setup_database(mysql_root_password):
    """Setup database and user."""
    print_header("SETTING UP DATABASE")
    
    db_password = generate_password()
    
    # Create database and user
    mysql_commands = f"""
    CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
    CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{db_password}';
    GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'localhost';
    FLUSH PRIVILEGES;
    """
    
    # Write commands to temporary file
    with open('/tmp/mysql_setup.sql', 'w') as f:
        f.write(mysql_commands)
    
    run_command(f'mysql -u root -p{mysql_root_password} < /tmp/mysql_setup.sql', 
                "Setting up database and user")
    run_command('rm /tmp/mysql_setup.sql', "Cleaning up temporary files")
    
    print_success("Database setup completed")
    return db_password

def clone_repository():
    """Clone the application repository."""
    print_header("CLONING APPLICATION")
    
    # Create app directory
    run_command(f"mkdir -p {APP_DIR}", f"Creating application directory")
    
    # Clone repository
    run_command(f"git clone {GITHUB_REPO} {APP_DIR}", "Cloning repository")
    run_command(f"chown -R {APP_USER}:{APP_USER} {APP_DIR}", f"Setting ownership")
    
    print_success("Repository cloned successfully")

def setup_python_environment():
    """Setup Python virtual environment and install dependencies."""
    print_header("SETTING UP PYTHON ENVIRONMENT")
    
    # Create virtual environment
    run_command(f"cd {APP_DIR} && python3 -m venv venv", "Creating virtual environment")
    
    # Install dependencies
    run_command(f"cd {APP_DIR} && source venv/bin/activate && pip install --upgrade pip", 
                "Upgrading pip in virtual environment")
    run_command(f"cd {APP_DIR} && source venv/bin/activate && pip install -r requirements.txt", 
                "Installing Python dependencies")
    
    # Set permissions
    run_command(f"chown -R {APP_USER}:{APP_USER} {APP_DIR}", "Setting permissions")
    
    print_success("Python environment setup completed")

def import_database(db_password):
    """Import database schema."""
    print_header("IMPORTING DATABASE SCHEMA")
    
    run_command(f"mysql -u {DB_USER} -p{db_password} {DB_NAME} < {APP_DIR}/database_schema.sql", 
                "Importing database schema")
    
    print_success("Database schema imported successfully")

def create_app_config(db_password):
    """Create application configuration."""
    print_header("CREATING APPLICATION CONFIG")
    
    secret_key = generate_password(32)
    
    config_content = f"""#!/usr/bin/env python3
# Production Configuration for Dewata Motor

import os

class Config:
    # Database Configuration
    DB_CONFIG = {{
        'host': 'localhost',
        'user': '{DB_USER}',
        'password': '{db_password}',
        'database': '{DB_NAME}',
        'charset': 'utf8mb4'
    }}
    
    # Flask Configuration
    SECRET_KEY = '{secret_key}'
    DEBUG = False
    TESTING = False
    
    # Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Security Headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
"""
    
    with open(f"{APP_DIR}/config.py", "w") as f:
        f.write(config_content)
    
    run_command(f"chown {APP_USER}:{APP_USER} {APP_DIR}/config.py", "Setting config file permissions")
    run_command(f"chmod 600 {APP_DIR}/config.py", "Securing config file")
    
    print_success("Application configuration created")

def create_wsgi_file():
    """Create WSGI file for Apache."""
    print_header("CREATING WSGI CONFIGURATION")
    
    wsgi_content = f"""#!/usr/bin/env python3
import sys
import os

# Add application directory to Python path
sys.path.insert(0, '{APP_DIR}')

# Change to application directory
os.chdir('{APP_DIR}')

# Activate virtual environment
activate_this = '{APP_DIR}/venv/bin/activate_this.py'
if os.path.exists(activate_this):
    exec(open(activate_this).read(), {{'__file__': activate_this}})

# Import Flask application
from app import app as application

if __name__ == "__main__":
    application.run()
"""
    
    with open(f"{APP_DIR}/app.wsgi", "w") as f:
        f.write(wsgi_content)
    
    run_command(f"chown {APP_USER}:{APP_USER} {APP_DIR}/app.wsgi", "Setting WSGI file permissions")
    
    print_success("WSGI configuration created")

def create_apache_vhost():
    """Create Apache virtual host configuration."""
    print_header("CREATING APACHE VIRTUAL HOST")
    
    vhost_content = f"""<VirtualHost *:80>
    ServerName {DOMAIN}
    ServerAlias www.{DOMAIN}
    DocumentRoot {APP_DIR}
    WSGIDaemonProcess {APP_NAME} python-home={APP_DIR}/venv python-path={APP_DIR}
    WSGIProcessGroup {APP_NAME}
    WSGIScriptAlias / {APP_DIR}/app.wsgi
    
    <Directory {APP_DIR}>
        WSGIApplicationGroup %{{GLOBAL}}
        Require all granted
    </Directory>
    
    # Static files
    Alias /static {APP_DIR}/static
    <Directory {APP_DIR}/static>
        Require all granted
    </Directory>
    
    # Security headers
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    
    # Logging
    ErrorLog ${{APACHE_LOG_DIR}}/{APP_NAME}_error.log
    CustomLog ${{APACHE_LOG_DIR}}/{APP_NAME}_access.log combined
</VirtualHost>"""
    
    with open(f"/etc/apache2/sites-available/{APP_NAME}.conf", "w") as f:
        f.write(vhost_content)
    
    # Enable site and disable default
    run_command(f"a2ensite {APP_NAME}", "Enabling site")
    run_command("a2dissite 000-default", "Disabling default site")
    run_command("systemctl reload apache2", "Reloading Apache")
    
    print_success("Apache virtual host created")

def setup_firewall():
    """Configure UFW firewall."""
    print_header("CONFIGURING FIREWALL")
    
    run_command("ufw --force enable", "Enabling UFW firewall")
    run_command("ufw default deny incoming", "Setting default deny incoming")
    run_command("ufw default allow outgoing", "Setting default allow outgoing")
    run_command("ufw allow ssh", "Allowing SSH")
    run_command("ufw allow 'Apache Full'", "Allowing Apache")
    run_command("ufw allow mysql", "Allowing MySQL")
    
    print_success("Firewall configured successfully")

def setup_ssl_certbot():
    """Install and setup SSL with Let's Encrypt."""
    print_header("SETTING UP SSL (OPTIONAL)")
    
    print_info("Installing Certbot for SSL certificates...")
    run_command("apt install -y snapd", "Installing snapd")
    run_command("snap install core; snap refresh core", "Installing snap core")
    run_command("snap install --classic certbot", "Installing Certbot")
    run_command("ln -sf /snap/bin/certbot /usr/bin/certbot", "Creating Certbot symlink")
    
    print_warning(f"To setup SSL, run: certbot --apache -d {DOMAIN} -d www.{DOMAIN}")
    print_success("Certbot installed successfully")

def create_systemd_service():
    """Create systemd service for the application."""
    print_header("CREATING SYSTEMD SERVICE")
    
    service_content = f"""[Unit]
Description=Dewata Motor Flask Application
After=network.target mysql.service
Requires=mysql.service

[Service]
Type=notify
User={APP_USER}
Group=www-data
WorkingDirectory={APP_DIR}
Environment=PATH={APP_DIR}/venv/bin
ExecStart={APP_DIR}/venv/bin/python app.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    
    with open(f"/etc/systemd/system/{APP_NAME}.service", "w") as f:
        f.write(service_content)
    
    run_command("systemctl daemon-reload", "Reloading systemd")
    run_command(f"systemctl enable {APP_NAME}", "Enabling service")
    
    print_success("Systemd service created")

def create_backup_script():
    """Create database backup script."""
    print_header("CREATING BACKUP SCRIPT")
    
    backup_script = f"""#!/bin/bash
# Dewata Motor Database Backup Script

BACKUP_DIR="/var/backups/{APP_NAME}"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="{DB_NAME}"
DB_USER="{DB_USER}"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
mysqldump -u $DB_USER -p{'{DB_PASSWORD}'} $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Keep only last 30 backups
find $BACKUP_DIR -name "backup_*.sql" -type f -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/backup_$DATE.sql"
"""
    
    with open(f"/usr/local/bin/{APP_NAME}-backup", "w") as f:
        f.write(backup_script)
    
    run_command(f"chmod +x /usr/local/bin/{APP_NAME}-backup", "Making backup script executable")
    
    # Add to crontab
    cron_entry = f"0 2 * * * /usr/local/bin/{APP_NAME}-backup"
    run_command(f'(crontab -l 2>/dev/null; echo "{cron_entry}") | crontab -', "Adding backup to crontab")
    
    print_success("Backup script created")

def save_credentials(mysql_root_password, db_password, phpmyadmin_password):
    """Save all credentials to a secure file."""
    print_header("SAVING CREDENTIALS")
    
    credentials = {
        "mysql_root_password": mysql_root_password,
        "database_name": DB_NAME,
        "database_user": DB_USER,
        "database_password": db_password,
        "phpmyadmin_password": phpmyadmin_password,
        "app_user": APP_USER,
        "app_directory": APP_DIR,
        "domain": DOMAIN
    }
    
    with open(f"{APP_DIR}/CREDENTIALS.json", "w") as f:
        json.dump(credentials, f, indent=4)
    
    run_command(f"chown {APP_USER}:{APP_USER} {APP_DIR}/CREDENTIALS.json", "Setting credentials file ownership")
    run_command(f"chmod 600 {APP_DIR}/CREDENTIALS.json", "Securing credentials file")
    
    print_success("Credentials saved to CREDENTIALS.json")

def final_steps():
    """Final configuration steps."""
    print_header("FINAL CONFIGURATION")
    
    # Restart services
    run_command("systemctl restart mysql", "Restarting MySQL")
    run_command("systemctl restart apache2", "Restarting Apache")
    
    # Set final permissions
    run_command(f"chown -R {APP_USER}:www-data {APP_DIR}", "Setting final permissions")
    run_command(f"chmod -R 755 {APP_DIR}", "Setting directory permissions")
    run_command(f"chmod -R 644 {APP_DIR}/static", "Setting static files permissions")
    
    print_success("Final configuration completed")

def print_summary(mysql_root_password, db_password, phpmyadmin_password):
    """Print deployment summary."""
    print_header("DEPLOYMENT COMPLETED")
    
    print(f"""
{Colors.OKGREEN}🎉 Dewata Motor has been successfully deployed!{Colors.ENDC}

{Colors.OKBLUE}📋 DEPLOYMENT SUMMARY:{Colors.ENDC}
{Colors.BOLD}Application URL:{Colors.ENDC} http://{DOMAIN}
{Colors.BOLD}phpMyAdmin URL:{Colors.ENDC} http://{DOMAIN}/phpmyadmin
{Colors.BOLD}Application Directory:{Colors.ENDC} {APP_DIR}
{Colors.BOLD}Application User:{Colors.ENDC} {APP_USER}

{Colors.OKBLUE}🔐 IMPORTANT CREDENTIALS:{Colors.ENDC}
{Colors.BOLD}MySQL Root Password:{Colors.ENDC} {mysql_root_password}
{Colors.BOLD}Database Name:{Colors.ENDC} {DB_NAME}
{Colors.BOLD}Database User:{Colors.ENDC} {DB_USER}
{Colors.BOLD}Database Password:{Colors.ENDC} {db_password}
{Colors.BOLD}phpMyAdmin Password:{Colors.ENDC} {phpmyadmin_password}

{Colors.OKBLUE}👤 DEFAULT LOGIN CREDENTIALS:{Colors.ENDC}
{Colors.BOLD}Superadmin:{Colors.ENDC} superadmin / admin123
{Colors.BOLD}Admin:{Colors.ENDC} admin / admin123

{Colors.WARNING}⚠️  IMPORTANT NEXT STEPS:{Colors.ENDC}
1. Change default login passwords immediately
2. Update domain name in Apache configuration if needed
3. Setup SSL certificate: certbot --apache -d {DOMAIN}
4. Review and test all functionality
5. Setup monitoring and log rotation

{Colors.OKBLUE}📁 IMPORTANT FILES:{Colors.ENDC}
- Credentials: {APP_DIR}/CREDENTIALS.json
- Configuration: {APP_DIR}/config.py
- Apache Config: /etc/apache2/sites-available/{APP_NAME}.conf
- Systemd Service: /etc/systemd/system/{APP_NAME}.service
- Backup Script: /usr/local/bin/{APP_NAME}-backup

{Colors.OKGREEN}✅ Deployment completed successfully!{Colors.ENDC}
""")

def main():
    """Main deployment function."""
    print_header("DEWATA MOTOR DEPLOYMENT SCRIPT")
    print_info("Starting deployment process...")
    
    # Check prerequisites
    check_root()
    
    try:
        # System setup
        update_system()
        install_basic_packages()
        install_python()
        
        # Database setup
        mysql_root_password = install_mysql()
        phpmyadmin_password = install_phpmyadmin()
        
        # Web server setup
        install_apache()
        
        # Application setup
        create_app_user()
        db_password = setup_database(mysql_root_password)
        clone_repository()
        setup_python_environment()
        import_database(db_password)
        
        # Configuration
        create_app_config(db_password)
        create_wsgi_file()
        create_apache_vhost()
        
        # Security and services
        setup_firewall()
        setup_ssl_certbot()
        create_systemd_service()
        create_backup_script()
        
        # Finalization
        save_credentials(mysql_root_password, db_password, phpmyadmin_password)
        final_steps()
        
        # Summary
        print_summary(mysql_root_password, db_password, phpmyadmin_password)
        
    except KeyboardInterrupt:
        print_error("\nDeployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Deployment failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 