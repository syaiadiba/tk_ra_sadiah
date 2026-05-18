"""
Tanggapan Model for TK RA SA'DIAH
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Tanggapan:
    """Tanggapan model for student responses"""
    
    def __init__(self):
        self.table_name = 'tanggapan'
    
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
    
    def get_by_pembelajaran(self, pembelajaran_id):
        """Get responses by lesson ID"""
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
            return []
    
    def get_by_murid(self, murid_id):
        """Get responses by student ID"""
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
            return []
    
    def get_by_id(self, record_id):
        """Get response by ID"""
        try:
            query = "SELECT * FROM tanggapan WHERE id = %s"
            return self.execute_query(query, (record_id,), fetch_one=True)
        except Exception as e:
            logger.error(f"Error in get_by_id: {str(e)}")
            return None
    
    def has_responded(self, murid_id, pembelajaran_id):
        """Check if student has responded"""
        try:
            query = "SELECT COUNT(*) as total FROM tanggapan WHERE murid_id = %s AND pembelajaran_id = %s"
            result = self.execute_query(query, (murid_id, pembelajaran_id), fetch_one=True)
            return result['total'] > 0 if result else False
        except Exception as e:
            logger.error(f"Error in has_responded: {str(e)}")
            return False
    
    def insert(self, data):
        """Insert new response"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO tanggapan ({columns}) VALUES ({placeholders}) RETURNING id"
            result = self.execute_query(query, tuple(data.values()), fetch_one=True)
            return result['id'] if result else None
        except Exception as e:
            logger.error(f"Error in insert: {str(e)}")
            raise