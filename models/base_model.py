"""
Base Model with PostgreSQL Connection
Menggunakan Database URL Builder dari config
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from abc import ABC, abstractmethod
from config import Config

logger = logging.getLogger(__name__)


class BaseModel(ABC):
    """Abstract base class for all models"""
    
    def __init__(self):
        self.primary_key = 'id'
        # Ambil konfigurasi dari Config
        self.db_config = Config.get_db_config()
        self.db_url = Config.build_database_url()  # ← Database URL Builder
    
    def get_connection(self):
        """Get PostgreSQL database connection"""
        try:
            # Cara 1: Pakai dictionary config
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
    
    def get_connection_from_url(self):
        """Alternatif: Koneksi menggunakan URL (cara lain)"""
        try:
            conn = psycopg2.connect(self.db_url)
            return conn
        except Exception as e:
            logger.error(f"Database connection error (URL): {str(e)}")
            raise
    
    @abstractmethod
    def get_table_name(self):
        pass
    
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
    
    def get_all(self, limit=None, offset=None, order_by=None):
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
        try:
            query = f"SELECT * FROM {self.get_table_name()} WHERE {self.primary_key} = %s"
            return self.execute_query(query, (record_id,), fetch_one=True)
        except Exception as e:
            logger.error(f"Error in get_by_id: {str(e)}")
            raise
    
    def insert(self, data):
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
        try:
            set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
            query = f"UPDATE {self.get_table_name()} SET {set_clause} WHERE {self.primary_key} = %s"
            params = tuple(data.values()) + (record_id,)
            return self.execute_query(query, params)
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
            raise
    
    def delete(self, record_id):
        try:
            query = f"DELETE FROM {self.get_table_name()} WHERE {self.primary_key} = %s"
            return self.execute_query(query, (record_id,))
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            raise
    
    def sequential_search(self, records, key, search_value):
        """Sequential search implementation - Time Complexity: O(n)"""
        try:
            results = []
            comparisons = 0
            for record in records:
                comparisons += 1
                if (str(record.get(key, '')).lower() == str(search_value).lower() or
                    str(record.get('username', '')).lower().find(str(search_value).lower()) != -1 or
                    str(record.get('full_name', '')).lower().find(str(search_value).lower()) != -1):
                    results.append(record)
            logger.info(f"Sequential search: {comparisons} comparisons, {len(results)} results")
            return results, comparisons
        except Exception as e:
            logger.error(f"Error in sequential_search: {str(e)}")
            raise