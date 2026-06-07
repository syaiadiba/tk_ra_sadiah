"""
Base Model - Koneksi ke Supabase dengan pg8000
"""

import os
import pg8000
import logging
from abc import ABC, abstractmethod
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
logger = logging.getLogger(__name__)


class BaseModel(ABC):
    
    def __init__(self):
        self.primary_key = 'id'
        self.database_url = os.getenv('DATABASE_URL', '')
    
    def get_connection(self):
        """
        Koneksi ke Supabase menggunakan pg8000 dengan parameter terpisah
        """
        if not self.database_url:
            raise Exception("DATABASE_URL tidak ditemukan! Periksa file .env")
        
        try:
            # Parse URL menjadi komponen terpisah
            parsed = urlparse(self.database_url)
            
            user = parsed.username
            password = parsed.password
            host = parsed.hostname
            port = parsed.port or 5432
            database = parsed.path.lstrip('/')
            
            print(f"🔍 Connecting to: {host}:{port} as {user}")
            
            # Koneksi dengan parameter terpisah
            conn = pg8000.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database=database
            )
            print("✅ Connected to Supabase!")
            return conn
            
        except Exception as e:
            print(f"❌ Connection error: {e}")
            raise
    
    @abstractmethod
    def get_table_name(self):
        pass
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            
            if fetch_one:
                result = cursor.fetchone()
                if result:
                    columns = [desc[0] for desc in cursor.description]
                    result = dict(zip(columns, result))
                return result
            elif fetch_all:
                results = cursor.fetchall()
                if results:
                    columns = [desc[0] for desc in cursor.description]
                    results = [dict(zip(columns, row)) for row in results]
                return results
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
        try:
            query = f"DELETE FROM {self.get_table_name()} WHERE {self.primary_key} = %s"
            return self.execute_query(query, (record_id,))
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            raise