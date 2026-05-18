"""
Pembayaran Model for TK RA SA'DIAH
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Pembayaran:
    """Pembayaran model for student payments"""
    
    def __init__(self):
        self.table_name = 'pembayaran'
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'tk_ra_sadiah'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Mahdiyah6822'),
            port=os.getenv('DB_PORT', '5432')
        )
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Execute database query"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
            
            return result
            
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_table_name(self):
        return self.table_name
    
    def get_by_murid(self, murid_id):
        """Get payments by student ID"""
        try:
            query = "SELECT * FROM pembayaran WHERE murid_id = %s ORDER BY tahun DESC, bulan DESC"
            return self.execute_query(query, (murid_id,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_murid: {str(e)}")
            return []
    
    def get_all_with_murid(self):
        """Get all payments with student info"""
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
            return []
    
    def get_total_paid_by_murid(self, murid_id):
        """Get total paid amount by student"""
        try:
            query = "SELECT COALESCE(SUM(nominal), 0) as total FROM pembayaran WHERE murid_id = %s AND status = 'lunas'"
            result = self.execute_query(query, (murid_id,), fetch_one=True)
            return result['total'] if result else 0
        except Exception as e:
            logger.error(f"Error in get_total_paid_by_murid: {str(e)}")
            return 0
    
    def insert(self, data):
        """Insert new payment"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO pembayaran ({columns}) VALUES ({placeholders}) RETURNING id"
            result = self.execute_query(query, tuple(data.values()), fetch_one=True)
            return result['id'] if result else None
        except Exception as e:
            logger.error(f"Error in insert: {str(e)}")
            raise
    
    def update(self, record_id, data):
        """Update payment"""
        try:
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE pembayaran SET {set_clause} WHERE id = %s"
            params = tuple(data.values()) + (record_id,)
            return self.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
            raise
    
    def delete(self, record_id):
        """Delete payment"""
        try:
            query = "DELETE FROM pembayaran WHERE id = %s"
            return self.execute_query(query, (record_id,))
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            raise