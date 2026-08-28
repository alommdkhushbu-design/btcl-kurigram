import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_NAME = "database.db"
SECURITY_PIN = "137955"

# ---------------------------------------------------------
# ডাটাবেস সেটআপ
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # ইউজার টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT UNIQUE, username TEXT UNIQUE, password TEXT, status TEXT DEFAULT 'pending'
        )
    ''')
    
    # গ্রাহক ডাটা টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, service TEXT, phone TEXT, amount TEXT, address TEXT, note TEXT
        )
    ''')
    
    # মেসেঞ্জার টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT, receiver TEXT, message TEXT, file_url TEXT, file_type TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ডিফল্ট এডমিন একাউন্ট
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, phone, username, password, status) VALUES (?, ?, ?, ?, ?, ?)",
                       ("Admin", "admin@btcl.gov.bd", "01700000000", "admin", "admin123", "admin"))
    
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print("Database Init Error:", e)

# ---------------------------------------------------------
# UI টেমপ্লেট
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

        .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
        .header-left { display: flex; align-items: center; gap: 8px; }
        .menu-btn, .group-btn { font-size: 18px; color: #00ff66; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; padding: 6px 10px; cursor: pointer; }
        .header-title { color: #00ff66; font-size: 14px; font-weight: bold; background: #1e1e1e; padding: 6px 10px; border-radius: 6px; border: 1px solid #2a2a2a; }
        
        .search-container { position: relative; margin-bottom: 15px; }
        .search-box { width: 100%; padding: 10px 12px 10px 35px; background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 20px; color: #fff; font-size: 13px; }
        .search-icon { position: absolute; left: 12px; top: 10px; color: #888; }

        .sidebar { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: #1e1e1e; z-index: 1000; transition: 0.3s; padding: 15px; border-right: 1px solid #333; }
        .sidebar.active { left: 0; }
        .close-btn { color: #ff4d4d; background: none; border: none; font-size: 15px; cursor: pointer; float: right; font-weight: bold; }
        
        .menu-title { color: #888; font-size: 12px; margin: 20px 0 10px 0; }
        .menu-list { display: flex; flex-direction: column; gap: 8px; }
        .menu-item { background: #2a2a2a; color: #fff; padding: 10px; border-radius: 6px; font-size: 13px; border: none; text-align: left; width: 100%; cursor: pointer; }
        .menu-item.active { background: #00e65c; color: #000; font-weight: bold; }
        .logout-btn { background: #ff4d4d; color: #fff; width: 100%; padding: 10px; border-radius: 6px; border: none; margin-top: 20px; font-weight: bold; cursor: pointer; }

        .card { background: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #2a2a2a; margin-bottom: 15px; }
        .card-title { font-size: 14px; font-weight: bold; text-align: center; margin-bottom: 12px; }
        
        .grid-stats { display: grid; grid-template-columns: 1fr; gap: 10px; text-align: center; }
        .stat-box { background: #003311; border: 1px solid #00e65c; padding: 12px; border-radius: 8px; }
        .stat-box h2 { color: #00ff66; margin-top: 5px; font-size: 20px; }
        .stat-box p { font-size: 12px; color: #ccc; }

        .input-box { width: 100%; padding: 10px; margin-bottom: 10px; background: #2a2a2a; border: 1px solid #333; border-radius: 6px; color: #fff; font-size: 13px; }
        .submit-btn { width: 100%; padding: 10px; background: #00e65c; color: #000; font-weight: bold; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }
        .btn-danger { background: #ff4d4d; color: #fff; border: none; padding: 5px 8px; border-radius: 4px; cursor: pointer; }
        .btn-edit { background: #ffaa00; color: #000; border: none; padding: 5px 8px; border-radius: 4px; cursor: pointer; margin-right: 5px; }

        .table-responsive { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background: #2a2a2a; color: #00ff66; }

        .auth-container { max-width: 400px; margin: 20px auto; background: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #2a2a2a; }
        .tab-buttons { display: flex; gap: 10px; margin-bottom: 15px; }
        .tab-btn { flex: 1; padding: 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        
        .chat-box { height: 200px; overflow-y: auto; border: 1px solid #333; border-radius: 6px; padding: 10px; margin-bottom: 10px; background: #121212; display: flex; flex-direction: column; gap: 8px; }
        .chat-msg { max-width: 85%; padding: 8px 10px; border-radius: 8px; font-size: 12px; }
        .chat-msg.sent { background: #005c26; color: #fff; align-self: flex-end; }
        .chat-msg.received { background: #2a2a2a; color: #fff; align-self: flex-start; }
        
        .hidden { display: none !important; }
        .overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 999; display: none; }
        .overlay.active { display: block; }
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
            <button id="menu-pending" class="menu-item admin-only" onclick="navTo('sec-pending', this)">⏳ ২. পেন্ডিং ইউজার</button>
            <button id="menu-users" class="menu-item admin-only" onclick="navTo('sec-users', this)">👥 ৩. সকল ইউজার তথ্য</button>
            <button class="menu-item" onclick="navTo('sec-customers', this)">📋 ৪. সকল গ্রাহক তালিকা</button>
            <button class="menu-item" onclick="navTo('sec-messenger', this)">💬 মেসেঞ্জার</button>
        </div>
        <button class="logout-btn" onclick="logout()">লগআউট</button>
    </div>

    <div id="auth-view" class="auth-container">
        <div style="color:#00ff66; text-align:center; font-weight:bold; font-size:16px; margin-bottom:15px;">বিটিসিএল (BTCL), কুড়িগ্রাম</div>
        <div class="tab-buttons">
            <button id="btn-tab-login" class="tab-btn" style="background:#00e65c; color:#000;" onclick="toggleAuthTab('login')">লগইন</button>
            <button id="btn-tab-reg" class="tab-btn" style="background:#2a2a2a; color:#fff;" onclick="toggleAuthTab('reg')">রেজিস্ট্রেশন</button>
        </div>

        <form id="form-login" onsubmit="doLogin(event)">
            <input type="text" id="log-username" class="input-box" placeholder="ইউজারনেম / জিমেইল / ফোন" required>
            <input type="password" id="log-password" class="input-box" placeholder="পাসওয়ার্ড" required>
            <button type="submit" class="submit-btn">লগইন করুন</button>
        </form>

        <form id="form-reg" class="hidden" onsubmit="sendOTP(event)">
            <input type="text" id="reg-name" class="input-box" placeholder="আপনার নাম" required>
            <input type="email" id="reg-email" class="input-box" placeholder="জিমেইল আইডি (e.g. name@gmail.com)" required>
            <input type="tel" id="reg-phone" class="input-box" placeholder="১১ ডিজিট মোবাইল নম্বর (e.g. 01712345678)" required>
            <input type="text" id="reg-username" class="input-box" placeholder="ইউজারনেম" required>
            <input type="password" id="reg-pass" class="input-box" placeholder="পাসওয়ার্ড" required>
            <input type="password" id="reg-cpass" class="input-box" placeholder="কনফার্ম পাসওয়ার্ড" required>
            <button type="submit" class="submit-btn">মোবাইল ভেরিফাই করুন (OTP পাঠান)</button>
        </form>

        <form id="form-otp" class="hidden" onsubmit="verifyOTP(event)">
            <div style="text-align:center; color:#888; font-size:12px; margin-bottom:10px;">মোবাইলে পাঠানো ৪ ডিজিটের OTP কোডটি লিখুন</div>
            <input type="text" id="otp-input" class="input-box" placeholder="OTP কোড (পরীক্ষার জন্য: 1234)" required>
            <button type="submit" class="submit-btn">ভেরিফাই করে অ্যাকাউন্ট তৈরি করুন</button>
        </form>
    </div>

    <div id="pending-user-view" class="auth-container hidden">
        <div style="color:#ffaa00; text-align:center; font-weight:bold; font-size:15px; margin-bottom:10px;">⏳ একাউন্ট পেন্ডিং অবস্থায় রয়েছে</div>
        <p style="font-size:12px; color:#ccc; text-align:center; margin-bottom:15px;">এডমিন পারমিশন না দেওয়া পর্যন্ত আপনি ডাটা দেখতে পারবেন না। মেসেঞ্জারে এডমিনের সাথে যোগাযোগ করুন।</p>
        
        <div class="card">
            <div class="card-title" style="color:#00ff66;">💬 এডমিন লাইভ চ্যাট</div>
            <div id="pending-chat-box" class="chat-box"></div>
            <div style="display:flex; gap:5px;">
                <input type="text" id="pending-msg-input" class="input-box" style="margin-bottom:0;" placeholder="মেসেজ লিখুন...">
                <button class="submit-btn" style="width:80px;" onclick="sendPendingMsg()">পাঠান</button>
            </div>
        </div>
        <button class="logout-btn" onclick="logout()">লগআউট</button>
    </div>

    <div id="dashboard-view" class="hidden">
        <div class="header">
            <div class="header-left">
                <button class="menu-btn" onclick="openSidebar()">☰</button>
                <button class="group-btn" title="গ্রুপ ব্রডকাস্ট" onclick="openGroupModal()">📢 গ্রুপ</button>
            </div>
            <div class="header-title">BTCL, কুড়িগ্রাম</div>
            <div style="font-size: 14px;" id="user-badge">👤 ইউজার</div>
        </div>

        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="search-input" class="search-box" onkeyup="filterCustomers()" placeholder="নাম, নম্বর বা ঠিকানা দিয়ে খুঁজুন...">
        </div>

        <div id="sec-overview">
            <div class="card">
                <div class="grid-stats">
                    <div class="stat-box">
                        <p>মোট গ্রাহক সংযোগ</p>
                        <h2 id="stat-total">0</h2>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-title" style="text-align:left;">গ্রাহক তথ্য তালিকা</div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>নাম</th>
                                <th>সেবা</th>
                                <th>ফোন</th>
                                <th>বিল</th>
                                <th>ঠিকানা</th>
                                <th class="admin-only">অ্যাকশন</th>
                            </tr>
                        </thead>
                        <tbody id="customer-table-body"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="sec-add" class="card hidden admin-only">
            <div class="card-title" id="form-add-title">নতুন নম্বর / ডাটা যুক্ত করুন</div>
            <form onsubmit="saveCustomer(event)">
                <input type="hidden" id="cust-id">
                <input type="text" id="cust-name" class="input-box" placeholder="গ্রাহকের নাম" required>
                <select id="cust-service" class="input-box" required>
                    <option value="">সেবা নির্বাচন করুন</option>
                    <option>টেলিফোন নম্বর</option>
                    <option>টেলিফোন+ওয়াইফাই নম্বর</option>
                    <option>ওয়াইফাই নম্বর</option>
                </select>
                <input type="text" id="cust-phone" class="input-box" placeholder="ফোন নম্বর" required>
                <input type="text" id="cust-amount" class="input-box" placeholder="বিল পরিমাণ (টাকা)" required>
                <input type="text" id="cust-address" class="input-box" placeholder="ঠিকানা" required>
                <input type="text" id="cust-note" class="input-box" placeholder="অতিরিক্ত তথ্য/ডকুমেন্ট নম্বর">
                <button type="submit" class="submit-btn" id="cust-submit-btn">ডাটা সংরক্ষণ করুন</button>
            </form>
        </div>

        <div id="sec-pending" class="card hidden admin-only">
            <div class="card-title">পেন্ডিং ইউজার পারমিশন রিকুয়েস্ট</div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>নাম</th>
                            <th>জিমেইল</th>
                            <th>ফোন</th>
                            <th>পারমিশন</th>
                        </tr>
                    </thead>
                    <tbody id="pending-users-body"></tbody>
                </table>
            </div>
        </div>

        <div id="sec-users" class="card hidden admin-only">
            <div class="card-title">সকল নিবন্ধিত ইউজার</div>
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

        <div id="sec-customers" class="card hidden">
            <div class="card-title">সকল গ্রাহকের তালিকা</div>
            <div class="table-responsive">
                <table>
                    <thead>
                        <tr>
                            <th>নাম</th>
                            <th>ফোন</th>
                            <th>ঠিকানা</th>
                            <th>নোট/ডকুমেন্ট</th>
                        </tr>
                    </thead>
                    <tbody id="all-customers-list-body"></tbody>
                </table>
            </div>
        </div>

        <div id="sec-messenger" class="card hidden">
            <div class="card-title" style="color:#00ff66;">💬 বিটিসিএল মেসেঞ্জার</div>
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

    <div id="group-modal" class="auth-container hidden" style="position:fixed; top:10%; left:5%; right:5%; z-index:1001; max-width:500px;">
        <div class="card-title" style="color:#00ff66;">📢 গ্রুপ মেসেজ (অ্যানাউন্সমেন্ট)</div>
        <div id="group-broadcast-list" class="chat-box" style="height:150px;"></div>

        <div class="admin-only">
            <input type="text" id="group-msg-input" class="input-box" placeholder="সবাইকে গ্রুপ মেসেজ পাঠান...">
            <button class="submit-btn" onclick="sendGroupBroadcast()">গ্রুপে সেন্ড করুন</button>
        </div>
        <button class="btn-danger" style="width:100%; margin-top:10px;" onclick="closeGroupModal()">বন্ধ করুন</button>
    </div>

    <script>
        let currentUser = null;
        let customerDataCache = [];

        function toggleAuthTab(tab) {
            if(tab === 'login') {
                document.getElementById('btn-tab-login').style.background = '#00e65c';
                document.getElementById('btn-tab-login').style.color = '#000';
                document.getElementById('btn-tab-reg').style.background = '#2a2a2a';
                document.getElementById('btn-tab-reg').style.color = '#fff';
                document.getElementById('form-login').classList.remove('hidden');
                document.getElementById('form-reg').classList.add('hidden');
                document.getElementById('form-otp').classList.add('hidden');
            } else {
                document.getElementById('btn-tab-reg').style.background = '#00e65c';
                document.getElementById('btn-tab-reg').style.color = '#000';
                document.getElementById('btn-tab-login').style.background = '#2a2a2a';
                document.getElementById('btn-tab-login').style.color = '#fff';
                document.getElementById('form-reg').classList.remove('hidden');
                document.getElementById('form-login').classList.add('hidden');
            }
        }

        function sendOTP(e) {
            e.preventDefault();
            const phone = document.getElementById('reg-phone').value;
            const email = document.getElementById('reg-email').value;
            const pass = document.getElementById('reg-pass').value;
            const cpass = document.getElementById('reg-cpass').value;

            if (phone.length !== 11 || !phone.startsWith("01")) {
                alert("ভুল নম্বর! মোবাইল নম্বরটি অবশ্যই ১১ ডিজিটের হতে হবে।");
                return;
            }
            if (!email.includes("@") || !email.includes(".")) {
                alert("অনুগ্রহ করে একটি সঠিক জিমেইল আইডি প্রদান করুন।");
                return;
            }
            if (pass !== cpass) {
                alert("পাসওয়ার্ড মিলছে না!");
                return;
            }

            alert("OTP কোড: 1234");
            document.getElementById('form-reg').classList.add('hidden');
            document.getElementById('form-otp').classList.remove('hidden');
        }

        function verifyOTP(e) {
            e.preventDefault();
            if (document.getElementById('otp-input').value !== "1234") {
                alert("ভুল OTP কোড!");
                return;
            }

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
                    alert("রেজিস্ট্রেশন সফল! এডমিন অনুমোদন দেওয়া পর্যন্ত অপেক্ষা করুন।");
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

                    if (currentUser.status === 'pending') {
                        document.getElementById('pending-user-view').classList.remove('hidden');
                        loadMessages();
                    } else {
                        setupRoleUI();
                        document.getElementById('dashboard-view').classList.remove('hidden');
                        loadDashboardData();
                    }
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
            document.getElementById('user-badge').innerText = isAdmin ? "👑 এডমিন" : "👤 ইউজার";
        }

        function loadDashboardData() {
            fetch('/api/customers')
            .then(res => res.json())
            .then(data => {
                customerDataCache = data;
                renderCustomers(data);
            });

            if (currentUser.status === 'admin') {
                loadPendingUsers();
                loadAllUsers();
            }
            loadMessages();
        }

        function renderCustomers(data) {
            const tbody = document.getElementById('customer-table-body');
            const tbodyAll = document.getElementById('all-customers-list-body');
            document.getElementById('stat-total').innerText = data.length;
            tbody.innerHTML = '';
            tbodyAll.innerHTML = '';

            data.forEach(c => {
                let actionBtns = currentUser.status === 'admin' ? 
                    `<td>
                        <button class="btn-edit" onclick="editCustomer(${c.id}, '${c.name}', '${c.service}', '${c.phone}', '${c.amount}', '${c.address}', '${c.note}')">এডিট</button>
                        <button class="btn-danger" onclick="deleteCustomer(${c.id})">ডিলিট</button>
                     </td>` : '';
                
                tbody.innerHTML += `
                    <tr>
                        <td>${c.name}</td>
                        <td>${c.service}</td>
                        <td>${c.phone}</td>
                        <td>৳${c.amount}</td>
                        <td>${c.address}</td>
                        ${actionBtns}
                    </tr>
                `;

                tbodyAll.innerHTML += `
                    <tr>
                        <td>${c.name}</td>
                        <td>${c.phone}</td>
                        <td>${c.address}</td>
                        <td>${c.note || '-'}</td>
                    </tr>
                `;
            });
        }

        function filterCustomers() {
            const query = document.getElementById('search-input').value.toLowerCase();
            const filtered = customerDataCache.filter(c => 
                c.name.toLowerCase().includes(query) ||
                c.phone.includes(query) ||
                c.address.toLowerCase().includes(query)
            );
            renderCustomers(filtered);
        }

        function saveCustomer(e) {
            e.preventDefault();
            const payload = {
                id: document.getElementById('cust-id').value,
                name: document.getElementById('cust-name').value,
                service: document.getElementById('cust-service').value,
                phone: document.getElementById('cust-phone').value,
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
                navTo('sec-overview');
                loadDashboardData();
            });
        }

        function editCustomer(id, name, service, phone, amount, address, note) {
            document.getElementById('cust-id').value = id;
            document.getElementById('cust-name').value = name;
            document.getElementById('cust-service').value = service;
            document.getElementById('cust-phone').value = phone;
            document.getElementById('cust-amount').value = amount;
            document.getElementById('cust-address').value = address;
            document.getElementById('cust-note').value = note;
            navTo('sec-add');
        }

        function deleteCustomer(id) {
            const pin = prompt("ডিলিট করতে সিকিউরিটি পাসওয়ার্ড দিন:");
            if (pin !== "137955") {
                alert("ভুল পাসওয়ার্ড!");
                return;
            }

            fetch('/api/delete-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id, pin: pin})
            })
            .then(res => res.json())
            .then(res => {
                alert(res.message);
                loadDashboardData();
            });
        }

        function loadPendingUsers() {
            fetch('/api/pending-users')
            .then(res => res.json())
            .then(users => {
                const tbody = document.getElementById('pending-users-body');
                tbody.innerHTML = '';
                users.forEach(u => {
                    tbody.innerHTML += `
                        <tr>
                            <td>${u.name}</td>
                            <td>${u.email}</td>
                            <td>${u.phone}</td>
                            <td><button class="submit-btn" style="padding:4px 8px; font-size:11px;" onclick="approveUser(${u.id})">পারমিশন দিন</button></td>
                        </tr>
                    `;
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
                loadDashboardData();
            });
        }

        function loadAllUsers() {
            fetch('/api/all-users')
            .then(res => res.json())
            .then(users => {
                const tbody = document.getElementById('all-users-body');
                tbody.innerHTML = '';
                users.forEach(u => {
                    if(u.username !== 'admin') {
                        tbody.innerHTML += `
                            <tr>
                                <td>${u.name}</td>
                                <td>${u.username}</td>
                                <td>${u.phone}</td>
                                <td>${u.status}</td>
                                <td><button class="btn-danger" onclick="deleteUser(${u.id})">ডিলিট</button></td>
                            </tr>
                        `;
                    }
                });
            });
        }

        function deleteUser(id) {
            const pin = prompt("সিকিউরিটি পাসওয়ার্ড:");
            if (pin !== "137955") {
                alert("ভুল পাসওয়ার্ড!");
                return;
            }
            fetch('/api/delete-user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id: id, pin: pin})
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
            const formData = new FormData();
            formData.append('sender', currentUser.username);
            formData.append('message', msgInput.value);
            if (fileInput.files[0]) formData.append('file', fileInput.files[0]);

            fetch('/api/send-message', { method: 'POST', body: formData })
            .then(() => {
                msgInput.value = '';
                fileInput.value = '';
                loadMessages();
            });
        }

        function sendPendingMsg() {
            const msgInput = document.getElementById('pending-msg-input');
            const formData = new FormData();
            formData.append('sender', currentUser.username);
            formData.append('message', msgInput.value);

            fetch('/api/send-message', { method: 'POST', body: formData })
            .then(() => {
                msgInput.value = '';
                loadMessages();
            });
        }

        function loadMessages() {
            fetch('/api/messages')
            .then(res => res.json())
            .then(msgs => {
                const container = document.getElementById('chat-messages');
                const pendingContainer = document.getElementById('pending-chat-box');
                const groupContainer = document.getElementById('group-broadcast-list');
                let html = '', groupHtml = '';

                msgs.forEach(m => {
                    let media = m.file_url ? `<br><a href="${m.file_url}" target="_blank" style="color:#00ff66;">📄 ফাইল লিঙ্ক</a>` : '';
                    const isMe = m.sender === currentUser.username;
                    const msgDiv = `<div class="chat-msg ${isMe ? 'sent' : 'received'}"><strong>${m.sender}:</strong> ${m.message}${media}</div>`;

                    html += msgDiv;
                    if(m.receiver === 'group') groupHtml += msgDiv;
                });

                if(container) container.innerHTML = html;
                if(pendingContainer) pendingContainer.innerHTML = html;
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