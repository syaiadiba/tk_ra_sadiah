"""
Pembelajaran Model for TK RA SA'DIAH
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class Pembelajaran:
    """Pembelajaran model for teacher's lessons"""
    
    def __init__(self):
        self.table_name = 'pembelajaran'
    
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
    
    def get_by_guru(self, guru_id):
        """Get lessons by teacher ID"""
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
            return []
    
    def get_all_with_guru(self):
        """Get all lessons with teacher info"""
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
            return []
    
    def get_by_id(self, record_id):
        """Get lesson by ID"""
        try:
            query = "SELECT * FROM pembelajaran WHERE id = %s"
            return self.execute_query(query, (record_id,), fetch_one=True)
        except Exception as e:
            logger.error(f"Error in get_by_id: {str(e)}")
            return None
    
    def insert(self, data):
        """Insert new lesson"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO pembelajaran ({columns}) VALUES ({placeholders}) RETURNING id"
            result = self.execute_query(query, tuple(data.values()), fetch_one=True)
            return result['id'] if result else None
        except Exception as e:
            logger.error(f"Error in insert: {str(e)}")
            raise
    
    def update(self, record_id, data):
        """Update lesson"""
        try:
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE pembelajaran SET {set_clause} WHERE id = %s"
            params = tuple(data.values()) + (record_id,)
            return self.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
            raise
    
    def delete(self, record_id):
        """Delete lesson"""
        try:
            query = "DELETE FROM pembelajaran WHERE id = %s"
            return self.execute_query(query, (record_id,))
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            raise