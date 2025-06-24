# 🏍️ Dewata Motor - Sistem Rental Motor

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-5.7%2B-orange.svg)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC.svg)](https://tailwindcss.com)

Sistem manajemen rental motor modern dan responsif yang dibangun dengan Flask dan MySQL. Dilengkapi dengan fitur autentikasi berbasis role, manajemen motor dengan upload gambar, dan antarmuka yang user-friendly.

## ✨ Highlights

- 🔐 **Secure Authentication** - Session-based dengan role management dan rate limiting
- 📱 **Responsive Design** - Mobile-first dengan Tailwind CSS yang modern
- 🖼️ **Image Management** - Upload, resize, preview, dan manajemen gambar motor
- 👥 **Multi-Role System** - Superadmin dan Admin dengan akses berbeda
- 🚗 **Motor Management** - CRUD lengkap dengan status tracking dan deskripsi
- 🔑 **Password Management** - Ganti password sendiri dan admin
- 🛡️ **Security Features** - Rate limiting, XSS protection, secure file upload
- 📊 **Data Isolation** - Setiap admin hanya melihat data motornya sendiri

## 📋 Fitur Lengkap

### 🔐 Sistem Autentikasi
- **Login/Logout** dengan session-based security
- **Role-based Access Control** (Superadmin vs Admin)
- **Rate Limiting** untuk mencegah brute force attack
- **Session timeout** untuk keamanan ekstra
- **Password change** untuk semua user

### 👥 Manajemen User (Superadmin Only)
- **Lihat daftar user** dengan informasi role
- **Tambah admin baru** (superadmin tidak bisa buat superadmin lain)
- **Edit password admin** untuk reset akses
- **Validasi input** dan sanitasi data

### 🏍️ Manajemen Motor (Admin Only)
- **CRUD lengkap**: Create, Read, Update, Delete motor
- **Upload gambar** dengan validasi dan resize otomatis
- **Status tracking**: Tersedia, Disewa, Maintenance
- **Deskripsi detail** untuk setiap motor
- **Data isolation**: Admin hanya melihat motor miliknya
- **Preview gambar** dengan modal view

### 🎨 User Interface
- **Responsive design** untuk desktop, tablet, dan mobile
- **Modern UI** dengan Tailwind CSS dan Inter font
- **Dashboard interaktif** dengan statistik real-time
- **Dark/light mode** compatible
- **Smooth animations** dan hover effects
- **Flash messaging** untuk feedback user

### 🛡️ Keamanan
- **Secure file upload** dengan validasi extensi dan size
- **Image processing** untuk mencegah malicious file
- **XSS protection** dengan proper templating
- **CSRF protection** (Flask built-in)
- **Password hashing** dengan Werkzeug
- **Input validation** dan sanitasi

## 🛠️ Teknologi

- **Backend**: Flask 2.3.3 (Python)
- **Database**: MySQL dengan PyMySQL connector
- **Frontend**: HTML5 + Tailwind CSS 3.0 (via CDN)
- **Image Processing**: Pillow (PIL)
- **Security**: Werkzeug, Session-based auth
- **Development**: Black, Pytest, Flake8

## 📦 Persyaratan Sistem

- **Python 3.8+**
- **MySQL Server 5.7+**
- **Minimum 1GB RAM**
- **Minimum 100MB disk space**
- **XAMPP/phpMyAdmin** (opsional untuk manajemen database)

## 🚀 Instalasi & Setup

### 🎯 Quick Setup Local

```bash
# 1. Clone atau download project
git clone <repository-url>
cd DewataMotorRent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup database MySQL
# Buka XAMPP -> Start MySQL
# Buka phpMyAdmin -> Import database_schema.sql

# 4. Konfigurasi database (jika perlu)
# Edit app.py bagian DB_CONFIG sesuai setup MySQL Anda

# 5. Jalankan aplikasi
python app.py
```

**Aplikasi berjalan di**: `http://localhost:5000`

### 🔧 Konfigurasi Database

Update konfigurasi di `app.py` jika diperlukan:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Bambang0912',  # Sesuaikan dengan password MySQL Anda
    'database': 'motordewata',
    'charset': 'utf8mb4'
}
```

## 👤 Akun Default

| Role | Username | Password | Akses |
|------|----------|----------|--------|
| **Superadmin** | `superadmin` | `admin123` | Kelola admin, lihat semua data |
| **Admin** | `admin_denpasar` | `admin123` | Kelola motor area Denpasar |
| **Admin** | `admin_ubud` | `admin123` | Kelola motor area Ubud |
| **Admin** | `admin_sanur` | `admin123` | Kelola motor area Sanur |
| **Admin** | `admin_kuta` | `admin123` | Kelola motor area Kuta |
| **Admin** | `admin_seminyak` | `admin123` | Kelola motor area Seminyak |

> **Note**: Setiap admin memiliki data motor terpisah (data isolation)

## 📊 Struktur Database

### Tabel `users`
| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | ID unik user |
| username | VARCHAR(50) | NOT NULL, UNIQUE | Username untuk login |
| password | VARCHAR(255) | NOT NULL | Password ter-hash (Werkzeug) |
| role | ENUM('superadmin', 'admin') | NOT NULL | Role pengguna |

### Tabel `motor`
| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| id | INT | PRIMARY KEY, AUTO_INCREMENT | ID unik motor |
| nama_motor | VARCHAR(100) | NOT NULL | Nama/merk motor |
| plat_nomor | VARCHAR(20) | NOT NULL, UNIQUE | Plat nomor kendaraan |
| status | ENUM | DEFAULT 'tersedia' | Status: tersedia/disewa/maintenance |
| deskripsi | TEXT | NULL | Deskripsi detail motor |
| gambar | VARCHAR(255) | NULL | Nama file gambar |
| admin_id | INT | FOREIGN KEY | ID admin pemilik data |

## 🎯 Cara Penggunaan

### 🔐 Login ke Sistem
1. Buka `http://localhost:5000`
2. Masukkan username dan password
3. Sistem akan redirect sesuai role

### 👑 Fitur Superadmin
- **Dashboard**: Statistik total user dan motor di sistem
- **Kelola User**: 
  - Lihat semua admin yang terdaftar
  - Tambah admin baru untuk area/cabang
  - Edit password admin (reset akses)
- **Keamanan**:
  - Tidak bisa membuat superadmin baru
  - Tidak bisa melihat/edit data motor langsung

### 🔧 Fitur Admin
- **Dashboard**: Statistik motor milik admin tersebut
- **Kelola Motor**:
  - Lihat daftar motor dengan gambar
  - Tambah motor baru dengan upload gambar
  - Edit data motor (nama, plat, status, deskripsi, gambar)
  - Hapus motor yang tidak digunakan
  - Preview gambar dalam modal
- **Data Isolation**: Hanya melihat motor yang di-assign ke admin tersebut

### 🔑 Manajemen Password
- **Ganti Password**: Semua user bisa ganti password sendiri
- **Reset Password Admin**: Superadmin bisa reset password admin

## 📁 Struktur Project

```
DewataMotorRent/
├── 📄 app.py                 # Main Flask application (798 lines)
├── 📄 requirements.txt       # Production dependencies
├── 📄 requirements-dev.txt   # Development dependencies
├── 📄 database_schema.sql    # Complete database schema + sample data
├── 📄 README.md             # Dokumentasi lengkap (ini)
├── 📄 CHANGELOG.md          # Riwayat perubahan
├── 📄 CONTRIBUTING.md       # Panduan kontribusi
├── 📄 LICENSE               # MIT License
├── 📁 static/
│   └── 📁 uploads/          # Folder untuk upload gambar motor
└── 📁 templates/            # Template HTML
    ├── 📄 base.html         # Template dasar dengan navbar
    ├── 📄 login.html        # Halaman login
    ├── 📄 dashboard.html    # Dashboard utama
    ├── 📄 users.html        # Daftar user (superadmin)
    ├── 📄 add_user.html     # Form tambah admin
    ├── 📄 motors.html       # Daftar motor dengan gambar
    ├── 📄 add_motor.html    # Form tambah motor
    ├── 📄 edit_motor.html   # Form edit motor
    ├── 📄 change_password.html      # Form ganti password
    └── 📄 edit_admin_password.html  # Form edit password admin
```

## 🔧 Troubleshooting

### ❌ Error Database Connection
```bash
# Pastikan MySQL berjalan
sudo systemctl start mysql  # Linux
# Atau jalankan XAMPP

# Periksa konfigurasi di app.py
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password_anda',  # Update ini
    'database': 'motordewata'
}
```

### ❌ Error Import Module
```bash
pip install --upgrade pip
pip install -r requirements.txt

# Jika masih error, coba virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### ❌ Error Upload Gambar
- Pastikan folder `static/uploads/` exist dan writable
- Cek ukuran file (max 5MB)
- Format yang didukung: PNG, JPG, JPEG, GIF, WEBP

### ❌ Error Port 5000 Sudah Digunakan
```python
# Edit app.py bagian akhir
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Ganti port
```

## 🚀 Fitur Lanjutan

### 🖼️ Manajemen Gambar
- **Auto-resize** ke 800x600px dengan maintain aspect ratio
- **Format conversion** ke JPEG untuk optimasi
- **Secure filename** dengan UUID untuk mencegah conflict
- **File validation** untuk mencegah upload file berbahaya
- **Compression** dengan quality 85% untuk balance size-quality

### 🛡️ Keamanan Lanjutan
- **Rate limiting**: Max 5 login attempts per 5 menit per IP
- **Session timeout**: Otomatis logout setelah 2 jam
- **XSS protection**: Auto-escape template variables
- **File upload security**: Validasi type, size, dan content
- **Path traversal protection**: Secure file path handling

### 📱 Responsive Design
- **Mobile-first**: Optimized untuk device kecil
- **Breakpoints**: sm (640px), md (768px), lg (1024px), xl (1280px)
- **Touch-friendly**: Button dan form optimal untuk touch
- **Fast loading**: Optimized images dan minimal CSS

## 📚 Documentation

Dokumentasi lengkap tersedia dalam beberapa file:

- 📖 **[README.md](README.md)** - Panduan utama dan overview
- 📋 **[CHANGELOG.md](CHANGELOG.md)** - Riwayat perubahan dan update
- 🤝 **[CONTRIBUTING.md](CONTRIBUTING.md)** - Panduan kontribusi developer
- 🔌 **[API_REFERENCE.md](API_REFERENCE.md)** - Dokumentasi endpoint dan API
- 🚀 **[DEPLOYMENT.md](DEPLOYMENT.md)** - Panduan deployment production
- ⚖️ **[LICENSE](LICENSE)** - MIT License

## 🤝 Contributing

Kontribusi sangat diterima! Baca [CONTRIBUTING.md](CONTRIBUTING.md) untuk panduan:

- 🐛 **Bug reports** - Gunakan issue template
- 💡 **Feature requests** - Jelaskan kebutuhan dan solusi
- 🔧 **Code contributions** - Follow coding standards
- 📝 **Documentation** - Improve atau translate docs

## 📄 License

Project ini menggunakan [MIT License](LICENSE). Bebas digunakan untuk komersial dan non-komersial.

## 📞 Support

- **Issues**: Gunakan GitHub Issues untuk bug report
- **Email**: [your-email@domain.com]
- **Documentation**: Baca CHANGELOG.md untuk riwayat update

---

**Dibuat dengan ❤️ menggunakan Flask & Tailwind CSS**

> 🌟 **Star** project ini jika bermanfaat! 