# 🔌 API Reference - Dewata Motor

Dokumentasi lengkap untuk semua endpoint dan fungsi dalam sistem rental motor Dewata Motor.

## 📋 Overview

- **Base URL**: `http://localhost:5000`
- **Authentication**: Session-based (cookies)
- **Content-Type**: `application/x-www-form-urlencoded` (forms), `multipart/form-data` (file upload)
- **Response Format**: HTML pages dengan redirect untuk POST operations

## 🔐 Authentication

### Login
```http
POST /login
```

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | Username untuk login |
| `password` | string | Yes | Password user |

**Response:**
- **Success**: Redirect ke `/dashboard`
- **Error**: Redirect ke `/login` dengan flash message

**Rate Limiting:** 5 attempts per 5 minutes per IP address

---

### Logout
```http
GET /logout
```

**Authentication Required:** Yes

**Response:**
- Redirect ke `/login` dengan session cleared

---

## 👤 User Management (Superadmin Only)

### View Users
```http
GET /users
```

**Authentication Required:** Superadmin role

**Response:** HTML page dengan daftar semua users

---

### Add User
```http
GET /add_user
POST /add_user
```

**Authentication Required:** Superadmin role

**GET Response:** Form untuk tambah user

**POST Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `username` | string | Yes | Username baru (3-50 karakter) |
| `password` | string | Yes | Password (minimum 6 karakter) |
| `role` | string | Yes | Role: 'admin' only (superadmin tidak bisa buat superadmin) |

**POST Response:**
- **Success**: Redirect ke `/users` dengan success message
- **Error**: Redirect ke `/add_user` dengan error message

---

## 🏍️ Motor Management (Admin Only)

### View Motors
```http
GET /motors
```

**Authentication Required:** Admin role

**Response:** HTML page dengan daftar motor milik admin yang login

**Features:**
- Image preview dengan modal
- Status color coding
- Pagination (jika diperlukan)

---

### Add Motor
```http
GET /add_motor
POST /add_motor
```

**Authentication Required:** Admin role

**GET Response:** Form untuk tambah motor

**POST Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nama_motor` | string | Yes | Nama/merk motor (max 100 karakter) |
| `plat_nomor` | string | Yes | Plat nomor unik (max 20 karakter) |
| `status` | enum | Yes | 'tersedia', 'disewa', 'maintenance' |
| `deskripsi` | text | No | Deskripsi detail motor |
| `gambar` | file | No | Image file (PNG, JPG, JPEG, GIF, WEBP, max 5MB) |

**File Upload Specifications:**
- **Max Size**: 5MB
- **Allowed Types**: PNG, JPG, JPEG, GIF, WEBP
- **Auto Processing**: Resize to 800x600px, convert to JPEG
- **Security**: Virus scan, content validation, secure filename

**POST Response:**
- **Success**: Redirect ke `/motors` dengan success message
- **Error**: Redirect ke `/add_motor` dengan error message

---

### Edit Motor
```http
GET /edit_motor/<motor_id>
POST /edit_motor/<motor_id>
```

**Authentication Required:** Admin role (can only edit own motors)

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `motor_id` | integer | ID motor yang akan diedit |

**GET Response:** Form untuk edit motor dengan data existing

**POST Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `nama_motor` | string | Yes | Nama/merk motor |
| `plat_nomor` | string | Yes | Plat nomor (harus unik) |
| `status` | enum | Yes | Status motor |
| `deskripsi` | text | No | Deskripsi motor |
| `gambar` | file | No | Image baru (optional, keep existing if not provided) |

**POST Response:**
- **Success**: Redirect ke `/motors` dengan success message
- **Error**: Redirect ke `/edit_motor/<motor_id>` dengan error message

---

### Delete Motor
```http
POST /delete_motor/<motor_id>
```

**Authentication Required:** Admin role (can only delete own motors)

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `motor_id` | integer | ID motor yang akan dihapus |

**Response:**
- **Success**: Redirect ke `/motors` dengan success message
- **Error**: Redirect ke `/motors` dengan error message

**Note:** File gambar juga akan dihapus dari server

---

## 🔑 Password Management

### Change Password (All Users)
```http
GET /change_password
POST /change_password
```

**Authentication Required:** Any logged-in user

**GET Response:** Form ganti password

**POST Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `current_password` | string | Yes | Password saat ini |
| `new_password` | string | Yes | Password baru (min 6 karakter) |
| `confirm_password` | string | Yes | Konfirmasi password baru |

**POST Response:**
- **Success**: Redirect ke `/dashboard` dengan success message
- **Error**: Redirect ke `/change_password` dengan error message

---

### Edit Admin Password (Superadmin Only)
```http
GET /edit_admin_password/<user_id>
POST /edit_admin_password/<user_id>
```

**Authentication Required:** Superadmin role

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `user_id` | integer | ID admin yang passwordnya akan diedit |

**GET Response:** Form edit password admin

**POST Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `new_password` | string | Yes | Password baru untuk admin |
| `confirm_password` | string | Yes | Konfirmasi password baru |

**POST Response:**
- **Success**: Redirect ke `/users` dengan success message
- **Error**: Redirect ke `/edit_admin_password/<user_id>` dengan error message

---

## 📊 Dashboard

### Main Dashboard
```http
GET /dashboard
```

**Authentication Required:** Any logged-in user

**Response:** Dashboard dengan statistik berdasarkan role:

**Superadmin Dashboard:**
- Total users di sistem
- Total motors di sistem
- Quick actions: Kelola User
- Recent activity summary

**Admin Dashboard:**
- Total motors milik admin
- Motor breakdown by status (Tersedia/Disewa/Maintenance)
- Quick actions: Kelola Motor, Tambah Motor
- Recent motor activities

---

## 📁 File Management

### View Uploaded Files
```http
GET /uploads/<filename>
```

**Authentication Required:** Any logged-in user

**URL Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | Nama file gambar |

**Response:** Image file dengan proper content-type

**Security:** 
- Path traversal protection
- File existence validation
- Content-type headers

---

## 🛡️ Security Features

### Rate Limiting
- **Login attempts**: Max 5 per 5 minutes per IP
- **Implementation**: In-memory store (production should use Redis)
- **Cleanup**: Automatic cleanup of old attempts

### Session Management
- **Session timeout**: 2 hours
- **Secure cookies**: HttpOnly, SameSite=Lax
- **Session data**: user_id, username, role

### File Upload Security
- **File type validation**: Extension and MIME type checking
- **Content validation**: Image processing untuk verify content
- **Size limits**: 5MB maximum
- **Filename sanitization**: UUID-based filenames
- **Path traversal protection**: Absolute path validation

### Input Validation
- **SQL Injection**: Parameterized queries
- **XSS Protection**: Template auto-escaping
- **CSRF Protection**: Flask built-in protection
- **Input sanitization**: Length limits, pattern matching

---

## 📋 Error Handling

### HTTP Status Codes
| Code | Description | When |
|------|-------------|------|
| 200 | Success | Normal page load |
| 302 | Redirect | After successful form submission |
| 403 | Forbidden | Role access violation |
| 404 | Not Found | Invalid motor ID atau file |
| 413 | Request Too Large | File upload exceeds 5MB |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Database atau server error |

### Error Messages
- **Flash messages**: User-friendly error descriptions
- **Form validation**: Field-specific error messages
- **File upload errors**: Detailed file validation feedback
- **Database errors**: Graceful error handling dengan fallback

---

## 🔄 Data Flow

### Authentication Flow
```
1. User submits login form
2. Rate limiting check
3. Credential validation
4. Session creation
5. Redirect to dashboard
```

### Motor Management Flow
```
1. Admin accesses motor section
2. Role validation (admin only)
3. Data isolation (own motors only)
4. CRUD operations with validation
5. File processing (if image upload)
6. Database update
7. Success/error feedback
```

### File Upload Flow
```
1. File selection and upload
2. Size and type validation
3. Content verification (image processing)
4. Secure filename generation
5. File save to secure location
6. Database record update
7. Old file cleanup (if replacing)
```

---

## 🗃️ Database Schema Reference

### Users Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,  -- Hashed dengan Werkzeug
    role ENUM('superadmin', 'admin') NOT NULL
);
```

### Motor Table
```sql
CREATE TABLE motor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_motor VARCHAR(100) NOT NULL,
    plat_nomor VARCHAR(20) NOT NULL UNIQUE,
    status ENUM('tersedia', 'disewa', 'maintenance') DEFAULT 'tersedia',
    deskripsi TEXT,
    gambar VARCHAR(255),  -- Filename saja, bukan full path
    admin_id INT NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 🚀 Usage Examples

### Login sebagai Superadmin
```bash
curl -X POST http://localhost:5000/login \
  -d "username=superadmin&password=admin123" \
  -c cookies.txt
```

### Tambah Motor (sebagai Admin)
```bash
curl -X POST http://localhost:5000/add_motor \
  -b cookies.txt \
  -F "nama_motor=Honda Scoopy 2024" \
  -F "plat_nomor=DK 9999 XX" \
  -F "status=tersedia" \
  -F "deskripsi=Motor matic baru dengan fitur modern" \
  -F "gambar=@motor.jpg"
```

### Get Dashboard Data
```bash
curl -X GET http://localhost:5000/dashboard \
  -b cookies.txt
```

---

## 📝 Development Notes

### Adding New Endpoints
1. Add route dengan proper authentication decorator
2. Implement input validation
3. Add error handling
4. Update documentation
5. Test dengan different roles

### Security Checklist
- [ ] Authentication required
- [ ] Role-based access control
- [ ] Input validation dan sanitization
- [ ] Rate limiting (if applicable)
- [ ] Error handling
- [ ] Logging sensitive operations

### Performance Considerations
- Database query optimization
- Image processing efficiency
- Session storage optimization
- File I/O optimization

---

**Last Updated**: January 27, 2025  
**API Version**: 2.0.0  
**Author**: Dewata Motor Development Team 