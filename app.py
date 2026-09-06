from flask import Flask, render_template, request, redirect, url_for, session, jsonify
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

def init_db():
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, email TEXT, phone TEXT, 
                        username TEXT UNIQUE, password TEXT, 
                        role TEXT DEFAULT 'user',
                        status TEXT DEFAULT 'Pending',
                        profile_pic TEXT DEFAULT 'default.png',
                        assigned_upazila TEXT DEFAULT 'All',
                        last_active TEXT)''')
                        
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        action TEXT,
                        timestamp TEXT)''')

    # রিয়েল এডমিন নিশ্চিতকরণ
    cursor.execute("SELECT * FROM users WHERE username = 'Khushbu23'")
    if not cursor.fetchone():
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users (name, email, phone, username, password, role, status, profile_pic, assigned_upazila, last_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       ("Real Admin", "admin@btcl.com", "01751947523", "Khushbu23", "01751947523", "super_admin", "Active", "default.png", "All", time_now))
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS upazilas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE)''')
                        
    default_upazilas = ['ফুলবাড়ী', 'রাজারহাট', 'উলিপুর', 'চিলমারী', 'রৌমারী', 'রাজিবপুর', 'নাগেশ্বরী', 'ভুরুঙ্গামারী']
    for upa in default_upazilas:
        cursor.execute("INSERT OR IGNORE INTO upazilas (name) VALUES (?)", (upa,))

    cursor.execute('''CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        upazila TEXT DEFAULT 'District HQ',
                        name TEXT, phone TEXT, service_type TEXT, 
                        service_no TEXT, address TEXT, note TEXT, 
                        doc_file TEXT, is_deleted INTEGER DEFAULT 0,
                        created_at TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender TEXT, message TEXT, msg_type TEXT DEFAULT 'single',
                        timestamp TEXT)''')

    conn.commit()
    conn.close()

init_db()

def log_user_action(user_id, action):
    try:
        conn = sqlite3.connect('btcl_database.db')
        cursor = conn.cursor()
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)", (user_id, action, time_now))
        conn.commit()
        conn.close()
    except:
        pass

def get_all_upazilas():
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM upazilas ORDER BY name ASC")
    res = [row[0] for row in cursor.fetchall()]
    conn.close()
    return res

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html', page='login')

@app.route('/register_page')
def register_page():
    upazilas = get_all_upazilas()
    return render_template('index.html', page='register', upazilas=upazilas)

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    username = request.form['username']
    password = request.form['password']
    pref_type = request.form['pref_type']
    pref_upazila = request.form.get('pref_upazila', 'All') if pref_type == 'Upazila' else 'District'
    
    try:
        conn = sqlite3.connect('btcl_database.db')
        cursor = conn.cursor()
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users (name, email, phone, username, password, role, status, profile_pic, assigned_upazila, last_active) VALUES (?, ?, ?, ?, ?, 'user', 'Pending', 'default.png', ?, ?)",
                       (name, email, phone, username, password, pref_upazila, time_now))
        conn.commit()
        conn.close()
        return "রেজিস্ট্রেশন রিকোয়েস্ট সফলভাবে জমা হয়েছে। রিয়েল বা সহকারী এডমিন এক্সেপ্ট করলে লগইন করতে পারবেন।"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/create_user_by_admin', methods=['POST'])
def create_user_by_admin():
    if 'user' not in session or session.get('role') != 'super_admin':
        return "Access Denied!"
    
    name = request.form['name']
    username = request.form['username']
    phone = request.form['phone']
    email = request.form['email']
    password = request.form['password']
    role = request.form['role']
    assigned_upazila = request.form.get('assigned_upazila', 'All')
        
    try:
        conn = sqlite3.connect('btcl_database.db')
        cursor = conn.cursor()
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO users (name, email, phone, username, password, role, status, profile_pic, assigned_upazila, last_active) VALUES (?, ?, ?, ?, ?, ?, 'Active', 'default.png', ?, ?)",
                       (name, email, phone, username, password, role, assigned_upazila, time_now))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    
    if user:
        if user[7] != 'Active' and username != 'Khushbu23':
            conn.close()
            return "আপনার অ্যাকাউন্টটি এখনো এডমিন কর্তৃক অনুমোদিত হয়নি!"
                
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE users SET last_active = ? WHERE username = ?", (time_now, username))
        conn.commit()
        conn.close()
        
        log_user_action(user[0], "লগইন করেছেন")
        session['user'] = user[4]
        session['role'] = user[6]
        session['assigned_upazila'] = user[9]
        return redirect(url_for('dashboard'))
    conn.close()
    return "ভুল ইউজারনেম অথবা পাসওয়ার্ড!"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    filter_type = request.args.get('filter', 'all')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'az')
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND upazila = 'District HQ'")
    total_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND upazila = 'District HQ' AND service_type = 'Telephone'")
    tel_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND upazila = 'District HQ' AND service_type = 'Tel+WiFi'")
    tel_wifi_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND upazila = 'District HQ' AND service_type = 'WiFi'")
    wifi_count = cursor.fetchone()[0]
    
    query = "SELECT * FROM records WHERE is_deleted = 0 AND upazila = 'District HQ'"
    params = []
    
    if filter_type != 'all':
        query += " AND service_type = ?"
        params.append(filter_type)
        
    if search_query:
        query += " AND (name LIKE ? OR phone LIKE ? OR service_no LIKE ? OR address LIKE ?)"
        s_param = f"%{search_query}%"
        params.extend([s_param, s_param, s_param, s_param])
        
    if sort_by == 'za':
        query += " ORDER BY service_no DESC, name DESC"
    else:
        query += " ORDER BY service_no ASC, name ASC"
        
    cursor.execute(query, params)
    records = cursor.fetchall()
    
    cursor.execute("SELECT * FROM users WHERE status = 'Pending'")
    pending_users = cursor.fetchall()

    cursor.execute("SELECT * FROM users")
    all_users = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM users WHERE assigned_upazila = 'District' OR assigned_upazila = 'All'")
    district_users_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE assigned_upazila != 'District' AND assigned_upazila != 'All'")
    upazila_users_count = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM messages WHERE msg_type = 'group' ORDER BY id DESC LIMIT 5")
    group_notices = cursor.fetchall()

    cursor.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 50")
    messages = cursor.fetchall()
    
    cursor.execute("SELECT DISTINCT sender FROM messages WHERE sender != ?", (session.get('user'),))
    chat_senders = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (session.get('user'),))
    current_user_data = cursor.fetchone()

    conn.close()
    upazilas = get_all_upazilas()
    
    return render_template('index.html', page='dashboard', records=records, 
                           pending_users=pending_users, all_users=all_users, messages=messages,
                           group_notices=group_notices, chat_senders=chat_senders,
                           current_user_data=current_user_data, upazilas=upazilas,
                           total_count=total_count, tel_count=tel_count, 
                           tel_wifi_count=tel_wifi_count, wifi_count=wifi_count,
                           active_filter=filter_type, district_users_count=district_users_count,
                           upazila_users_count=upazila_users_count)

@app.route('/upazila/<upazila_name>')
def upazila_page(upazila_name):
    if 'user' not in session:
        return redirect(url_for('index'))
        
    filter_type = request.args.get('filter', 'all')
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort', 'az')
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    
    query = "SELECT * FROM records WHERE is_deleted = 0 AND upazila = ?"
    params = [upazila_name]
    
    if filter_type != 'all':
        query += " AND service_type = ?"
        params.append(filter_type)
        
    if search_query:
        query += " AND (name LIKE ? OR phone LIKE ? OR service_no LIKE ? OR address LIKE ?)"
        s_param = f"%{search_query}%"
        params.extend([s_param, s_param, s_param, s_param])
        
    if sort_by == 'za':
        query += " ORDER BY service_no DESC, name DESC"
    else:
        query += " ORDER BY service_no ASC, name ASC"
        
    cursor.execute(query, params)
    records = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND upazila = ?", (upazila_name,))
    total_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND upazila = ? AND service_type = 'Telephone'", (upazila_name,))
    tel_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND upazila = ? AND service_type = 'Tel+WiFi'", (upazila_name,))
    tel_wifi_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM records WHERE is_deleted = 0 AND upazila = ? AND service_type = 'WiFi'", (upazila_name,))
    wifi_count = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM users WHERE username = ?", (session.get('user'),))
    current_user_data = cursor.fetchone()

    cursor.execute("SELECT * FROM messages WHERE msg_type = 'group' ORDER BY id DESC LIMIT 5")
    group_notices = cursor.fetchall()

    cursor.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 50")
    messages = cursor.fetchall()

    conn.close()
    upazilas = get_all_upazilas()

    return render_template('index.html', page='upazila_page', records=records, 
                           selected_upazila=upazila_name, upazilas=upazilas,
                           current_user_data=current_user_data, messages=messages,
                           group_notices=group_notices, total_count=total_count, 
                           tel_count=tel_count, tel_wifi_count=tel_wifi_count, 
                           wifi_count=wifi_count, active_filter=filter_type)

@app.route('/get_user_history/<int:user_id>')
def get_user_history(user_id):
    if session.get('role') != 'super_admin':
        return jsonify([])
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, action FROM user_logs WHERE user_id = ? ORDER BY id DESC LIMIT 20", (user_id,))
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)

@app.route('/add_upazila', methods=['POST'])
def add_upazila():
    if session.get('role') == 'user':
        return "Access Denied!"
    up_name = request.form['upazila_name'].strip()
    if up_name:
        try:
            conn = sqlite3.connect('btcl_database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO upazilas (name) VALUES (?)", (up_name,))
            conn.commit()
            conn.close()
        except:
            pass
    return redirect(url_for('dashboard'))

@app.route('/add_record', methods=['POST'])
def add_record():
    if session.get('role') == 'user':
        return "Access Denied!"
    upazila = request.form.get('upazila', 'District HQ')
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
    cursor.execute("INSERT INTO records (upazila, name, phone, service_type, service_no, address, note, doc_file, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (upazila, name, phone, service_type, service_no, address, note, doc_file_name, time_now))
    conn.commit()
    conn.close()
    
    if upazila != 'District HQ':
        return redirect(url_for('upazila_page', upazila_name=upazila))
    return redirect(url_for('dashboard'))

@app.route('/update_record', methods=['POST'])
def update_record():
    if session.get('role') == 'user':
        return "Access Denied!"
    rec_id = request.form['rec_id']
    name = request.form['name']
    phone = request.form['phone']
    service_type = request.form['service_type']
    service_no = request.form['service_no']
    address = request.form['address']
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT upazila FROM records WHERE id = ?", (rec_id,))
    res = cursor.fetchone()
    upa = res[0] if res else 'District HQ'
    
    if 'doc_file' in request.files:
        file = request.files['doc_file']
        if file.filename != '':
            doc_file_name = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], doc_file_name))
            cursor.execute("UPDATE records SET name=?, phone=?, service_type=?, service_no=?, address=?, doc_file=? WHERE id=?",
                           (name, phone, service_type, service_no, address, doc_file_name, rec_id))
        else:
            cursor.execute("UPDATE records SET name=?, phone=?, service_type=?, service_no=?, address=? WHERE id=?",
                           (name, phone, service_type, service_no, address, rec_id))
    conn.commit()
    conn.close()
    
    if upa != 'District HQ':
        return redirect(url_for('upazila_page', upazila_name=upa))
    return redirect(url_for('dashboard'))

@app.route('/delete_record', methods=['POST'])
def delete_record():
    if session.get('role') == 'user' or session.get('role') == 'editor_admin':
        return "Access Denied!"
    rec_id = request.form['rec_id']
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET is_deleted = 1 WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/approve_user/<int:user_id>')
def approve_user(user_id):
    if session.get('role') != 'super_admin':
        return "Access Denied!"
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'Active' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if session.get('role') != 'super_admin':
        return "Access Denied!"
    user_id = request.form['user_id']
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    target = cursor.fetchone()
    if target and target[0] == 'Khushbu23':
        conn.close()
        return "রিয়েল এডমিনের আইডি ডিলিট করা নিষেধ!"
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session:
        return redirect(url_for('index'))
    message = request.form['message']
    msg_type = request.form.get('msg_type', 'single')
    
    if msg_type == 'group' and session.get('role') == 'user':
        return "সাধারণ ইউজাররা গ্রুপ নোটিশ পাঠাতে পারবে না।"
        
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, message, msg_type, timestamp) VALUES (?, ?, ?, ?)",
                   (session.get('user'), message, msg_type, time_now))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('dashboard'))

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
            cursor.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (filename, session.get('user')))
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