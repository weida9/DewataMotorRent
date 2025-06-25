#!/usr/bin/env python3
"""
Setup script untuk Dewata Motor Rental System
Membantu setup awal environment variables dan dependencies
"""

import os
import secrets
import subprocess
import sys

def print_banner():
    print("🏍️  Dewata Motor Rental - Setup Script")
    print("=" * 50)

def check_python_version():
    """Check if Python version is supported"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ diperlukan")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} terdeteksi")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies berhasil diinstall")
    except subprocess.CalledProcessError:
        print("❌ Gagal install dependencies")
        sys.exit(1)

def setup_environment():
    """Setup environment variables from template"""
    env_template = "config.env.template"
    env_file = ".env"
    
    if os.path.exists(env_file):
        print(f"\n⚠️  File {env_file} sudah ada")
        overwrite = input("Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            print("Setup environment diabaikan")
            return
    
    if not os.path.exists(env_template):
        print(f"❌ Template file {env_template} tidak ditemukan")
        return
    
    print(f"\n🔧 Membuat file {env_file} dari template...")
    
    # Read template
    with open(env_template, 'r') as f:
        content = f.read()
    
    # Generate secure secret key
    secret_key = secrets.token_hex(32)
    content = content.replace('generate-a-secure-secret-key-here', secret_key)
    
    # Ask for database password
    print("\n🔐 Konfigurasi Database:")
    db_password = input("Masukkan password MySQL (kosong jika tidak ada): ").strip()
    content = content.replace('your-database-password-here', db_password)
    
    # Write .env file
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✅ File {env_file} berhasil dibuat dengan secure secret key")

def check_database():
    """Check database connection"""
    print("\n🗄️  Checking database connection...")
    try:
        import pymysql
        from dotenv import load_dotenv
        
        load_dotenv()
        
        config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'motordewata'),
            'charset': os.getenv('DB_CHARSET', 'utf8mb4')
        }
        
        connection = pymysql.connect(**config)
        connection.close()
        print("✅ Database connection berhasil")
        
    except ImportError:
        print("⚠️  PyMySQL belum terinstall, install dependencies dulu")
    except Exception as e:
        print(f"❌ Database connection gagal: {e}")
        print("💡 Pastikan MySQL server berjalan dan database 'motordewata' sudah dibuat")

def create_upload_folder():
    """Create upload folder if not exists"""
    upload_folder = "static/uploads"
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"✅ Folder {upload_folder} berhasil dibuat")
    else:
        print(f"✅ Folder {upload_folder} sudah ada")

def print_next_steps():
    """Print next steps after setup"""
    print("\n🎉 Setup selesai!")
    print("\n📋 Langkah selanjutnya:")
    print("1. Pastikan MySQL server berjalan")
    print("2. Import database_schema.sql ke MySQL")
    print("3. Jalankan: python app.py")
    print("4. Buka http://localhost:80 di browser")
    print("\n👤 Default login:")
    print("   Username: superadmin")
    print("   Password: admin123")
    print("\n📚 Dokumentasi:")
    print("   - README.md")
    print("   - ENVIRONMENT_SETUP.md")
    print("   - SECURITY_CHECKLIST.md")

def main():
    print_banner()
    
    # Check requirements
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Setup environment
    setup_environment()
    
    # Create upload folder
    create_upload_folder()
    
    # Check database
    check_database()
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main() 