from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'btcl_kurigram_super_secret_key'

# ডেটাবেস ইনিশিয়ালাইজেশন
def init_db():
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    
    # ইউজার টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, email TEXT, phone TEXT, 
                        username TEXT UNIQUE, password TEXT, 
                        status TEXT DEFAULT 'Pending')''')
    
    # নাম্বার এবং ডকুমেন্ট টেবিল (সাথে সফট ডিলিট ও রিকভার অপশন)
    cursor.execute('''CREATE TABLE IF NOT EXISTS records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT, phone TEXT, service_type TEXT, 
                        service_no TEXT, address TEXT, note TEXT, 
                        doc_file TEXT, is_deleted INTEGER DEFAULT 0,
                        created_at TEXT)''')
                        
    # নোটিফিকেশন টেবিল
    cursor.execute('''CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT, message TEXT, link_type TEXT, 
                        is_read INTEGER DEFAULT 0, timestamp TEXT)''')

    # মেসেজ টেবিল (গ্রুপ এবং পার্সোনাল চ্যাট)
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        sender TEXT, receiver TEXT, message TEXT, 
                        is_broadcast INTEGER DEFAULT 0, timestamp TEXT)''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

# লগইন রাউট
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    # সুপার এডমিন হার্ডকোডেড চেক (বা ডেটাবেস চেক)
    if username == "Khushbu23" and password == "01751947523":
        session['user'] = username
        session['role'] = 'super_admin'
        return redirect(url_for('dashboard'))
        
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ? AND status = 'Active'", (username, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user'] = user[4] # username
        session['role'] = 'user'
        return redirect(url_for('dashboard'))
    return "Invalid Credentials or Account Not Approved!"

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    
    # ডাটা ফেচিং
    cursor.execute("SELECT * FROM records WHERE is_deleted = 0")
    records = cursor.fetchall()
    
    cursor.execute("SELECT * FROM records WHERE is_deleted = 1")
    trash_records = cursor.fetchall()
    
    cursor.execute("SELECT * FROM notifications WHERE is_read = 0")
    notifications = cursor.fetchall()
    
    cursor.execute("SELECT * FROM messages WHERE is_broadcast = 1")
    broadcasts = cursor.fetchall()
    
    conn.close()
    return render_template('index.html', records=records, trash=trash_records, notifications=notifications, broadcasts=broadcasts, role=session.get('role'))

# নাম্বার এড করার রাউট
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
                   
    # নোটিফিকেশন জেনারেট
    cursor.execute("INSERT INTO notifications (title, message, link_type, timestamp) VALUES (?, ?, ?, ?)",
                   ("New Number Added", f"{name} added a new service number.", "records", time_now))
                   
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# নাম্বার ডিলিট (সফট ডিলিট -> রিকভারির জন্য)
@app.route('/delete_record/<int:rec_id>')
def delete_record(rec_id):
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET is_deleted = 1 WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# সুপার এডমিন কর্তৃক ডিলিট হওয়া নাম্বার রিকভার (Restore)
@app.route('/recover_record/<int:rec_id>')
def recover_record(rec_id):
    if session.get('role') != 'super_admin':
        return "Access Denied! Only Super Admin can recover deleted records."
    
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE records SET is_deleted = 0 WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# নোটিফিকেশন রিড করলে কাউন্ট কমানোর API
@app.route('/read_notification/<int:notif_id>')
def read_notification(notif_id):
    conn = sqlite3.connect('btcl_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)