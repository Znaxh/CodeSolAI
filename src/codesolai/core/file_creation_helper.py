"""
File Creation Helper for CodeSolAI
Provides templates and utilities for creating complete, functional files
"""

from typing import Dict, List, Optional, Any


class FileCreationHelper:
    """Helper class for creating complete, functional files with proper content"""

    def __init__(self):
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Dict[str, str]]:
        """Load file templates for different project types"""

        flask_app_py = """from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

def init_db():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if not username or not email or not password:
            flash('All fields are required')
            return render_template('register.html')

        password_hash = generate_password_hash(password)

        try:
            conn = sqlite3.connect('app.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            flash('Login successful!')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)"""

        base_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Flask App{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">Flask App</a>
            <div class="navbar-nav ms-auto">
                {% if session.user_id %}
                    <a class="nav-link" href="{{ url_for('dashboard') }}">Dashboard</a>
                    <a class="nav-link" href="{{ url_for('logout') }}">Logout</a>
                {% else %}
                    <a class="nav-link" href="{{ url_for('login') }}">Login</a>
                    <a class="nav-link" href="{{ url_for('register') }}">Register</a>
                {% endif %}
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-info alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}

        {% block content %}{% endblock %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""

        index_html = """{% extends "base.html" %}

{% block title %}Home - Flask App{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8 mx-auto">
        <div class="jumbotron bg-light p-5 rounded">
            <h1 class="display-4">Welcome to Flask App!</h1>
            <p class="lead">A simple web application with user authentication.</p>
            {% if not session.user_id %}
                <hr class="my-4">
                <p>Get started by creating an account or logging in.</p>
                <a class="btn btn-primary btn-lg" href="{{ url_for('register') }}" role="button">Register</a>
                <a class="btn btn-outline-primary btn-lg" href="{{ url_for('login') }}" role="button">Login</a>
            {% else %}
                <hr class="my-4">
                <p>Welcome back, {{ session.username }}!</p>
                <a class="btn btn-primary btn-lg" href="{{ url_for('dashboard') }}" role="button">Go to Dashboard</a>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}"""

        login_html = """{% extends "base.html" %}

{% block title %}Login - Flask App{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-6 mx-auto">
        <div class="card">
            <div class="card-header">
                <h3>Login</h3>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Login</button>
                    <a href="{{ url_for('register') }}" class="btn btn-link">Don't have an account? Register</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""

        register_html = """{% extends "base.html" %}

{% block title %}Register - Flask App{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-6 mx-auto">
        <div class="card">
            <div class="card-header">
                <h3>Register</h3>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary">Register</button>
                    <a href="{{ url_for('login') }}" class="btn btn-link">Already have an account? Login</a>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""

        dashboard_html = """{% extends "base.html" %}

{% block title %}Dashboard - Flask App{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-8 mx-auto">
        <h2>Welcome to your Dashboard, {{ username }}!</h2>
        <p class="lead">You are successfully logged in.</p>

        <div class="card mt-4">
            <div class="card-header">
                <h4>Account Information</h4>
            </div>
            <div class="card-body">
                <p><strong>Username:</strong> {{ username }}</p>
                <p><strong>Status:</strong> <span class="badge bg-success">Active</span></p>
                <hr>
                <a href="{{ url_for('logout') }}" class="btn btn-outline-danger">Logout</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}"""

        return {
            "flask_web_app": {
                "app.py": flask_app_py,
                "requirements.txt": "Flask==2.3.3\nWerkzeug==2.3.7",
                "templates/base.html": base_html,
                "templates/index.html": index_html,
                "templates/login.html": login_html,
                "templates/register.html": register_html,
                "templates/dashboard.html": dashboard_html
            }
        }

    def get_project_files(self, project_type: str) -> Dict[str, str]:
        """Get all files for a specific project type"""
        return self.templates.get(project_type, {})

    def generate_file_creation_tasks(self, project_type: str, base_path: str = ".") -> List[Dict[str, str]]:
        """Generate task list for creating all files in a project"""
        project_files = self.get_project_files(project_type)
        tasks = []

        for file_path, content in project_files.items():
            full_path = f"{base_path}/{file_path}" if base_path != "." else file_path

            tasks.append({
                "name": f"Create {file_path}",
                "description": f"Create the {file_path} file with complete implementation",
                "file_path": full_path,
                "content": content.strip()
            })

        return tasks

    def get_supported_project_types(self) -> List[str]:
        """Get list of supported project types"""
        return list(self.templates.keys())