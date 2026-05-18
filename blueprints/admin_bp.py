"""
Admin Blueprint for TK RA SA'DIAH
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models.user_model import User
from models.pembayaran_model import Pembayaran
import logging

# ============================================
# MEMBUAT BLUEPRINT
# ============================================
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

logger = logging.getLogger(__name__)


@admin_bp.before_request
@login_required
def check_role():
    """Check if user has admin role"""
    if current_user.role != 'admin':
        flash('Akses ditolak! Anda bukan admin.', 'danger')
        return redirect(url_for('auth.login'))


@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard"""
    try:
        user_model = User()
        pembayaran_model = Pembayaran()
        
        siswa = user_model.get_by_role('murid') or []
        guru = user_model.get_by_role('guru') or []
        pembayaran = pembayaran_model.get_all_with_murid() or []
        
        return render_template('admin/dashboard.html',
                             total_siswa=len(siswa),
                             total_guru=len(guru),
                             siswa=siswa,
                             pembayaran=pembayaran,
                             name=current_user.full_name)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


__all__ = ['admin_bp']