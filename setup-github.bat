@echo off
echo.
echo ===============================================
echo   🚀 Dewata Motor - GitHub Setup Script  
echo ===============================================
echo.

echo 📋 Panduan Setup GitHub Repository:
echo.
echo 1. Buat repository baru di GitHub dengan nama: DewataMotorRent
echo 2. JANGAN tambahkan README, .gitignore, atau license
echo 3. Copy URL repository yang baru dibuat
echo.

set /p username="Masukkan GitHub username Anda: "
if "%username%"=="" (
    echo ❌ Username tidak boleh kosong!
    pause
    exit /b 1
)

echo.
echo 🔧 Mengupdate remote repository...

REM Remove existing remote
git remote remove origin 2>nul

REM Add new remote
git remote add origin https://github.com/%username%/DewataMotorRent.git

echo ✅ Remote repository berhasil diset ke: https://github.com/%username%/DewataMotorRent.git
echo.

echo 🔍 Cek status git...
git status

echo.
echo 🚀 Siap untuk push ke GitHub!
echo.
echo Jalankan command berikut untuk push:
echo   git push -u origin main
echo.
echo 💡 Tips:
echo - Jika diminta password, gunakan Personal Access Token
echo - Buat token di: GitHub Settings → Developer settings → Personal access tokens
echo - Berikan scope 'repo' pada token
echo.

pause 