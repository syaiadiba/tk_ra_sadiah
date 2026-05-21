"""
Pengumuman Model for TK RA SA'DIAH
"""

from .base_model import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Pengumuman(BaseModel):
    
    def get_table_name(self):
        return 'pengumuman'
    
    @classmethod
    def create_table(cls):
        query = """
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
        """
        try:
            temp = Pengumuman()
            temp.execute_query(query)
            print("✅ Tabel 'pengumuman' siap")
            return True
        except Exception as e:
            print(f"❌ Gagal membuat tabel pengumuman: {e}")
            return False
    
    def get_all_with_admin(self):
        try:
            query = """
                SELECT p.*, u.full_name as admin_name
                FROM pengumuman p
                JOIN users u ON p.admin_id = u.id
                ORDER BY p.is_pinned DESC, p.created_at DESC
            """
            return self.execute_query(query, fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_all_with_admin: {str(e)}")
            return []
    
    def get_by_role(self, role):
        try:
            query = """
                SELECT * FROM pengumuman 
                WHERE target_role = 'semua' OR target_role = %s
                ORDER BY is_pinned DESC, created_at DESC
            """
            return self.execute_query(query, (role,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_role: {str(e)}")
            return []