-- Script untuk menambahkan kolom gambar ke tabel motor
-- Jalankan script ini di MySQL/phpMyAdmin

USE motordewata;

-- Cek apakah kolom gambar sudah ada, jika belum tambahkan
ALTER TABLE motor ADD COLUMN IF NOT EXISTS gambar VARCHAR(255) AFTER deskripsi;

-- Jika kolom deskripsi belum ada, tambahkan juga
ALTER TABLE motor ADD COLUMN IF NOT EXISTS deskripsi TEXT AFTER status;

-- Cek struktur tabel setelah update
DESCRIBE motor;

SELECT 'Database berhasil diupdate! Kolom gambar dan deskripsi telah ditambahkan.' as status; 