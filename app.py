from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'btcl_kurigram_super_secret_key_2026'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

SECURITY_PIN = "137955"  # আপনার নির্ধারিত সিকিউরিটি পিন

def init_db():
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, email TEXT, phone TEXT, 
                        username TEXT UNIQUE, password TEXT, 
                        role TEXT DEFAULT 'user',
                        status TEXT DEFAULT 'Pending',
                        profile_pic TEXT DEFAULT 'default.png')''')
                        
    # ফিক্সড রিয়েল এডমিন (Khushbu23 / 01751947523)
    cursor.execute("SELECT * FROM users WHERE username = 'Khushbu23'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, phone, username, password, role, status, profile_pic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       ("Real Admin", "admin@btcl.com", "01751947523", "Khushbu23", "01751947523", "super_admin", "Active", "default.png"))
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, phone TEXT, service_type TEXT, 
                        service_no TEXT, address TEXT, note TEXT, 
                        doc_file TEXT, is_deleted INTEGER DEFAULT 0,
                        created_at TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action TEXT, username TEXT, timestamp TEXT)''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html', page='login')

@app.route('/register_page')
def register_page():
    return render_template('index.html', page='register')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    username = request.form['username']
    password = request.form['password']
    
    try:
        conn = sqlite3.connect('btcl_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, phone, username, password, role, status) VALUES (?, ?, ?, ?, ?, 'user', 'Pending')",
                       (name, email, phone, username, password))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    except Exception as e:
        return f"Registration Error: {str(e)}"

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        if user[7] != 'Active' and username != 'Khushbu23':
            return "আপনার অ্যাকাউন্টটি এখনো রিয়েল এডমিন কর্তৃক অনুমোদিত (Active) হয়নি!"
                
        session['user'] = user[4]
        session['role'] = user[6]
        return redirect(url_for('dashboard'))
    return "ভুল ইউজারনেম অথবা পাসওয়ার্ড!"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    filter_type = request.args.get('filter', 'all')
    search_query = request.args.get('search', '')
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    
    # কাউন্টসের জন্য
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND service_type = 'Telephone'")
    tel_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND service_type = 'Tel+WiFi'")
    tel_wifi_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND service_type = 'WiFi'")
    wifi_count = cursor.fetchone()[0]
    
    # কুয়েরি ফিল্টার
    query = "SELECT * FROM records WHERE is_deleted = 0"
    params = []
    
    if filter_type != 'all':
        query += " AND service_type = ?"
        params.append(filter_type)
        
    if search_query:
        query += " AND (name LIKE ? OR phone LIKE ? OR service_no LIKE ? OR address LIKE ?)"
        s_param = f"%{search_query}%"
        params.extend([s_param, s_param, s_param, s_param])
        
    cursor.execute(query, params)
    records = cursor.fetchall()
    
    cursor.execute("SELECT * FROM records WHERE is_deleted = 1")
    trash_records = cursor.fetchall()
    
    cursor.execute("SELECT * FROM users WHERE status = 'Pending'")
    pending_users = cursor.fetchall()

    cursor.execute("SELECT * FROM users")
    all_users = cursor.fetchall()

    cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT 20")
    history_logs = cursor.fetchall()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (session['user'],))
    current_user_data = cursor.fetchone()

    conn.close()
    
    return render_template('index.html', page='dashboard', records=records, trash=trash_records, 
                           pending_users=pending_users, all_users=all_users, history_logs=history_logs,
                           role=session.get('role'), current_user=session.get('user'),
                           current_user_data=current_user_data,
                           total_count=total_count, tel_count=tel_count, 
                           tel_wifi_count=tel_wifi_count, wifi_count=wifi_count,
                           active_filter=filter_type)

@app.route('/add_record', methods=['POST'])
def add_record():
    name = request.form['name']
    phone = request.form['phone']
    service_type = request.form['service_type']
    service_no = request.form['service_no']
    address = request.form['address']
    note = request.form['note']
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    doc_file_name = ""
    if 'doc_file' in request.files:
        file = request.files['doc_file']
        if file.filename != '':
            doc_file_name = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], doc_file_name))
            
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO records (name, phone, service_type, service_no, address, note, doc_file, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                   (name, phone, service_type, service_no, address, note, doc_file_name, time_now))
    
    cursor.execute("INSERT INTO history (action, username, timestamp) VALUES (?, ?, ?)",
                   (f"Added record: {name}", session['user'], time_now))
                   
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/approve_user/<int:user_id>')
def approve_user(user_id):
    if session.get('user') != 'Khushbu23':
        return "Access Denied!"
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'Active' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('user') != 'Khushbu23':
        return "Access Denied!"
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    target = cursor.fetchone()
    if target and target[0] == 'Khushbu23':
        conn.close()
        return "রিয়েল এডমিনের আইডি ডিলিট করা নিষিদ্ধ!"
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_record/<int:rec_id>')
def delete_record(rec_id):
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET is_deleted = 1 WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/recover_record/<int:rec_id>')
def recover_record(rec_id):
    if session.get('user') != 'Khushbu23':
        return "Access Denied!"
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET is_deleted = 0 WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            conn = sqlite3.connect('btcl_database.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (filename, session['user']))
            conn.commit()
            conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)