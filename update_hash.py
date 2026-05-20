import bcrypt
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def update_all_passwords():
    print("=" * 60)
    print("🔐 UPDATE PASSWORD SEMUA USER")
    print("=" * 60)
    
    # Generate hash untuk 'admin123'
    hashed = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    print(f"\n📝 Hash baru: {hashed}\n")
    
    # Koneksi database
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'tk_ra_sadiah'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432')
    )
    cur = conn.cursor()
    
    # Update semua user
    cur.execute("UPDATE users SET password_hash = %s", (hashed,))
    updated = cur.rowcount
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"✅ Berhasil mengupdate {updated} user!")
    print("🔑 Semua user sekarang bisa login dengan password: admin123")
    print("=" * 60)

if __name__ == '__main__':
    confirm = input("Update password semua user ke 'admin123'? (y/n): ")
    if confirm.lower() == 'y':
        update_all_passwords()
    else:
        print("Dibatalkan.")