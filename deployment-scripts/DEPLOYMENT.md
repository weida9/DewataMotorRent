# 🚀 Dewata Motor Deployment Guide

Panduan lengkap untuk deploy aplikasi Dewata Motor di server Ubuntu.

## 📋 Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04 LTS atau lebih baru
- **RAM**: Minimum 2GB (Recommended 4GB+)
- **Storage**: Minimum 20GB free space
- **Network**: Internet connection untuk download packages
- **Access**: Root/sudo access

### Domain Requirements
- Domain name yang sudah di-point ke server IP
- DNS sudah propagated (bisa dicek dengan `nslookup domain.com`)

## 🎯 Deployment Methods

### Method 1: One-Click Deployment (Recommended)

```bash
# Download and run quick deployment script
curl -sSL https://raw.githubusercontent.com/weida9/DewataMotorRent/main/deploy-quick.sh | sudo bash
```

### Method 2: Manual Deployment

1. **Download deployment script**
   ```bash
   wget https://raw.githubusercontent.com/weida9/DewataMotorRent/main/deploy.py
   ```

2. **Run deployment**
   ```bash
   sudo python3 deploy.py
   ```

### Method 3: Clone and Deploy

1. **Clone repository**
   ```bash
   git clone https://github.com/weida9/DewataMotorRent.git
   cd DewataMotorRent
   ```

2. **Run deployment script**
   ```bash
   sudo python3 deploy.py
   ```

## 🔧 What Gets Installed

### System Packages
- **Web Server**: Apache2 with mod_wsgi
- **Database**: MySQL Server 8.0+
- **Database Admin**: phpMyAdmin
- **Python**: Python 3.8+ with pip and venv
- **Security**: UFW Firewall, Fail2ban
- **SSL**: Certbot for Let's Encrypt certificates
- **Utilities**: Git, curl, wget, htop, nano, vim

### Application Components
- **Flask Application**: Dewata Motor rental system
- **Virtual Environment**: Isolated Python environment
- **Database Schema**: Complete with sample data
- **Static Files**: Images and CSS assets
- **Configuration**: Production-ready settings

### Security Features
- **Firewall**: UFW configured with necessary ports
- **SSL Ready**: Certbot installed for HTTPS
- **Secure Headers**: Apache security headers configured
- **File Permissions**: Proper ownership and permissions
- **Database Security**: Dedicated database user with limited privileges

## 📁 File Structure After Deployment

```
/opt/dewata-motor/               # Application directory
├── app.py                       # Main Flask application
├── config.py                    # Production configuration
├── app.wsgi                     # WSGI entry point
├── CREDENTIALS.json             # Secure credentials file
├── venv/                        # Python virtual environment
├── static/                      # Static assets
│   └── uploads/                 # Uploaded images
├── templates/                   # HTML templates
└── *.sql                        # Database files

/etc/apache2/sites-available/    # Apache configuration
├── dewata-motor.conf           # Virtual host configuration

/etc/systemd/system/            # Systemd services
├── dewata-motor.service        # Application service

/usr/local/bin/                 # Custom scripts
├── dewata-motor-backup         # Database backup script

/var/backups/dewata-motor/      # Backup directory
├── backup_YYYYMMDD_HHMMSS.sql  # Daily database backups
```

## 🔐 Default Credentials

### Application Login
| Role | Username | Password |
|------|----------|----------|
| Superadmin | `superadmin` | `admin123` |
| Admin | `admin` | `admin123` |

### System Access
- **MySQL Root**: Auto-generated (saved in CREDENTIALS.json)
- **Database User**: `dewata_user` (password in CREDENTIALS.json)
- **phpMyAdmin**: Available at `http://your-domain.com/phpmyadmin`
- **App User**: `dewata` (system user for application)

## 🌐 Post-Deployment Steps

### 1. Update Domain Configuration

Edit Apache configuration:
```bash
sudo nano /etc/apache2/sites-available/dewata-motor.conf
```

Change `ServerName` and `ServerAlias` to your actual domain:
```apache
ServerName your-domain.com
ServerAlias www.your-domain.com
```

Reload Apache:
```bash
sudo systemctl reload apache2
```

### 2. Setup SSL Certificate

```bash
# Install SSL certificate
sudo certbot --apache -d your-domain.com -d www.your-domain.com

# Verify SSL renewal
sudo certbot renew --dry-run
```

### 3. Change Default Passwords

**Important**: Change default application passwords immediately!

1. Login to application at `http://your-domain.com`
2. Go to Settings → Change Password
3. Update both superadmin and admin passwords

### 4. Configure Backup

Backup script runs daily at 2 AM. To run manually:
```bash
sudo /usr/local/bin/dewata-motor-backup
```

View backup files:
```bash
ls -la /var/backups/dewata-motor/
```

### 5. Monitor Application

Check application status:
```bash
# Application service
sudo systemctl status dewata-motor

# Apache status
sudo systemctl status apache2

# MySQL status
sudo systemctl status mysql

# View logs
sudo tail -f /var/log/apache2/dewata-motor_error.log
```

## 🛠️ Maintenance Commands

### Restart Services
```bash
# Restart all services
sudo systemctl restart dewata-motor apache2 mysql

# Restart individual services
sudo systemctl restart dewata-motor
sudo systemctl restart apache2
sudo systemctl restart mysql
```

### Update Application
```bash
cd /opt/dewata-motor
sudo -u dewata git pull origin main
sudo systemctl restart dewata-motor apache2
```

### Database Operations
```bash
# Access MySQL as root
sudo mysql -u root -p

# Access application database
sudo mysql -u dewata_user -p motordewata

# Backup database manually
sudo mysqldump -u dewata_user -p motordewata > backup.sql

# Restore database
sudo mysql -u dewata_user -p motordewata < backup.sql
```

### View Logs
```bash
# Apache logs
sudo tail -f /var/log/apache2/dewata-motor_access.log
sudo tail -f /var/log/apache2/dewata-motor_error.log

# MySQL logs
sudo tail -f /var/log/mysql/error.log

# System logs
sudo journalctl -u dewata-motor -f
sudo journalctl -u apache2 -f
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Application Not Loading
```bash
# Check Apache status
sudo systemctl status apache2

# Check application service
sudo systemctl status dewata-motor

# Check Apache error logs
sudo tail -f /var/log/apache2/dewata-motor_error.log
```

#### 2. Database Connection Issues
```bash
# Test database connection
sudo mysql -u dewata_user -p motordewata

# Check MySQL status
sudo systemctl status mysql

# Restart MySQL
sudo systemctl restart mysql
```

#### 3. Permission Issues
```bash
# Fix application permissions
sudo chown -R dewata:www-data /opt/dewata-motor
sudo chmod -R 755 /opt/dewata-motor
sudo chmod -R 644 /opt/dewata-motor/static
```

#### 4. SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew

# Test renewal
sudo certbot renew --dry-run
```

### Performance Optimization

#### 1. Enable Apache Modules
```bash
sudo a2enmod deflate expires headers
sudo systemctl reload apache2
```

#### 2. MySQL Optimization
```bash
sudo mysql_secure_installation
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

#### 3. Monitor Resources
```bash
# Check system resources
htop
df -h
free -h

# Check Apache processes
sudo apache2ctl status
```

## 🔒 Security Best Practices

### 1. Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
cd /opt/dewata-motor
sudo -u dewata ./venv/bin/pip list --outdated
```

### 2. Firewall Management
```bash
# Check firewall status
sudo ufw status verbose

# Allow specific IP
sudo ufw allow from IP_ADDRESS

# Remove rule
sudo ufw delete allow 'Apache Full'
```

### 3. Log Monitoring
```bash
# Monitor failed login attempts
sudo grep "Failed password" /var/log/auth.log

# Monitor Apache access
sudo tail -f /var/log/apache2/dewata-motor_access.log
```

### 4. Database Security
```bash
# Run MySQL security script
sudo mysql_secure_installation

# Check user privileges
sudo mysql -u root -p -e "SELECT User,Host FROM mysql.user;"
```

## 📞 Support

### Getting Help
- **Documentation**: Check this file and README.md
- **Logs**: Always check log files first
- **GitHub Issues**: Create issue with error logs
- **Community**: Join project discussions

### Emergency Recovery
```bash
# Stop all services
sudo systemctl stop dewata-motor apache2

# Restore from backup
sudo mysql -u dewata_user -p motordewata < /var/backups/dewata-motor/latest_backup.sql

# Start services
sudo systemctl start mysql apache2 dewata-motor
```

---

## 🎉 Deployment Complete!

Your Dewata Motor application is now successfully deployed and ready for production use!

**Next Steps:**
1. ✅ Update domain configuration
2. ✅ Setup SSL certificate
3. ✅ Change default passwords
4. ✅ Test all functionality
5. ✅ Setup monitoring

**Important Files:**
- Application: `http://your-domain.com`
- phpMyAdmin: `http://your-domain.com/phpmyadmin`
- Credentials: `/opt/dewata-motor/CREDENTIALS.json`

Enjoy your new motor rental management system! 🏍️✨ 