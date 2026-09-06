from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'btcl_kurigram_super_secret_key_2026'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
SECURITY_PIN = '137955'

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
                        profile_pic TEXT DEFAULT 'default.png')''')
                        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_pic TEXT DEFAULT 'default.png'")
    except:
        pass

    cursor.execute("SELECT * FROM users WHERE username = 'Khushbu23'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, phone, username, password, role, status, profile_pic) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       ("Real Admin", "admin@btcl.com", "01751947523", "Khushbu23", "01751947523", "super_admin", "Active", "default.png"))
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS upazilas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE)''')
                        
    # ডিফল্ট কিছু উপজেলা যোগ করে দেওয়া
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
                        
    try:
        cursor.execute("ALTER TABLE records ADD COLUMN upazila TEXT DEFAULT 'District HQ'")
    except:
        pass

    cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action TEXT, username TEXT, timestamp TEXT)''')

    conn.commit()
    conn.close()

init_db()

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
    return render_template('index.html', page='register')

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    username = request.form['username']
    password = request.form['password']
    sec_pin = request.form['security_pin']
    
    if sec_pin != SECURITY_PIN:
        return "ভুল সিকিউরিটি পাসওয়ার্ড! সঠিক সিকিউরিটি পিন দিন।"
    
    try:
        conn = sqlite3.connect('btcl_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, phone, username, password, role, status, profile_pic) VALUES (?, ?, ?, ?, ?, 'user', 'Pending', 'default.png')",
                       (name, email, phone, username, password))
        conn.commit()
        conn.close()
        return "সফলভাবে রেজিস্ট্রেশন রিকোয়েস্ট পাঠানো হয়েছে। রিয়েল এডমিন এপ্রুভ করলে লগইন করতে পারবেন।"
    except Exception as e:
        return f"Registration Error: {str(e)}"

@app.route('/create_user_by_admin', methods=['POST'])
def create_user_by_admin():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    name = request.form['name']
    username = request.form['username']
    phone = request.form['phone']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    sec_pin = request.form['security_pin']
    role = request.form['role']
    
    if password != confirm_password:
        return "পাসওয়ার্ড এবং কনফার্ম পাসওয়ার্ড মিলছে না!"
        
    if sec_pin != SECURITY_PIN:
        return "ভুল সিকিউরিটি পাসওয়ার্ড (137955)!"
        
    try:
        conn = sqlite3.connect('btcl_database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, phone, username, password, role, status, profile_pic) VALUES (?, ?, ?, ?, ?, ?, 'Active', 'default.png')",
                       (name, email, phone, username, password, role))
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
    sort_by = request.args.get('sort', 'az') # az = ছোট থেকে বড়, za = বড় থেকে ছোট
    
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
        
    # ছোট সংখ্যা থেকে বড় (A-Z) অথবা বড় সংখ্যা থেকে ছোট (Z-A) সংযোগ নম্বর/নাম অনুযায়ী সর্টিং
    if sort_by == 'za':
        query += " ORDER BY service_no DESC, name DESC"
    else:
        query += " ORDER BY service_no ASC, name ASC"
        
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
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (session.get('user'),))
    current_user_data = cursor.fetchone()
    if not current_user_data:
        current_user_data = (0, 'User', '', '', session.get('user'), '', 'user', 'Active', 'default.png')

    conn.close()
    
    upazilas = get_all_upazilas()
    
    return render_template('index.html', page='dashboard', records=records, trash=trash_records, 
                           pending_users=pending_users, all_users=all_users, history_logs=history_logs,
                           role=session.get('role'), current_user=session.get('user'),
                           current_user_data=current_user_data, upazilas=upazilas,
                           total_count=total_count, tel_count=tel_count, 
                           tel_wifi_count=tel_wifi_count, wifi_count=wifi_count,
                           active_filter=filter_type)

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
    if not current_user_data:
        current_user_data = (0, 'User', '', '', session.get('user'), '', 'user', 'Active', 'default.png')

    cursor.execute("SELECT * FROM history ORDER BY id DESC LIMIT 20")
    history_logs = cursor.fetchall()

    conn.close()
    
    upazilas = get_all_upazilas()

    return render_template('index.html', page='upazila_page', records=records, 
                           selected_upazila=upazila_name, upazilas=upazilas,
                           current_user_data=current_user_data, history_logs=history_logs,
                           total_count=total_count, tel_count=tel_count,
                           tel_wifi_count=tel_wifi_count, wifi_count=wifi_count,
                           active_filter=filter_type)

@app.route('/add_upazila', methods=['POST'])
def add_upazila():
    if 'user' not in session:
        return redirect(url_for('index'))
    up_name = request.form['upazila_name'].strip()
    if up_name:
        try:
            conn = sqlite3.connect('btcl_database.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO upazilas (name) VALUES (?)", (up_name,))
            time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO history (action, username, timestamp) VALUES (?, ?, ?)",
                           (f"Added new Upazila: {up_name}", session.get('user'), time_now))
            conn.commit()
            conn.close()
        except:
            pass
    return redirect(url_for('dashboard'))

@app.route('/add_record', methods=['POST'])
def add_record():
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
    
    cursor.execute("INSERT INTO history (action, username, timestamp) VALUES (?, ?, ?)",
                   (f"Added record in {upazila}: {name} ({service_no})", session.get('user'), time_now))
                   
    conn.commit()
    conn.close()
    
    if upazila != 'District HQ':
        return redirect(url_for('upazila_page', upazila_name=upazila))
    return redirect(url_for('dashboard'))

@app.route('/update_record', methods=['POST'])
def update_record():
    rec_id = request.form['rec_id']
    name = request.form['name']
    phone = request.form['phone']
    service_type = request.form['service_type']
    service_no = request.form['service_no']
    address = request.form['address']
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
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
    
    cursor.execute("INSERT INTO history (action, username, timestamp) VALUES (?, ?, ?)",
                   (f"Updated record ID: {rec_id}", session.get('user'), time_now))
                   
    conn.commit()
    conn.close()
    
    if upa != 'District HQ':
        return redirect(url_for('upazila_page', upazila_name=upa))
    return redirect(url_for('dashboard'))

@app.route('/approve_user/<int:user_id>')
def approve_user(user_id):
    if session.get('role') == 'user':
        return "Access Denied!"
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'Active' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form['user_id']
    sec_pin = request.form['security_pin']
    
    if sec_pin != SECURITY_PIN:
        return "ভুল সিকিউরিটি পাসওয়ার্ড! সঠিক পিন (137955) দিন।"
        
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

@app.route('/delete_record', methods=['POST'])
def delete_record():
    rec_id = request.form['rec_id']
    sec_pin = request.form['security_pin']
    
    if sec_pin != SECURITY_PIN:
        return "ভুল সিকিউরিটি পিন! সঠিক পিন (137955) দিয়ে ডিলিট করুন।"
        
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET is_deleted = 1 WHERE id = ?", (rec_id,))
    
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO history (action, username, timestamp) VALUES (?, ?, ?)",
                   (f"Deleted record ID: {rec_id}", session.get('user'), time_now))
                   
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/recover_record', methods=['POST'])
def recover_record():
    rec_id = request.form['rec_id']
    sec_pin = request.form['security_pin']
    
    if sec_pin != SECURITY_PIN:
        return "ভুল সিকিউরিটি পিন (137955)!"
        
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET is_deleted = 0 WHERE id = ?", (rec_id,))
    
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO history (action, username, timestamp) VALUES (?, ?, ?)",
                   (f"Recovered record ID: {rec_id}", session.get('user'), time_now))
                   
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