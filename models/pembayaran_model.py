"""
Pembayaran Model for TK RA SA'DIAH
"""

from .base_model import BaseModel
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Pembayaran(BaseModel):
    
    def get_table_name(self):
        return 'pembayaran'
    
    # ============================================
    # CREATE TABLE METHOD - PERBAIKI INI!
    # ============================================
    @classmethod
    def create_table(cls):
        """Create pembayaran table in PostgreSQL"""
        query = """
        CREATE TABLE IF NOT EXISTS pembayaran (
            id SERIAL PRIMARY KEY,
            murid_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            bulan VARCHAR(20) NOT NULL,
            tahun INTEGER NOT NULL,
            nominal INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'belum_bayar',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(murid_id, bulan, tahun)
        )
        """
        try:
            temp = Pembayaran()
            temp.execute_query(query)
            print("✅ Tabel 'pembayaran' berhasil dibuat / sudah ada")
            return True
        except Exception as e:
            print(f"❌ Gagal membuat tabel pembayaran: {str(e)}")
            return False
    
    # ============================================
    # METHOD LAINNYA
    # ============================================
    def get_by_murid(self, murid_id):
        try:
            query = """
                SELECT * FROM pembayaran
                WHERE murid_id = %s
                ORDER BY tahun DESC, 
                         CASE bulan
                             WHEN 'Januari' THEN 1 WHEN 'Februari' THEN 2 WHEN 'Maret' THEN 3
                             WHEN 'April' THEN 4 WHEN 'Mei' THEN 5 WHEN 'Juni' THEN 6
                             WHEN 'Juli' THEN 7 WHEN 'Agustus' THEN 8 WHEN 'September' THEN 9
                             WHEN 'Oktober' THEN 10 WHEN 'November' THEN 11 WHEN 'Desember' THEN 12
                         END DESC
            """
            return self.execute_query(query, (murid_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_murid: {str(e)}")
            raise
    
    def get_all_with_murid(self):
        try:
            query = """
                SELECT p.*, u.username as murid_name, u.full_name as murid_full_name
                FROM pembayaran p
                JOIN users u ON p.murid_id = u.id
                ORDER BY p.tahun DESC, p.bulan DESC
            """
            return self.execute_query(query, fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_all_with_murid: {str(e)}")
            raise
    
    def get_total_paid_by_murid(self, murid_id):
        try:
            query = "SELECT COALESCE(SUM(nominal), 0) as total FROM pembayaran WHERE murid_id = %s AND status = 'lunas'"
            result = self.execute_query(query, (murid_id,), fetch_one=True)
            return result['total'] if result else 0
        except Exception as e:
            logger.error(f"Error in get_total_paid_by_murid: {str(e)}")
            return 0
    
    def insert(self, data):
        try:
            required_fields = ['murid_id', 'bulan', 'tahun', 'nominal']
            for field in required_fields:
                if field not in data or not data[field]:
                    raise ValueError(f"Field '{field}' harus diisi")
            
            if 'status' not in data or not data['status']:
                data['status'] = 'belum_bayar'
            
            data['created_at'] = datetime.now()
            data['updated_at'] = datetime.now()
            return super().insert(data)
        except Exception as e:
            logger.error(f"Error in insert: {str(e)}")
            raise