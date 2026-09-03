from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'btcl_kurigram_super_secret_key_2026'

SECURITY_PIN = "137955"  # আপনার দেওয়া সিকিউরিটি পাসওয়ার্ড

# ডেটাবেস এবং রিয়েল এডমিন ইনিশিয়ালাইজেশন
def init_db():
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    
    # ইউজার টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, email TEXT, phone TEXT, 
                        username TEXT UNIQUE, password TEXT, 
                        role TEXT DEFAULT 'user',
                        status TEXT DEFAULT 'Pending')''')
                        
    # ফিক্সড রিয়েল এডমিন তৈরি (ইউজারনেম: Khushbu23, পাসওয়ার্ড: 01751947523)
    cursor.execute("SELECT * FROM users WHERE username = 'Khushbu23'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, phone, username, password, role, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       ("Real Admin", "admin@btcl.com", "01751947523", "Khushbu23", "01751947523", "super_admin", "Active"))
    
    # নাম্বার এবং ডকুমেন্ট টেবিল (সফট ডিলিট সহ)
    cursor.execute('''CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, phone TEXT, service_type TEXT, 
                        service_no TEXT, address TEXT, note TEXT, 
                        doc_file TEXT, is_deleted INTEGER DEFAULT 0,
                        created_at TEXT)''')
                        
    # নোটিফিকেশন টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT, message TEXT, is_read INTEGER DEFAULT 0, timestamp TEXT)''')

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

# রেজিস্ট্রেশন হ্যান্ডেল (নতুন ইউজার বা সাব-এডমিন রিকোয়েস্ট)
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
        
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO notifications (title, message, timestamp) VALUES (?, ?, ?)",
                       ("নতুন অ্যাকাউন্ট রিকোয়েস্ট", f"{name} ({username}) একটি নতুন অ্যাকাউন্টের জন্য আবেদন করেছেন।", time_now))
        
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    except Exception as e:
        return f"Registration Error: Username already exists or invalid data! ({str(e)})"

# লগইন হ্যান্ডেল
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
        # স্ট্যাটাস পেন্ডিং থাকলে লগইন আটকে দেওয়া (রিয়েল এডমিন বাদে)
        if user[7] != 'Active' and username != 'Khushbu23':
            return "আপনার অ্যাকাউন্টটি এখনো রিয়েল এডমিন কর্তৃক অনুমোদিত (Active) হয়নি! দয়া করে অপেক্ষা করুন।"
                
        session['user'] = user[4]
        session['role'] = 'super_admin' if username == 'Khushbu23' else 'user'
        return redirect(url_for('dashboard'))
    return "ভুল ইউজারনেম অথবা পাসওয়ার্ড!"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM records WHERE is_deleted = 0")
    records = cursor.fetchall()
    
    cursor.execute("SELECT * FROM records WHERE is_deleted = 1")
    trash_records = cursor.fetchall()
    
    cursor.execute("SELECT * FROM users WHERE status = 'Pending'")
    pending_users = cursor.fetchall()

    cursor.execute("SELECT * FROM users")
    all_users = cursor.fetchall()
    
    cursor.execute("SELECT * FROM notifications WHERE is_read = 0")
    notifications = cursor.fetchall()
    
    conn.close()
    return render_template('index.html', page='dashboard', records=records, trash=trash_records, 
                           pending_users=pending_users, all_users=all_users, notifications=notifications, 
                           role=session.get('role'), current_user=session.get('user'))

# অ্যাকাউন্ট এপ্রুভ করার রুট (শুধুমাত্র রিয়েল এডমিন)
@app.route('/approve_user/<int:user_id>')
def approve_user(user_id):
    if session.get('user') != 'Khushbu23':
        return "Access Denied! শুধুমাত্র রিয়েল এডমিন অ্যাকাউন্ট এপ্রুভ করতে পারবেন।"
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'Active' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# ইউজার বা এডমিন ডিলেট করার রুট (শুধুমাত্র রিয়েল এডমিন করতে পারবে, ফিক্সড এডমিন Khushbu23 ডিলিট করা যাবে না)
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('user') != 'Khushbu23':
        return "Access Denied!"
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    target_user = cursor.fetchone()
    if target_user and target_user[0] == 'Khushbu23':
        conn.close()
        return "রিয়েল এডমিনের আইডি কখনো ডিলিট করা যাবে না!"
    
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# নাম্বার এড করার রুট
@app.route('/add_record', methods=['POST'])
def add_record():
    name = request.form['name']
    phone = request.form['phone']
    service_type = request.form['service_type']
    service_no = request.form['service_no']
    address = request.form['address']
    note = request.form['note']
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO records (name, phone, service_type, service_no, address, note, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (name, phone, service_type, service_no, address, note, time_now))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# সফট ডিলিট (নাম্বার ট্র্যাশ বিনে পাঠানো)
@app.route('/delete_record/<int:rec_id>')
def delete_record(rec_id):
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET is_deleted = 1 WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# রিকভার রেকর্ড (শুধুমাত্র রিয়েল এডমিন রিসাইকেল বিন থেকে রিকভার করতে পারবে)
@app.route('/recover_record/<int:rec_id>')
def recover_record(rec_id):
    if session.get('user') != 'Khushbu23':
        return "অনুমতি নেই! শুধুমাত্র রিয়েল এডমিন ডিলিট করা নাম্বার রিকভার করতে পারবেন।"
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET is_deleted = 0 WHERE id = ?", (rec_id,))
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