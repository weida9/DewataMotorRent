-- Script untuk menambahkan kolom deskripsi ke tabel motor yang sudah ada
-- Jalankan script ini jika database sudah dibuat sebelumnya

USE motordewata;

-- Tambahkan kolom deskripsi dan gambar
ALTER TABLE motor ADD COLUMN deskripsi TEXT AFTER status;
ALTER TABLE motor ADD COLUMN gambar VARCHAR(255) AFTER deskripsi;

-- Update data existing dengan deskripsi sample
UPDATE motor SET deskripsi = CASE 
    WHEN nama_motor = 'Honda Scoopy 2023' THEN 'Motor matic stylish warna putih, cocok untuk perjalanan dalam kota'
    WHEN nama_motor = 'Yamaha NMAX 155' THEN 'Motor premium dengan fitur keyless dan Smart Key System'
    WHEN nama_motor = 'Honda Vario 150' THEN 'Matic sporty dengan mesin bertenaga dan konsumsi BBM irit'
    WHEN nama_motor = 'Yamaha Aerox 155' THEN 'Motor sport bergaya agresif dengan performa tinggi'
    WHEN nama_motor = 'Honda Beat Street' THEN 'Motor praktis untuk sehari-hari dengan desain modern'
    WHEN nama_motor = 'Honda PCX 160' THEN 'Motor premium dengan CVT otomatis dan suspensi nyaman'
    WHEN nama_motor = 'Yamaha Lexi 125' THEN 'Design sporty dengan teknologi Blue Core yang irit BBM'
    WHEN nama_motor = 'Honda Genio 110' THEN 'Motor retro dengan gaya klasik dan performa modern'
    WHEN nama_motor = 'Yamaha Gear 125' THEN 'Motor adventure kompak untuk jalanan berkelok Ubud'
    WHEN nama_motor = 'Honda Scoopy FI' THEN 'Motor elegant dengan teknologi fuel injection'
    WHEN nama_motor = 'Yamaha Fino 125' THEN 'Motor retro stylish dengan desain vintage yang menawan'
    WHEN nama_motor = 'Yamaha NMAX ABS' THEN 'Motor premium dengan sistem ABS untuk keamanan maksimal'
    WHEN nama_motor = 'Honda Forza 250' THEN 'Maxi scooter mewah dengan mesin 250cc berperforma tinggi'
    WHEN nama_motor = 'Yamaha XMAX 250' THEN 'Adventure scooter dengan desain sporty dan kenyamanan touring'
    WHEN nama_motor = 'Honda ADV 150' THEN 'Motor adventure dengan ground clearance tinggi untuk segala medan'
    WHEN nama_motor = 'Yamaha Aerox Connected' THEN 'Motor sport dengan teknologi Y-Connect untuk konektivitas digital'
    WHEN nama_motor = 'Honda Vario 125' THEN 'Motor matic paling populer dengan teknologi PGM-FI'
    WHEN nama_motor = 'Yamaha Soul GT' THEN 'Motor sport berdesain agresif dengan performa maksimal'
    WHEN nama_motor = 'Honda Beat Pop' THEN 'Motor ekonomis dengan desain colorful dan cheerful'
    WHEN nama_motor = 'Yamaha Mio M3' THEN 'Motor praktis untuk aktivitas sehari-hari dengan efisiensi tinggi'
    WHEN nama_motor = 'Honda Scoopy Stylish' THEN 'Motor fashion dengan ban lebar dan tampilan stylish'
    WHEN nama_motor = 'Yamaha Freego' THEN 'Motor urban dengan desain modern dan fitur praktis'
    WHEN nama_motor = 'Honda Genio CBS' THEN 'Motor retro dengan sistem CBS untuk pengereman aman'
    WHEN nama_motor = 'Honda PCX Hybrid' THEN 'Motor hybrid ramah lingkungan dengan teknologi terdepan'
    WHEN nama_motor = 'Yamaha NMAX Turbo' THEN 'Motor premium dengan teknologi turbo untuk performa ekstra'
    WHEN nama_motor = 'Honda Vario Techno' THEN 'Motor teknologi tinggi dengan fitur canggih dan modern'
    WHEN nama_motor = 'Yamaha Aerox S-Version' THEN 'Motor sport special edition dengan performa tinggi'
    WHEN nama_motor = 'Honda ADV 160' THEN 'Motor adventure terbaru dengan ground clearance optimal'
    WHEN nama_motor = 'Yamaha Lexi S' THEN 'Motor sporty dengan desain futuristik dan teknologi modern'
    WHEN nama_motor = 'Honda Beat Deluxe' THEN 'Motor ekonomis versi deluxe dengan fitur lengkap'
    WHEN nama_motor = 'Yamaha Fino Premium' THEN 'Motor retro premium dengan kualitas dan kenyamanan terbaik'
    ELSE 'Motor berkualitas untuk rental harian dan jangka panjang'
END;

SELECT 'Kolom deskripsi dan gambar berhasil ditambahkan dan data telah diupdate!' as status; 