from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from datetime import date, datetime
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'summer2026secretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///planning2026.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ── Upload config ────────────────────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

db = SQLAlchemy(app)

# ══════════════════════════════════════════════
# UTILISATEURS (hardcodé comme avant)
# ══════════════════════════════════════════════
USERS = {
    'sarah':    'sarah2026',
    'fifi':     'fifi2026',
    'khadidja': 'khadidja2026',
    'mimi':     'mimi2026',
    'hadjere':  'hadjere2026',
    'kiki':     'kiki2026',
}

# ══════════════════════════════════════════════
# HELPER — week_key compatible avec le JS
# ══════════════════════════════════════════════

def get_week_key(d_obj):
    if isinstance(d_obj, str):
        d_obj = datetime.strptime(d_obj, '%Y-%m-%d')
    t = d_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    dow = t.weekday()
    thursday = t.toordinal() + (3 - dow)
    thu_date = date.fromordinal(thursday)
    jan4 = date(thu_date.year, 1, 4)
    week_num = (thursday - jan4.toordinal()) // 7 + 1
    return f"{thu_date.year}-W{week_num}"


# ══════════════════════════════════════════════
# MODÈLES BASE DE DONNÉES
# ══════════════════════════════════════════════

class Profil(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(50), unique=True, nullable=False)
    avatar       = db.Column(db.Text, nullable=True)          # base64
    bio          = db.Column(db.String(200), nullable=True)
    display_name = db.Column(db.String(50), nullable=True)
    member_since = db.Column(db.String(50), nullable=True)
    gallery      = db.Column(db.Text, default='[]')           # JSON [{url, date, label}]

class DeenData(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(50), nullable=False)
    week_key     = db.Column(db.String(20), nullable=False)
    salat_data   = db.Column(db.Text, default='{}')
    juzamma      = db.Column(db.Text, default='{}')
    quran_hizb   = db.Column(db.Text, default='{}')
    book_title   = db.Column(db.String(200), default='')
    book_reading = db.Column(db.Text, default='{}')
    __table_args__ = (db.UniqueConstraint('username', 'week_key'),)

class DeenDaily(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(50), nullable=False)
    date_key     = db.Column(db.String(10), nullable=False)
    adhkar_data  = db.Column(db.Text, default='{}')
    __table_args__ = (db.UniqueConstraint('username', 'date_key'),)

class SportData(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    username    = db.Column(db.String(50), nullable=False)
    date_key    = db.Column(db.String(10), nullable=False)
    steps       = db.Column(db.Integer, default=0)
    water       = db.Column(db.Integer, default=0)
    stretching  = db.Column(db.Text, default='{}')
    swim        = db.Column(db.Text, default='{}')
    __table_args__ = (db.UniqueConstraint('username', 'date_key'),)

class SportWeek(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(50), nullable=False)
    week_key  = db.Column(db.String(20), nullable=False)
    gym_days  = db.Column(db.Text, default='[]')
    __table_args__ = (db.UniqueConstraint('username', 'week_key'),)

class RegimeData(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(50), nullable=False)
    date_key  = db.Column(db.String(10), nullable=False)
    journal   = db.Column(db.Text, default='')
    checks    = db.Column(db.Text, default='{}')
    hard_data = db.Column(db.Text, default='{}')
    __table_args__ = (db.UniqueConstraint('username', 'date_key'),)

class RegimePersist(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    goal     = db.Column(db.String(300), default='')
    hard75   = db.Column(db.Text, default='{}')

class LearningData(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    username       = db.Column(db.String(50), nullable=False)
    date_key       = db.Column(db.String(10), nullable=False)
    lang_checks    = db.Column(db.Text, default='{}')
    activity_done  = db.Column(db.Text, default='{}')
    culture_note   = db.Column(db.String(300), default='')
    __table_args__  = (db.UniqueConstraint('username', 'date_key'),)

class LearningPersist(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    username         = db.Column(db.String(50), unique=True, nullable=False)
    lang_name        = db.Column(db.String(100), default='')
    activity_name    = db.Column(db.String(200), default='')
    lang_streak      = db.Column(db.Text, default='{}')
    activity_streak  = db.Column(db.Text, default='{}')
    culture_streak   = db.Column(db.Text, default='{}')

class SelfcareData(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    username  = db.Column(db.String(50), nullable=False)
    date_key  = db.Column(db.String(10), nullable=False)
    checks    = db.Column(db.Text, default='{}')
    mood      = db.Column(db.String(10), default='')
    mood_note = db.Column(db.Text, default='')
    __table_args__ = (db.UniqueConstraint('username', 'date_key'),)

class SelfcarePersist(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    streak   = db.Column(db.Text, default='{}')

class HomecareData(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    date_key = db.Column(db.String(10), nullable=False)
    checks   = db.Column(db.Text, default='{}')
    minutes  = db.Column(db.Text, default='{}')
    __table_args__ = (db.UniqueConstraint('username', 'date_key'),)

class HomecarePersist(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    streak   = db.Column(db.Text, default='{}')

class GoalItem(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    username   = db.Column(db.String(50), nullable=False)
    goal_id    = db.Column(db.BigInteger, nullable=False)
    category   = db.Column(db.String(30), nullable=False)
    title      = db.Column(db.String(200), nullable=False)
    quarter    = db.Column(db.String(10), default='year')
    note       = db.Column(db.String(200), default='')
    done       = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.String(20), default='')
    __table_args__ = (db.UniqueConstraint('username', 'goal_id'),)


# ══════════════════════════════════════════════
# AUTH
# ══════════════════════════════════════════════

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
            if not Profil.query.filter_by(username=username).first():
                p = Profil(username=username, display_name=username)
                db.session.add(p)
                db.session.commit()
            return redirect(url_for('home'))
        else:
            error = 'Identifiants incorrects'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ══════════════════════════════════════════════
# PAGES
# ══════════════════════════════════════════════

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

@app.route('/profil')
@login_required
def profil():
    return render_template('profil.html')

@app.route('/goals')
@login_required
def goals():
    return render_template('goals.html')


# ══════════════════════════════════════════════
# API — PROFIL
# ══════════════════════════════════════════════

@app.route('/api/profil', methods=['GET'])
@login_required
def api_profil_get():
    u = session['username']
    p = Profil.query.filter_by(username=u).first()
    if not p:
        return jsonify({})
    return jsonify({
        'username':    p.display_name or u,
        'avatar':      p.avatar or '',
        'bio':         p.bio or '',
        'memberSince': p.member_since or '',
        'gallery':     json.loads(p.gallery or '[]'),
    })

@app.route('/api/profil', methods=['POST'])
@login_required
def api_profil_save():
    u = session['username']
    data = request.get_json()
    p = Profil.query.filter_by(username=u).first()
    if not p:
        p = Profil(username=u)
        db.session.add(p)
    if 'username'    in data: p.display_name = data['username']
    if 'avatar'      in data: p.avatar       = data['avatar']
    if 'bio'         in data: p.bio          = data['bio']
    if 'memberSince' in data: p.member_since = data['memberSince']
    if 'gallery'     in data: p.gallery      = json.dumps(data['gallery'])
    db.session.commit()
    return jsonify({'ok': True})


@app.route('/api/profil/gallery/upload', methods=['POST'])
@login_required
def api_gallery_upload():
    u = session['username']
    if 'photo' not in request.files:
        return jsonify({'error': 'Aucun fichier'}), 400

    file = request.files['photo']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({'error': 'Fichier invalide'}), 400

    # Dossier par utilisateur : static/uploads/<username>/
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], u)
    os.makedirs(user_folder, exist_ok=True)

    ext      = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{int(datetime.utcnow().timestamp() * 1000)}.{ext}"
    filepath = os.path.join(user_folder, filename)
    file.save(filepath)

    url = f"/static/uploads/{u}/{filename}"
    return jsonify({'ok': True, 'url': url})


@app.route('/api/profil/gallery/delete', methods=['POST'])
@login_required
def api_gallery_delete():
    u = session['username']
    data = request.get_json()
    url  = data.get('url', '')

    # Sécurité : le chemin doit appartenir à l'utilisateur
    expected_prefix = f"/static/uploads/{u}/"
    if url.startswith(expected_prefix):
        filepath = url.lstrip('/')
        if os.path.exists(filepath):
            os.remove(filepath)

    return jsonify({'ok': True})


# ══════════════════════════════════════════════
# API — DEEN
# ══════════════════════════════════════════════

@app.route('/api/deen/<week_key>', methods=['GET'])
@login_required
def api_deen_get(week_key):
    u = session['username']
    d     = DeenData.query.filter_by(username=u, week_key=week_key).first()
    any_d = DeenData.query.filter_by(username=u).first()
    return jsonify({
        'salat':        json.loads(d.salat_data    if d     else '{}'),
        'juzamma':      json.loads(any_d.juzamma   if any_d else '{}'),
        'quran_hizb':   json.loads(any_d.quran_hizb if any_d else '{}'),
        'book_title':   any_d.book_title            if any_d else '',
        'book_reading': json.loads(any_d.book_reading if any_d else '{}'),
    })

@app.route('/api/deen/salat', methods=['POST'])
@login_required
def api_deen_salat():
    u = session['username']
    data     = request.get_json()
    week_key = data.get('week_key')
    d = DeenData.query.filter_by(username=u, week_key=week_key).first()
    if not d:
        d = DeenData(username=u, week_key=week_key)
        db.session.add(d)
    d.salat_data = json.dumps(data.get('salat', {}))
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/deen/persist', methods=['POST'])
@login_required
def api_deen_persist():
    u = session['username']
    data = request.get_json()
    d = DeenData.query.filter_by(username=u).first()
    if not d:
        week_key = get_week_key(datetime.utcnow())
        d = DeenData(username=u, week_key=week_key)
        db.session.add(d)
    if 'juzamma'      in data: d.juzamma      = json.dumps(data['juzamma'])
    if 'quran_hizb'   in data: d.quran_hizb   = json.dumps(data['quran_hizb'])
    if 'book_title'   in data: d.book_title   = data['book_title']
    if 'book_reading' in data: d.book_reading = json.dumps(data['book_reading'])
    db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════════
# API — SPORT
# ══════════════════════════════════════════════

@app.route('/api/sport/<date_key>', methods=['GET'])
@login_required
def api_sport_get(date_key):
    u        = session['username']
    week_key = get_week_key(date_key)
    s = SportData.query.filter_by(username=u, date_key=date_key).first()
    w = SportWeek.query.filter_by(username=u, week_key=week_key).first()
    return jsonify({
        'steps':      s.steps if s else 0,
        'water':      s.water if s else 0,
        'stretching': json.loads(s.stretching if s else '{}'),
        'swim':       json.loads(s.swim if s else '{}'),
        'gym_days':   json.loads(w.gym_days if w else '[]'),
        'week_key':   week_key,
    })

@app.route('/api/sport/day', methods=['POST'])
@login_required
def api_sport_day():
    u        = session['username']
    data     = request.get_json()
    date_key = data.get('date_key')
    s = SportData.query.filter_by(username=u, date_key=date_key).first()
    if not s:
        s = SportData(username=u, date_key=date_key)
        db.session.add(s)
    if 'steps'      in data: s.steps      = int(data['steps'])
    if 'water'      in data: s.water      = int(data['water'])
    if 'stretching' in data: s.stretching = json.dumps(data['stretching'])
    if 'swim'       in data: s.swim       = json.dumps(data['swim'])
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/sport/gym', methods=['POST'])
@login_required
def api_sport_gym():
    u        = session['username']
    data     = request.get_json()
    week_key = data.get('week_key')
    w = SportWeek.query.filter_by(username=u, week_key=week_key).first()
    if not w:
        w = SportWeek(username=u, week_key=week_key)
        db.session.add(w)
    w.gym_days = json.dumps(data.get('gym_days', []))
    db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════════
# API — RÉGIME
# ══════════════════════════════════════════════

@app.route('/api/regime/<date_key>', methods=['GET'])
@login_required
def api_regime_get(date_key):
    u = session['username']
    r = RegimeData.query.filter_by(username=u, date_key=date_key).first()
    p = RegimePersist.query.filter_by(username=u).first()
    return jsonify({
        'journal':   r.journal   if r else '',
        'checks':    json.loads(r.checks    if r else '{}'),
        'hard_data': json.loads(r.hard_data if r else '{}'),
        'goal':      p.goal      if p else '',
        'hard75':    json.loads(p.hard75    if p else '{}'),
    })

@app.route('/api/regime/day', methods=['POST'])
@login_required
def api_regime_day():
    u        = session['username']
    data     = request.get_json()
    date_key = data.get('date_key')
    r = RegimeData.query.filter_by(username=u, date_key=date_key).first()
    if not r:
        r = RegimeData(username=u, date_key=date_key)
        db.session.add(r)
    if 'journal'   in data: r.journal   = data['journal']
    if 'checks'    in data: r.checks    = json.dumps(data['checks'])
    if 'hard_data' in data: r.hard_data = json.dumps(data['hard_data'])
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/regime/persist', methods=['POST'])
@login_required
def api_regime_persist():
    u    = session['username']
    data = request.get_json()
    p = RegimePersist.query.filter_by(username=u).first()
    if not p:
        p = RegimePersist(username=u)
        db.session.add(p)
    if 'goal'   in data: p.goal   = data['goal']
    if 'hard75' in data: p.hard75 = json.dumps(data['hard75'])
    db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════════
# API — LEARNING
# ══════════════════════════════════════════════

@app.route('/api/learning/<date_key>', methods=['GET'])
@login_required
def api_learning_get(date_key):
    u = session['username']
    l = LearningData.query.filter_by(username=u, date_key=date_key).first()
    p = LearningPersist.query.filter_by(username=u).first()
    return jsonify({
        'lang_checks':     json.loads(l.lang_checks    if l else '{}'),
        'activity_done':   json.loads(l.activity_done  if l else '{}'),
        'culture_note':    l.culture_note               if l else '',
        'lang_name':       p.lang_name                  if p else '',
        'activity_name':   p.activity_name              if p else '',
        'lang_streak':     json.loads(p.lang_streak     if p else '{}'),
        'activity_streak': json.loads(p.activity_streak if p else '{}'),
        'culture_streak':  json.loads(p.culture_streak  if p else '{}'),
    })

@app.route('/api/learning/day', methods=['POST'])
@login_required
def api_learning_day():
    u        = session['username']
    data     = request.get_json()
    date_key = data.get('date_key')
    l = LearningData.query.filter_by(username=u, date_key=date_key).first()
    if not l:
        l = LearningData(username=u, date_key=date_key)
        db.session.add(l)
    if 'lang_checks'   in data: l.lang_checks   = json.dumps(data['lang_checks'])
    if 'activity_done' in data: l.activity_done  = json.dumps(data['activity_done'])
    if 'culture_note'  in data: l.culture_note   = data['culture_note']
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/learning/persist', methods=['POST'])
@login_required
def api_learning_persist():
    u    = session['username']
    data = request.get_json()
    p = LearningPersist.query.filter_by(username=u).first()
    if not p:
        p = LearningPersist(username=u)
        db.session.add(p)
    if 'lang_name'       in data: p.lang_name        = data['lang_name']
    if 'activity_name'   in data: p.activity_name    = data['activity_name']
    if 'lang_streak'     in data: p.lang_streak      = json.dumps(data['lang_streak'])
    if 'activity_streak' in data: p.activity_streak  = json.dumps(data['activity_streak'])
    if 'culture_streak'  in data: p.culture_streak   = json.dumps(data['culture_streak'])
    db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════════
# API — SELFCARE
# ══════════════════════════════════════════════

@app.route('/api/selfcare/<date_key>', methods=['GET'])
@login_required
def api_selfcare_get(date_key):
    u = session['username']
    s = SelfcareData.query.filter_by(username=u, date_key=date_key).first()
    p = SelfcarePersist.query.filter_by(username=u).first()
    return jsonify({
        'checks':    json.loads(s.checks    if s else '{}'),
        'mood':      s.mood                 if s else '',
        'mood_note': s.mood_note            if s else '',
        'streak':    json.loads(p.streak    if p else '{}'),
    })

@app.route('/api/selfcare/day', methods=['POST'])
@login_required
def api_selfcare_day():
    u        = session['username']
    data     = request.get_json()
    date_key = data.get('date_key')
    s = SelfcareData.query.filter_by(username=u, date_key=date_key).first()
    if not s:
        s = SelfcareData(username=u, date_key=date_key)
        db.session.add(s)
    if 'checks'    in data: s.checks    = json.dumps(data['checks'])
    if 'mood'      in data: s.mood      = data['mood']
    if 'mood_note' in data: s.mood_note = data['mood_note']
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/selfcare/persist', methods=['POST'])
@login_required
def api_selfcare_persist():
    u    = session['username']
    data = request.get_json()
    p = SelfcarePersist.query.filter_by(username=u).first()
    if not p:
        p = SelfcarePersist(username=u)
        db.session.add(p)
    if 'streak' in data: p.streak = json.dumps(data['streak'])
    db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════════
# API — HOMECARE
# ══════════════════════════════════════════════

@app.route('/api/homecare/<date_key>', methods=['GET'])
@login_required
def api_homecare_get(date_key):
    u = session['username']
    h = HomecareData.query.filter_by(username=u, date_key=date_key).first()
    p = HomecarePersist.query.filter_by(username=u).first()
    return jsonify({
        'checks':  json.loads(h.checks  if h else '{}'),
        'minutes': json.loads(h.minutes if h else '{}'),
        'streak':  json.loads(p.streak  if p else '{}'),
    })

@app.route('/api/homecare/day', methods=['POST'])
@login_required
def api_homecare_day():
    u        = session['username']
    data     = request.get_json()
    date_key = data.get('date_key')
    h = HomecareData.query.filter_by(username=u, date_key=date_key).first()
    if not h:
        h = HomecareData(username=u, date_key=date_key)
        db.session.add(h)
    if 'checks'  in data: h.checks  = json.dumps(data['checks'])
    if 'minutes' in data: h.minutes = json.dumps(data['minutes'])
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/homecare/persist', methods=['POST'])
@login_required
def api_homecare_persist():
    u    = session['username']
    data = request.get_json()
    p = HomecarePersist.query.filter_by(username=u).first()
    if not p:
        p = HomecarePersist(username=u)
        db.session.add(p)
    if 'streak' in data: p.streak = json.dumps(data['streak'])
    db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════════
# API — DASHBOARD
# ══════════════════════════════════════════════

@app.route('/api/dashboard/<date_key>', methods=['GET'])
@login_required
def api_dashboard(date_key):
    u        = session['username']
    week_key = get_week_key(date_key)

    deen       = DeenData.query.filter_by(username=u, week_key=week_key).first()
    salat      = json.loads(deen.salat_data if deen else '{}')
    sport      = SportData.query.filter_by(username=u, date_key=date_key).first()
    sport_week = SportWeek.query.filter_by(username=u, week_key=week_key).first()
    regime     = RegimeData.query.filter_by(username=u, date_key=date_key).first()
    learning   = LearningData.query.filter_by(username=u, date_key=date_key).first()
    sc         = SelfcareData.query.filter_by(username=u, date_key=date_key).first()
    hc         = HomecareData.query.filter_by(username=u, date_key=date_key).first()
    hc_minutes = json.loads(hc.minutes if hc else '{}')
    hc_min     = sum(v for v in hc_minutes.values() if isinstance(v, (int, float)))

    return jsonify({
        'salat':           salat,
        'steps':           sport.steps if sport else 0,
        'water':           sport.water if sport else 0,
        'gym_days':        json.loads(sport_week.gym_days if sport_week else '[]'),
        'regime_checks':   json.loads(regime.checks if regime else '{}'),
        'learning_checks': json.loads(learning.lang_checks if learning else '{}'),
        'selfcare_checks': json.loads(sc.checks if sc else '{}'),
        'homecare_min':    hc_min,
    })


# ══════════════════════════════════════════════
# API — GOALS
# ══════════════════════════════════════════════

@app.route('/api/goals', methods=['GET'])
@login_required
def api_goals_get():
    u     = session['username']
    items = GoalItem.query.filter_by(username=u).order_by(GoalItem.id).all()
    return jsonify([{
        'id':       g.goal_id,
        'category': g.category,
        'title':    g.title,
        'quarter':  g.quarter,
        'note':     g.note or '',
        'done':     g.done,
    } for g in items])

@app.route('/api/goals', methods=['POST'])
@login_required
def api_goals_save():
    u       = session['username']
    data    = request.get_json()
    goal_id = int(data.get('id'))
    g = GoalItem.query.filter_by(username=u, goal_id=goal_id).first()
    if not g:
        g = GoalItem(username=u, goal_id=goal_id,
                     created_at=datetime.utcnow().strftime('%Y-%m-%d'))
        db.session.add(g)
    g.category = data.get('category', 'personnel')
    g.title    = data.get('title', '')
    g.quarter  = data.get('quarter', 'year')
    g.note     = data.get('note', '')
    g.done     = data.get('done', False)
    db.session.commit()
    return jsonify({'ok': True})

@app.route('/api/goals/<string:goal_id>/toggle', methods=['POST'])
@login_required
def api_goals_toggle(goal_id):
    u       = session['username']
    goal_id = int(goal_id)
    g = GoalItem.query.filter_by(username=u, goal_id=goal_id).first()
    if g:
        g.done = not g.done
        db.session.commit()
    return jsonify({'ok': True, 'done': g.done if g else False})

@app.route('/api/goals/<string:goal_id>', methods=['DELETE'])
@login_required
def api_goals_delete(goal_id):
    u       = session['username']
    goal_id = int(goal_id)
    g = GoalItem.query.filter_by(username=u, goal_id=goal_id).first()
    if g:
        db.session.delete(g)
        db.session.commit()
    return jsonify({'ok': True})


# ══════════════════════════════════════════════
# INIT DB + RUN
# ══════════════════════════════════════════════

with app.app_context():
    db.create_all()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2003, debug=True)