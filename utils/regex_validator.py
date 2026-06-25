"""
Regex Validator untuk TK RA SA'DIAH
Fungsi-fungsi validasi menggunakan Regular Expression
"""

import re
from datetime import datetime


class RegexValidator:
    """Kelas untuk validasi data menggunakan Regex"""
    
    # Pattern Regex
    PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'username': r'^[a-zA-Z0-9_]{3,20}$',
        'password': r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{4,}$',
        'nis': r'^\d{8,12}$',
        'nisn': r'^\d{10}$',
        'phone': r'^(08|\+62)[0-9]{8,12}$',
        'nip': r'^\d{6,18}$',
        'nama': r'^[a-zA-Z\s\.\']{2,50}$',
        'nilai': r'^\d{1,3}$|^100$',
        'tahun': r'^\d{4}$',
        'mapel': r'^[a-zA-Z\s\-]{2,30}$',
        'judul': r'^[a-zA-Z0-9\s\-_.,!?]{3,100}$',
        'deskripsi': r'^[a-zA-Z0-9\s\-_.,!?\n]{5,500}$',
        'alamat': r'^[a-zA-Z0-9\s\.,\#\-]{5,100}$',
        'kelas': r'^[A-Za-z0-9\s\-]{1,20}$',
        'address': r'^[a-zA-Z0-9\s\.,\#\-]{5,100}$',
        'full_name': r'^[a-zA-Z\s\.\']{2,50}$',
    }
    
    @classmethod
    def validate(cls, value, pattern_name, required=True):
        """
        Validasi value dengan pattern tertentu
        
        Args:
            value: Nilai yang akan divalidasi
            pattern_name: Nama pattern dari PATTERNS
            required: Apakah field wajib diisi
        
        Returns:
            tuple: (is_valid, message)
        """
        # Jika nilai kosong
        if not value or str(value).strip() == '':
            if required:
                return False, f"{pattern_name} tidak boleh kosong"
            return True, "Field opsional (kosong)"
        
        # Ambil pattern
        pattern = cls.PATTERNS.get(pattern_name)
        if not pattern:
            return False, f"Pattern '{pattern_name}' tidak ditemukan"
        
        # Validasi dengan regex
        if re.match(pattern, str(value)):
            return True, "Valid"
        return False, f"Format {pattern_name} tidak valid"
    
    @classmethod
    def validate_email(cls, email, required=False):
        """Validasi email"""
        return cls.validate(email, 'email', required)
    
    @classmethod
    def validate_username(cls, username, required=True):
        """Validasi username (huruf, angka, underscore, 3-20 karakter)"""
        return cls.validate(username, 'username', required)
    
    @classmethod
    def validate_password(cls, password, required=True):
        """Validasi password (minimal 4 karakter, kombinasi huruf dan angka)"""
        if not password or str(password).strip() == '':
            if required:
                return False, "Password harus diisi"
            return True, "Password kosong (opsional)"
        
        # Password minimal 4 karakter
        if len(password) < 4:
            return False, "Password minimal 4 karakter"
        
        # Cek kombinasi huruf dan angka
        if re.match(cls.PATTERNS['password'], password):
            return True, "Password valid"
        return False, "Password harus mengandung huruf dan angka"
    
    @classmethod
    def validate_nis(cls, nis, required=True):
        """Validasi NIS (8-12 digit angka)"""
        return cls.validate(nis, 'nis', required)
    
    @classmethod
    def validate_nisn(cls, nisn, required=False):
        """Validasi NISN (10 digit angka)"""
        return cls.validate(nisn, 'nisn', required)
    
    @classmethod
    def validate_phone(cls, phone, required=False):
        """Validasi nomor telepon (Indonesia)"""
        return cls.validate(phone, 'phone', required)
    
    @classmethod
    def validate_nip(cls, nip, required=True):
        """Validasi NIP (6-18 digit angka)"""
        return cls.validate(nip, 'nip', required)
    
    @classmethod
    def validate_nama(cls, nama, required=True):
        """Validasi nama lengkap"""
        return cls.validate(nama, 'nama', required)
    
    @classmethod
    def validate_full_name(cls, nama, required=True):
        """Validasi nama lengkap"""
        return cls.validate(nama, 'full_name', required)
    
    @classmethod
    def validate_nilai(cls, nilai, required=True):
        """Validasi nilai (0-100)"""
        return cls.validate(nilai, 'nilai', required)
    
    @classmethod
    def validate_tahun(cls, tahun, required=True):
        """Validasi tahun (4 digit)"""
        return cls.validate(tahun, 'tahun', required)
    
    @classmethod
    def validate_mapel(cls, mapel, required=False):
        """Validasi mata pelajaran"""
        return cls.validate(mapel, 'mapel', required)
    
    @classmethod
    def validate_judul(cls, judul, required=True):
        """Validasi judul"""
        return cls.validate(judul, 'judul', required)
    
    @classmethod
    def validate_deskripsi(cls, deskripsi, required=False):
        """Validasi deskripsi"""
        return cls.validate(deskripsi, 'deskripsi', required)
    
    @classmethod
    def validate_kelas(cls, kelas, required=False):
        """Validasi kelas"""
        return cls.validate(kelas, 'kelas', required)
    
    @classmethod
    def validate_alamat(cls, alamat, required=False):
        """Validasi alamat"""
        return cls.validate(alamat, 'alamat', required)
    
    @classmethod
    def sanitize_input(cls, value):
        """Bersihkan input dari karakter berbahaya"""
        if not value:
            return value
        # Hapus tag HTML
        clean = re.sub(r'<[^>]+>', '', str(value))
        # Hapus karakter berbahaya
        clean = re.sub(r'[<>"\']', '', clean)
        return clean.strip()
    
    @classmethod
    def contains_sql_injection(cls, text):
        """Deteksi potensi SQL Injection"""
        if not text:
            return False
        sql_patterns = [
            r'(?i)(select|insert|update|delete|drop|union|exec|script)',
            r'(-\s*\-)|(;\s*\-\-)|(\|\|)',
            r'(/\*.*\*/)',
        ]
        for pattern in sql_patterns:
            if re.search(pattern, str(text)):
                return True
        return False


# Singleton untuk kemudahan penggunaan
validator = RegexValidator()