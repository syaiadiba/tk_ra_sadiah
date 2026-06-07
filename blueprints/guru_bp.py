"""
Guru Blueprint for TK RA SA'DIAH - FULL VERSION (ALL ROUTES) - DENGAN PG8000
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
import bcrypt
import pg8000
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

guru_bp = Blueprint('guru', __name__, url_prefix='/guru')
logger = logging.getLogger(__name__)


def get_db_connection():
    """Mendapatkan koneksi database dari DATABASE_URL (Supabase) menggunakan pg8000"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        raise Exception("DATABASE_URL tidak ditemukan di environment!")
    
    # Parse URL menjadi komponen terpisah
    parsed = urlparse(database_url)
    
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port or 5432
    database = parsed.path.lstrip('/')
    
    print(f"🔍 Connecting to: {host}:{port} as {user}")
    
    # Koneksi dengan parameter terpisah
    return pg8000.connect(
        user=user,
        password=password,
        host=host,
        port=port,
        database=database
    )


def execute_query(conn, query, params=None, fetch_one=False, fetch_all=False):
    """Helper untuk eksekusi query dengan konversi ke dictionary"""
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    
    if fetch_one:
        result = cursor.fetchone()
        if result:
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, result))
        cursor.close()
        return result
    elif fetch_all:
        results = cursor.fetchall()
        if results:
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in results]
        cursor.close()
        return results
    else:
        conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        return rowcount


# ============================================
# CHECK ROLE
# ============================================
@guru_bp.before_request
@login_required
def check_role():
    if current_user.role != 'guru':
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'murid':
            return redirect(url_for('murid.dashboard'))
        flash('Akses ditolak! Anda bukan guru.', 'danger')
        return redirect(url_for('auth.login'))


# ============================================
# DASHBOARD
# ============================================
@guru_bp.route('/dashboard')
def dashboard():
    try:
        conn = get_db_connection()
        
        total_murid = execute_query(conn, "SELECT COUNT(*) as total FROM users WHERE role = 'murid'", fetch_one=True)
        total_murid = total_murid['total'] if total_murid else 0
        
        tugas_aktif = execute_query(conn, "SELECT COUNT(*) as total FROM tugas WHERE guru_id = %s", (current_user.id,), fetch_one=True)
        tugas_aktif = tugas_aktif['total'] if tugas_aktif else 0
        
        tugas_terbaru = execute_query(conn, "SELECT * FROM tugas WHERE guru_id = %s ORDER BY created_at DESC LIMIT 5", (current_user.id,), fetch_all=True) or []
        
        nilai_terbaru = execute_query(conn, """
            SELECT e.*, u.full_name as siswa_name 
            FROM e_rapor e 
            JOIN users u ON e.siswa_id = u.id 
            ORDER BY e.created_at DESC LIMIT 5
        """, fetch_all=True) or []
        
        pengumuman_terbaru = execute_query(conn, "SELECT * FROM pengumuman WHERE target_role IN ('semua', 'guru') ORDER BY created_at DESC LIMIT 3", fetch_all=True) or []
        
        conn.close()
        
        return render_template('guru/dashboard.html',
                             name=current_user.full_name or 'Guru',
                             email=getattr(current_user, 'email', ''),
                             mata_pelajaran=getattr(current_user, 'mata_pelajaran', '-'),
                             total_murid=total_murid,
                             tugas_aktif=tugas_aktif,
                             tugas_dikumpulkan=0,
                             pengumuman_aktif=len(pengumuman_terbaru),
                             tugas_terbaru=tugas_terbaru,
                             nilai_terbaru=nilai_terbaru,
                             pengumuman_terbaru=pengumuman_terbaru,
                             jadwal_hari_ini=[],
                             active_menu='dashboard')
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('Terjadi kesalahan pada dashboard', 'danger')
        return render_template('guru/dashboard.html', name=current_user.full_name or 'Guru', active_menu='dashboard')


# ============================================
# TUGAS (CRUD)
# ============================================
@guru_bp.route('/tugas')
def tugas():
    try:
        conn = get_db_connection()
        tugas_list = execute_query(conn, "SELECT * FROM tugas WHERE guru_id = %s ORDER BY created_at DESC", (current_user.id,), fetch_all=True) or []
        total_murid = execute_query(conn, "SELECT COUNT(*) as total FROM users WHERE role = 'murid'", fetch_one=True)
        total_murid = total_murid['total'] if total_murid else 0
        conn.close()
        return render_template('guru/tugas.html', tugas_list=tugas_list, total_murid=total_murid, active_menu='tugas')
    except Exception as e:
        logger.error(f"Tugas error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


@guru_bp.route('/buat-tugas', methods=['GET', 'POST'])
def buat_tugas():
    if request.method == 'POST':
        judul = request.form.get('judul')
        mapel = request.form.get('mapel')
        deskripsi = request.form.get('deskripsi')
        deadline = request.form.get('deadline')
        kelas = request.form.get('kelas')
        
        if not judul or not deskripsi:
            flash('Judul dan deskripsi harus diisi!', 'danger')
            return render_template('guru/buat_tugas.html', active_menu='tugas')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tugas (guru_id, judul, mapel, deskripsi, deadline, kelas, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (current_user.id, judul, mapel, deskripsi, deadline, kelas, datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            flash('✅ Tugas berhasil dibuat!', 'success')
            return redirect(url_for('guru.tugas'))
        except Exception as e:
            logger.error(f"Buat tugas error: {str(e)}")
            flash('Terjadi kesalahan', 'danger')
    
    return render_template('guru/buat_tugas.html', active_menu='tugas')


@guru_bp.route('/kirim-tugas/<int:id>')
def kirim_tugas(id):
    try:
        conn = get_db_connection()
        tugas = execute_query(conn, "SELECT * FROM tugas WHERE id = %s AND guru_id = %s", (id, current_user.id), fetch_one=True)
        
        if not tugas:
            flash('Tugas tidak ditemukan!', 'danger')
            conn.close()
            return redirect(url_for('guru.tugas'))
        
        kiriman_list = execute_query(conn, """
            SELECT k.*, u.full_name as siswa_name, u.nis, u.kelas
            FROM kiriman_tugas k
            JOIN users u ON k.siswa_id = u.id
            WHERE k.tugas_id = %s
            ORDER BY k.created_at DESC
        """, (id,), fetch_all=True) or []
        
        conn.close()
        
        return render_template('guru/kirim_tugas.html', 
                             tugas=tugas, 
                             kiriman_list=kiriman_list,
                             active_menu='tugas')
    except Exception as e:
        logger.error(f"Kirim tugas error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.tugas'))


# ============================================
# DAFTAR MURID
# ============================================
@guru_bp.route('/daftar-murid')
def daftar_murid():
    """Menampilkan daftar murid untuk guru"""
    try:
        conn = get_db_connection()
        
        # Ambil semua murid
        murid_list = execute_query(conn, """
            SELECT id, full_name, nis, nisn, kelas, jenis_kelamin, 
                   email, phone, address, tanggal_lahir
            FROM users 
            WHERE role = 'murid' 
            ORDER BY kelas, full_name
        """, fetch_all=True) or []
        
        conn.close()
        
        return render_template('guru/daftar_murid.html',
                             murid=murid_list,
                             total_murid=len(murid_list),
                             active_menu='daftar_murid')
    except Exception as e:
        logger.error(f"Daftar murid error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


# ============================================
# DETAIL MURID
# ============================================
@guru_bp.route('/murid/<int:id>')
def detail_murid(id):
    """Menampilkan detail murid"""
    try:
        conn = get_db_connection()
        
        murid = execute_query(conn, """
            SELECT id, full_name, nis, nisn, kelas, jenis_kelamin, 
                   email, phone, address, tanggal_lahir, created_at
            FROM users 
            WHERE id = %s AND role = 'murid'
        """, (id,), fetch_one=True)
        
        if not murid:
            flash('Murid tidak ditemukan!', 'danger')
            conn.close()
            return redirect(url_for('guru.daftar_murid'))
        
        # Ambil nilai/rapor murid
        nilai = execute_query(conn, """
            SELECT * FROM e_rapor 
            WHERE siswa_id = %s 
            ORDER BY created_at DESC
        """, (id,), fetch_all=True) or []
        
        # Ambil tugas yang dikumpulkan
        tugas = execute_query(conn, """
            SELECT k.*, t.judul as tugas_judul, t.mapel
            FROM kiriman_tugas k
            JOIN tugas t ON k.tugas_id = t.id
            WHERE k.siswa_id = %s
            ORDER BY k.created_at DESC
        """, (id,), fetch_all=True) or []
        
        conn.close()
        
        return render_template('guru/detail_murid.html',
                             murid=murid,
                             nilai=nilai,
                             tugas=tugas,
                             active_menu='daftar_murid')
    except Exception as e:
        logger.error(f"Detail murid error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.daftar_murid'))


# ============================================
# PENGUMUMAN
# ============================================
@guru_bp.route('/pengumuman')
def pengumuman():
    """Halaman pengumuman untuk guru"""
    try:
        conn = get_db_connection()
        pengumuman_list = execute_query(conn, "SELECT * FROM pengumuman WHERE target_role IN ('semua', 'guru') ORDER BY created_at DESC", fetch_all=True) or []
        conn.close()
        return render_template('guru/pengumuman.html', 
                             pengumuman=pengumuman_list,
                             active_menu='pengumuman')
    except Exception as e:
        logger.error(f"Pengumuman error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


# ============================================
# NILAI / RAPOR
# ============================================
@guru_bp.route('/nilai')
def nilai():
    """Halaman nilai/rapor untuk guru"""
    try:
        conn = get_db_connection()
        nilai_list = execute_query(conn, """
            SELECT e.*, u.full_name as siswa_name, u.nis, u.kelas 
            FROM e_rapor e 
            JOIN users u ON e.siswa_id = u.id 
            ORDER BY e.created_at DESC
        """, fetch_all=True) or []
        conn.close()
        return render_template('guru/nilai.html', 
                             nilai=nilai_list,
                             active_menu='nilai')
    except Exception as e:
        logger.error(f"Nilai error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


# ============================================
# JADWAL MENGAJAR
# ============================================
@guru_bp.route('/jadwal-mengajar')
def jadwal_mengajar():
    """Halaman jadwal mengajar untuk guru"""
    try:
        mata_pelajaran = getattr(current_user, 'mata_pelajaran', 'Matematika')
        
        # Data jadwal contoh (hardcoded untuk sementara)
        jadwal_list = [
            {'hari': 'Senin', 'jam': '07:30 - 09:00', 'kelas': 'Kelas A', 'ruang': 'Ruang 101'},
            {'hari': 'Senin', 'jam': '09:15 - 10:45', 'kelas': 'Kelas B', 'ruang': 'Ruang 102'},
            {'hari': 'Selasa', 'jam': '07:30 - 09:00', 'kelas': 'Kelas C', 'ruang': 'Ruang 103'},
            {'hari': 'Rabu', 'jam': '10:00 - 11:30', 'kelas': 'Kelas A', 'ruang': 'Ruang 101'},
            {'hari': 'Kamis', 'jam': '07:30 - 09:00', 'kelas': 'Kelas B', 'ruang': 'Ruang 102'},
            {'hari': 'Jumat', 'jam': '08:00 - 09:30', 'kelas': 'Kelas C', 'ruang': 'Ruang 103'},
        ]
        
        return render_template('guru/jadwal_mengajar.html',
                             jadwal=jadwal_list,
                             mata_pelajaran=mata_pelajaran,
                             active_menu='jadwal')
    except Exception as e:
        logger.error(f"Jadwal mengajar error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


# ============================================
# PROFIL GURU
# ============================================
@guru_bp.route('/profil', methods=['GET', 'POST'])
def profil():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        nip = request.form.get('nip')
        mata_pelajaran = request.form.get('mata_pelajaran')
        jenis_kelamin = request.form.get('jenis_kelamin')
        address = request.form.get('address')
        password = request.form.get('password')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if password and len(password) >= 4:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("""
                    UPDATE users SET full_name=%s, email=%s, phone=%s, nip=%s, mata_pelajaran=%s,
                                   jenis_kelamin=%s, address=%s, password_hash=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, email, phone, nip, mata_pelajaran, jenis_kelamin, address, hashed, datetime.now(), current_user.id))
            else:
                cursor.execute("""
                    UPDATE users SET full_name=%s, email=%s, phone=%s, nip=%s, mata_pelajaran=%s,
                                   jenis_kelamin=%s, address=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, email, phone, nip, mata_pelajaran, jenis_kelamin, address, datetime.now(), current_user.id))
            
            conn.commit()
            cursor.close()
            conn.close()
            flash('✅ Profil berhasil diupdate!', 'success')
            return redirect(url_for('guru.profil'))
        except Exception as e:
            logger.error(f"Update profil error: {str(e)}")
            flash('Terjadi kesalahan', 'danger')
    
    return render_template('guru/profil.html',
                         name=current_user.full_name,
                         email=getattr(current_user, 'email', ''),
                         phone=getattr(current_user, 'phone', ''),
                         nip=getattr(current_user, 'nip', ''),
                         mata_pelajaran=getattr(current_user, 'mata_pelajaran', ''),
                         jenis_kelamin=getattr(current_user, 'jenis_kelamin', ''),
                         address=getattr(current_user, 'address', ''),
                         active_menu='profil')


# ============================================
# PENGATURAN
# ============================================
@guru_bp.route('/pengaturan')
def pengaturan():
    return render_template('guru/pengaturan.html', active_menu='pengaturan')


# ============================================
# INDEX / ROOT REDIRECT
# ============================================
@guru_bp.route('/')
def index():
    """Redirect ke dashboard guru"""
    return redirect(url_for('guru.dashboard'))


__all__ = ['guru_bp']