"""
User Model for TK RA SA'DIAH
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import logging
import os
from flask_login import UserMixin
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, id=None, username=None, role=None, password_hash=None, full_name=None):
        self.id = id
        self.username = username
        self.role = role
        self.password_hash = password_hash
        self.full_name = full_name
    
    def get_id(self):
        return str(self.id)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    @staticmethod
    def get_connection():
        """Get database connection"""
        return psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'tk_ra_sadiah'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'Mahdiyah6822'),
            port=os.getenv('DB_PORT', '5432')
        )
    
    @staticmethod
    def execute_query(query, params=None, fetch_one=False, fetch_all=False):
        """Execute database query"""
        conn = None
        cursor = None
        try:
            conn = User.get_connection()
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
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        try:
            query = "SELECT * FROM users WHERE id = %s"
            return User.execute_query(query, (user_id,), fetch_one=True)
        except Exception as e:
            logger.error(f"Error in get_by_id: {str(e)}")
            return None
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        try:
            query = "SELECT * FROM users WHERE username = %s"
            return User.execute_query(query, (username,), fetch_one=True)
        except Exception as e:
            logger.error(f"Error in get_by_username: {str(e)}")
            return None
    
    @staticmethod
    def get_by_role(role):
        """Get all users by role"""
        try:
            query = "SELECT * FROM users WHERE role = %s ORDER BY username"
            return User.execute_query(query, (role,), fetch_all=True) or []
        except Exception as e:
            logger.error(f"Error in get_by_role: {str(e)}")
            return []
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate user"""
        try:
            user_data = User.get_by_username(username)
            if user_data:
                if bcrypt.checkpw(password.encode('utf-8'), user_data['password_hash'].encode('utf-8')):
                    return User(
                        id=user_data['id'],
                        username=user_data['username'],
                        role=user_data['role'],
                        password_hash=user_data['password_hash'],
                        full_name=user_data.get('full_name')
                    )
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    @staticmethod
    def get(user_id):
        """Get user for Flask-Login"""
        user_data = User.get_by_id(int(user_id))
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                role=user_data['role'],
                password_hash=user_data['password_hash'],
                full_name=user_data.get('full_name')
            )
        return None
    
    def set_password(self, password):
        """Hash password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        return self.password_hash
    
    def save(self):
        """Save user to database"""
        try:
            query = """
                INSERT INTO users (username, password_hash, role, full_name)
                VALUES (%s, %s, %s, %s) RETURNING id
            """
            result = User.execute_query(
                query, 
                (self.username, self.password_hash, self.role, self.full_name),
                fetch_one=True
            )
            self.id = result['id'] if result else None
            return self.id
        except Exception as e:
            logger.error(f"Error saving user: {str(e)}")
            raise