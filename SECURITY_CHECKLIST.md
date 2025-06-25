# Security Checklist

## ✅ Pre-Deployment Security Checklist

### Environment Variables
- [ ] File `.env` sudah dibuat dari `config.env.template`
- [ ] `SECRET_KEY` sudah diubah dari default (minimal 32 karakter random)
- [ ] `DB_PASSWORD` sudah diset dengan password MySQL yang benar
- [ ] File `.env` **TIDAK** ter-commit ke repository (ada di `.gitignore`)

### Production Configuration
- [ ] `FLASK_ENV=production` (untuk production)
- [ ] `DEBUG=False` (untuk production)
- [ ] `SESSION_COOKIE_SECURE=True` (jika menggunakan HTTPS)
- [ ] Database password tidak menggunakan default XAMPP

### Database Security
- [ ] Database user memiliki privilege minimal yang diperlukan
- [ ] Database tidak menggunakan user `root` untuk production
- [ ] Password database cukup kuat (minimal 12 karakter)

### File Security
- [ ] Folder `static/uploads/` sudah ada dan memiliki permission yang benar
- [ ] Tidak ada file sensitif di folder uploads
- [ ] File uploads memiliki validasi yang ketat

### General Security
- [ ] Semua dependencies sudah update ke versi terbaru
- [ ] Rate limiting sudah dikonfigurasi dengan benar
- [ ] Session timeout sudah dikonfigurasi sesuai kebutuhan

## ⚠️ Files Yang TIDAK Boleh Di-Commit

```
# Jangan commit files ini:
.env
.env.local
.env.production
*.env
database_backup/
logs/
```

## 🔒 Best Practices

### Secret Key Generation
Gunakan salah satu cara ini untuk generate secret key yang aman:

```python
# Cara 1: Python
import secrets
print(secrets.token_hex(32))

# Cara 2: Command line
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database Credentials
- Jangan gunakan password kosong atau default
- Gunakan user database khusus dengan privilege terbatas
- Backup database secara teratur

### HTTPS Configuration
Untuk production dengan HTTPS:
```env
SESSION_COOKIE_SECURE=True
FLASK_ENV=production
DEBUG=False
```

## 🚨 Emergency Response

Jika credentials ter-leak:
1. Segera ganti `SECRET_KEY` di file `.env`
2. Ganti password database
3. Revoke dan regenerate API keys (jika ada)
4. Monitor logs untuk aktivitas mencurigakan
5. Inform users untuk logout dan login ulang 