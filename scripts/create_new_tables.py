"""
Script untuk membuat tabel-tabel baru di database
Jalankan: python create_new_tables.py
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'tk_ra_sadiah'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432')
    )

def create_tables():
    print("=" * 60)
    print("📦 Membuat Tabel Baru di Database")
    print("=" * 60)
    
    conn = get_connection()
    cur = conn.cursor()
    
    # 1. Tabel e_rapor
    cur.execute("""
        CREATE TABLE IF NOT EXISTS e_rapor (
            id SERIAL PRIMARY KEY,
            siswa_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            mapel VARCHAR(100) NOT NULL,
            nilai DECIMAL(5,2),
            predikat VARCHAR(10),
            catatan TEXT,
            semester VARCHAR(10),
            tahun_ajaran VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Tabel 'e_rapor' siap")
    
    # 2. Tabel pengumuman
    cur.execute("""
        CREATE TABLE IF NOT EXISTS pengumuman (
            id SERIAL PRIMARY KEY,
            admin_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            judul VARCHAR(200) NOT NULL,
            isi TEXT NOT NULL,
            target_role VARCHAR(20) DEFAULT 'semua',
            is_pinned BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Tabel 'pengumuman' siap")
    
    # 3. Tabel penugasan
    cur.execute("""
        CREATE TABLE IF NOT EXISTS penugasan (
            id SERIAL PRIMARY KEY,
            guru_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            judul VARCHAR(200) NOT NULL,
            deskripsi TEXT NOT NULL,
            deadline DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Tabel 'penugasan' siap")
    
    # 4. Tabel diskusi
    cur.execute("""
        CREATE TABLE IF NOT EXISTS diskusi (
            id SERIAL PRIMARY KEY,
            penugasan_id INTEGER REFERENCES penugasan(id) ON DELETE CASCADE,
            siswa_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            komentar TEXT NOT NULL,
            lampiran VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Tabel 'diskusi' siap")
    
    # 5. Tambah kolom ke users
    columns = [
        "ADD COLUMN IF NOT EXISTS nis VARCHAR(20) UNIQUE",
        "ADD COLUMN IF NOT EXISTS nisn VARCHAR(20) UNIQUE", 
        "ADD COLUMN IF NOT EXISTS kelas VARCHAR(20)",
        "ADD COLUMN IF NOT EXISTS nip VARCHAR(20) UNIQUE",
        "ADD COLUMN IF NOT EXISTS mata_pelajaran VARCHAR(100)",
        "ADD COLUMN IF NOT EXISTS jenis_kelamin VARCHAR(10)",
        "ADD COLUMN IF NOT EXISTS tanggal_lahir DATE",
        "ADD COLUMN IF NOT EXISTS phone VARCHAR(20)",
        "ADD COLUMN IF NOT EXISTS address TEXT"
    ]
    
    for col in columns:
        try:
            cur.execute(f"ALTER TABLE users {col}")
            print(f"✅ Kolom users berhasil ditambahkan")
        except:
            pass
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("=" * 60)
    print("✅ SEMUA TABEL BERHASIL DIBUAT!")
    print("=" * 60)

if __name__ == '__main__':
    create_tables()