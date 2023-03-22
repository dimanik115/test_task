import sqlite3
import io
import pandas as pd
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from User_Login import UserLogin

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

def get_dateframe(file):
    df = pd.read_csv (io.StringIO(file['content'].decode('utf-8')), sep=",+")
    return df

def add_db_file(filename, csv):
    conn = get_db_connection()
    cur = conn.cursor()
    binary = sqlite3.Binary(csv)
    cur.execute("INSERT INTO files (name, content) VALUES (?, ?)",
                 (filename, binary))
    conn.commit()
    conn.close()

def add_user(name, email, hash):
    conn = get_db_connection()
    cur = conn.cursor()
    res = cur.execute(f'SELECT COUNT() as `count` FROM users WHERE email LIKE "{email}"').fetchone()
    if res['count'] > 0:
        print('There are such user already')
        return False
    cur.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)", (name, email, hash))
    conn.commit()
    conn.close()
    return True

def get_user_by_email(email):
    conn = get_db_connection()
    res = conn.execute(f'SELECT * FROM users WHERE email = "{email}" LIMIT 1').fetchone()
    conn.close()
    if not res:
        print('User not found')
        return False
    return res
    

app = Flask(__name__)
app.config['SECRET_KEY'] = b'\xb8\xbe<[\xce=\x9a\x9ey^\x8f\xd1\x1e\xf6^\xde'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return UserLogin().fromDB(user_id)

@app.route('/')
def index():
    conn = get_db_connection()
    files = conn.execute('SELECT * FROM files').fetchall()
    conn.close()
    return render_template('index.html', files=files)

@app.route('/<int:file_id>')
@login_required
def file(file_id):
    file = get_file(file_id)
    return render_template('file.html', file=file, df=get_dateframe(file))

@app.route('/<int:file_id>/filter', methods=['POST', 'GET'])
@login_required
def filter(file_id):
    file = get_file(file_id)
    df = get_dateframe(file)
    if request.method == 'POST':
        res = request.form['filter']
        if res:
            try:
                df = df[res.split(',')]
            except KeyError:
                flash('Enter the existing columns, separated by commas')                                 
    return render_template('file.html', file=file, df=df)
    
@app.route('/<int:file_id>/sort', methods=['POST', 'GET'])
@login_required
def sort(file_id):
    file = get_file(file_id)
    df = get_dateframe(file)
    if request.method == 'POST':
        res = request.form['sort']
        if res:
            try:
                columns, str_bool = res.split(' ')
                columns_list = columns.split(',')
                bool_list = [i == "True" for i in str_bool.split(',')]
                df = df.sort_values(columns_list, ascending=bool_list)
            except (KeyError, ValueError) as e:
                flash('Enter the existing columns, separated by commas and True|False, '+
                      'separated by commas for ascending')                                 
    return render_template('file.html', file=file, df=df)
    
@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and check_csv(file.filename):
            csv_file = file.read()
            add_db_file(file.filename, csv_file)
            flash('File is uploaded')
        else:
            flash("Only csv files")
    
    return redirect(url_for('index'))

@app.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    file = get_file(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM files WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(file['name']))
    return redirect(url_for('index'))

@app.route('/login', methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    if request.method == 'POST':
        user = get_user_by_email(request.form['email'])
        if user and check_password_hash(user['psw'], request.form['psw']):
            userlogin = UserLogin().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userlogin, remember=rm)
            return redirect(request.args.get('next') or url_for('profile'))
        flash('pair login/pas is not correct')

    return render_template('login.html')

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        if len(request.form['name']) > 3 and len(request.form['psw']) > 3 \
            and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = add_user(request.form['name'], request.form['email'], hash)
            if res:
                flash("You have successfully signed up", 'success')
                return redirect(url_for('login'))
            else:
                flash('Error on adding to db')
        else:
            flash('The fields are not filled in correctly')
    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are out of the profile')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)