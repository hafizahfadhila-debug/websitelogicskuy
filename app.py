from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# File untuk menyimpan data
DATA_DIR = 'data'
QUESTIONS_FILE = os.path.join(DATA_DIR, 'questions.json')
LEADERBOARD_FILE = os.path.join(DATA_DIR, 'leaderboard.json')

# Kode akses
ADMIN_CODES = ['ADMIN1','ADMIN2', 'ADMIN3']
USER_CODES = ['USERSER1', 'USERSERI2']

# Buat folder data jika belum ada
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Initialize data files
def init_data_files():
    if not os.path.exists(QUESTIONS_FILE):
        default_questions = {
            'Aritmatika Sosial': [],
            'Fungsi': [],
            'Aturan Pencacahan': [],
            'Statistika': [],
            'Logika': []
        }
        with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_questions, f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(LEADERBOARD_FILE):
        default_leaderboard = {
            'Aritmatika Sosial': [],
            'Fungsi': [],
            'Aturan Pencacahan': [],
            'Statistika': [],
            'Logika': []
        }
        with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_leaderboard, f, ensure_ascii=False, indent=2)

init_data_files()

# Load data
def load_questions():
    with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_questions(questions):
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

def load_leaderboard():
    with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_leaderboard(leaderboard):
    with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(leaderboard, f, ensure_ascii=False, indent=2)

# Routes
@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    name = data.get('name')
    code = data.get('code')
    
    if code in ADMIN_CODES:  
        session['logged_in'] = True
        session['name'] = name
        session['role'] = 'admin'
        return jsonify({'success': True, 'role': 'admin'})
    elif code in USER_CODES:  
        session['logged_in'] = True
        session['name'] = name
        session['role'] = 'user'
        return jsonify({'success': True, 'role': 'user'})
    else:
        return jsonify({'success': False, 'message': 'Kode salah!'})

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', name=session['name'], role=session['role'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/quiz/<category>')
def quiz(category):
    if 'logged_in' not in session:
        return redirect(url_for('index'))
    return render_template('quiz.html', category=category, name=session['name'])

@app.route('/leaderboard')
def leaderboard():
    if 'logged_in' not in session:
        return redirect(url_for('index'))
    return render_template('leaderboard.html', role=session['role'])

@app.route('/admin')
def admin():
    if 'logged_in' not in session or session['role'] != 'admin':
        return redirect(url_for('dashboard'))
    return render_template('admin.html')

# API Routes
@app.route('/api/questions/<category>')
def get_questions(category):
    questions = load_questions()
    return jsonify(questions.get(category, []))

@app.route('/api/questions/<category>', methods=['POST'])
def add_question(category):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    questions = load_questions()
    new_question = request.json
    new_question['id'] = len(questions[category]) + 1
    questions[category].append(new_question)
    save_questions(questions)
    return jsonify({'success': True})

@app.route('/api/questions/<category>/<int:question_id>', methods=['DELETE'])
def delete_question(category, question_id):
    if session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    questions = load_questions()
    questions[category] = [q for q in questions[category] if q['id'] != question_id]
    save_questions(questions)
    return jsonify({'success': True})

@app.route('/api/leaderboard/<category>')
def get_leaderboard(category):
    leaderboard = load_leaderboard()
    return jsonify(leaderboard.get(category, []))

@app.route('/api/leaderboard/all')
def get_all_leaderboard():
    leaderboard = load_leaderboard()
    return jsonify(leaderboard)

@app.route('/api/leaderboard/<category>', methods=['POST'])
def submit_score(category):
    data = request.json
    leaderboard = load_leaderboard()
    
    new_entry = {
        'name': data['name'],
        'score': data['score'],
        'date': datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    leaderboard[category].append(new_entry)
    leaderboard[category].sort(key=lambda x: x['score'], reverse=True)
    leaderboard[category] = leaderboard[category][:10]  # Keep top 10
    
    save_leaderboard(leaderboard)
    return jsonify({'success': True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)