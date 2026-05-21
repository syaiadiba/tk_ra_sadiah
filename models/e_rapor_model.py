"""
E-Rapor Model for TK RA SA'DIAH
"""

from .base_model import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ERapor(BaseModel):
    
    def get_table_name(self):
        return 'e_rapor'
    
    @classmethod
    def create_table(cls):
        query = """
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
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(siswa_id, mapel, semester, tahun_ajaran)
        )
        """
        try:
            temp = ERapor()
            temp.execute_query(query)
            print("✅ Tabel 'e_rapor' siap")
            return True
        except Exception as e:
            print(f"❌ Gagal membuat tabel e_rapor: {e}")
            return False
    
    def get_by_siswa(self, siswa_id):
        try:
            query = "SELECT * FROM e_rapor WHERE siswa_id = %s ORDER BY mapel"
            return self.execute_query(query, (siswa_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_siswa: {str(e)}")
            return []
    
    def get_statistik_by_siswa(self, siswa_id):
        try:
            query = """
                SELECT 
                    COUNT(*) as total_mapel,
                    AVG(nilai) as rata_rata,
                    MIN(nilai) as nilai_min,
                    MAX(nilai) as nilai_max
                FROM e_rapor 
                WHERE siswa_id = %s
            """
            return self.execute_query(query, (siswa_id,), fetch_one=True) or {}
        except Exception as e:
            logger.error(f"Error in get_statistik_by_siswa: {str(e)}")
            return {}