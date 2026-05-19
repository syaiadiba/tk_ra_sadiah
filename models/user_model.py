"""
User Model for TK RA SA'DIAH
"""

from .base_model import BaseModel
import bcrypt
import logging
from flask_login import UserMixin

logger = logging.getLogger(__name__)


class User(BaseModel, UserMixin):
    """User model for authentication"""
    
    def __init__(self, id=None, username=None, role=None, password_hash=None, full_name=None):
        super().__init__()
        self.id = id
        self.username = username
        self.role = role
        self.password_hash = password_hash
        self.full_name = full_name
    
    def get_table_name(self):
        return 'users'
    
    # ============================================
    # CREATE TABLE METHOD - PERBAIKI INI!
    # ============================================
    @classmethod
    def create_table(cls):
        """
        Create users table in PostgreSQL
        Menggunakan @classmethod agar bisa dipanggil tanpa instance
        """
        query = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL CHECK (role IN ('murid', 'guru', 'admin')),
            full_name VARCHAR(200),
            reset_token VARCHAR(100),
            reset_token_expiry TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        try:
            # Buat instance temporary untuk execute_query
            temp = User()
            temp.execute_query(query)
            print("✅ Tabel 'users' berhasil dibuat / sudah ada")
            return True
        except Exception as e:
            print(f"❌ Gagal membuat tabel users: {str(e)}")
            return False
    
    # ============================================
    # METHOD LAINNYA
    # ============================================
    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        return self.password_hash
    
    def check_password(self, password):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password check error: {str(e)}")
            return False
    
    def get_by_username(self, username):
        try:
            query = "SELECT * FROM users WHERE username = %s"
            return self.execute_query(query, (username,), fetch_one=True)
        except Exception as e:
            logger.error(f"Error in get_by_username: {str(e)}")
            raise
    
    def get_by_role(self, role):
        try:
            query = "SELECT * FROM users WHERE role = %s ORDER BY username"
            return self.execute_query(query, (role,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_role: {str(e)}")
            raise
    
    @staticmethod
    def authenticate(username, password):
        try:
            user_model = User()
            user_data = user_model.get_by_username(username)
            if user_data:
                user = User(
                    id=user_data['id'],
                    username=user_data['username'],
                    role=user_data['role'],
                    password_hash=user_data['password_hash']
                )
                if user.check_password(password):
                    return user
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    @staticmethod
    def get(user_id):
        try:
            user_model = User()
            user_data = user_model.get_by_id(int(user_id))
            if user_data:
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    role=user_data['role'],
                    password_hash=user_data['password_hash'],
                    full_name=user_data.get('full_name')
                )
            return None
        except Exception as e:
            logger.error(f"Error getting user: {str(e)}")
            return None
    
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False