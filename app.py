import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_NAME = "database.db"
ADMIN_SECURITY_CODE = "137955"

# ---------------------------------------------------------
# ডাটাবেস ইনিশিয়ালাইজেশন
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # ইউজার টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT UNIQUE, username TEXT UNIQUE, password TEXT, 
            status TEXT DEFAULT 'pending', is_deleted INTEGER DEFAULT 0
        )
    ''')
    
    # গ্রাহক/সংযোগ টেবিল (ডকুমেন্ট ফাইলের জন্য doc_url কলামসহ)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, service_type TEXT, service_no TEXT, phone TEXT, 
            address TEXT, note TEXT, doc_url TEXT, is_deleted INTEGER DEFAULT 0
        )
    ''')
    
    # মেসেজ টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT, receiver TEXT, message TEXT, file_url TEXT, file_type TEXT, 
            is_read INTEGER DEFAULT 0, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # পড়া হওয়া নোটিফিকেশন ট্র্যাক করার টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS read_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            notif_type TEXT,
            target_id INTEGER,
            username TEXT
        )
    ''')
    
    # ডিফল্ট এডমিন অ্যাকাউন্ট
    cursor.execute("SELECT * FROM users WHERE status='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, phone, username, password, status, is_deleted) VALUES (?, ?, ?, ?, ?, ?, 0)",
                       ("Admin Khushbu", "admin@btcl.gov.bd", "01751947523", "Khushbu23", "01751947523", "admin"))
    
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# ফ্রন্টএন্ড UI (HTML, CSS, JS)
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
        .header-left, .header-right { display: flex; align-items: center; gap: 6px; }
        
        .nav-btn { font-size: 13px; color: #00ff66; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; padding: 6px 10px; cursor: pointer; display: flex; align-items: center; gap: 4px; }
        .nav-btn:hover { background: #2a2a2a; }
        
        .header-title { color: #00ff66; font-size: 15px; font-weight: bold; background: #1e1e1e; padding: 6px 10px; border-radius: 6px; border: 1px solid #2a2a2a; }
        
        .role-badge { font-size: 11px; font-weight: bold; padding: 4px 8px; border-radius: 6px; }
        .admin-badge-style { background: #ff4d4d; color: #ffffff; border: 1px solid #ff1a1a; }
        .user-badge-style { background: #1e1e1e; color: #00ff66; border: 1px solid #333; }

        .notif-bell-btn { position: relative; font-size: 16px; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; padding: 5px 8px; cursor: pointer; color: #fff; }
        .notif-badge { position: absolute; top: -5px; right: -5px; background: #ff4d4d; color: white; font-size: 10px; font-weight: bold; padding: 2px 5px; border-radius: 50%; display: none; }
        .notif-dropdown { position: absolute; top: 45px; right: 12px; width: 300px; max-height: 350px; overflow-y: auto; background: #1e1e1e; border: 1px solid #333; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); z-index: 1002; display: none; }
        .notif-dropdown.active { display: block; }
        .notif-header { padding: 10px; border-bottom: 1px solid #333; font-weight: bold; color: #00ff66; font-size: 13px; }
        .notif-item { padding: 10px; border-bottom: 1px solid #2a2a2a; font-size: 12px; cursor: pointer; }
        .notif-item:hover { background: #2a2a2a; }
        .notif-empty { padding: 15px; text-align: center; color: #888; font-size: 12px; }

        .search-container { position: relative; margin-bottom: 10px; }
        .search-box { width: 100%; padding: 12px 15px 12px 38px; background: #1e1e1e; border: 1px solid #00ff66; border-radius: 20px; color: #fff; font-size: 14px; outline: none; }
        .search-box:focus { box-shadow: 0 0 10px rgba(0,255,102,0.3); }
        .search-icon { position: absolute; left: 14px; top: 12px; color: #00ff66; }

        .sort-controls { display: flex; gap: 10px; margin-bottom: 15px; align-items: center; background: #1e1e1e; padding: 8px 12px; border-radius: 8px; border: 1px solid #2a2a2a; }
        .sort-label { font-size: 12px; color: #aaa; }
        .sort-select { background: #2a2a2a; color: #00ff66; border: 1px solid #333; padding: 6px 10px; border-radius: 6px; font-size: 12px; outline: none; cursor: pointer; }

        .sidebar { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: #1e1e1e; z-index: 1000; transition: 0.3s; padding: 15px; border-right: 1px solid #333; box-shadow: 5px 0 15px rgba(0,0,0,0.5); overflow-y: auto; }
        .sidebar.active { left: 0; }
        .close-btn { color: #ff4d4d; background: none; border: none; font-size: 16px; cursor: pointer; float: right; font-weight: bold; }
        
        .menu-title { color: #888; font-size: 13px; margin: 20px 0 10px 0; }
        .menu-list { display: flex; flex-direction: column; gap: 8px; }
        .menu-item { background: #2a2a2a; color: #fff; padding: 12px; border-radius: 6px; font-size: 13px; border: none; text-align: left; width: 100%; cursor: pointer; }
        .menu-item.active { background: #00e65c; color: #000; font-weight: bold; }
        .logout-btn { background: #ff4d4d; color: #fff; width: 100%; padding: 12px; border-radius: 6px; border: none; margin-top: 20px; font-weight: bold; cursor: pointer; }

        .card { background: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #2a2a2a; margin-bottom: 15px; }
        .card-title { font-size: 15px; font-weight: bold; text-align: center; margin-bottom: 12px; }
        
        .grid-stats { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; text-align: center; }
        .stat-box { background: #18221a; border: 1px solid #00ff66; padding: 8px 2px; border-radius: 8px; cursor: pointer; transition: 0.2s; }
        .stat-box:hover { background: #005c26; }
        .stat-box.active-card { background: #00e65c; color: #000; }
        .stat-box.active-card p, .stat-box.active-card h3 { color: #000 !important; }
        .stat-box p { font-size: 9px; color: #aaa; pointer-events: none; }
        .stat-box h3 { color: #00ff66; margin-top: 4px; font-size: 14px; pointer-events: none; }

        .input-box { width: 100%; padding: 12px; margin-bottom: 10px; background: #2a2a2a; border: 1px solid #333; border-radius: 6px; color: #fff; font-size: 14px; }
        .submit-btn { width: 100%; padding: 12px; background: #00e65c; color: #000; font-weight: bold; border: none; border-radius: 6px; font-size: 15px; cursor: pointer; }
        .btn-approve { background: #00e65c; color: #000; border: none; padding: 4px 8px; border-radius: 4px; font-weight: bold; cursor: pointer; margin-right: 4px; }
        .btn-danger { background: #ff4d4d; color: #fff; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; }

        .table-responsive { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background: #2a2a2a; color: #00ff66; }

        .clickable-name { color: #00ff66; cursor: pointer; font-weight: bold; text-decoration: underline; }
        .clickable-name:hover { color: #ffffff; }

        .auth-container { max-width: 400px; margin: 30px auto; background: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #2a2a2a; }
        .tab-buttons { display: flex; gap: 10px; margin-bottom: 15px; }
        .tab-btn { flex: 1; padding: 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        
        /* মেসেঞ্জার লেআউট */
        .messenger-layout { display: flex; gap: 10px; height: 420px; }
        .chat-user-list { width: 35%; background: #121212; border: 1px solid #333; border-radius: 6px; overflow-y: auto; padding: 5px; }
        .chat-user-item { padding: 10px; border-bottom: 1px solid #222; border-radius: 6px; cursor: pointer; display: flex; flex-direction: column; gap: 3px; margin-bottom: 3px; background: #1a1a1a; }
        .chat-user-item:hover, .chat-user-item.active { background: #005c26; color: #fff; }
        .chat-user-item .u-name { font-weight: bold; font-size: 13px; color: #00ff66; }
        .chat-user-item .u-msg { font-size: 11px; color: #ccc; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        
        .chat-area { width: 65%; display: flex; flex-direction: column; }
        .chat-header { background: #2a2a2a; padding: 8px 12px; font-size: 13px; font-weight: bold; color: #00ff66; border-radius: 6px 6px 0 0; border: 1px solid #333; }
        .chat-box { flex: 1; overflow-y: auto; border: 1px solid #333; border-top: none; padding: 10px; background: #121212; display: flex; flex-direction: column; gap: 8px; }
        .chat-msg { max-width: 85%; padding: 8px 12px; border-radius: 8px; font-size: 13px; }
        .chat-msg.sent { background: #005c26; color: #fff; align-self: flex-end; }
        .chat-msg.received { background: #2a2a2a; color: #fff; align-self: flex-start; }
        
        /* ক্যামেরা প্রিভিউ ও বাটন */
        .camera-btn-group { display: flex; gap: 10px; margin-bottom: 10px; }
        .cam-btn { flex: 1; padding: 10px; background: #2a2a2a; color: #00ff66; border: 1px solid #00ff66; border-radius: 6px; font-size: 12px; cursor: pointer; text-align: center; }
        .cam-btn:hover { background: #005c26; color: #fff; }
        #camera-preview-container { text-align: center; margin-bottom: 10px; display: none; }
        #video-element { width: 100%; max-height: 200px; background: #000; border-radius: 6px; border: 1px solid #333; }
        #captured-image-preview { max-width: 100%; max-height: 150px; border-radius: 6px; border: 1px solid #00ff66; margin-top: 5px; display: none; }

        .hidden { display: none !important; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 999; display: none; }
        .overlay.active { display: block; }

        .modal { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1e1e1e; border: 1px solid #00ff66; border-radius: 10px; padding: 20px; width: 90%; max-width: 450px; z-index: 1001; box-shadow: 0 5px 20px rgba(0,0,0,0.8); }
        .modal-title { color: #00ff66; font-size: 16px; font-weight: bold; margin-bottom: 12px; border-bottom: 1px solid #333; padding-bottom: 6px; }
        .modal-item { margin-bottom: 8px; font-size: 13px; }
        .modal-item span { color: #aaa; }
        
        .history-card { background: #2a2a2a; padding: 10px; border-radius: 6px; margin-bottom: 8px; border-left: 3px solid #00ff66; }
    </style>
</head>
<body>

    <div id="overlay" class="overlay" onclick="closeSidebar()"></div>

    <!-- সাইডবার মেনু -->
    <div id="sidebar" class="sidebar">
        <button class="close-btn" onclick="closeSidebar()">✖ বন্ধ করুন</button>
        <div style="clear:both;"></div>
        <div class="menu-title">প্রধান মেনু</div>
        <div class="menu-list">
            <button class="menu-item active" onclick="navTo('sec-overview', this)">📊 ওভারভিউ ও ডাটা</button>
            <button id="menu-notif-history" class="menu-item" onclick="navTo('sec-notif-history', this)">📜 নোটিফিকেশন হিস্ট্রি</button>
            <button id="menu-add" class="menu-item admin-only" onclick="navTo('sec-add', this)">➕ ১. নম্বর এড করুন</button>
            <button id="menu-create-user" class="menu-item admin-only" onclick="navTo('sec-create-user', this)">👤 ২. নতুন ইউজার তৈরি করুন</button>
            <button id="menu-users" class="menu-item admin-only" onclick="navTo('sec-users', this)">👥 ৩. নিবন্ধিত ইউজার তথ্য</button>
            <button id="menu-admin-settings" class="menu-item admin-only" onclick="navTo('sec-admin-settings', this)">🔐 ৪. সিকিউরিটি ও পাসওয়ার্ড</button>
            <button class="menu-item" onclick="navTo('sec-messenger', this)">💬 মেসেঞ্জার</button>
        </div>
        <button class="logout-btn" onclick="logout()">লগআউট</button>
    </div>

    <!-- লগইন ও রেজিস্ট্রেশন -->
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

    <!-- মূল ড্যাশবোর্ড -->
    <div id="dashboard-view" class="hidden">
        <div class="header">
            <div class="header-left">
                <button class="nav-btn" onclick="openSidebar()">☰ মেনু</button>
                <button class="nav-btn" onclick="goHome()">🏠 হোম</button>
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

        <!-- সার্চ বার -->
        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="search-input" class="search-box" oninput="filterCustomers()" placeholder="সার্চ করুন...">
        </div>

        <!-- সর্টিং -->
        <div class="sort-controls">
            <span class="sort-label">ফিল্টার:</span>
            <select id="sort-option" class="sort-select" onchange="filterCustomers()">
                <option value="none">ডিফল্ট</option>
                <option value="num-asc">নম্বর (ছোট থেকে বড়)</option>
                <option value="num-desc">নম্বর (বড় থেকে ছোট)</option>
                <option value="name-asc">নাম (A to Z)</option>
                <option value="name-desc">নাম (Z to A)</option>
            </select>
        </div>

        <!-- ওভারভিউ -->
        <div id="sec-overview">
            <div class="card admin-only">
                <div class="grid-stats">
                    <div class="stat-box active-card" id="card-total" onclick="filterByCard('all', this)">
                        <p>টোটাল বিল/নম্বর</p>
                        <h3 id="stat-total-count">0</h3>
                    </div>
                    <div class="stat-box" id="card-tel" onclick="filterByCard('টেলিফোন নম্বর', this)">
                        <p>টেলিফোন</p>
                        <h3 id="stat-tel-count">0</h3>
                    </div>
                    <div class="stat-box" id="card-tel-wifi" onclick="filterByCard('টেলিফোন+ওয়াইফাই নম্বর', this)">
                        <p>টেলি+ওয়াইফাই</p>
                        <h3 id="stat-tel-wifi-count">0</h3>
                    </div>
                    <div class="stat-box" id="card-wifi" onclick="filterByCard('ওয়াইফাই নম্বর', this)">
                        <p>ওয়াইফাই</p>
                        <h3 id="stat-wifi-count">0</h3>
                    </div>
                    <div class="stat-box" id="card-users" onclick="navTo('sec-users')">
                        <p>টোটাল ইউজার</p>
                        <h3 id="stat-users-count" style="color:#007bff;">0</h3>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-title" style="text-align:left;" id="list-title">গ্রাহক ও সংযোগ তালিকা</div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr id="table-header-row"></tr>
                        </thead>
                        <tbody id="customer-table-body"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- নোটিফিকেশন হিস্ট্রি -->
        <div id="sec-notif-history" class="card hidden">
            <div class="card-title" style="color:#00ff66;">📜 নোটিফিকেশন হিস্ট্রি</div>
            <div id="notif-history-list"></div>
        </div>

        <!-- ১. নম্বর এড করুন (ক্যামেরা ও গ্যালারি অপশনসহ) -->
        <div id="sec-add" class="card hidden admin-only">
            <div class="card-title" id="form-add-title">নতুন নম্বর ও ডকুমেন্ট এড করুন</div>
            <form onsubmit="saveCustomer(event)">
                <input type="hidden" id="cust-id">
                <input type="text" id="cust-name" class="input-box" placeholder="গ্রাহকের নাম" required>
                <input type="tel" id="cust-phone" class="input-box" placeholder="মোবাইল নম্বর" required>
                <select id="cust-service-type" class="input-box" required>
                    <option value="">-- সেবার ধরন --</option>
                    <option value="টেলিফোন নম্বর">টেলিফোন নম্বর</option>
                    <option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই নম্বর</option>
                    <option value="ওয়াইফাই নম্বর">ওয়াইফাই নম্বর</option>
                </select>
                <input type="text" id="cust-service-no" class="input-box" placeholder="সংযোগ নম্বর" required>
                <input type="text" id="cust-address" class="input-box" placeholder="ঠিকানা" required>
                <input type="text" id="cust-note" class="input-box" placeholder="অতিরিক্ত নোট">

                <!-- ক্যামেরা ও ফাইল ফাইল সিলেক্টর (ঐচ্ছিক/Optional) -->
                <div style="font-size:12px; color:#aaa; margin-bottom:5px;">ডকুমেন্ট যুক্ত করুন (ছবি বা ফাইল তুলে দেওয়া ঐচ্ছিক):</div>
                
                <div class="camera-btn-group">
                    <button type="button" class="cam-btn" onclick="startCamera()">📷 ক্যামেরা চালু করুন</button>
                    <button type="button" class="cam-btn" onclick="triggerGallery()">📁 গ্যালারি থেকে ছবি নিন</button>
                </div>

                <!-- লুকায়িত ফাইল ইনপুট (গ্যালারির জন্য) -->
                <input type="file" id="cust-gallery-input" accept="image/*,.pdf" style="display:none;" onchange="handleGallerySelect(event)">

                <!-- লাইভ ক্যামেরা ভিউ -->
                <div id="camera-preview-container">
                    <video id="video-element" autoplay playsinline></video>
                    <button type="button" class="cam-btn" style="background:#00ff66; color:#000; margin-top:5px;" onclick="capturePhoto()">📸 ছবি তুলুন</button>
                </div>

                <!-- সিলেক্ট হওয়া ছবির প্রিভিউ -->
                <div style="text-align:center;">
                    <img id="captured-image-preview" src="" alt="ডকুমেন্ট প্রিভিউ">
                </div>

                <button type="submit" class="submit-btn" style="margin-top:10px;" id="cust-submit-btn">সংরক্ষণ করুন</button>
            </form>
        </div>

        <div id="sec-create-user" class="card hidden admin-only">
            <div class="card-title">নতুন ইউজার একাউন্ট তৈরি করুন</div>
            <form onsubmit="adminCreateUser(event)">
                <input type="text" id="adm-user-name" class="input-box" placeholder="নাম" required>
                <input type="email" id="adm-user-email" class="input-box" placeholder="ইমেইল" required>
                <input type="tel" id="adm-user-phone" class="input-box" placeholder="ফোন" required>
                <input type="text" id="adm-user-uname" class="input-box" placeholder="ইউজারনেম" required>
                <input type="password" id="adm-user-pass" class="input-box" placeholder="পাসওয়ার্ড" required>
                <button type="submit" class="submit-btn">তৈরি করুন</button>
            </form>
        </div>

        <!-- ইউজার লিস্ট -->
        <div id="sec-users" class="card hidden admin-only">
            <div class="card-title">নিবন্ধিত ইউজার তালিকা</div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>নাম</th>
                            <th>ইমেইল</th>
                            <th>ফোন</th>
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

        <!-- সিকিউরিটি -->
        <div id="sec-admin-settings" class="card hidden admin-only">
            <div class="card-title" style="color:#00ff66;">🔐 এডমিন সিকিউরিটি</div>
            <form onsubmit="updateAdminProfile(event)">
                <input type="text" id="new-admin-uname" class="input-box" placeholder="নতুন ইউজারনেম" required>
                <input type="password" id="new-admin-pass" class="input-box" placeholder="নতুন পাসওয়ার্ড" required>
                <input type="password" id="admin-sec-code" class="input-box" style="border:1px solid #ff4d4d;" placeholder="সিকিউরিটি কোড" required>
                <button type="submit" class="submit-btn" style="background:#ff4d4d; color:#fff;">আপডেট করুন</button>
            </form>
        </div>

        <!-- মেসেঞ্জার -->
        <div id="sec-messenger" class="card hidden">
            <div class="card-title" style="color:#00ff66;">💬 মেসেঞ্জার</div>
            
            <div class="messenger-layout">
                <div id="messenger-user-list-container" class="chat-user-list admin-only">
                    <div style="font-size:11px; color:#aaa; margin-bottom:5px; text-align:center;">সর্বশেষ মেসেজ অনুযায়ী সিরিয়াল</div>
                    <div id="inbox-user-list"></div>
                </div>

                <div class="chat-area" id="chat-area-main" style="width:100%;">
                    <div id="active-chat-header" class="chat-header">💬 চ্যাট বক্স</div>
                    <div id="chat-messages" class="chat-box"></div>
                    
                    <div style="display:flex; flex-direction:column; gap:5px; margin-top:5px;">
                        <input type="file" id="chat-file-input" class="input-box" style="padding:5px;" accept="image/*,.pdf,.doc">
                        <div style="display:flex; gap:5px;">
                            <input type="text" id="chat-msg-input" class="input-box" style="margin-bottom:0;" placeholder="মেসেজ টাইপ করুন...">
                            <button class="submit-btn" style="width:80px;" onclick="sendChatMessage()">পাঠান</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ডিটেইলস পপআপ -->
    <div id="details-modal" class="modal hidden">
        <div class="modal-title">📄 গ্রাহকের সম্পূর্ণ তথ্য</div>
        <div id="details-modal-content"></div>
        <button class="btn-danger" style="width:100%; margin-top:15px; padding:8px;" onclick="closeDetailsModal()">বন্ধ করুন</button>
    </div>

    <script>
        let currentUser = null;
        let customerDataCache = [];
        let activeSelectedUser = '';
        let mediaStream = null;
        let selectedFileBlob = null; // গ্যালারি বা ক্যামেরা থেকে পাওয়া ছবি জমা থাকবে

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
                    alert("রেজিস্ট্রেশন সফল হয়েছে! এডমিন অনুমোদনের পর লগইন করতে পারবেন।");
                    toggleAuthTab('login');
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
                    setInterval(loadMessengerData, 3000);
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
            
            if(isAdmin) {
                document.getElementById('chat-area-main').style.width = '65%';
            } else {
                document.getElementById('chat-area-main').style.width = '100%';
            }

            const badgeEl = document.getElementById('user-badge');
            if (isAdmin) {
                badgeEl.innerText = "👑 ADMIN";
                badgeEl.className = "role-badge admin-badge-style";
                document.getElementById('new-admin-uname').value = currentUser.username;
            } else {
                badgeEl.innerText = "👤 USER (@" + currentUser.username + ")";
                badgeEl.className = "role-badge user-badge-style";
            }

            const headerRow = document.getElementById('table-header-row');
            if (isAdmin) {
                headerRow.innerHTML = `
                    <th>ক্র.নং</th>
                    <th>নাম</th>
                    <th>মোবাইল</th>
                    <th>সেবার ধরন</th>
                    <th>সংযোগ নম্বর</th>
                    <th>ঠিকানা</th>
                    <th>ডকুমেন্ট</th>
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
            loadNotifHistory();
            checkNotifications();
            loadMessengerData();
        }

        function updateStats(data) {
            let telCount = 0, telWifiCount = 0, wifiCount = 0;
            data.forEach(c => {
                if (c.service_type === 'টেলিফোন নম্বর') telCount++;
                else if (c.service_type === 'টেলিফোন+ওয়াইফাই নম্বর') telWifiCount++;
                else if (c.service_type === 'ওয়াইফাই নম্বর') wifiCount++;
            });

            document.getElementById('stat-total-count').innerText = data.length;
            document.getElementById('stat-tel-count').innerText = telCount;
            document.getElementById('stat-tel-wifi-count').innerText = telWifiCount;
            document.getElementById('stat-wifi-count').innerText = wifiCount;
        }

        function filterCustomers() {
            const q = document.getElementById('search-input').value.toLowerCase().trim();
            let filtered = customerDataCache.filter(c => {
                return (c.name || '').toLowerCase().includes(q) ||
                       (c.phone || '').includes(q) ||
                       (c.service_no || '').toLowerCase().includes(q);
            });
            renderCustomers(filtered);
        }

        function renderCustomers(data) {
            const tbody = document.getElementById('customer-table-body');
            tbody.innerHTML = '';
            const isAdmin = currentUser.status === 'admin';

            data.forEach((c, index) => {
                const tr = document.createElement('tr');
                let docHtml = c.doc_url ? `<a href="${c.doc_url}" target="_blank" style="color:#00ff66;">📄 দেখুন</a>` : 'নাই';
                
                if (isAdmin) {
                    tr.innerHTML = `
                        <td>${index + 1}</td>
                        <td><span class="clickable-name" onclick="showCustomerDetails(${c.id})">${c.name}</span></td>
                        <td>${c.phone}</td>
                        <td>${c.service_type}</td>
                        <td><strong>${c.service_no}</strong></td>
                        <td>${c.address}</td>
                        <td>${docHtml}</td>
                        <td>
                            <a href="https://wa.me/${c.phone}" target="_blank" style="color:#00ff66;">WA</a>
                        </td>
                        <td>
                            <button class="btn-danger" onclick="deleteCustomer(${c.id})">ডিলিট</button>
                        </td>
                    `;
                } else {
                    tr.innerHTML = `
                        <td>${index + 1}</td>
                        <td><strong>${c.service_no}</strong></td>
                        <td>${c.service_type}</td>
                        <td>${c.address}</td>
                    `;
                }
                tbody.appendChild(tr);
            });
        }

        /* ---------------------------------------------------------
           ক্যামেরা ও গ্যালারি হ্যান্ডলিং
        --------------------------------------------------------- */
        async function startCamera() {
            stopCamera();
            document.getElementById('camera-preview-container').style.display = 'block';
            try {
                mediaStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' }, audio: false });
                document.getElementById('video-element').srcObject = mediaStream;
            } catch (err) {
                alert("ক্যামেরা চালু করা সম্ভব হয়নি! অনুমতি দিন বা ব্রাউজার চেক করুন।");
                document.getElementById('camera-preview-container').style.display = 'none';
            }
        }

        function stopCamera() {
            if (mediaStream) {
                mediaStream.getTracks().forEach(track => track.stop());
                mediaStream = null;
            }
            document.getElementById('camera-preview-container').style.display = 'none';
        }

        function capturePhoto() {
            const video = document.getElementById('video-element');
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth || 640;
            canvas.height = video.videoHeight || 480;
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob(blob => {
                selectedFileBlob = new File([blob], "camera_doc.jpg", { type: "image/jpeg" });
                const previewImg = document.getElementById('captured-image-preview');
                previewImg.src = URL.createObjectURL(blob);
                previewImg.style.display = 'inline-block';
                stopCamera();
            }, 'image/jpeg');
        }

        function triggerGallery() {
            stopCamera();
            document.getElementById('cust-gallery-input').click();
        }

        function handleGallerySelect(e) {
            const file = e.target.files[0];
            if (file) {
                selectedFileBlob = file;
                const previewImg = document.getElementById('captured-image-preview');
                previewImg.src = URL.createObjectURL(file);
                previewImg.style.display = 'inline-block';
            }
        }

        /* ---------------------------------------------------------
           নম্বর সেভ লজিক
        --------------------------------------------------------- */
        function saveCustomer(e) {
            e.preventDefault();

            const formData = new FormData();
            formData.append('id', document.getElementById('cust-id').value);
            formData.append('name', document.getElementById('cust-name').value);
            formData.append('phone', document.getElementById('cust-phone').value);
            formData.append('service_type', document.getElementById('cust-service-type').value);
            formData.append('service_no', document.getElementById('cust-service-no').value);
            formData.append('address', document.getElementById('cust-address').value);
            formData.append('note', document.getElementById('cust-note').value);

            // ফাইল সংযুক্ত করা (যদি গ্রহণ করা হয়)
            if (selectedFileBlob) {
                formData.append('document', selectedFileBlob);
            }

            fetch('/api/save-customer', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(res => {
                if (res.success) {
                    alert("গ্রাহক তথ্য সফলভাবে সংরক্ষিত হয়েছে!");
                    // ফর্ম রিসেট
                    document.getElementById('cust-id').value = '';
                    document.getElementById('cust-name').value = '';
                    document.getElementById('cust-phone').value = '';
                    document.getElementById('cust-service-no').value = '';
                    document.getElementById('cust-address').value = '';
                    document.getElementById('cust-note').value = '';
                    document.getElementById('captured-image-preview').style.display = 'none';
                    selectedFileBlob = null;
                    stopCamera();
                    
                    loadDashboardData();
                    navTo('sec-overview');
                } else {
                    alert("সংরক্ষণ করতে সমস্যা হয়েছে!");
                }
            });
        }

        function deleteCustomer(id) {
            if(confirm("আপনি কি এটি ডিলিট করতে চান?")) {
                fetch('/api/delete-customer', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({id: id})
                }).then(() => loadDashboardData());
            }
        }

        function showCustomerDetails(id) {
            const c = customerDataCache.find(item => item.id === id);
            if (!c) return;

            let docPreview = c.doc_url ? `<div class="modal-item"><span>ডকুমেন্ট:</span> <br><a href="${c.doc_url}" target="_blank"><img src="${c.doc_url}" style="max-width:100%; border-radius:6px; margin-top:5px;"></a></div>` : '';

            const html = `
                <div class="modal-item"><span>গ্রাহকের নাম:</span> <strong>${c.name}</strong></div>
                <div class="modal-item"><span>মোবাইল নম্বর:</span> <strong>${c.phone}</strong></div>
                <div class="modal-item"><span>সেবার ধরন:</span> <strong>${c.service_type}</strong></div>
                <div class="modal-item"><span>সংযোগ নম্বর:</span> <strong>${c.service_no}</strong></div>
                <div class="modal-item"><span>ঠিকানা:</span> <strong>${c.address}</strong></div>
                <div class="modal-item"><span>নোট:</span> <strong>${c.note || 'নাই'}</strong></div>
                ${docPreview}
            `;
            document.getElementById('details-modal-content').innerHTML = html;
            document.getElementById('details-modal').classList.remove('hidden');
            document.getElementById('overlay').classList.add('active');
        }

        function closeDetailsModal() {
            document.getElementById('details-modal').classList.add('hidden');
            document.getElementById('overlay').classList.remove('active');
        }

        /* ---------------------------------------------------------
           মেসেঞ্জার ও চ্যাটিং
        --------------------------------------------------------- */
        function loadMessengerData() {
            if (!currentUser) return;

            if (currentUser.status === 'admin') {
                fetch('/api/admin/messenger-threads')
                .then(res => res.json())
                .then(threads => {
                    const inboxBody = document.getElementById('inbox-user-list');
                    inboxBody.innerHTML = '';

                    if (threads.length === 0) {
                        inboxBody.innerHTML = '<div style="font-size:11px; text-align:center; color:#888;">কোনো চ্যাট নেই</div>';
                        return;
                    }

                    if (!activeSelectedUser && threads.length > 0) {
                        activeSelectedUser = threads[0].username;
                    }

                    threads.forEach(t => {
                        const isActive = t.username === activeSelectedUser ? 'active' : '';
                        inboxBody.innerHTML += `
                            <div class="chat-user-item ${isActive}" onclick="selectUserChat('${t.username}', '${t.name}')">
                                <div class="u-name">${t.name} (@${t.username})</div>
                                <div class="u-msg">${t.last_message || 'মেসেজ নেই'}</div>
                            </div>
                        `;
                    });

                    if (activeSelectedUser) {
                        loadSpecificUserChat(activeSelectedUser);
                    }
                });
            } else {
                loadSpecificUserChat('Khushbu23');
                document.getElementById('active-chat-header').innerText = "💬 Admin এর সাথে চ্যাট";
            }
        }

        function selectUserChat(username, name) {
            activeSelectedUser = username;
            document.getElementById('active-chat-header').innerText = "💬 " + name + " (@" + username + ")";
            loadMessengerData();
        }

        function loadSpecificUserChat(otherUser) {
            fetch('/api/messages/thread?user1=' + currentUser.username + '&user2=' + otherUser)
            .then(res => res.json())
            .then(msgs => {
                const container = document.getElementById('chat-messages');
                let html = '';

                msgs.forEach(m => {
                    let media = '';
                    if(m.file_url) {
                        if(m.file_type && m.file_type.startsWith('image/')) {
                            media = `<br><img src="${m.file_url}" style="max-width:140px; border-radius:6px; margin-top:5px;">`;
                        } else {
                            media = `<br><a href="${m.file_url}" target="_blank" style="color:#00ff66;">📄 ডাউনলোড</a>`;
                        }
                    }

                    const isMe = m.sender === currentUser.username;
                    let displayName = (m.sender_status === 'admin') ? 'Admin' : '@' + m.sender;

                    html += `<div class="chat-msg ${isMe ? 'sent' : 'received'}">
                        <strong>${displayName}:</strong> ${m.message}${media}
                    </div>`;
                });

                container.innerHTML = html;
                container.scrollTop = container.scrollHeight;
            });
        }

        function sendChatMessage() {
            const msgInput = document.getElementById('chat-msg-input');
            const fileInput = document.getElementById('chat-file-input');
            
            let receiver = 'Khushbu23'; 
            if (currentUser.status === 'admin') {
                receiver = activeSelectedUser;
            }

            if (!receiver) {
                alert("অনুগ্রহ করে বার্তা পাঠানোর জন্য একটি ইউজার সিলেক্ট করুন।");
                return;
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
                loadMessengerData();
            });
        }

        /* ---------------------------------------------------------
           নোটিফিকেশন
        --------------------------------------------------------- */
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
                            notifHtml = `<div class="notif-item" onclick="handleNotifClick('${item.type}', '${item.id}', '${item.sender || ''}')">
                                👤 <strong>নতুন রেজিস্ট্রেশন:</strong> ${item.title}
                            </div>`;
                        } else if(item.type === 'message') {
                            notifHtml = `<div class="notif-item" onclick="handleNotifClick('${item.type}', '${item.id}', '${item.sender || ''}')">
                                💬 <strong>নতুন মেসেজ:</strong> @${item.sender}: "${item.title}"
                            </div>`;
                        }
                        listBody.innerHTML += notifHtml;
                    });
                } else {
                    badge.style.display = 'none';
                    listBody.innerHTML = '<div class="notif-empty">কোনো নতুন নোটিফিকেশন নেই</div>';
                }
            });
        }

        function handleNotifClick(type, id, sender) {
            document.getElementById('notif-dropdown').classList.remove('active');
            
            fetch('/api/mark-notification-read', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ type: type, id: id, username: currentUser.username })
            }).then(() => {
                checkNotifications();
                if(type === 'registration') {
                    navTo('sec-users');
                } else if(type === 'message') {
                    navTo('sec-messenger');
                    if(currentUser.status === 'admin' && sender) {
                        activeSelectedUser = sender;
                        loadMessengerData();
                    }
                }
            });
        }

        function loadNotifHistory() {
            fetch('/api/notification-history?username=' + currentUser.username + '&status=' + currentUser.status)
            .then(res => res.json())
            .then(data => {
                const historyList = document.getElementById('notif-history-list');
                historyList.innerHTML = '';

                if(data.length === 0) {
                    historyList.innerHTML = '<div style="color:#aaa; text-align:center; padding:10px;">কোনো হিস্ট্রি পাওয়া যায়নি।</div>';
                    return;
                }

                data.forEach(item => {
                    let badgeColor = item.type === 'registration' ? '#ffaa00' : '#00ff66';
                    historyList.innerHTML += `
                        <div class="history-card">
                            <div style="font-size:11px; color:${badgeColor}; font-weight:bold; margin-bottom:4px;">
                                ${item.type === 'registration' ? '👤 রেজিস্ট্রেশন রিকোয়েস্ট' : '💬 ইনকামিং মেসেজ'}
                            </div>
                            <div style="font-size:13px;">${item.details}</div>
                            <div style="font-size:10px; color:#aaa; margin-top:4px;">সময়: ${item.timestamp}</div>
                        </div>
                    `;
                });
            });
        }

        /* ---------------------------------------------------------
           সাইডবার ও ন্যাভিগেশন
        --------------------------------------------------------- */
        function openSidebar() {
            document.getElementById('sidebar').classList.add('active');
            document.getElementById('overlay').classList.add('active');
        }

        function closeSidebar() {
            document.getElementById('sidebar').classList.remove('active');
            document.getElementById('overlay').classList.remove('active');
            stopCamera();
            closeDetailsModal();
        }

        function navTo(secId, btnEl) {
            stopCamera();
            closeSidebar();
            document.querySelectorAll('#dashboard-view > div[id^="sec-"]').forEach(d => d.classList.add('hidden'));
            document.getElementById(secId).classList.remove('hidden');

            if(secId === 'sec-notif-history') {
                loadNotifHistory();
            }

            if(btnEl) {
                document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
                btnEl.classList.add('active');
            }
        }

        function logout() {
            stopCamera();
            currentUser = null;
            location.reload();
        }

        function loadAllUsers() {
            fetch('/api/all-users').then(res => res.json()).then(users => {
                const tbody = document.getElementById('all-users-body');
                if(!tbody) return;
                tbody.innerHTML = '';
                users.forEach(u => {
                    if(u.status !== 'admin') {
                        tbody.innerHTML += `<tr>
                            <td>${u.name}</td><td>${u.email}</td><td>${u.phone}</td>
                            <td>@${u.username}</td><td>${u.password}</td><td>${u.status}</td>
                            <td><button class="btn-approve" onclick="approveUser(${u.id})">অনুমোদন</button></td>
                        </tr>`;
                    }
                });
            });
        }

        function approveUser(id) {
            fetch('/api/approve-user', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({id: id}) })
            .then(() => loadAllUsers());
        }

        function updateAdminProfile(e) { e.preventDefault(); }
        function adminCreateUser(e) { e.preventDefault(); }
    </script>
</body>
</html>
"""

# ---------------------------------------------------------
# ব্যাকএন্ড API রাউটস
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
        return jsonify({"success": False, "message": "ইউজারনেম বা ফোন নম্বরটি নিবন্ধিত!"})
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
            return jsonify({"success": False, "message": "আপনার অ্যাকাউন্টটি অনুমোদনের অপেক্ষায় আছে।"})
            
        return jsonify({
            "success": True,
            "user": {"id": user[0], "name": user[1], "email": user[2], "phone": user[3], "username": user[4], "status": user[5]}
        })
    return jsonify({"success": False, "message": "ইউজারনেম বা পাসওয়ার্ড ভুল!"})

# গ্রাহক সেভ করা (ক্যামেরা/গ্যালারি ডকুমেন্ট আপলোড সহ)
@app.route('/api/save-customer', methods=['POST'])
def save_customer():
    c_id = request.form.get('id')
    name = request.form.get('name')
    phone = request.form.get('phone')
    service_type = request.form.get('service_type')
    service_no = request.form.get('service_no')
    address = request.form.get('address')
    note = request.form.get('note', '')
    doc_file = request.files.get('document')

    doc_url = None
    if doc_file:
        upload_folder = 'static/uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, doc_file.filename)
        doc_file.save(file_path)
        doc_url = '/' + file_path

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if c_id:
        if doc_url:
            cursor.execute("UPDATE customers SET name=?, service_type=?, service_no=?, phone=?, address=?, note=?, doc_url=? WHERE id=?",
                           (name, service_type, service_no, phone, address, note, doc_url, c_id))
        else:
            cursor.execute("UPDATE customers SET name=?, service_type=?, service_no=?, phone=?, address=?, note=? WHERE id=?",
                           (name, service_type, service_no, phone, address, note, c_id))
    else:
        cursor.execute("INSERT INTO customers (name, service_type, service_no, phone, address, note, doc_url) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (name, service_type, service_no, phone, address, note, doc_url))

    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/delete-customer', methods=['POST'])
def delete_customer():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET is_deleted=1 WHERE id=?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, service_type, service_no, phone, address, note, doc_url FROM customers WHERE is_deleted=0")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "service_type": r[2], "service_no": r[3], "phone": r[4], "address": r[5], "note": r[6], "doc_url": r[7]} for r in rows])

@app.route('/api/admin/messenger-threads', methods=['GET'])
def admin_messenger_threads():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT username, name FROM users WHERE status != 'admin' AND is_deleted = 0")
    users = cursor.fetchall()

    threads = []
    for u in users:
        username, name = u[0], u[1]
        cursor.execute("""
            SELECT message, timestamp FROM messages 
            WHERE (sender=? OR receiver=?) 
            ORDER BY id DESC LIMIT 1
        """, (username, username))
        last_msg = cursor.fetchone()
        
        last_message_text = last_msg[0] if last_msg else ""
        last_timestamp = last_msg[1] if last_msg else "1970-01-01 00:00:00"

        threads.append({
            "username": username,
            "name": name,
            "last_message": last_message_text,
            "timestamp": last_timestamp
        })

    conn.close()
    threads.sort(key=lambda x: x['timestamp'], reverse=True)
    return jsonify(threads)

@app.route('/api/messages/thread', methods=['GET'])
def get_message_thread():
    u1 = request.args.get('user1')
    u2 = request.args.get('user2')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.sender, m.receiver, m.message, m.file_url, m.file_type, m.timestamp, u.status 
        FROM messages m 
        LEFT JOIN users u ON m.sender = u.username 
        WHERE (m.sender=? AND m.receiver=?) OR (m.sender=? AND m.receiver=?)
        ORDER BY m.id ASC
    """, (u1, u2, u2, u1))
    rows = cursor.fetchall()
    conn.close()

    return jsonify([{
        "sender": r[0], 
        "receiver": r[1], 
        "message": r[2], 
        "file_url": r[3], 
        "file_type": r[4], 
        "time": r[5],
        "sender_status": r[6]
    } for r in rows])

@app.route('/api/send-message', methods=['POST'])
def send_message():
    sender = request.form.get('sender')
    receiver = request.form.get('receiver')
    message = request.form.get('message', '')
    file = request.files.get('file')
    
    file_url, file_type = None, None

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

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    username = request.args.get('username')
    status = request.args.get('status')
    
    notifications = []
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if status == 'admin':
        cursor.execute("""
            SELECT id, name, username FROM users 
            WHERE status='pending' AND is_deleted=0 AND id NOT IN (
                SELECT target_id FROM read_notifications WHERE notif_type='registration'
            )
        """)
        for u in cursor.fetchall():
            notifications.append({"type": "registration", "id": u[0], "title": f"{u[1]} ({u[2]})"})

    cursor.execute("SELECT id, sender, message FROM messages WHERE receiver=? AND is_read=0 ORDER BY id DESC", (username,))
    for m in cursor.fetchall():
        notifications.append({"type": "message", "id": m[0], "sender": m[1], "title": m[2]})

    conn.close()
    return jsonify(notifications)

@app.route('/api/mark-notification-read', methods=['POST'])
def mark_notification_read():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if data.get('type') == 'message':
        cursor.execute("UPDATE messages SET is_read=1 WHERE id=?", (data.get('id'),))
    elif data.get('type') == 'registration':
        cursor.execute("INSERT INTO read_notifications (notif_type, target_id, username) VALUES ('registration', ?, ?)", 
                       (data.get('id'), data.get('username')))

    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/notification-history', methods=['GET'])
def notification_history():
    username = request.args.get('username')
    status = request.args.get('status')
    
    history = []
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if status == 'admin':
        cursor.execute("SELECT name, username, email, phone FROM users WHERE status='pending' OR status='approved' ORDER BY id DESC")
        for u in cursor.fetchall():
            history.append({
                "type": "registration",
                "details": f"রেজিস্ট্রেশন: {u[0]} (@{u[1]}) - ফোন: {u[3]}, ইমেইল: {u[2]}",
                "timestamp": "নিবন্ধন হিস্ট্রি"
            })

    cursor.execute("SELECT sender, message, timestamp FROM messages WHERE receiver=? ORDER BY id DESC LIMIT 50", (username,))
    for m in cursor.fetchall():
        history.append({
            "type": "message",
            "details": f"প্রেরক @{m[0]}: \"{m[1]}\"",
            "timestamp": m[2]
        })

    conn.close()
    return jsonify(history)

@app.route('/api/all-users', methods=['GET'])
def all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, username, password, status FROM users WHERE is_deleted=0")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "email": r[2], "phone": r[3], "username": r[4], "password": r[5], "status": r[6]} for r in rows])

@app.route('/api/approve-user', methods=['POST'])
def approve_user():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status='approved' WHERE id=?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)