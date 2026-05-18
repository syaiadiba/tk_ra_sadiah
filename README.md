# TK RA SA'DIAH Web Application

Sistem Informasi Sekolah untuk TK RA SA'DIAH

## Fitur Utama

### 1. Multi-role Login
- **Admin**: Mengelola data siswa, pembayaran SPP (CRUD)
- **Guru**: Membuat pembelajaran, melihat tanggapan siswa
- **Murid**: Melihat pembelajaran, memberi tanggapan, melihat keuangan

### 2. Fitur Khusus
- Sequential search untuk pencarian data siswa
- Blur background dengan gambar sekolah
- Notifikasi pembelajaran real-time
- Manajemen pembayaran SPP per bulan

### 3. Teknologi
- Flask 2.3.2
- PostgreSQL
- Bootstrap 5
- Flask-Login untuk autentikasi

## Cara Install & Jalankan

### 1. Install PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows: Download dari https://www.postgresql.org/download/windows/