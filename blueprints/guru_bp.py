"""
Guru Blueprint for TK RA SA'DIAH - FULL VERSION (ALL ROUTES)
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

guru_bp = Blueprint('guru', __name__, url_prefix='/guru')
logger = logging.getLogger(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        database=os.getenv('DB_NAME', 'tk_ra_sadiah'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', ''),
        port=os.getenv('DB_PORT', '5432')
    )


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
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT COUNT(*) as total FROM users WHERE role = 'murid'")
        total_murid = cur.fetchone()['total'] if cur.fetchone() else 0
        
        cur.execute("SELECT COUNT(*) as total FROM tugas WHERE guru_id = %s", (current_user.id,))
        tugas_aktif = cur.fetchone()['total'] if cur.fetchone() else 0
        
        cur.execute("SELECT * FROM tugas WHERE guru_id = %s ORDER BY created_at DESC LIMIT 5", (current_user.id,))
        tugas_terbaru = cur.fetchall() or []
        
        cur.execute("""
            SELECT e.*, u.full_name as siswa_name 
            FROM e_rapor e 
            JOIN users u ON e.siswa_id = u.id 
            ORDER BY e.created_at DESC LIMIT 5
        """)
        nilai_terbaru = cur.fetchall() or []
        
        cur.execute("SELECT * FROM pengumuman ORDER BY created_at DESC LIMIT 3")
        pengumuman_terbaru = cur.fetchall() or []
        
        cur.close()
        conn.close()
        
        return render_template('guru/dashboard.html',
                             name=current_user.full_name or 'Guru',
                             email=current_user.email or '',
                             mata_pelajaran=current_user.mata_pelajaran or '-',
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
        return render_template('guru/dashboard.html', name=current_user.full_name or 'Guru', active_menu='dashboard')


# ============================================
# TUGAS (CRUD)
# ============================================
@guru_bp.route('/tugas')
def tugas():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM tugas WHERE guru_id = %s ORDER BY created_at DESC", (current_user.id,))
        tugas_list = cur.fetchall() or []
        cur.execute("SELECT COUNT(*) as total FROM users WHERE role = 'murid'")
        total_murid = cur.fetchone()['total'] if cur.fetchone() else 0
        cur.close()
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
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO tugas (guru_id, judul, mapel, deskripsi, deadline, kelas, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (current_user.id, judul, mapel, deskripsi, deadline, kelas, datetime.now()))
            conn.commit()
            cur.close()
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
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT * FROM tugas WHERE id = %s AND guru_id = %s", (id, current_user.id))
        tugas = cur.fetchone()
        
        if not tugas:
            flash('Tugas tidak ditemukan!', 'danger')
            return redirect(url_for('guru.tugas'))
        
        cur.execute("""
            SELECT k.*, u.full_name as siswa_name, u.nis, u.kelas
            FROM kiriman_tugas k
            JOIN users u ON k.siswa_id = u.id
            WHERE k.tugas_id = %s
            ORDER BY k.created_at DESC
        """, (id,))
        kiriman_list = cur.fetchall() or []
        
        cur.close()
        conn.close()
        
        return render_template('guru/kirim_tugas.html', 
                             tugas=tugas, 
                             kiriman_list=kiriman_list,
                             active_menu='tugas')
    except Exception as e:
        logger.error(f"Kirim tugas error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.tugas'))


@guru_bp.route('/edit-tugas/<int:id>', methods=['GET', 'POST'])
def edit_tugas(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'POST':
            judul = request.form.get('judul')
            mapel = request.form.get('mapel')
            deskripsi = request.form.get('deskripsi')
            deadline = request.form.get('deadline')
            kelas = request.form.get('kelas')
            
            cur.execute("""
                UPDATE tugas SET judul=%s, mapel=%s, deskripsi=%s, deadline=%s, kelas=%s, updated_at=%s
                WHERE id=%s AND guru_id=%s
            """, (judul, mapel, deskripsi, deadline, kelas, datetime.now(), id, current_user.id))
            conn.commit()
            flash('✅ Tugas berhasil diupdate!', 'success')
            cur.close()
            conn.close()
            return redirect(url_for('guru.tugas'))
        
        cur.execute("SELECT * FROM tugas WHERE id=%s AND guru_id=%s", (id, current_user.id))
        tugas = cur.fetchone()
        cur.close()
        conn.close()
        
        if not tugas:
            flash('Tugas tidak ditemukan!', 'danger')
            return redirect(url_for('guru.tugas'))
        
        return render_template('guru/edit_tugas.html', tugas=tugas, active_menu='tugas')
    except Exception as e:
        logger.error(f"Edit tugas error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.tugas'))


@guru_bp.route('/hapus-tugas/<int:id>')
def hapus_tugas(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tugas WHERE id=%s AND guru_id=%s", (id, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        flash('✅ Tugas berhasil dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus tugas error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('guru.tugas'))


# ============================================
# PENGUMUMAN (CRUD)
# ============================================
@guru_bp.route('/pengumuman')
def pengumuman():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM pengumuman ORDER BY created_at DESC")
        pengumuman_list = cur.fetchall() or []
        cur.close()
        conn.close()
        return render_template('guru/pengumuman.html', pengumuman=pengumuman_list, active_menu='pengumuman')
    except Exception as e:
        logger.error(f"Pengumuman error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


@guru_bp.route('/tambah-pengumuman', methods=['POST'])
def tambah_pengumuman():
    try:
        judul = request.form.get('judul')
        isi = request.form.get('isi')
        target_role = request.form.get('target_role', 'semua')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO pengumuman (admin_id, judul, isi, target_role, created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (current_user.id, judul, isi, target_role, datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        flash('✅ Pengumuman berhasil ditambahkan!', 'success')
    except Exception as e:
        logger.error(f"Tambah pengumuman error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('guru.pengumuman'))


@guru_bp.route('/hapus-pengumuman/<int:id>')
def hapus_pengumuman(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM pengumuman WHERE id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('✅ Pengumuman berhasil dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus pengumuman error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('guru.pengumuman'))


# ============================================
# DAFTAR MURID (CRUD)
# ============================================
@guru_bp.route('/daftar-murid')
def daftar_murid():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE role = 'murid' ORDER BY full_name")
        murid_list = cur.fetchall() or []
        cur.close()
        conn.close()
        return render_template('guru/daftar_murid.html', murid_list=murid_list, active_menu='daftar_murid')
    except Exception as e:
        logger.error(f"Daftar murid error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


@guru_bp.route('/tambah-murid', methods=['GET', 'POST'])
def tambah_murid():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        nis = request.form.get('nis')
        kelas = request.form.get('kelas')
        email = request.form.get('email', '')
        
        if not username or not full_name or not password:
            flash('Username, Nama, dan Password harus diisi!', 'danger')
            return render_template('guru/tambah_murid.html', active_menu='daftar_murid')
        
        try:
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (username, password_hash, role, full_name, nis, kelas, email, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (username, hashed, 'murid', full_name, nis, kelas, email, datetime.now()))
            conn.commit()
            cur.close()
            conn.close()
            flash('✅ Murid berhasil ditambahkan!', 'success')
            return redirect(url_for('guru.daftar_murid'))
        except Exception as e:
            logger.error(f"Tambah murid error: {str(e)}")
            flash('Terjadi kesalahan', 'danger')
    
    return render_template('guru/tambah_murid.html', active_menu='daftar_murid')


@guru_bp.route('/edit-murid/<int:id>', methods=['GET', 'POST'])
def edit_murid(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if request.method == 'POST':
            full_name = request.form.get('full_name')
            nis = request.form.get('nis')
            kelas = request.form.get('kelas')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if password:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute("""
                    UPDATE users SET full_name=%s, nis=%s, kelas=%s, email=%s, password_hash=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, nis, kelas, email, hashed, datetime.now(), id))
            else:
                cur.execute("""
                    UPDATE users SET full_name=%s, nis=%s, kelas=%s, email=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, nis, kelas, email, datetime.now(), id))
            conn.commit()
            flash('✅ Data murid berhasil diupdate!', 'success')
            cur.close()
            conn.close()
            return redirect(url_for('guru.daftar_murid'))
        
        cur.execute("SELECT * FROM users WHERE id=%s AND role='murid'", (id,))
        murid = cur.fetchone()
        cur.close()
        conn.close()
        
        if not murid:
            flash('Murid tidak ditemukan!', 'danger')
            return redirect(url_for('guru.daftar_murid'))
        
        return render_template('guru/edit_murid.html', murid=murid, active_menu='daftar_murid')
    except Exception as e:
        logger.error(f"Edit murid error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.daftar_murid'))


@guru_bp.route('/hapus-murid/<int:id>')
def hapus_murid(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id=%s AND role='murid'", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('✅ Murid berhasil dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus murid error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('guru.daftar_murid'))


# ============================================
# JADWAL MENGAJAR (CRUD)
# ============================================
@guru_bp.route('/jadwal-mengajar')
def jadwal_mengajar():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM jadwal WHERE guru_id = %s ORDER BY hari, jam_mulai", (current_user.id,))
        jadwal_list = cur.fetchall() or []
        cur.close()
        conn.close()
        return render_template('guru/jadwal_mengajar.html', jadwal_list=jadwal_list, active_menu='jadwal')
    except Exception as e:
        logger.error(f"Jadwal mengajar error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


# ============================================
# NILAI & E-RAPOR (CRUD)
# ============================================
@guru_bp.route('/nilai')
def nilai():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT e.*, u.full_name as siswa_name, u.kelas
            FROM e_rapor e
            JOIN users u ON e.siswa_id = u.id
            ORDER BY e.created_at DESC
        """)
        nilai_list = cur.fetchall() or []
        cur.execute("SELECT id, full_name, kelas FROM users WHERE role = 'murid' ORDER BY full_name")
        murid_list = cur.fetchall() or []
        cur.close()
        conn.close()
        return render_template('guru/nilai.html', nilai_list=nilai_list, murid_list=murid_list, active_menu='nilai')
    except Exception as e:
        logger.error(f"Nilai error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


@guru_bp.route('/tambah-nilai', methods=['POST'])
def tambah_nilai():
    try:
        siswa_id = request.form.get('siswa_id')
        mapel = request.form.get('mapel')
        nilai = request.form.get('nilai')
        predikat = request.form.get('predikat')
        semester = request.form.get('semester')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO e_rapor (siswa_id, mapel, nilai, predikat, semester, tahun_ajaran, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (siswa_id, mapel, nilai, predikat, semester, '2024/2025', datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        flash('✅ Nilai berhasil ditambahkan!', 'success')
    except Exception as e:
        logger.error(f"Tambah nilai error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('guru.nilai'))


@guru_bp.route('/edit-nilai/<int:id>', methods=['POST'])
def edit_nilai(id):
    try:
        nilai = request.form.get('nilai')
        predikat = request.form.get('predikat')
        catatan = request.form.get('catatan', '')
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE e_rapor SET nilai=%s, predikat=%s, catatan=%s, updated_at=%s
            WHERE id=%s
        """, (nilai, predikat, catatan, datetime.now(), id))
        conn.commit()
        cur.close()
        conn.close()
        flash('✅ Nilai berhasil diupdate!', 'success')
    except Exception as e:
        logger.error(f"Edit nilai error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('guru.nilai'))


@guru_bp.route('/hapus-nilai/<int:id>')
def hapus_nilai(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM e_rapor WHERE id=%s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        flash('✅ Nilai berhasil dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus nilai error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('guru.nilai'))


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
            cur = conn.cursor()
            
            if password and len(password) >= 4:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cur.execute("""
                    UPDATE users SET full_name=%s, email=%s, phone=%s, nip=%s, mata_pelajaran=%s,
                                   jenis_kelamin=%s, address=%s, password_hash=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, email, phone, nip, mata_pelajaran, jenis_kelamin, address, hashed, datetime.now(), current_user.id))
            else:
                cur.execute("""
                    UPDATE users SET full_name=%s, email=%s, phone=%s, nip=%s, mata_pelajaran=%s,
                                   jenis_kelamin=%s, address=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, email, phone, nip, mata_pelajaran, jenis_kelamin, address, datetime.now(), current_user.id))
            
            conn.commit()
            cur.close()
            conn.close()
            flash('✅ Profil berhasil diupdate!', 'success')
            return redirect(url_for('guru.profil'))
        except Exception as e:
            logger.error(f"Update profil error: {str(e)}")
            flash('Terjadi kesalahan', 'danger')
    
    return render_template('guru/profil.html',
                         name=current_user.full_name,
                         email=current_user.email,
                         phone=current_user.phone,
                         nip=current_user.nip,
                         mata_pelajaran=current_user.mata_pelajaran,
                         jenis_kelamin=current_user.jenis_kelamin,
                         address=current_user.address,
                         active_menu='profil')


# ============================================
# PENGATURAN
# ============================================
@guru_bp.route('/pengaturan')
def pengaturan():
    return render_template('guru/pengaturan.html', active_menu='pengaturan')


__all__ = ['guru_bp']