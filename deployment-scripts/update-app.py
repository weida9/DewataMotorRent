#!/usr/bin/env python3
"""
Dewata Motor Application Update Script
Updates the application to the latest version from GitHub.

Usage: python3 update-app.py [--backup] [--restart]
"""

import os
import sys
import subprocess
import argparse
import json
from datetime import datetime

# Configuration
APP_NAME = "dewata-motor"
APP_DIR = f"/opt/{APP_NAME}"
APP_USER = "dewata"
BACKUP_DIR = f"/var/backups/{APP_NAME}/updates"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

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

def run_command(command, description="", check=True):
    """Run a shell command with error handling."""
    if description:
        print_info(f"{description}...")
    
    try:
        result = subprocess.run(command, shell=True, check=check, 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return False, "", str(e)

def check_root():
    """Check if running as root."""
    if os.geteuid() != 0:
        print_error("This script must be run as root (use sudo)")
        sys.exit(1)

def backup_current_version():
    """Create backup of current application."""
    print_header("CREATING BACKUP")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}/backup_{timestamp}"
    
    # Create backup directory
    run_command(f"mkdir -p {backup_path}", "Creating backup directory")
    
    # Backup application files (excluding venv and uploads)
    run_command(f"rsync -av --exclude='venv' --exclude='static/uploads' {APP_DIR}/ {backup_path}/", 
                "Backing up application files")
    
    # Backup database
    try:
        if os.path.exists(f"{APP_DIR}/CREDENTIALS.json"):
            with open(f"{APP_DIR}/CREDENTIALS.json", 'r') as f:
                creds = json.load(f)
            
            db_user = creds.get('database_user')
            db_password = creds.get('database_password')
            db_name = creds.get('database_name')
            
            run_command(f"mysqldump -u {db_user} -p{db_password} {db_name} > {backup_path}/database_backup.sql", 
                       "Backing up database")
        else:
            print_warning("Credentials file not found, skipping database backup")
    except Exception as e:
        print_warning(f"Database backup failed: {str(e)}")
    
    print_success(f"Backup created: {backup_path}")
    return backup_path

def stop_services():
    """Stop application services."""
    print_header("STOPPING SERVICES")
    
    services = [APP_NAME, "apache2"]
    for service in services:
        run_command(f"systemctl stop {service}", f"Stopping {service}")
    
    print_success("Services stopped successfully")

def update_application():
    """Update application from GitHub."""
    print_header("UPDATING APPLICATION")
    
    # Change to app directory
    os.chdir(APP_DIR)
    
    # Fetch latest changes
    run_command("git fetch origin", "Fetching latest changes")
    
    # Check if there are updates
    success, local_commit, _ = run_command("git rev-parse HEAD", check=False)
    success, remote_commit, _ = run_command("git rev-parse origin/main", check=False)
    
    if local_commit == remote_commit:
        print_info("Application is already up to date")
        return False
    
    # Show what will be updated
    run_command("git log --oneline HEAD..origin/main", "Changes to be applied")
    
    # Pull updates
    run_command("git pull origin main", "Pulling updates")
    
    # Update Python dependencies
    run_command(f"cd {APP_DIR} && source venv/bin/activate && pip install -r requirements.txt --upgrade", 
                "Updating Python dependencies")
    
    # Set permissions
    run_command(f"chown -R {APP_USER}:www-data {APP_DIR}", "Setting permissions")
    
    print_success("Application updated successfully")
    return True

def update_database():
    """Apply database migrations if any."""
    print_header("CHECKING DATABASE UPDATES")
    
    # Check for database update files
    update_files = []
    for file in os.listdir(APP_DIR):
        if file.startswith("update_") and file.endswith(".sql"):
            update_files.append(file)
    
    if not update_files:
        print_info("No database updates found")
        return
    
    try:
        if os.path.exists(f"{APP_DIR}/CREDENTIALS.json"):
            with open(f"{APP_DIR}/CREDENTIALS.json", 'r') as f:
                creds = json.load(f)
            
            db_user = creds.get('database_user')
            db_password = creds.get('database_password')
            db_name = creds.get('database_name')
            
            for update_file in sorted(update_files):
                print_info(f"Applying database update: {update_file}")
                run_command(f"mysql -u {db_user} -p{db_password} {db_name} < {APP_DIR}/{update_file}", 
                           f"Applying {update_file}")
            
            print_success("Database updates applied successfully")
        else:
            print_warning("Credentials file not found, skipping database updates")
    except Exception as e:
        print_error(f"Database update failed: {str(e)}")

def start_services():
    """Start application services."""
    print_header("STARTING SERVICES")
    
    services = ["mysql", "apache2", APP_NAME]
    for service in services:
        run_command(f"systemctl start {service}", f"Starting {service}")
        run_command(f"systemctl enable {service}", f"Enabling {service}")
    
    print_success("Services started successfully")

def verify_update():
    """Verify that the update was successful."""
    print_header("VERIFYING UPDATE")
    
    # Check service status
    services = ["apache2", "mysql", APP_NAME]
    for service in services:
        success, stdout, stderr = run_command(f"systemctl is-active {service}", check=False)
        if success and "active" in stdout:
            print_success(f"Service {service} is running")
        else:
            print_error(f"Service {service} is not running")
    
    # Test web application
    try:
        import requests
        response = requests.get("http://localhost", timeout=10)
        if response.status_code == 200:
            print_success("Web application is responding")
        else:
            print_error(f"Web application returned status code: {response.status_code}")
    except Exception as e:
        print_error(f"Web application test failed: {str(e)}")
    
    # Check latest commit
    success, commit, _ = run_command(f"cd {APP_DIR} && git rev-parse --short HEAD", check=False)
    if success:
        print_success(f"Current version: {commit}")

def rollback_update(backup_path):
    """Rollback to previous version if update fails."""
    print_header("ROLLING BACK UPDATE")
    
    if not backup_path or not os.path.exists(backup_path):
        print_error("Backup path not found, cannot rollback")
        return
    
    # Stop services
    stop_services()
    
    # Restore application files
    run_command(f"rsync -av --exclude='venv' --exclude='static/uploads' {backup_path}/ {APP_DIR}/", 
                "Restoring application files")
    
    # Restore database if backup exists
    db_backup = f"{backup_path}/database_backup.sql"
    if os.path.exists(db_backup):
        try:
            if os.path.exists(f"{APP_DIR}/CREDENTIALS.json"):
                with open(f"{APP_DIR}/CREDENTIALS.json", 'r') as f:
                    creds = json.load(f)
                
                db_user = creds.get('database_user')
                db_password = creds.get('database_password')
                db_name = creds.get('database_name')
                
                run_command(f"mysql -u {db_user} -p{db_password} {db_name} < {db_backup}", 
                           "Restoring database")
        except Exception as e:
            print_error(f"Database rollback failed: {str(e)}")
    
    # Set permissions
    run_command(f"chown -R {APP_USER}:www-data {APP_DIR}", "Setting permissions")
    
    # Start services
    start_services()
    
    print_success("Rollback completed")

def main():
    parser = argparse.ArgumentParser(description='Update Dewata Motor Application')
    parser.add_argument('--backup', action='store_true', 
                       help='Create backup before update (recommended)')
    parser.add_argument('--restart', action='store_true', 
                       help='Restart services after update')
    parser.add_argument('--rollback', 
                       help='Rollback to specific backup (provide backup path)')
    args = parser.parse_args()
    
    print_header("DEWATA MOTOR UPDATE SCRIPT")
    
    # Check prerequisites
    check_root()
    
    # Handle rollback
    if args.rollback:
        rollback_update(args.rollback)
        return
    
    backup_path = None
    
    try:
        # Create backup if requested
        if args.backup:
            backup_path = backup_current_version()
        
        # Stop services
        stop_services()
        
        # Update application
        updated = update_application()
        
        if updated:
            # Update database
            update_database()
            
            # Start services
            start_services()
            
            # Verify update
            verify_update()
            
            print_header("UPDATE COMPLETED SUCCESSFULLY")
            print_success("Dewata Motor has been updated to the latest version!")
            
            if backup_path:
                print_info(f"Backup available at: {backup_path}")
                print_info(f"To rollback: python3 update-app.py --rollback {backup_path}")
        else:
            # Start services even if no update
            start_services()
            print_info("No updates were applied")
    
    except KeyboardInterrupt:
        print_error("\nUpdate interrupted by user")
        if backup_path:
            print_warning(f"To rollback: python3 update-app.py --rollback {backup_path}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Update failed: {str(e)}")
        if backup_path:
            print_warning("Attempting automatic rollback...")
            rollback_update(backup_path)
        sys.exit(1)

if __name__ == "__main__":
    main() 