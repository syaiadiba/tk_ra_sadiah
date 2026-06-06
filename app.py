"""
TK RA SA'DIAH Web Application
Main application file for Flask web server
"""

from flask import Flask, redirect, url_for, request, render_template_string
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
    # REGISTER BLUEPRINTS - DENGAN DEBUG PRINT
    # ============================================
    print("\n" + "=" * 60)
    print("🔵 REGISTERING BLUEPRINTS...")
    print("=" * 60)
    
    try:
        from blueprints.auth_bp import auth_bp
        print("✅ auth_bp imported")
        
        # ============================================
        # UNTUK TESTING, COMMENT 3 BLUEPRINT DI BAWAH INI
        # ============================================
        # from blueprints.murid_bp import murid_bp
        # print("✅ murid_bp imported")
        # from blueprints.guru_bp import guru_bp
        # print("✅ guru_bp imported")
        # from blueprints.admin_bp import admin_bp
        # print("✅ admin_bp imported")
        
        from blueprints.umum_bp import umum_bp
        print("✅ umum_bp imported")
        
        app.register_blueprint(auth_bp)
        print("✅ auth_bp registered")
        
        # ============================================
        # UNTUK TESTING, COMMENT 3 BLUEPRINT DI BAWAH INI
        # ============================================
        # app.register_blueprint(murid_bp)
        # print("✅ murid_bp registered")
        # app.register_blueprint(guru_bp)
        # print("✅ guru_bp registered")
        # app.register_blueprint(admin_bp)
        # print("✅ admin_bp registered")
        
        app.register_blueprint(umum_bp)
        print("✅ umum_bp registered")
        
        logger.info("All blueprints registered successfully")
        
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
    
    # ============================================
    # FALLBACK ROUTE - JIKA BLUEPRINT GAGAL
    # ============================================
    @app.route('/auth/login', methods=['GET', 'POST'])
    def fallback_auth_login():
        """Fallback login jika blueprint auth tidak berfungsi"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            role = request.form.get('role')
            
            if username == 'admin' and password == 'admin123':
                from flask_login import login_user
                class SimpleUser:
                    id = 1
                    role = role
                    full_name = 'Administrator'
                    is_authenticated = True
                    def get_id(self):
                        return str(self.id)
                login_user(SimpleUser())
                return redirect(url_for('admin.dashboard'))
            else:
                return '''
                <h2>Login Gagal</h2>
                <p>Username atau password salah</p>
                <a href="/auth/login">Coba lagi</a>
                '''
        
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login - TK RA SA'DIAH</title>
            <style>
                body { font-family: Arial; background: linear-gradient(135deg, #2e7d32, #4caf50); display: flex; justify-content: center; align-items: center; height: 100vh; }
                .login-box { background: white; padding: 40px; border-radius: 20px; width: 350px; text-align: center; }
                input, select { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
                button { width: 100%; padding: 10px; background: #2e7d32; color: white; border: none; border-radius: 5px; cursor: pointer; }
                h2 { color: #2e7d32; }
            </style>
        </head>
        <body>
            <div class="login-box">
                <h2>🏫 TK RA SA'DIAH</h2>
                <form method="POST">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <select name="role">
                        <option value="admin">Admin</option>
                        <option value="guru">Guru</option>
                        <option value="murid">Murid</option>
                    </select>
                    <button type="submit">Login</button>
                </form>
                <p style="margin-top: 20px; font-size: 12px;">Demo: admin/admin123</p>
            </div>
        </body>
        </html>
        '''
    
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
        return redirect('/auth/login')
    
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