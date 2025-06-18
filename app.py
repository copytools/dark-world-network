from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session import os import sqlite3 from werkzeug.utils import secure_filename

app = Flask(name) app.secret_key = 'darkworldsupersecretkey'

UPLOAD_FOLDER = 'uploads' ALLOWED_EXTENSIONS = {'zip', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3', 'apk', 'exe'} app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ADMIN_USERNAME = 'admin' ADMIN_PASSWORD = '12345'

def allowed_file(filename): return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/") def index(): search = request.args.get('search') category = request.args.get('filter')

conn = sqlite3.connect('file.db')
c = conn.cursor()

query = "SELECT * FROM files WHERE 1=1"
params = []

if search:
    query += " AND name LIKE ?"
    params.append(f"%{search}%")
if category:
    query += " AND category = ?"
    params.append(category)

c.execute(query, params)
files = c.fetchall()
conn.close()
return render_template("index.html", files=files)

@app.route('/login', methods=['GET', 'POST']) def login(): if request.method == 'POST': user = request.form['username'] pw = request.form['password'] if user == ADMIN_USERNAME and pw == ADMIN_PASSWORD: session['logged_in'] = True return redirect('/upload') else: flash('Invalid credentials') return render_template('login.html')

@app.route('/logout') def logout(): session.pop('logged_in', None) return redirect('/')

@app.route('/upload', methods=['GET', 'POST']) def upload_file(): if not session.get('logged_in'): return redirect('/login')

if request.method == 'POST':
    file = request.files['file']
    category = request.form['category']
    desc = request.form['description']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        conn = sqlite3.connect('file.db')
        c = conn.cursor()
        c.execute("INSERT INTO files (name, category, description, filename, downloads) VALUES (?, ?, ?, ?, 0)",
                  (filename, category, desc, filename))
        conn.commit()
        conn.close()
        flash('File uploaded successfully!')
        return redirect('/')
return render_template('upload.html')

@app.route('/download/int:file_id') def download(file_id): conn = sqlite3.connect('file.db') c = conn.cursor() c.execute("SELECT * FROM files WHERE id=?", (file_id,)) file = c.fetchone() if file: filename = file[4] c.execute("UPDATE files SET downloads = downloads + 1 WHERE id=?", (file_id,)) conn.commit() conn.close() return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True) return "File not found", 404

if name == 'main': if not os.path.exists('uploads'): os.makedirs('uploads') app.run(debug=True)

