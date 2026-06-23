"""
Admin Blueprint for TK RA SA'DIAH - FULL VERSION
Fitur: CRUD Siswa, Guru, Keuangan, Pengumuman, E-Rapor, Sorting (Merge/Shell/Insertion)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_required, current_user
import bcrypt
import logging
from datetime import datetime
import pg8000
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
logger = logging.getLogger(__name__)


# ============================================
# TEMPLATE FILTERS UNTUK ADMIN BP
# ============================================

@admin_bp.app_template_filter('format_rp')
def format_rp(value):
    """Format angka menjadi Rupiah (contoh: 500000 -> 500.000)"""
    try:
        if value is None:
            return '0'
        return f"{int(value):,}".replace(',', '.')
    except (ValueError, TypeError):
        return str(value)


@admin_bp.app_template_filter('format_date')
def format_date(value):
    """Format tanggal menjadi dd/mm/yyyy"""
    try:
        if value is None:
            return '-'
        if isinstance(value, str):
            from datetime import datetime
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value.strftime('%d/%m/%Y')
    except:
        return str(value)


@admin_bp.app_template_filter('format_datetime')
def format_datetime(value):
    """Format datetime menjadi dd/mm/yyyy HH:MM"""
    try:
        if value is None:
            return '-'
        if isinstance(value, str):
            from datetime import datetime
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value.strftime('%d/%m/%Y %H:%M')
    except:
        return str(value)


@admin_bp.before_request
@login_required
def check_role():
    if current_user.role != 'admin':
        flash('Akses ditolak! Anda bukan admin.', 'danger')
        return redirect(url_for('auth.login'))


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
# ALGORITMA SORTING
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
        if left[i].get(key, '').lower() <= right[j].get(key, '').lower():
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def shell_sort(arr, key):
    """Shell Sort - O(n log n) sampai O(n²)"""
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and temp.get(key, '').lower() < arr[j - gap].get(key, '').lower():
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr


def insertion_sort(arr, key):
    """Insertion Sort - O(n²)"""
    for i in range(1, len(arr)):
        current = arr[i]
        j = i - 1
        while j >= 0 and current.get(key, '').lower() < arr[j].get(key, '').lower():
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current
    return arr


def binary_search(data, key, value):
    """Binary Search - O(log n) (data harus terurut)"""
    left, right = 0, len(data) - 1
    results = []
    
    while left <= right:
        mid = (left + right) // 2
        current_val = data[mid].get(key, '').lower()
        search_val = value.lower()
        
        if search_val in current_val:
            results.append(data[mid])
            l, r = mid - 1, mid + 1
            while l >= 0 and search_val in data[l].get(key, '').lower():
                results.append(data[l])
                l -= 1
            while r < len(data) and search_val in data[r].get(key, '').lower():
                results.append(data[r])
                r += 1
            break
        elif search_val < current_val:
            right = mid - 1
        else:
            left = mid + 1
    
    return results


# ============================================
# DASHBOARD ADMIN
# ============================================
@admin_bp.route('/dashboard')
def dashboard():
    try:
        conn = get_db_connection()
        
        def run_query(query, params=None, fetch_one=False, fetch_all=False):
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            if fetch_one:
                result = cursor.fetchone()
                if result:
                    cols = [desc[0] for desc in cursor.description]
                    result = dict(zip(cols, result))
                cursor.close()
                return result
            elif fetch_all:
                results = cursor.fetchall()
                if results:
                    cols = [desc[0] for desc in cursor.description]
                    results = [dict(zip(cols, row)) for row in results]
                cursor.close()
                return results
            else:
                conn.commit()
                rowcount = cursor.rowcount
                cursor.close()
                return rowcount
        
        total_siswa = run_query("SELECT COUNT(*) as total FROM users WHERE role = 'murid'", fetch_one=True)['total']
        total_guru = run_query("SELECT COUNT(*) as total FROM users WHERE role = 'guru'", fetch_one=True)['total']
        total_pembayaran = run_query("SELECT COUNT(*) as total FROM pembayaran WHERE status = 'lunas'", fetch_one=True)['total']
        total_rapor = run_query("SELECT COUNT(*) as total FROM e_rapor", fetch_one=True)['total']
        
        aktivitas = run_query("""
            (SELECT 'siswa' as tipe, full_name as nama, created_at, 'ditambahkan' as aksi 
             FROM users WHERE role = 'murid' ORDER BY created_at DESC LIMIT 5)
            UNION ALL
            (SELECT 'pembayaran' as tipe, u.full_name as nama, p.created_at, p.status as aksi 
             FROM pembayaran p JOIN users u ON p.nis_murid = u.nis ORDER BY p.created_at DESC LIMIT 5)
            ORDER BY created_at DESC LIMIT 10
        """, fetch_all=True) or []
        
        conn.close()
        
        return render_template('admin/dashboard.html',
                             name=current_user.full_name,
                             active_menu='dashboard',
                             total_siswa=total_siswa,
                             total_guru=total_guru,
                             total_pembayaran=total_pembayaran,
                             total_rapor=total_rapor,
                             aktivitas=aktivitas,
                             now=datetime.now())
    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


# ============================================
# KELOLA SISWA
# ============================================
@admin_bp.route('/siswa')
def kelola_siswa():
    """Kelola data siswa dengan pencarian dan sorting"""
    try:
        conn = get_db_connection()
        
        def run_query(query, params=None, fetch_all=False):
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            if results:
                cols = [desc[0] for desc in cursor.description]
                results = [dict(zip(cols, row)) for row in results]
            cursor.close()
            return results
        
        search_query = request.args.get('search_query', '')
        sort_by = request.args.get('sort_by', 'full_name')
        sort_type = request.args.get('sort_type', 'merge')
        
        if search_query:
            query = """
                SELECT * FROM users 
                WHERE role = 'murid' 
                AND (full_name ILIKE %s OR nis ILIKE %s)
                ORDER BY full_name
            """
            siswa = run_query(query, (f'%{search_query}%', f'%{search_query}%'), fetch_all=True)
        else:
            siswa = run_query("SELECT * FROM users WHERE role = 'murid' ORDER BY full_name", fetch_all=True)
        
        conn.close()
        
        if sort_type == 'merge':
            siswa = merge_sort(siswa, sort_by)
        elif sort_type == 'insertion':
            siswa = insertion_sort(siswa, sort_by)
        elif sort_type == 'shell':
            siswa = shell_sort(siswa, sort_by)
        
        if search_query:
            flash(f'🔍 Menampilkan {len(siswa)} hasil pencarian untuk "{search_query}"', 'info')
        
        return render_template('admin/kelola_siswa.html',
                             active_menu='siswa',
                             name=current_user.full_name,
                             siswa=siswa,
                             search_query=search_query,
                             sort_by=sort_by,
                             sort_type=sort_type)
    except Exception as e:
        logger.error(f"Kelola siswa error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


# ============================================
# TAMBAH SISWA
# ============================================
@admin_bp.route('/siswa/tambah', methods=['GET', 'POST'])
def tambah_siswa():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        nis = request.form.get('nis')
        nisn = request.form.get('nisn')
        kelas = request.form.get('kelas')
        jenis_kelamin = request.form.get('jenis_kelamin')
        tanggal_lahir = request.form.get('tanggal_lahir')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        address = request.form.get('address', '')
        
        errors = []
        if not username:
            errors.append('Username harus diisi')
        if not full_name:
            errors.append('Nama lengkap harus diisi')
        if not nis:
            errors.append('NIS harus diisi')
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
            cursor = conn.cursor()
            
            cursor.execute("SELECT id FROM users WHERE username = %s OR nis = %s", (username, nis))
            if cursor.fetchone():
                flash('Username atau NIS sudah digunakan!', 'danger')
                cursor.close()
                conn.close()
                return render_template('admin/tambah_siswa.html')
            
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name, nis, nisn, kelas, 
                                   jenis_kelamin, tanggal_lahir, email, phone, address, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (username, hashed, 'murid', full_name, nis, nisn, kelas, 
                  jenis_kelamin, tanggal_lahir, email, phone, address, datetime.now(), datetime.now()))
            
            conn.commit()
            new_id = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            flash(f'✅ Siswa "{full_name}" (NIS: {nis}) berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.kelola_siswa'))
            
        except Exception as e:
            logger.error(f"Tambah siswa error: {str(e)}")
            flash(f'Terjadi kesalahan: {str(e)}', 'danger')
    
    return render_template('admin/tambah_siswa.html')


# ============================================
# EDIT SISWA - DITAMBAHKAN!
# ============================================
@admin_bp.route('/siswa/edit/<int:id>', methods=['GET', 'POST'])
def edit_siswa(id):
    """Edit data siswa"""
    try:
        conn = get_db_connection()
        
        if request.method == 'POST':
            full_name = request.form.get('full_name')
            nis = request.form.get('nis')
            nisn = request.form.get('nisn')
            kelas = request.form.get('kelas')
            jenis_kelamin = request.form.get('jenis_kelamin')
            tanggal_lahir = request.form.get('tanggal_lahir')
            email = request.form.get('email')
            phone = request.form.get('phone')
            address = request.form.get('address')
            password = request.form.get('password')
            
            cursor = conn.cursor()
            
            if password:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("""
                    UPDATE users SET full_name=%s, nis=%s, nisn=%s, kelas=%s, jenis_kelamin=%s,
                                   tanggal_lahir=%s, email=%s, phone=%s, address=%s,
                                   password_hash=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, nis, nisn, kelas, jenis_kelamin, tanggal_lahir,
                      email, phone, address, hashed, datetime.now(), id))
            else:
                cursor.execute("""
                    UPDATE users SET full_name=%s, nis=%s, nisn=%s, kelas=%s, jenis_kelamin=%s,
                                   tanggal_lahir=%s, email=%s, phone=%s, address=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, nis, nisn, kelas, jenis_kelamin, tanggal_lahir,
                      email, phone, address, datetime.now(), id))
            
            conn.commit()
            cursor.close()
            conn.close()
            flash('✅ Data siswa berhasil diupdate!', 'success')
            return redirect(url_for('admin.kelola_siswa'))
        
        # GET request - tampilkan form edit
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s AND role = 'murid'", (id,))
        result = cursor.fetchone()
        if result:
            cols = [desc[0] for desc in cursor.description]
            siswa = dict(zip(cols, result))
        else:
            siswa = None
        cursor.close()
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
# HAPUS SISWA - DITAMBAHKAN!
# ============================================
@admin_bp.route('/siswa/hapus/<int:id>')
def hapus_siswa(id):
    """Hapus siswa"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s AND role = 'murid'", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('✅ Siswa berhasil dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus siswa error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('admin.kelola_siswa'))


# ============================================
# KELOLA GURU
# ============================================
@admin_bp.route('/guru')
def kelola_guru():
    try:
        conn = get_db_connection()
        
        def run_query(query, params=None, fetch_all=False):
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            if results:
                cols = [desc[0] for desc in cursor.description]
                results = [dict(zip(cols, row)) for row in results]
            cursor.close()
            return results
        
        guru = run_query("SELECT * FROM users WHERE role = 'guru' ORDER BY id", fetch_all=True)
        conn.close()
        
        search_query = request.args.get('search_query', '')
        sort_by = request.args.get('sort_by', 'full_name')
        sort_type = request.args.get('sort_type', 'merge')
        
        if sort_type == 'merge':
            guru = merge_sort(guru, sort_by)
            flash_msg = f'✅ Data diurutkan dengan Merge Sort (O(n log n)) berdasarkan {sort_by}'
        elif sort_type == 'shell':
            guru = shell_sort(guru, sort_by)
            flash_msg = f'✅ Data diurutkan dengan Shell Sort (O(n log n)) berdasarkan {sort_by}'
        else:
            guru = merge_sort(guru, sort_by)
            flash_msg = f'✅ Data diurutkan dengan Merge Sort (O(n log n)) berdasarkan {sort_by}'
        
        if search_query:
            guru_sorted = merge_sort(guru, 'full_name')
            guru = binary_search(guru_sorted, 'full_name', search_query)
            flash(f'🔍 Binary Search: Ditemukan {len(guru)} data untuk "{search_query}"', 'info')
        elif sort_type in ['merge', 'shell']:
            flash(flash_msg, 'success')
        
        return render_template('admin/kelola_guru.html',
                             active_menu='guru',
                             name=current_user.full_name,
                             guru=guru,
                             search_query=search_query,
                             sort_by=sort_by,
                             sort_type=sort_type,
                             total_guru=len(guru))
    except Exception as e:
        logger.error(f"Kelola guru error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


# ============================================
# TAMBAH GURU
# ============================================
@admin_bp.route('/guru/tambah', methods=['GET', 'POST'])
def tambah_guru():
    """Tambah guru baru"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        nip = request.form.get('nip')
        mata_pelajaran = request.form.get('mata_pelajaran')
        jenis_kelamin = request.form.get('jenis_kelamin')
        tanggal_lahir = request.form.get('tanggal_lahir')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')
        
        if not username or not full_name or not nip or not password:
            flash('Semua field wajib harus diisi!', 'danger')
            return render_template('admin/tambah_guru.html')
        
        if len(password) < 4:
            flash('Password minimal 4 karakter!', 'danger')
            return render_template('admin/tambah_guru.html')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Cek username atau NIP sudah ada
            cursor.execute("SELECT id FROM users WHERE username = %s OR nip = %s", (username, nip))
            if cursor.fetchone():
                flash('Username atau NIP sudah digunakan!', 'danger')
                cursor.close()
                conn.close()
                return render_template('admin/tambah_guru.html')
            
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, full_name, nip, mata_pelajaran,
                                   jenis_kelamin, tanggal_lahir, email, phone, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (username, hashed, 'guru', full_name, nip, mata_pelajaran,
                  jenis_kelamin, tanggal_lahir, email, phone, datetime.now(), datetime.now()))
            conn.commit()
            new_id = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            flash(f'✅ Guru "{full_name}" (NIP: {nip}) berhasil ditambahkan!', 'success')
            return redirect(url_for('admin.kelola_guru'))
            
        except Exception as e:
            logger.error(f"Tambah guru error: {str(e)}")
            flash('Terjadi kesalahan', 'danger')
    
    return render_template('admin/tambah_guru.html')


# ============================================
# EDIT GURU
# ============================================
@admin_bp.route('/guru/edit/<int:id>', methods=['GET', 'POST'])
def edit_guru(id):
    """Edit data guru"""
    try:
        conn = get_db_connection()
        
        if request.method == 'POST':
            full_name = request.form.get('full_name')
            nip = request.form.get('nip')
            mata_pelajaran = request.form.get('mata_pelajaran')
            jenis_kelamin = request.form.get('jenis_kelamin')
            tanggal_lahir = request.form.get('tanggal_lahir')
            email = request.form.get('email')
            phone = request.form.get('phone')
            password = request.form.get('password')
            
            cursor = conn.cursor()
            
            if password:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("""
                    UPDATE users SET full_name=%s, nip=%s, mata_pelajaran=%s, jenis_kelamin=%s,
                                   tanggal_lahir=%s, email=%s, phone=%s, password_hash=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, nip, mata_pelajaran, jenis_kelamin, tanggal_lahir,
                      email, phone, hashed, datetime.now(), id))
            else:
                cursor.execute("""
                    UPDATE users SET full_name=%s, nip=%s, mata_pelajaran=%s, jenis_kelamin=%s,
                                   tanggal_lahir=%s, email=%s, phone=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, nip, mata_pelajaran, jenis_kelamin, tanggal_lahir,
                      email, phone, datetime.now(), id))
            
            conn.commit()
            cursor.close()
            conn.close()
            flash('✅ Data guru berhasil diupdate!', 'success')
            return redirect(url_for('admin.kelola_guru'))
        
        # GET request
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s AND role = 'guru'", (id,))
        result = cursor.fetchone()
        if result:
            cols = [desc[0] for desc in cursor.description]
            guru = dict(zip(cols, result))
        else:
            guru = None
        cursor.close()
        conn.close()
        
        if not guru:
            flash('Guru tidak ditemukan!', 'danger')
            return redirect(url_for('admin.kelola_guru'))
        
        return render_template('admin/edit_guru.html', guru=guru)
        
    except Exception as e:
        logger.error(f"Edit guru error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.kelola_guru'))


# ============================================
# HAPUS GURU
# ============================================
@admin_bp.route('/guru/hapus/<int:id>')
def hapus_guru(id):
    """Hapus guru"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s AND role = 'guru'", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('✅ Guru berhasil dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus guru error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('admin.kelola_guru'))


# ============================================
# KELOLA PENGUMUMAN (CRUD)
# ============================================
@admin_bp.route('/pengumuman')
def kelola_pengumuman():
    """Kelola pengumuman"""
    try:
        from models.pengumuman_model import Pengumuman
        pengumuman_model = Pengumuman()
        pengumuman = pengumuman_model.get_all_with_admin()
        return render_template('admin/pengumuman.html',
                             active_menu='pengaturan',
                             name=current_user.full_name,
                             pengumuman=pengumuman)
    except Exception as e:
        logger.error(f"Kelola pengumuman error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/pengumuman/tambah', methods=['POST'])
def tambah_pengumuman():
    """Tambah pengumuman"""
    try:
        from models.pengumuman_model import Pengumuman
        judul = request.form.get('judul')
        isi = request.form.get('isi')
        target_role = request.form.get('target_role', 'semua')
        
        data = {
            'admin_id': current_user.id,
            'judul': judul,
            'isi': isi,
            'target_role': target_role
        }
        pengumuman = Pengumuman()
        pengumuman.insert(data)
        flash('✅ Pengumuman berhasil ditambahkan!', 'success')
    except Exception as e:
        logger.error(f"Tambah pengumuman error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('admin.kelola_pengumuman'))


@admin_bp.route('/pengumuman/hapus/<int:id>')
def hapus_pengumuman(id):
    """Hapus pengumuman"""
    try:
        from models.pengumuman_model import Pengumuman
        pengumuman = Pengumuman()
        pengumuman.delete(id)
        flash('✅ Pengumuman dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus pengumuman error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('admin.kelola_pengumuman'))


# ============================================
# KELOLA PEMBAYARAN
# ============================================
@admin_bp.route('/pembayaran')
def kelola_pembayaran():
    try:
        conn = get_db_connection()
        
        def run_query(query, params=None, fetch_all=False):
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            if results:
                cols = [desc[0] for desc in cursor.description]
                results = [dict(zip(cols, row)) for row in results]
            cursor.close()
            return results
        
        pembayaran = run_query("""
            SELECT p.*, u.full_name as murid_name, u.nis, u.kelas
            FROM pembayaran p
            JOIN users u ON p.nis_murid = u.nis
            ORDER BY p.tahun DESC, p.bulan DESC
        """, fetch_all=True) or []
        
        siswa = run_query("SELECT nis, full_name, kelas FROM users WHERE role = 'murid' ORDER BY full_name", fetch_all=True) or []
        
        conn.close()
        
        total_tagihan = sum(p['nominal'] for p in pembayaran)
        total_terbayar = sum(p['nominal'] for p in pembayaran if p['status'] == 'lunas')
        
        return render_template('admin/kelola_pembayaran.html',
                             active_menu='pembayaran',
                             name=current_user.full_name,
                             pembayaran=pembayaran,
                             siswa=siswa,
                             total_tagihan=total_tagihan,
                             total_terbayar=total_terbayar,
                             total_belum_bayar=total_tagihan - total_terbayar)
    except Exception as e:
        logger.error(f"Kelola pembayaran error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/pembayaran/tambah', methods=['POST'])
def tambah_pembayaran():
    try:
        nis_murid = request.form.get('nis_murid')
        bulan = request.form.get('bulan')
        tahun = request.form.get('tahun')
        nominal = request.form.get('nominal')
        status = request.form.get('status')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pembayaran (nis_murid, bulan, tahun, nominal, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nis_murid, bulan, tahun, nominal, status, datetime.now(), datetime.now()))
        conn.commit()
        cursor.close()
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
        cursor = conn.cursor()
        cursor.execute("UPDATE pembayaran SET status = %s, updated_at = %s WHERE id = %s", 
                   (status, datetime.now(), id))
        conn.commit()
        cursor.close()
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
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pembayaran WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('✅ Pembayaran dihapus!', 'success')
    except Exception as e:
        logger.error(f"Hapus pembayaran error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
    return redirect(url_for('admin.kelola_pembayaran'))


# ============================================
# E-RAPOR
# ============================================
@admin_bp.route('/e-rapor')
def e_rapor():
    try:
        conn = get_db_connection()
        
        def run_query(query, params=None, fetch_all=False):
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            if results:
                cols = [desc[0] for desc in cursor.description]
                results = [dict(zip(cols, row)) for row in results]
            cursor.close()
            return results
        
        rapor = run_query("""
            SELECT e.*, u.full_name as siswa_name, u.nis, u.kelas
            FROM e_rapor e
            JOIN users u ON e.siswa_id = u.id
            ORDER BY e.created_at DESC
        """, fetch_all=True) or []
        
        siswa = run_query("SELECT id, full_name, nis, kelas FROM users WHERE role = 'murid' ORDER BY full_name", fetch_all=True) or []
        
        conn.close()
        
        return render_template('admin/e_rapor.html',
                             active_menu='e_rapor',
                             name=current_user.full_name,
                             rapor=rapor,
                             siswa=siswa)
    except Exception as e:
        logger.error(f"E-Rapor error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))


# ============================================
# PROFIL ADMIN
# ============================================
@admin_bp.route('/profil', methods=['GET', 'POST'])
def profil():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            if password:
                hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("""
                    UPDATE users SET full_name=%s, email=%s, phone=%s, password_hash=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, email, phone, hashed, datetime.now(), current_user.id))
            else:
                cursor.execute("""
                    UPDATE users SET full_name=%s, email=%s, phone=%s, updated_at=%s
                    WHERE id=%s
                """, (full_name, email, phone, datetime.now(), current_user.id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('✅ Profil berhasil diupdate!', 'success')
            return redirect(url_for('admin.profil'))
            
        except Exception as e:
            logger.error(f"Update profil error: {str(e)}")
            flash('Terjadi kesalahan', 'danger')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT full_name, email, phone FROM users WHERE id = %s", (current_user.id,))
    result = cursor.fetchone()
    if result:
        cols = [desc[0] for desc in cursor.description]
        user_data = dict(zip(cols, result))
    else:
        user_data = None
    cursor.close()
    conn.close()
    
    return render_template('admin/profil.html',
                         active_menu='profil',
                         name=user_data['full_name'] if user_data else current_user.full_name,
                         email=user_data['email'] if user_data else '',
                         phone=user_data['phone'] if user_data else '')


# ============================================
# PENGATURAN SISTEM
# ============================================
@admin_bp.route('/pengaturan')
def pengaturan():
    try:
        conn = get_db_connection()
        
        def run_query(query, fetch_one=False):
            cursor = conn.cursor()
            cursor.execute(query)
            if fetch_one:
                result = cursor.fetchone()
                if result:
                    cols = [desc[0] for desc in cursor.description]
                    result = dict(zip(cols, result))
            else:
                result = None
            cursor.close()
            return result
        
        total_users = run_query("SELECT COUNT(*) as total FROM users", fetch_one=True)['total']
        total_pengumuman = run_query("SELECT COUNT(*) as total FROM pengumuman", fetch_one=True)['total']
        total_penugasan = run_query("SELECT COUNT(*) as total FROM penugasan", fetch_one=True)['total']
        
        conn.close()
        
        return render_template('admin/pengaturan.html', 
                             name=current_user.full_name,
                             active_menu='pengaturan',
                             total_users=total_users,
                             total_pengumuman=total_pengumuman,
                             total_penugasan=total_penugasan,
                             now=datetime.now())
    except Exception as e:
        logger.error(f"Pengaturan error: {str(e)}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('admin.dashboard'))