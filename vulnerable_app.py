from flask import Flask, request, render_template_string, session, redirect, url_for
import sqlite3
import os
import hashlib

app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# CORRECCIÓN (hallazgos ZAP): se agregan las cabeceras de seguridad que ZAP 
# reportó como ausentes, en todas las respuestas de la aplicación.
@app.after_request
def set_security_headers(response):
    # Medium - Content Security Policy (CSP) Header Not Set
    # Política restrictiva: solo permite recursos del propio origen.
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )

    # Medium - Missing Anti-clickjacking Header
    response.headers['X-Frame-Options'] = 'DENY'

    # Low - X-Content-Type-Options Header Missing
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Low - Cross-Origin-Opener-Policy Header Missing or Invalid
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'

    # Low - Cross-Origin-Embedder-Policy Header Missing or Invalid
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'

    # Low - Cross-Origin-Resource-Policy Header Missing or Invalid
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'

    # Low - Permissions Policy Header Not Set
    # Deshabilita el acceso a APIs sensibles del navegador que la app no usa.
    response.headers['Permissions-Policy'] = (
        "geolocation=(), microphone=(), camera=(), payment=(), usb=()"
    )

    # Low - Server Leaks Version Information via "Server" HTTP Response Header
    # El servidor de desarrollo de Werkzeug agrega "Server: Werkzeug/x Python/x".
    # Se sobreescribe con un valor genérico para no revelar versiones exactas.
    response.headers['Server'] = 'WebServer'

    # Informational - Storable and Cacheable Content
    # Las respuestas contienen datos de sesión/tareas de usuario: 
    # se evita que queden cacheadas por proxies o el propio navegador.
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response


@app.route('/')
def index():
    return 'Welcome to the Task Manager Application!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()

        # CORRECCIÓN CWE-89: INYECCIÓN SQL
        # Se elimina la concatenación insegura (f-strings).
        # Se utiliza exclusivamente la consulta parametrizada con placeholders (?)
        query = "SELECT * FROM users WHERE username = ? AND password = ?"
        hashed_password = hash_password(password)

        # Ejecución segura de la consulta
        user = conn.execute(query, (username, hashed_password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials!'
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    conn = get_db_connection()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()

    return render_template_string('''
        <h1>Welcome, user {{ user_id }}!</h1>
        <form action="/add_task" method="post">
            <input type="text" name="task" placeholder="New task"><br>
            <input type="submit" value="Add Task">
        </form>
        <h2>Your Tasks</h2>
        <ul>
        {% for task in tasks %}
            <li>
                {{ task['task'] }}

                <!--CORRECCIÓN: Ahora la eliminación se hace a través de una petición POST-->
                <form action="/delete_task/{{ task['id'] }}" method="post" style="display:inline;">
                    <input type="submit" value="Delete">
                </form>
            </li>
        {% endfor %}
        </ul>
    ''', user_id=user_id, tasks=tasks)


@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    task = request.form['task']
    user_id = session['user_id']

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO tasks (user_id, task) VALUES (?, ?)", (user_id, task))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))


@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()

    # CORRECCIÓN: La tarea se elimina si pertenece al usuario autenticado
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, session['user_id']))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('dashboard'))


@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    return 'Welcome to the admin panel!'


if __name__ == '__main__':
    # CORRECCIÓN CWE-94: debug=True
    # Se desactiva el modo debug para entornos de producción
    app.run(debug=False)