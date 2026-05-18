"""
Murid Blueprint for TK RA SA'DIAH
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from models.pembelajaran_model import Pembelajaran
from models.tanggapan_model import Tanggapan
from models.pembayaran_model import Pembayaran
import logging

# ============================================
# MEMBUAT BLUEPRINT
# ============================================
murid_bp = Blueprint('murid', __name__, url_prefix='/murid')

logger = logging.getLogger(__name__)


@murid_bp.before_request
@login_required
def check_role():
    """Check if user has murid role"""
    if current_user.role != 'murid':
        flash('Akses ditolak! Anda bukan murid.', 'danger')
        return redirect(url_for('auth.login'))


@murid_bp.route('/dashboard')
def dashboard():
    """Student dashboard"""
    try:
        pembelajaran_model = Pembelajaran()
        tanggapan_model = Tanggapan()
        
        semua_pembelajaran = pembelajaran_model.get_all_with_guru()
        tanggapan_saya = tanggapan_model.get_by_murid(current_user.id)
        responded_ids = [t['pembelajaran_id'] for t in tanggapan_saya] if tanggapan_saya else []
        
        visi_misi = {
            'visi': "Membentuk generasi yang beriman, bertaqwa, cerdas, terampil, dan berakhlak mulia",
            'misi': [
                "Menyelenggarakan pendidikan anak usia dini yang berkualitas",
                "Mengembangkan potensi anak secara optimal",
                "Menanamkan nilai-nilai keislaman dalam kehidupan sehari-hari"
            ]
        }
        
        return render_template('murid/dashboard.html', 
                             visi_misi=visi_misi,
                             pembelajaran=semua_pembelajaran,
                             tanggapan_saya=responded_ids,
                             name=current_user.full_name)
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('murid.dashboard'))


@murid_bp.route('/keuangan')
def keuangan():
    """Student finance page"""
    try:
        pembayaran_model = Pembayaran()
        pembayaran = pembayaran_model.get_by_murid(current_user.id)
        
        total_tagihan = sum(p['nominal'] for p in pembayaran)
        total_dibayar = sum(p['nominal'] for p in pembayaran if p['status'] == 'lunas')
        
        return render_template('murid/keuangan.html',
                             pembayaran=pembayaran,
                             total_tagihan=total_tagihan,
                             total_dibayar=total_dibayar,
                             sisa=total_tagihan - total_dibayar,
                             name=current_user.full_name)
    except Exception as e:
        logger.error(f"Keuangan error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('murid.dashboard'))


__all__ = ['murid_bp']