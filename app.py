import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "btcl_kurigram_green_vibrant_pro_2026")

MAIN_ADMIN_USERNAME = "Khushbu23"
SECURITY_DELETE_PASSWORD = "137955"
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ডেটাবেজ লক ও ক্র্যাশ রোধ করার জন্য নিরাপদ কানেকশন ফাংশন
def get_db_connection():
    conn = sqlite3.connect('database.db', timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE,
            email TEXT,
            phone TEXT,
            password TEXT,
            raw_pass TEXT,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'pending',
            profile_pic TEXT DEFAULT '',
            added_by TEXT DEFAULT 'Khushbu23',
            is_deleted INTEGER DEFAULT 0,
            last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phone_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            mobile TEXT,
            service_type TEXT,
            connection_num TEXT,
            address TEXT,
            note TEXT,
            record_image TEXT DEFAULT '',
            added_by TEXT DEFAULT 'Khushbu23',
            is_deleted INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            file_url TEXT,
            is_group INTEGER DEFAULT 0,
            is_read INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute("SELECT * FROM users WHERE username = ?", (MAIN_ADMIN_USERNAME,))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("01751947523")
        cursor.execute('''INSERT INTO users (name, username, email, phone, password, raw_pass, role, status) 
                         VALUES (?, ?, ?, ?, ?, ?, 'main_admin', 'active')''',
                       ('Md Khushbu Alom', MAIN_ADMIN_USERNAME, 'admin@btcl.com', '01751947523', hashed_pw, '01751947523'))

    conn.commit()
    conn.close()

init_db()

# আপনার সেই সুন্দর গ্রিন ভাইব্রেন্ট এবং মোবাইল-কম্পিউটার ফ্রেন্ডলি ডিজাইন টেমপ্লেট
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম - Smart Control Desk & Messenger</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: linear-gradient(135deg, #052e16 0%, #064e3b 50%, #022c22 100%); color: #ecfdf5; font-family: 'Segoe UI', sans-serif; min-height: 100vh; padding-bottom: 70px; }
        .green-vibrant-header { background: linear-gradient(90deg, #10b981 0%, #34d399 50%, #059669 100%); color: #022c22; font-weight: bold; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4); }
        .card-custom { background: rgba(6, 78, 59, 0.95); border: 1px solid #34d399; border-radius: 12px; box-shadow: 0 4px 20px rgba(52, 211, 153, 0.15); }
        .form-label { color: #a7f3d0; font-weight: bold; }
        .form-control, .form-select { background-color: #022c22; color: #fff; border: 1px solid #10b981; }
        .form-control:focus, .form-select:focus { background-color: #022c22; color: #fff; border-color: #34d399; box-shadow: 0 0 10px rgba(52, 211, 153, 0.5); }
        .btn-green-gold { background: linear-gradient(45deg, #10b981, #fbbf24); color: #000; font-weight: bold; border: none; }
        .btn-green-gold:hover { background: linear-gradient(45deg, #059669, #f59e0b); color: #fff; }
        .stat-card { background: rgba(16, 185, 129, 0.2); border: 1px solid #34d399; text-align: center; padding: 15px; border-radius: 10px; }
        .stat-number { font-size: 20px; font-weight: bold; color: #fde047; }
    </style>
</head>
<body>
<div class="green-vibrant-header text-center py-2">
    <h3 class="m-0"><i class="fa-solid fa-phone-volume"></i> BTCL, কুড়িগ্রাম</h3>
    <small>Smart Control Desk & Messenger Pro</small>
</div>
<div class="container py-4">
    {% if session.get('user') %}
        <div class="card-custom p-4 shadow-lg text-center">
            <h4 class="text-success mb-3"><i class="fa-solid fa-user-shield"></i> স্বাগতম, {{ session.get('user').get('name') }}!</h4>
            <p class="text-warning">সার্ভারটি মোবাইল ও কম্পিউটার উভয় ব্রাউজারে সচল আছে এবং মেইন এডমিন আইডি সম্পূর্ণ সুরক্ষিত রয়েছে।</p>
            <div class="row g-3 my-3">
                <div class="col-md-3 col-6"><div class="stat-card"><div>মোট নম্বর</div><div class="stat-number">0</div></div></div>
                <div class="col-md-3 col-6"><div class="stat-card"><div>টেলিফোন নম্বর</div><div class="stat-number">0</div></div></div>
                <div class="col-md-3 col-6"><div class="stat-card"><div>উভয় সার্ভিস</div><div class="stat-number">0</div></div></div>
                <div class="col-md-3 col-6"><div class="stat-card"><div>ওয়াইফাই নম্বর</div><div class="stat-number">0</div></div></div>
            </div>
            <a href="/logout" class="btn btn-danger px-4 mt-2"><i class="fa-solid fa-right-from-bracket"></i> লগআউট করুন</a>
        </div>
    {% else %}
        <div class="row justify-content-center mt-5">
            <div class="col-md-5">
                <div class="card-custom p-4 shadow-lg">
                    <h4 class="text-warning text-center mb-3"><i class="fa-solid fa-lock"></i> সিস্টেমে লগইন করুন</h4>
                    <form action="/login" method="POST">
                        <div class="mb-3"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" required></div>
                        <div class="mb-3"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
                        <button type="submit" class="btn btn-green-gold w-100 py-2">প্রবেশ করুন</button>
                    </form>
                </div>
            </div>
        </div>
    {% endif %}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user'] = dict(user)
            return redirect(url_for('index'))
        return "Invalid Credentials", 400
    except Exception as e:
        return str(e), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/ping')
def ping():
    return jsonify({"status": "alive"})

@app.route('/api/stats')
def stats():
    return jsonify({"total": 0, "tel": 0, "both": 0, "wifi": 0})

# মেইন এডমিন আইডি (Khushbu23) ডিলিট করা যাবে না, বাকি সব ইউজার ডিলিট করা যাবে
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user' not in session:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    target_user = cursor.execute("SELECT username, role FROM users WHERE id = ?", (user_id,)).fetchone()
    
    if target_user:
        # যদি ডিলিট করতে চাওয়া আইডিটি মেইন এডমিন হয়, তবে ব্লক করবে
        if target_user['username'] == MAIN_ADMIN_USERNAME or target_user['role'] == 'main_admin':
            conn.close()
            return "মেইন এডমিনের আইডি কোনোভাবেই ডিলিট করা সম্ভব নয়!", 403
            
        # বাকি সাধারণ ইউজার বা অন্য আইডিগুলো সফলভাবে ডিলিট বা রিমুভ হবে
        cursor.execute("UPDATE users SET is_deleted = 1 WHERE id = ?", (user_id,))
        conn.commit()
        
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))