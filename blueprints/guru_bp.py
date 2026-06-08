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
    
    parsed = urlparse(database_url)
    
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port or 5432
    database = parsed.path.lstrip('/')
    
    print(f"Connecting to: {host}:{port} as {user}")
    
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


# CHECK ROLE
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
# ALGORITMA SORTING UNTUK DAFTAR MURID
# ============================================

def merge_sort(arr, key):
    """Merge Sort - O(n log n)"""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    
    return merge(left, right, key)


def merge(left, right, key):
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if str(left[i].get(key, '')).lower() <= str(right[j].get(key, '')).lower():
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heap_sort(arr, key):
    """Heap Sort - O(n log n)"""
    def heapify(arr, n, i, key):
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        
        if left < n and str(arr[left].get(key, '')).lower() > str(arr[largest].get(key, '')).lower():
            largest = left
        
        if right < n and str(arr[right].get(key, '')).lower() > str(arr[largest].get(key, '')).lower():
            largest = right
        
        if largest != i:
            arr[i], arr[largest] = arr[largest], arr[i]
            heapify(arr, n, largest, key)
    
    n = len(arr)
    
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i, key)
    
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0, key)
    
    return arr


def insertion_sort(arr, key):
    """Insertion Sort - O(n²)"""
    for i in range(1, len(arr)):
        current = arr[i]
        j = i - 1
        while j >= 0 and str(current.get(key, '')).lower() < str(arr[j].get(key, '')).lower():
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current
    return arr


def sequential_search(arr, key, value):
    """Sequential Search - O(n)"""
    results = []
    value_lower = value.lower()
    for item in arr:
        if value_lower in str(item.get(key, '')).lower():
            results.append(item)
    return results


def binary_search(arr, key, value):
    """Binary Search - O(log n) (data harus terurut ASC berdasarkan key)"""
    results = []
    search_value = value.lower()
    
    # Binary search untuk mencari satu elemen
    left, right = 0, len(arr) - 1
    found_index = -1
    
    while left <= right:
        mid = (left + right) // 2
        mid_value = str(arr[mid].get(key, '')).lower()
        
        if search_value == mid_value:
            found_index = mid
            break
        elif search_value < mid_value:
            right = mid - 1
        else:
            left = mid + 1
    
    # Cari semua yang match (kiri dan kanan)
    if found_index != -1:
        results.append(arr[found_index])
        # Cari ke kiri
        i = found_index - 1
        while i >= 0 and search_value in str(arr[i].get(key, '')).lower():
            results.append(arr[i])
            i -= 1
        # Cari ke kanan
        i = found_index + 1
        while i < len(arr) and search_value in str(arr[i].get(key, '')).lower():
            results.append(arr[i])
            i += 1
    
    return results

# DASHBOARD
@guru_bp.route('/dashboard')
def dashboard():
    try:
        conn = get_db_connection()
        
        total_murid = execute_query(conn, "SELECT COUNT(*) as total FROM users WHERE role = 'murid'", fetch_one=True)
        total_murid = total_murid['total'] if total_murid else 0
        
        tugas_aktif = execute_query(conn, "SELECT COUNT(*) as total FROM tugas WHERE guru_id = %s", (current_user.id,), fetch_one=True)
        tugas_aktif = tugas_aktif['total'] if tugas_aktif else 0
        
        tugas_terbaru = execute_query(conn, "SELECT * FROM tugas WHERE guru_id = %s ORDER BY created_at DESC LIMIT 5", (current_user.id,), fetch_all=True) or []
        
        for tugas in tugas_terbaru:
            jml = execute_query(conn, "SELECT COUNT(*) as total FROM kiriman_tugas WHERE tugas_id = %s", (tugas['id'],), fetch_one=True)
            tugas['jml_dikumpulkan'] = jml['total'] if jml else 0
        
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


# TUGAS
@guru_bp.route('/tugas')
def tugas():
    try:
        conn = get_db_connection()
        tugas_list = execute_query(conn, "SELECT * FROM tugas WHERE guru_id = %s ORDER BY created_at DESC", (current_user.id,), fetch_all=True) or []
        total_murid = execute_query(conn, "SELECT COUNT(*) as total FROM users WHERE role = 'murid'", fetch_one=True)
        total_murid = total_murid['total'] if total_murid else 0
        
        for tugas in tugas_list:
            jml = execute_query(conn, "SELECT COUNT(*) as total FROM kiriman_tugas WHERE tugas_id = %s", (tugas['id'],), fetch_one=True)
            tugas['jml_dikumpulkan'] = jml['total'] if jml else 0
        
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
                INSERT INTO tugas (guru_id, judul, mapel, deskripsi, deadline, kelas, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (current_user.id, judul, mapel, deskripsi, deadline, kelas, datetime.now(), datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Tugas berhasil dibuat!', 'success')
            return redirect(url_for('guru.tugas'))
        except Exception as e:
            logger.error(f"Buat tugas error: {str(e)}")
            flash('Terjadi kesalahan', 'danger')
    
    return render_template('guru/buat_tugas.html', active_menu='tugas')


@guru_bp.route('/tugas/edit/<int:id>', methods=['GET', 'POST'])
def edit_tugas(id):
    try:
        conn = get_db_connection()
        tugas = execute_query(conn, "SELECT * FROM tugas WHERE id = %s AND guru_id = %s", (id, current_user.id), fetch_one=True)
        
        if not tugas:
            flash('Tugas tidak ditemukan!', 'danger')
            conn.close()
            return redirect(url_for('guru.tugas'))
        
        if request.method == 'POST':
            judul = request.form.get('judul')
            mapel = request.form.get('mapel')
            deskripsi = request.form.get('deskripsi')
            deadline = request.form.get('deadline')
            kelas = request.form.get('kelas')
            
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tugas SET judul=%s, mapel=%s, deskripsi=%s, deadline=%s, kelas=%s, updated_at=%s
                WHERE id=%s AND guru_id=%s
            """, (judul, mapel, deskripsi, deadline, kelas, datetime.now(), id, current_user.id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Tugas berhasil diupdate!', 'success')
            return redirect(url_for('guru.tugas'))
        
        conn.close()
        return render_template('guru/edit_tugas.html', tugas=tugas, active_menu='tugas')
    except Exception as e:
        logger.error(f"Edit tugas error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.tugas'))


@guru_bp.route('/tugas/hapus/<int:id>')
def hapus_tugas(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM kiriman_tugas WHERE tugas_id = %s", (id,))
        cursor.execute("DELETE FROM tugas WHERE id = %s AND guru_id = %s", (id, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Tugas berhasil dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus tugas error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('guru.tugas'))


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
        return render_template('guru/kirim_tugas.html', tugas=tugas, kiriman_list=kiriman_list, active_menu='tugas')
    except Exception as e:
        logger.error(f"Kirim tugas error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.tugas'))


@guru_bp.route('/tugas/nilai/<int:kiriman_id>', methods=['POST'])
def nilai_tugas(kiriman_id):
    try:
        nilai = request.form.get('nilai')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE kiriman_tugas SET nilai=%s, dinilai_pada=%s WHERE id=%s", (nilai, datetime.now(), kiriman_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Nilai berhasil diberikan!', 'success')
    except Exception as e:
        logger.error(f"Nilai tugas error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(request.referrer or url_for('guru.tugas'))


# DAFTAR MURID
# ============================================
# DAFTAR MURID (dengan Sorting dan Searching)
# ============================================
@guru_bp.route('/daftar-murid')
def daftar_murid():
    try:
        conn = get_db_connection()
        
        # Ambil semua murid
        murid_list = execute_query(conn, """
            SELECT id, full_name, nis, nisn, kelas, jenis_kelamin, 
                   email, phone, address, tanggal_lahir
            FROM users 
            WHERE role = 'murid'
        """, fetch_all=True) or []
        
        conn.close()
        
        # Parameter dari request
        search_query = request.args.get('search', '')
        search_type = request.args.get('search_type', 'sequential')
        sort_by = request.args.get('sort_by', 'full_name')
        sort_algorithm = request.args.get('sort_algorithm', 'merge')
        action = request.args.get('action', '')
        
        # ========== SORTING ==========
        if action == 'sort' or sort_algorithm:
            if sort_algorithm == 'merge':
                murid_list = merge_sort(murid_list, sort_by)
            elif sort_algorithm == 'heap':
                murid_list = heap_sort(murid_list, sort_by)
            elif sort_algorithm == 'insertion':
                murid_list = insertion_sort(murid_list, sort_by)
            else:
                murid_list = merge_sort(murid_list, sort_by)
        
        # ========== SEARCHING ==========
        if search_query:
            if search_type == 'binary':
                # Binary search - pastikan data sudah terurut berdasarkan full_name
                murid_list_sorted = merge_sort(murid_list, 'full_name')
                murid_list = binary_search(murid_list_sorted, 'full_name', search_query)
                if not murid_list:
                    flash(f'Tidak ditemukan data untuk "{search_query}"', 'warning')
                else:
                    flash(f'🔍 Binary Search: Ditemukan {len(murid_list)} data untuk "{search_query}"', 'info')
            else:
                # Sequential search
                murid_list = sequential_search(murid_list, 'full_name', search_query)
                if not murid_list:
                    flash(f'Tidak ditemukan data untuk "{search_query}"', 'warning')
                else:
                    flash(f'🔍 Sequential Search: Ditemukan {len(murid_list)} data untuk "{search_query}"', 'info')
        
        return render_template('guru/daftar_murid.html',
                             murid=murid_list,
                             total_murid=len(murid_list),
                             search_query=search_query,
                             search_type=search_type,
                             sort_by=sort_by,
                             sort_algorithm=sort_algorithm,
                             active_menu='daftar_murid')
    except Exception as e:
        logger.error(f"Daftar murid error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))

@guru_bp.route('/murid/<int:id>')
def detail_murid(id):
    try:
        conn = get_db_connection()
        murid = execute_query(conn, """
            SELECT id, full_name, nis, nisn, kelas, jenis_kelamin, 
                   email, phone, address, tanggal_lahir, created_at
            FROM users WHERE id = %s AND role = 'murid'
        """, (id,), fetch_one=True)
        
        if not murid:
            flash('Murid tidak ditemukan!', 'danger')
            conn.close()
            return redirect(url_for('guru.daftar_murid'))
        
        nilai = execute_query(conn, "SELECT * FROM e_rapor WHERE siswa_id = %s ORDER BY created_at DESC", (id,), fetch_all=True) or []
        tugas = execute_query(conn, """
            SELECT k.*, t.judul as tugas_judul, t.mapel
            FROM kiriman_tugas k JOIN tugas t ON k.tugas_id = t.id
            WHERE k.siswa_id = %s ORDER BY k.created_at DESC
        """, (id,), fetch_all=True) or []
        
        conn.close()
        return render_template('guru/detail_murid.html', murid=murid, nilai=nilai, tugas=tugas, active_menu='daftar_murid')
    except Exception as e:
        logger.error(f"Detail murid error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.daftar_murid'))


# PENGUMUMAN
@guru_bp.route('/pengumuman')
def pengumuman():
    try:
        conn = get_db_connection()
        pengumuman_list = execute_query(conn, "SELECT * FROM pengumuman WHERE target_role IN ('semua', 'guru') ORDER BY created_at DESC", fetch_all=True) or []
        conn.close()
        return render_template('guru/pengumuman.html', pengumuman=pengumuman_list, active_menu='pengumuman')
    except Exception as e:
        logger.error(f"Pengumuman error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))

# ============================================
# TAMBAH PENGUMUMAN (GET dan POST)
# ============================================
@guru_bp.route('/pengumuman/tambah', methods=['GET', 'POST'])
def tambah_pengumuman():
    """Tambah pengumuman oleh guru"""
    if request.method == 'POST':
        try:
            judul = request.form.get('judul')
            isi = request.form.get('isi')
            target_role = request.form.get('target_role', 'semua')
            
            if not judul or not isi:
                flash('Judul dan isi pengumuman harus diisi!', 'danger')
                return redirect(url_for('guru.pengumuman'))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pengumuman (admin_id, judul, isi, target_role, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (current_user.id, judul, isi, target_role, datetime.now(), datetime.now()))
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('✅ Pengumuman berhasil ditambahkan!', 'success')
            return redirect(url_for('guru.pengumuman'))
        except Exception as e:
            logger.error(f"Tambah pengumuman error: {str(e)}")
            flash('Terjadi kesalahan saat menambah pengumuman', 'danger')
            return redirect(url_for('guru.pengumuman'))
    
    # GET request - tampilkan form tambah pengumuman
    return render_template('guru/tambah_pengumuman.html', active_menu='pengumuman')


# ============================================
# HAPUS PENGUMUMAN
# ============================================
@guru_bp.route('/pengumuman/hapus/<int:id>')
def hapus_pengumuman(id):
    """Hapus pengumuman oleh guru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pengumuman WHERE id = %s AND admin_id = %s", (id, current_user.id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('✅ Pengumuman berhasil dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus pengumuman error: {str(e)}")
        flash('Terjadi kesalahan saat menghapus pengumuman', 'danger')
    return redirect(url_for('guru.pengumuman'))

# NILAI / RAPOR
@guru_bp.route('/nilai')
def nilai():
    try:
        conn = get_db_connection()
        nilai_list = execute_query(conn, """
            SELECT e.*, u.full_name as siswa_name, u.nis, u.kelas 
            FROM e_rapor e JOIN users u ON e.siswa_id = u.id 
            ORDER BY e.created_at DESC
        """, fetch_all=True) or []
        conn.close()
        return render_template('guru/nilai.html', nilai=nilai_list, active_menu='nilai')
    except Exception as e:
        logger.error(f"Nilai error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


# JADWAL MENGAJAR
@guru_bp.route('/jadwal-mengajar')
def jadwal_mengajar():
    try:
        mata_pelajaran = getattr(current_user, 'mata_pelajaran', 'Matematika')
        jadwal_list = [
            {'hari': 'Senin', 'jam': '07:30 - 09:00', 'kelas': 'Kelas A', 'ruang': 'Ruang 101'},
            {'hari': 'Senin', 'jam': '09:15 - 10:45', 'kelas': 'Kelas B', 'ruang': 'Ruang 102'},
            {'hari': 'Selasa', 'jam': '07:30 - 09:00', 'kelas': 'Kelas C', 'ruang': 'Ruang 103'},
            {'hari': 'Rabu', 'jam': '10:00 - 11:30', 'kelas': 'Kelas A', 'ruang': 'Ruang 101'},
            {'hari': 'Kamis', 'jam': '07:30 - 09:00', 'kelas': 'Kelas B', 'ruang': 'Ruang 102'},
            {'hari': 'Jumat', 'jam': '08:00 - 09:30', 'kelas': 'Kelas C', 'ruang': 'Ruang 103'},
        ]
        return render_template('guru/jadwal_mengajar.html', jadwal=jadwal_list, mata_pelajaran=mata_pelajaran, active_menu='jadwal')
    except Exception as e:
        logger.error(f"Jadwal mengajar error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('guru.dashboard'))


# PROFIL GURU
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
            flash('Profil berhasil diupdate!', 'success')
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


# PENGATURAN
@guru_bp.route('/pengaturan')
def pengaturan():
    return render_template('guru/pengaturan.html', active_menu='pengaturan')


# INDEX / ROOT REDIRECT
@guru_bp.route('/')
def index():
    return redirect(url_for('guru.dashboard'))


__all__ = ['guru_bp']