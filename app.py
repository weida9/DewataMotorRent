from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import uuid
from PIL import Image

app = Flask(__name__)
app.secret_key = 'dewata_motor_secret_key_2025'

# Upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    """Save uploaded file and return filename"""
    if file and allowed_file(file.filename):
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            # Save file
            file.save(file_path)
            
            # Resize image
            if resize_image(file_path):
                return unique_filename
            else:
                # If resize fails, delete file and return None
                if os.path.exists(file_path):
                    os.remove(file_path)
                return None
                
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
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

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Bambang0912',  # Default XAMPP MySQL password is empty
    'database': 'motordewata',
    'charset': 'utf8mb4'
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

@app.route('/')
def index():
    """Home page - redirect to login if not authenticated"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        connection = get_db_connection()
        if not connection:
            flash('Koneksi database gagal!', 'danger')
            return render_template('login.html')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, username, password, role FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user[2], password):
                    session['user_id'] = user[0]
                    session['username'] = user[1]
                    session['role'] = user[3]
                    flash(f'Selamat datang, {user[1]}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Username atau password salah!', 'danger')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
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
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

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
    """Add new admin user (superadmin only)"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        # Validasi: superadmin hanya bisa menambah admin
        if role != 'admin':
            flash('Superadmin hanya bisa menambah admin!', 'danger')
            return render_template('add_user.html')
        
        connection = get_db_connection()
        if not connection:
            flash('Koneksi database gagal!', 'danger')
            return render_template('add_user.html')
        
        try:
            hashed_password = generate_password_hash(password)
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)", 
                             (username, hashed_password, role))
                connection.commit()
                flash(f'Admin {username} berhasil ditambahkan!', 'success')
                return redirect(url_for('users'))
        except pymysql.IntegrityError:
            flash('Username sudah ada!', 'danger')
        except Exception as e:
            flash(f'Error: {e}', 'danger')
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
    """Change user's own password"""
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Validation
        if not current_password or not new_password or not confirm_password:
            flash('Semua field password harus diisi!', 'danger')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('Password baru dan konfirmasi password tidak cocok!', 'danger')
            return render_template('change_password.html')
        
        if len(new_password) < 6:
            flash('Password baru harus minimal 6 karakter!', 'danger')
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
                
                # Update password
                hashed_password = generate_password_hash(new_password)
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", 
                             (hashed_password, session['user_id']))
                connection.commit()
                
                flash('Password berhasil diubah!', 'success')
                return redirect(url_for('dashboard'))
                
        except Exception as e:
            flash(f'Error: {e}', 'danger')
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

if __name__ == '__main__':
    app.run(debug=True) 