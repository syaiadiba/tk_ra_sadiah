// Validasi Real-time dengan Regex
document.addEventListener('DOMContentLoaded', function() {
    const validations = {
        username: {
            pattern: /^[a-zA-Z0-9_]{3,20}$/,
            message: 'Username 3-20 karakter (huruf, angka, underscore)'
        },
        full_name: {
            pattern: /^[a-zA-Z\s\.\']{2,50}$/,
            message: 'Nama 2-50 karakter (huruf, spasi, titik)'
        },
        nis: {
            pattern: /^\d{8,12}$/,
            message: 'NIS 8-12 digit angka'
        },
        nisn: {
            pattern: /^\d{10}$/,
            message: 'NISN 10 digit angka'
        },
        phone: {
            pattern: /^(08|\+62)[0-9]{8,12}$/,
            message: 'Format: 081234567890 atau +6281234567890'
        },
        email: {
            pattern: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
            message: 'Email tidak valid (contoh: nama@domain.com)'
        },
        password: {
            pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{4,}$/,
            message: 'Minimal 4 karakter, kombinasi huruf dan angka'
        },
        nip: {
            pattern: /^\d{6,18}$/,
            message: 'NIP 6-18 digit angka'
        },
        nilai: {
            pattern: /^\d{1,3}$|^100$/,
            message: 'Nilai 0-100'
        },
        mapel: {
            pattern: /^[a-zA-Z\s\-]{2,30}$/,
            message: 'Mata pelajaran 2-30 karakter (huruf, spasi)'
        },
        judul: {
            pattern: /^[a-zA-Z0-9\s\-_.,!?]{3,100}$/,
            message: 'Judul 3-100 karakter'
        }
    };
    
    // Implementasi validasi real-time
    // ...
});