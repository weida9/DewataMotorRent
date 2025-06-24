# 🚀 Deployment Guide - Dewata Motor

Panduan lengkap untuk deployment sistem rental motor Dewata Motor ke production environment.

## 📋 Overview

Dokumen ini mencakup:
- Production deployment pada Ubuntu/CentOS server
- Docker deployment
- NGINX configuration
- SSL/TLS setup
- Performance optimization
- Security hardening
- Monitoring dan backup

## 🎯 Production Requirements

### Minimum System Requirements
- **OS**: Ubuntu 20.04 LTS / CentOS 8+
- **RAM**: 2GB minimum, 4GB recommended
- **Storage**: 10GB minimum, 20GB recommended
- **CPU**: 2 cores minimum
- **Network**: Stable internet connection

### Software Dependencies
- **Python**: 3.8+
- **MySQL**: 8.0+
- **NGINX**: 1.18+
- **Gunicorn**: 20.0+
- **SSL Certificate** (Let's Encrypt recommended)

---

## 🐧 Ubuntu Server Deployment

### 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv \
    mysql-server nginx git ufw \
    build-essential libmysqlclient-dev

# Install Certbot for SSL
sudo apt install -y certbot python3-certbot-nginx
```

### 2. MySQL Setup

```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p
```

```sql
-- Di MySQL console
CREATE DATABASE motordewata CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dewata_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON motordewata.* TO 'dewata_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. Application Setup

```bash
# Create application user
sudo adduser dewata --disabled-password --gecos ""
sudo usermod -aG sudo dewata

# Switch to application user
sudo su - dewata

# Clone application
git clone https://github.com/yourusername/DewataMotorRent.git
cd DewataMotorRent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Additional production packages
pip install gunicorn gevent
```

### 4. Configuration

```bash
# Create production config
cp app.py app_production.py
```

Edit `app_production.py`:

```python
# Production configuration
import os
from werkzeug.middleware.proxy_fix import ProxyFix

# Database config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'dewata_user',
    'password': os.getenv('DB_PASSWORD', 'your_secure_password'),
    'database': 'motordewata',
    'charset': 'utf8mb4'
}

# Security config
app.secret_key = os.getenv('SECRET_KEY', 'your-super-secret-key-here')
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# Trust proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Disable debug in production
if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=8000)
```

### 5. Database Import

```bash
# Import database schema
mysql -u dewata_user -p motordewata < database_schema.sql
```

### 6. Create Systemd Service

```bash
sudo nano /etc/systemd/system/dewata-motor.service
```

```ini
[Unit]
Description=Gunicorn instance to serve Dewata Motor
After=network.target

[Service]
User=dewata
Group=www-data
WorkingDirectory=/home/dewata/DewataMotorRent
Environment="PATH=/home/dewata/DewataMotorRent/.venv/bin"
Environment="DB_PASSWORD=your_secure_password"
Environment="SECRET_KEY=your-super-secret-key"
ExecStart=/home/dewata/DewataMotorRent/.venv/bin/gunicorn --workers 3 --worker-class gevent --bind 127.0.0.1:8000 app_production:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable dewata-motor
sudo systemctl start dewata-motor
sudo systemctl status dewata-motor
```

### 7. NGINX Configuration

```bash
sudo nano /etc/nginx/sites-available/dewata-motor
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.tailwindcss.com; style-src 'self' 'unsafe-inline' cdn.tailwindcss.com; img-src 'self' data:; font-src 'self' fonts.googleapis.com fonts.gstatic.com;" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # Rate limit login endpoint
    location /login {
        limit_req zone=login burst=3 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files
    location /static/ {
        alias /home/dewata/DewataMotorRent/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # File uploads
    location /uploads/ {
        alias /home/dewata/DewataMotorRent/static/uploads/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Limit upload size
    client_max_body_size 5M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/dewata-motor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. SSL Certificate Setup

```bash
# Get SSL certificate from Let's Encrypt
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### 9. Firewall Configuration

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

---

## 🐳 Docker Deployment

### 1. Dockerfile

```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy project
COPY . .

# Create uploads directory
RUN mkdir -p static/uploads

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
```

### 2. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=db
      - DB_USER=dewata_user
      - DB_PASSWORD=secure_password
      - DB_NAME=motordewata
      - SECRET_KEY=your-super-secret-key
    depends_on:
      - db
    volumes:
      - ./static/uploads:/app/static/uploads
    restart: unless-stopped

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=root_password
      - MYSQL_DATABASE=motordewata
      - MYSQL_USER=dewata_user
      - MYSQL_PASSWORD=secure_password
    volumes:
      - mysql_data:/var/lib/mysql
      - ./database_schema.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  mysql_data:
```

### 3. Production Docker Commands

```bash
# Build and start services
docker-compose up -d --build

# View logs
docker-compose logs -f web

# Execute commands in container
docker-compose exec web python manage.py collectstatic

# Database backup
docker-compose exec db mysqldump -u dewata_user -p motordewata > backup.sql

# Update application
git pull
docker-compose build web
docker-compose up -d web
```

---

## 🔧 Performance Optimization

### 1. Gunicorn Configuration

```python
# gunicorn.conf.py
bind = "127.0.0.1:8000"
workers = 3
worker_class = "gevent"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 5
preload_app = True
```

### 2. MySQL Optimization

```sql
-- /etc/mysql/mysql.conf.d/mysqld.cnf
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT
query_cache_type = 1
query_cache_size = 256M
```

### 3. NGINX Optimization

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;

# Enable sendfile
sendfile on;
tcp_nopush on;
tcp_nodelay on;

# Buffer sizes
client_body_buffer_size 128k;
client_max_body_size 5m;
client_header_buffer_size 1k;
large_client_header_buffers 4 4k;
output_buffers 1 32k;
postpone_output 1460;
```

---

## 🛡️ Security Hardening

### 1. Application Security

```python
# Security headers in app.py
@app.after_request
def security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

### 2. Database Security

```sql
-- Remove test databases
DROP DATABASE IF EXISTS test;

-- Secure user permissions
REVOKE ALL PRIVILEGES ON *.* FROM 'dewata_user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON motordewata.* TO 'dewata_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. File Permissions

```bash
# Set proper permissions
sudo chown -R dewata:www-data /home/dewata/DewataMotorRent
sudo chmod -R 755 /home/dewata/DewataMotorRent
sudo chmod -R 644 /home/dewata/DewataMotorRent/static/uploads
```

### 4. Log Monitoring

```bash
# Install fail2ban
sudo apt install fail2ban

# Configure fail2ban for NGINX
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
```

---

## 📊 Monitoring & Backup

### 1. Application Monitoring

```bash
# Create monitoring script
nano /home/dewata/monitor.sh
```

```bash
#!/bin/bash
# Check if application is running
if ! curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "Application is down! Restarting..."
    sudo systemctl restart dewata-motor
    echo "Application restart attempted at $(date)" >> /var/log/dewata-monitor.log
fi
```

```bash
# Add to crontab
crontab -e
# Add: */5 * * * * /home/dewata/monitor.sh
```

### 2. Database Backup

```bash
# Create backup script
nano /home/dewata/backup.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/dewata/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Database backup
mysqldump -u dewata_user -p'your_password' motordewata > "$BACKUP_DIR/db_backup_$DATE.sql"

# Application backup
tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" -C /home/dewata DewataMotorRent

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed at $(date)" >> /var/log/dewata-backup.log
```

```bash
# Schedule daily backup
crontab -e
# Add: 0 2 * * * /home/dewata/backup.sh
```

### 3. Log Rotation

```bash
sudo nano /etc/logrotate.d/dewata-motor
```

```
/var/log/dewata-*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
}
```

---

## 🚀 Deployment Checklist

### Pre-deployment
- [ ] Code review dan testing completed
- [ ] Database migration scripts prepared
- [ ] Backup current production data
- [ ] SSL certificates valid
- [ ] DNS records configured

### During Deployment
- [ ] Stop application gracefully
- [ ] Deploy new code
- [ ] Run database migrations
- [ ] Update dependencies
- [ ] Start application
- [ ] Verify functionality

### Post-deployment
- [ ] Monitor application logs
- [ ] Check database connections
- [ ] Verify SSL certificate
- [ ] Test critical functionality
- [ ] Monitor performance metrics

---

## 📞 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
sudo journalctl -u dewata-motor -f

# Check Python errors
sudo su - dewata
cd DewataMotorRent
source .venv/bin/activate
python app_production.py
```

#### Database Connection Issues
```bash
# Test database connection
mysql -u dewata_user -p motordewata

# Check MySQL status
sudo systemctl status mysql
```

#### NGINX Issues
```bash
# Test NGINX configuration
sudo nginx -t

# Check NGINX logs
sudo tail -f /var/log/nginx/error.log
```

#### SSL Certificate Problems
```bash
# Check certificate status
sudo certbot certificates

# Renew certificate
sudo certbot renew
```

### Performance Issues

#### High Memory Usage
```bash
# Monitor memory
free -h
htop

# Optimize Gunicorn workers
# Reduce worker count in service file
```

#### Slow Database Queries
```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
SET GLOBAL long_query_time = 2;
```

---

**Last Updated**: January 27, 2025  
**Version**: 2.0.0  
**Author**: Dewata Motor Development Team 