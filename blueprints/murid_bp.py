"""
Murid Blueprint for TK RA SA'DIAH - WITH PG8000
"""

from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
import pg8000
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime

load_dotenv()
murid_bp = Blueprint('murid', __name__, url_prefix='/murid')


def get_db_connection():
    """Mendapatkan koneksi database dari DATABASE_URL (Supabase) menggunakan pg8000"""
    import os
    import pg8000
    from dotenv import load_dotenv
    
    load_dotenv()
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        raise Exception("DATABASE_URL tidak ditemukan di environment!")
    
    return pg8000.connect(database_url)


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


@murid_bp.before_request
@login_required
def check_role():
    """Check if user has murid role"""
    if current_user.role != 'murid':
        flash('Akses ditolak! Anda bukan murid.', 'danger')
        return redirect(url_for('auth.login'))


# ============================================
# DASHBOARD MURID
# ============================================
@murid_bp.route('/dashboard')
def dashboard():
    """Student dashboard"""
    try:
        # Data sementara untuk testing (karena tabel mungkin belum ada)
        statistik = {
            'rata_rata_nilai': 85,
            'tugas_selesai': 3,
            'tugas_terlambat': 1,
            'pengumuman_baru': 2
        }
        
        daftar_tugas = [
            {'id': 1, 'judul': 'Matematika - Latihan Soal', 'mapel': 'Matematika', 'deadline': '2024-12-20', 'status': 'belum'},
            {'id': 2, 'judul': 'Bahasa Indonesia - Membaca', 'mapel': 'Bahasa Indonesia', 'deadline': '2024-12-18', 'status': 'terlambat'},
            {'id': 3, 'judul': 'IPA - Praktikum', 'mapel': 'IPA', 'deadline': '2024-12-25', 'status': 'belum'},
        ]
        
        nilai_terbaru = [
            {'mapel': 'Matematika', 'nilai': 90, 'predikat': 'A', 'tanggal': '2024-12-10'},
            {'mapel': 'Bahasa Indonesia', 'nilai': 85, 'predikat': 'B', 'tanggal': '2024-12-09'},
        ]
        
        pengumuman_terbaru = [
            {'judul': 'Libur Akhir Semester', 'isi': 'Libur akan dimulai tanggal 20 Desember 2024', 'created_at': datetime.now()},
            {'judul': 'Pembagian Rapor', 'isi': 'Pembagian rapor akan dilaksanakan tanggal 18 Desember', 'created_at': datetime.now()},
        ]
        
        jadwal_hari_ini = [
            {'jam': '07:30 - 08:30', 'mapel': 'Matematika', 'guru': 'Budi Santoso', 'ruangan': 'Ruang 1'},
            {'jam': '08:30 - 09:30', 'mapel': 'Bahasa Indonesia', 'guru': 'Siti Aminah', 'ruangan': 'Ruang 2'},
        ]
        
        return render_template('murid/dashboard.html',
                             name=current_user.full_name or current_user.username,
                             email=getattr(current_user, 'email', 'email@example.com'),
                             kelas=getattr(current_user, 'kelas', 'TK A'),
                             rata_rata_nilai=statistik['rata_rata_nilai'],
                             tugas_selesai=statistik['tugas_selesai'],
                             tugas_terlambat=statistik['tugas_terlambat'],
                             pengumuman_baru=statistik['pengumuman_baru'],
                             daftar_tugas=daftar_tugas,
                             nilai_terbaru=nilai_terbaru,
                             pengumuman_terbaru=pengumuman_terbaru,
                             jadwal_hari_ini=jadwal_hari_ini,
                             active_menu='dashboard')
    except Exception as e:
        print(f"Dashboard error: {e}")
        flash('Terjadi kesalahan saat memuat dashboard', 'danger')
        return redirect(url_for('murid.dashboard_fallback'))


@murid_bp.route('/dashboard-fallback')
def dashboard_fallback():
    """Fallback dashboard jika terjadi error"""
    return render_template('murid/dashboard.html',
                         name=current_user.full_name or current_user.username,
                         email='',
                         kelas='TK A',
                         rata_rata_nilai=0,
                         tugas_selesai=0,
                         tugas_terlambat=0,
                         pengumuman_baru=0,
                         daftar_tugas=[],
                         nilai_terbaru=[],
                         pengumuman_terbaru=[],
                         jadwal_hari_ini=[],
                         active_menu='dashboard')


# ============================================
# PENUGASAN (TUGAS)
# ============================================
@murid_bp.route('/tugas')
def tugas():
    try:
        tugas_list = [
            {'id': 1, 'judul': 'Matematika - Latihan Soal', 'mapel': 'Matematika', 'deadline': '2024-12-20', 'status': 'belum', 'nilai': None},
            {'id': 2, 'judul': 'Bahasa Indonesia - Membaca', 'mapel': 'Bahasa Indonesia', 'deadline': '2024-12-18', 'status': 'terlambat', 'nilai': None},
            {'id': 3, 'judul': 'IPA - Praktikum', 'mapel': 'IPA', 'deadline': '2024-12-25', 'status': 'belum', 'nilai': None},
        ]
        return render_template('murid/tugas.html', tugas_list=tugas_list, active_menu='tugas')
    except Exception as e:
        print(f"Tugas error: {e}")
        flash('Terjadi kesalahan', 'danger')
        return redirect(url_for('murid.dashboard'))


@murid_bp.route('/tugas/kirim/<int:id>', methods=['GET', 'POST'])
def kirim_tugas(id):
    if request.method == 'POST':
        jawaban = request.form.get('jawaban')
        flash(f'Tugas berhasil dikirim!', 'success')
        return redirect(url_for('murid.tugas'))
    
    tugas = {'id': id, 'judul': f'Tugas #{id}', 'deskripsi': 'Kerjakan soal-soal berikut dengan teliti.', 'deadline': '2024-12-20'}
    return render_template('murid/kirim_tugas.html', tugas=tugas, active_menu='tugas')


@murid_bp.route('/riwayat-tugas')
def riwayat_tugas():
    riwayat = [
        {'judul': 'Matematika - Kuis 1', 'tanggal_kirim': '2024-12-01', 'nilai': 90, 'feedback': 'Bagus!'},
        {'judul': 'Bahasa Indonesia - Esai', 'tanggal_kirim': '2024-11-28', 'nilai': 85, 'feedback': 'Perbanyak kosa kata'},
    ]
    return render_template('murid/riwayat_tugas.html', riwayat=riwayat, active_menu='riwayat_tugas')


# ============================================
# KEUANGAN (READ ONLY)
# ============================================
@murid_bp.route('/keuangan')
def keuangan():
    pembayaran = [
        {'bulan': 'Januari', 'tahun': 2024, 'nominal': 500000, 'status': 'lunas'},
        {'bulan': 'Februari', 'tahun': 2024, 'nominal': 500000, 'status': 'lunas'},
        {'bulan': 'Maret', 'tahun': 2024, 'nominal': 500000, 'status': 'belum_bayar'},
    ]
    total_tagihan = sum(p['nominal'] for p in pembayaran)
    total_dibayar = sum(p['nominal'] for p in pembayaran if p['status'] == 'lunas')
    
    return render_template('murid/keuangan.html',
                         pembayaran=pembayaran,
                         total_tagihan=total_tagihan,
                         total_dibayar=total_dibayar,
                         sisa=total_tagihan - total_dibayar,
                         active_menu='keuangan')


# ============================================
# PENGUMUMAN (READ ONLY)
# ============================================
@murid_bp.route('/pengumuman')
def pengumuman():
    pengumuman = [
        {'judul': 'Libur Akhir Semester', 'isi': 'Libur akan dimulai tanggal 20 Desember 2024', 'created_at': datetime.now(), 'admin_name': 'Admin'},
        {'judul': 'Pembagian Rapor', 'isi': 'Pembagian rapor akan dilaksanakan tanggal 18 Desember', 'created_at': datetime.now(), 'admin_name': 'Admin'},
    ]
    return render_template('murid/pengumuman.html', pengumuman=pengumuman, active_menu='pengumuman')


# ============================================
# PENGATURAN
# ============================================
@murid_bp.route('/pengaturan')
def pengaturan():
    return render_template('murid/pengaturan.html', active_menu='pengaturan')


# ============================================
# PROFIL (CRUD)
# ============================================
@murid_bp.route('/profil', methods=['GET', 'POST'])
def profil():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        kelas = request.form.get('kelas')
        address = request.form.get('address')
        password = request.form.get('password')
        
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                if password and len(password) >= 4:
                    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute("""
                        UPDATE users SET full_name=%s, email=%s, phone=%s, kelas=%s, address=%s, 
                                       password_hash=%s, updated_at=%s WHERE id=%s
                    """, (full_name, email, phone, kelas, address, hashed, datetime.now(), current_user.id))
                else:
                    cursor.execute("""
                        UPDATE users SET full_name=%s, email=%s, phone=%s, kelas=%s, address=%s, updated_at=%s
                        WHERE id=%s
                    """, (full_name, email, phone, kelas, address, datetime.now(), current_user.id))
                conn.commit()
                cursor.close()
                conn.close()
                flash('✅ Profil berhasil diupdate!', 'success')
                return redirect(url_for('murid.profil'))
        except Exception as e:
            print(f"Update profil error: {e}")
            flash('Terjadi kesalahan', 'danger')
    
    return render_template('murid/profil.html',
                         name=current_user.full_name or current_user.username,
                         email=getattr(current_user, 'email', ''),
                         phone=getattr(current_user, 'phone', ''),
                         kelas=getattr(current_user, 'kelas', 'TK A'),
                         nis=getattr(current_user, 'nis', ''),
                         address=getattr(current_user, 'address', ''),
                         active_menu='profil')


__all__ = ['murid_bp']