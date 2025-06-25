from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import uuid
from PIL import Image
import secrets
import re
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))

# Security configurations from environment
app.config['SESSION_COOKIE_SECURE'] = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
app.config['SESSION_COOKIE_SAMESITE'] = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=int(os.getenv('SESSION_LIFETIME_HOURS', '2')))

# Upload configuration from environment
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'static/uploads')
ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,webp').split(','))
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', str(5 * 1024 * 1024)))  # Default 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Rate limiting configuration from environment
RATE_LIMIT_ATTEMPTS = int(os.getenv('RATE_LIMIT_ATTEMPTS', '5'))
RATE_LIMIT_WINDOW = int(os.getenv('RATE_LIMIT_WINDOW', '300'))  # 5 minutes in seconds

# Simple rate limiting (in memory - for production use Redis)
login_attempts = {}

def is_rate_limited(ip_address):
    """Check if IP is rate limited"""
    current_time = time.time()
    
    if ip_address not in login_attempts:
        login_attempts[ip_address] = []
    
    # Remove old attempts outside the window
    login_attempts[ip_address] = [
        attempt_time for attempt_time in login_attempts[ip_address]
        if current_time - attempt_time < RATE_LIMIT_WINDOW
    ]
    
    return len(login_attempts[ip_address]) >= RATE_LIMIT_ATTEMPTS

def record_login_attempt(ip_address):
    """Record a failed login attempt"""
    current_time = time.time()
    
    if ip_address not in login_attempts:
        login_attempts[ip_address] = []
    
    login_attempts[ip_address].append(current_time)

def validate_input(text, max_length=100, pattern=None):
    """Validate and sanitize input"""
    if not text or not isinstance(text, str):
        return False
    
    # Check length
    if len(text.strip()) > max_length:
        return False
    
    # Check pattern if provided
    if pattern and not re.match(pattern, text.strip()):
        return False
    
    return True

def sanitize_filename(filename):
    """Secure filename handling"""
    if not filename:
        return None
    
    # Use werkzeug's secure_filename
    filename = secure_filename(filename)
    
    # Additional validation
    if not filename or len(filename) > 100:
        return None
    
    return filename

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def resize_image(image_path, max_size=(800, 600)):
    """Resize image to max dimensions while maintaining aspect ratio"""
    try:
        with Image.open(image_path) as img:
            # Convert RGBA to RGB if needed
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Calculate new size maintaining aspect ratio
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save with optimized quality
            img.save(image_path, 'JPEG', quality=85, optimize=True)
            return True
    except Exception as e:
        print(f"Error resizing image: {e}")
        return False

def save_uploaded_file(file):
    """Save uploaded file securely and return filename"""
    if not file or not file.filename:
        return None
    
    # Sanitize filename
    original_filename = sanitize_filename(file.filename)
    if not original_filename or not allowed_file(original_filename):
        return None
    
    # Check file size (additional check)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        return None
    
    # Generate unique filename to prevent path traversal
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    # Ensure file path is within upload directory (prevent directory traversal)
    if not os.path.abspath(file_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
        return None
    
    try:
        # Save file
        file.save(file_path)
        
        # Verify it's actually an image by trying to process it
        try:
            with Image.open(file_path) as img:
                img.verify()  # Verify it's a valid image
        except Exception:
            # Not a valid image, delete and return None
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
        
        # Resize image (this also re-saves as JPEG, removing potential malicious content)
        if resize_image(file_path):
            return unique_filename
        else:
            # If resize fails, delete file and return None
            if os.path.exists(file_path):
                os.remove(file_path)
            return None
            
    except Exception as e:
        print(f"Error saving file: {e}")
        # Clean up on error
        if os.path.exists(file_path):
            os.remove(file_path)
        return None

def delete_uploaded_file(filename):
    """Delete uploaded file"""
    if filename:
        try:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"Error deleting file: {e}")
    return False

# Database configuration from environment
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'motordewata'),
    'charset': os.getenv('DB_CHARSET', 'utf8mb4')
}

def get_db_connection():
    """Get database connection"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu!', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def superadmin_required(f):
    """Decorator to check if user is superadmin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'superadmin':
            flash('Akses ditolak! Hanya superadmin yang dapat mengakses halaman ini.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def admin_only_required(f):
    """Decorator to check if user is admin only (not superadmin)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Akses ditolak! Hanya admin yang dapat mengakses halaman ini.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Security middleware
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'DENY'
    
    # Prevent MIME type sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # XSS Protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer Policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Content Security Policy (basic)
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;"
    
    return response

@app.before_request
def check_session_timeout():
    """Check if user session has timed out"""
    if 'user_id' in session and 'login_time' in session:
        try:
            login_time = datetime.fromisoformat(session['login_time'])
            if datetime.now() - login_time > app.config['PERMANENT_SESSION_LIFETIME']:
                session.clear()
                flash('Sesi Anda telah berakhir. Silakan login kembali.', 'warning')
                return redirect(url_for('login'))
        except (ValueError, TypeError):
            # Invalid login_time format, clear session
            session.clear()
            return redirect(url_for('login'))

@app.route('/')
def index():
    """Home page - redirect to login if not authenticated"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with security measures"""
    if request.method == 'POST':
        # Get client IP
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # Check rate limiting
        if is_rate_limited(client_ip):
            flash('Terlalu banyak percobaan login. Coba lagi dalam 5 menit.', 'danger')
            return render_template('login.html')
        
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate input
        if not validate_input(username, max_length=50, pattern=r'^[a-zA-Z0-9_]+$'):
            flash('Username tidak valid!', 'danger')
            record_login_attempt(client_ip)
            return render_template('login.html')
        
        if not password or len(password) > 200:
            flash('Password tidak valid!', 'danger')
            record_login_attempt(client_ip)
            return render_template('login.html')
        
        connection = get_db_connection()
        if not connection:
            flash('Koneksi database gagal!', 'danger')
            return render_template('login.html')
        
        try:
            with connection.cursor() as cursor:
                # Use parameterized query to prevent SQL injection
                cursor.execute("SELECT id, username, password, role FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user[2], password):
                    # Clear failed attempts on successful login
                    if client_ip in login_attempts:
                        del login_attempts[client_ip]
                    
                    # Set session with security
                    session.permanent = True
                    session['user_id'] = user[0]
                    session['username'] = user[1]
                    session['role'] = user[3]
                    session['login_time'] = datetime.now().isoformat()
                    
                    flash(f'Selamat datang, {user[1]}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    # Record failed attempt
                    record_login_attempt(client_ip)
                    flash('Username atau password salah!', 'danger')
        except Exception as e:
            flash('Terjadi kesalahan sistem!', 'danger')
            print(f"Login error: {e}")  # Log for debugging
        finally:
            connection.close()
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout and clear session"""
    session.clear()
    flash('Anda telah berhasil logout!', 'success')
    return redirect(url_for('login'))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    """Serve uploaded files with security check"""
    # Sanitize filename to prevent directory traversal
    filename = sanitize_filename(filename)
    if not filename:
        flash('File tidak ditemukan!', 'danger')
        return redirect(url_for('dashboard'))
    
    # Ensure file exists and is within upload directory
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path) or not os.path.abspath(file_path).startswith(os.path.abspath(app.config['UPLOAD_FOLDER'])):
        flash('File tidak ditemukan!', 'danger')
        return redirect(url_for('dashboard'))
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    dashboard_data = {}
    
    # Get motor statistics for admin users
    if session.get('role') == 'admin':
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Get motor statistics
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_motors,
                            SUM(CASE WHEN status = 'tersedia' THEN 1 ELSE 0 END) as available,
                            SUM(CASE WHEN status = 'disewa' THEN 1 ELSE 0 END) as rented,
                            SUM(CASE WHEN status = 'maintenance' THEN 1 ELSE 0 END) as maintenance
                        FROM motor WHERE admin_id = %s
                    """, (session['user_id'],))
                    stats = cursor.fetchone()
                    dashboard_data['stats'] = {
                        'total': stats[0] or 0,
                        'available': stats[1] or 0,
                        'rented': stats[2] or 0,
                        'maintenance': stats[3] or 0
                    }
                    
                    # Get recent motors (last 5 added)
                    cursor.execute("""
                        SELECT id, nama_motor, plat_nomor, status, deskripsi, gambar 
                        FROM motor WHERE admin_id = %s 
                        ORDER BY id DESC LIMIT 5
                    """, (session['user_id'],))
                    dashboard_data['recent_motors'] = cursor.fetchall()
                    
            except Exception as e:
                print(f"Dashboard stats error: {e}")
            finally:
                connection.close()
    
    # Get admin statistics for superadmin users
    elif session.get('role') == 'superadmin':
        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    # Get admin statistics only
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_admins
                        FROM users WHERE role = 'admin'
                    """)
                    admin_stats = cursor.fetchone()
                    
                    # Get total users (including superadmin)
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_users
                        FROM users
                    """)
                    user_stats = cursor.fetchone()
                    
                    dashboard_data['admin_stats'] = {
                        'total_admins': admin_stats[0] or 0,
                        'total_users': user_stats[0] or 0
                    }
                    
                    # Get recent admins (last 5 added)
                    cursor.execute("""
                        SELECT id, username, role 
                        FROM users WHERE role = 'admin' 
                        ORDER BY id DESC LIMIT 5
                    """)
                    dashboard_data['recent_admins'] = cursor.fetchall()
                    
            except Exception as e:
                print(f"Dashboard admin stats error: {e}")
            finally:
                connection.close()
    
    return render_template('dashboard.html', **dashboard_data)

@app.route('/users')
@superadmin_required
def users():
    """View all users (superadmin only)"""
    connection = get_db_connection()
    if not connection:
        flash('Koneksi database gagal!', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, role FROM users ORDER BY id")
            users_list = cursor.fetchall()
        return render_template('users.html', users=users_list)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        connection.close()

@app.route('/add_user', methods=['GET', 'POST'])
@superadmin_required
def add_user():
    """Add new admin user (superadmin only) with input validation"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '')
        
        # Validate input
        if not validate_input(username, max_length=50, pattern=r'^[a-zA-Z0-9_]+$'):
            flash('Username tidak valid! Gunakan hanya huruf, angka, dan underscore (max 50 karakter).', 'danger')
            return render_template('add_user.html')
        
        if not password or len(password) < 6 or len(password) > 100:
            flash('Password harus antara 6-100 karakter!', 'danger')
            return render_template('add_user.html')
        
        # Validasi: superadmin hanya bisa menambah admin
        if role != 'admin':
            flash('Superadmin hanya bisa menambah admin!', 'danger')
            return render_template('add_user.html')
        
        connection = get_db_connection()
        if not connection:
            flash('Koneksi database gagal!', 'danger')
            return render_template('add_user.html')
        
        try:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                             (username, hashed_password, role))
                connection.commit()
                flash(f'Admin {username} berhasil ditambahkan!', 'success')
                return redirect(url_for('users'))
        except pymysql.IntegrityError:
            flash('Username sudah ada!', 'danger')
        except Exception as e:
            flash('Terjadi kesalahan sistem!', 'danger')
            print(f"Add user error: {e}")
        finally:
            connection.close()
    
    return render_template('add_user.html')

@app.route('/motors')
@admin_only_required
def motors():
    """View all motors (admin only)"""
    connection = get_db_connection()
    if not connection:
        flash('Koneksi database gagal!', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        with connection.cursor() as cursor:
            # Hanya tampilkan motor milik admin yang login
            cursor.execute("SELECT id, nama_motor, plat_nomor, status, deskripsi, gambar FROM motor WHERE admin_id = %s ORDER BY id", 
                         (session['user_id'],))
            motors_list = cursor.fetchall()
        return render_template('motors.html', motors=motors_list)
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('dashboard'))
    finally:
        connection.close()

@app.route('/add_motor', methods=['GET', 'POST'])
@admin_only_required
def add_motor():
    """Add new motor (admin only)"""
    if request.method == 'POST':
        nama_motor = request.form['nama_motor']
        plat_nomor = request.form['plat_nomor']
        status = request.form['status']
        deskripsi = request.form['deskripsi']
        
        # Handle file upload
        gambar_filename = None
        if 'gambar' in request.files:
            file = request.files['gambar']
            if file.filename != '':
                if allowed_file(file.filename):
                    gambar_filename = save_uploaded_file(file)
                    if not gambar_filename:
                        flash('Gagal mengupload gambar! Pastikan format file benar (PNG, JPG, JPEG, GIF, WEBP) dan ukuran tidak lebih dari 5MB.', 'danger')
                        return render_template('add_motor.html')
                else:
                    flash('Format file tidak diizinkan! Gunakan PNG, JPG, JPEG, GIF, atau WEBP.', 'danger')
                    return render_template('add_motor.html')
        
        connection = get_db_connection()
        if not connection:
            flash('Koneksi database gagal!', 'danger')
            return render_template('add_motor.html')
        
        try:
            with connection.cursor() as cursor:
                # Tambahkan motor dengan admin_id dari session
                cursor.execute("INSERT INTO motor (nama_motor, plat_nomor, status, deskripsi, gambar, admin_id) VALUES (%s, %s, %s, %s, %s, %s)", 
                             (nama_motor, plat_nomor, status, deskripsi, gambar_filename, session['user_id']))
                connection.commit()
                flash(f'Motor {nama_motor} berhasil ditambahkan!', 'success')
                return redirect(url_for('motors'))
        except pymysql.IntegrityError:
            flash('Plat nomor sudah ada!', 'danger')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            connection.close()
    
    return render_template('add_motor.html')

@app.route('/edit_motor/<int:motor_id>', methods=['GET', 'POST'])
@admin_only_required
def edit_motor(motor_id):
    """Edit motor (admin only)"""
    connection = get_db_connection()
    if not connection:
        flash('Koneksi database gagal!', 'danger')
        return redirect(url_for('motors'))
    
    try:
        with connection.cursor() as cursor:
            # Cek apakah motor milik admin yang login
            cursor.execute("SELECT id, nama_motor, plat_nomor, status, deskripsi, gambar FROM motor WHERE id = %s AND admin_id = %s", 
                         (motor_id, session['user_id']))
            motor = cursor.fetchone()
            
            if not motor:
                flash('Motor tidak ditemukan atau bukan milik Anda!', 'danger')
                return redirect(url_for('motors'))
            
            if request.method == 'POST':
                nama_motor = request.form['nama_motor']
                plat_nomor = request.form['plat_nomor']
                status = request.form['status']
                deskripsi = request.form['deskripsi']
                
                # Handle file upload
                gambar_filename = motor[5]  # Keep existing image
                hapus_gambar = request.form.get('hapus_gambar') == 'on'
                
                if hapus_gambar:
                    # Delete existing image
                    if motor[5]:
                        delete_uploaded_file(motor[5])
                    gambar_filename = None
                elif 'gambar' in request.files:
                    file = request.files['gambar']
                    if file.filename != '':
                        if allowed_file(file.filename):
                            new_filename = save_uploaded_file(file)
                            if new_filename:
                                # Delete old image
                                if motor[5]:
                                    delete_uploaded_file(motor[5])
                                gambar_filename = new_filename
                            else:
                                flash('Gagal mengupload gambar! Pastikan format file benar dan ukuran tidak lebih dari 5MB.', 'danger')
                        else:
                            flash('Format file tidak diizinkan! Gunakan PNG, JPG, JPEG, GIF, atau WEBP.', 'danger')
                
                try:
                    cursor.execute("""UPDATE motor SET nama_motor = %s, plat_nomor = %s, status = %s, deskripsi = %s, gambar = %s 
                                    WHERE id = %s AND admin_id = %s""", 
                                 (nama_motor, plat_nomor, status, deskripsi, gambar_filename, motor_id, session['user_id']))
                    connection.commit()
                    flash(f'Motor {nama_motor} berhasil diupdate!', 'success')
                    return redirect(url_for('motors'))
                except pymysql.IntegrityError:
                    flash('Plat nomor sudah digunakan motor lain!', 'danger')
                except Exception as e:
                    flash(f'Error: {e}', 'danger')
            
            return render_template('edit_motor.html', motor=motor)
            
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('motors'))
    finally:
        connection.close()

@app.route('/delete_motor/<int:motor_id>', methods=['POST'])
@admin_only_required
def delete_motor(motor_id):
    """Delete motor (admin only)"""
    connection = get_db_connection()
    if not connection:
        flash('Koneksi database gagal!', 'danger')
        return redirect(url_for('motors'))
    
    try:
        with connection.cursor() as cursor:
            # Cek apakah motor milik admin yang login
            cursor.execute("SELECT nama_motor, gambar FROM motor WHERE id = %s AND admin_id = %s", 
                         (motor_id, session['user_id']))
            motor = cursor.fetchone()
            
            if not motor:
                flash('Motor tidak ditemukan atau bukan milik Anda!', 'danger')
            else:
                # Delete image file if exists
                if motor[1]:
                    delete_uploaded_file(motor[1])
                
                cursor.execute("DELETE FROM motor WHERE id = %s AND admin_id = %s", 
                             (motor_id, session['user_id']))
                connection.commit()
                flash(f'Motor {motor[0]} berhasil dihapus!', 'success')
                
    except Exception as e:
        flash(f'Error: {e}', 'danger')
    finally:
        connection.close()
    
    return redirect(url_for('motors'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user's own password with enhanced validation"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Enhanced validation
        if not current_password or len(current_password) > 200:
            flash('Password lama tidak valid!', 'danger')
            return render_template('change_password.html')
        
        if not new_password or len(new_password) < 6 or len(new_password) > 100:
            flash('Password baru harus antara 6-100 karakter!', 'danger')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('Password baru dan konfirmasi password tidak cocok!', 'danger')
            return render_template('change_password.html')
        
        connection = get_db_connection()
        if not connection:
            flash('Koneksi database gagal!', 'danger')
            return render_template('change_password.html')
        
        try:
            with connection.cursor() as cursor:
                # Get current user data
                cursor.execute("SELECT password FROM users WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                
                if not user or not check_password_hash(user[0], current_password):
                    flash('Password lama tidak benar!', 'danger')
                    return render_template('change_password.html')
                
                # Update password with stronger hashing
                hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                             (hashed_password, session['user_id']))
                connection.commit()
                
                flash('Password berhasil diubah!', 'success')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            flash('Terjadi kesalahan sistem!', 'danger')
            print(f"Change password error: {e}")
        finally:
            connection.close()
    
    return render_template('change_password.html')

@app.route('/edit_admin_password/<int:user_id>', methods=['GET', 'POST'])
@superadmin_required
def edit_admin_password(user_id):
    """Edit admin password (superadmin only)"""
    connection = get_db_connection()
    if not connection:
        flash('Koneksi database gagal!', 'danger')
        return redirect(url_for('users'))
    
    try:
        with connection.cursor() as cursor:
            # Get admin data
            cursor.execute("SELECT id, username, role FROM users WHERE id = %s AND role = 'admin'", (user_id,))
            admin = cursor.fetchone()
            
            if not admin:
                flash('Admin tidak ditemukan!', 'danger')
                return redirect(url_for('users'))
            
            if request.method == 'POST':
                new_password = request.form['new_password']
                confirm_password = request.form['confirm_password']
                
                # Validation
                if not new_password or not confirm_password:
                    flash('Semua field password harus diisi!', 'danger')
                    return render_template('edit_admin_password.html', admin=admin)
                
                if new_password != confirm_password:
                    flash('Password baru dan konfirmasi password tidak cocok!', 'danger')
                    return render_template('edit_admin_password.html', admin=admin)
                
                if len(new_password) < 6:
                    flash('Password baru harus minimal 6 karakter!', 'danger')
                    return render_template('edit_admin_password.html', admin=admin)
                
                # Update password
                hashed_password = generate_password_hash(new_password)
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                             (hashed_password, user_id))
                connection.commit()
                
                flash(f'Password admin {admin[1]} berhasil diubah!', 'success')
                return redirect(url_for('users'))
            
            return render_template('edit_admin_password.html', admin=admin)
            
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        return redirect(url_for('users'))
    finally:
        connection.close()

@app.route('/delete_admin/<int:user_id>', methods=['POST'])
@superadmin_required
def delete_admin(user_id):
    """Delete admin user (superadmin only)"""
    connection = get_db_connection()
    if not connection:
        flash('Koneksi database gagal!', 'danger')
        return redirect(url_for('users'))
    
    try:
        with connection.cursor() as cursor:
            # Get admin data to validate
            cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
            admin = cursor.fetchone()
            
            if not admin:
                flash('Admin tidak ditemukan!', 'danger')
                return redirect(url_for('users'))
            
            # Prevent deletion of superadmin accounts
            if admin[2] == 'superadmin':
                flash('Tidak dapat menghapus akun superadmin!', 'danger')
                return redirect(url_for('users'))
            
            # Prevent self-deletion (although superadmin shouldn't be admin role)
            if admin[0] == session['user_id']:
                flash('Tidak dapat menghapus akun Anda sendiri!', 'danger')
                return redirect(url_for('users'))
            
            # Check if admin has motors assigned
            cursor.execute("SELECT COUNT(*) FROM motor WHERE admin_id = %s", (user_id,))
            motor_count = cursor.fetchone()[0]
            
            if motor_count > 0:
                flash(f'Tidak dapat menghapus admin {admin[1]} karena masih memiliki {motor_count} motor yang terdaftar. Hapus atau pindahkan motor terlebih dahulu!', 'danger')
                return redirect(url_for('users'))
            
            # Delete the admin
            cursor.execute("DELETE FROM users WHERE id = %s AND role = 'admin'", (user_id,))
            connection.commit()
            
            if cursor.rowcount > 0:
                flash(f'Admin {admin[1]} berhasil dihapus!', 'success')
            else:
                flash('Gagal menghapus admin!', 'danger')
                
    except Exception as e:
        flash(f'Error: {e}', 'danger')
        print(f"Delete admin error: {e}")
    finally:
        connection.close()
    
    return redirect(url_for('users'))

if __name__ == '__main__':
    # Flask run configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '80'))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug) 