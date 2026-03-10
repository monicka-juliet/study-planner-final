from flask import Flask, request, redirect, session, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import re
from datetime import datetime, timedelta
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.secret_key = 'study2026-super-secure-key-change-this-in-production'

# Create necessary folders
os.makedirs('static/uploads', exist_ok=True)

# Initialize SQLite Database
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

# Email Configuration - UPDATE THESE WITH YOUR GMAIL
GMAIL_USER = "your-gmail@gmail.com"  # Change this to your Gmail
GMAIL_PASS = "your-16-digit-app-password"  # Gmail App Password (not regular password)

def is_valid_email(email):
    """Validate Gmail format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@gmail.com$'
    return re.match(pattern, email.lower())

def send_verification_email(email, name):
    """Send verification email after registration"""
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = email
        msg['Subject'] = "✅ Account Created - Study Planner"
        body = f"""
Hi {name},

Your Study Planner account has been created successfully!

Login with:
Email: {email}
Password: (the one you set)

Start studying! 📚✨

Study Planner Team
        """
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email send failed: {e}")
        return False

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        action = request.form.get('action', 'login')
        email = request.form['email'].lower().strip()
        password = request.form['password'].strip()
        
        # Validate Gmail format
        if not is_valid_email(email):
            error = "❌ Please use a valid Gmail address only!"
        else:
            conn = get_db_connection()
            c = conn.cursor()
            
            if action == 'register':
                # Check if email already exists
                c.execute("SELECT email FROM users WHERE email=?", (email,))
                if c.fetchone():
                    error = "❌ This Gmail is already registered!"
                else:
                    # Create user with generated name
                    name = email.split('@')[0].title()
                    hashed_pw = generate_password_hash(password)
                    c.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", 
                             (email, hashed_pw, name))
                    conn.commit()
                    
                    # Send welcome email
                    send_verification_email(email, name)
                    
                    session['logged_in'] = True
                    session['email'] = email
                    session['name'] = name
                    conn.close()
                    return redirect('/dashboard')
            
            elif action == 'login':
                c.execute("SELECT * FROM users WHERE email=?", (email,))
                user = c.fetchone()
                conn.close()
                
                if user:
                    if check_password_hash(user['password'], password):
                        session['logged_in'] = True
                        session['email'] = email
                        session['name'] = user['name']
                        return redirect('/dashboard')
                    else:
                        error = "❌ Wrong password!"
                else:
                    error = "❌ Gmail not registered! Register first."
    
    return render_login_page(error)
    
def render_login_page(error=""):
    demo_email = "test@gmail.com"  # Fixed demo email
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Study Planner & Reminder App</title>
        <style>
            *{{margin:0;padding:0;box-sizing:border-box}}
            body{{font-family:'Segoe UI',Arial,sans-serif;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}}
            .login-box{{background:white;color:#333;padding:50px;border-radius:20px;box-shadow:0 20px 40px rgba(0,0,0,0.2);width:100%;max-width:420px}}
            .tabs{{display:flex;background:#f8f9fa;border-radius:12px;overflow:hidden;margin:30px 0}}
            .tab{{flex:1;padding:18px 10px;text-align:center;cursor:pointer;font-weight:600;transition:all 0.3s;font-size:16px}}
            .tab.active{{background:#667eea;color:white}}
            input{{width:100%;padding:15px;margin:10px 0;font-size:16px;border:2px solid #e1e5e9;border-radius:12px;box-sizing:border-box;transition:all 0.3s}}
            input:focus{{border-color:#667eea;outline:none;box-shadow:0 0 0 3px rgba(102,126,234,0.1)}}
            button{{width:100%;padding:16px;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);color:white;border:none;border-radius:12px;font-size:18px;font-weight:600;cursor:pointer;transition:all 0.3s;margin:5px 0}}
            button:hover{{transform:translateY(-2px);box-shadow:0 10px 25px rgba(102,126,234,0.4)}}
            .error{{background:#fee;color:#c53030;padding:12px;border-radius:8px;margin:15px 0;font-weight:500}}
            .demo{{text-align:center;margin-top:25px;font-size:14px;color:#666;padding:15px;background:#f8f9fa;border-radius:8px}}
            h1{{text-align:center;margin-bottom:30px;font-size:32px;color:#333}}
            .tabs-container{{margin:25px 0}}
            .gmail-only{{background:#e8f4fd;padding:10px;border-radius:8px;margin:10px 0;font-size:14px;color:#1976d2;font-weight:500}}
        </style>
    </head>
    <body>
        <div class="login-box">
            <h1>🎓 Study Planner</h1>
            <div class="gmail-only">📧 Gmail addresses only allowed</div>
            {f'<div class="error">{error}</div>' if error else ''}
            
            <div class="tabs-container">
                <div class="tabs">
                    <div class="tab active" onclick="showTab('login')">🔐 Login</div>
                    <div class="tab" onclick="showTab('register')">➕ Register</div>
                </div>
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
                <input type="password" name="password" placeholder="Create Password" required minlength="6">
                <button type="submit">Create Account</button>
            </form>
            
            <div class="demo">
                Demo: {demo_email} / 123456
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

# Add demo user if not exists (run once)
def create_demo_user():
    conn = get_db_connection()
    c = conn.cursor()
    demo_email = "test@gmail.com"
    demo_pass = generate_password_hash("123456")
    c.execute("SELECT email FROM users WHERE email=?", (demo_email,))
    if not c.fetchone():
        c.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)", 
                 (demo_email, demo_pass, "Test"))
        conn.commit()
    conn.close()

create_demo_user()

# Rest of your code remains the same...
# [Include all other routes from dashboard onwards - they are unchanged]

def check_notifications():
    conn = get_db_connection()
    c = conn.cursor()
    email = session.get('email', '')
    now = datetime.now()
    
    c.execute("SELECT * FROM reminders WHERE email=? AND datetime(deadline) <= datetime(?)", 
              (email, now.isoformat()))
    overdue = c.fetchall()
    
    notifications = ""
    for reminder in overdue:
        # Email notification
        send_email(email, "🚨 Study Reminder - OVERDUE", 
                  f"Your reminder '{reminder['title']}' was due at {reminder['deadline']}!")
        notifications += f'<div class="notification">🚨 <strong>{reminder["title"]}</strong> - Deadline Passed!</div>'
    
    conn.close()
    return notifications

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        return False

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'): 
        return redirect('/')
    
    notifications = check_notifications()
    
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
            h2{{font-size:24px;margin-bottom:40px;opacity:0.9}}
            .btn{{display:inline-block;padding:22px 45px;margin:15px;background:linear-gradient(135deg,#f093fb 0%,#f5576c 100%);color:white;text-decoration:none;border-radius:20px;font-size:22px;font-weight:600;box-shadow:0 12px 30px rgba(0,0,0,0.3);transition:all 0.3s;position:relative;overflow:hidden}}
            .btn:hover{{transform:translateY(-5px);box-shadow:0 20px 40px rgba(0,0,0,0.4)}}
            .btn.logout{{background:linear-gradient(135deg,#e74c3c,#c0392b)}}
            .notification{{background:rgba(231,76,60,0.9);padding:20px;border-radius:15px;margin:20px auto;font-size:20px;max-width:600px;box-shadow:0 10px 30px rgba(231,76,60,0.4)}}
            .welcome-card{{background:rgba(255,255,255,0.15);padding:40px;border-radius:25px;margin-bottom:40px;backdrop-filter:blur(15px);box-shadow:0 20px 40px rgba(0,0,0,0.2)}}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="welcome-card">
                <h1>Welcome {session['name']}! 🎓</h1>
                <h2>Study Planner & Reminder App</h2>
                {notifications}
            </div>
            <a href="/study" class="btn">📚 Study Dashboard</a>
            <a href="/goals" class="btn">🎯 Set Goal</a>
            <a href="/view-goals" class="btn">📊 View Goals</a>
            <a href="/reminders" class="btn">⏰ Reminders</a>
            <a href="/logout" class="btn logout">🚪 Logout</a>
        </div>
    </body>
    </html>
    '''

# [Include all other routes - study, goals, reminders, etc. They remain unchanged]
# Just paste the rest of your original routes here...

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
