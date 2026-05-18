"""
Base Model with PostgreSQL Connection
Menggunakan psycopg2 untuk koneksi database lokal
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables langsung (tanpa import config untuk menghindari circular)
load_dotenv()

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """
    Abstract base class for all models
    Mengimplementasikan pewarisan (OOP Inheritance)
    """
    
    def __init__(self):
        self.primary_key = 'id'
        # Ambil konfigurasi langsung dari environment
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'Mahdiyah6822'),
            'database': os.getenv('DB_NAME', 'tk_ra_sadiah')
        }
    
    def get_connection(self):
        """
        Get PostgreSQL database connection
        Time Complexity: O(1)
        """
        try:
            conn = psycopg2.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config['port']
            )
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    @abstractmethod
    def get_table_name(self):
        """
        Abstract method to get table name
        Harus diimplementasikan oleh child class
        """
        pass
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """
        Execute database query with error handling
        Time Complexity: O(n) where n is number of rows affected
        """
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
            
        except psycopg2.Error as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {str(e)}")
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Unexpected error: {str(e)}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_all(self, limit=None, offset=None, order_by=None):
        """Get all records with pagination"""
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
        """Get record by ID"""
        try:
            query = f"SELECT * FROM {self.get_table_name()} WHERE {self.primary_key} = %s"
            return self.execute_query(query, (record_id,), fetch_one=True)
        except Exception as e:
            logger.error(f"Error in get_by_id: {str(e)}")
            raise
    
    def insert(self, data):
        """Insert new record"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            query = f"INSERT INTO {self.get_table_name()} ({columns}) VALUES ({placeholders}) RETURNING {self.primary_key}"
            result = self.execute_query(query, tuple(data.values()), fetch_one=True)
            return result[self.primary_key] if result else None
        except Exception as e:
            logger.error(f"Error in insert: {str(e)}")
            raise
    
    def update(self, record_id, data):
        """Update record by ID"""
        try:
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {self.get_table_name()} SET {set_clause} WHERE {self.primary_key} = %s"
            params = tuple(data.values()) + (record_id,)
            return self.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
            raise
    
    def delete(self, record_id):
        """Delete record by ID"""
        try:
            query = f"DELETE FROM {self.get_table_name()} WHERE {self.primary_key} = %s"
            return self.execute_query(query, (record_id,))
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            raise
    
    def sequential_search(self, records, key, search_value):
        """
        Sequential search implementation
        Time Complexity: O(n) where n is number of records
        """
        try:
            results = []
            comparisons = 0
            
            for record in records:
                comparisons += 1
                if (str(record.get(key, '')).lower() == str(search_value).lower() or
                    str(record.get('username', '')).lower().find(str(search_value).lower()) != -1 or
                    str(record.get('full_name', '')).lower().find(str(search_value).lower()) != -1):
                    results.append(record)
            
            logger.info(f"Sequential search completed: {comparisons} comparisons, {len(results)} results")
            return results, comparisons
        except Exception as e:
            logger.error(f"Error in sequential_search: {str(e)}")
            raise