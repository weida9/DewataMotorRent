#!/usr/bin/env python3
"""
Dewata Motor Application Update Script
Safely updates the application from GitHub repository.

Usage: python3 update-app.py [--backup] [--force]
"""

import os
import sys
import subprocess
import shutil
import json
import argparse
from datetime import datetime
from pathlib import Path

# Configuration
APP_NAME = "dewata-motor"
APP_DIR = f"/opt/{APP_NAME}"
APP_USER = "dewata"
BACKUP_DIR = f"/var/backups/{APP_NAME}"
GITHUB_REPO = "https://github.com/weida9/DewataMotorRent.git"

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

def run_command(command, description="", check=True, capture_output=False):
    """Run a shell command with error handling."""
    if description:
        print_info(f"{description}...")
    
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, check=check, 
                                  capture_output=True, text=True)
            return result.stdout.strip()
        else:
            result = subprocess.run(command, shell=True, check=check)
            return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        if check:
            sys.exit(1)
        return None

def check_root():
    """Check if running as root."""
    if os.geteuid() != 0:
        print_error("This script must be run as root (use sudo)")
        sys.exit(1)

def check_prerequisites():
    """Check if application is installed."""
    if not os.path.exists(APP_DIR):
        print_error(f"Application directory {APP_DIR} not found")
        print_info("Please run the deployment script first")
        sys.exit(1)
    
    if not os.path.exists(f"{APP_DIR}/.git"):
        print_error("Git repository not found in application directory")
        sys.exit(1)

def get_current_version():
    """Get current application version."""
    try:
        os.chdir(APP_DIR)
        current_hash = run_command("git rev-parse HEAD", capture_output=True)
        current_branch = run_command("git branch --show-current", capture_output=True)
        return current_hash[:8], current_branch
    except:
        return "unknown", "unknown"

def backup_application(create_backup=True):
    """Create backup of current application."""
    if not create_backup:
        print_info("Skipping backup as requested")
        return None
    
    print_header("CREATING BACKUP")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}/app_backup_{timestamp}"
    
    # Create backup directory
    run_command(f"mkdir -p {backup_path}", "Creating backup directory")
    
    # Backup application files (excluding .git and venv)
    run_command(f"rsync -av --exclude='.git' --exclude='venv' --exclude='__pycache__' {APP_DIR}/ {backup_path}/", 
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
    except Exception as e:
        print_warning(f"Could not backup database: {str(e)}")
    
    print_success(f"Backup created at: {backup_path}")
    return backup_path

def stop_services():
    """Stop application services."""
    print_header("STOPPING SERVICES")
    
    services = [APP_NAME, "apache2"]
    for service in services:
        run_command(f"systemctl stop {service}", f"Stopping {service}", check=False)
    
    print_success("Services stopped")

def start_services():
    """Start application services."""
    print_header("STARTING SERVICES")
    
    services = ["apache2", APP_NAME]
    for service in services:
        run_command(f"systemctl start {service}", f"Starting {service}")
    
    print_success("Services started")

def update_application():
    """Update application from repository."""
    print_header("UPDATING APPLICATION")
    
    os.chdir(APP_DIR)
    
    # Fetch latest changes
    run_command("git fetch origin", "Fetching latest changes")
    
    # Check if there are updates
    local_hash = run_command("git rev-parse HEAD", capture_output=True)
    remote_hash = run_command("git rev-parse origin/main", capture_output=True)
    
    if local_hash == remote_hash:
        print_info("Application is already up to date")
        return False
    
    # Pull latest changes
    run_command("git pull origin main", "Pulling latest changes")
    
    # Update Python dependencies
    run_command(f"source venv/bin/activate && pip install -r requirements.txt", 
                "Updating Python dependencies")
    
    # Set proper permissions
    run_command(f"chown -R {APP_USER}:www-data {APP_DIR}", "Setting permissions")
    run_command(f"chmod -R 755 {APP_DIR}", "Setting directory permissions")
    
    print_success("Application updated successfully")
    return True

def check_database_updates():
    """Check and apply database updates."""
    print_header("CHECKING DATABASE UPDATES")
    
    update_files = [
        "update_database.sql",
        "fix_database.sql"
    ]
    
    updates_applied = False
    
    for update_file in update_files:
        file_path = f"{APP_DIR}/{update_file}"
        if os.path.exists(file_path):
            print_info(f"Found database update file: {update_file}")
            
            try:
                if os.path.exists(f"{APP_DIR}/CREDENTIALS.json"):
                    with open(f"{APP_DIR}/CREDENTIALS.json", 'r') as f:
                        creds = json.load(f)
                    
                    db_user = creds.get('database_user')
                    db_password = creds.get('database_password')
                    db_name = creds.get('database_name')
                    
                    run_command(f"mysql -u {db_user} -p{db_password} {db_name} < {file_path}", 
                                f"Applying {update_file}")
                    
                    updates_applied = True
            except Exception as e:
                print_warning(f"Could not apply {update_file}: {str(e)}")
    
    if updates_applied:
        print_success("Database updates applied")
    else:
        print_info("No database updates found")

def verify_update():
    """Verify that the update was successful."""
    print_header("VERIFYING UPDATE")
    
    # Check if services are running
    services = ["apache2", APP_NAME]
    all_running = True
    
    for service in services:
        result = run_command(f"systemctl is-active {service}", capture_output=True, check=False)
        if result and "active" in result:
            print_success(f"Service {service} is running")
        else:
            print_error(f"Service {service} is not running")
            all_running = False
    
    # Test web application
    try:
        import requests
        response = requests.get("http://localhost", timeout=10)
        if response.status_code == 200:
            print_success("Web application is responding")
        else:
            print_error(f"Web application returned status: {response.status_code}")
            all_running = False
    except Exception as e:
        print_error(f"Could not test web application: {str(e)}")
        all_running = False
    
    return all_running

def rollback_application(backup_path):
    """Rollback application to backup."""
    if not backup_path or not os.path.exists(backup_path):
        print_error("No valid backup found for rollback")
        return False
    
    print_header("ROLLING BACK APPLICATION")
    
    stop_services()
    
    # Restore application files
    run_command(f"rsync -av --delete --exclude='venv' {backup_path}/ {APP_DIR}/", 
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
            print_warning(f"Could not restore database: {str(e)}")
    
    # Set permissions
    run_command(f"chown -R {APP_USER}:www-data {APP_DIR}", "Setting permissions")
    
    start_services()
    
    print_success("Application rolled back successfully")
    return True

def cleanup_old_backups():
    """Clean up old backup files."""
    print_header("CLEANING UP OLD BACKUPS")
    
    # Keep only last 10 backups
    run_command(f"find {BACKUP_DIR} -name 'app_backup_*' -type d | sort | head -n -10 | xargs rm -rf", 
                "Removing old backups", check=False)
    
    print_success("Old backups cleaned up")

def main():
    parser = argparse.ArgumentParser(description='Update Dewata Motor Application')
    parser.add_argument('--backup', action='store_true', help='Create backup before update')
    parser.add_argument('--force', action='store_true', help='Force update even if up to date')
    parser.add_argument('--no-verify', action='store_true', help='Skip verification after update')
    args = parser.parse_args()
    
    print_header("DEWATA MOTOR UPDATE SCRIPT")
    
    # Check prerequisites
    check_root()
    check_prerequisites()
    
    # Get current version
    current_hash, current_branch = get_current_version()
    print_info(f"Current version: {current_hash} ({current_branch})")
    
    backup_path = None
    
    try:
        # Create backup if requested
        backup_path = backup_application(args.backup)
        
        # Stop services
        stop_services()
        
        # Update application
        updated = update_application()
        
        if not updated and not args.force:
            print_info("No updates available")
            start_services()
            return
        
        # Check for database updates
        check_database_updates()
        
        # Start services
        start_services()
        
        # Verify update
        if not args.no_verify:
            if not verify_update():
                print_error("Update verification failed")
                
                if backup_path:
                    response = input("Do you want to rollback? (y/N): ")
                    if response.lower() in ['y', 'yes']:
                        rollback_application(backup_path)
                        return
                
                sys.exit(1)
        
        # Get new version
        new_hash, new_branch = get_current_version()
        print_success(f"Update completed successfully!")
        print_info(f"Updated from {current_hash} to {new_hash}")
        
        # Cleanup old backups
        cleanup_old_backups()
        
    except KeyboardInterrupt:
        print_error("\nUpdate interrupted by user")
        
        if backup_path:
            response = input("Do you want to rollback? (y/N): ")
            if response.lower() in ['y', 'yes']:
                rollback_application(backup_path)
        
        sys.exit(1)
        
    except Exception as e:
        print_error(f"Update failed: {str(e)}")
        
        if backup_path:
            print_info("Attempting automatic rollback...")
            rollback_application(backup_path)
        
        sys.exit(1)

if __name__ == "__main__":
    main() 