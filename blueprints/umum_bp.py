"""
Umum Blueprint for TK RA SA'DIAH
"""

from flask import Blueprint, render_template

# ============================================
# MEMBUAT BLUEPRINT
# ============================================
umum_bp = Blueprint('umum', __name__)


@umum_bp.route('/profil')
def profil():
    """School profile page"""
    return render_template('profil.html')


@umum_bp.route('/acara')
def acara():
    """Upcoming events page"""
    return render_template('acara.html')


@umum_bp.route('/pemberitahuan')
def pemberitahuan():
    """Notifications page"""
    return render_template('pemberitahuan.html')


__all__ = ['umum_bp']