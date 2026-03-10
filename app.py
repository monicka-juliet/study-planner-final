@app.route('/', methods=['GET', 'POST'])
def login():
    error = ""

    if request.method == 'POST':
        action = request.form.get('action', 'login')
        email = request.form['email'].lower()
        password = request.form['password']

        conn = get_db_connection()
        c = conn.cursor()

        if action == 'register':
            c.execute("SELECT email FROM users WHERE email=?", (email,))
            if c.fetchone():
                error = "❌ Email already registered!"
            else:
                name = email.split('@')[0].title()
                hashed_pw = generate_password_hash(password)

                c.execute(
                    "INSERT INTO users (email, password, name) VALUES (?, ?, ?)",
                    (email, hashed_pw, name)
                )
                conn.commit()

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
                    # Correct password
                    session['logged_in'] = True
                    session['email'] = email
                    session['name'] = user['name']
                    return redirect('/dashboard')
                else:
                    # Wrong password → send email alert
                    send_email(
                        email,
                        "⚠️ Login Attempt Failed",
                        f"""
Someone tried to login to your Study Planner account with a wrong password.

Time: {datetime.now()}

If this was not you, please change your password immediately.
"""
                    )
                    error = "❌ Wrong password! Alert email sent to your Gmail."

            else:
                error = "❌ Email not registered!"

    return render_login_page(error)
