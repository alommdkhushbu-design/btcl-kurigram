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
            name TEXT, email TEXT, phone TEXT UNIQUE, username TEXT UNIQUE, password TEXT, 
            status TEXT DEFAULT 'pending', is_deleted INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, service_type TEXT, service_no TEXT, phone TEXT, 
            address TEXT, note TEXT, is_deleted INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT, receiver TEXT, message TEXT, file_url TEXT, file_type TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # এডমিন একাউন্ট সেটআপ (Khushbu23)
    cursor.execute("SELECT * FROM users WHERE username='Khushbu23'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, phone, username, password, status, is_deleted) VALUES (?, ?, ?, ?, ?, ?, 0)",
                       ("Admin Khushbu", "admin@btcl.gov.bd", "01751947523", "Khushbu23", "01751947523", "admin"))
    else:
        cursor.execute("UPDATE users SET password='01751947523', status='admin', is_deleted=0 WHERE username='Khushbu23'")
    
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# UI (HTML, CSS & JavaScript)
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
        .header-left { display: flex; align-items: center; gap: 6px; }
        .header-right { display: flex; align-items: center; gap: 6px; }
        
        .nav-btn { font-size: 14px; color: #00ff66; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; padding: 6px 10px; cursor: pointer; display: flex; align-items: center; gap: 4px; }
        .nav-btn:hover { background: #2a2a2a; }
        
        .header-title { color: #00ff66; font-size: 15px; font-weight: bold; background: #1e1e1e; padding: 6px 10px; border-radius: 6px; border: 1px solid #2a2a2a; }
        
        /* ইউজার / এডমিন ট্যাগ স্টাইল */
        .role-badge { font-size: 11px; font-weight: bold; padding: 4px 8px; border-radius: 6px; }
        .admin-badge-style { background: #ff4d4d; color: #ffffff; border: 1px solid #ff1a1a; }
        .user-badge-style { background: #1e1e1e; color: #00ff66; border: 1px solid #333; }

        /* নোটিফিকেশন বেল */
        .notif-bell-btn { position: relative; font-size: 16px; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; padding: 5px 8px; cursor: pointer; color: #fff; }
        .notif-badge { position: absolute; top: -5px; right: -5px; background: #ff4d4d; color: white; font-size: 10px; font-weight: bold; padding: 2px 5px; border-radius: 50%; display: none; }
        .notif-dropdown { position: absolute; top: 45px; right: 12px; width: 280px; background: #1e1e1e; border: 1px solid #333; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); z-index: 1002; display: none; }
        .notif-dropdown.active { display: block; }
        .notif-header { padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: #00ff66; font-size: 13px; }
        .notif-item { padding: 10px; border-bottom: 1px solid #2a2a2a; font-size: 12px; cursor: pointer; }
        .notif-item:hover { background: #2a2a2a; }
        .notif-empty { padding: 15px; text-align: center; color: #888; font-size: 12px; }

        /* ইনস্ট্যান্ট সার্চ বার */
        .search-container { position: relative; margin-bottom: 15px; }
        .search-box { width: 100%; padding: 12px 15px 12px 38px; background: #1e1e1e; border: 1px solid #00ff66; border-radius: 20px; color: #fff; font-size: 14px; outline: none; }
        .search-box:focus { box-shadow: 0 0 10px rgba(0,255,102,0.3); }
        .search-icon { position: absolute; left: 14px; top: 12px; color: #00ff66; }

        .sidebar { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: #1e1e1e; z-index: 1000; transition: 0.3s; padding: 15px; border-right: 1px solid #333; box-shadow: 5px 0 15px rgba(0,0,0,0.5); }
        .sidebar.active { left: 0; }
        .close-btn { color: #ff4d4d; background: none; border: none; font-size: 16px; cursor: pointer; float: right; font-weight: bold; }
        
        .menu-title { color: #888; font-size: 13px; margin: 20px 0 10px 0; }
        .menu-list { display: flex; flex-direction: column; gap: 8px; }
        .menu-item { background: #2a2a2a; color: #fff; padding: 12px; border-radius: 6px; font-size: 13px; border: none; text-align: left; width: 100%; cursor: pointer; }
        .menu-item.active { background: #00e65c; color: #000; font-weight: bold; }
        .logout-btn { background: #ff4d4d; color: #fff; width: 100%; padding: 12px; border-radius: 6px; border: none; margin-top: 20px; font-weight: bold; cursor: pointer; }

        .card { background: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #2a2a2a; margin-bottom: 15px; }
        .card-title { font-size: 15px; font-weight: bold; text-align: center; margin-bottom: 12px; }
        
        .grid-stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; text-align: center; }
        .stat-box { background: #18221a; border: 1px solid #00ff66; padding: 12px 8px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .stat-box:hover { background: #005c26; }
        .stat-box.active-card { background: #00e65c; color: #000; }
        .stat-box.active-card p, .stat-box.active-card h3 { color: #000 !important; }
        .stat-box p { font-size: 11px; color: #aaa; pointer-events: none; }
        .stat-box h3 { color: #00ff66; margin-top: 4px; font-size: 16px; pointer-events: none; }

        .input-box { width: 100%; padding: 12px; margin-bottom: 10px; background: #2a2a2a; border: 1px solid #333; border-radius: 6px; color: #fff; font-size: 14px; }
        .submit-btn { width: 100%; padding: 12px; background: #00e65c; color: #000; font-weight: bold; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; }
        .btn-approve { background: #00e65c; color: #000; border: none; padding: 4px 8px; border-radius: 4px; font-weight: bold; cursor: pointer; margin-right: 4px; }
        .btn-restore { background: #007bff; color: #fff; border: none; padding: 4px 8px; border-radius: 4px; font-weight: bold; cursor: pointer; }
        .btn-danger { background: #ff4d4d; color: #fff; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; }
        .btn-edit { background: #ffaa00; color: #000; border: none; padding: 6px 10px; border-radius: 4px; cursor: pointer; margin-right: 5px; }

        .table-responsive { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background: #2a2a2a; color: #00ff66; }

        .clickable-name { color: #00ff66; cursor: pointer; font-weight: bold; text-decoration: underline; }
        .clickable-name:hover { color: #ffffff; }

        .auth-container { max-width: 400px; margin: 30px auto; background: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #2a2a2a; }
        .tab-buttons { display: flex; gap: 10px; margin-bottom: 15px; }
        .tab-btn { flex: 1; padding: 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        
        .chat-box { height: 250px; overflow-y: auto; border: 1px solid #333; border-radius: 6px; padding: 10px; margin-bottom: 10px; background: #121212; display: flex; flex-direction: column; gap: 8px; }
        .chat-msg { max-width: 85%; padding: 8px 12px; border-radius: 8px; font-size: 13px; }
        .chat-msg.sent { background: #005c26; color: #fff; align-self: flex-end; }
        .chat-msg.received { background: #2a2a2a; color: #fff; align-self: flex-start; }
        
        .hidden { display: none !important; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 999; display: none; }
        .overlay.active { display: block; }
        
        .action-link { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; text-decoration: none; margin-right: 4px; color: #fff; }
        .wa-link { background: #25D366; }
        .sms-link { background: #007bff; }

        /* ডিটেইলস পপআপ মোডাল */
        .modal { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1e1e1e; border: 1px solid #00ff66; border-radius: 10px; padding: 20px; width: 90%; max-width: 450px; z-index: 1001; box-shadow: 0 5px 20px rgba(0,0,0,0.8); }
        .modal-title { color: #00ff66; font-size: 16px; font-weight: bold; margin-bottom: 12px; border-bottom: 1px solid #333; padding-bottom: 6px; }
        .modal-item { margin-bottom: 8px; font-size: 13px; }
        .modal-item span { color: #aaa; }
    </style>
</head>
<body>

    <div id="overlay" class="overlay" onclick="closeSidebar()"></div>

    <div id="sidebar" class="sidebar">
        <button class="close-btn" onclick="closeSidebar()">✖ বন্ধ করুন</button>
        <div style="clear:both;"></div>
        <div class="menu-title">প্রধান মেনু</div>
        <div class="menu-list">
            <button class="menu-item active" onclick="navTo('sec-overview', this)">📊 ওভারভিউ ও ডাটা</button>
            <button id="menu-add" class="menu-item admin-only" onclick="navTo('sec-add', this)">➕ ১. নম্বর এড করুন</button>
            <button id="menu-create-user" class="menu-item admin-only" onclick="navTo('sec-create-user', this)">👤 ২. নতুন ইউজার তৈরি করুন</button>
            <button id="menu-users" class="menu-item admin-only" onclick="navTo('sec-users', this)">👥 ৩. নিবন্ধিত ইউজার ও পাসওয়ার্ড তথ্য</button>
            <button id="menu-deleted-cust" class="menu-item admin-only" onclick="navTo('sec-deleted-customers', this)">🗑️ ৪. ডিলিট হওয়া নম্বর তালিকা</button>
            <button id="menu-deleted-users" class="menu-item admin-only" onclick="navTo('sec-deleted-users', this)">🗑️ ৫. ডিলিট হওয়া ইউজার তালিকা</button>
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
                <button class="nav-btn" onclick="openSidebar()">☰ মেনু</button>
                <button class="nav-btn" onclick="goHome()">🏠 হোম</button>
                <button class="nav-btn" onclick="openGroupModal()">📢 গ্রুপ</button>
            </div>
            <div class="header-title">BTCL</div>
            <div class="header-right">
                <div style="position:relative;">
                    <button class="notif-bell-btn" onclick="toggleNotifDropdown()">
                        🔔 <span id="notif-badge" class="notif-badge">0</span>
                    </button>
                    <div id="notif-dropdown" class="notif-dropdown">
                        <div class="notif-header">নোটিফিকেশনসমূহ</div>
                        <div id="notif-list-body"></div>
                    </div>
                </div>
                <div id="user-badge" class="role-badge"></div>
            </div>
        </div>

        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="search-input" class="search-box" oninput="filterCustomers()" placeholder="যেকোনো অক্ষর বা নম্বর দিয়ে ইনস্ট্যান্ট সার্চ করুন...">
        </div>

        <div id="sec-overview">
            <div class="card">
                <div class="grid-stats">
                    <div class="stat-box active-card" id="card-tel" onclick="filterByCard('টেলিফোন নম্বর', this)">
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
                            <tr id="table-header-row">
                                </tr>
                        </thead>
                        <tbody id="customer-table-body"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="sec-add" class="card hidden admin-only">
            <div class="card-title" id="form-add-title">নতুন নম্বর এড করুন</div>
            <form onsubmit="saveCustomer(event)">
                <input type="hidden" id="cust-id">
                
                <label style="font-size:12px; color:#aaa;">১. গ্রাহকের নাম:</label>
                <input type="text" id="cust-name" class="input-box" placeholder="গ্রাহকের নাম" required>

                <label style="font-size:12px; color:#aaa;">২. মোবাইল নম্বর:</label>
                <input type="tel" id="cust-phone" class="input-box" placeholder="গ্রাহকের মোবাইল নম্বর" required>

                <label style="font-size:12px; color:#aaa;">৩. সেবার ধরন সিলেক্ট করুন:</label>
                <select id="cust-service-type" class="input-box" required>
                    <option value="">-- অপশন সিলেক্ট করুন --</option>
                    <option value="টেলিফোন নম্বর">টেলিফোন নম্বর</option>
                    <option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই নম্বর</option>
                    <option value="ওয়াইফাই নম্বর">ওয়াইফাই নম্বর</option>
                </select>

                <label style="font-size:12px; color:#aaa;">৪. সার্ভিস/সংযোগ নম্বর লিখুন:</label>
                <input type="text" id="cust-service-no" class="input-box" placeholder="যে নম্বরটি এড করতে চান" required>

                <label style="font-size:12px; color:#aaa;">৫. ঠিকানা:</label>
                <input type="text" id="cust-address" class="input-box" placeholder="গ্রাহকের ঠিকানা" required>

                <label style="font-size:12px; color:#aaa;">৬. অতিরিক্ত তথ্য / গোপন নোট:</label>
                <input type="text" id="cust-note" class="input-box" placeholder="অন্যান্য তথ্য (কেবল এডমিন দেখতে পাবে)">

                <button type="submit" class="submit-btn" id="cust-submit-btn">নম্বর সংরক্ষণ করুন</button>
            </form>
        </div>

        <div id="sec-create-user" class="card hidden admin-only">
            <div class="card-title">নতুন ইউজার একাউন্ট তৈরি করুন</div>
            <form onsubmit="adminCreateUser(event)">
                <input type="text" id="adm-user-name" class="input-box" placeholder="ইউজারের নাম" required>
                <input type="email" id="adm-user-email" class="input-box" placeholder="ইমেইল আইডি" required>
                <input type="tel" id="adm-user-phone" class="input-box" placeholder="ফোন নম্বর" required>
                <input type="text" id="adm-user-uname" class="input-box" placeholder="ইউজারনেম" required>
                <input type="password" id="adm-user-pass" class="input-box" placeholder="পাসওয়ার্ড" required>
                <button type="submit" class="submit-btn">ইউজার একাউন্ট তৈরি করুন</button>
            </form>
        </div>

        <div id="sec-users" class="card hidden admin-only">
            <div class="card-title">সকল নিবন্ধিত ইউজার ও পাসওয়ার্ড তথ্য</div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>নাম</th>
                            <th>ইমেইল</th>
                            <th>ফোন নম্বর</th>
                            <th>ইউজারনেম</th>
                            <th>পাসওয়ার্ড</th>
                            <th>স্ট্যাটাস</th>
                            <th>অ্যাকশন</th>
                        </tr>
                    </thead>
                    <tbody id="all-users-body"></tbody>
                </table>
            </div>
        </div>

        <div id="sec-deleted-customers" class="card hidden admin-only">
            <div class="card-title" style="color:#ff4d4d;">🗑️ ডিলিট হওয়া নম্বর ও ডাটা তালিকা</div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>নাম</th>
                            <th>মোবাইল</th>
                            <th>সেবার ধরন</th>
                            <th>সংযোগ নম্বর</th>
                            <th>অ্যাকশন</th>
                        </tr>
                    </thead>
                    <tbody id="deleted-customers-body"></tbody>
                </table>
            </div>
        </div>

        <div id="sec-deleted-users" class="card hidden admin-only">
            <div class="card-title" style="color:#ff4d4d;">🗑️ ডিলিট হওয়া ইউজার তালিকা</div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>নাম</th>
                            <th>ইউজারনেম</th>
                            <th>ফোন</th>
                            <th>অ্যাকশন</th>
                        </tr>
                    </thead>
                    <tbody id="deleted-users-body"></tbody>
                </table>
            </div>
        </div>

        <div id="sec-messenger" class="card hidden">
            <div class="card-title" style="color:#00ff66;">💬 মেসেঞ্জার</div>
            
            <div id="admin-chat-select-container" style="margin-bottom:10px;" class="admin-only">
                <input type="text" id="chat-user-search" class="input-box" onkeyup="filterChatUsers()" placeholder="🔍 ইউজার আইডি বা নাম দিয়ে সার্চ করুন...">
                <select id="chat-receiver-select" class="input-box" onchange="loadMessages()"></select>
            </div>

            <div id="chat-messages" class="chat-box"></div>
            
            <div style="display:flex; flex-direction:column; gap:5px;">
                <input type="file" id="chat-file-input" class="input-box" style="padding:5px;" accept="image/*,.pdf,.doc">
                <div style="display:flex; gap:5px;">
                    <input type="text" id="chat-msg-input" class="input-box" style="margin-bottom:0;" placeholder="মেসেজ লিখুন...">
                    <button class="submit-btn" style="width:80px;" onclick="sendChatMessage()">পাঠান</button>
                </div>
            </div>
        </div>
    </div>

    <div id="details-modal" class="modal hidden">
        <div class="modal-title">📄 গ্রাহকের সম্পূর্ণ তথ্য</div>
        <div id="details-modal-content"></div>
        <button class="btn-danger" style="width:100%; margin-top:15px; padding:8px;" onclick="closeDetailsModal()">বন্ধ করুন</button>
    </div>

    <div id="group-modal" class="auth-container hidden" style="position:fixed; top:5%; left:5%; right:5%; z-index:1001; max-width:500px;">
        <div class="card-title" style="color:#00ff66;">📢 গ্রুপ মেসেজ (WhatsApp & SMS)</div>
        <div id="group-broadcast-list" class="chat-box" style="height:150px;"></div>
        
        <div class="admin-only">
            <textarea id="group-msg-input" class="input-box" style="height:60px;" placeholder="গ্রুপ বার্তা টাইপ করুন..."></textarea>
            <button class="submit-btn" onclick="sendGroupBroadcast()">গ্রুপে বার্তা পাঠান</button>
        </div>

        <button class="btn-danger" style="width:100%; margin-top:10px;" onclick="closeGroupModal()">বন্ধ করুন</button>
    </div>

    <script>
        let currentUser = null;
        let customerDataCache = [];
        let allUsersCache = [];
        let activeCategoryFilter = 'all';

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

        function registerUserDirect(e) {
            e.preventDefault();
            const data = {
                name: document.getElementById('reg-name').value,
                email: document.getElementById('reg-email').value,
                phone: document.getElementById('reg-phone').value,
                username: document.getElementById('reg-username').value,
                password: document.getElementById('reg-pass').value
            };

            fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(res => {
                if(res.success) {
                    alert("রেজিস্ট্রেশন সফল হয়েছে! এডমিনের অনুমোদনের পর লগইন করতে পারবেন।");
                    toggleAuthTab('login');
                } else {
                    alert(res.message);
                }
            });
        }

        function adminCreateUser(e) {
            e.preventDefault();
            const data = {
                name: document.getElementById('adm-user-name').value,
                email: document.getElementById('adm-user-email').value,
                phone: document.getElementById('adm-user-phone').value,
                username: document.getElementById('adm-user-uname').value,
                password: document.getElementById('adm-user-pass').value
            };

            fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(res => {
                if(res.success) {
                    alert("নতুন ইউজার একাউন্ট সফলভাবে তৈরি করা হয়েছে!");
                    document.getElementById('adm-user-name').value = '';
                    document.getElementById('adm-user-email').value = '';
                    document.getElementById('adm-user-phone').value = '';
                    document.getElementById('adm-user-uname').value = '';
                    document.getElementById('adm-user-pass').value = '';
                    loadAllUsers();
                } else {
                    alert(res.message);
                }
            });
        }

        function doLogin(e) {
            e.preventDefault();
            fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    username: document.getElementById('log-username').value,
                    password: document.getElementById('log-password').value
                })
            })
            .then(res => res.json())
            .then(res => {
                if(res.success) {
                    currentUser = res.user;
                    document.getElementById('auth-view').classList.add('hidden');
                    setupRoleUI();
                    document.getElementById('dashboard-view').classList.remove('hidden');
                    loadDashboardData();
                    setInterval(checkNotifications, 3000);
                } else {
                    alert(res.message);
                }
            });
        }

        function setupRoleUI() {
            const isAdmin = currentUser.status === 'admin';
            document.querySelectorAll('.admin-only').forEach(el => {
                if(isAdmin) el.classList.remove('hidden');
                else el.classList.add('hidden');
            });
            
            const badgeEl = document.getElementById('user-badge');
            if (isAdmin) {
                badgeEl.innerText = "👑 ADMIN";
                badgeEl.className = "role-badge admin-badge-style";
            } else {
                badgeEl.innerText = "👤 USER (@" + currentUser.username + ")";
                badgeEl.className = "role-badge user-badge-style";
            }

            // টেবিল হেডার ডাইনামিকভাবে ইউজার/এডমিন অনুযায়ী পরিবর্তন
            const headerRow = document.getElementById('table-header-row');
            if (isAdmin) {
                headerRow.innerHTML = `
                    <th>ক্র.নং</th>
                    <th>নাম (ডিটেইলস)</th>
                    <th>মোবাইল</th>
                    <th>সেবার ধরন</th>
                    <th>সংযোগ নম্বর</th>
                    <th>ঠিকানা</th>
                    <th>মেসেজ</th>
                    <th>অ্যাকশন</th>
                `;
            } else {
                headerRow.innerHTML = `
                    <th>ক্র.নং</th>
                    <th>সংযোগ নম্বর</th>
                    <th>সেবার ধরন</th>
                    <th>ঠিকানা</th>
                `;
            }
        }

        function goHome() {
            navTo('sec-overview', document.querySelector('.menu-item'));
            document.getElementById('search-input').value = '';
            filterCustomers();
        }

        function loadDashboardData() {
            fetch('/api/customers')
            .then(res => res.json())
            .then(data => {
                customerDataCache = data;
                updateStats(data);
                filterCustomers();
            });

            loadAllUsers();
            loadMessages();
            loadDeletedCustomers();
            loadDeletedUsers();
            checkNotifications();
        }

        function updateStats(data) {
            let telCount = 0, telWifiCount = 0, wifiCount = 0;
            data.forEach(c => {
                if (c.service_type === 'টেলিফোন নম্বর') telCount++;
                else if (c.service_type === 'টেলিফোন+ওয়াইফাই নম্বর') telWifiCount++;
                else if (c.service_type === 'ওয়াইফাই নম্বর') wifiCount++;
            });

            document.getElementById('stat-tel-count').innerText = telCount;
            document.getElementById('stat-tel-wifi-count').innerText = telWifiCount;
            document.getElementById('stat-wifi-count').innerText = wifiCount;
        }

        function filterByCard(category, cardEl) {
            if (activeCategoryFilter === category) {
                activeCategoryFilter = 'all';
                document.querySelectorAll('.stat-box').forEach(el => el.classList.remove('active-card'));
                document.getElementById('list-title').innerText = 'গ্রাহক ও সংযোগ তালিকা (সকল)';
            } else {
                activeCategoryFilter = category;
                document.querySelectorAll('.stat-box').forEach(el => el.classList.remove('active-card'));
                cardEl.classList.add('active-card');
                document.getElementById('list-title').innerText = 'গ্রাহক তালিকা: ' + category;
            }
            filterCustomers();
        }

        function filterCustomers() {
            const q = document.getElementById('search-input').value.toLowerCase().trim();
            const filtered = customerDataCache.filter(c => {
                const matchCategory = (activeCategoryFilter === 'all') || (c.service_type === activeCategoryFilter);
                const matchQuery = (c.name || '').toLowerCase().includes(q) ||
                                   (c.phone || '').includes(q) ||
                                   (c.service_type || '').toLowerCase().includes(q) ||
                                   (c.service_no || '').toLowerCase().includes(q) ||
                                   (c.address || '').toLowerCase().includes(q);
                return matchCategory && matchQuery;
            });
            renderCustomers(filtered);
        }

        function renderCustomers(data) {
            const tbody = document.getElementById('customer-table-body');
            tbody.innerHTML = '';
            const isAdmin = currentUser.status === 'admin';

            data.forEach((c, index) => {
                const tr = document.createElement('tr');
                
                if (isAdmin) {
                    let formattedPhone = c.phone.startsWith('88') ? c.phone : '88' + c.phone;
                    tr.innerHTML = `
                        <td>${index + 1}</td>
                        <td><span class="clickable-name" onclick="showCustomerDetails(${c.id})">${c.name}</span></td>
                        <td>${c.phone}</td>
                        <td><span style="color:#00ff66;">${c.service_type}</span></td>
                        <td><strong>${c.service_no}</strong></td>
                        <td>${c.address}</td>
                        <td>
                            <a href="https://wa.me/${formattedPhone}" target="_blank" class="action-link wa-link">WhatsApp</a>
                            <a href="sms:${c.phone}" class="action-link sms-link">SMS</a>
                        </td>
                        <td>
                            <button class="btn-edit" onclick="editCustomer(${c.id}, '${c.name}', '${c.phone}', '${c.service_type}', '${c.service_no}', '${c.address}', '${c.note}')">এডিট</button>
                            <button class="btn-danger" onclick="deleteCustomer(${c.id})">ডিলিট</button>
                        </td>
                    `;
                } else {
                    // সাধারণ ইউজারদের জন্য সংক্ষিপ্ত ভিউ (নাম ও মেসেজ অপশন ছাড়া)
                    tr.innerHTML = `
                        <td>${index + 1}</td>
                        <td><strong>${c.service_no}</strong></td>
                        <td><span style="color:#00ff66;">${c.service_type}</span></td>
                        <td>${c.address}</td>
                    `;
                }
                tbody.appendChild(tr);
            });
        }

        /* এডমিনের জন্য কাস্টমার ডিটেইলস দেখা */
        function showCustomerDetails(id) {
            const c = customerDataCache.find(item => item.id === id);
            if (!c) return;

            const html = `
                <div class="modal-item"><span>গ্রাহকের নাম:</span> <strong>${c.name}</strong></div>
                <div class="modal-item"><span>মোবাইল নম্বর:</span> <strong>${c.phone}</strong></div>
                <div class="modal-item"><span>সেবার ধরন:</span> <strong style="color:#00ff66;">${c.service_type}</strong></div>
                <div class="modal-item"><span>সংযোগ নম্বর:</span> <strong>${c.service_no}</strong></div>
                <div class="modal-item"><span>ঠিকানা:</span> <strong>${c.address}</strong></div>
                <div class="modal-item"><span>অতিরিক্ত নোট:</span> <strong>${c.note || 'কোনো নোট নেই'}</strong></div>
            `;
            document.getElementById('details-modal-content').innerHTML = html;
            document.getElementById('details-modal').classList.remove('hidden');
            document.getElementById('overlay').classList.add('active');
        }

        function closeDetailsModal() {
            document.getElementById('details-modal').classList.add('hidden');
            document.getElementById('overlay').classList.remove('active');
        }

        function saveCustomer(e) {
            e.preventDefault();
            const payload = {
                id: document.getElementById('cust-id').value,
                name: document.getElementById('cust-name').value,
                phone: document.getElementById('cust-phone').value,
                service_type: document.getElementById('cust-service-type').value,
                service_no: document.getElementById('cust-service-no').value,
                address: document.getElementById('cust-address').value,
                note: document.getElementById('cust-note').value
            };

            fetch('/api/save-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(res => {
                alert(res.message);
                document.getElementById('cust-id').value = '';
                document.getElementById('form-add-title').innerText = 'নতুন নম্বর এড করুন';
                document.getElementById('cust-submit-btn').innerText = 'নম্বর সংরক্ষণ করুন';
                navTo('sec-overview');
                loadDashboardData();
            });
        }

        function editCustomer(id, name, phone, service_type, service_no, address, note) {
            document.getElementById('cust-id').value = id;
            document.getElementById('cust-name').value = name;
            document.getElementById('cust-phone').value = phone;
            document.getElementById('cust-service-type').value = service_type;
            document.getElementById('cust-service-no').value = service_no;
            document.getElementById('cust-address').value = address;
            document.getElementById('cust-note').value = note;

            document.getElementById('form-add-title').innerText = 'ডাটা এডিট করুন';
            document.getElementById('cust-submit-btn').innerText = 'আপডেট করুন';
            navTo('sec-add');
        }

        function deleteCustomer(id) {
            if(!confirm("আপনি কি এই নম্বরটি ডিলিট ট্র্যাশ বিনে পাঠাতে চান?")) return;
            fetch('/api/delete-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id})
            })
            .then(res => res.json())
            .then(res => {
                alert(res.message);
                loadDashboardData();
            });
        }

        function loadDeletedCustomers() {
            fetch('/api/deleted-customers')
            .then(res => res.json())
            .then(data => {
                const tbody = document.getElementById('deleted-customers-body');
                if(!tbody) return;
                tbody.innerHTML = '';
                data.forEach(c => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${c.name}</td>
                            <td>${c.phone}</td>
                            <td>${c.service_type}</td>
                            <td>${c.service_no}</td>
                            <td>
                                <button class="btn-restore" onclick="restoreCustomer(${c.id})">পুনরুদ্ধার করুন</button>
                            </td>
                        </tr>
                    `;
                });
            });
        }

        function restoreCustomer(id) {
            fetch('/api/restore-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id})
            })
            .then(res => res.json())
            .then(res => {
                alert(res.message);
                loadDashboardData();
            });
        }

        function loadAllUsers() {
            fetch('/api/all-users')
            .then(res => res.json())
            .then(users => {
                allUsersCache = users;
                const tbody = document.getElementById('all-users-body');
                const select = document.getElementById('chat-receiver-select');
                
                if(tbody) tbody.innerHTML = '';
                if(select) select.innerHTML = '';

                users.forEach(u => {
                    if(tbody && u.username !== 'Khushbu23') {
                        let statusText = u.status === 'pending' ? '<span style="color:#ffaa00;">পেন্ডিং</span>' : '<span style="color:#00ff66;">অনুমোদিত</span>';
                        let approveBtn = u.status === 'pending' ? `<button class="btn-approve" onclick="approveUser(${u.id})">অনুমোদন</button>` : '';

                        tbody.innerHTML += `
                            <tr>
                                <td>${u.name}</td>
                                <td>${u.email}</td>
                                <td>${u.phone}</td>
                                <td><strong>@${u.username}</strong></td>
                                <td><span style="color:#ffaa00; font-family:monospace;">${u.password}</span></td>
                                <td>${statusText}</td>
                                <td>
                                    ${approveBtn}
                                    <button class="btn-danger" onclick="deleteUser(${u.id})">ডিলিট</button>
                                </td>
                            </tr>
                        `;
                    }
                    if(select && u.username !== 'Khushbu23') {
                        select.innerHTML += `<option value="${u.username}">${u.name} (@${u.username})</option>`;
                    }
                });
            });
        }

        function approveUser(id) {
            fetch('/api/approve-user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id})
            })
            .then(res => res.json())
            .then(res => {
                alert(res.message);
                loadAllUsers();
                checkNotifications();
            });
        }

        function deleteUser(id) {
            if(!confirm("আপনি কি নিশ্চিত এই ইউজার ডিলিট ট্র্যাশ বিনে পাঠাতে চান?")) return;
            fetch('/api/delete-user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id})
            })
            .then(res => res.json())
            .then(res => {
                alert(res.message);
                loadAllUsers();
                loadDeletedUsers();
            });
        }

        function loadDeletedUsers() {
            fetch('/api/deleted-users')
            .then(res => res.json())
            .then(data => {
                const tbody = document.getElementById('deleted-users-body');
                if(!tbody) return;
                tbody.innerHTML = '';
                data.forEach(u => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${u.name}</td>
                            <td>@${u.username}</td>
                            <td>${u.phone}</td>
                            <td>
                                <button class="btn-restore" onclick="restoreUser(${u.id})">পুনরুদ্ধার করুন</button>
                            </td>
                        </tr>
                    `;
                });
            });
        }

        function restoreUser(id) {
            fetch('/api/restore-user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id})
            })
            .then(res => res.json())
            .then(res => {
                alert(res.message);
                loadAllUsers();
                loadDeletedUsers();
            });
        }

        function filterChatUsers() {
            const q = document.getElementById('chat-user-search').value.toLowerCase();
            const select = document.getElementById('chat-receiver-select');
            select.innerHTML = '';

            allUsersCache.filter(u => u.username !== 'Khushbu23' && (u.username.toLowerCase().includes(q) || u.name.toLowerCase().includes(q))).forEach(u => {
                select.innerHTML += `<option value="${u.username}">${u.name} (@${u.username})</option>`;
            });
            loadMessages();
        }

        function sendChatMessage() {
            const msgInput = document.getElementById('chat-msg-input');
            const fileInput = document.getElementById('chat-file-input');
            
            let receiver = 'Khushbu23'; 
            if (currentUser.status === 'admin') {
                receiver = document.getElementById('chat-receiver-select').value;
            }

            if(!msgInput.value && !fileInput.files[0]) return;
            
            const formData = new FormData();
            formData.append('sender', currentUser.username);
            formData.append('receiver', receiver);
            formData.append('message', msgInput.value);
            if (fileInput.files[0]) formData.append('file', fileInput.files[0]);

            fetch('/api/send-message', { method: 'POST', body: formData })
            .then(() => {
                msgInput.value = '';
                fileInput.value = '';
                loadMessages();
            });
        }

        function loadMessages() {
            fetch('/api/messages')
            .then(res => res.json())
            .then(msgs => {
                const container = document.getElementById('chat-messages');
                const groupContainer = document.getElementById('group-broadcast-list');
                
                let html = '';
                let groupHtml = '';

                let activeTarget = (currentUser.status === 'admin') ? 
                    (document.getElementById('chat-receiver-select').value || '') : 'Khushbu23';

                msgs.forEach(m => {
                    let media = '';
                    if(m.file_url) {
                        if(m.file_type && m.file_type.startsWith('image/')) {
                            media = `<br><img src="${m.file_url}" style="max-width:140px; border-radius:6px; margin-top:5px;">`;
                        } else {
                            media = `<br><a href="${m.file_url}" target="_blank" style="color:#00ff66;">📄 ফাইল ডাউনলোড</a>`;
                        }
                    }

                    const isMe = m.sender === currentUser.username;
                    const msgDiv = `<div class="chat-msg ${isMe ? 'sent' : 'received'}">
                        <strong>@${m.sender}:</strong> ${m.message}${media}
                    </div>`;

                    if (m.receiver === 'group') {
                        const encodedMsg = encodeURIComponent(m.message);
                        groupHtml += `<div class="chat-msg received">
                            <strong>📢 @${m.sender}:</strong> ${m.message}${media}
                            <div style="margin-top:5px;">
                                <a href="https://wa.me/?text=${encodedMsg}" target="_blank" class="action-link wa-link">WhatsApp-এ শেয়ার</a>
                                <a href="sms:?body=${encodedMsg}" class="action-link sms-link">SMS পাঠান</a>
                            </div>
                        </div>`;
                    } else {
                        if((m.sender === currentUser.username && m.receiver === activeTarget) || 
                           (m.sender === activeTarget && m.receiver === currentUser.username)) {
                            html += msgDiv;
                        }
                    }
                });

                if(container) container.innerHTML = html;
                if(groupContainer) groupContainer.innerHTML = groupHtml;
            });
        }

        function toggleNotifDropdown() {
            document.getElementById('notif-dropdown').classList.toggle('active');
        }

        function checkNotifications() {
            if(!currentUser) return;

            fetch('/api/notifications?username=' + currentUser.username + '&status=' + currentUser.status)
            .then(res => res.json())
            .then(data => {
                const badge = document.getElementById('notif-badge');
                const listBody = document.getElementById('notif-list-body');
                listBody.innerHTML = '';

                let count = data.length;
                if(count > 0) {
                    badge.innerText = count;
                    badge.style.display = 'inline-block';

                    data.forEach(item => {
                        let notifHtml = '';
                        if(item.type === 'registration') {
                            notifHtml = `<div class="notif-item" onclick="handleNotifClick('registration')">
                                👤 <strong>নতুন রেজিস্ট্রেশন:</strong> ${item.title} একাউন্ট খোলার আবেদন করেছেন।
                            </div>`;
                        } else if(item.type === 'message') {
                            notifHtml = `<div class="notif-item" onclick="handleNotifClick('message', '${item.sender}')">
                                💬 <strong>নতুন মেসেজ:</strong> @${item.sender}: "${item.title}"
                            </div>`;
                        }
                        listBody.innerHTML += notifHtml;
                    });
                } else {
                    badge.style.display = 'none';
                    listBody.innerHTML = '<div class="notif-empty">কোনো নতুন নোটিফিকেশন নেই।</div>';
                }
            });
        }

        function handleNotifClick(type, sender) {
            document.getElementById('notif-dropdown').classList.remove('active');
            
            if(type === 'registration') {
                navTo('sec-users');
            } else if(type === 'message') {
                navTo('sec-messenger');
                if(currentUser.status === 'admin' && sender) {
                    document.getElementById('chat-receiver-select').value = sender;
                    loadMessages();
                }
            }
        }

        function openGroupModal() {
            document.getElementById('group-modal').classList.remove('hidden');
            document.getElementById('overlay').classList.add('active');
            loadMessages();
        }

        function closeGroupModal() {
            document.getElementById('group-modal').classList.add('hidden');
            document.getElementById('overlay').classList.remove('active');
        }

        function sendGroupBroadcast() {
            const msg = document.getElementById('group-msg-input').value;
            if(!msg) return;

            fetch('/api/group-broadcast', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({sender: currentUser.username, message: msg})
            })
            .then(() => {
                document.getElementById('group-msg-input').value = '';
                loadMessages();
            });
        }

        function openSidebar() {
            document.getElementById('sidebar').classList.add('active');
            document.getElementById('overlay').classList.add('active');
        }

        function closeSidebar() {
            document.getElementById('sidebar').classList.remove('active');
            document.getElementById('overlay').classList.remove('active');
            closeGroupModal();
            closeDetailsModal();
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

        function logout() {
            currentUser = null;
            location.reload();
        }
    </script>
</body>
</html>
"""

# ---------------------------------------------------------
# API সার্ভিস
# ---------------------------------------------------------
@app.route('/')
def index():
    return render_template_string(HTML_LAYOUT)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, email, phone, username, password, status, is_deleted) VALUES (?, ?, ?, ?, ?, 'pending', 0)",
                       (data['name'], data['email'], data['phone'], data['username'], data['password']))
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "ইউজারনেম বা ফোন নম্বরটি ইতোমধ্যে ব্যবহার করা হয়েছে!"})
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, username, status FROM users WHERE (username=? OR email=? OR phone=?) AND password=? AND is_deleted=0",
                   (data['username'], data['username'], data['username'], data['password']))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        if user[5] == 'pending':
            return jsonify({"success": False, "message": "আপনার একাউন্টটি এখনও এডমিন অনুমোদন করেননি। দয়া করে অপেক্ষা করুন!"})
            
        return jsonify({
            "success": True,
            "user": {"id": user[0], "name": user[1], "email": user[2], "phone": user[3], "username": user[4], "status": user[5]}
        })
    return jsonify({"success": False, "message": "ভুল ইউজারনেম বা পাসওয়ার্ড অথবা একাউন্টটি ডিলিট করা হয়েছে!"})

@app.route('/api/approve-user', methods=['POST'])
def approve_user():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status='approved' WHERE id=?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "ইউজার একাউন্ট অনুমোদন করা হয়েছে!"})

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    username = request.args.get('username')
    status = request.args.get('status')
    
    notifications = []
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if status == 'admin':
        cursor.execute("SELECT name, username FROM users WHERE status='pending' AND is_deleted=0")
        pending_users = cursor.fetchall()
        for u in pending_users:
            notifications.append({"type": "registration", "title": f"{u[0]} (@{u[1]})"})

    cursor.execute("SELECT sender, message FROM messages WHERE receiver=? ORDER BY id DESC LIMIT 5", (username,))
    msgs = cursor.fetchall()
    for m in msgs:
        notifications.append({"type": "message", "sender": m[0], "title": m[1]})

    conn.close()
    return jsonify(notifications)

@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, service_type, service_no, phone, address, note FROM customers WHERE is_deleted=0")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "service_type": r[2], "service_no": r[3], "phone": r[4], "address": r[5], "note": r[6]} for r in rows])

@app.route('/api/deleted-customers', methods=['GET'])
def get_deleted_customers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, service_type, service_no, phone FROM customers WHERE is_deleted=1")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "service_type": r[2], "service_no": r[3], "phone": r[4]} for r in rows])

@app.route('/api/save-customer', methods=['POST'])
def save_customer():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if data.get('id'):
        cursor.execute("UPDATE customers SET name=?, service_type=?, service_no=?, phone=?, address=?, note=? WHERE id=?",
                       (data['name'], data['service_type'], data['service_no'], data['phone'], data['address'], data['note'], data['id']))
        msg = "গ্রাহক তথ্য ও নম্বর আপডেট করা হয়েছে!"
    else:
        cursor.execute("INSERT INTO customers (name, service_type, service_no, phone, address, note, is_deleted) VALUES (?, ?, ?, ?, ?, ?, 0)",
                       (data['name'], data['service_type'], data['service_no'], data['phone'], data['address'], data['note']))
        msg = "নতুন নম্বর ও ডাটা সফলভাবে সংরক্ষিত হয়েছে!"
        
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": msg})

@app.route('/api/delete-customer', methods=['POST'])
def delete_customer():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET is_deleted=1 WHERE id=?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "ডাটা ডিলিট বিনে পাঠানো হয়েছে!"})

@app.route('/api/restore-customer', methods=['POST'])
def restore_customer():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET is_deleted=0 WHERE id=?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "ডাটা সফলভাবে পুনরুদ্ধার করা হয়েছে!"})

@app.route('/api/all-users', methods=['GET'])
def all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, username, password, status FROM users WHERE is_deleted=0")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "email": r[2], "phone": r[3], "username": r[4], "password": r[5], "status": r[6]} for r in rows])

@app.route('/api/deleted-users', methods=['GET'])
def deleted_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, phone FROM users WHERE is_deleted=1")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "username": r[2], "phone": r[3]} for r in rows])

@app.route('/api/delete-user', methods=['POST'])
def delete_user():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_deleted=1 WHERE id=?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "ইউজার একাউন্ট ডিলিট বিনে পাঠানো হয়েছে!"})

@app.route('/api/restore-user', methods=['POST'])
def restore_user():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_deleted=0 WHERE id=?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "ইউজার একাউন্ট পুনরুদ্ধার করা হয়েছে!"})

@app.route('/api/send-message', methods=['POST'])
def send_message():
    sender = request.form.get('sender')
    receiver = request.form.get('receiver', 'Khushbu23')
    message = request.form.get('message', '')
    file = request.files.get('file')
    
    file_url = None
    file_type = None

    if file:
        upload_folder = 'static/uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)
        file_url = '/' + file_path
        file_type = file.content_type

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, receiver, message, file_url, file_type) VALUES (?, ?, ?, ?, ?)",
                   (sender, receiver, message, file_url, file_type))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/group-broadcast', methods=['POST'])
def group_broadcast():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (?, 'group', ?)",
                   (data['sender'], data['message']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/messages', methods=['GET'])
def get_messages():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT sender, receiver, message, file_url, file_type, timestamp FROM messages ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"sender": r[0], "receiver": r[1], "message": r[2], "file_url": r[3], "file_type": r[4], "time": r[5]} for r in rows])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)