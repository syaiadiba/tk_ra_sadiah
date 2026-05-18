# blueprints/__init__.py
# File ini membuat folder 'blueprints' menjadi Python package

from .auth_bp import auth_bp
from .murid_bp import murid_bp
from .guru_bp import guru_bp
from .admin_bp import admin_bp
from .umum_bp import umum_bp

__all__ = [
    'auth_bp',
    'murid_bp',
    'guru_bp',
    'admin_bp',
    'umum_bp'
]