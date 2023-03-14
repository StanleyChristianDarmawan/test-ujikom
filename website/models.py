from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Masyarakat(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nik = db.Column(db.String(16))
    nama = db.Column(db.String(35))
    username = db.Column(db.String(25))
    password = db.Column(db.String(32))
    telp = db.Column(db.String(13))
    isi_laporan_masyarakat = db.relationship('Pengaduan')
    
class Pengaduan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tgl_pengaduan = db.Column(db.DateTime(timezone=True), default=func.now())
    nik = db.Column(db.String, db.ForeignKey('masyarakat.nik'))
    isi_laporan_pengaduan = db.Column(db.String(200))
    foto = db.Column(db.String(255))
    status = db.Column(db.String(7))

class Petugas(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nama_petugas = db.Column(db.String(35))
    username = db.Column(db.String(25))
    password = db.Column(db.String(32))
    telp = db.Column(db.String(13))
    level = db.Column(db.String(7))

class Tanggapan(db.Model):
    id_tanggapan = db.Column(db.Integer, primary_key=True)
    id_pengaduan = db.Column(db.Integer, db.ForeignKey('pengaduan.id'))
    tgl_tanggapan = db.Column(db.DateTime(timezone=True), default=func.now())
    tanggapan = db.Column(db.String(200))
    id_petugas = db.Column(db.Integer, db.ForeignKey('petugas.id'))