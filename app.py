import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_btcl_kurigram_key_2026")

ADMIN_USERNAME = "Khushbu23"
ADMIN_PASSWORD = "01751947523"
ADMIN_SECURITY_CODE = "137955"

# --- Database Setup ---
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE,
            email TEXT,
            phone TEXT,
            password TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    
    # Phone Records Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phone_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            mobile TEXT,
            service_type TEXT,
            connection_num TEXT,
            address TEXT,
            note TEXT
        )
    ''')
    
    # Messages Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_username TEXT,
            receiver_username TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message TEXT,
            is_read INTEGER DEFAULT 0
        )
    ''')

    # Create Admin Account
    cursor.execute("SELECT * FROM users WHERE username = ?", (ADMIN_USERNAME,))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash(ADMIN_PASSWORD)
        cursor.execute("INSERT INTO users (name, username, email, phone, password, status) VALUES (?, ?, ?, ?, ?, ?)",
                       ('Admin', ADMIN_USERNAME, 'admin@btcl.com', '01751947523', hashed_pw, 'active'))

    conn.commit()
    conn.close()

init_db()

# --- Single File HTML Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #121212; color: #fff; font-family: sans-serif; }
        .card { background-color: #1e1e1e; color: white; border: 1px solid #333; }
        .form-control, .form-select { background-color: #2b2b2b; color: #fff; border: 1px solid #444; }
        .form-control:focus, .form-select:focus { background-color: #333; color: #fff; }
        .btn-success-custom { background-color: #00e676; border: none; color: #000; font-weight: bold; }
    </style>
</head>
<body>
<div class="container py-3">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="text-success">BTCL, কুড়িগ্রাম</h4>
        {% if session.get('user') %}
            <div>
                <span class="me-2">স্বাগতম, {{ session['user']['name'] }}</span>
                <a href="/logout" class="btn btn-danger btn-sm">লগআউট</a>
            </div>
        {% endif %}
    </div>

    {% if not session.get('user') %}
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card p-4">
                <ul class="nav nav-tabs mb-3" id="authTab">
                    <li class="nav-item">
                        <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#loginTab">লগইন</button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#regTab">রেজিস্ট্রেশন</button>
                    </li>
                </ul>
                <div class="tab-content">
                    <div class="tab-pane fade show active" id="loginTab">
                        <form action="/login" method="POST">
                            <input type="text" name="username" class="form-control mb-2" placeholder="ইউজারনেম / জিমেইল / ফোন" required>
                            <input type="password" name="password" class="form-control mb-3" placeholder="পাসওয়ার্ড" required>
                            <button type="submit" class="btn btn-success-custom w-100">লগইন করুন</button>
                        </form>
                    </div>
                    <div class="tab-pane fade" id="regTab">
                        <form action="/register" method="POST">
                            <input type="text" name="name" class="form-control mb-2" placeholder="আপনার নাম" required>
                            <input type="email" name="email" class="form-control mb-2" placeholder="সঠিক জিমেইল আইডি" required>
                            <input type="text" name="phone" class="form-control mb-2" placeholder="১১ ডিজিট মোবাইল নম্বর" required>
                            <input type="text" name="username" class="form-control mb-2" placeholder="ইউজারনেম" required>
                            <input type="password" name="password" class="form-control mb-2" placeholder="পাসওয়ার্ড" required>
                            <input type="password" name="confirm_password" class="form-control mb-3" placeholder="কনফার্ম পাসওয়ার্ড" required>
                            <button type="submit" class="btn btn-success-custom w-100">রেজিস্ট্রেশন করুন</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% else %}
    <div class="mb-3">
        <input type="text" id="searchInput" class="form-control" placeholder="যেকোনো কিছু দিয়ে সার্চ করুন (নাম, নম্বর, ঠিকানা...)" onkeyup="performSearch()">
    </div>

    <div class="card p-3 mb-4">
        <h5>গ্রাহক ও সংযোগ তালিকা</h5>
        <div class="table-responsive">
            <table class="table table-dark table-striped mt-2">
                <thead>
                    <tr>
                        <th>নাম</th><th>মোবাইল</th><th>সেবা</th><th>সংযোগ নং</th><th>ঠিকানা</th><th>নোট</th><th>অ্যাকশন</th>
                    </tr>
                </thead>
                <tbody id="searchResults"></tbody>
            </table>
        </div>
    </div>

    <div class="card p-3 mb-4">
        <h5>নতুন নম্বর এড করুন</h5>
        <form action="/add_record" method="POST" class="row g-2">
            <div class="col-md-4"><input type="text" name="customer_name" class="form-control" placeholder="গ্রাহকের নাম" required></div>
            <div class="col-md-4"><input type="text" name="mobile" class="form-control" placeholder="মোবাইল নম্বর" required></div>
            <div class="col-md-4">
                <select name="service_type" class="form-select">
                    <option value="টেলিফোন">টেলিফোন</option>
                    <option value="ওয়াইফাই">ওয়াইফাই</option>
                    <option value="টেলিফোন+ওয়াইফাই">টেলিফোন+ওয়াইফাই</option>
                </select>
            </div>
            <div class="col-md-4"><input type="text" name="connection_num" class="form-control" placeholder="সংযোগ নম্বর"></div>
            <div class="col-md-4"><input type="text" name="address" class="form-control" placeholder="ঠিকানা"></div>
            <div class="col-md-4"><input type="text" name="note" class="form-control" placeholder="অতিরিক্ত নোট"></div>
            <div class="col-12 mt-2">
                <button type="submit" class="btn btn-success-custom w-100">সংরক্ষণ করুন</button>
            </div>
        </form>
    </div>
    {% endif %}
</div>

<div class="modal fade" id="deleteModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content bg-dark text-white">
      <form id="deleteForm" method="POST">
          <div class="modal-header"><h5 class="modal-title">ডিলেটের নিশ্চিতকরণ</h5></div>
          <div class="modal-body">
            <p>ডিলেট করতে এডমিন সিকিউরিটি কোড দিন:</p>
            <input type="password" name="security_code" class="form-control" required placeholder="সিকিউরিটি কোড">
          </div>
          <div class="modal-footer"><button type="submit" class="btn btn-danger">ডিলেট নিশ্চিত করুন</button></div>
      </form>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
function performSearch() {
    let q = document.getElementById('searchInput') ? document.getElementById('searchInput').value : '';
    fetch('/api/search?q=' + q)
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.forEach(row => {
            html += `<tr>
                <td>${row[1]}</td><td>${row[2]}</td><td>${row[3]}</td><td>${row[4]}</td><td>${row[5]}</td><td>${row[6]}</td>
                <td><button class="btn btn-danger btn-sm" onclick="promptDelete(${row[0]})">ডিলেট</button></td>
            </tr>`;
        });
        if(document.getElementById('searchResults')) document.getElementById('searchResults').innerHTML = html;
    });
}
function promptDelete(id) {
    document.getElementById('deleteForm').action = '/delete_record/' + id;
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}
if (document.getElementById('searchInput')) performSearch();
</script>
</body>
</html>
"""

# --- Routes ---
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ? OR phone = ?", (username, username, username))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[5], password):
        if user[6] == 'pending':
            return "আপনার একাউন্টটি এখনও এডমিন অনুমোদন করেনি।"
        elif user[6] == 'blocked':
            return "আপনার একাউন্টটি ব্লক করা হয়েছে।"
        
        session['user'] = {'id': user[0], 'name': user[1], 'username': user[2], 'is_admin': (user[2] == ADMIN_USERNAME)}
        return redirect(url_for('home'))
    return "ভুল ইউজারনেম অথবা পাসওয়ার্ড!"

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return "পাসওয়ার্ড দুটি মেলেনি!"

    hashed_pw = generate_password_hash(password)
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, username, email, phone, password) VALUES (?, ?, ?, ?, ?)",
                       (name, username, email, phone, hashed_pw))
        conn.commit()
        conn.close()
        return "রেজিস্ট্রেশন সফল হয়েছে! এডমিন অনুমোদন দিলে লগইন করতে পারবেন।"
    except:
        return "ইউজারনেমটি আগে থেকেই ব্যবহৃত হচ্ছে।"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/add_record', methods=['POST'])
def add_record():
    if 'user' not in session: return redirect(url_for('home'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO phone_records (customer_name, mobile, service_type, connection_num, address, note) 
                      VALUES (?, ?, ?, ?, ?, ?)''', 
                   (request.form['customer_name'], request.form['mobile'], request.form['service_type'],
                    request.form['connection_num'], request.form['address'], request.form['note']))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/delete_record/<int:id>', methods=['POST'])
def delete_record(id):
    if request.form.get('security_code') != ADMIN_SECURITY_CODE:
        return "সিকিউরিটি কোড ভুল!"
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM phone_records WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM phone_records WHERE customer_name LIKE ? OR mobile LIKE ? OR connection_num LIKE ? OR address LIKE ? OR note LIKE ?''',
                   (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    records = cursor.fetchall()
    conn.close()
    return jsonify(records)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)