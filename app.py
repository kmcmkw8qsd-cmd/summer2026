from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps

app = Flask(__name__)
app.secret_key = 'summer2026secretkey'

USERS = {

    'sarah': 'sarah2026',

    'khadidja': 'khadidja2026',

}

# Décorateur pour protéger les pages
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = 'Identifiants incorrects'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/deen')
@login_required
def deen():
    return render_template('deen.html')

@app.route('/sport')
@login_required
def sport():
    return render_template('sport.html')

@app.route('/regime')
@login_required
def regime():
    return render_template('regime.html')

@app.route('/learning')
@login_required
def learning():
    return render_template('learning.html')

@app.route('/selfcare')
@login_required
def selfcare():
    return render_template('selfcare.html')

@app.route('/homecare')
@login_required
def homecare():
    return render_template('homecare.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2003, debug=True)