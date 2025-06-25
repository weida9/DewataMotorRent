# Environment Setup Guide

## Instalasi Dependencies

Jalankan perintah berikut untuk menginstall dependency yang diperlukan:

```bash
pip install -r requirements.txt
```

## Setup Environment Variables

1. **Copy file template konfigurasi:**
   ```bash
   cp config.env.template .env
   ```

2. **Edit file `.env` sesuai dengan konfigurasi Anda:**
   
   Buka file `.env` dan ubah nilai-nilai berikut:

   ```env
   # Flask Configuration
   SECRET_KEY=ganti-dengan-secret-key-yang-aman
   DEBUG=True
   
   # Database Configuration
   DB_PASSWORD=password-mysql-anda
   
   # Untuk production, ubah konfigurasi berikut:
   FLASK_ENV=production
   DEBUG=False
   SESSION_COOKIE_SECURE=True
   ```

## Konfigurasi yang Tersedia

### Flask Configuration
- `FLASK_ENV`: Environment Flask (development/production)
- `SECRET_KEY`: Secret key untuk session (wajib diganti untuk production)
- `DEBUG`: Mode debug (True/False)
- `PORT`: Port aplikasi (default: 80)
- `HOST`: Host aplikasi (default: 0.0.0.0)

### Database Configuration
- `DB_HOST`: Host database (default: localhost)
- `DB_USER`: Username database (default: root)
- `DB_PASSWORD`: Password database (default: kosong)
- `DB_NAME`: Nama database (default: motordewata)
- `DB_CHARSET`: Charset database (default: utf8mb4)

### File Upload Configuration
- `UPLOAD_FOLDER`: Folder untuk upload file (default: static/uploads)
- `MAX_FILE_SIZE`: Ukuran maksimal file dalam bytes (default: 5242880 = 5MB)
- `ALLOWED_EXTENSIONS`: Ekstensi file yang diizinkan (default: png,jpg,jpeg,gif,webp)

### Security Configuration
- `SESSION_COOKIE_SECURE`: Cookie secure flag (default: False)
- `SESSION_COOKIE_HTTPONLY`: Cookie httponly flag (default: True)
- `SESSION_COOKIE_SAMESITE`: Cookie samesite policy (default: Lax)
- `SESSION_LIFETIME_HOURS`: Durasi session dalam jam (default: 2)

### Rate Limiting
- `RATE_LIMIT_ATTEMPTS`: Maksimal percobaan login (default: 5)
- `RATE_LIMIT_WINDOW`: Window rate limiting dalam detik (default: 300)

## Keamanan

⚠️ **PENTING:**
- Jangan commit file `.env` ke repository
- Selalu gunakan SECRET_KEY yang kuat untuk production
- Set `SESSION_COOKIE_SECURE=True` jika menggunakan HTTPS
- Set `DEBUG=False` untuk production

## Menjalankan Aplikasi

Setelah setup environment, jalankan aplikasi:

```bash
python app.py
```

Aplikasi akan membaca konfigurasi dari file `.env` secara otomatis. 