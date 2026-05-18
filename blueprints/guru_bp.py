"""
Guru Blueprint for TK RA SA'DIAH
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models.pembelajaran_model import Pembelajaran
from models.tanggapan_model import Tanggapan
import logging

# ============================================
# MEMBUAT BLUEPRINT
# ============================================
guru_bp = Blueprint('guru', __name__, url_prefix='/guru')

logger = logging.getLogger(__name__)


@guru_bp.before_request
@login_required
def check_role():
    """Check if user has guru role"""
    if current_user.role != 'guru':
        flash('Akses ditolak! Anda bukan guru.', 'danger')
        return redirect(url_for('auth.login'))


@guru_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """Teacher dashboard"""
    try:
        pembelajaran_model = Pembelajaran()
        tanggapan_model = Tanggapan()
        
        if request.method == 'POST':
            judul = request.form.get('judul')
            konten = request.form.get('konten')
            
            if judul and konten:
                data = {
                    'guru_id': current_user.id,
                    'judul': judul.strip(),
                    'konten': konten.strip()
                }
                pembelajaran_model.insert(data)
                flash('✅ Pembelajaran berhasil diposting!', 'success')
                return redirect(url_for('guru.dashboard'))
            else:
                flash('Judul dan konten harus diisi!', 'danger')
        
        pembelajaran_saya = pembelajaran_model.get_by_guru(current_user.id)
        
        pembelajaran_dengan_tanggapan = []
        for p in pembelajaran_saya:
            tanggapan = tanggapan_model.get_by_pembelajaran(p['id'])
            pembelajaran_dengan_tanggapan.append({
                'pembelajaran': p,
                'tanggapan': tanggapan if tanggapan else [],
                'jumlah_tanggapan': len(tanggapan) if tanggapan else 0
            })
        
        return render_template('guru/dashboard.html',
                             pembelajaran=pembelajaran_dengan_tanggapan,
                             name=current_user.full_name)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


__all__ = ['guru_bp']