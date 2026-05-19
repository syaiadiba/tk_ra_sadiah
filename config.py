"""
Configuration for TK RA SA'DIAH
Menggunakan PostgreSQL Lokal dengan Database Builder
"""

import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', '881a10aa6949dac202a7c6b42565848350761e91ae30272daf1e7b7ca029f1ad')
    
    # PostgreSQL Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'tk_ra_sadiah')
    
    # ============================================
    # DATABASE URL BUILDER - INI YANG PENTING!
    # ============================================
    @classmethod
    def build_database_url(cls):
        """
        Membangun URL database dari konfigurasi
        Format: postgresql://user:password@host:port/database
        """
        # Encode password untuk karakter spesial (@, #, $, dll)
        encoded_password = quote_plus(cls.DB_PASSWORD) if cls.DB_PASSWORD else ''
        
        # Bangun URL
        database_url = f"postgresql://{cls.DB_USER}:{encoded_password}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        
        return database_url
    
    @classmethod
    def get_db_config(cls):
        """Return dictionary config untuk psycopg2"""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME
        }
    
    @classmethod
    def get_safe_url(cls):
        """Return URL dengan password tersembunyi (untuk logging)"""
        url = cls.build_database_url()
        return url.replace(cls.DB_PASSWORD, '******') if cls.DB_PASSWORD else url


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


__all__ = ['Config', 'DevelopmentConfig', 'ProductionConfig']

config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}