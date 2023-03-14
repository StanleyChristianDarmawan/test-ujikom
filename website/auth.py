from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import Masyarakat, Petugas
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        session['username'] = request.form['username']

        petugas = Petugas.query.filter_by(username=username).first()
        if petugas:
            if check_password_hash(petugas.password, password):
                flash('Berhasil masuk!', category='success')
                login_user(petugas, remember=True)
                return redirect(url_for('views.admin_dashboard'))
            else:
                flash('Password salah!', category='error')

        masyarakat = Masyarakat.query.filter_by(username=username).first()
        if masyarakat:
            if check_password_hash(masyarakat.password, password):
                flash('Berhasil masuk!', category='success')
                login_user(masyarakat, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Password salah!', category='error')
        else:
            flash('Username tidak ditemukan', category='error')

    return render_template("login.html", user=current_user)
    

@auth.route('/signup', methods=['GET', 'POST'])
def signUp():
    if current_user.is_authenticated:
        return redirect(url_for('views.home'))
    if request.method == 'POST':
        nik = request.form.get('nik')
        nama = request.form.get('nama')
        username = request.form.get('username')
        password = request.form.get('password')
        passwordConf = request.form.get('passwordConf')
        telp = request.form.get('telp')

        session['username'] = request.form['username']

        masyarakat = Masyarakat.query.filter_by(username=username).first()
        petugas = Petugas.query.filter_by(username=username).first()

        if masyarakat or petugas:
            flash('Username sudah terdaftar!', category='error')
        elif len(password) < 7:
            flash('Password harus diatas 7 karakter', category='error')
        elif password != passwordConf:
            flash('Password tidak cocok', category='error')
        else:
            new_masyarakat = Masyarakat(nik=nik, nama=nama, username=username, telp=telp, password=generate_password_hash(password, method='sha256'))
            db.session.add(new_masyarakat)
            db.session.commit()
            login_user(new_masyarakat, remember=True)
            flash('Akun Berhasil dibuat!', category='success')
            return redirect(url_for('views.home'))
    # session.clear()
    return render_template("signUp.html", user=current_user)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("auth.login"))


# ADMIN/PETUGAS AUTH
@auth.route('/signup_admin_petugas', methods=['GET', 'POST'])
def signUp_admin_petugas():
    if request.method == 'POST':
        nama = request.form.get('nama')
        username = request.form.get('username')
        password = request.form.get('password')
        passwordConf = request.form.get('passwordConf')
        telp = request.form.get('telp')

        petugas = Petugas.query.filter_by(username=username).first()
        masyarakat = Masyarakat.query.filter_by(username=username).first()
        if petugas or masyarakat:
            flash('Username sudah terdaftar!', category='error')
        elif len(password) < 7:
            flash('Password harus diatas 7 karakter', category='error')
        else:
            new_petugas = Petugas(nama_petugas=nama, username=username, telp=telp, password=generate_password_hash(password, method='sha256'), level="petugas")
            db.session.add(new_petugas)
            db.session.commit()
            flash('Akun petugas berhasil dibuat!', category='success')
            return redirect(url_for('views.manajemen_petugas'))
    
    return render_template("admin/register_petugas.html", user=current_user)