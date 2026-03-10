from flask import Flask, request, redirect, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'study2026-super-secure-key-change-this-in-production'

# Create folders
os.makedirs('static/uploads', exist_ok=True)

# Initialize Database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (email TEXT PRIMARY KEY, password TEXT, name TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS goals 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  email TEXT, subject TEXT, goal TEXT, 
                  target_score INTEGER, study_hours TEXT, 
                  progress INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reminders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  email TEXT, title TEXT, deadline TEXT)''')
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def is_valid_email(email):
    """Only Gmail addresses allowed"""
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail.com$'
    return bool(re.match(pattern, email.lower()))

def create_demo_user():
    conn = get_db_connection()
    c = conn.cursor()
    demo_email = "test@gmail.com"
    demo_pass = generate_password_hash("123456")
    c.execute("SELECT email FROM users WHERE email=?", (demo_email,))
    if not c.fetchone():
        c.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", 
                 (demo_email, demo_pass, "Demo User"))
        conn.commit()
    conn.close()

create_demo_user()

@app.route('/', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        action = request.form.get('action', 'login')
        email = request.form['email'].lower().strip()
        password = request.form['password'].strip()
        
        # STRICT VALIDATION - Only Gmail
        if not is_valid_email(email):
            error = "❌ Only Gmail addresses allowed!"
        else:
            conn = get_db_connection()
            
            if action == 'register':
                # Check if exists
                c = conn.cursor()
                c.execute("SELECT email FROM users WHERE email=?", (email,))
                if c.fetchone():
                    error = "❌ Gmail already registered!"
                else:
                    # Create user
                    name = email.split('@')[0].title()
                    hashed_pw = generate_password_hash(password)
                    c.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", 
                             (email, hashed_pw, name))
                    conn.commit()
                    conn.close()
                    
                    # Login immediately after register
                    session['logged_in'] = True
                    session['email'] = email
                    session['name'] = name
                    return redirect('/dashboard')
            
            elif action == 'login':
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE email=?", (email,))
                user = c.fetchone()
                conn.close()
                
                # STRICT PASSWORD CHECK
                if user and check_password_hash(user['password'], password):
                    session['logged_in'] = True
                    session['email'] = email
                    session['name'] = user['name']
                    return redirect('/dashboard')
                else:
                    error = "❌ Wrong Gmail or Password!"
    
    return render_login_page(error)

def render_login_page(error=""):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Study Planner - Login</title>
        <style>
            *{{margin:0;padding:0;box-sizing:border-box}}
            body{{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center}}
            .login-box{{background:white;color:#333;padding:50px;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.2);width:100%;max-width:420px}}
            .tabs{{display:flex;background:#f8f9fa;border-radius:12px;overflow:hidden;margin:30px 0}}
            .tab{{flex:1;padding:18px 10px;text-align:center;cursor:pointer;font-weight:600;transition:all 0.3s}}
            .tab.active{{background:#667eea;color:white}}
            input{{width:100%;padding:15px;margin:10px 0;border:2px solid #e1e5e9;border-radius:12px;font-size:16px;transition:all 0.3s}}
            input:focus{{border-color:#667eea;outline:none;box-shadow:0 0 0 3px rgba(102,126,234,0.1)}}
            button{{width:100%;padding:16px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;border-radius:12px;font-size:18px;font-weight:600;cursor:pointer;transition:all 0.3s}}
            button:hover{{transform:translateY(-2px);box-shadow:0 10px 25px rgba(102,126,234,0.4)}}
            .error{{background:#fee;color:#c53030;padding:15px;border-radius:10px;margin:15px 0;font-weight:500}}
            h1{{text-align:center;margin-bottom:30px;font-size:32px}}
            .demo{{text-align:center;margin-top:25px;font-size:14px;color:#666;padding:15px;background:#f8f9fa;border-radius:8px}}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>🎓 Study Planner</h1>
            <div style="background:#e8f4fd;padding:10px;border-radius:8px;margin-bottom:20px;font-weight:500;color:#1976d2">
                📧 Gmail addresses only
            </div>
            {f'<div class="error">{error}</div>' if error else ''}
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('login')">🔐 Login</div>
                <div class="tab" onclick="showTab('register')">➕ Register</div>
            </div>
            
            <form method="POST" id="login-form">
                <input type="hidden" name="action" value="login">
                <input type="email" name="email" placeholder="your-email@gmail.com" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            
            <form method="POST" id="register-form" style="display:none">
                <input type="hidden" name="action" value="register">
                <input type="email" name="email" placeholder="your-email@gmail.com" required>
                <input type="password" name="password" placeholder="Create Password (6+ chars)" required minlength="6">
                <button type="submit">Create Account</button>
            </form>
            
            <div class="demo">
                💡 Demo: test@gmail.com / 123456
            </div>
        </div>
        <script>
        function showTab(tab) {{
            document.getElementById('login-form').style.display = tab === 'login' ? 'block' : 'none';
            document.getElementById('register-form').style.display = tab === 'register' ? 'block' : 'none';
            document.querySelectorAll('.tab')[0].classList.toggle('active', tab === 'login');
            document.querySelectorAll('.tab')[1].classList.toggle('active', tab === 'register');
        }}
        </script>
    </body>
    </html>
    '''

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'): 
        return redirect('/')
    
    conn = get_db_connection()
    c = conn.cursor()
    email = session['email']
    
    # Get user goals count
    c.execute("SELECT COUNT(*) FROM goals WHERE email=?", (email,))
    goals_count = c.fetchone()[0]
    
    # Get reminders count
    c.execute("SELECT COUNT(*) FROM reminders WHERE email=?", (email,))
    reminders_count = c.fetchone()[0]
    
    conn.close()
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - Study Planner</title>
        <style>
            *{{margin:0;padding:0;box-sizing:border-box}}
            body{{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;min-height:100vh;padding:30px}}
            .container{{max-width:1000px;margin:0 auto;text-align:center}}
            h1{{font-size:42px;margin-bottom:10px;text-shadow:0 2px 10px rgba(0,0,0,0.3)}}
            .stats{{display:flex;justify-content:center;gap:30px;margin:40px 0;flex-wrap:wrap}}
            .stat-card{{background:rgba(255,255,255,0.15);padding:30px;border-radius:20px;min-width:200px;flex:1;max-width:250px;backdrop-filter:blur(15px)}}
            .stat-number{{font-size:48px;font-weight:bold;color:#f093fb}}
            .btn{{display:inline-block;padding:20px 40px;margin:15px;background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);color:white;text-decoration:none;border-radius:20px;font-size:20px;font-weight:600;box-shadow:0 12px 30px rgba(0,0,0,0.3);transition:all 0.3s}}
            .btn:hover{{transform:translateY(-5px);box-shadow:0 20px 40px rgba(0,0,0,0.4)}}
            .btn.logout{{background:linear-gradient(135deg,#e74c3c,#c0392b)}}
            .welcome-card{{background:rgba(255,255,255,0.15);padding:40px;border-radius:25px;margin-bottom:40px;backdrop-filter:blur(15px)}}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="welcome-card">
                <h1>Hi {session['name']}! 🎓</h1>
                <p style="font-size:24px;opacity:0.9">Your Study Dashboard</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{goals_count}</div>
                    <div style="font-size:18px;margin-top:10px">Goals Set</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{reminders_count}</div>
                    <div style="font-size:18px;margin-top:10px">Reminders</div>
                </div>
            </div>
            
            <a href="/study" class="btn">📚 Study Now</a>
            <a href="/goals" class="btn">🎯 Add Goal</a>
            <a href="/view-goals" class="btn">📊 My Goals</a>
            <a href="/reminders" class="btn">⏰ Reminders</a>
            <a href="/logout" class="btn logout">🚪 Logout</a>
        </div>
    </body>
    </html>
    '''

# PROTECTED ROUTES - Only logged in users
@app.route('/study')
@app.route('/goals')
@app.route('/view-goals')
@app.route('/reminders')
def protected_routes():
    if not session.get('logged_in'):
        return redirect('/')
    return f'<h1>{request.path[1:].replace("-"," ").title()}</h1><a href="/dashboard">← Back</a> (Coming Soon!)'

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
