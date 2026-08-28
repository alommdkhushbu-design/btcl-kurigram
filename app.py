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
    
    # এডমিন একাউন্ট সেটআপ (Khushbu23)
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
        .header-left { display: flex; align-items: center; gap: 10px; }
        .menu-btn, .group-btn { font-size: 15px; color: #00ff66; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; padding: 6px 12px; cursor: pointer; }
        .header-title { color: #00ff66; font-size: 15px; font-weight: bold; background: #1e1e1e; padding: 6px 12px; border-radius: 6px; border: 1px solid #2a2a2a; }
        
        .search-container { position: relative; margin-bottom: 15px; }
        .search-box { width: 100%; padding: 12px 15px 12px 35px; background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 20px; color: #fff; font-size: 14px; }
        .search-icon { position: absolute; left: 12px; top: 12px; color: #888; }

        .sidebar { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: #1e1e1e; z-index: 1000; transition: 0.3s; padding: 15px; border-right: 1px solid #333; box-shadow: 5px 0 15px rgba(0,0,0,0.5); }
        .sidebar.active { left: 0; }
        .close-btn { color: #ff4d4d; background: none; border: none; font-size: 16px; cursor: pointer; float: right; font-weight: bold; }
        
        .menu-title { color: #888; font-size: 13px; margin: 20px 0 10px 0; }
        .menu-list { display: flex; flex-direction: column; gap: 8px; }
        .menu-item { background: #2a2a2a; color: #fff; padding: 12px; border-radius: 6px; font-size: 14px; border: none; text-align: left; width: 100%; cursor: pointer; }
        .menu-item.active { background: #00e65c; color: #000; font-weight: bold; }
        .logout-btn { background: #ff4d4d; color: #fff; width: 100%; padding: 12px; border-radius: 6px; border: none; margin-top: 20px; font-weight: bold; cursor: pointer; }

        .card { background: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #2a2a2a; margin-bottom: 15px; }
        .card-title { font-size: 15px; font-weight: bold; text-align: center; margin-bottom: 12px; }
        
        /* ৪টি ফিল্টার অপশন কার্ড */
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
        <div class="menu-title">মেনু বার</div>
        <div class="menu-list">
            <button class="menu-item active" onclick="navTo('sec-overview', this)">📊 ওভারভিউ ও ডাটা</button>
            <button id="menu-add" class="menu-item admin-only" onclick="navTo('sec-add', this)">➕ ১. নম্বর এড করুন</button>
            <button id="menu-create-user" class="menu-item admin-only" onclick="navTo('sec-create-user', this)">👤 ২. ইউজার তৈরি করুন</button>
            <button id="menu-users" class="menu-item admin-only" onclick="navTo('sec-users', this)">👥 ৩. সকল ইউজার তথ্য</button>
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
                <button class="group-btn" onclick="openGroupModal()">📢 গ্রুপ মেসেজ</button>
            </div>
            <div class="header-title">BTCL, কুড়িগ্রাম</div>
            <div style="font-size: 12px;" id="user-badge">👤 ইউজার</div>
        </div>

        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="search-input" class="search-box" onkeyup="filterCustomers()" placeholder="নাম, নম্বর, সার্ভিস বা ঠিকানা দিয়ে খুঁজুন...">
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
                                <th>মেসেজ</th>
                                <th class="admin-only">অ্যাকশন</th>
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

                <label style="font-size:12px; color:#aaa;">৫. বিলের পরিমাণ (টাকা):</label>
                <input type="number" id="cust-amount" class="input-box" placeholder="বিল পরিমাণ" required>

                <label style="font-size:12px; color:#aaa;">৬. ঠিকানা:</label>
                <input type="text" id="cust-address" class="input-box" placeholder="গ্রাহকের ঠিকানা" required>

                <label style="font-size:12px; color:#aaa;">৭. অতিরিক্ত তথ্য:</label>
                <input type="text" id="cust-note" class="input-box" placeholder="অন্যান্য তথ্য/নোট">

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
            <div class="card-title">সকল নিবন্ধিত ইউজার তালিকা</div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>নাম</th>
                            <th>ইউজারনেম</th>
                            <th>ফোন</th>
                            <th>স্ট্যাটাস</th>
                            <th>অ্যাকশন</th>
                        </tr>
                    </thead>
                    <tbody id="all-users-body"></tbody>
                </table>
            </div>
        </div>

        <div id="sec-messenger" class="card hidden">
            <div class="card-title" style="color:#00ff66;">💬 মেসেঞ্জার</div>
            <div style="margin-bottom:10px;">
                <input type="text" id="chat-user-search" class="input-box" onkeyup="filterChatUsers()" placeholder="🔍 ইউজার আইডি সার্চ করুন...">
                <select id="chat-receiver-select" class="input-box">
                    <option value="admin">এডমিন (Khushbu23)</option>
                </select>
            </div>

            <div id="chat-messages" class="chat-box"></div>
            
            <div style="display:flex; flex-direction:column; gap:5px;">
                <input type="file" id="chat-file-input" class="input-box" style="padding:5px;" accept="image/*,video/*,.pdf,.doc">
                <div style="display:flex; gap:5px;">
                    <input type="text" id="chat-msg-input" class="input-box" style="margin-bottom:0;" placeholder="মেসেজ লিখুন...">
                    <button class="submit-btn" style="width:80px;" onclick="sendChatMessage()">পাঠান</button>
                </div>
            </div>
        </div>
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
                    alert("রেজিস্ট্রেশন সফল! এখন লগইন করুন।");
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
                    alert("ইউজার একাউন্ট তৈরি সফল হয়েছে!");
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
            document.getElementById('user-badge').innerText = isAdmin ? "👑 এডমিন" : "👤 " + currentUser.username;
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
        }

        function updateStats(data) {
            let totalBill = 0, telCount = 0, telWifiCount = 0, wifiCount = 0;
            data.forEach(c => {
                totalBill += parseFloat(c.amount || 0);
                if (c.service_type === 'টেলিফোন নম্বর') telCount++;
                else if (c.service_type === 'টেলিফোন+ওয়াইফাই নম্বর') telWifiCount++;
                else if (c.service_type === 'ওয়াইফাই নম্বর') wifiCount++;
            });

            document.getElementById('stat-total-bill').innerText = '৳' + totalBill;
            document.getElementById('stat-tel-count').innerText = telCount;
            document.getElementById('stat-tel-wifi-count').innerText = telWifiCount;
            document.getElementById('stat-wifi-count').innerText = wifiCount;
        }

        function filterByCard(category, cardEl) {
            activeCategoryFilter = category;
            document.querySelectorAll('.stat-box').forEach(el => el.classList.remove('active-card'));
            cardEl.classList.add('active-card');
            
            document.getElementById('list-title').innerText = category === 'all' ? 
                'গ্রাহক ও সংযোগ তালিকা (সকল)' : 'গ্রাহক তালিকা: ' + category;
            
            filterCustomers();
        }

        function filterCustomers() {
            const q = document.getElementById('search-input').value.toLowerCase();
            const filtered = customerDataCache.filter(c => {
                const matchCategory = (activeCategoryFilter === 'all') || (c.service_type === activeCategoryFilter);
                const matchQuery = c.name.toLowerCase().includes(q) ||
                                   c.phone.includes(q) ||
                                   c.service_type.toLowerCase().includes(q) ||
                                   c.service_no.toLowerCase().includes(q) ||
                                   c.address.toLowerCase().includes(q);
                return matchCategory && matchQuery;
            });
            renderCustomers(filtered);
        }

        function renderCustomers(data) {
            const tbody = document.getElementById('customer-table-body');
            tbody.innerHTML = '';

            data.forEach((c, index) => {
                const tr = document.createElement('tr');
                let actionBtns = currentUser.status === 'admin' ? 
                    `<td>
                        <button class="btn-edit" onclick="editCustomer(${c.id}, '${c.name}', '${c.phone}', '${c.service_type}', '${c.service_no}', '${c.amount}', '${c.address}', '${c.note}')">এডিট</button>
                        <button class="btn-danger" onclick="deleteCustomer(${c.id})">ডিলিট</button>
                     </td>` : '';
                
                let formattedPhone = c.phone.startsWith('88') ? c.phone : '88' + c.phone;

                tr.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${c.name}</td>
                    <td>${c.phone}</td>
                    <td><span style="color:#00ff66;">${c.service_type}</span></td>
                    <td><strong>${c.service_no}</strong></td>
                    <td>৳${c.amount}</td>
                    <td>${c.address}</td>
                    <td>${c.note || '-'}</td>
                    <td>
                        <a href="https://wa.me/${formattedPhone}" target="_blank" class="action-link wa-link">WhatsApp</a>
                        <a href="sms:${c.phone}" class="action-link sms-link">SMS</a>
                    </td>
                    ${actionBtns}
                `;
                tbody.appendChild(tr);
            });
        }

        function saveCustomer(e) {
            e.preventDefault();
            const payload = {
                id: document.getElementById('cust-id').value,
                name: document.getElementById('cust-name').value,
                phone: document.getElementById('cust-phone').value,
                service_type: document.getElementById('cust-service-type').value,
                service_no: document.getElementById('cust-service-no').value,
                amount: document.getElementById('cust-amount').value,
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

        function editCustomer(id, name, phone, service_type, service_no, amount, address, note) {
            document.getElementById('cust-id').value = id;
            document.getElementById('cust-name').value = name;
            document.getElementById('cust-phone').value = phone;
            document.getElementById('cust-service-type').value = service_type;
            document.getElementById('cust-service-no').value = service_no;
            document.getElementById('cust-amount').value = amount;
            document.getElementById('cust-address').value = address;
            document.getElementById('cust-note').value = note;

            document.getElementById('form-add-title').innerText = 'ডাটা এডিট করুন';
            document.getElementById('cust-submit-btn').innerText = 'আপডেট করুন';
            navTo('sec-add');
        }

        function deleteCustomer(id) {
            if(!confirm("আপনি কি নিশ্চিত এই গ্রাহকের ডাটা ডিলিট করতে চান?")) return;
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

        function loadAllUsers() {
            fetch('/api/all-users')
            .then(res => res.json())
            .then(users => {
                allUsersCache = users;
                const tbody = document.getElementById('all-users-body');
                const select = document.getElementById('chat-receiver-select');
                
                if(tbody) tbody.innerHTML = '';
                if(select) select.innerHTML = '<option value="admin">এডমিন (Khushbu23)</option>';

                users.forEach(u => {
                    if(tbody && u.username !== 'Khushbu23') {
                        tbody.innerHTML += `
                            <tr>
                                <td>${u.name}</td>
                                <td><strong>${u.username}</strong></td>
                                <td>${u.phone}</td>
                                <td>${u.status}</td>
                                <td><button class="btn-danger" onclick="deleteUser(${u.id})">ডিলিট</button></td>
                            </tr>
                        `;
                    }
                    if(select && u.username !== currentUser.username) {
                        select.innerHTML += `<option value="${u.username}">${u.name} (@${u.username})</option>`;
                    }
                });
            });
        }

        function filterChatUsers() {
            const q = document.getElementById('chat-user-search').value.toLowerCase();
            const select = document.getElementById('chat-receiver-select');
            select.innerHTML = '<option value="admin">এডমিন (Khushbu23)</option>';

            allUsersCache.filter(u => u.username.toLowerCase().includes(q) || u.name.toLowerCase().includes(q)).forEach(u => {
                if(u.username !== currentUser.username) {
                    select.innerHTML += `<option value="${u.username}">${u.name} (@${u.username})</option>`;
                }
            });
        }

        function deleteUser(id) {
            if(!confirm("আপনি কি নিশ্চিত এই ইউজার ডিলিট করতে চান?")) return;
            fetch('/api/delete-user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id})
            })
            .then(res => res.json())
            .then(res => {
                alert(res.message);
                loadAllUsers();
            });
        }

        function sendChatMessage() {
            const msgInput = document.getElementById('chat-msg-input');
            const fileInput = document.getElementById('chat-file-input');
            const receiver = document.getElementById('chat-receiver-select').value;
            
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
                                <a href="sms:?body=${encodedMsg}" class="action-link sms-link">SMS পাঠাতেন</a>
                            </div>
                        </div>`;
                    } else if (m.sender === currentUser.username || m.receiver === currentUser.username || currentUser.status === 'admin') {
                        html += msgDiv;
                    }
                });

                if(container) container.innerHTML = html;
                if(groupContainer) groupContainer.innerHTML = groupHtml;
            });
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
        cursor.execute("INSERT INTO users (name, email, phone, username, password, status) VALUES (?, ?, ?, ?, ?, 'approved')",
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
    cursor.execute("SELECT id, name, email, phone, username, status FROM users WHERE (username=? OR email=? OR phone=?) AND password=?",
                   (data['username'], data['username'], data['username'], data['password']))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return jsonify({
            "success": True,
            "user": {"id": user[0], "name": user[1], "email": user[2], "phone": user[3], "username": user[4], "status": user[5]}
        })
    return jsonify({"success": False, "message": "ভুল ইউজারনেম বা পাসওয়ার্ড!"})

@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, service_type, service_no, phone, amount, address, note FROM customers")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "service_type": r[2], "service_no": r[3], "phone": r[4], "amount": r[5], "address": r[6], "note": r[7]} for r in rows])

@app.route('/api/save-customer', methods=['POST'])
def save_customer():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if data.get('id'):
        cursor.execute("UPDATE customers SET name=?, service_type=?, service_no=?, phone=?, amount=?, address=?, note=? WHERE id=?",
                       (data['name'], data['service_type'], data['service_no'], data['phone'], data['amount'], data['address'], data['note'], data['id']))
        msg = "গ্রাহক তথ্য ও নম্বর আপডেট করা হয়েছে!"
    else:
        cursor.execute("INSERT INTO customers (name, service_type, service_no, phone, amount, address, note) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (data['name'], data['service_type'], data['service_no'], data['phone'], data['amount'], data['address'], data['note']))
        msg = "নতুন নম্বর ও ডাটা সফলভাবে সংরক্ষিত হয়েছে!"
        
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": msg})

@app.route('/api/delete-customer', methods=['POST'])
def delete_customer():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM customers WHERE id=?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "ডাটা মুছে ফেলা হয়েছে!"})

@app.route('/api/all-users', methods=['GET'])
def all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, phone, status FROM users")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "username": r[2], "phone": r[3], "status": r[4]} for r in rows])

@app.route('/api/delete-user', methods=['POST'])
def delete_user():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "ইউজার একাউন্ট ডিলিট করা হয়েছে!"})

@app.route('/api/send-message', methods=['POST'])
def send_message():
    sender = request.form.get('sender')
    receiver = request.form.get('receiver', 'admin')
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