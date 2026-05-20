"""
Admin Blueprint for TK RA SA'DIAH
Mengelola data siswa, guru, dan pembayaran
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
import bcrypt
import logging
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)


@admin_bp.before_request
@login_required
def check_role():
    if current_user.role != 'admin':
        flash('Akses ditolak! Anda bukan admin.', 'danger')
        return redirect(url_for('auth.login'))


def get_db_connection():
    """Mendapatkan koneksi database"""
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'tk_ra_sadiah'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432')
    )


# ============================================
# DASHBOARD ADMIN
# ============================================
@admin_bp.route('/dashboard')
def dashboard():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT COUNT(*) as total FROM users WHERE role = 'murid'")
        total_siswa = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM users WHERE role = 'guru'")
        total_guru = cur.fetchone()['total']
        
        cur.execute("SELECT COUNT(*) as total FROM pembelajaran")
        total_pembelajaran = cur.fetchone()['total']
        
        cur.close()
        conn.close()
        
        return render_template('admin/dashboard.html',
                             name=current_user.full_name,
                             total_siswa=total_siswa,
                             total_guru=total_guru,
                             total_pembelajaran=total_pembelajaran,
                             now=datetime.now())
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


# ============================================
# KELOLA SISWA (READ)
# ============================================
@admin_bp.route('/siswa')
def kelola_siswa():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        search = request.args.get('search', '')
        
        if search:
            cur.execute("""
                SELECT * FROM users 
                WHERE role = 'murid' 
                AND (username ILIKE %s OR full_name ILIKE %s OR email ILIKE %s)
                ORDER BY id
            """, (f'%{search}%', f'%{search}%', f'%{search}%'))
        else:
            cur.execute("SELECT * FROM users WHERE role = 'murid' ORDER BY id")
        
        siswa = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template('admin/kelola_siswa.html', siswa=siswa, search_query=search)
        
    except Exception as e:
        logger.error(f"Kelola siswa error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


# ============================================
# TAMBAH SISWA (CREATE)
# ============================================
@admin_bp.route('/siswa/tambah', methods=['GET', 'POST'])
def tambah_siswa():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        
        # Validasi
        errors = []
        if not username:
            errors.append('Username harus diisi')
        if not full_name:
            errors.append('Nama lengkap harus diisi')
        if not password:
            errors.append('Password harus diisi')
        elif len(password) < 4:
            errors.append('Password minimal 4 karakter')
        elif password != confirm_password:
            errors.append('Password dan konfirmasi tidak sama')
        
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('admin/tambah_siswa.html')
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Cek username sudah ada
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                flash(f'Username "{username}" sudah digunakan!', 'danger')
                cur.close()
                conn.close()
                return render_template('admin/tambah_siswa.html')
            
            # Cek email sudah ada (jika diisi)
            if email:
                cur.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cur.fetchone():
                    flash(f'Email "{email}" sudah digunakan!', 'danger')
                    cur.close()
                    conn.close()
                    return render_template('admin/tambah_siswa.html')
            
            # Hash password
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Insert ke database
            cur.execute("""
                INSERT INTO users (username, password_hash, role, full_name, email, phone, address, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (username, hashed, 'murid', full_name, email, phone, address, datetime.now(), datetime.now()))
            
            conn.commit()
            new_id = cur.fetchone()[0]
            
            cur.close()
            conn.close()
            
            flash(f'✅ Siswa "{full_name}" berhasil ditambahkan! Username: {username}, Password: {password}', 'success')
            return redirect(url_for('admin.kelola_siswa'))
            
        except Exception as e:
            logger.error(f"Tambah siswa error: {str(e)}")
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return render_template('admin/tambah_siswa.html')


# ============================================
# EDIT SISWA (UPDATE)
# ============================================
@admin_bp.route('/siswa/edit/<int:id>', methods=['GET', 'POST'])
def edit_siswa(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'POST':
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            password = request.form.get('password')
            
            if password:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute("""
                    UPDATE users 
                    SET full_name = %s, email = %s, phone = %s, address = %s, 
                        password_hash = %s, updated_at = %s
                    WHERE id = %s
                """, (full_name, email, phone, address, hashed, datetime.now(), id))
            else:
                cur.execute("""
                    UPDATE users 
                    SET full_name = %s, email = %s, phone = %s, address = %s, updated_at = %s
                    WHERE id = %s
                """, (full_name, email, phone, address, datetime.now(), id))
            
            conn.commit()
            flash('✅ Data siswa berhasil diupdate!', 'success')
            cur.close()
            conn.close()
            return redirect(url_for('admin.kelola_siswa'))
        
        # GET request
        cur.execute("SELECT * FROM users WHERE id = %s AND role = 'murid'", (id,))
        siswa = cur.fetchone()
        cur.close()
        conn.close()
        
        if not siswa:
            flash('Siswa tidak ditemukan!', 'danger')
            return redirect(url_for('admin.kelola_siswa'))
        
        return render_template('admin/edit_siswa.html', siswa=siswa)
        
    except Exception as e:
        logger.error(f"Edit siswa error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.kelola_siswa'))


# ============================================
# HAPUS SISWA (DELETE)
# ============================================
@admin_bp.route('/siswa/hapus/<int:id>')
def hapus_siswa(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s AND role = 'murid'", (id,))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('✅ Siswa berhasil dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus siswa error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    
    return redirect(url_for('admin.kelola_siswa'))


# ============================================
# KELOLA GURU (CRUD)
# ============================================
@admin_bp.route('/guru')
def kelola_guru():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE role = 'guru' ORDER BY id")
        guru = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template('admin/kelola_guru.html', guru=guru)
    except Exception as e:
        logger.error(f"Kelola guru error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/guru/tambah', methods=['GET', 'POST'])
def tambah_guru():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        email = request.form.get('email', '')
        
        if not username or not full_name or not password:
            flash('Semua field harus diisi!', 'danger')
            return render_template('admin/tambah_guru.html')
        
        if len(password) < 4:
            flash('Password minimal 4 karakter!', 'danger')
            return render_template('admin/tambah_guru.html')
        
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Cek username
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                flash(f'Username "{username}" sudah digunakan!', 'danger')
                cur.close()
                conn.close()
                return render_template('admin/tambah_guru.html')
            
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cur.execute("""
                INSERT INTO users (username, password_hash, role, full_name, email, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (username, hashed, 'guru', full_name, email, datetime.now(), datetime.now()))
            conn.commit()
            
            cur.close()
            conn.close()
            
            flash(f'✅ Guru "{full_name}" berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.kelola_guru'))
            
        except Exception as e:
            logger.error(f"Tambah guru error: {str(e)}")
            flash('Terjadi kesalahan', 'danger')
    
    return render_template('admin/tambah_guru.html')


@admin_bp.route('/guru/edit/<int:id>', methods=['GET', 'POST'])
def edit_guru(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'POST':
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if password:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute("""
                    UPDATE users SET full_name = %s, email = %s, password_hash = %s, updated_at = %s
                    WHERE id = %s
                """, (full_name, email, hashed, datetime.now(), id))
            else:
                cur.execute("""
                    UPDATE users SET full_name = %s, email = %s, updated_at = %s
                    WHERE id = %s
                """, (full_name, email, datetime.now(), id))
            
            conn.commit()
            flash('✅ Data guru berhasil diupdate!', 'success')
            cur.close()
            conn.close()
            return redirect(url_for('admin.kelola_guru'))
        
        cur.execute("SELECT * FROM users WHERE id = %s AND role = 'guru'", (id,))
        guru = cur.fetchone()
        cur.close()
        conn.close()
        
        if not guru:
            flash('Guru tidak ditemukan!', 'danger')
            return redirect(url_for('admin.kelola_guru'))
        
        return render_template('admin/edit_guru.html', guru=guru)
        
    except Exception as e:
        logger.error(f"Edit guru error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.kelola_guru'))


@admin_bp.route('/guru/hapus/<int:id>')
def hapus_guru(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id = %s AND role = 'guru'", (id,))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('✅ Guru berhasil dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus guru error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    
    return redirect(url_for('admin.kelola_guru'))


# ============================================
# KELOLA PEMBAYARAN
# ============================================
@admin_bp.route('/pembayaran')
def kelola_pembayaran():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT p.*, u.username as murid_name, u.full_name as murid_full_name
            FROM pembayaran p
            JOIN users u ON p.murid_id = u.id
            ORDER BY p.tahun DESC, p.bulan DESC
        """)
        pembayaran = cur.fetchall()
        
        cur.execute("SELECT id, full_name, username FROM users WHERE role = 'murid' ORDER BY full_name")
        siswa = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return render_template('admin/kelola_pembayaran.html', pembayaran=pembayaran, siswa=siswa)
    except Exception as e:
        logger.error(f"Kelola pembayaran error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/pembayaran/tambah', methods=['POST'])
def tambah_pembayaran():
    try:
        murid_id = request.form.get('murid_id')
        bulan = request.form.get('bulan')
        tahun = request.form.get('tahun')
        nominal = request.form.get('nominal')
        status = request.form.get('status', 'belum_bayar')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pembayaran (murid_id, bulan, tahun, nominal, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (murid_id, bulan, tahun, nominal, status, datetime.now(), datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('✅ Pembayaran berhasil ditambahkan!', 'success')
    except Exception as e:
        logger.error(f"Tambah pembayaran error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    
    return redirect(url_for('admin.kelola_pembayaran'))


@admin_bp.route('/pembayaran/edit/<int:id>', methods=['POST'])
def edit_pembayaran(id):
    try:
        status = request.form.get('status')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE pembayaran SET status = %s, updated_at = %s WHERE id = %s", (status, datetime.now(), id))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('✅ Status pembayaran diupdate!', 'success')
    except Exception as e:
        logger.error(f"Edit pembayaran error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    
    return redirect(url_for('admin.kelola_pembayaran'))


@admin_bp.route('/pembayaran/hapus/<int:id>')
def hapus_pembayaran(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM pembayaran WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        
        flash('✅ Pembayaran dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus pembayaran error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    
    return redirect(url_for('admin.kelola_pembayaran'))