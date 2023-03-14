from flask import Blueprint, render_template, request, flash, redirect, session, url_for, make_response, Flask
from flask_login import login_required, current_user
from .models import Pengaduan, Masyarakat, Tanggapan, Petugas
from datetime import date
import pdfkit
path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
from . import db
from werkzeug.utils import secure_filename
import os

views = Blueprint('views', __name__)
UPLOAD_FOLDER = 'website\static\data_foto_laporan'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@views.route('/', methods=['GET', 'POST'])   
@login_required
def home():
    user_data = Masyarakat.query.filter_by(username=session['username']).first()
    if user_data:
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        if request.method == 'POST':
            def allowed_file(filename):
                return '.' in filename and \
                    filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            # PHOTO UPLOAD
            file = request.files['foto']
            isi_laporan_pengaduan = request.form.get('laporan')
            foto = request.form.get('foto')
            # if user does not select file, browser also
            # submit a empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect('/')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_pengaduan = Pengaduan(nik=user_data.nik, isi_laporan_pengaduan=isi_laporan_pengaduan, foto=filename, status="0")
                db.session.add(new_pengaduan)
                db.session.commit()
                flash('Laporan berhasil dikirim', category='success')
            else:
                flash('File harus berbentuk png, jpg, jpeg')
            
        laporan = Pengaduan.query.order_by(Pengaduan.id).all()
        aduan_user = Pengaduan.query.filter_by(nik=user_data.nik).all()
        return render_template("home.html", user=current_user, aduan_user=aduan_user)
    else:
        return redirect('/admin_dashboard_0')

# PROSES LAPORAN
@views.route('/admin_dashboard_0', methods=['GET', 'POST'])   
@login_required
def admin_dashboard():
    petugas = Petugas.query.filter_by(username=session['username']).first()
    if petugas:
        data_laporan_0 = Pengaduan.query.filter_by(status="0").all()
        return render_template("admin/dashboard.html", user=current_user, data_laporan_0=data_laporan_0)
    else:
        return redirect('/')

@views.route('/admin_dashboard_proses', methods=['GET', 'POST'])
@login_required
def admin_dashboard_proses():
    petugas = Petugas.query.filter_by(username=session['username']).first()
    if petugas:
        data_laporan_proses = Pengaduan.query.filter_by(status="proses").all()
        return render_template("admin/proses.html", user=current_user, data_laporan_proses=data_laporan_proses)
    else:
        return redirect('/')

@views.route('/admin_dashboard_selesai', methods=['GET', 'POST'])
@login_required
def admin_dashboard_selesai():
    petugas = Petugas.query.filter_by(username=session['username']).first()
    if petugas:
        data_laporan_selesai = Pengaduan.query.filter_by(status="selesai").all()
        data_tanggapan = Tanggapan.query.order_by(Tanggapan.id_tanggapan).all()
        return render_template("admin/selesai.html", user=current_user, data_laporan_selesai=data_laporan_selesai, data_tanggapan=data_tanggapan)
    else:
        return redirect('/')

@views.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete(id):
    try:
        task_to_delete = Pengaduan.query.get_or_404(id)
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/admin_dashboard')
    except:
        return 'Gagal Menghapus Data'

@views.route('/verifikasi/<int:id>', methods=['GET', 'POST'])
@login_required
def verifikasi(id):
    try:
        pengaduan = Pengaduan.query.filter_by(id=id).first()
        pengaduan.status = "proses"
        db.session.commit()
        return redirect('/admin_dashboard_0')
    except:
        return 'Gagal Memverifikasi Data'

@views.route('/tanggapan/<int:id>', methods=['GET', 'POST'])   
@login_required
def tanggapan(id):
    petugas_data = Petugas.query.filter_by(username=session['username']).first()
    pengaduan = Pengaduan.query.filter_by(id=id).first()
    if request.method == 'POST':
        isi_tanggapan = request.form.get('tanggapan')

        # aduan_untuk_ditanggapi = Pengaduan.query.filter_by(id=id).first()
        
        new_tanggapan = Tanggapan(id_pengaduan=id, tanggapan=isi_tanggapan, id_petugas=petugas_data.id)
        db.session.add(new_tanggapan)
        flash('Laporan berhasil dikirim', category='success')

        pengaduan.status = "selesai"
        db.session.commit()
        return redirect(url_for('views.admin_dashboard_proses'))
    # return render_template("admin/tanggapan.html", user=current_user, aduan_untuk_ditanggapi=aduan_untuk_ditanggapi)
    return render_template("admin/tanggapan.html", user=current_user, pengaduan_data=pengaduan)
    # else:
    #     return 'Gagal Memberi Tanggapan'

@views.route('/generate_laporan', methods=['GET', 'POST'])
@login_required
def generate_laporan():
    petugas = Petugas.query.filter_by(username=session['username']).first()
    if petugas:
        if petugas.level == "admin":
            if request.method == "GET":
                return render_template("admin/generatePDF.html", user=current_user)
            if request.method == 'POST':
                tanggal_awal = request.form.get('tanggal_awal')
                tanggal_akhir = request.form.get('tanggal_akhir')

                if tanggal_awal and tanggal_akhir:
                    tanggal_awal_splits = tanggal_awal.split('-')
                    tanggal_awal = int(tanggal_awal_splits[2])
                    bulan_awal = int(tanggal_awal_splits[1])
                    tahun_awal = int(tanggal_awal_splits[0])
                    
                    tanggal_akhir_splits = tanggal_akhir.split('-')
                    tanggal_akhir = int(tanggal_akhir_splits[2])
                    bulan_akhir = int(tanggal_akhir_splits[1])
                    tahun_akhir = int(tanggal_akhir_splits[0])

                    tanggal_pengaduan_awal = date(tahun_awal, bulan_awal, tanggal_awal)
                    tanggal_pengaduan_akhir = date(tahun_akhir, bulan_akhir, tanggal_akhir)
                    data_laporan = Pengaduan.query.filter(Pengaduan.tgl_pengaduan.between(tanggal_pengaduan_awal, tanggal_pengaduan_akhir)).all()

                    rendered = render_template('admin/pdf_template.html', data_laporan=data_laporan)
                    
                    pdfkit.from_string(rendered, "out.pdf", configuration=config)

                    return render_template("admin/pdf_template.html", user=current_user, data_laporan=data_laporan)
                else:
                    flash("Tanggal awal dan tanggal akhir tidak boleh kosong!", category='error')
                    return render_template("admin/generatePDF.html", user=current_user)
        else:
            flash("Dibutuhkan role admin untuk mengakses halaman ini.", category='error')
            return redirect('/admin_dashboard_0')

@views.route('/manajemen_petugas', methods=['GET', 'POST'])
@login_required
def manajemen_petugas():
    petugas = Petugas.query.filter_by(username=session['username']).first()
    if petugas:
        if petugas.level == "admin":
            data_petugas = Petugas.query.order_by(Petugas.id).all()
            return render_template("admin/manajemen_petugas.html", user=current_user, data_petugas=data_petugas)
        else:
            flash("Dibutuhkan role admin untuk mengakses halaman ini.", category='error')
            return redirect('/admin_dashboard_0')
    else:
        return redirect('/')

@views.route('/delete_petugas/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_petugas(id):
    try:
        task_to_delete = Petugas.query.get_or_404(id)
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/manajemen_petugas')
    except:
        return 'Gagal Menghapus Data'
