"""
Configuration for TK RA SA'DIAH
Menggunakan Supabase (PostgreSQL Cloud)
"""

import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', '881a10aa6949dac202a7c6b42565848350761e91ae30272daf1e7b7ca029f1ad')
    
    # ============================================
    # SUPABASE CONFIGURATION
    # ============================================
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', '')
    DATABASE_URL = os.getenv('DATABASE_URL', '')
    
    @classmethod
    def get_db_config(cls):
        """Return database config untuk psycopg2"""
        return cls.DATABASE_URL
    
    @classmethod
    def get_supabase_client(cls):
        """Get Supabase client"""
        if cls.SUPABASE_URL and cls.SUPABASE_KEY:
            from supabase import create_client
            return create_client(cls.SUPABASE_URL, cls.SUPABASE_KEY)
        return None


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