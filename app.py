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
    
    # ============================================
    # TEMPLATE FILTERS
    # ============================================
    
    @app.template_filter('format_rp')
    def format_rp(value):
        """Format angka menjadi Rupiah (contoh: 500000 -> 500.000)"""
        try:
            if value is None:
                return '0'
            return f"{int(value):,}".replace(',', '.')
        except (ValueError, TypeError):
            return str(value)
    
    @app.template_filter('format_date')
    def format_date(value):
        """Format tanggal menjadi dd/mm/yyyy"""
        try:
            if value is None:
                return '-'
            if isinstance(value, str):
                from datetime import datetime
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value.strftime('%d/%m/%Y')
        except:
            return str(value)
    
    @app.template_filter('format_datetime')
    def format_datetime(value):
        """Format datetime menjadi dd/mm/yyyy HH:MM"""
        try:
            if value is None:
                return '-'
            if isinstance(value, str):
                from datetime import datetime
                value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value.strftime('%d/%m/%Y %H:%M')
        except:
            return str(value)
    
    @app.template_filter('format_phone')
    def format_phone(value):
        """Format nomor telepon (contoh: 081234567890 -> 0812-3456-7890)"""
        try:
            if not value:
                return '-'
            phone = str(value).strip()
            if len(phone) == 12:
                return f"{phone[:4]}-{phone[4:8]}-{phone[8:]}"
            elif len(phone) == 11:
                return f"{phone[:4]}-{phone[4:7]}-{phone[7:]}"
            return phone
        except:
            return str(value)
    
    @app.template_filter('truncate')
    def truncate(value, length=50, suffix='...'):
        """Potong teks jika lebih dari panjang tertentu"""
        try:
            if not value:
                return ''
            if len(value) <= length:
                return value
            return value[:length] + suffix
        except:
            return str(value)
    
    @app.template_filter('status_badge')
    def status_badge(value):
        """Konversi status menjadi badge HTML"""
        status_map = {
            'lunas': '<span class="badge bg-success"><i class="fas fa-check-circle"></i> Lunas</span>',
            'belum_bayar': '<span class="badge bg-danger"><i class="fas fa-times-circle"></i> Belum Bayar</span>',
            'aktif': '<span class="badge bg-success"><i class="fas fa-check-circle"></i> Aktif</span>',
            'tidak_aktif': '<span class="badge bg-secondary"><i class="fas fa-times-circle"></i> Tidak Aktif</span>',
        }
        return status_map.get(str(value).lower(), f'<span class="badge bg-secondary">{value}</span>')
    
    # ============================================
    # REGISTER BLUEPRINTS
    # ============================================
    print("\n" + "=" * 60)
    print("🔵 REGISTERING BLUEPRINTS...")
    print("=" * 60)
    
    try:
        from blueprints.auth_bp import auth_bp
        print("✅ auth_bp imported")
        
        from blueprints.admin_bp import admin_bp
        print("✅ admin_bp imported")
        
        from blueprints.guru_bp import guru_bp
        print("✅ guru_bp imported")
        
        from blueprints.murid_bp import murid_bp
        print("✅ murid_bp imported")
        
        from blueprints.umum_bp import umum_bp
        print("✅ umum_bp imported")
        
        app.register_blueprint(auth_bp)
        print("✅ auth_bp registered")
        
        app.register_blueprint(admin_bp)
        print("✅ admin_bp registered")
        
        app.register_blueprint(guru_bp)
        print("✅ guru_bp registered")
        
        app.register_blueprint(murid_bp)
        print("✅ murid_bp registered")
        
        app.register_blueprint(umum_bp)
        print("✅ umum_bp registered")
        
        logger.info("Blueprints registered successfully")
        
    except ImportError as e:
        logger.error(f"Blueprint import error: {str(e)}")
        print(f"❌ Blueprint import error: {e}")
    except Exception as e:
        logger.error(f"Error registering blueprints: {str(e)}")
        print(f"❌ Error registering blueprints: {e}")
    
    # ============================================
    # PRINT ALL ROUTES FOR DEBUGGING
    # ============================================
    print("\n" + "=" * 60)
    print("📋 ALL REGISTERED ROUTES:")
    print("=" * 60)
    for rule in app.url_map.iter_rules():
        print(f"   {rule.endpoint} -> {rule.rule}")
    print("=" * 60 + "\n")
    
    # Default route
    @app.route('/')
    def index():
        """Home page - redirect to login"""
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
    
    app.run(host=host, port=port, debug=app.config['DEBUG'])