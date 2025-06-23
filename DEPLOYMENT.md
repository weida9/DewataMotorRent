# 🚀 Deployment Guide - Dewata Motor

Panduan lengkap untuk deploy aplikasi Dewata Motor ke server Ubuntu.

## 📋 Prerequisites

### Server Requirements
- **OS**: Ubuntu 18.04+ (20.04 LTS recommended)
- **RAM**: Minimum 1GB (2GB+ recommended)
- **Storage**: Minimum 10GB free space
- **Network**: Public IP address & domain name (optional)

### Local Requirements
- Git dengan SSH key configured untuk GitHub
- Access ke server Ubuntu dengan sudo privileges

## 🚀 Quick Deployment (Recommended)

### Option 1: One-Command Deployment
```bash
# Download and run quick deploy script
curl -fsSL https://raw.githubusercontent.com/weida9/DewataMotorRent/main/quick-deploy.sh | bash
```

### Option 2: Manual Download
```bash
# Clone repository
git clone git@github.com:weida9/DewataMotorRent.git
cd DewataMotorRent

# Make scripts executable
chmod +x *.sh

# Run quick deployment
./quick-deploy.sh
```

## 🔧 Advanced Deployment

Untuk deployment dengan konfigurasi advanced (SSL, domain, monitoring):

```bash
# Run full deployment script
./deploy.sh
```

Script ini akan meminta:
- Domain name
- SSL certificate setup
- Advanced security configuration

## 📁 Deployment Scripts

### 1. `quick-deploy.sh`
- ✅ **Recommended untuk testing/development**
- Setup dasar dengan konfigurasi minimal
- Akses via IP address
- Tidak termasuk SSL

### 2. `deploy.sh`
- 🎯 **Recommended untuk production**
- Full configuration dengan security
- SSL certificate dengan Let's Encrypt
- Domain name configuration
- Monitoring & backup setup

### 3. `update-app.sh`
- 🔄 Update aplikasi dari GitHub
- Automatic backup sebelum update
- Zero-downtime deployment

## 🏗️ Manual Deployment Steps

Jika ingin melakukan deployment manual:

### 1. System Update
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv mysql-server nginx git curl
```

### 2. MySQL Setup
```bash
# Secure MySQL
sudo mysql_secure_installation

# Create database
sudo mysql -u root -p
```
```sql
CREATE DATABASE motordewata;
CREATE USER 'dewatamotor'@'localhost' IDENTIFIED BY 'YourSecurePassword';
GRANT ALL PRIVILEGES ON motordewata.* TO 'dewatamotor'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Application Setup
```bash
# Create application user
sudo adduser --system --group --home /var/www/dewatamotor dewatamotor

# Clone repository
sudo -u dewatamotor git clone git@github.com:weida9/DewataMotorRent.git /var/www/dewatamotor/DewataMotorRent

# Setup Python environment
cd /var/www/dewatamotor/DewataMotorRent
sudo -u dewatamotor python3 -m venv venv
sudo -u dewatamotor ./venv/bin/pip install -r requirements.txt
```

### 4. Database Import
```bash
mysql -u dewatamotor -p motordewata < database_schema.sql
```

### 5. Systemd Service
```bash
sudo cp deployment/dewatamotor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dewatamotor
sudo systemctl start dewatamotor
```

### 6. Nginx Configuration
```bash
sudo cp deployment/nginx.conf /etc/nginx/sites-available/dewatamotor
sudo ln -s /etc/nginx/sites-available/dewatamotor /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 🔒 Security Configuration

### Firewall Setup
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
```

### SSL Certificate (Production)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### Secure Database
```bash
# Change default passwords
mysql -u root -p
```
```sql
ALTER USER 'dewatamotor'@'localhost' IDENTIFIED BY 'NewSecurePassword';
FLUSH PRIVILEGES;
```

## 📊 Post-Deployment

### Verify Installation
```bash
# Check services
sudo systemctl status dewatamotor
sudo systemctl status nginx
sudo systemctl status mysql

# Test application
curl http://localhost:5000
curl http://your-domain.com
```

### Default Credentials
- **Superadmin**: `superadmin` / `admin123`
- **Admin**: `admin` / `admin123`

⚠️ **IMPORTANT**: Change these passwords immediately after deployment!

## 🔄 Application Updates

### Quick Update
```bash
cd /var/www/dewatamotor/DewataMotorRent
./update-app.sh
```

### Manual Update
```bash
cd /var/www/dewatamotor/DewataMotorRent
sudo systemctl stop dewatamotor
sudo -u dewatamotor git pull origin main
sudo -u dewatamotor ./venv/bin/pip install -r requirements.txt
sudo systemctl start dewatamotor
```

## 📈 Monitoring & Maintenance

### View Logs
```bash
# Application logs
sudo journalctl -u dewatamotor -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# MySQL logs
sudo tail -f /var/log/mysql/error.log
```

### Backup
```bash
# Manual backup
sudo /usr/local/bin/backup-dewatamotor.sh

# Automated backup (already configured via cron)
sudo crontab -l
```

### Performance Monitoring
```bash
# System resources
htop
df -h
free -h

# Service status
sudo systemctl status dewatamotor nginx mysql
```

## 🐛 Troubleshooting

### Application Not Starting
```bash
# Check logs
sudo journalctl -u dewatamotor -n 50

# Check Python environment
cd /var/www/dewatamotor/DewataMotorRent
sudo -u dewatamotor ./venv/bin/python -c "import flask; print('Flask OK')"

# Check database connection
sudo -u dewatamotor ./venv/bin/python -c "import pymysql; print('MySQL OK')"
```

### Database Connection Issues
```bash
# Test MySQL connection
mysql -u dewatamotor -p -h localhost motordewata

# Check MySQL status
sudo systemctl status mysql
sudo mysql -u root -p -e "SHOW PROCESSLIST;"
```

### Nginx Issues
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# Check port 80/443
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

### Permission Issues
```bash
# Fix permissions
sudo chown -R dewatamotor:www-data /var/www/dewatamotor
sudo chmod -R 755 /var/www/dewatamotor
sudo chmod -R 775 /var/www/dewatamotor/DewataMotorRent/static/uploads
```

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Create production environment file
cp production.env /var/www/dewatamotor/DewataMotorRent/.env
# Edit values as needed
sudo nano /var/www/dewatamotor/DewataMotorRent/.env
```

### Custom Domain
1. Point domain A record to server IP
2. Update Nginx configuration
3. Obtain SSL certificate
4. Update application configuration

### Load Balancing (Multiple Servers)
- Use reverse proxy (Nginx/HAProxy)
- Shared database server
- Shared file storage for uploads
- Session store (Redis/Memcached)

## 📞 Support

### Common Commands
```bash
# Service management
sudo systemctl {start|stop|restart|status} dewatamotor
sudo systemctl {start|stop|restart|status} nginx
sudo systemctl {start|stop|restart|status} mysql

# Application management
cd /var/www/dewatamotor/DewataMotorRent
./update-app.sh                    # Update application
sudo journalctl -u dewatamotor -f  # View live logs
git log --oneline -n 10            # View recent commits
```

### File Locations
- **Application**: `/var/www/dewatamotor/DewataMotorRent`
- **Service Config**: `/etc/systemd/system/dewatamotor.service`
- **Nginx Config**: `/etc/nginx/sites-available/dewatamotor`
- **Logs**: `/var/log/nginx/` & `journalctl -u dewatamotor`
- **Backups**: `/var/backups/dewatamotor/`

---

**🎉 Happy Deploying!**

Untuk pertanyaan dan issue, silakan buat GitHub issue di repository ini. 