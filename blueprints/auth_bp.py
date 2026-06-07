"""
Authentication Blueprint for TK RA SA'DIAH
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user_model import User
import bcrypt
import logging
from datetime import datetime

# ============================================
# MEMBUAT BLUEPRINT - INI YANG PALING PENTING!
# ============================================
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

logger = logging.getLogger(__name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Halaman login"""
    
    # Jika sudah login, redirect ke dashboard
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'guru':
            return redirect(url_for('guru.dashboard'))
        elif current_user.role == 'murid':
            return redirect(url_for('murid.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Debug
        print(f"Login attempt: {username}, {role}")
        
        try:
            # Authentikasi user
            user = User.authenticate(username, password)
            
            if user and user.role == role:
                login_user(user)
                session['role'] = user.role
                session['user_id'] = user.id
                flash(f'Selamat datang, {user.full_name or user.username}!', 'success')
                
                # Redirect berdasarkan role
                if user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                elif user.role == 'guru':
                    # Pastikan redirect ke endpoint yang benar
                    print(f"Redirecting guru to dashboard. User ID: {user.id}")
                    return redirect(url_for('guru.dashboard'))
                elif user.role == 'murid':
                    return redirect(url_for('murid.dashboard'))
                else:
                    flash('Role tidak dikenal!', 'danger')
                    return redirect(url_for('auth.login'))
            else:
                if user:
                    flash(f'Role tidak sesuai! Anda adalah {user.role}, bukan {role}', 'danger')
                else:
                    flash('Username atau password salah!', 'danger')
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            import traceback
            traceback.print_exc()
            flash('Terjadi kesalahan sistem', 'danger')
    
    return render_template('login.html')


@auth_bp.route('/lupa-password', methods=['GET', 'POST'])
def lupa_password():
    """Halaman lupa password"""
    if request.method == 'POST':
        username = request.form.get('username')
        flash(f'Link reset password akan dikirim ke email {username} (Demo)', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('lupa_password.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))


# Ekspor blueprint
__all__ = ['auth_bp']