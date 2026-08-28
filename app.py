import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_NAME = "database.db"

# ---------------------------------------------------------
# ডাটাবেস ইনিশিয়ালাইজেশন
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_approved INTEGER DEFAULT 0
        )
    ''')
    
    # Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            phone TEXT,
            address TEXT NOT NULL,
            amount TEXT NOT NULL,
            is_deleted INTEGER DEFAULT 0
        )
    ''')
    
    # ডিফল্ট অ্যাডমিন
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (name, email, phone, username, password, is_admin, is_approved)
            VALUES ('Md.Khushbu Alom', 'admin@btcl.com', '01751947523', 'admin', 'admin123', 1, 1)
        ''')
    
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# ডার্ক থিম ফ্রন্টএন্ড UI (আপনার স্ক্রিনশট অনুযায়ী)
# ---------------------------------------------------------
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>বিটিসিএল (BTCL), কুড়িগ্রাম</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: #121212; color: #ffffff; padding: 15px; }
        
        .header-title { color: #00ff66; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 5px; }
        .welcome-subtitle { color: #cccccc; text-align: center; font-size: 15px; margin-bottom: 15px; }
        .green-line { height: 2px; background-color: #00ff66; margin-bottom: 20px; width: 100%; }
        
        .auth-container { background: #1e1e1e; padding: 20px; border-radius: 12px; max-width: 450px; margin: 0 auto; border: 1px solid #2a2a2a; }
        .tab-buttons { display: flex; gap: 10px; margin-bottom: 20px; }
        .tab-btn { flex: 1; padding: 12px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 15px; }
        .btn-active { background-color: #00e65c; color: #000; }
        .btn-inactive { background-color: #2a2a2a; color: #ffffff; }
        
        .input-box { width: 100%; padding: 14px; margin-bottom: 12px; background-color: #2a2a2a; border: 1px solid #333; border-radius: 8px; color: #fff; font-size: 15px; }
        .input-box::placeholder { color: #888; }
        .submit-btn { width: 100%; padding: 14px; background-color: #00e65c; color: #000; font-weight: bold; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-top: 10px; }
        
        .menu-title { color: #888; font-size: 14px; margin-bottom: 10px; }
        .menu-list { display: flex; flex-direction: column; gap: 10px; margin-bottom: 25px; }
        .menu-item { background: #1e1e1e; padding: 15px; border-radius: 8px; font-size: 16px; font-weight: 500; cursor: pointer; display: flex; align-items: center; gap: 10px; }
        .menu-item.active { background: #00e65c; color: #000; font-weight: bold; }
        
        .logout-btn { width: 100%; padding: 15px; background-color: #ff4d4d; color: white; font-weight: bold; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; margin-bottom: 30px; }
        
        .section-header { font-size: 20px; font-weight: bold; margin-bottom: 15px; }
        .stat-card { background: #1e1e1e; padding: 20px; border-radius: 12px; text-align: center; border-left: 4px solid #00e65c; }
        .stat-card p { color: #aaa; font-size: 14px; margin-bottom: 10px; }
        .stat-card h1 { font-size: 36px; color: #00e65c; }
        
        .hidden { display: none; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; background: #1e1e1e; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #2a2a2a; font-size: 14px; }
        th { background-color: #2a2a2a; color: #00e65c; }
    </style>
</head>
<body>

    <div class="header-title">বাংলাদেশ টেলিকমিউনিকেশনস কোম্পানী লিমিটেড (বিটিসিএল), কুড়িগ্রাম</div>
    <div class="welcome-subtitle" id="top-sub">Welcome Md. Khushbu Alom (Admin)</div>
    <div class="green-line"></div>

    <!-- লগইন ও রেজিস্ট্রেশন ভিউ -->
    <div id="auth-view" class="auth-container hidden">
        <div class="tab-buttons">
            <button id="tab-login" class="tab-btn btn-active" onclick="toggleAuth('login')">লগইন</button>
            <button id="tab-reg" class="tab-btn btn-inactive" onclick="toggleAuth('reg')">রেজিস্ট্রেশন</button>
        </div>

        <form id="login-form" onsubmit="handleLogin(event)">
            <input type="text" id="l_user" class="input-box" placeholder="মোবাইল নম্বর বা ইউজার নেম" required>
            <input type="password" id="l_pass" class="input-box" placeholder="পাসওয়ার্ড" required>
            <button type="submit" class="submit-btn">লগইন করুন</button>
        </form>

        <form id="reg-form" class="hidden" onsubmit="handleReg(event)">
            <input type="text" id="r_name" class="input-box" placeholder="আপনার নাম" required>
            <input type="email" id="r_email" class="input-box" placeholder="জিচেইল আইডি" required>
            <input type="text" id="r_phone" class="input-box" placeholder="মোবাইল নম্বর" required>
            <input type="text" id="r_uname" class="input-box" placeholder="নতুন ইউজার নেম" required>
            <input type="password" id="r_pass" class="input-box" placeholder="পাসওয়ার্ড" required>
            <button type="submit" class="submit-btn">একাউন্ট তৈরি করুন</button>
        </form>
    </div>

    <!-- অ্যাডমিন ড্যাশবোর্ড ভিউ -->
    <div id="dashboard-view">
        <div class="menu-title">মেনু বার</div>
        <div class="menu-list">
            <div class="menu-item active">📊 ওভারভিউ ও সার্চ</div>
            <div class="menu-item">➕ ১. নম্বর এড করুন</div>
            <div class="menu-item">⏳ ২. পেন্ডিং ইউজার</div>
            <div class="menu-item">👥 ৩. সকল ইউজার তথ্য</div>
            <div class="menu-item">❌ ৪. ইউজার ডিলিট</div>
            <div class="menu-item">📋 ৫. সকল গ্রাহক তালিকা</div>
            <div class="menu-item">🗑️ রিসাইকেল বিন</div>
        </div>

        <button class="logout-btn" onclick="logout()">লগআউট</button>

        <div class="section-header">টোটাল সংযোগ ও বিলের হিসাব</div>
        <div class="stat-card">
            <p>মোট গ্রাহক সংযোগ</p>
            <h1 id="total-count">0</h1>
        </div>
    </div>

    <script>
        function toggleAuth(type) {
            if(type === 'login') {
                document.getElementById('tab-login').className = 'tab-btn btn-active';
                document.getElementById('tab-reg').className = 'tab-btn btn-inactive';
                document.getElementById('login-form').classList.remove('hidden');
                document.getElementById('reg-form').classList.add('hidden');
            } else {
                document.getElementById('tab-login').className = 'tab-btn btn-inactive';
                document.getElementById('tab-reg').className = 'tab-btn btn-active';
                document.getElementById('login-form').classList.add('hidden');
                document.getElementById('reg-form').classList.remove('hidden');
            }
        }

        function handleLogin(e) {
            e.preventDefault();
            document.getElementById('auth-view').classList.add('hidden');
            document.getElementById('dashboard-view').classList.remove('hidden');
        }

        function handleReg(e) {
            e.preventDefault();
            alert('রেজিস্ট্রেশন জমা হয়েছে! অ্যাডমিন এপ্রুভালের অপেক্ষা করুন।');
            toggleAuth('login');
        }

        function logout() {
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('auth-view').classList.remove('hidden');
        }
    </script>
</body>
</html>
"""

# ---------------------------------------------------------
# মূল রাউট
# ---------------------------------------------------------
@app.route('/')
def index():
    return render_template_string(HTML_LAYOUT)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)