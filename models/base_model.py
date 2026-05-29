"""
Base Model - Disesuaikan untuk Supabase
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from abc import ABC, abstractmethod
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class BaseModel(ABC):
    
    def __init__(self):
        self.primary_key = 'id'  # Default, bisa di-override
        # Gunakan DATABASE_URL dari environment (Supabase)
        self.database_url = os.getenv('DATABASE_URL', '')
    
    def get_connection(self):
        """
        Get database connection menggunakan DATABASE_URL (Supabase)
        """
        try:
            if not self.database_url:
                raise Exception("DATABASE_URL tidak ditemukan di environment!")
            
            # Koneksi langsung menggunakan URL
            conn = psycopg2.connect(self.database_url)
            return conn
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            print(f"❌ Gagal koneksi ke Supabase: {str(e)}")
            print("   Periksa DATABASE_URL di file .env")
            raise
    
    @abstractmethod
    def get_table_name(self):
        pass
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params or ())
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Query error: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    # ============================================
    # METHOD CRUD
    # ============================================
    
    def get_all(self, limit=None, offset=None, order_by=None):
        """
        Get all records with pagination
        Time Complexity: O(n)
        """
        try:
            query = f"SELECT * FROM {self.get_table_name()}"
            if order_by:
                query += f" ORDER BY {order_by}"
            if limit:
                query += f" LIMIT {limit}"
            if offset:
                query += f" OFFSET {offset}"
            return self.execute_query(query, fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_all: {str(e)}")
            raise
    
    def get_by_id(self, record_id):
        """
        Get record by ID
        Time Complexity: O(log n)
        """
        try:
            query = f"SELECT * FROM {self.get_table_name()} WHERE {self.primary_key} = %s"
            return self.execute_query(query, (record_id,), fetch_one=True)
        except Exception as e:
            logger.error(f"Error in get_by_id: {str(e)}")
            raise
    
    def count(self):
        """
        Get total number of records
        Time Complexity: O(n)
        """
        try:
            query = f"SELECT COUNT(*) as total FROM {self.get_table_name()}"
            result = self.execute_query(query, fetch_one=True)
            return result['total'] if result else 0
        except Exception as e:
            logger.error(f"Error in count: {str(e)}")
            raise
    
    def insert(self, data):
        """
        Insert new record
        Time Complexity: O(1)
        """
        try:
            if not data:
                raise ValueError("Data tidak boleh kosong")
            
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {self.get_table_name()} ({columns}) VALUES ({placeholders}) RETURNING {self.primary_key}"
            
            result = self.execute_query(query, tuple(data.values()), fetch_one=True)
            return result[self.primary_key] if result else None
        except Exception as e:
            logger.error(f"Error in insert: {str(e)}")
            raise
    
    def update(self, record_id, data):
        """
        Update record by ID
        Time Complexity: O(1)
        """
        try:
            if not data:
                raise ValueError("Data update tidak boleh kosong")
            
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {self.get_table_name()} SET {set_clause} WHERE {self.primary_key} = %s"
            params = tuple(data.values()) + (record_id,)
            return self.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
            raise
    
    def delete(self, record_id):
        """
        Delete record by ID
        Time Complexity: O(1)
        """
        try:
            query = f"DELETE FROM {self.get_table_name()} WHERE {self.primary_key} = %s"
            return self.execute_query(query, (record_id,))
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            raise