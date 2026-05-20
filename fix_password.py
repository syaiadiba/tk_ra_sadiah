import bcrypt
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_passwords():
    print("🔐 Memperbaiki password...")
    
    # Koneksi ke database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'tk_ra_sadiah'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432')
    )
    cur = conn.cursor()
    
    # Hash untuk password 'admin123'
    hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"Hash baru: {hashed}")
    
    # Update semua user
    users = ['admin', 'guru', 'murid1', 'murid2']
    
    for username in users:
        cur.execute("UPDATE users SET password_hash = %s WHERE username = %s", (hashed, username))
        if cur.rowcount > 0:
            print(f"✅ Password '{username}' berhasil diupdate")
        else:
            print(f"⚠️ User '{username}' tidak ditemukan")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print("\n✅ Selesai! Sekarang semua user bisa login dengan password: admin123")

if __name__ == '__main__':
    fix_passwords()