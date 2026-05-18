"""
TK RA SA'DIAH Web Application
Main application file for Flask web server
"""

from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# KONFIGURASI - LANGSUNG DARI ENV (TANPA IMPORT CONFIG)
# ============================================
class AppConfig:
    """Simple configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = True if os.getenv('FLASK_ENV', 'development') == 'development' else False
    
    # Database config
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Mahdiyah6822')
    DB_NAME = os.getenv('DB_NAME', 'tk_ra_sadiah')
    
    @classmethod
    def get_db_config(cls):
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME
        }


def create_app():
    """
    Application factory pattern
    Time Complexity: O(1)
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = AppConfig.SECRET_KEY
    app.config['DEBUG'] = AppConfig.DEBUG
    
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
        """Load user by ID for Flask-Login - Time Complexity: O(log n)"""
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


def init_database():
    """
    Initialize database tables and default data
    Time Complexity: O(1) for table creation, O(n) for data insertion
    """
    from models.user_model import User
    from models.pembelajaran_model import Pembelajaran
    from models.tanggapan_model import Tanggapan
    from models.pembayaran_model import Pembayaran
    import bcrypt
    
    print("\n" + "=" * 60)
    print("📦 Inisialisasi Database PostgreSQL")
    print("=" * 60)
    
    # Create all tables
    try:
        User.create_table()
        print("✅ Tabel 'users' siap")
        
        Pembelajaran.create_table()
        print("✅ Tabel 'pembelajaran' siap")
        
        Tanggapan.create_table()
        print("✅ Tabel 'tanggapan' siap")
        
        Pembayaran.create_table()
        print("✅ Tabel 'pembayaran' siap")
        
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        return False
    
    # Check and create default admin
    user_model = User()
    admin = user_model.get_by_username('admin')
    if not admin:
        user = User()
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), salt).decode('utf-8')
        data = {
            'username': 'admin',
            'password_hash': password_hash,
            'role': 'admin',
            'full_name': 'Administrator TK RA SA\'DIAH'
        }
        user.insert(data)
        print("✅ Admin default dibuat (username: admin, password: admin123)")
    
    # Check and create default guru
    guru = user_model.get_by_username('guru')
    if not guru:
        user = User()
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), salt).decode('utf-8')
        data = {
            'username': 'guru',
            'password_hash': password_hash,
            'role': 'guru',
            'full_name': 'Guru TK RA SA\'DIAH'
        }
        user.insert(data)
        print("✅ Guru default dibuat (username: guru, password: admin123)")
    
    # Check and create default murid
    murid1 = user_model.get_by_username('murid1')
    if not murid1:
        user = User()
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw('admin123'.encode('utf-8'), salt).decode('utf-8')
        data = {
            'username': 'murid1',
            'password_hash': password_hash,
            'role': 'murid',
            'full_name': 'Aisyah Putri'
        }
        user.insert(data)
        
        user2 = User()
        data2 = {
            'username': 'murid2',
            'password_hash': password_hash,
            'role': 'murid',
            'full_name': 'Muhammad Rizki'
        }
        user2.insert(data2)
        print("✅ Murid default dibuat (username: murid1/murid2, password: admin123)")
    
    print("=" * 60)
    print("✅ Database siap digunakan!")
    print("=" * 60)
    return True


# ============================================
# MAIN
# ============================================
if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print("=" * 60)
    print("🏫 TK RA SA'DIAH - SISTEM INFORMASI SEKOLAH")
    print("=" * 60)
    print(f"🗄️  Database: PostgreSQL Lokal")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    print(f"\n🚀 Server: http://{host}:{port}")
    print("=" * 60)
    print("\n📝 AKUN DEFAULT:")
    print("   👑 Admin  - username: admin  | password: admin123")
    print("   👩‍🏫 Guru   - username: guru   | password: admin123")
    print("   👧 Murid  - username: murid1 | password: admin123")
    print("=" * 60)
    print("\n✨ FITUR:")
    print("   ✅ Multi-role (Admin, Guru, Murid)")
    print("   ✅ Admin: CRUD siswa, guru, pembayaran SPP, sequential search")
    print("   ✅ Guru: CRUD pembelajaran, lihat tanggapan siswa")
    print("   ✅ Murid: lihat pembelajaran, beri tanggapan, lihat keuangan")
    print("   ✅ Lupa password dengan token reset")
    print("=" * 60)
    print("\n🚀 Starting server...\n")
    
    # Create app instance
    app = create_app()
    
    # Run the application
    app.run(host=host, port=port, debug=app.config['DEBUG'])