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
            file_url TEXT,
            file_type TEXT,
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
        :root { --primary: #00e676; --bg: #121212; --card: #1e1e1e; --text: #ffffff; --sidebar: #181818; --chat-bg: #252525; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; }
        
        /* Sticky Top Navbar & Global Search Bar */
        .top-navbar-container { position: sticky; top: 0; z-index: 1000; background: #000; border-bottom: 2px solid var(--primary); }
        .top-navbar { display: flex; align-items: center; justify-content: space-between; padding: 8px 15px; }
        .menu-btn { font-size: 22px; cursor: pointer; color: var(--primary); background: none; border: none; }
        .header-title { font-size: 15px; font-weight: bold; color: var(--primary); text-align: center; }
        .notif-box { position: relative; cursor: pointer; font-size: 20px; }
        .notif-badge { position: absolute; top: -5px; right: -8px; background: #ff5252; color: white; border-radius: 50%; padding: 2px 6px; font-size: 10px; font-weight: bold; }

        /* Global Persistent Search Bar (YouTube Style) */
        .global-search-box { padding: 5px 15px 10px 15px; background: #000; position: relative; }
        .search-input-wrapper { position: relative; max-width: 800px; margin: 0 auto; }
        .search-input-wrapper input { width: 100%; padding: 10px 15px; border-radius: 20px; border: 1px solid #333; background: #1a1a1a; color: #fff; font-size: 14px; outline: none; }
        .search-input-wrapper input:focus { border-color: var(--primary); box-shadow: 0 0 8px rgba(0,230,118,0.3); }
        
        .search-results-dropdown { position: absolute; top: 45px; left: 0; right: 0; background: var(--card); border: 1px solid #333; border-radius: 8px; max-height: 350px; overflow-y: auto; box-shadow: 0 10px 20px rgba(0,0,0,0.8); z-index: 2000; display: none; }
        .search-item { padding: 10px 15px; border-bottom: 1px solid #2e2e2e; cursor: pointer; transition: 0.2s; }
        .search-item:hover { background: #2a2a2a; }
        .search-item-title { font-weight: bold; color: var(--primary); font-size: 14px; }
        .search-item-sub { font-size: 12px; color: #aaa; margin-top: 3px; }

        .auth-container { max-width: 400px; margin: 40px auto; background: var(--card); padding: 25px; border-radius: 10px; }
        input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 6px; border: 1px solid #333; background: #2a2a2a; color: #fff; box-sizing: border-box; }
        button { width: 100%; padding: 12px; border: none; border-radius: 6px; background: var(--primary); color: #000; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .btn-danger { background: #ff5252; color: #fff; }
        .btn-warning { background: #ffb74d; color: #000; }

        .sidebar-overlay { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: var(--sidebar); z-index: 3000; transition: 0.3s; padding: 15px; box-sizing: border-box; display: flex; flex-direction: column; }
        .sidebar-overlay.active { left: 0; }
        .close-sidebar { align-self: flex-end; font-size: 18px; cursor: pointer; color: #888; margin-bottom: 10px; }
        .nav-item { padding: 12px; margin: 5px 0; background: #222; border-radius: 6px; cursor: pointer; font-size: 14px; }
        .nav-item:hover, .nav-item.active { background: var(--primary); color: #000; font-weight: bold; }

        .main-content { padding: 15px; max-width: 900px; margin: 0 auto; }
        .card { background: var(--card); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; }
        .stat-card { background: #222; border-left: 4px solid var(--primary); padding: 10px; border-radius: 8px; text-align: center; cursor: pointer; }
        .stat-card h4 { margin: 0; color: #aaa; font-size: 11px; }
        .stat-card .number { font-size: 18px; font-weight: bold; color: var(--primary); margin-top: 5px; }

        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #333; padding: 10px; text-align: left; font-size: 13px; }
        th { background: #2a2a2a; color: var(--primary); }

        /* Messenger Premium UI */
        .chat-container { display: flex; flex-direction: column; height: 500px; background: var(--chat-bg); border-radius: 10px; overflow: hidden; border: 1px solid #333; }
        .chat-header { padding: 12px 15px; background: #1a1a1a; border-bottom: 1px solid #333; display: flex; align-items: center; justify-content: space-between; }
        .chat-body { flex-grow: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .chat-bubble { max-width: 75%; padding: 10px 14px; border-radius: 15px; font-size: 13px; line-height: 1.4; word-wrap: break-word; }
        .chat-bubble.me { background: var(--primary); color: #000; align-self: flex-end; border-bottom-right-radius: 2px; }
        .chat-bubble.other { background: #333; color: #fff; align-self: flex-start; border-bottom-left-radius: 2px; }
        .chat-bubble img, .chat-bubble video { max-width: 100%; border-radius: 8px; margin-top: 5px; }
        .typing-indicator { font-size: 11px; color: var(--primary); padding: 0 15px 5px 15px; font-style: italic; }
        .chat-footer { padding: 10px; background: #1a1a1a; display: flex; align-items: center; gap: 8px; }
        .chat-footer input[type="text"] { margin: 0; border-radius: 20px; }
        .file-btn { cursor: pointer; font-size: 20px; padding: 0 8px; }

        .backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 2500; display: none; }
        .backdrop.active { display: block; }
        .hidden { display: none !important; }
    </style>
</head>
<body>

    <div class="top-navbar-container">
        <div class="top-navbar">
            <button id="hamburger-btn" class="menu-btn hidden" onclick="toggleSidebar()">☰</button>
            <div class="header-title">বিটিসিএল (BTCL), কুড়িগ্রাম</div>
            <div id="notif-icon" class="notif-box hidden" onclick="openMessages()">
                🔔 <span id="notif-count" class="notif-badge hidden">0</span>
            </div>
        </div>

        <!-- YouTube Style Persistent Global Search Bar -->
        <div id="global-search-container" class="global-search-box hidden">
            <div class="search-input-wrapper">
                <input type="text" id="global-search-input" placeholder="🔍 নাম, মোবাইল, টেলিফোন, সেবা বা ঠিকানা দিয়ে খুঁজুন..." oninput="liveSearch()" autocomplete="off">
                <div id="search-results-dropdown" class="search-results-dropdown"></div>
            </div>
        </div>
    </div>

    <div id="backdrop" class="backdrop" onclick="toggleSidebar()"></div>

    <div id="sidebar" class="sidebar-overlay">
        <div class="close-sidebar" onclick="toggleSidebar()">✖ বন্ধ করুন</div>
        <h3 style="font-size:14px; color:#888; border-bottom:1px solid #333; padding-bottom:5px;">মেনু বার</h3>
        <div class="nav-menu-list">
            <div class="nav-item active" onclick="showTab('overview')">📊 ওভারভিউ ও ডাটা</div>
            <div class="nav-item" onclick="showTab('add-entry')">➕ ১. নম্বর এড করুন</div>
            <div class="nav-item admin-only hidden" onclick="showTab('user-requests')">⏳ ২. পেন্ডিং ইউজার</div>
            <div class="nav-item admin-only hidden" onclick="showTab('all-users')">👥 ৩. সকল ইউজার তথ্য</div>
            <div class="nav-item admin-only hidden" onclick="showTab('manage-users')">❌ ৪. ইউজার ডিলিট</div>
            <div class="nav-item" onclick="showTab('customer-list')">📋 ৫. সকল গ্রাহক তালিকা</div>
            <div class="nav-item admin-only hidden" onclick="showTab('recycle-bin')">🗑️ রিসাইকেল বিন</div>
            <div class="nav-item" onclick="showTab('messages')">💬 মেসেঞ্জার</div>
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
            <input type="text" id="login-username" placeholder="ইউজারনেম / জিমেইল / ফোন" required autocomplete="off">
            <input type="password" id="login-pass" placeholder="পাসওয়ার্ড" required autocomplete="new-password">
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

        <!-- Premium Messenger UI -->
        <div id="tab-content-messages" class="hidden">
            <div class="card" style="padding:10px;">
                <div class="chat-container">
                    <div class="chat-header">
                        <div style="font-weight:bold; color:var(--primary);">💬 বিটিসিএল লাইভ মেসেঞ্জার</div>
                        <span style="font-size:11px; color:#888;">অনলাইন হেল্পডেস্ক</span>
                    </div>
                    <div id="chat-body" class="chat-body"></div>
                    <div id="typing-indicator" class="typing-indicator hidden">মেসেজ সেন্ড হচ্ছে...</div>
                    <div class="chat-footer">
                        <label class="file-btn" title="ছবি/ভিডিও/ডকুমেন্ট দিন">
                            📎 <input type="file" id="chat-file-input" style="display:none;" onchange="handleFileSelect(this)">
                        </label>
                        <input type="text" id="chat-msg-input" placeholder="এখানে মেসেজ লিখুন..." oninput="handleTyping()">
                        <button onclick="sendChatMessage()" style="width:auto; margin:0; padding:10px 18px;">পাঠান</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentUser = JSON.parse(localStorage.getItem('btcl_user')) || null;
        let allCustomersData = [];
        let selectedFile = null;

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
            document.getElementById('global-search-container').classList.remove('hidden');

            if(currentUser.is_admin) {
                document.querySelectorAll('.admin-only').forEach(el => el.classList.remove('hidden'));
            }

            loadStats();
            loadOverviewData();
            checkNotifications();
            setInterval(checkNotifications, 5000);
            setInterval(loadMessages, 3000);
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

        /* YouTube Style Global Real-Time Search Function */
        function liveSearch() {
            const query = document.getElementById('global-search-input').value.toLowerCase().trim();
            const dropdown = document.getElementById('search-results-dropdown');

            if(!query) {
                dropdown.style.display = 'none';
                renderTable(allCustomersData);
                return;
            }

            const results = allCustomersData.filter(item => 
                item.name.toLowerCase().includes(query) ||
                item.phone_number.includes(query) ||
                item.service_type.toLowerCase().includes(query) ||
                item.address.toLowerCase().includes(query)
            );

            if(results.length > 0) {
                let html = '';
                results.forEach(r => {
                    html += `<div class="search-item" onclick="selectSearchResult('${r.phone_number}')">
                        <div class="search-item-title">${r.name} (${r.service_type})</div>
                        <div class="search-item-sub">📞 ${r.phone_number} | 🏠 ${r.address} | ৳${r.bill_amount}</div>
                    </div>`;
                });
                dropdown.innerHTML = html;
                dropdown.style.display = 'block';
            } else {
                dropdown.innerHTML = '<div class="search-item" style="color:#888;">কোনো মিল পাওয়া যায়নি</div>';
                dropdown.style.display = 'block';
            }

            renderTable(results);
        }

        function selectSearchResult(phone) {
            document.getElementById('search-results-dropdown').style.display = 'none';
            showTab('overview');
            const matched = allCustomersData.filter(i => i.phone_number === phone);
            renderTable(matched);
            document.getElementById('filtered-section').scrollIntoView({ behavior: 'smooth' });
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
                met