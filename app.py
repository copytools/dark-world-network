from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash, session
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'darkworldsupersecretkey'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'zip', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create DB table if not exists
def init_db():
    conn = sqlite3.connect('file.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            category TEXT,
            description TEXT,
            downloads INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('file.db')
    c = conn.cursor()
    c.execute('SELECT * FROM files ORDER BY id DESC')
    files = c.fetchall()
    conn.close()
    return render_template('index.html', files=files)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            category = request.form.get('category')
            description = request.form.get('description')

            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            conn = sqlite3.connect('file.db')
            c = conn.cursor()
            c.execute('INSERT INTO files (filename, category, description) VALUES (?, ?, ?)',
                      (filename, category, description))
            conn.commit()
            conn.close()

            flash('File uploaded successfully!')
            return redirect(url_for('index'))

    return render_template('upload.html')

@app.route('/download/<int:file_id>')
def download(file_id):
    conn = sqlite3.connect('file.db')
    c = conn.cursor()
    c.execute('SELECT filename FROM files WHERE id = ?', (file_id,))
    result = c.fetchone()
    if result:
        filename = result[0]
        c.execute('UPDATE files SET downloads = downloads + 1 WHERE id = ?', (file_id,))
        conn.commit()
        conn.close()
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    else:
        conn.close()
        flash('File not found')
        return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # simple admin login system
        if username == 'admin' and password == 'dark123':
            session['username'] = username
            return redirect(url_for('upload'))
        else:
            flash('Invalid credentials')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/filter')
def filter_category():
    category = request.args.get('category')
    conn = sqlite3.connect('file.db')
    c = conn.cursor()
    c.execute('SELECT * FROM files WHERE category = ? ORDER BY id DESC', (category,))
    files = c.fetchall()
    conn.close()
    return render_template('index.html', files=files)

if __name__ == '__main__':
    app.run(debug=True)
