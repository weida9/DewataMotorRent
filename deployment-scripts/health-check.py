#!/usr/bin/env python3
"""
Dewata Motor Health Check Script
Monitors application health and sends alerts if issues are detected.

Usage: python3 health-check.py [--email your@email.com]
"""

import os
import sys
import subprocess
import requests
import json
import smtplib
import argparse
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
APP_NAME = "dewata-motor"
APP_URL = "http://localhost"
CREDENTIALS_FILE = f"/opt/{APP_NAME}/CREDENTIALS.json"
LOG_FILE = f"/var/log/{APP_NAME}-health.log"

class HealthChecker:
    def __init__(self, email=None):
        self.email = email
        self.issues = []
        self.warnings = []
        self.success_checks = []
        
    def log(self, message, level="INFO"):
        """Log message to file and console."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        
        print(log_message)
        
        try:
            with open(LOG_FILE, "a") as f:
                f.write(log_message + "\n")
        except:
            pass
    
    def run_command(self, command, description=""):
        """Run command and return result."""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except Exception as e:
            return False, "", str(e)
    
    def check_services(self):
        """Check if all required services are running."""
        services = ["apache2", "mysql", APP_NAME]
        
        for service in services:
            success, stdout, stderr = self.run_command(f"systemctl is-active {service}")
            if success and "active" in stdout:
                self.success_checks.append(f"✅ Service {service} is running")
            else:
                self.issues.append(f"❌ Service {service} is not running")
    
    def check_web_response(self):
        """Check if web application responds."""
        try:
            response = requests.get(APP_URL, timeout=10)
            if response.status_code == 200:
                self.success_checks.append("✅ Web application is responding")
            else:
                self.issues.append(f"❌ Web application returned status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            self.issues.append("❌ Cannot connect to web application")
        except requests.exceptions.Timeout:
            self.issues.append("❌ Web application response timeout")
        except Exception as e:
            self.issues.append(f"❌ Web application error: {str(e)}")
    
    def check_database_connection(self):
        """Check database connectivity."""
        try:
            if os.path.exists(CREDENTIALS_FILE):
                with open(CREDENTIALS_FILE, 'r') as f:
                    creds = json.load(f)
                
                db_user = creds.get('database_user')
                db_password = creds.get('database_password')
                db_name = creds.get('database_name')
                
                success, stdout, stderr = self.run_command(
                    f'mysql -u {db_user} -p{db_password} {db_name} -e "SELECT 1;" 2>/dev/null'
                )
                
                if success:
                    self.success_checks.append("✅ Database connection successful")
                else:
                    self.issues.append("❌ Database connection failed")
            else:
                self.warnings.append("⚠️ Credentials file not found")
        except Exception as e:
            self.issues.append(f"❌ Database check error: {str(e)}")
    
    def check_disk_space(self):
        """Check available disk space."""
        success, stdout, stderr = self.run_command("df -h / | tail -1 | awk '{print $5}' | sed 's/%//'")
        
        if success:
            try:
                usage = int(stdout)
                if usage > 90:
                    self.issues.append(f"❌ Disk usage is critical: {usage}%")
                elif usage > 80:
                    self.warnings.append(f"⚠️ Disk usage is high: {usage}%")
                else:
                    self.success_checks.append(f"✅ Disk usage is normal: {usage}%")
            except ValueError:
                self.warnings.append("⚠️ Could not check disk usage")
        else:
            self.warnings.append("⚠️ Could not check disk usage")
    
    def check_memory_usage(self):
        """Check memory usage."""
        success, stdout, stderr = self.run_command("free | grep Mem | awk '{print ($3/$2) * 100.0}'")
        
        if success:
            try:
                usage = float(stdout)
                if usage > 90:
                    self.issues.append(f"❌ Memory usage is critical: {usage:.1f}%")
                elif usage > 80:
                    self.warnings.append(f"⚠️ Memory usage is high: {usage:.1f}%")
                else:
                    self.success_checks.append(f"✅ Memory usage is normal: {usage:.1f}%")
            except ValueError:
                self.warnings.append("⚠️ Could not check memory usage")
        else:
            self.warnings.append("⚠️ Could not check memory usage")
    
    def check_log_errors(self):
        """Check for recent errors in logs."""
        log_files = [
            f"/var/log/apache2/{APP_NAME}_error.log",
            "/var/log/mysql/error.log"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                success, stdout, stderr = self.run_command(
                    f"tail -100 {log_file} | grep -i error | tail -5"
                )
                
                if success and stdout.strip():
                    self.warnings.append(f"⚠️ Recent errors in {log_file}")
                    for line in stdout.strip().split('\n')[:3]:  # Show only first 3 lines
                        self.warnings.append(f"   {line}")
    
    def check_ssl_certificate(self):
        """Check SSL certificate expiration."""
        success, stdout, stderr = self.run_command("certbot certificates 2>/dev/null")
        
        if success and "Certificate Name" in stdout:
            self.success_checks.append("✅ SSL certificates are configured")
            
            # Check expiration
            success, stdout, stderr = self.run_command(
                "certbot certificates 2>/dev/null | grep -A2 'Expiry Date' | head -1"
            )
            
            if success and stdout.strip():
                self.success_checks.append(f"✅ SSL certificate info: {stdout.strip()}")
        else:
            self.warnings.append("⚠️ No SSL certificates found")
    
    def run_all_checks(self):
        """Run all health checks."""
        self.log("Starting health check...", "INFO")
        
        self.check_services()
        self.check_web_response()
        self.check_database_connection()
        self.check_disk_space()
        self.check_memory_usage()
        self.check_log_errors()
        self.check_ssl_certificate()
        
        self.log("Health check completed", "INFO")
    
    def generate_report(self):
        """Generate health check report."""
        report = []
        report.append("🏍️ DEWATA MOTOR HEALTH CHECK REPORT")
        report.append("=" * 50)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        if self.issues:
            report.append("🚨 CRITICAL ISSUES:")
            for issue in self.issues:
                report.append(f"  {issue}")
            report.append("")
        
        if self.warnings:
            report.append("⚠️ WARNINGS:")
            for warning in self.warnings:
                report.append(f"  {warning}")
            report.append("")
        
        if self.success_checks:
            report.append("✅ SUCCESSFUL CHECKS:")
            for check in self.success_checks:
                report.append(f"  {check}")
            report.append("")
        
        # Overall status
        if self.issues:
            report.append("🔴 OVERALL STATUS: CRITICAL - Immediate attention required!")
        elif self.warnings:
            report.append("🟡 OVERALL STATUS: WARNING - Monitor closely")
        else:
            report.append("🟢 OVERALL STATUS: HEALTHY - All systems operational")
        
        return "\n".join(report)
    
    def send_email_alert(self, report):
        """Send email alert if configured."""
        if not self.email:
            return
        
        if not self.issues and not self.warnings:
            return  # Don't send email for successful checks
        
        try:
            # Email configuration (adjust as needed)
            smtp_server = "localhost"
            smtp_port = 25
            
            msg = MIMEMultipart()
            msg['From'] = f"{APP_NAME}@localhost"
            msg['To'] = self.email
            msg['Subject'] = f"🚨 Dewata Motor Health Alert - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            msg.attach(MIMEText(report, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.send_message(msg)
            server.quit()
            
            self.log(f"Alert email sent to {self.email}", "INFO")
            
        except Exception as e:
            self.log(f"Failed to send email: {str(e)}", "ERROR")

def main():
    parser = argparse.ArgumentParser(description='Dewata Motor Health Check')
    parser.add_argument('--email', help='Email address for alerts')
    parser.add_argument('--quiet', action='store_true', help='Suppress output except for issues')
    args = parser.parse_args()
    
    checker = HealthChecker(email=args.email)
    checker.run_all_checks()
    
    report = checker.generate_report()
    
    if not args.quiet or checker.issues or checker.warnings:
        print(report)
    
    # Log to file
    checker.log("Health check report:", "INFO")
    for line in report.split('\n'):
        checker.log(line, "INFO")
    
    # Send email if there are issues
    if checker.email and (checker.issues or checker.warnings):
        checker.send_email_alert(report)
    
    # Exit with appropriate code
    if checker.issues:
        sys.exit(2)  # Critical issues
    elif checker.warnings:
        sys.exit(1)  # Warnings
    else:
        sys.exit(0)  # All good

if __name__ == "__main__":
    main() 