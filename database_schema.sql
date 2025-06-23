-- Database: motordewata
CREATE DATABASE IF NOT EXISTS motordewata;
USE motordewata;

-- Table: users
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('superadmin', 'admin') NOT NULL
);

-- Table: motor
CREATE TABLE motor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_motor VARCHAR(100) NOT NULL,
    plat_nomor VARCHAR(20) NOT NULL UNIQUE,
    status ENUM('tersedia', 'disewa', 'maintenance') DEFAULT 'tersedia',
    deskripsi TEXT,
    gambar VARCHAR(255),
    admin_id INT NOT NULL,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ========================================
-- SAMPLE DATA INSERTION
-- ========================================

-- Insert users (password untuk semua: admin123)
INSERT INTO users (username, password, role) VALUES 
-- Superadmin account
('superadmin', 'scrypt:32768:8:1$ptnaqkm6BzZ5xuSb$0904d5c66a736df6f3f6ddfddc7df29e2315fbe304cd3904c7d966223a0b21193cc91eff7115e0d21e2c3e8debce256f2b7696ea888ac2fea4acfac0bb9cd465', 'superadmin'),

-- Admin accounts untuk berbagai cabang/area
('admin_denpasar', 'scrypt:32768:8:1$ptnaqkm6BzZ5xuSb$0904d5c66a736df6f3f6ddfddc7df29e2315fbe304cd3904c7d966223a0b21193cc91eff7115e0d21e2c3e8debce256f2b7696ea888ac2fea4acfac0bb9cd465', 'admin'),
('admin_ubud', 'scrypt:32768:8:1$ptnaqkm6BzZ5xuSb$0904d5c66a736df6f3f6ddfddc7df29e2315fbe304cd3904c7d966223a0b21193cc91eff7115e0d21e2c3e8debce256f2b7696ea888ac2fea4acfac0bb9cd465', 'admin'),
('admin_sanur', 'scrypt:32768:8:1$ptnaqkm6BzZ5xuSb$0904d5c66a736df6f3f6ddfddc7df29e2315fbe304cd3904c7d966223a0b21193cc91eff7115e0d21e2c3e8debce256f2b7696ea888ac2fea4acfac0bb9cd465', 'admin'),
('admin_kuta', 'scrypt:32768:8:1$ptnaqkm6BzZ5xuSb$0904d5c66a736df6f3f6ddfddc7df29e2315fbe304cd3904c7d966223a0b21193cc91eff7115e0d21e2c3e8debce256f2b7696ea888ac2fea4acfac0bb9cd465', 'admin'),
('admin_seminyak', 'scrypt:32768:8:1$ptnaqkm6BzZ5xuSb$0904d5c66a736df6f3f6ddfddc7df29e2315fbe304cd3904c7d966223a0b21193cc91eff7115e0d21e2c3e8debce256f2b7696ea888ac2fea4acfac0bb9cd465', 'admin');

-- ========================================
-- SAMPLE MOTOR DATA FOR EACH ADMIN
-- ========================================

-- Motor untuk Admin Denpasar (ID: 2)
INSERT INTO motor (nama_motor, plat_nomor, status, deskripsi, gambar, admin_id) VALUES 
('Honda Scoopy 2023', 'DK 1234 AB', 'tersedia', 'Motor matic stylish warna putih, cocok untuk perjalanan dalam kota', NULL, 2),
('Yamaha NMAX 155', 'DK 1235 AB', 'disewa', 'Motor premium dengan fitur keyless dan Smart Key System', NULL, 2),
('Honda Vario 150', 'DK 1236 AB', 'tersedia', 'Matic sporty dengan mesin bertenaga dan konsumsi BBM irit', NULL, 2),
('Yamaha Aerox 155', 'DK 1237 AB', 'maintenance', 'Motor sport bergaya agresif dengan performa tinggi', NULL, 2),
('Honda Beat Street', 'DK 1238 AB', 'tersedia', 'Motor praktis untuk sehari-hari dengan desain modern', NULL, 2);

-- Motor untuk Admin Ubud (ID: 3)
INSERT INTO motor (nama_motor, plat_nomor, status, deskripsi, admin_id) VALUES 
('Honda PCX 160', 'DK 2001 UB', 'tersedia', 'Motor premium dengan CVT otomatis dan suspensi nyaman', 3),
('Yamaha Lexi 125', 'DK 2002 UB', 'tersedia', 'Design sporty dengan teknologi Blue Core yang irit BBM', 3),
('Honda Genio 110', 'DK 2003 UB', 'disewa', 'Motor retro dengan gaya klasik dan performa modern', 3),
('Yamaha Gear 125', 'DK 2004 UB', 'tersedia', 'Motor adventure kompak untuk jalanan berkelok Ubud', 3),
('Honda Scoopy FI', 'DK 2005 UB', 'maintenance', 'Motor elegant dengan teknologi fuel injection', 3),
('Yamaha Fino 125', 'DK 2006 UB', 'tersedia', 'Motor retro stylish dengan desain vintage yang menawan', 3);

-- Motor untuk Admin Sanur (ID: 4)
INSERT INTO motor (nama_motor, plat_nomor, status, deskripsi, admin_id) VALUES 
('Yamaha NMAX ABS', 'DK 3001 SR', 'tersedia', 'Motor premium dengan sistem ABS untuk keamanan maksimal', 4),
('Honda Forza 250', 'DK 3002 SR', 'disewa', 'Maxi scooter mewah dengan mesin 250cc berperforma tinggi', 4),
('Yamaha XMAX 250', 'DK 3003 SR', 'tersedia', 'Adventure scooter dengan desain sporty dan kenyamanan touring', 4),
('Honda ADV 150', 'DK 3004 SR', 'tersedia', 'Motor adventure dengan ground clearance tinggi untuk segala medan', 4),
('Yamaha Aerox Connected', 'DK 3005 SR', 'maintenance', 'Motor sport dengan teknologi Y-Connect untuk konektivitas digital', 4);

-- Motor untuk Admin Kuta (ID: 5)
INSERT INTO motor (nama_motor, plat_nomor, status, deskripsi, admin_id) VALUES 
('Honda Vario 125', 'DK 4001 KT', 'tersedia', 'Motor matic paling populer dengan teknologi PGM-FI', 5),
('Yamaha Soul GT', 'DK 4002 KT', 'tersedia', 'Motor sport berdesain agresif dengan performa maksimal', 5),
('Honda Beat Pop', 'DK 4003 KT', 'disewa', 'Motor ekonomis dengan desain colorful dan cheerful', 5),
('Yamaha Mio M3', 'DK 4004 KT', 'tersedia', 'Motor praktis untuk aktivitas sehari-hari dengan efisiensi tinggi', 5),
('Honda Scoopy Stylish', 'DK 4005 KT', 'tersedia', 'Motor fashion dengan ban lebar dan tampilan stylish', 5),
('Yamaha Freego', 'DK 4006 KT', 'maintenance', 'Motor urban dengan desain modern dan fitur praktis', 5),
('Honda Genio CBS', 'DK 4007 KT', 'tersedia', 'Motor retro dengan sistem CBS untuk pengereman aman', 5);

-- Motor untuk Admin Seminyak (ID: 6)
INSERT INTO motor (nama_motor, plat_nomor, status, deskripsi, admin_id) VALUES 
('Honda PCX Hybrid', 'DK 5001 SM', 'tersedia', 'Motor hybrid ramah lingkungan dengan teknologi terdepan', 6),
('Yamaha NMAX Turbo', 'DK 5002 SM', 'disewa', 'Motor premium dengan teknologi turbo untuk performa ekstra', 6),
('Honda Vario Techno', 'DK 5003 SM', 'tersedia', 'Motor teknologi tinggi dengan fitur canggih dan modern', 6),
('Yamaha Aerox S-Version', 'DK 5004 SM', 'tersedia', 'Motor sport special edition dengan performa tinggi', 6),
('Honda ADV 160', 'DK 5005 SM', 'maintenance', 'Motor adventure terbaru dengan ground clearance optimal', 6),
('Yamaha Lexi S', 'DK 5006 SM', 'tersedia', 'Motor sporty dengan desain futuristik dan teknologi modern', 6),
('Honda Beat Deluxe', 'DK 5007 SM', 'tersedia', 'Motor ekonomis versi deluxe dengan fitur lengkap', 6),
('Yamaha Fino Premium', 'DK 5008 SM', 'disewa', 'Motor retro premium dengan kualitas dan kenyamanan terbaik', 6); 