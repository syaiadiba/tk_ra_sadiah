"""
Tanggapan Model for TK RA SA'DIAH
"""

from .base_model import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Tanggapan(BaseModel):
    
    def get_table_name(self):
        return 'tanggapan'
    
    # ============================================
    # CREATE TABLE METHOD - PERBAIKI INI!
    # ============================================
    @classmethod
    def create_table(cls):
        """Create tanggapan table in PostgreSQL"""
        query = """
        CREATE TABLE IF NOT EXISTS tanggapan (
            id SERIAL PRIMARY KEY,
            pembelajaran_id INTEGER REFERENCES pembelajaran(id) ON DELETE CASCADE,
            murid_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            tanggapan TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            temp = Tanggapan()
            temp.execute_query(query)
            print("✅ Tabel 'tanggapan' berhasil dibuat / sudah ada")
            return True
        except Exception as e:
            print(f"❌ Gagal membuat tabel tanggapan: {str(e)}")
            return False
    
    # ============================================
    # METHOD LAINNYA
    # ============================================
    def get_by_pembelajaran(self, pembelajaran_id):
        try:
            query = """
                SELECT t.*, u.username as murid_name, u.full_name as murid_full_name
                FROM tanggapan t
                JOIN users u ON t.murid_id = u.id
                WHERE t.pembelajaran_id = %s
                ORDER BY t.created_at DESC
            """
            return self.execute_query(query, (pembelajaran_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_pembelajaran: {str(e)}")
            raise
    
    def get_by_murid(self, murid_id):
        try:
            query = """
                SELECT t.*, p.judul as pembelajaran_judul
                FROM tanggapan t
                JOIN pembelajaran p ON t.pembelajaran_id = p.id
                WHERE t.murid_id = %s
                ORDER BY t.created_at DESC
            """
            return self.execute_query(query, (murid_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_murid: {str(e)}")
            raise
    
    def has_responded(self, murid_id, pembelajaran_id):
        try:
            query = "SELECT COUNT(*) as total FROM tanggapan WHERE murid_id = %s AND pembelajaran_id = %s"
            result = self.execute_query(query, (murid_id, pembelajaran_id), fetch_one=True)
            return result['total'] > 0 if result else False
        except Exception as e:
            logger.error(f"Error in has_responded: {str(e)}")
            return False
    
    def insert(self, data):
        try:
            if 'pembelajaran_id' not in data or not data['pembelajaran_id']:
                raise ValueError("Pembelajaran ID harus diisi")
            if 'murid_id' not in data or not data['murid_id']:
                raise ValueError("Murid ID harus diisi")
            if 'tanggapan' not in data or not data['tanggapan']:
                raise ValueError("Tanggapan harus diisi")
            
            if len(data['tanggapan']) < 5:
                raise ValueError("Tanggapan minimal 5 karakter")
            
            if self.has_responded(data['murid_id'], data['pembelajaran_id']):
                raise ValueError("Siswa sudah memberikan tanggapan")
            
            data['created_at'] = datetime.now()
            return super().insert(data)
        except Exception as e:
            logger.error(f"Error in insert: {str(e)}")
            raise