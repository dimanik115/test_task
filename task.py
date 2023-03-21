import sqlite3
import pandas as pd
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_file(file_id):
    conn = get_db_connection()
    file = conn.execute('SELECT * FROM files WHERE id = ?',
                        (file_id,)).fetchone()
    conn.close()
    if file is None:
        abort(404)
    return file

def check_csv(filename):
    ext = filename.rsplit('.', 1)[1]
    return ext == 'csv'

def add_db_file(filename, csv, columns):
    conn = get_db_connection()
    cur = conn.cursor()
    binary = sqlite3.Binary(csv)
    cur.execute("INSERT INTO files (name, content, columns) VALUES (?, ?, ?)",
                 (filename, binary, columns.decode('utf-8')))
    conn.commit()
    conn.close()

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xb8\xbe<[\xce=\x9a\x9ey^\x8f\xd1\x1e\xf6^\xde'

@app.route('/')
def index():
    conn = get_db_connection()
    files = conn.execute('SELECT * FROM files').fetchall()
    conn.close()
    return render_template('index.html', files=files)

@app.route('/<int:file_id>')
def file(file_id):
    file = get_file(file_id)
    return render_template('file.html', file=file)

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and check_csv(file.filename):
            columns = file.readline()
            csv_file = file.read()
            add_db_file(file.filename, csv_file, columns)
            flash('File is uploaded')
        else:
            flash("Only csv files")
    
    return redirect(url_for('index'))

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    file = get_file(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM files WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(file['name']))
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)