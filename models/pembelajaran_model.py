"""
Pembelajaran Model for TK RA SA'DIAH
"""

from .base_model import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Pembelajaran(BaseModel):
    
    def get_table_name(self):
        return 'pembelajaran'
    
    # ============================================
    # CREATE TABLE METHOD - PERBAIKI INI!
    # ============================================
    @classmethod
    def create_table(cls):
        """Create pembelajaran table in PostgreSQL"""
        query = """
        CREATE TABLE IF NOT EXISTS pembelajaran (
            id SERIAL PRIMARY KEY,
            guru_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            judul VARCHAR(200) NOT NULL,
            konten TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            temp = Pembelajaran()
            temp.execute_query(query)
            print("✅ Tabel 'pembelajaran' berhasil dibuat / sudah ada")
            return True
        except Exception as e:
            print(f"❌ Gagal membuat tabel pembelajaran: {str(e)}")
            return False
    
    # ============================================
    # METHOD LAINNYA
    # ============================================
    def get_by_guru(self, guru_id):
        try:
            query = """
                SELECT p.*, u.username as guru_name, u.full_name as guru_full_name
                FROM pembelajaran p
                JOIN users u ON p.guru_id = u.id
                WHERE p.guru_id = %s
                ORDER BY p.created_at DESC
            """
            return self.execute_query(query, (guru_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_guru: {str(e)}")
            raise
    
    def get_all_with_guru(self):
        try:
            query = """
                SELECT p.*, u.username as guru_name, u.full_name as guru_full_name
                FROM pembelajaran p
                JOIN users u ON p.guru_id = u.id
                ORDER BY p.created_at DESC
            """
            return self.execute_query(query, fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_all_with_guru: {str(e)}")
            raise
    
    def get_by_id(self, record_id):
        try:
            query = "SELECT * FROM pembelajaran WHERE id = %s"
            return self.execute_query(query, (record_id,), fetch_one=True)
        except Exception as e:
            logger.error(f"Error in get_by_id: {str(e)}")
            raise
    
    def insert(self, data):
        try:
            if 'judul' not in data or not data['judul']:
                raise ValueError("Judul pembelajaran harus diisi")
            if 'konten' not in data or not data['konten']:
                raise ValueError("Konten pembelajaran harus diisi")
            if 'guru_id' not in data or not data['guru_id']:
                raise ValueError("Guru ID harus diisi")
            
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()
            return super().insert(data)
        except Exception as e:
            logger.error(f"Error in insert: {str(e)}")
            raise