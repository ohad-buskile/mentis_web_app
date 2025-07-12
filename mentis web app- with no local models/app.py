
from flask import Flask, render_template, request, redirect, url_for, session, flash
from utils import csv_utils
from modules.client import client_bp
from modules.therapist import therapist_bp

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with secure key in production

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for(f"{session['user']['role']}.dashboard"))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        email = request.form['email']
        password = request.form['password']
        first = request.form['first_name']
        last = request.form['last_name']


        users = csv_utils.read_csv('users.csv')

        if any(u['email'] == email for u in users):
            flash("User already exists.")
            return redirect(url_for('register'))

        csv_utils.append_csv('users.csv', [role, email, password, first, last])
        flash("Registered successfully.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = csv_utils.read_csv('users.csv')

        for user in users:
            if user['email'] == email and user['password'] == password:
                session['user'] = user
                return redirect(url_for(f"{user['role']}.dashboard"))

        flash("Invalid credentials.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.")
    return redirect(url_for('login'))

# Register Blueprints
app.register_blueprint(client_bp)
app.register_blueprint(therapist_bp)

if __name__ == '__main__':
    app.run(debug=True)
