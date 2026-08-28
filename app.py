import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_NAME = "database.db"

# ---------------------------------------------------------
# ডাটাবেস সেটআপ
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT, username TEXT UNIQUE, password TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, service TEXT, phone TEXT, amount TEXT, address TEXT, note TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# ভিডিও অনুযায়ী সাইডবার ও ইউজার ইন্টারফেস (UI)
# ---------------------------------------------------------
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>বিটিসিএল (BTCL), কুড়িগ্রাম</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
        body { background-color: #121212; color: #ffffff; padding: 12px; }

        /* হেডার */
        .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
        .menu-btn { font-size: 24px; color: #00ff66; background: none; border: none; cursor: pointer; }
        .header-title { color: #00ff66; font-size: 16px; font-weight: bold; background: #1e1e1e; padding: 6px 12px; border-radius: 6px; border: 1px solid #2a2a2a; }
        
        /* সার্চ বক্স */
        .search-container { position: relative; margin-bottom: 15px; }
        .search-box { width: 100%; padding: 12px 15px 12px 35px; background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 20px; color: #fff; font-size: 14px; }
        .search-icon { position: absolute; left: 12px; top: 12px; color: #888; }

        /* সাইডবার / ড্রয়ার মেনু */
        .sidebar { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: #1e1e1e; z-index: 1000; transition: 0.3s; padding: 15px; border-right: 1px solid #333; box-shadow: 5px 0 15px rgba(0,0,0,0.5); }
        .sidebar.active { left: 0; }
        .close-btn { color: #ff4d4d; background: none; border: none; font-size: 16px; cursor: pointer; float: right; font-weight: bold; }
        
        .menu-title { color: #888; font-size: 13px; margin: 20px 0 10px 0; }
        .menu-list { display: flex; flex-direction: column; gap: 8px; }
        .menu-item { background: #2a2a2a; color: #fff; padding: 12px; border-radius: 6px; font-size: 14px; text-decoration: none; display: block; border: none; text-align: left; width: 100%; cursor: pointer; }
        .menu-item.active { background: #00e65c; color: #000; font-weight: bold; }
        .logout-btn { background: #ff4d4d; color: #fff; width: 100%; padding: 12px; border-radius: 6px; border: none; margin-top: 20px; font-weight: bold; cursor: pointer; }

        /* কার্ড থিম */
        .card { background: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #2a2a2a; margin-bottom: 15px; }
        .card-title { font-size: 15px; font-weight: bold; text-align: center; margin-bottom: 12px; }
        
        .grid-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center; }
        .stat-box { background: #2a2a2a; padding: 10px; border-radius: 8px; }
        .stat-box.green { background: #003311; border: 1px solid #00e65c; grid-column: span 2; }
        .stat-box h2 { color: #00ff66; margin-top: 5px; font-size: 18px; }
        .stat-box p { font-size: 12px; color: #ccc; }

        /* ইনপুট ফিল্ড ও বাটন */
        .input-box { width: 100%; padding: 12px; margin-bottom: 10px; background: #2a2a2a; border: 1px solid #333; border-radius: 6px; color: #fff; font-size: 14px; }
        .submit-btn { width: 100%; padding: 12px; background: #00e65c; color: #000; font-weight: bold; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; }

        /* লগইন / রেজিস্ট্রেশন ট্যাব */
        .auth-container { max-width: 400px; margin: 40px auto; background: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #2a2a2a; }
        .tab-buttons { display: flex; gap: 10px; margin-bottom: 15px; }
        .tab-btn { flex: 1; padding: 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        
        .hidden { display: none !important; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 999; display: none; }
        .overlay.active { display: block; }
    </style>
</head>
<body>

    <!-- ওভারলে -->
    <div id="overlay" class="overlay" onclick="closeSidebar()"></div>

    <!-- সাইডবার ড্রয়ার -->
    <div id="sidebar" class="sidebar">
        <button class="close-btn" onclick="closeSidebar()">✖ বন্ধ করুন</button>
        <div style="clear:both;"></div>
        <div class="menu-title">মেনু বার</div>
        <div class="menu-list">
            <button class="menu-item active" onclick="navTo('sec-overview', this)">📊 ওভারভিউ ও ডাটা</button>
            <button class="menu-item" onclick="navTo('sec-add', this)">➕ ১. নম্বর এড করুন</button>
            <button class="menu-item" onclick="navTo('sec-pending', this)">⏳ ২. পেন্ডিং ইউজার</button>
            <button class="menu-item" onclick="navTo('sec-users', this)">👥 ৩. সকল ইউজার তথ্য</button>
            <button class="menu-item" onclick="navTo('sec-delete', this)">❌ ৪. ইউজার ডিলিট</button>
            <button class="menu-item" onclick="navTo('sec-customers', this)">📋 ৬. সকল গ্রাহক তালিকা</button>
            <button class="menu-item" onclick="navTo('sec-recycle', this)">🗑️ রিসাইকেল বিন</button>
            <button class="menu-item" onclick="navTo('sec-messenger', this)">💬 মেসেঞ্জার</button>
        </div>
        <button class="logout-btn" onclick="logout()">লগআউট</button>
    </div>

    <!-- অথেনটিকেশন পেজ (লগইন / রেজিস্ট্রেশন) -->
    <div id="auth-view" class="auth-container">
        <div style="color:#00ff66; text-align:center; font-weight:bold; font-size:18px; margin-bottom:15px;">বিটিসিএল (BTCL), কুড়িগ্রাম</div>
        <div class="tab-buttons">
            <button id="btn-tab-login" class="tab-btn" style="background:#00e65c; color:#000;" onclick="toggleAuthTab('login')">লগইন</button>
            <button id="btn-tab-reg" class="tab-btn" style="background:#2a2a2a; color:#fff;" onclick="toggleAuthTab('reg')">রেজিস্ট্রেশন</button>
        </div>

        <form id="form-login" onsubmit="doLogin(event)">
            <input type="text" class="input-box" placeholder="ইউজারনেম / জিমেইল / ফোন" required>
            <input type="password" class="input-box" placeholder="পাসওয়ার্ড" required>
            <button type="submit" class="submit-btn">লগইন করুন</button>
        </form>

        <form id="form-reg" class="hidden" onsubmit="doRegister(event)">
            <input type="text" class="input-box" placeholder="আপনার নাম" required>
            <input type="email" class="input-box" placeholder="জিমেইল আইডি" required>
            <input type="text" class="input-box" placeholder="মোবাইল নম্বর" required>
            <input type="text" class="input-box" placeholder="ইউজারনেম" required>
            <input type="password" class="input-box" placeholder="পাসওয়ার্ড" required>
            <input type="password" class="input-box" placeholder="কনফার্ম পাসওয়ার্ড" required>
            <button type="submit" class="submit-btn">একাউন্ট তৈরি করুন</button>
        </form>
    </div>

    <!-- মূল ড্যাশবোর্ড -->
    <div id="dashboard-view" class="hidden">
        <div class="header">
            <button class="menu-btn" onclick="openSidebar()">☰</button>
            <div class="header-title">বিটিসিএল (BTCL), কুড়িগ্রাম</div>
            <div style="font-size: 20px;">🔔</div>
        </div>

        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" class="search-box" placeholder="নাম, মোবাইল, টেলিফোন, সেবা বা ঠিকানা দিয়ে খুঁজুন...">
        </div>

        <!-- ১. ওভারভিউ -->
        <div id="sec-overview">
            <div class="card">
                <div class="card-title">টোটাল সংযোগ ও বিলের হিসাব (ফিল্টার করতে ক্লিক করুন)</div>
                <div class="grid-stats">
                    <div class="stat-box green">
                        <p>মোট সংযোগ / টোটাল বিল</p>
                        <h2>0 (৳0)</h2>
                    </div>
                    <div class="stat-box">
                        <p>টেলিফোন নম্বর</p>
                        <h2>0</h2>
                    </div>
                    <div class="stat-box">
                        <p>টেলিফোন + ওয়াইফাই</p>
                        <h2>0</h2>
                    </div>
                    <div class="stat-box" style="grid-column: span 2;">
                        <p>ওয়াইফাই নম্বর</p>
                        <h2>0</h2>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-title" style="text-align:left;">সকল গ্রাহক নম্বর এর তালিকা</div>
                <p style="text-align:center; color:#888; font-size:13px; margin:15px 0;">কোনো রেকর্ড পাওয়া যায়নি</p>
            </div>
        </div>

        <!-- ২. নম্বর এড করুন -->
        <div id="sec-add" class="card hidden">
            <div class="card-title">নতুন তথ্য যুক্ত করুন</div>
            <form onsubmit="alert('ডাটা সংরক্ষণ করা হয়েছে!'); navTo('sec-overview'); return false;">
                <input type="text" class="input-box" placeholder="গ্রাহকের নাম" required>
                <select class="input-box" required>
                    <option value="">সেবা নির্বাচন করুন</option>
                    <option>টেলিফোন নম্বর</option>
                    <option>টেলিফোন+ওয়াইফাই নম্বর</option>
                    <option>ওয়াইফাই নম্বর</option>
                </select>
                <input type="text" class="input-box" placeholder="ফোন নম্বর" required>
                <input type="text" class="input-box" placeholder="বিল পরিমাণ (টাকা)" required>
                <input type="text" class="input-box" placeholder="ঠিকানা" required>
                <input type="text" class="input-box" placeholder="অতিরিক্ত তথ্য">
                <button type="submit" class="submit-btn">ডাটা সংরক্ষণ করুন</button>
            </form>
        </div>

        <!-- ৩. পেন্ডিং ইউজার -->
        <div id="sec-pending" class="card hidden">
            <div class="card-title">পেন্ডিং ইউজার পারমিশন রিকুয়েস্ট</div>
            <p style="text-align:center; color:#888; font-size:13px; margin:15px 0;">কোনো পেন্ডিং রিকুয়েস্ট নেই</p>
        </div>

        <!-- ৪. সকল ইউজার তথ্য -->
        <div id="sec-users" class="card hidden">
            <div class="card-title">সকল নিবন্ধিত ইউজার</div>
            <p style="text-align:center; color:#888; font-size:13px; margin:15px 0;">কোনো ইউজার ডাটা নেই</p>
        </div>

        <!-- ৫. ইউজার ডিলিট -->
        <div id="sec-delete" class="card hidden">
            <div class="card-title">ইউজার ডিলিট করুন</div>
            <p style="text-align:center; color:#888; font-size:13px; margin:15px 0;">কোনো ইউজার পাওয়া যায়নি</p>
        </div>

        <!-- ৬. সকল গ্রাহক তালিকা -->
        <div id="sec-customers" class="card hidden">
            <div class="card-title">সিরিয়াল করা গ্রাহক তালিকা</div>
            <p style="text-align:center; color:#888; font-size:13px; margin:15px 0;">কোনো রেকর্ড পাওয়া যায়নি</p>
        </div>

        <!-- ৭. রিসাইকেল বিন -->
        <div id="sec-recycle" class="card hidden">
            <div class="card-title">ডিলিট করা ফাইল (রিসাইকেল বিন)</div>
            <p style="text-align:center; color:#888; font-size:13px; margin:15px 0;">রিসাইকেল বিন ফাঁকা</p>
        </div>

        <!-- ৮. মেসেঞ্জার -->
        <div id="sec-messenger" class="card hidden">
            <div class="card-title" style="color:#00ff66;">💬 বিটিসিএল লাইভ মেসেঞ্জার</div>
            <div style="height:150px; border:1px solid #333; border-radius:6px; padding:10px; margin-bottom:10px; background:#121212;">
                <p style="text-align:center; color:#888; font-size:13px; margin-top:50px;">কোনো কথোপকথন নেই</p>
            </div>
            <div style="display:flex; gap:5px;">
                <input type="text" class="input-box" style="margin-bottom:0;" placeholder="এখানে মেসেজ লিখুন...">
                <button class="submit-btn" style="width:80px;">পাঠান</button>
            </div>
        </div>
    </div>

    <script>
        function openSidebar() {
            document.getElementById('sidebar').classList.add('active');
            document.getElementById('overlay').classList.add('active');
        }

        function closeSidebar() {
            document.getElementById('sidebar').classList.remove('active');
            document.getElementById('overlay').classList.remove('active');
        }

        function toggleAuthTab(tab) {
            if(tab === 'login') {
                document.getElementById('btn-tab-login').style.background = '#00e65c';
                document.getElementById('btn-tab-login').style.color = '#000';
                document.getElementById('btn-tab-reg').style.background = '#2a2a2a';
                document.getElementById('btn-tab-reg').style.color = '#fff';
                document.getElementById('form-login').classList.remove('hidden');
                document.getElementById('form-reg').classList.add('hidden');
            } else {
                document.getElementById('btn-tab-reg').style.background = '#00e65c';
                document.getElementById('btn-tab-reg').style.color = '#000';
                document.getElementById('btn-tab-login').style.background = '#2a2a2a';
                document.getElementById('btn-tab-login').style.color = '#fff';
                document.getElementById('form-reg').classList.remove('hidden');
                document.getElementById('form-login').classList.add('hidden');
            }
        }

        function doLogin(e) {
            e.preventDefault();
            document.getElementById('auth-view').classList.add('hidden');
            document.getElementById('dashboard-view').classList.remove('hidden');
        }

        function doRegister(e) {
            e.preventDefault();
            alert('রেজিস্ট্রেশন জমা হয়েছে!');
            toggleAuthTab('login');
        }

        function logout() {
            closeSidebar();
            document.getElementById('dashboard-view').classList.add('hidden');
            document.getElementById('auth-view').classList.remove('hidden');
        }

        function navTo(secId, btnEl) {
            closeSidebar();
            document.querySelectorAll('#dashboard-view > div[id^="sec-"]').forEach(d => d.classList.add('hidden'));
            document.getElementById(secId).classList.remove('hidden');

            if(btnEl) {
                document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
                btnEl.classList.add('active');
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_LAYOUT)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)