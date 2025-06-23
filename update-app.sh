#!/bin/bash

# Update Dewata Motor Application
# Script to pull latest changes and restart services

set -e

APP_DIR="/var/www/dewatamotor/DewataMotorRent"
SERVICE_NAME="dewatamotor"

echo "🔄 Updating Dewata Motor Application..."
echo "======================================"

# Check if app directory exists
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Application directory not found: $APP_DIR"
    echo "Please run the deployment script first."
    exit 1
fi

cd $APP_DIR

# Create backup before update
echo "📦 Creating backup..."
BACKUP_DIR="/var/backups/dewatamotor"
DATE=$(date +%Y%m%d_%H%M%S)
sudo mkdir -p $BACKUP_DIR

# Backup current application
sudo tar --exclude='venv' --exclude='__pycache__' --exclude='.git' \
    -czf $BACKUP_DIR/app_before_update_$DATE.tar.gz -C /var/www/dewatamotor DewataMotorRent/

# Backup database
sudo mysqldump -u root -p'Bambang0912' motordewata > $BACKUP_DIR/database_before_update_$DATE.sql

echo "✅ Backup created in $BACKUP_DIR"

# Stop the service
echo "🛑 Stopping application service..."
sudo systemctl stop $SERVICE_NAME

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
sudo -u dewatamotor git fetch origin
sudo -u dewatamotor git reset --hard origin/main

# Update Python dependencies
echo "📦 Updating Python dependencies..."
sudo -u dewatamotor ./venv/bin/pip install --upgrade pip
sudo -u dewatamotor ./venv/bin/pip install -r requirements.txt

# Check for database updates
if [ -f "update_database.sql" ]; then
    echo "🗄️ Applying database updates..."
    sudo mysql -u root -p'Bambang0912' motordewata < update_database.sql
    echo "✅ Database updated"
else
    echo "ℹ️ No database updates found"
fi

# Set proper permissions
echo "🔐 Setting permissions..."
sudo chown -R dewatamotor:www-data /var/www/dewatamotor
sudo chmod -R 755 /var/www/dewatamotor
sudo chmod -R 775 $APP_DIR/static/uploads

# Start the service
echo "🚀 Starting application service..."
sudo systemctl start $SERVICE_NAME

# Check service status
sleep 3
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service is running"
else
    echo "❌ Service failed to start. Checking logs..."
    sudo journalctl -u $SERVICE_NAME --lines=20 --no-pager
    exit 1
fi

# Test application
echo "🧪 Testing application..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5000 | grep -q "200\|302"; then
    echo "✅ Application is responding"
else
    echo "⚠️ Application might not be responding correctly"
fi

# Reload Nginx (in case of static file changes)
echo "🌐 Reloading Nginx..."
sudo systemctl reload nginx

echo ""
echo "🎉 UPDATE COMPLETE!"
echo "=================="
echo "Application has been updated and restarted successfully!"
echo ""
echo "Service Status: $(sudo systemctl is-active $SERVICE_NAME)"
echo "Latest Commit: $(git log -1 --oneline)"
echo ""
echo "Useful Commands:"
echo "- View logs: sudo journalctl -u $SERVICE_NAME -f"
echo "- Restart service: sudo systemctl restart $SERVICE_NAME"
echo "- Check status: sudo systemctl status $SERVICE_NAME"
echo ""
echo "Backups saved in: $BACKUP_DIR"
echo "🚀 Update completed successfully!" 