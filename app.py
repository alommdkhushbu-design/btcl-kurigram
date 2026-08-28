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
            name TEXT, email TEXT, phone TEXT UNIQUE, username TEXT UNIQUE, password TEXT, status TEXT DEFAULT 'approved'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, service_type TEXT, service_no TEXT, phone TEXT, amount REAL, address TEXT, note TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT, receiver TEXT, message TEXT, file_url TEXT, file_type TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # এডমিন একাউন্ট সেটআপ
    cursor.execute("SELECT * FROM users WHERE username='Khushbu23'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, phone, username, password, status) VALUES (?, ?, ?, ?, ?, ?)",
                       ("Admin Khushbu", "admin@btcl.gov.bd", "01751947523", "Khushbu23", "01751947523", "admin"))
    else:
        cursor.execute("UPDATE users SET password='01751947523', status='admin' WHERE username='Khushbu23'")
    
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# UI (HTML, CSS & JS)
# ---------------------------------------------------------
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
        body { background-color: #121212; color: #ffffff; padding: 12px; }

        .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
        .header-left { display: flex; align-items: center; gap: 10px; }
        .menu-btn, .group-btn { font-size: 16px; color: #00ff66; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; padding: 6px 12px; cursor: pointer; }
        .header-title { color: #00ff66; font-size: 15px; font-weight: bold; background: #1e1e1e; padding: 6px 12px; border-radius: 6px; border: 1px solid #2a2a2a; }
        
        .search-container { position: relative; margin-bottom: 15px; }
        .search-box { width: 100%; padding: 12px 15px 12px 35px; background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 20px; color: #fff; font-size: 14px; }
        .search-icon { position: absolute; left: 12px; top: 12px; color: #888; }

        /* সাইডবার (থ্রি ডট মেনু) */
        .sidebar { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: #1e1e1e; z-index: 1000; transition: 0.3s; padding: 15px; border-right: 1px solid #333; box-shadow: 5px 0 15px rgba(0,0,0,0.5); }
        .sidebar.active { left: 0; }
        .close-btn { color: #ff4d4d; background: none; border: none; font-size: 16px; cursor: pointer; float: right; font-weight: bold; }
        
        .menu-title { color: #888; font-size: 13px; margin: 20px 0 10px 0; font-weight: bold; }
        .menu-list { display: flex; flex-direction: column; gap: 8px; }
        .menu-item { background: #2a2a2a; color: #fff; padding: 12px; border-radius: 6px; font-size: 14px; border: none; text-align: left; width: 100%; cursor: pointer; display: flex; align-items: center; gap: 8px; }
        .menu-item.active { background: #00e65c; color: #000; font-weight: bold; }
        .logout-btn { background: #ff4d4d; color: #fff; width: 100%; padding: 12px; border-radius: 6px; border: none; margin-top: 20px; font-weight: bold; cursor: pointer; }

        .card { background: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #2a2a2a; margin-bottom: 15px; }
        .card-title { font-size: 15px; font-weight: bold; text-align: center; margin-bottom: 12px; }
        
        /* ৪টি ক্লিকযোগ্য কার্ড স্টাইল */
        .grid-stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; text-align: center; }
        .stat-box { background: #18221a; border: 1px solid #00ff66; padding: 12px 8px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .stat-box:hover { background: #005c26; }
        .stat-box.active-card { background: #00e65c; color: #000; }
        .stat-box.active-card p, .stat-box.active-card h3 { color: #000 !important; }
        .stat-box p { font-size: 12px; color: #aaa; pointer-events: none; }
        .stat-box h3 { color: #00ff66; margin-top: 4px; font-size: 18px; pointer-events: none; }

        .input-box { width: 100%; padding: 12px; margin-bottom: 10px; background: #2a2a2a; border: 1px solid #333; border-radius: 6px; color: #fff; font-size: 14px; }
        .submit-btn { width: 100%; padding: 12px; background: #00e65c; color: #000; font-weight: bold; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; }
        .btn-danger { background: #ff4d4d; color: #fff; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; }
        .btn-edit { background: #ffaa00; color: #000; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; margin-right: 5px; }

        .table-responsive { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background: #2a2a2a; color: #00ff66; }

        .auth-container { max-width: 400px; margin: 30px auto; background: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #2a2a2a; }
        .tab-buttons { display: flex; gap: 10px; margin-bottom: 15px; }
        .tab-btn { flex: 1; padding: 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        
        .chat-box { height: 220px; overflow-y: auto; border: 1px solid #333; border-radius: 6px; padding: 10px; margin-bottom: 10px; background: #121212; display: flex; flex-direction: column; gap: 8px; }
        .chat-msg { max-width: 85%; padding: 8px 12px; border-radius: 8px; font-size: 13px; }
        .chat-msg.sent { background: #005c26; color: #fff; align-self: flex-end; }
        .chat-msg.received { background: #2a2a2a; color: #fff; align-self: flex-start; }
        
        .hidden { display: none !important; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 999; display: none; }
        .overlay.active { display: block; }
        
        .action-link { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-decoration: none; margin-right: 4px; color: #fff; }
        .wa-link { background: #25D366; }
        .sms-link { background: #007bff; }
    </style>
</head>
<body>

    <div id="overlay" class="overlay" onclick="closeSidebar()"></div>

    <div id="sidebar" class="sidebar">
        <button class="close-btn" onclick="closeSidebar()">✖ বন্ধ করুন</button>
        <div style="clear:both;"></div>
        <div class="menu-title">মেনু অপশনসমূহ</div>
        <div class="menu-list">
            <button class="menu-item active" onclick="navTo('sec-overview', this)">📊 ওভারভিউ ও ডাটা</button>
            <button id="menu-add" class="menu-item admin-only" onclick="navTo('sec-add', this)">➕ নম্বর এড করুন</button>
            <button id="menu-create-user" class="menu-item admin-only" onclick="navTo('sec-create-user', this)">👤 নতুন ইউজার তৈরি</button>
            <button id="menu-users" class="menu-item admin-only" onclick="navTo('sec-users', this)">👥 সকল ইউজার তথ্য</button>
            <button class="menu-item" onclick="navTo('sec-messenger', this)">💬 মেসেঞ্জার</button>
        </div>
        <button class="logout-btn" onclick="logout()">লগআউট</button>
    </div>

    <div id="auth-view" class="auth-container">
        <div style="color:#00ff66; text-align:center; font-weight:bold; font-size:18px; margin-bottom:15px;">BTCL, কুড়িগ্রাম</div>
        <div class="tab-buttons">
            <button id="btn-tab-login" class="tab-btn" style="background:#00e65c; color:#000;" onclick="toggleAuthTab('login')">লগইন</button>
            <button id="btn-tab-reg" class="tab-btn" style="background:#2a2a2a; color:#fff;" onclick="toggleAuthTab('reg')">রেজিস্ট্রেশন</button>
        </div>

        <form id="form-login" onsubmit="doLogin(event)">
            <input type="text" id="log-username" class="input-box" placeholder="ইউজারনেম / জিমেইল / ফোন" required>
            <input type="password" id="log-password" class="input-box" placeholder="পাসওয়ার্ড" required>
            <button type="submit" class="submit-btn">লগইন করুন</button>
        </form>

        <form id="form-reg" class="hidden" onsubmit="registerUserDirect(event)">
            <input type="text" id="reg-name" class="input-box" placeholder="আপনার নাম" required>
            <input type="email" id="reg-email" class="input-box" placeholder="সঠিক জিমেইল আইডি" required>
            <input type="tel" id="reg-phone" class="input-box" placeholder="১১ ডিজিট মোবাইল নম্বর" required>
            <input type="text" id="reg-username" class="input-box" placeholder="ইউজারনেম" required>
            <input type="password" id="reg-pass" class="input-box" placeholder="পাসওয়ার্ড" required>
            <button type="submit" class="submit-btn">রেজিস্ট্রেশন করুন</button>
        </form>
    </div>

    <div id="dashboard-view" class="hidden">
        <div class="header">
            <div class="header-left">
                <button class="menu-btn" onclick="openSidebar()">☰</button>
                <button class="group-btn" onclick="openGroupModal()">📢 গ্রুপ ব্রডকাস্ট</button>
            </div>
            <div class="header-title">BTCL, কুড়িগ্রাম</div>
            <div style="font-size: 13px;" id="user-badge">👤 ইউজার</div>
        </div>

        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="search-input" class="search-box" onkeyup="filterCustomers()" placeholder="নাম, ফোন, সার্ভিস বা নম্বর দিয়ে দ্রুত খুঁজুন...">
        </div>

        <div id="sec-overview">
            <div class="card">
                <div class="grid-stats">
                    <div class="stat-box active-card" id="card-all" onclick="filterByCard('all', this)">
                        <p>টোটাল বিল</p>
                        <h3 id="stat-total-bill">৳0</h3>
                    </div>
                    <div class="stat-box" id="card-tel" onclick="filterByCard('টেলিফোন নম্বর', this)">
                        <p>টেলিফোন নম্বর</p>
                        <h3 id="stat-tel-count">0</h3>
                    </div>
                    <div class="stat-box" id="card-tel-wifi" onclick="filterByCard('টেলিফোন+ওয়াইফাই নম্বর', this)">
                        <p>টেলিফোন+ওয়াইফাই</p>
                        <h3 id="stat-tel-wifi-count">0</h3>
                    </div>
                    <div class="stat-box" id="card-wifi" onclick="filterByCard('ওয়াইফাই নম্বর', this)">
                        <p>ওয়াইফাই নম্বর</p>
                        <h3 id="stat-wifi-count">0</h3>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-title" style="text-align:left;" id="list-title">গ্রাহক ও সংযোগ তালিকা (সকল)</div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>ক্র.নং</th>
                                <th>নাম</th>
                                <th>মোবাইল</th>
                                <th>সেবার ধরন</th>
                                <th>সংযোগ নম্বর</th>
                                <th>বিল</th>
                                <th>ঠিকানা</th>
                                <th>তথ্য</th>
                                <th>মেসেজ পাঠান</th>
                                <th class="admin-only">অ্যাকশন</th>
                            </tr>
                        </thead>
                        <tbody id="customer-table-body"></tbody>
                    </table>
                </div>
            </div>
        </div>