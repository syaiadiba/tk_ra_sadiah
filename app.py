"""
TK RA SA'DIAH Web Application
Main application file for Flask web server
"""

from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
import os
import logging
from dotenv import load_dotenv
from config import config_dict

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config = config_dict.get(config_name, config_dict['default'])
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = config.DEBUG
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Silakan login terlebih dahulu'
    login_manager.login_message_category = 'info'
    
    # Import models here to avoid circular imports
    from models.user_model import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        try:
            return User.get(int(user_id))
        except Exception as e:
            logger.error(f"Error loading user: {str(e)}")
            return None
    
    # Register all blueprints
    try:
        from blueprints.auth_bp import auth_bp
        from blueprints.murid_bp import murid_bp
        from blueprints.guru_bp import guru_bp
        from blueprints.admin_bp import admin_bp
        from blueprints.umum_bp import umum_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(murid_bp)
        app.register_blueprint(guru_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(umum_bp)
        
        logger.info("All blueprints registered successfully")
        
    except ImportError as e:
        logger.error(f"Blueprint import error: {str(e)}")
    except Exception as e:
        logger.error(f"Error registering blueprints: {str(e)}")
    
    # Default route
    @app.route('/')
    def index():
        """Home page - redirect to login"""
        if current_user.is_authenticated:
            if current_user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif current_user.role == 'guru':
                return redirect(url_for('guru.dashboard'))
            elif current_user.role == 'murid':
                return redirect(url_for('murid.dashboard'))
        return redirect(url_for('auth.login'))
    
    logger.info("Application initialized successfully")
    return app


# ============================================
# CREATE APP INSTANCE FOR GUNICORN (PRODUCTION)
# ============================================
app = create_app()


# ============================================
# MAIN (Untuk Development)
# ============================================
if __name__ == '__main__':
    # Get configuration from environment
    flask_env = os.getenv('FLASK_ENV', 'development')
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print("=" * 60)
    print("🏫 TK RA SA'DIAH - SISTEM INFORMASI SEKOLAH")
    print("=" * 60)
    print(f"🌍 Environment: {flask_env}")
    print(f"🗄️  Database: Supabase (PostgreSQL Cloud)")
    print("=" * 60)
    print(f"\n🚀 Server: http://{host}:{port}")
    print("=" * 60)
    print("\n📝 AKUN DEFAULT:")
    print("   👑 Admin  - admin / admin123")
    print("   👩‍🏫 Guru   - guru / admin123")
    print("   👧 Murid  - murid1 / admin123")
    print("=" * 60)
    print("\n🚀 Starting server...\n")
    
    # App already created, just run it
    app.run(host=host, port=port, debug=app.config['DEBUG'])