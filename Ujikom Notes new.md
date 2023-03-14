## Struktur Folder dan File:
website~
	static~
	templates~
		admin~
			base.html
			dashboard_0.html
			dashboard_proses.html
			dashboard_selesai.html
			tanggapan.html
			generate_pdf.html
			pdf_template.html
			register_petugas.html
			manajemen_petugas.html
		base.html
		home.html
		login.html
		register.html
	__init__.py
	auth.py
	models.py
	views.py
main.py

---
## Steps:
- [ ] Activate Virtual Env (PengaduanMasyarakat_env\\Scripts\\activate)
- [ ] Create files and folders structure
- [ ] Models
- [ ] auth
- [ ] views
- [ ] templates

---
## Reminders
Jinja templating engine
![[1200px-Jinja_logo.png|500]]
base template define example
{% block title %}{% endblock %}

template call:
{% extends 'base.html' %}
{% block title %}Home{% endblock %}


## Contoh code template:
main.py
```python
from website import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
```

__init__.py
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "pengaduan_masyarakat.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'asokdasdkad bfaefa'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import Masyarakat, Pengaduan, Petugas, Tanggapan

    with app.app_context():

        db.create_all()

        print('Created Database')

  
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Masyarakat.query.get(int(id))

    return app
```

models.py example
```python
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Mobil(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    warna = db.Column(db.String(16))
    merk = db.Column(db.String(35))
    type_mobil = db.Column(db.String(25))
    jenis_rangka = db.Column(db.String(32))
    jenis_ban = db.Column(db.String(13))
    nomor_rangka = db.relationship('Pengaduan')

class Pabrik(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tgl_berdiri = db.Column(db.DateTime(timezone=True), default=func.now())
    merk = db.Column(db.String, db.ForeignKey('mobil.merk'))
    alamat = db.Column(db.String(200))
    foto = db.Column(db.String(255))
    status = db.Column(db.String(7))
```

```python
<link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css">
<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"
crossorigin="anonymous" />
```

```python
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
```
```python
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
```