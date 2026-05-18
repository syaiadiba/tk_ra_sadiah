"""
TK RA SA'DIAH Web Application
Main application file for Flask web server
"""

from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
import os
import logging
from dotenv import load_dotenv
from config import Config, DevelopmentConfig, ProductionConfig

# Load environment variables
load_dotenv()

config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
logger = logging.getLogger(__name__)


def create_app(config_name='default'):
    """
    Application factory pattern
    Time Complexity: O(1)
    
    # UNTUK ANDA GANTI: Sesuaikan konfigurasi sesuai kebutuhan
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['DEBUG'] = True if config_name == 'development' else False
    
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
    
    # UNTUK ANDA GANTI: Jalankan sekali saat pertama kali setup
    """
    from models.user_model import User
    from models.pembelajaran_model import Pembelajaran
    from models.tanggapan_model import Tanggapan
    from models.pembayaran_model import Pembayaran
    
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
        password_hash = user.set_password('admin123')
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
        password_hash = user.set_password('admin123')
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
        password_hash = user.set_password('admin123')
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
    
    # Check and create sample lessons
    pembelajaran_model = Pembelajaran()
    lessons = pembelajaran_model.get_all()
    if not lessons:
        guru_data = user_model.get_by_username('guru')
        if guru_data:
            data_lesson = {
                'guru_id': guru_data['id'],
                'judul': 'Pengenalan Huruf Hijaiyah',
                'konten': 'Assalamualaikum anak-anak! Hari ini kita akan belajar mengenal huruf hijaiyah. Huruf hijaiyah ada 29 huruf. Mari kita mulai dari huruf Alif, Ba, Ta, Tsa...'
            }
            pembelajaran_model.insert(data_lesson)
            
            data_lesson2 = {
                'guru_id': guru_data['id'],
                'judul': 'Belajar Berhitung 1-10',
                'konten': 'Halo adik-adik! Hari ini kita belajar berhitung dari 1 sampai 10. Sambil menyanyi yuk! Satu, dua, tiga, empat, lima, enam, tujuh, delapan, sembilan, sepuluh!'
            }
            pembelajaran_model.insert(data_lesson2)
            print("✅ Contoh pembelajaran dibuat")
    
    # Check and create sample payments
    pembayaran_model = Pembayaran()
    payments = pembayaran_model.get_all()
    if not payments:
        murids = user_model.get_by_role('murid')
        for m in murids:
            data_payment = {
                'murid_id': m['id'],
                'bulan': 'Januari',
                'tahun': 2024,
                'nominal': 500000,
                'status': 'lunas'
            }
            pembayaran_model.insert(data_payment)
            
            data_payment2 = {
                'murid_id': m['id'],
                'bulan': 'Februari',
                'tahun': 2024,
                'nominal': 500000,
                'status': 'lunas'
            }
            pembayaran_model.insert(data_payment2)
            
            data_payment3 = {
                'murid_id': m['id'],
                'bulan': 'Maret',
                'tahun': 2024,
                'nominal': 500000,
                'status': 'belum_bayar'
            }
            pembayaran_model.insert(data_payment3)
        print("✅ Contoh pembayaran dibuat")
    
    print("=" * 60)
    print("✅ Database siap digunakan!")
    print("=" * 60)
    return True


# ============================================
# MAIN
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
    app = create_app(flask_env)
    
    # Run the application
    app.run(host=host, port=port, debug=app.config['DEBUG'])