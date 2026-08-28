import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_NAME = "btcl_system.db"
SECURITY_PIN = "137955"

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
            name TEXT NOT NULL,
            service_type TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            address TEXT NOT NULL,
            bill_amount REAL DEFAULT 0,
            details TEXT,
            is_deleted INTEGER DEFAULT 0
        )
    ''')

    # Messages Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sender_name TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0
        )
    ''')
    
    # Default Admin User
    cursor.execute("SELECT * FROM users WHERE username = 'Khushbu23'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (name, email, phone, username, password, is_admin, is_approved)
            VALUES (?, ?, ?, ?, ?, 1, 1)
        ''', ("Md. Khushbu Alom", "admin@btcl.gov.bd", "01751947523", "Khushbu23", "01751947523"))
        
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL Kurigram System</title>
    <style>
        :root { --primary: #00e676; --bg: #121212; --card: #1e1e1e; --text: #ffffff; --sidebar: #181818; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; }
        
        .top-navbar { background: #000; display: flex; align-items: center; justify-content: space-between; padding: 10px 15px; border-bottom: 2px solid var(--primary); position: sticky; top: 0; z-index: 1000; }
        .menu-btn { font-size: 24px; cursor: pointer; color: var(--primary); background: none; border: none; padding: 0 10px; }
        .header-title { font-size: 16px; font-weight: bold; color: var(--primary); text-align: center; flex-grow: 1; margin: 0 10px; }
        .nav-right { display: flex; align-items: center; gap: 15px; }
        .notif-box { position: relative; cursor: pointer; font-size: 20px; }
        .notif-badge { position: absolute; top: -5px; right: -8px; background: #ff5252; color: white; border-radius: 50%; padding: 2px 6px; font-size: 10px; font-weight: bold; }

        .auth-container { max-width: 400px; margin: 50px auto; background: var(--card); padding: 25px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 6px; border: 1px solid #333; background: #2a2a2a; color: #fff; box-sizing: border-box; }
        button { width: 100%; padding: 12px; border: none; border-radius: 6px; background: var(--primary); color: #000; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .btn-danger { background: #ff5252; color: #fff; }
        .btn-warning { background: #ffb74d; color: #000; }

        .sidebar-overlay { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: var(--sidebar); z-index: 2000; transition: 0.3s; padding: 15px; box-sizing: border-box; display: flex; flex-direction: column; box-shadow: 5px 0 15px rgba(0,0,0,0.7); }
        .sidebar-overlay.active { left: 0; }
        .close-sidebar { align-self: flex-end; font-size: 20px; cursor: pointer; color: #888; margin-bottom: 10px; }
        .nav-menu-list { flex-grow: 1; overflow-y: auto; }
        .nav-item { padding: 12px; margin: 6px 0; background: #222; border-radius: 6px; cursor: pointer; font-size: 14px; transition: 0.2s; }
        .nav-item:hover, .nav-item.active { background: var(--primary); color: #000; font-weight: bold; }

        .main-content { padding: 15px; max-width: 900px; margin: 0 auto; }
        .card { background: var(--card); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; margin-bottom: 20px; }
        .stat-card { background: #222; border-left: 4px solid var(--primary); padding: 12px; border-radius: 8px; text-align: center; cursor: pointer; transition: 0.2s; }
        .stat-card:hover { background: #2e2e2e; transform: translateY(-2px); }
        .stat-card h4 { margin: 0; color: #aaa; font-size: 12px; }
        .stat-card .number { font-size: 20px; font-weight: bold; color: var(--primary); margin-top: 5px; }

        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #333; padding: 10px; text-align: left; font-size: 13px; }
        th { background: #2a2a2a; color: var(--primary); }
        tr:nth-child(even) { background: #181818; }

        .backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1500; display: none; }
        .backdrop.active { display: block; }
        .hidden { display: none !important; }
    </style>
</head>
<body>

    <div class="top-navbar">
        <button id="hamburger-btn" class="menu-btn hidden" onclick="toggleSidebar()">☰</button>
        <div class="header-title">বিটিসিএল (BTCL), কুড়িগ্রাম</div>
        <div class="nav-right">
            <div id="notif-icon" class="notif-box hidden" onclick="openMessages()">
                🔔 <span id="notif-count" class="notif-badge hidden">0</span>
            </div>
        </div>
    </div>

    <div id="backdrop" class="backdrop" onclick="toggleSidebar()"></div>

    <div id="sidebar" class="sidebar-overlay">
        <div class="close-sidebar" onclick="toggleSidebar()">✖ বন্ধ করুন</div>
        <h3 style="font-size:14px; color:#888; border-bottom:1px solid #333; padding-bottom:5px;">মেনু বার</h3>
        <div class="nav-menu-list">
            <div class="nav-item active" onclick="showTab('overview')">📊 ওভারভিউ ও সার্চ</div>
            <div class="nav-item" onclick="showTab('add-entry')">➕ ১. নম্বর এড করুন</div>
            <div class="nav-item admin-only hidden" onclick="showTab('user-requests')">⏳ ২. পেন্ডিং ইউজার</div>
            <div class="nav-item admin-only hidden" onclick="showTab('all-users')">👥 ৩. সকল ইউজার তথ্য</div>
            <div class="nav-item admin-only hidden" onclick="showTab('manage-users')">❌ ৪. ইউজার ডিলিট</div>
            <div class="nav-item" onclick="showTab('customer-list')">📋 ৫. সকল গ্রাহক তালিকা</div>
            <div class="nav-item admin-only hidden" onclick="showTab('recycle-bin')">🗑️ রিসাইকেল বিন</div>
            <div class="nav-item" onclick="showTab('messages')">💬 মেসেজ ও রিকুয়েস্ট</div>
        </div>
        <button onclick="logout()" class="btn-danger" style="margin-top:auto;">লগআউট</button>
    </div>

    <!-- Login / Registration -->
    <div id="auth-section" class="auth-container">
        <div style="display:flex; gap:10px; margin-bottom:15px;">
            <button onclick="toggleAuth('login')" id="tab-login" style="background: var(--primary)">লগইন</button>
            <button onclick="toggleAuth('register')" id="tab-reg" style="background: #333; color: #fff">রেজিস্ট্রেশন</button>
        </div>

        <form id="login-form" autocomplete="off">
            <input type="text" id="login-username" placeholder="ইউজারনেম / জিমেইল / ফোন" value="" autocomplete="off" required>
            <input type="password" id="login-pass" placeholder="পাসওয়ার্ড" value="" autocomplete="new-password" required>
            <button type="submit">লগইন করুন</button>
        </form>

        <form id="reg-form" class="hidden" autocomplete="off">
            <input type="text" id="reg-name" placeholder="আপনার নাম" required>
            <input type="email" id="reg-email" placeholder="জিমেইল আইডি" required>
            <input type="text" id="reg-phone" placeholder="মোবাইল নম্বর" required>
            <input type="text" id="reg-username" placeholder="ইউজারনেম" required>
            <input type="password" id="reg-pass" placeholder="পাসওয়ার্ড" required>
            <input type="password" id="reg-confirm-pass" placeholder="কনফার্ম পাসওয়ার্ড" required>
            <button type="submit">একাউন্ট তৈরি করুন</button>
        </form>
    </div>

    <div id="app-view" class="main-content hidden">
        <div id="tab-content-overview">
            <div class="card">
                <h3>টোটাল সংযোগ ও বিলের হিসাব (ফিল্টার করতে ক্লিক করুন)</h3>
                <div class="summary-grid">
                    <div class="stat-card" onclick="filterCustomers('ALL')">
                        <h4>মোট সংযোগ / টোটাল বিল</h4>
                        <div class="number" id="stat-total">0</div>
                    </div>
                    <div class="stat-card" onclick="filterCustomers('টেলিফোন নম্বর')">
                        <h4>টেলিফোন নম্বর</h4>
                        <div class="number" id="stat-phone">0</div>
                    </div>
                    <div class="stat-card" onclick="filterCustomers('টেলিফোন+ওয়াইফাই নম্বর')">
                        <h4>টেলিফোন + ওয়াইফাই</h4>
                        <div class="number" id="stat-combo">0</div>
                    </div>
                    <div class="stat-card" onclick="filterCustomers('ওয়াইফাই নম্বর')">
                        <h4>ওয়াইফাই নম্বর</h4>
                        <div class="number" id="stat-wifi">0</div>
                    </div>
                </div>
            </div>

            <div class="card" id="filtered-section">
                <h3 id="filter-title">সকল গ্রাহক নম্বর এর তালিকা</h3>
                <input type="text" id="search-input" placeholder="খুঁজতে নাম বা ফোন নম্বর লিখুন..." oninput="handleSearch()">
                <div style="overflow-x:auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>নাম</th>
                                <th>সেবা</th>
                                <th>ফোন নম্বর</th>
                                <th>বিল পরিমাণ</th>
                                <th>ঠিকানা</th>
                            </tr>
                        </thead>
                        <tbody id="overview-table-body"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="tab-content-add-entry" class="hidden">
            <div class="card">
                <h3>নতুন তথ্য যুক্ত করুন</h3>
                <form id="add-data-form">
                    <input type="text" id="cust-name" placeholder="গ্রাহকের নাম" required>
                    <select id="cust-service" required>
                        <option value="">সেবা নির্বাচন করুন</option>
                        <option value="টেলিফোন নম্বর">টেলিফোন নম্বর</option>
                        <option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই নম্বর</option>
                        <option value="ওয়াইফাই নম্বর">ওয়াইফাই নম্বর</option>
                    </select>
                    <input type="text" id="cust-phone" placeholder="ফোন নম্বর" required>
                    <input type="number" id="cust-bill" placeholder="বিল পরিমাণ (টাকা)" required>
                    <textarea id="cust-address" placeholder="ঠিকানা" required></textarea>
                    <textarea id="cust-details" placeholder="অতিরিক্ত তথ্য"></textarea>
                    <button type="submit">ডাটা সংরক্ষণ করুন</button>
                </form>
            </div>
        </div>

        <div id="tab-content-user-requests" class="hidden">
            <div class="card">
                <h3>পেন্ডিং ইউজার পারমিশন রিকুয়েস্ট</h3>
                <div id="pending-users-list"></div>
            </div>
        </div>

        <div id="tab-content-all-users" class="hidden">
            <div class="card">
                <h3>রেজিস্টার্ড সকল ইউজারের তথ্য</h3>
                <table>
                    <thead>
                        <tr>
                            <th>আইডি</th>
                            <th>নাম</th>
                            <th>ইউজারনেম</th>
                            <th>ইমেইল</th>
                            <th>মোবাইল</th>
                            <th>পাসওয়ার্ড</th>
                        </tr>
                    </thead>
                    <tbody id="all-users-tbody"></tbody>
                </table>
            </div>
        </div>

        <div id="tab-content-manage-users" class="hidden">
            <div class="card">
                <h3>ইউজার ডিলিট করুন</h3>
                <div id="delete-users-list"></div>
            </div>
        </div>

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
                            <th>বিল (টাকা)</th>
                            <th>ঠিকানা</th>
                        </tr>
                    </thead>
                    <tbody id="customer-list-tbody"></tbody>
                </table>
            </div>
        </div>

        <div id="tab-content-recycle-bin" class="hidden">
            <div class="card">
                <h3>ডিলিট করা ফাইল (রিসাইকেল বিন)</h3>
                <div id="recycle-bin-list"></div>
            </div>
        </div>

        <div id="tab-content-messages" class="hidden">
            <div class="card">
                <h3>মেসেজ ও পারমিশন রিকুয়েস্ট</h3>
                <div id="user-msg-box" class="hidden">
                    <textarea id="msg-text" placeholder="এডমিনকে মেসেজ বা রিকুয়েস্ট পাঠান..."></textarea>
                    <button onclick="sendMessage()">মেসেজ পাঠান</button>
                </div>
                <div id="msg-history-list" style="margin-top:15px;"></div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = JSON.parse(localStorage.getItem('btcl_user')) || null;
        let allCustomersData = [];

        window.onload = () => {
            if(currentUser) initDashboard();
        };

        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
            document.getElementById('backdrop').classList.toggle('active');
        }

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
                    auth_id: document.getElementById('login-username').value,
                    password: document.getElementById('login-pass').value
                })
            });
            const data = await res.json();
            if(data.success) {
                currentUser = data.user;
                localStorage.setItem('btcl_user', JSON.stringify(currentUser));
                initDashboard();
            } else {
                alert(data.message);
            }
        };

        document.getElementById('reg-form').onsubmit = async (e) => {
            e.preventDefault();
            const pass = document.getElementById('reg-pass').value;
            if(pass !== document.getElementById('reg-confirm-pass').value) {
                alert("পাসওয়ার্ড মিলছে না!");
                return;
            }

            const res = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: document.getElementById('reg-name').value,
                    email: document.getElementById('reg-email').value,
                    phone: document.getElementById('reg-phone').value,
                    username: document.getElementById('reg-username').value,
                    password: pass
                })
            });
            const data = await res.json();
            alert(data.message);
            if(data.success) toggleAuth('login');
        };

        function initDashboard() {
            document.getElementById('auth-section').classList.add('hidden');
            document.getElementById('app-view').classList.remove('hidden');
            document.getElementById('hamburger-btn').classList.remove('hidden');
            document.getElementById('notif-icon').classList.remove('hidden');

            if(currentUser.is_admin) {
                document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('hidden'));
            } else {
                document.getElementById('user-msg-box').classList.remove('hidden');
            }

            loadStats();
            loadOverviewData();
            checkNotifications();
            setInterval(checkNotifications, 10000);
        }

        function showTab(tabName) {
            if(document.getElementById('sidebar').classList.contains('active')) toggleSidebar();

            const tabs = ['overview', 'add-entry', 'user-requests', 'all-users', 'manage-users', 'customer-list', 'recycle-bin', 'messages'];
            tabs.forEach(t => {
                const el = document.getElementById('tab-content-' + t);
                if(el) el.classList.add('hidden');
            });

            document.getElementById('tab-content-' + tabName).classList.remove('hidden');

            if(tabName === 'overview') { loadStats(); loadOverviewData(); }
            if(tabName === 'user-requests') loadPendingUsers();
            if(tabName === 'all-users') loadAllUsers();
            if(tabName === 'manage-users') loadManageUsers();
            if(tabName === 'customer-list') loadCustomerList();
            if(tabName === 'recycle-bin') loadRecycleBin();
            if(tabName === 'messages') loadMessages();
        }

        function openMessages() { showTab('messages'); }

        async function loadStats() {
            const res = await fetch('/api/stats');
            const data = await res.json();
            document.getElementById('stat-total').innerText = `${data.total} (৳${data.total_bill})`;
            document.getElementById('stat-phone').innerText = data.phone;
            document.getElementById('stat-combo').innerText = data.combo;
            document.getElementById('stat-wifi').innerText = data.wifi;
        }

        async function loadOverviewData() {
            const res = await fetch('/api/customers');
            allCustomersData = await res.json();
            renderTable(allCustomersData);
        }

        function renderTable(data) {
            let html = '';
            data.forEach((item, index) => {
                html += `<tr>
                    <td>${index + 1}</td>
                    <td>${item.name}</td>
                    <td>${item.service_type}</td>
                    <td>${item.phone_number}</td>
                    <td>৳${item.bill_amount}</td>
                    <td>${item.address}</td>
                </tr>`;
            });
            document.getElementById('overview-table-body').innerHTML = html || '<tr><td colspan="6" style="text-align:center;">কোনো রেকর্ড পাওয়া যায়নি</td></tr>';
        }

        function filterCustomers(type) {
            let filtered = [];
            if(type === 'ALL') {
                document.getElementById('filter-title').innerText = "সকল গ্রাহক ও টোটাল বিলের হিসাব";
                filtered = allCustomersData;
            } else {
                document.getElementById('filter-title').innerText = type + " - এর তালিকা";
                filtered = allCustomersData.filter(i => i.service_type === type);
            }
            renderTable(filtered);
            document.getElementById('filtered-section').scrollIntoView({ behavior: 'smooth' });
        }

        function handleSearch() {
            const q = document.getElementById('search-input').value.toLowerCase();
            const filtered = allCustomersData.filter(i => i.name.toLowerCase().includes(q) || i.phone_number.includes(q));
            renderTable(filtered);
        }

        document.getElementById('add-data-form').onsubmit = async (e) => {
            e.preventDefault();

            if(!currentUser.is_admin) {
                const pin = prompt("সিকিউরিটি পাসওয়ার্ড লিখুন:");
                if(pin !== "137955") return alert("ভুল পাসওয়ার্ড!");
            }

            const res = await fetch('/api/add-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: document.getElementById('cust-name').value,
                    service_type: document.getElementById('cust-service').value,
                    phone_number: document.getElementById('cust-phone').value,
                    bill_amount: document.getElementById('cust-bill').value,
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
                    <div><strong>${u.name}</strong> (@${u.username})<br><small>${u.email} | ${u.phone}</small></div>
                    <button onclick="approveUser(${u.id})" style="width:auto;" class="btn-warning">Approve</button>
                </div>`;
            });
            document.getElementById('pending-users-list').innerHTML = html || '<p style="color:#888;">কোনো পেন্ডিং রিকুয়েস্ট নেই</p>';
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
                html += `<tr><td>${u.id}</td><td>${u.name}</td><td>${u.username}</td><td>${u.email}</td><td>${u.phone}</td><td><code>${u.password}</code></td></tr>`;
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
                        <div><strong>${u.name}</strong> (@${u.username})</div>
                        <button onclick="deleteUserAccount(${u.id})" style="width:auto;" class="btn-danger">ডিলিট</button>
                    </div>`;
                }
            });
            document.getElementById('delete-users-list').innerHTML = html;
        }

        async function deleteUserAccount(id) {
            const pin = prompt("সিকিউরিটি পাসওয়ার্ড লিখুন:");
            if(pin !== "137955") return alert("ভুল পাসওয়ার্ড!");

            await fetch(`/api/admin/delete-user/${id}`, {method: 'POST'});
            loadManageUsers();
        }

        async function loadCustomerList() {
            const res = await fetch('/api/customers');
            const data = await res.json();
            let html = '';
            data.forEach((item, index) => {
                html += `<tr><td>${index + 1}</td><td>${item.name}</td><td>${item.service_type}</td><td>${item.phone_number}</td><td>৳${item.bill_amount}</td><td>${item.address}</td></tr>`;
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
                    <button onclick="restoreCustomer(${i.id})" style="width:auto; background:var(--primary);">Restore</button>
                </div>`;
            });
            document.getElementById('recycle-bin-list').innerHTML = html || '<p style="color:#888;">রিসাইকেল বিন ফাঁকা</p>';
        }

        async function restoreCustomer(id) {
            const pin = prompt("সিকিউরিটি পাসওয়ার্ড দিন:");
            if(pin !== "137955") return alert("ভুল পাসওয়ার্ড!");
            await fetch('/api/admin/restore-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id: id })
            });
            loadRecycleBin();
        }

        async function sendMessage() {
            const text = document.getElementById('msg-text').value;
            if(!text) return;
            await fetch('/api/messages/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ user_id: currentUser.id, sender_name: currentUser.name, message: text })
            });
            document.getElementById('msg-text').value = '';
            loadMessages();
        }

        async function loadMessages() {
            const res = await fetch(`/api/messages?user_id=${currentUser.id}&is_admin=${currentUser.is_admin}`);
            const msgs = await res.json();
            let html = '';
            msgs.forEach(m => {
                html += `<div style="background:#2a2a2a; padding:10px; margin-top:8px; border-radius:5px;">
                    <strong>${m.sender_name}</strong> <small style="color:#888;">(${m.created_at})</small><br>${m.message}
                </div>`;
            });
            document.getElementById('msg-history-list').innerHTML = html || '<p style="color:#888;">কোনো মেসেজ নেই</p>';
        }

        async function checkNotifications() {
            if(!currentUser || !currentUser.is_admin) return;
            const res = await fetch('/api/admin/unread-count');
            const data = await res.json();
            const badge = document.getElementById('notif-count');
            if(data.count > 0) {
                badge.innerText = data.count;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }

        function logout() {
            localStorage.removeItem('btcl_user');
            location.reload();
        }
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
            INSERT INTO users (name, email, phone, username, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['name'], data['email'], data['phone'], data['username'], data['password']))
        user_id = cursor.lastrowid
        cursor.execute('''
            INSERT INTO messages (user_id, sender_name, message)
            VALUES (?, ?, ?)
        ''', (user_id, data['name'], f"নতুন রেজিস্ট্রেশন রিকুয়েস্ট: {data['name']} (@{data['username']})"))
        conn.commit()
        return jsonify({"success": True, "message": "রেজিস্ট্রেশন রিকুয়েস্ট পাঠানো হয়েছে! এডমিনের অনুমোদনের অপেক্ষা করুন।"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "ইউজারনেম, ইমেইল বা ফোন নম্বরটি নিবন্ধিত রয়েছে।"})
    finally:
        conn.close()

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE (username = ? OR email = ? OR phone = ?) AND password = ?", 
                   (data['auth_id'], data['auth_id'], data['auth_id'], data['password']))
    user = cursor.fetchone()
    conn.close()

    if user:
        if user[7] == 0:
            return jsonify({"success": False, "message": "এডমিন অনুমোদনের অপেক্ষায় আছে!"})
        return jsonify({
            "success": True,
            "user": { "id": user[0], "name": user[1], "email": user[2], "phone": user[3], "username": user[4], "is_admin": user[6] }
        })
    return jsonify({"success": False, "message": "ভুল ইউজারনেম/ফোন বা পাসওয়ার্ড!"})

@app.route("/api/stats", methods=["GET"])
def get_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(bill_amount), 0) FROM customers WHERE is_deleted = 0")
    row = cursor.fetchone()
    total, total_bill = row[0], row[1]
    
    cursor.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0 AND service_type = 'টেলিফোন নম্বর'")
    phone = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0 AND service_type = 'টেলিফোন+ওয়াইফাই নম্বর'")
    combo = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM customers WHERE is_deleted = 0 AND service_type = 'ওয়াইফাই নম্বর'")
    wifi = cursor.fetchone()[0]
    conn.close()
    return jsonify({"total": total, "total_bill": total_bill, "phone": phone, "combo": combo, "wifi": wifi})

@app.route("/api/customers", methods=["GET"])
def get_customers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, service_type, phone_number, bill_amount, address FROM customers WHERE is_deleted = 0 ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "service_type": r[2], "phone_number": r[3], "bill_amount": r[4], "address": r[5]} for r in rows])

@app.route("/api/add-customer", methods=["POST"])
def add_customer():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customers (name, service_type, phone_number, bill_amount, address, details)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['service_type'], data['phone_number'], data['bill_amount'], data['address'], data['details']))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "সফলভাবে তথ্য সংরক্ষণ করা হয়েছে!"})

@app.route("/api/admin/pending-users", methods=["GET"])
def pending_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, username FROM users WHERE is_approved = 0")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "email": r[2], "phone": r[3], "username": r[4]} for r in rows])

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
    cursor.execute("SELECT id, name, email, phone, username, password, is_admin, is_approved FROM users")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "email": r[2], "phone": r[3], "username": r[4], "password": r[5], "is_admin": r[6], "is_approved": r[7]} for r in rows])

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
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET is_deleted = 0 WHERE id = ?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/messages/send", methods=["POST"])
def send_message():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (user_id, sender_name, message) VALUES (?, ?, ?)",
                   (data['user_id'], data['sender_name'], data['message']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/messages", methods=["GET"])
def get_messages():
    user_id = request.args.get('user_id')
    is_admin = request.args.get('is_admin')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if is_admin == '1':
        cursor.execute("SELECT sender_name, message, created_at FROM messages ORDER BY id DESC")
        cursor.execute("UPDATE messages SET is_read = 1")
        conn.commit()
    else:
        cursor.execute("SELECT sender_name, message, created_at FROM messages WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"sender_name": r[0], "message": r[1], "created_at": r[2]} for r in rows])

@app.route("/api/admin/unread-count", methods=["GET"])
def unread_count():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE is_read = 0")
    count = cursor.fetchone()[0]
    conn.close()
    return jsonify({"count": count})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)