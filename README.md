# 🏍️ Dewata Motor - Sistem Rental Motor

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)](https://flask.palletsprojects.com)
[![MySQL](https://img.shields.io/badge/MySQL-5.7%2B-orange.svg)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.0-38B2AC.svg)](https://tailwindcss.com)

Sistem manajemen rental motor modern dan responsif yang dibangun dengan Flask dan MySQL. Dilengkapi dengan fitur autentikasi berbasis role, manajemen motor dengan upload gambar, dan antarmuka yang user-friendly.

## ✨ Highlights

- 🔐 **Secure Authentication** - Session-based dengan role management
- 📱 **Responsive Design** - Mobile-first dengan Tailwind CSS
- 🖼️ **Image Management** - Upload, resize, dan preview gambar motor
- 👥 **Multi-Role System** - Superadmin dan Admin dengan akses berbeda
- 🚗 **Motor Management** - CRUD lengkap dengan status tracking
- 🔑 **Password Management** - Ganti password sendiri dan admin

## 📋 Fitur

- **Autentikasi berbasis Session** - Login/logout dengan keamanan session
- **Role-based Access Control**:
  - **Superadmin**: Dapat melihat & menambah akun admin
  - **Admin**: Dapat melihat & menambah data motor
- **Manajemen User** - CRUD untuk akun pengguna
- **Manajemen Motor** - CRUD untuk data motor rental
- **Dashboard Interaktif** - Tampilan ringkasan dengan Tailwind CSS

## 🛠️ Teknologi

- **Backend**: Flask (Python)
- **Database**: MySQL
- **Frontend**: HTML + Tailwind CSS (via CDN)
- **Authentication**: Session-based (tanpa JWT)

## 📦 Persyaratan

- Python 3.7+
- MySQL Server
- XAMPP/phpMyAdmin (opsional untuk manajemen database)

## 🚀 Quick Deployment

### 🎯 Ubuntu Server (One-Click Install)

**Deployment super mudah tanpa perlu domain:**

```bash
# Option 1: Download dan jalankan
wget https://raw.githubusercontent.com/weida9/DewataMotorRent/main/install.sh
sudo bash install.sh

# Option 2: Direct run (Recommended)
curl -sSL https://raw.githubusercontent.com/weida9/DewataMotorRent/main/install.sh | sudo bash
```

**✅ Yang akan terinstall otomatis:**
- Apache2 + mod_wsgi
- MySQL 8.0+ + phpMyAdmin
- Python 3.8+ + dependencies
- UFW Firewall + security headers
- Complete aplikasi dengan sample data

**🌐 Setelah instalasi selesai:**
- **Akses aplikasi**: `http://IP_SERVER_ANDA`
- **phpMyAdmin**: `http://IP_SERVER_ANDA/phpmyadmin`
- **Login**: `superadmin` / `admin123`

### 🖥️ Local Development

### 1. Clone/Download Project
```bash
# Download atau extract project ke folder lokal
cd DewataMotorRent
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
- Jalankan XAMPP atau MySQL Server
- Buka phpMyAdmin atau MySQL client
- Import file `database_schema.sql`:
  ```sql
  # Buka phpMyAdmin -> Import -> Pilih file database_schema.sql
  ```

### 4. Konfigurasi Database (Opsional)
Jika menggunakan konfigurasi MySQL yang berbeda, edit file `app.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Sesuaikan dengan password MySQL Anda
    'database': 'motordewata',
    'charset': 'utf8mb4'
}
```

### 5. Jalankan Aplikasi
```bash
python app.py
```

Aplikasi akan berjalan di: `http://localhost:5000`

## 👤 Akun Default

| Role | Username | Password |
|------|----------|----------|
| Superadmin | `superadmin` | `admin123` |
| Admin | `admin` | `admin123` |

## 📊 Struktur Database

### Tabel `users`
| Field | Type | Description |
|-------|------|-------------|
| id | INT (PK) | ID unik user |
| username | VARCHAR(50) | Username untuk login |
| password | VARCHAR(255) | Password ter-hash |
| role | ENUM | 'superadmin' atau 'admin' |

### Tabel `motor`
| Field | Type | Description |
|-------|------|-------------|
| id | INT (PK) | ID unik motor |
| nama_motor | VARCHAR(100) | Nama/merk motor |
| plat_nomor | VARCHAR(20) | Plat nomor kendaraan |
| status | ENUM | 'tersedia', 'disewa', 'maintenance' |

## 🎯 Cara Penggunaan

### Login
1. Buka `http://localhost:5000`
2. Masukkan username dan password
3. Klik "Masuk"

### Superadmin
- **Dashboard**: Lihat ringkasan sistem
- **Kelola User**: Tambah/lihat akun admin
- **Kelola Motor**: Tambah/lihat data motor

### Admin
- **Dashboard**: Lihat ringkasan sistem
- **Kelola Motor**: Tambah/lihat data motor

## 📁 Struktur Project

```
DewataMotorRent/
├── app.py                 # Main Flask application
├── requirements.txt       # Dependencies Python
├── database_schema.sql    # Schema & data awal database
├── README.md             # Dokumentasi ini
└── templates/            # Template HTML
    ├── base.html         # Template dasar
    ├── login.html        # Halaman login
    ├── dashboard.html    # Dashboard utama
    ├── users.html        # Daftar user
    ├── add_user.html     # Form tambah user
    ├── motors.html       # Daftar motor
    └── add_motor.html    # Form tambah motor
```

## 🔧 Troubleshooting

### Error Database Connection
- Pastikan MySQL Server berjalan
- Periksa konfigurasi database di `app.py`
- Pastikan database `motordewata` sudah dibuat

### Error Import Module
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error Port 5000 Sudah Digunakan
Edit file `app.py` di bagian akhir:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Ganti port
```

## 📝 Catatan Pengembangan

- Aplikasi ini dibuat sesederhana mungkin sesuai requirement
- Semua logika backend ada di satu file `app.py`
- Tidak menggunakan JWT, REST API, atau struktur MVC
- Menggunakan Tailwind CSS via CDN untuk styling
- Session-based authentication untuk keamanan

## 🤝 Contributing

Kami menyambut kontribusi dari komunitas! Silakan baca [CONTRIBUTING.md](CONTRIBUTING.md) untuk panduan lengkap.

### Quick Start untuk Contributors
1. Fork repository ini
2. Buat branch baru: `git checkout -b feature/amazing-feature`
3. Commit perubahan: `git commit -m 'feat: add amazing feature'`
4. Push ke branch: `git push origin feature/amazing-feature`
5. Submit Pull Request

## 📊 Project Stats

- **Lines of Code**: ~500+ lines
- **Templates**: 11 HTML files
- **Database Tables**: 2 tables
- **Sample Data**: 6 users, 31 motors
- **Dependencies**: 4 main packages

## 🗺️ Roadmap

- [ ] API endpoints untuk mobile app
- [ ] Real-time notifications
- [ ] Advanced reporting dashboard
- [ ] Multi-language support
- [ ] Integration dengan payment gateway
- [ ] Automated backup system

## 📧 Support

Jika ada pertanyaan atau masalah:
- 🐛 **Bug Reports**: [Create an Issue](../../issues/new)
- 💡 **Feature Requests**: [Create an Issue](../../issues/new)
- 📖 **Documentation**: [Wiki](../../wiki)
- 💬 **Discussions**: [GitHub Discussions](../../discussions)

## 📄 License

Project ini dilisensikan di bawah [MIT License](LICENSE).

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Tailwind CSS](https://tailwindcss.com/) - CSS framework
- [Heroicons](https://heroicons.com/) - Beautiful icons
- [MySQL](https://mysql.com/) - Database system

---
**© 2025 Dewata Motor. Made with ❤️ for rental management.** 