from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "secret-key"
DB = "trainer.db"

app.config['ADMIN_EMAIL'] = 'admin@site.com'
app.config['ADMIN_PASSWORD'] = 'admin123'

safe_builtins = {
    "len": len, "sum": sum, "range": range, "min": min,
    "max": max, "abs": abs, "str": str, "int": int,
    "float": float, "bool": bool, "list": list
}

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT,
        email TEXT UNIQUE,
        group_name TEXT,
        password TEXT,
        role TEXT DEFAULT 'student'
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS chapters(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chapter_id INTEGER,
        title TEXT,
        question TEXT,
        function_name TEXT,
        starter_code TEXT,
        tests TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS submissions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        task_id INTEGER,
        code TEXT,
        status TEXT
    )
    """)

    admin = conn.execute("SELECT * FROM users WHERE email=?", (app.config['ADMIN_EMAIL'],)).fetchone()
    if not admin:
        conn.execute(
            "INSERT INTO users(fullname,email,group_name,password,role) VALUES(?,?,?,?,?)",
            ('Administrator', app.config['ADMIN_EMAIL'], 'Admins', generate_password_hash(app.config['ADMIN_PASSWORD']), 'admin')
        )

    chapter = conn.execute("SELECT * FROM chapters").fetchone()
    if not chapter:
        conn.execute("INSERT INTO chapters(title) VALUES(?)", ('Глава 1. Основы Python',))
        chapter_id = conn.execute("SELECT id FROM chapters LIMIT 1").fetchone()['id']
        conn.execute(
            "INSERT INTO tasks(chapter_id,title,question,function_name,starter_code,tests) VALUES(?,?,?,?,?,?)",
            (chapter_id, 'Квадрат числа', 'Напишите функцию square(n), которая возвращает квадрат числа.', 'square', 'def square(n):\n    return n*n', '[(2,4),(5,25)]')
        )

    conn.commit()
    conn.close()

init_db()

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Нет доступа')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return wrapper

def get_chapters():
    conn = db()
    chapters = conn.execute("SELECT * FROM chapters").fetchall()
    data = []
    for ch in chapters:
        tasks = conn.execute("SELECT * FROM tasks WHERE chapter_id=?", (ch['id'],)).fetchall()
        data.append({'id': ch['id'], 'title': ch['title'], 'tasks': tasks})
    conn.close()
    return data


def get_task(task_id):
    conn = db()
    task = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.close()
    return task


def check_solution(code, task):
    try:
        env = {"__builtins__": safe_builtins}
        local = {}
        exec(code, env, local)
        func = local.get(task['function_name'])

        if not func:
            return False, 'Функция не найдена'

        tests = eval(task['tests'])
        for test_input, expected in tests:
            result = func(*test_input) if isinstance(test_input, tuple) else func(test_input)
            if result != expected:
                return False, f'Ожидалось {expected}, получено {result}'

        return True, 'Все тесты пройдены'
    except Exception as e:
        return False, str(e)

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', chapters=get_chapters(), user=session)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = db()
        try:
            conn.execute(
                "INSERT INTO users(fullname,email,group_name,password,role) VALUES(?,?,?,?,?)",
                (
                    request.form['fullname'],
                    request.form['email'],
                    request.form['group'],
                    generate_password_hash(request.form['password']),
                    'student'
                )
            )
            conn.commit()
            flash('Регистрация успешна')
            return redirect(url_for('login'))
        except:
            flash('Пользователь уже существует')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = db()
        user = conn.execute('SELECT * FROM users WHERE email=?', (request.form['email'],)).fetchone()
        conn.close()

        if user and check_password_hash(user['password'], request.form['password']):
            session['user_id'] = user['id']
            session['fullname'] = user['fullname']
            session['role'] = user['role']
            return redirect(url_for('home'))

        flash('Неверный логин или пароль')

    return render_template('login.html')

@app.route('/chapter/<int:chapter_id>')
def chapter(chapter_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = db()
    chapter = conn.execute('SELECT * FROM chapters WHERE id=?', (chapter_id,)).fetchone()
    tasks = conn.execute('SELECT * FROM tasks WHERE chapter_id=?', (chapter_id,)).fetchall()
    conn.close()
    return render_template('chapter.html', chapter=chapter, tasks=tasks)

@app.route('/task/<int:task_id>', methods=['GET', 'POST'])
def task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    task = get_task(task_id)
    result = None

    if request.method == 'POST':
        code = request.form['code']
        ok, result = check_solution(code, task)
        conn = db()
        conn.execute(
            'INSERT INTO submissions(user_id,task_id,code,status) VALUES(?,?,?,?)',
            (session['user_id'], task_id, code, 'Правильно' if ok else 'Ошибка')
        )
        conn.commit()
        conn.close()

    return render_template('task.html', task=task, result=result)

@app.route('/profile')
def profile():
    conn = db()
    results = conn.execute('SELECT * FROM submissions WHERE user_id=?', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('profile.html', results=results)

@app.route('/admin')
@admin_required
def admin_panel():
    conn = db()
    submissions = conn.execute('''
        SELECT submissions.*, users.fullname, tasks.title
        FROM submissions
        JOIN users ON users.id=submissions.user_id
        JOIN tasks ON tasks.id=submissions.task_id
        ORDER BY submissions.id DESC
    ''').fetchall()
    conn.close()

    html = '<h1>Админ-панель</h1><a href="/admin/chapter/add">Добавить главу</a> | <a href="/admin/task/add">Добавить задание</a><hr>'
    for s in submissions:
        html += f"<p><b>{s['fullname']}</b> → {s['title']} : {s['status']}</p><pre>{s['code']}</pre><hr>"
    return html

@app.route('/admin/chapter/add', methods=['GET', 'POST'])
@admin_required
def add_chapter():
    if request.method == 'POST':
        conn = db()
        conn.execute('INSERT INTO chapters(title) VALUES(?)', (request.form['title'],))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_panel'))
    return '''<form method="post"><input name="title" placeholder="Название главы"><button>Создать</button></form>'''

@app.route('/admin/task/add', methods=['GET', 'POST'])
@admin_required
def add_task():
    conn = db()
    chapters = conn.execute('SELECT * FROM chapters').fetchall()

    if request.method == 'POST':
        conn.execute(
            'INSERT INTO tasks(chapter_id,title,question,function_name,starter_code,tests) VALUES(?,?,?,?,?,?)',
            (
                request.form['chapter_id'],
                request.form['title'],
                request.form['question'],
                request.form['function_name'],
                request.form['starter_code'],
                request.form['tests']
            )
        )
        conn.commit()
        conn.close()
        return redirect(url_for('admin_panel'))

    options = ''.join([f"<option value='{c['id']}'>{c['title']}</option>" for c in chapters])
    return f'''
    <form method="post">
    <select name="chapter_id">{options}</select><br><br>
    <input name="title" placeholder="Название"><br><br>
    <textarea name="question" placeholder="Описание"></textarea><br><br>
    <input name="function_name" placeholder="Имя функции"><br><br>
    <textarea name="starter_code"></textarea><br><br>
    <textarea name="tests" placeholder="[(2,4),(5,25)]"></textarea><br><br>
    <button>Создать задание</button>
    </form>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
