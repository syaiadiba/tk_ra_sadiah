"""
Test koneksi ke Supabase
Jalankan: python test_supabase.py
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    try:
        # Test dengan psycopg2
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM users")
        result = cur.fetchone()
        print(f"✅ Koneksi psycopg2 BERHASIL! Total users: {result[0]}")
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Gagal: {str(e)}")

if __name__ == '__main__':
    test_connection()