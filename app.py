# ADD THESE GLOBAL VARIABLES AT THE TOP (after Gmail credentials)
ADMIN_EMAIL = "admin@yourdomain.com"  # Your admin notification email

@app.route('/', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        action = request.form.get('action', 'login')
        email = request.form['email'].lower().strip()
        password = request.form['password'].strip()

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            error = "❌ Please enter a valid email address!"
            return render_login_page(error)

        conn = get_db_connection()
        c = conn.cursor()

        if action == 'register':
            c.execute("SELECT email FROM users WHERE email=?", (email,))
            if c.fetchone():
                error = "❌ Email already registered!"
            else:
                name = email.split('@')[0].title()
                hashed_pw = generate_password_hash(password)
                c.execute("INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
                         (email, hashed_pw, name))
                conn.commit()
                
                # Send welcome email
                welcome_msg = f"""
Hi {name},

Welcome to Study Planner! 🎓

Your account has been created successfully.
Email: {email}

Start planning your studies now!

Best regards,
Study Planner Team
"""
                send_email(email, "🎓 Welcome to Study Planner!", welcome_msg)
                
                # ADMIN NOTIFICATION FOR NEW REGISTRATION
                admin_msg = f"""
🎓 NEW USER REGISTERED - Study Planner

Email: {email}
Name: {name}
Registration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

New student joined the platform!
"""
                send_email(ADMIN_EMAIL, "🎓 New User Registration", admin_msg)
                
                session['logged_in'] = True
                session['email'] = email
                session['name'] = name
                conn.close()
                return redirect('/dashboard')

        elif action == 'login':
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            user = c.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['logged_in'] = True
                session['email'] = email
                session['name'] = user['name']
                conn.close()
                return redirect('/dashboard')
            else:
                # **ENHANCED RECOVERY + ADMIN NOTIFICATION SYSTEM**
                recovery_msg = f"""
🔐 ACCOUNT RECOVERY - Study Planner

Someone tried to login to your account (possibly you):
Email: {email}
Attempt Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

⚠️ LOGIN FAILED - Wrong password or non-existent account

ACTIONS AVAILABLE:
1. If this was YOU: Go to app and use correct password
2. If this was NOT you: Your account is still SECURE

LOGIN LINK (valid for 15 mins):
http://yourdomain.com/recover?email={email}

Study Planner Team
"""
                
                # Always send user notification
                send_email(email, "🔐 Login Attempt - Action Required", recovery_msg)
                
                # ADMIN NOTIFICATION (always sent)
                admin_login_msg = f"""
🚨 LOGIN ATTEMPT ALERT - Study Planner ADMIN

LOGIN ATTEMPT DETAILS:
Email: {email}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
IP: {request.remote_addr}
User Agent: {request.headers.get('User-Agent')}
SUCCESS: {'NO' if user is None or not check_password_hash(user['password'], password) else 'YES'}

ACTIONS:
1. Monitor suspicious activity
2. User has been notified with recovery link
"""
                send_email(ADMIN_EMAIL, "🚨 Login Attempt Detected", admin_login_msg)
                
                error = "❌ Login failed! Check your email for recovery instructions."
                conn.close()

    return render_login_page(error)
