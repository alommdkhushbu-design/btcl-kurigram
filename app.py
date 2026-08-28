import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_NAME = "btcl_system.db"

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
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            is_approved INTEGER DEFAULT 0
        )
    ''')
    
    # Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            service_type TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            address TEXT NOT NULL,
            details TEXT,
            is_deleted INTEGER DEFAULT 0
        )
    ''')
    
    # Default Admin User
    cursor.execute("SELECT * FROM users WHERE email = 'admin@btcl.gov.bd'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (name, email, phone, password, is_admin, is_approved)
            VALUES (?, ?, ?, ?, 1, 1)
        ''', ("Md. Khushbu Alom", "admin@btcl.gov.bd", "01751947523", "01751947523"))
        
    conn.commit()
    conn.close()

init_db()
SECURITY_PIN = "137955"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL Kurigram Dashboard</title>
    <style>
        :root { --primary: #00e676; --bg: #121212; --card: #1e1e1e; --text: #ffffff; --sidebar: #181818; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; display: flex; flex-direction: column; min-height: 100vh; }
        
        .header { background: #000; text-align: center; border-bottom: 2px solid var(--primary); padding: 15px; }
        .header h1 { color: var(--primary); font-size: 20px; margin: 0 0 5px 0; }
        .header h2 { color: #bbb; font-size: 14px; margin: 0; font-weight: normal; }
        
        .auth-container { max-width: 450px; margin: 40px auto; width: 90%; background: var(--card); padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 6px; border: 1px solid #333; background: #2a2a2a; color: #fff; box-sizing: border-box; }
        button { width: 100%; padding: 12px; border: none; border-radius: 6px; background: var(--primary); color: #000; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .btn-danger { background: #ff5252; color: #fff; }
        .btn-warning { background: #ffb74d; color: #000; }
        
        /* Dashboard Layout */
        .dashboard-layout { display: flex; flex: 1; flex-direction: row; }
        .sidebar { width: 250px; background: var(--sidebar); border-right: 1px solid #282828; padding: 15px; box-sizing: border-box; }
        .sidebar h3 { font-size: 14px; color: #888; text-transform: uppercase; margin-bottom: 10px; border-bottom: 1px solid #333; padding-bottom: 5px; }
        .nav-item { padding: 12px; margin: 5px 0; background: #222; border-radius: 6px; cursor: pointer; display: block; font-size: 14px; transition: 0.2s; }
        .nav-item:hover, .nav-item.active { background: var(--primary); color: #000; font-weight: bold; }
        
        .content { flex: 1; padding: 20px; box-sizing: border-box; }
        .card { background: var(--card); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        
        /* Summary Boxes */
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: #222; border-left: 4px solid var(--primary); padding: 15px; border-radius: 8px; text-align: center; }
        .stat-card h4 { margin: 0; color: #aaa; font-size: 13px; }
        .stat-card .number { font-size: 26px; font-weight: bold; color: var(--primary); margin-top: 8px; }
        
        /* Tables */
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #333; padding: 10px; text-align: left; font-size: 13px; }
        th { background: #2a2a2a; color: var(--primary); }
        tr:nth-child(even) { background: #181818; }
        
        .hidden { display: none !important; }
        
        @media (max-width: 768px) {
            .dashboard-layout { flex-direction: column; }
            .sidebar { width: 100%; border-right: none; border-bottom: 1px solid #333; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>বাংলাদেশ টেলিকমিউনিকেশন্স কোম্পানী লিমিটেড (বিটিসিএল), কুড়িগ্রাম</h1>
        <h2 id="header-welcome">Welcome to BTCL Portal</h2>
    </div>

    <!-- Auth Section -->
    <div id="auth-section" class="auth-container">
        <div style="display:flex; gap:10px; margin-bottom:15px;">
            <button onclick="toggleAuth('login')" id="tab-login" style="background: var(--primary)">লগইন</button>
            <button onclick="toggleAuth('register')" id="tab-reg" style="background: #333; color: #fff">রেজিস্ট্রেশন</button>
        </div>

        <form id="login-form">
            <input type="text" id="login-phone" placeholder="মোবাইল নম্বর / জিমেইল" value="01751947523" required>
            <input type="password" id="login-pass" placeholder="পাসওয়ার্ড" value="01751947523" required>
            <button type="submit">লগইন করুন</button>
        </form>

        <form id="reg-form" class="hidden">
            <input type="text" id="reg-name" placeholder="আপনার নাম" required>
            <input type="email" id="reg-email" placeholder="জিমেইল আইডি" required>
            <input type="text" id="reg-phone" placeholder="মোবাইল নম্বর" required>
            <input type="password" id="reg-pass" placeholder="পাসওয়ার্ড" required>
            <input type="password" id="reg-confirm-pass" placeholder="কনফার্ম পাসওয়ার্ড" required>
            <button type="submit">একাউন্ট তৈরি করুন</button>
        </form>
    </div>

    <!-- Main Dashboard -->
    <div id="dashboard" class="dashboard-layout hidden">
        <!-- Left Sidebar Navigation -->
        <div class="sidebar">
            <h3>মেনু বার</h3>
            <div class="nav-item active" onclick="showTab('overview')">📊 ওভারভিউ ও সার্চ</div>
            <div class="nav-item" onclick="showTab('add-entry')">➕ ১. নম্বর এড করুন</div>
            <div class="nav-item admin-only hidden" onclick="showTab('user-requests')">⏳ ২. পেন্ডিং ইউজার</div>
            <div class="nav-item admin-only hidden" onclick="showTab('all-users')">👥 ৩. সকল ইউজার তথ্য</div>
            <div class="nav-item admin-only hidden" onclick="showTab('manage-users')">❌ ৪. ইউজার ডিলিট</div>
            <div class="nav-item" onclick="showTab('customer-list')">📋 ৫. সকল গ্রাহক তালিকা</div>
            <div class="nav-item admin-only hidden" onclick="showTab('recycle-bin')">🗑️ রিসাইকেল বিন</div>
            <button onclick="logout()" class="btn-danger" style="margin-top:20px;">লগআউট</button>
        </div>

        <!-- Main Content Area -->
        <div class="content">
            <!-- 0. Overview & Live Search -->
            <div id="tab-content-overview">
                <h3>টোটাল সংযোগ ও বিলের হিসাব</h3>
                <div class="summary-grid">
                    <div class="stat-card">
                        <h4>মোট গ্রাহক সংযোগ</h4>
                        <div class="number" id="stat-total">0</div>
                    </div>
                    <div class="stat-card">
                        <h4>শুধু টেলিফোন</h4>
                        <div class="number" id="stat-phone">0</div>
                    </div>
                    <div class="stat-card">
                        <h4>টেলিফোন + ওয়াইফাই</h4>
                        <div class="number" id="stat-combo">0</div>
                    </div>
                    <div class="stat-card">
                        <h4>শুধু ওয়াইফাই</h4>
                        <div class="number" id="stat-wifi">0</div>
                    </div>
                </div>

                <div class="card">
                    <h3>লাইভ সার্চ (নাম বা ফোন নম্বর)</h3>
                    <input type="text" id="search-input" placeholder="খুঁজতে এখানে নাম বা ফোন নম্বর লিখুন..." oninput="handleSearch()">
                    <div id="search-results"></div>
                </div>
            </div>

            <!-- 1. Add Entry -->
            <div id="tab-content-add-entry" class="hidden">
                <div class="card">
                    <h3>নতুন তথ্য যুক্ত করুন</h3>
                    <form id="add-data-form">
                        <input type="text" id="cust-name" placeholder="গ্রাহকের নাম" required>
                        <select id="cust-service" required>
                            <option value="">সেবা নির্বাচন করুন</option>
                            <option value="টেলিফোন">টেলিফোন</option>
                            <option value="টেলিফোন+ওয়াইফাই">টেলিফোন+ওয়াইফাই</option>
                            <option value="ওয়াইফাই">ওয়াইফাই</option>
                        </select>
                        <input type="text" id="cust-phone" placeholder="ফোন নম্বর" required>
                        <textarea id="cust-address" placeholder="ঠিকানা" required></textarea>
                        <textarea id="cust-details" placeholder="অতিরিক্ত তথ্য"></textarea>
                        <button type="submit">ডাটা সংরক্ষণ করুন</button>
                    </form>
                </div>
            </div>

            <!-- 2. Pending User Requests -->
            <div id="tab-content-user-requests" class="hidden">
                <div class="card">
                    <h3>নতুন রেজিস্ট্রেশন পারমিশন রিকুয়েস্ট</h3>
                    <div id="pending-users-list"></div>
                </div>
            </div>

            <!-- 3. All Users Info -->
            <div id="tab-content-all-users" class="hidden">
                <div class="card">
                    <h3>রেজিস্টার্ড সকল ইউজারের তালিকা ও তথ্য</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>আইডি</th>
                                <th>নাম</th>
                                <th>ইমেইল</th>
                                <th>মোবাইল</th>
                                <th>পাসওয়ার্ড</th>
                                <th>স্ট্যাটাস</th>
                            </tr>
                        </thead>
                        <tbody id="all-users-tbody"></tbody>
                    </table>
                </div>
            </div>

            <!-- 4. Manage Users (Delete User) -->
            <div id="tab-content-manage-users" class="hidden">
                <div class="card">
                    <h3>ইউজার একাউন্ট ম্যানেজমেন্ট / ডিলিট</h3>
                    <p style="color:#bbb; font-size:12px;">এখান থেকে কোনো ইউজার ডিলিট করলে সে আর সিস্টেমে প্রবেশ করতে পারবে না।</p>
                    <div id="delete-users-list"></div>
                </div>
            </div>

            <!-- 5. All Customer List -->
            <div id="tab-content-customer-list" class="hidden">
                <div class="card">
                    <h3>সিরিয়াল করা গ্রাহক তালিকা</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>সিরিয়াল</th>
                                <th>নাম</th>
                                <th>সেবার ধরণ</th>
                                <th>ফোন নম্বর</th>
                                <th>ঠিকানা</th>
                            </tr>
                        </thead>
                        <tbody id="customer-list-tbody"></tbody>
                    </table>
                </div>
            </div>

            <!-- Recycle Bin -->
            <div id="tab-content-recycle-bin" class="hidden">
                <div class="card">
                    <h3>ডিলিট করা ফাইল (রিসাইকেল বিন)</h3>
                    <div id="recycle-bin-list"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = null;

        function toggleAuth(type) {
            if(type === 'login') {
                document.getElementById('login-form').classList.remove('hidden');
                document.getElementById('reg-form').classList.add('hidden');
                document.getElementById('tab-login').style.background = 'var(--primary)';
                document.getElementById('tab-reg').style.background = '#333';
            } else {
                document.getElementById('login-form').classList.add('hidden');
                document.getElementById('reg-form').classList.remove('hidden');
                document.getElementById('tab-reg').style.background = 'var(--primary)';
                document.getElementById('tab-login').style.background = '#333';
            }
        }

        document.getElementById('login-form').onsubmit = async (e) => {
            e.preventDefault();
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    auth_id: document.getElementById('login-phone').value,
                    password: document.getElementById('login-pass').value
                })
            });
            const data = await res.json();
            if(data.success) {
                currentUser = data.user;
                initDashboard();
            } else {
                alert(data.message);
            }
        };

        document.getElementById('reg-form').onsubmit = async (e) => {
            e.preventDefault();
            const pass = document.getElementById('reg-pass').value;
            const confirmPass = document.getElementById('reg-confirm-pass').value;

            if(pass !== confirmPass) {
                alert("পাসওয়ার্ড এবং কনফার্ম পাসওয়ার্ড মিলছে না!");
                return;
            }

            const res = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: document.getElementById('reg-name').value,
                    email: document.getElementById('reg-email').value,
                    phone: document.getElementById('reg-phone').value,
                    password: pass
                })
            });
            const data = await res.json();
            alert(data.message);
            if(data.success) toggleAuth('login');
        };

        function initDashboard() {
            document.getElementById('auth-section').classList.add('hidden');
            document.getElementById('dashboard').classList.remove('hidden');
            document.getElementById('header-welcome').innerText = "Welcome " + currentUser.name + (currentUser.is_admin ? " (Admin)" : "");

            if(currentUser.is_admin) {
                document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('hidden'));
            }

            loadStats();
            loadCustomerList();
        }

        function showTab(tabName) {
            document.querySelectorAll('.sidebar .nav-item').forEach(el => el.classList.remove('active'));
            event.currentTarget.classList.add('active');

            const tabs = ['overview', 'add-entry', 'user-requests', 'all-users', 'manage-users', 'customer-list', 'recycle-bin'];
            tabs.forEach(t => {
                const el = document.getElementById('tab-content-' + t);
                if(el) el.classList.add('hidden');
            });

            document.getElementById('tab-content-' + tabName).classList.remove('hidden');

            if(tabName === 'overview') loadStats();
            if(tabName === 'user-requests') loadPendingUsers();
            if(tabName === 'all-users') loadAllUsers();
            if(tabName === 'manage-users') loadManageUsers();
            if(tabName === 'customer-list') loadCustomerList();
            if(tabName === 'recycle-bin') loadRecycleBin();
        }

        async function loadStats() {
            const res = await fetch('/api/stats');
            const data = await res.json();
            document.getElementById('stat-total').innerText = data.total;
            document.getElementById('stat-phone').innerText = data.phone;
            document.getElementById('stat-combo').innerText = data.combo;
            document.getElementById('stat-wifi').innerText = data.wifi;
        }

        async function handleSearch() {
            const query = document.getElementById('search-input').value;
            if(!query) {
                document.getElementById('search-results').innerHTML = '';
                return;
            }
            const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const results = await res.json();
            let html = '';
            results.forEach(i => {
                html += `<div style="background:#2a2a2a; padding:10px; margin-top:8px; border-left:4px solid var(--primary); border-radius:4px;">
                    <strong>${i.name}</strong> (${i.service_type}) - ${i.phone_number}<br>
                    <small>${i.address}</small>
                </div>`;
            });
            document.getElementById('search-results').innerHTML = html || '<p style="color:#888;">কোনো তথ্য পাওয়া যায়নি</p>';
        }

        document.getElementById('add-data-form').onsubmit = async (e) => {
            e.preventDefault();
            const res = await fetch('/api/add-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: document.getElementById('cust-name').value,
                    service_type: document.getElementById('cust-service').value,
                    phone_number: document.getElementById('cust-phone').value,
                    address: document.getElementById('cust-address').value,
                    details: document.getElementById('cust-details').value
                })
            });
            const data = await res.json();
            alert(data.message);
            if(data.success) {
                document.getElementById('add-data-form').reset();
                loadStats();
            }
        };

        async function loadPendingUsers() {
            const res = await fetch('/api/admin/pending-users');
            const users = await res.json();
            let html = '';
            users.forEach(u => {
                html += `<div style="display:flex; justify-content:space-between; align-items:center; background:#2a2a2a; padding:10px; margin-top:5px; border-radius:5px;">
                    <div><strong>${u.name}</strong><br><small>${u.email} | ${u.phone}</small></div>
                    <div>
                        <button onclick="approveUser(${u.id})" style="width:auto; padding:5px 10px; margin:0;" class="btn-warning">Approve</button>
                    </div>
                </div>`;
            });
            document.getElementById('pending-users-list').innerHTML = html || '<p style="color:#888;">কোনো রিকুয়েস্ট নেই</p>';
        }

        async function approveUser(id) {
            await fetch(`/api/admin/approve-user/${id}`, {method: 'POST'});
            loadPendingUsers();
        }

        async function loadAllUsers() {
            const res = await fetch('/api/admin/all-users');
            const users = await res.json();
            let html = '';
            users.forEach(u => {
                html += `<tr>
                    <td>${u.id}</td>
                    <td>${u.name}</td>
                    <td>${u.email}</td>
                    <td>${u.phone}</td>
                    <td><code>${u.password}</code></td>
                    <td>${u.is_approved ? '<span style="color:var(--primary)">Active</span>' : '<span style="color:orange">Pending</span>'}</td>
                </tr>`;
            });
            document.getElementById('all-users-tbody').innerHTML = html;
        }

        async function loadManageUsers() {
            const res = await fetch('/api/admin/all-users');
            const users = await res.json();
            let html = '';
            users.forEach(u => {
                if(!u.is_admin) {
                    html += `<div style="display:flex; justify-content:space-between; align-items:center; background:#2a2a2a; padding:10px; margin-top:5px; border-radius:5px;">
                        <div><strong>${u.name}</strong> (${u.phone})</div>
                        <button onclick="deleteUserAccount(${u.id})" style="width:auto; padding:5px 10px; margin:0;" class="btn-danger">ডিলিট করুন</button>
                    </div>`;
                }
            });
            document.getElementById('delete-users-list').innerHTML = html || '<p style="color:#888;">কোনো ইউজার নেই</p>';
        }

        async function deleteUserAccount(id) {
            if(confirm("আপনি কি নিশ্চিত এই ইউজারকে স্থায়ীভাবে ডিলিট করতে চান?")) {
                await fetch(`/api/admin/delete-user/${id}`, {method: 'POST'});
                loadManageUsers();
            }
        }

        async function loadCustomerList() {
            const res = await fetch('/api/customers');
            const data = await res.json();
            let html = '';
            data.forEach((item, index) => {
                html += `<tr>
                    <td>${index + 1}</td>
                    <td>${item.name}</td>
                    <td>${item.service_type}</td>
                    <td>${item.phone_number}</td>
                    <td>${item.address}</td>
                </tr>`;
            });
            document.getElementById('customer-list-tbody').innerHTML = html;
        }

        async function loadRecycleBin() {
            const res = await fetch('/api/admin/recycle-bin');
            const items = await res.json();
            let html = '';
            items.forEach(i => {
                html += `<div style="display:flex; justify-content:space-between; align-items:center; background:#2a2a2a; padding:10px; margin-top:5px; border-radius:5px;">
                    <div>${i.name} - ${i.phone_number}</div>
                    <button onclick="restoreCustomer(${i.id})" style="width:auto; padding:5px 10px; margin:0; background:var(--primary);">Restore</button>
                </div>`;
            });
            document.getElementById('recycle-bin-list').innerHTML = html || '<p style="color:#888;">রিসাইকেল বিন ফাঁকা</p>';
        }

        async function restoreCustomer(id) {
            const pin = prompt("সিকিউরিটি পিন দিন:");
            if(!pin) return;
            const res = await fetch('/api/admin/restore-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id: id, pin: pin })
            });
            const data = await res.json();
            alert(data.message);
            if(data.success) loadRecycleBin();
        }

        function logout() { location.reload(); }
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (name, email, phone, password)
            VALUES (?, ?, ?, ?)
        ''', (data['name'], data['email'], data['phone'], data['password']))
        conn.commit()
        return jsonify({"success": True, "message": "রেজিস্ট্রেশন সফল হয়েছে! এডমিন পারমিশন দিলে প্রবেশ করতে পারবেন।"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "ইমেইল বা ফোন নম্বরটি আগে থেকেই ব্যবহৃত হচ্ছে।"})
    finally:
        conn.close()

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    auth_id = data['auth_id']
    password = data['password']
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE (email = ? OR phone = ?) AND password = ?", (auth_id, auth_id, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        if user[6] == 0: # is_approved check
            return jsonify({"success": False, "message": "এডমিন এখনও আপনার অ্যাকাউন্টটি একটিভ করেনি!"})
        return jsonify({
            "success": True,
            "user": { "id": user[0], "name": user[1], "email": user[2], "phone": user[3], "is_admin": user[5] }
        })
    return jsonify({"success": False, "message": "ভুল নম্বর/ইমেইল অথবা পাসওয়ার্ড!"})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0 AND service_type = 'টেলিফোন'")
    phone = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0 AND service_type = 'টেলিফোন+ওয়াইফাই'")
    combo = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0 AND service_type = 'ওয়াইফাই'")
    wifi = cursor.fetchone()[0]
    
    conn.close()
    return jsonify({"total": total, "phone": phone, "combo": combo, "wifi": wifi})

@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get('q', '')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, service_type, phone_number, address FROM customers 
        WHERE is_deleted = 0 AND (name LIKE ? OR phone_number LIKE ?)
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "service_type": r[2], "phone_number": r[3], "address": r[4]} for r in rows])

@app.route("/api/customers", methods=["GET"])
def get_customers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, service_type, phone_number, address FROM customers WHERE is_deleted = 0 ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "service_type": r[2], "phone_number": r[3], "address": r[4]} for r in rows])

@app.route("/api/add-customer", methods=["POST"])
def add_customer():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customers (name, service_type, phone_number, address, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data['service_type'], data['phone_number'], data['address'], data['details']))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "গ্রাহকের তথ্য সফলভাবে সংরক্ষণ করা হয়েছে!"})

@app.route("/api/admin/pending-users", methods=["GET"])
def pending_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone FROM users WHERE is_approved = 0")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "email": r[2], "phone": r[3]} for r in rows])

@app.route("/api/admin/approve-user/<int:user_id>", methods=["POST"])
def approve_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_approved = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/admin/all-users", methods=["GET"])
def all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, password, is_admin, is_approved FROM users")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "email": r[2], "phone": r[3], "password": r[4], "is_admin": r[5], "is_approved": r[6]} for r in rows])

@app.route("/api/admin/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/admin/recycle-bin", methods=["GET"])
def recycle_bin():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone_number FROM customers WHERE is_deleted = 1")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "phone_number": r[2]} for r in rows])

@app.route("/api/admin/restore-customer", methods=["POST"])
def restore_customer():
    data = request.json
    if data.get('pin') != SECURITY_PIN:
        return jsonify({"success": False, "message": "ভুল সিকিউরিটি পাসওয়ার্ড!"})
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET is_deleted = 0 WHERE id = ?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "তথ্য পুনঃপ্রতিষ্ঠা করা হয়েছে।"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)