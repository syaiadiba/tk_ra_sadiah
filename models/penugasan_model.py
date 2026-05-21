"""
Penugasan Model for TK RA SA'DIAH
"""

from .base_model import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Penugasan(BaseModel):
    
    def get_table_name(self):
        return 'penugasan'
    
    @classmethod
    def create_table(cls):
        query = """
        CREATE TABLE IF NOT EXISTS penugasan (
            id SERIAL PRIMARY KEY,
            guru_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            judul VARCHAR(200) NOT NULL,
            deskripsi TEXT NOT NULL,
            deadline DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            temp = Penugasan()
            temp.execute_query(query)
            print("✅ Tabel 'penugasan' siap")
            return True
        except Exception as e:
            print(f"❌ Gagal membuat tabel penugasan: {e}")
            return False
    
    def get_by_guru(self, guru_id):
        try:
            query = "SELECT * FROM penugasan WHERE guru_id = %s ORDER BY created_at DESC"
            return self.execute_query(query, (guru_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_guru: {str(e)}")
            return []
    
    def get_all_with_guru(self):
        try:
            query = """
                SELECT p.*, u.full_name as guru_name
                FROM penugasan p
                JOIN users u ON p.guru_id = u.id
                ORDER BY p.created_at DESC
            """
            return self.execute_query(query, fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_all_with_guru: {str(e)}")
            return []