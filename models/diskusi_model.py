"""
Diskusi Model for TK RA SA'DIAH
"""

from .base_model import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Diskusi(BaseModel):
    
    def get_table_name(self):
        return 'diskusi'
    
    @classmethod
    def create_table(cls):
        query = """
        CREATE TABLE IF NOT EXISTS diskusi (
            id SERIAL PRIMARY KEY,
            penugasan_id INTEGER REFERENCES penugasan(id) ON DELETE CASCADE,
            siswa_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            komentar TEXT NOT NULL,
            lampiran VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            temp = Diskusi()
            temp.execute_query(query)
            print("✅ Tabel 'diskusi' siap")
            return True
        except Exception as e:
            print(f"❌ Gagal membuat tabel diskusi: {e}")
            return False
    
    def get_by_penugasan(self, penugasan_id):
        try:
            query = """
                SELECT d.*, u.full_name as siswa_name
                FROM diskusi d
                JOIN users u ON d.siswa_id = u.id
                WHERE d.penugasan_id = %s
                ORDER BY d.created_at ASC
            """
            return self.execute_query(query, (penugasan_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_penugasan: {str(e)}")
            return []
    
    def get_by_siswa(self, siswa_id):
        try:
            query = """
                SELECT d.*, p.judul as penugasan_judul
                FROM diskusi d
                JOIN penugasan p ON d.penugasan_id = p.id
                WHERE d.siswa_id = %s
                ORDER BY d.created_at DESC
            """
            return self.execute_query(query, (siswa_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_siswa: {str(e)}")
            return []