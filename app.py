import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "btcl_kurigram_gold_pink_super_secret_2026")

MAIN_ADMIN_USERNAME = "Khushbu23"
ADMIN_SECURITY_CODE = "137955"
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE,
            email TEXT,
            phone TEXT,
            password TEXT,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'pending',
            profile_pic TEXT DEFAULT '',
            added_by TEXT DEFAULT 'Self',
            is_deleted INTEGER DEFAULT 0,
            last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phone_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            mobile TEXT,
            service_type TEXT,
            connection_num TEXT,
            address TEXT,
            note TEXT,
            added_by TEXT DEFAULT 'Khushbu23',
            is_deleted INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            file_url TEXT,
            is_group INTEGER DEFAULT 0,
            is_read INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute("SELECT * FROM users WHERE username = ?", (MAIN_ADMIN_USERNAME,))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("01751947523")
        cursor.execute('''INSERT INTO users (name, username, email, phone, password, role, status) 
                          VALUES (?, ?, ?, ?, ?, 'main_admin', 'active')''',
                       ('Md Khushbu Alom', MAIN_ADMIN_USERNAME, 'admin@btcl.com', '01751947523', hashed_pw))

    conn.commit()
    conn.close()

def log_activity(username, action):
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activity_logs (username, action) VALUES (?, ?)", (username, action))
        conn.commit()
        conn.close()
    except:
        pass

def update_last_active():
    if 'user' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE username = ?", (session['user']['username'],))
        conn.commit()
        conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম - Smart Control Desk</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: linear-gradient(135deg, #2b001e 0%, #4a1525 50%, #1f0010 100%); color: #ffe6f2; font-family: 'Segoe UI', sans-serif; min-height: 100vh; }
        .gold-pink-header { background: linear-gradient(90deg, #d4af37 0%, #ff66b2 50%, #d4af37 100%); color: #1a000d; font-weight: bold; }
        .card-custom { background: rgba(45, 10, 30, 0.95); border: 1px solid #d4af37; border-radius: 12px; }
        .form-label { color: #ffd700; font-weight: bold; }
        .form-control, .form-select { background-color: #1a0512; color: #fff; border: 1px solid #ff66b2; }
        .form-control:focus, .form-select:focus { background-color: #2b001e; color: #fff; border-color: #d4af37; }
        .btn-gold { background: linear-gradient(45deg, #d4af37, #f3e5ab); color: #000; font-weight: bold; border: none; }
        .btn-pink { background: linear-gradient(45deg, #ff66b2, #ff1493); color: #fff; font-weight: bold; border: none; }
        .stat-card { background: rgba(212, 175, 55, 0.15); border: 1px solid #d4af37; text-align: center; cursor: pointer; padding: 10px; border-radius: 10px; transition: 0.3s; }
        .stat-card:hover { background: rgba(255, 102, 178, 0.3); transform: scale(1.02); }
        .stat-number { font-size: 18px; font-weight: bold; color: #ffd700; }
        .close-cross { font-size: 1.5rem; color: #ff66b2; cursor: pointer; }
        .close-cross:hover { color: #ffd700; }
        .chat-bubble-me { background: #ff66b2; color: #fff; border-radius: 12px 12px 0 12px; margin-left: auto; max-width: 80%; }
        .chat-bubble-them { background: #d4af37; color: #000; border-radius: 12px 12px 12px 0; margin-right: auto; max-width: 80%; }
        .avatar-img { width: 35px; height: 35px; border-radius: 50%; object-fit: cover; border: 1px solid #ffd700; }
        .suggestions-box {
            position: absolute; top: 100%; left: 0; right: 0; z-index: 1000;
            background-color: #1f0010; border: 1px solid #d4af37; border-radius: 0 0 8px 8px;
            max-height: 250px; overflow-y: auto; display: none; box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
        .suggestion-item { padding: 8px 12px; cursor: pointer; color: #ffe6f2; border-bottom: 1px solid #2b001e; }
        .suggestion-item:hover { background-color: #ff66b2; color: #000; font-weight: bold; }
        .dropdown-menu-dark { background-color: #2b001e; border: 1px solid #d4af37; }
        .dropdown-item { color: #ffe6f2; }
        .dropdown-item:hover { background-color: #ff66b2; color: #000; }
        .unread-user-big { font-size: 1.15rem !important; font-weight: 900 !important; color: #ffd700 !important; }
        .read-user-normal { font-size: 0.95rem; font-weight: normal; color: #ffe6f2; }
        .admin-banner { background: linear-gradient(90deg, #ff1493, #d4af37); color: #000; padding: 12px; border-radius: 10px; font-weight: bold; border: 2px solid #fff; }
    </style>
</head>
<body>

<div class="gold-pink-header text-center py-2 position-relative">
    <h3 class="m-0"><i class="fa-solid fa-phone-volume"></i> BTCL, কুড়িগ্রাম</h3>
    <small>Smart Management Portal</small>
</div>

<div class="container py-3">
    {% if session.get('user') %}
    
    <div id="adminGroupNotice" class="admin-banner mb-3 shadow" style="display:none;">
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <i class="fa-solid fa-bullhorn fa-lg me-2"></i>
                <span class="text-uppercase" style="letter-spacing:1px;">📢 এডমিন থেকে সর্বশেষ বার্তা:</span>
                <p id="adminNoticeText" class="mb-0 mt-1 fs-6 text-white"></p>
            </div>
            <button class="btn btn-dark btn-sm" onclick="openMessenger()"><i class="fa-solid fa-reply"></i> মেসেঞ্জারে যান</button>
        </div>
    </div>

    <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center gap-2">
            <div class="dropdown">
                <button class="btn btn-gold btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-bars"></i> নেভিগেশন মেনু
                </button>
                <ul class="dropdown-menu dropdown-menu-dark">
                    <li><a class="dropdown-item" href="#" onclick="showSection('records')"><i class="fa-solid fa-house me-2"></i>হোম (গ্রাহক তালিকা)</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openMessenger()"><i class="fa-solid fa-comments me-2"></i>মেসেঞ্জার</a></li>
                    {% if session['user']['is_admin_or_sub'] %}
                    <li><a class="dropdown-item" href="#" onclick="openAddRecordModal()"><i class="fa-solid fa-plus me-2"></i>নতুন নম্বর যোগ</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openCreateUserModal()"><i class="fa-solid fa-user-plus me-2"></i>নতুন ইউজার তৈরি</a></li>
                    {% if session['user']['role'] == 'main_admin' %}
                    <li><a class="dropdown-item" href="#" onclick="showSection('users')"><i class="fa-solid fa-users me-2"></i>ইউজার তালিকা</a></li>
                    {% endif %}
                    {% endif %}
                    <li><hr class="dropdown-divider border-secondary"></li>
                    <li><a class="dropdown-item text-danger" href="/logout"><i class="fa-solid fa-right-from-bracket me-2"></i>লগআউট</a></li>
                </ul>
            </div>
            
            <button class="btn btn-pink btn-sm" onclick="showSection('records')"><i class="fa-solid fa-house"></i> হোম</button>
            <button class="btn btn-outline-warning btn-sm" onclick="openMessenger()"><i class="fa-solid fa-comments"></i> মেসেঞ্জার <span id="messengerBadge" class="badge bg-danger"></span></button>
            
            {% if session['user']['is_admin_or_sub'] %}
            <button class="btn btn-gold btn-sm" onclick="openAddRecordModal()"><i class="fa-solid fa-plus"></i> নম্বর যোগ</button>
            <button class="btn btn-pink btn-sm" onclick="openCreateUserModal()"><i class="fa-solid fa-user-plus"></i> ইউজার তৈরি</button>
            {% endif %}
        </div>
        
        <div>
            <button class="btn btn-gold btn-sm" onclick="openProfileModal()">
                <i class="fa-solid fa-circle-user"></i> প্রোফাইল
            </button>
        </div>
    </div>

    <div class="row g-2 mb-3">
        <div class="col-md-6 position-relative">
            <div class="input-group">
                <input type="text" id="searchInput" class="form-control" placeholder="নাম, মোবাইল বা সংযোগ নম্বর লিখে খুঁজুন..." oninput="handleSearchInput()" autocomplete="off">
                <button class="btn btn-gold" onclick="loadRecords()"><i class="fa-solid fa-magnifying-glass"></i> খুঁজুন</button>
            </div>
            <div id="suggestionsBox" class="suggestions-box"></div>
        </div>
        <div class="col-md-6">
            <div class="input-group">
                <span class="input-group-text bg-dark text-warning border-pink"><i class="fa-solid fa-arrow-down-a-z"></i> সাজান:</span>
                <select id="sortSelect" class="form-select" onchange="loadRecords()">
                    <option value="id_asc">ছোট সংখ্যা থেকে বড় সংখ্যা (১, ২, ৩...)</option>
                    <option value="id_desc">বড় সংখ্যা থেকে ছোট সংখ্যা (সর্বশেষ যোগ আগে)</option>
                    <option value="name_asc">নাম অনুযায়ী (A to Z)</option>
                    <option value="name_desc">নাম অনুযায়ী উল্টো (Z to A)</option>
                </select>
            </div>
        </div>
    </div>

    <div class="row g-2 mb-3">
        <div class="col" onclick="filterService('')"><div class="stat-card">{% if session['user']['is_admin_or_sub'] %}<div class="stat-number" id="countTotal">0</div>{% endif %}<div style="font-size:12px; font-weight:bold;">সকল নম্বর</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন নম্বর')"><div class="stat-card">{% if session['user']['is_admin_or_sub'] %}<div class="stat-number" id="countTel">0</div>{% endif %}<div style="font-size:12px; font-weight:bold;">শুধুমাত্র টেলিফোন</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন+ওয়াইফাই নম্বর')"><div class="stat-card">{% if session['user']['is_admin_or_sub'] %}<div class="stat-number" id="countBoth">0</div>{% endif %}<div style="font-size:12px; font-weight:bold;">টেলিফোন+ওয়াইফাই</div></div></div>
        <div class="col" onclick="filterService('ওয়াইফাই নম্বর')"><div class="stat-card">{% if session['user']['is_admin_or_sub'] %}<div class="stat-number" id="countWifi">0</div>{% endif %}<div style="font-size:12px; font-weight:bold;">শুধুমাত্র ওয়াইফাই</div></div></div>
    </div>

    <div id="recordsSection" class="card-custom p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center border-bottom border-warning pb-2">
            <h5 class="text-warning mb-0"><i class="fa-solid fa-list"></i> গ্রাহক ও সংযোগ নম্বরসমূহ</h5>
            <span class="badge bg-gold text-dark" id="currentFilterLabel">সকল নম্বর</span>
        </div>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle mt-2">
                <thead>
                    <tr>
                        <th>সিরিয়াল</th><th>গ্রাহকের নাম</th><th>মোবাইল</th><th>সেবার ধরন</th><th>সংযোগ নম্বর</th><th>ঠিকানা</th><th>নোট</th>
                        {% if session['user']['role'] == 'main_admin' %}<th>অ্যাকশন</th>{% endif %}
                    </tr>
                </thead>
                <tbody id="recordsTableBody"></tbody>
            </table>
        </div>
    </div>

    {% else %}
    <div class="row justify-content-center mt-4">
        <div class="col-md-6">
            <div class="card-custom p-4">
                <ul class="nav nav-tabs nav-justified mb-3">
                    <li class="nav-item"><button class="nav-link active btn-gold" data-bs-toggle="tab" data-bs-target="#loginTab">লগইন</button></li>
                    <li class="nav-item"><button class="nav-link btn-pink" data-bs-toggle="tab" data-bs-target="#regTab">রেজিস্ট্রেশন</button></li>
                </ul>
                <div class="tab-content">
                    <div class="tab-pane fade show active" id="loginTab">
                        <form action="/login" method="POST">
                            <div class="mb-3"><label class="form-label">ইউজারনেম / মোবাইল</label><input type="text" name="username" class="form-control" required></div>
                            <div class="mb-3"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
                            <button type="submit" class="btn btn-gold w-100 py-2">প্রবেশ করুন</button>
                        </form>
                    </div>
                    <div class="tab-pane fade" id="regTab">
                        <form action="/register" method="POST">
                            <div class="mb-2"><label class="form-label">আপনার নাম</label><input type="text" name="name" class="form-control" required></div>
                            <div class="mb-2"><label class="form-label">ইমেইল</label><input type="email" name="email" class="form-control" required></div>
                            <div class="mb-2"><label class="form-label">মোবাইল নম্বর</label><input type="text" name="phone" class="form-control" required></div>
                            <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" required></div>
                            <div class="mb-2"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
                            <button type="submit" class="btn btn-pink w-100 py-2">রেজিস্ট্রেশন আবেদন জমা দিন</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>

<div class="modal fade" id="recordModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning" id="recordModalTitle">গ্রাহক নম্বর যোগ/এডিট</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form id="recordForm" onsubmit="saveRecord(event)" class="modal-body row g-3">
        <input type="hidden" id="rec_id" name="id">
        <div class="col-md-6"><label class="form-label">গ্রাহকের নাম *</label><input type="text" id="rec_name" name="customer_name" class="form-control" required></div>
        <div class="col-md-6"><label class="form-label">মোবাইল নম্বর</label><input type="text" id="rec_mobile" name="mobile" class="form-control"></div>
        <div class="col-md-6">
            <label class="form-label">সেবার ধরন *</label>
            <select id="rec_service" name="service_type" class="form-select" required>
                <option value="টেলিফোন নম্বর">টেলিফোন নম্বর</option>
                <option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই নম্বর</option>
                <option value="ওয়াইফাই নম্বর">ওয়াইফাই নম্বর</option>
            </select>
        </div>
        <div class="col-md-6"><label class="form-label">সংযোগ নম্বর</label><input type="text" id="rec_conn" name="connection_num" class="form-control"></div>
        <div class="col-md-6"><label class="form-label">ঠিকানা</label><input type="text" id="rec_address" name="address" class="form-control"></div>
        <div class="col-md-6"><label class="form-label">নোট</label><input type="text" id="rec_note" name="note" class="form-control"></div>
        <div class="col-12 text-end"><button type="submit" class="btn btn-gold px-4">সেভ করুন</button></div>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="messengerModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-comments"></i> মেসেঞ্জার হেল্পডেস্ক</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body row g-0">
        <div class="col-md-4 border-end border-warning pe-2" style="max-height: 400px; overflow-y:auto;">
            <div class="p-2 bg-dark rounded mb-1 text-warning fw-bold cursor-pointer" onclick="selectChatTarget('GROUP', '📢 গ্রুপ চ্যাট')">
                📢 গ্রুপ চ্যাট
            </div>
            <div id="usersChatNav"></div>
        </div>
        
        <div class="col-md-8 ps-2 d-flex flex-column" style="min-height: 380px;">
            <div id="activeChatHeader" class="fw-bold text-warning pb-2 border-bottom border-secondary">📢 গ্রুপ চ্যাট</div>
            <div id="chatMessagesBox" class="flex-grow-1 p-2 my-2 border border-secondary rounded overflow-auto" style="height:270px; background:#12020d;"></div>
            
            <form id="chatForm" onsubmit="sendChatMsg(event)" class="input-group" enctype="multipart/form-data">
                <input type="file" id="chatFileInput" name="file" class="d-none" onchange="sendFilePreview()">
                <button type="button" class="btn btn-outline-warning" onclick="document.getElementById('chatFileInput').click()"><i class="fa-solid fa-paperclip"></i></button>
                <input type="text" id="chatInputMsg" name="message" class="form-control" placeholder="মেসেজ লিখুন...">
                <button type="submit" class="btn btn-gold"><i class="fa-solid fa-paper-plane"></i></button>
            </form>
            <small id="filePreviewName" class="text-warning mt-1" style="font-size:11px;"></small>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
let activeServiceFilter = '';
let currentChatTarget = 'GROUP'; 

function loadAdminPinnedNotice() {
    fetch('/api/latest_admin_group_msg')
    .then(res => res.json())
    .then(data => {
        if(data && data.message) {
            document.getElementById('adminNoticeText').innerText = data.sender_name + ": " + data.message;
            document.getElementById('adminGroupNotice').style.display = 'block';
        }
    });
}

function loadRecords() {
    let q = document.getElementById('searchInput') ? document.getElementById('searchInput').value : '';
    let sort = document.getElementById('sortSelect') ? document.getElementById('sortSelect').value : 'id_asc';
    
    fetch(`/api/search?q=${q}&service=${encodeURIComponent(activeServiceFilter)}&sort=${sort}`)
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.records.forEach((row, idx) => {
            let displayIndex = (sort === 'id_desc') ? (data.records.length - idx) : (idx + 1);
            html += `<tr>
                <td><strong>${displayIndex}</strong></td>
                <td><span class="text-warning fw-bold">${row[1]}</span></td>
                <td>${row[2] || '-'}</td>
                <td><span class="badge bg-warning text-dark">${row[3]}</span></td>
                <td>${row[4] || '-'}</td>
                <td>${row[5] || '-'}</td>
                <td>${row[6] || '-'}</td>
                {% if session.get('user', {}).get('role') == 'main_admin' %}
                <td>
                    <button class="btn btn-warning btn-sm me-1" onclick="openEditRecordModal(${row[0]})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="deleteRecord(${row[0]})"><i class="fa-solid fa-trash"></i></button>
                </td>
                {% endif %}
            </tr>`;
        });
        if(document.getElementById('recordsTableBody')) document.getElementById('recordsTableBody').innerHTML = html;
        if(document.getElementById('countTotal')) document.getElementById('countTotal').innerText = data.counts.total;
        if(document.getElementById('countTel')) document.getElementById('countTel').innerText = data.counts.tel;
        if(document.getElementById('countBoth')) document.getElementById('countBoth').innerText = data.counts.both;
        if(document.getElementById('countWifi')) document.getElementById('countWifi').innerText = data.counts.wifi;
    });
}

function openMessenger() {
    new bootstrap.Modal(document.getElementById('messengerModal')).show();
    loadChatUsers();
    loadMessages();
}

function loadChatUsers() {
    fetch('/api/users_with_unread')
    .then(res => res.json())
    .then(users => {
        let html = '';
        users.forEach(u => {
            if(u.username !== "{{ session.get('user', {}).get('username') }}") {
                let img = u.profile_pic ? `<img src="${u.profile_pic}" class="avatar-img me-1">` : '';
                let nameClass = u.unread_count > 0 ? 'unread-user-big' : 'read-user-normal';
                let badge = u.unread_count > 0 ? `<span class="badge bg-danger ms-1">🔴 (1)</span>` : '';
                
                html += `<div class="p-2 border-bottom border-secondary d-flex align-items-center justify-content-between text-white" style="cursor:pointer;" onclick="selectChatTarget('${u.username}', '${u.name}')">
                            <div class="${nameClass}">${img} ${u.name} ${badge}</div>
                         </div>`;
            }
        });
        document.getElementById('usersChatNav').innerHTML = html;
    });
}

function selectChatTarget(target, name) {
    currentChatTarget = target;
    document.getElementById('activeChatHeader').innerText = name;
    
    fetch(`/api/mark_read?sender=${target}`).then(() => {
        loadChatUsers();
        loadMessages();
    });
}

function sendFilePreview() {
    let inp = document.getElementById('chatFileInput');
    if(inp.files.length > 0) {
        document.getElementById('filePreviewName').innerText = "সংযুক্ত ফাইল: " + inp.files[0].name;
    }
}

function loadMessages() {
    fetch(`/api/messages?target=${currentChatTarget}`)
    .then(res => res.json())
    .then(msgs => {
        let html = '';
        msgs.forEach(m => {
            let isMe = m.sender === "{{ session.get('user', {}).get('username') }}";
            let fileAttachment = '';
            if(m.file_url) {
                if(m.file_url.match(/\.(jpeg|jpg|gif|png)$/i)) {
                    fileAttachment = `<br><img src="${m.file_url}" class="img-fluid rounded mt-1" style="max-height:150px;">`;
                } else {
                    fileAttachment = `<br><a href="${m.file_url}" target="_blank" class="badge bg-dark text-warning mt-1"><i class="fa-solid fa-file-arrow-down me-1"></i> ডাউনলোড</a>`;
                }
            }
            
            html += `<div class="d-flex mb-2 ${isMe?'justify-content-end':'justify-content-start'}">
                <div class="${isMe?'chat-bubble-me':'chat-bubble-them'} p-2">
                    <small class="d-block fw-bold" style="font-size:10px;">${m.sender_name}</small>
                    ${m.message || ''}
                    ${fileAttachment}
                    <small class="d-block text-end opacity-75 mt-1" style="font-size:9px;">${m.timestamp_time}</small>
                </div>
            </div>`;
        });
        let box = document.getElementById('chatMessagesBox');
        box.innerHTML = html;
        box.scrollTop = box.scrollHeight;
    });
}

function sendChatMsg(e) {
    e.preventDefault();
    let msgInput = document.getElementById('chatInputMsg');
    let fileInput = document.getElementById('chatFileInput');
    if(!msgInput.value && fileInput.files.length === 0) return;

    let formData = new FormData(document.getElementById('chatForm'));
    formData.append('target', currentChatTarget);

    fetch('/send_message', { method: 'POST', body: formData })
    .then(() => {
        msgInput.value = '';
        fileInput.value = '';
        document.getElementById('filePreviewName').innerText = '';
        loadMessages();
        loadChatUsers();
    });
}

if(document.getElementById('searchInput')) {
    loadRecords();
    loadAdminPinnedNotice();
    setInterval(loadChatUsers, 4000);
}
</script>
</body>
</html>
"""

# --- BACKEND API ROUTES ---

@app.route('/')
def home():
    update_last_active()
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE (username = ? OR phone = ?) AND is_deleted=0", (username, username))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[5], password):
        if user[7] == 'pending':
            return "<script>alert('আপনার রেজিস্ট্রেশন আবেদন এখনও অনুমোদিত হয়নি!'); window.location='/';</script>"
        
        session['user'] = {
            'id': user[0], 
            'name': user[1], 
            'username': user[2], 
            'role': user[6],
            'profile_pic': user[8],
            'is_admin_or_sub': user[6] in ['main_admin', 'admin']
        }
        log_activity(user[2], "লগইন করেছেন")
        return redirect(url_for('home'))
    return "<script>alert('ভুল ইউজারনেম অথবা পাসওয়ার্ড!'); window.location='/';</script>"

@app.route('/api/latest_admin_group_msg')
def latest_admin_group_msg():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.message, u.name, u.role FROM messages m 
        JOIN users u ON m.sender = u.username 
        WHERE m.receiver = 'GROUP' AND (u.role = 'main_admin' OR u.role = 'admin') 
        ORDER BY m.id DESC LIMIT 1
    """)
    row = cursor.fetchone()
    conn.close()
    if row:
        sender_name = "সাপোর্ট টিম / এডমিন" if (row[2] == 'main_admin' and session.get('user',{}).get('role') != 'main_admin') else row[1]
        return jsonify({'message': row[0], 'sender_name': sender_name})
    return jsonify({})

@app.route('/api/users_with_unread')
def users_with_unread():
    if 'user' not in session: return jsonify([])
    curr_user = session['user']['username']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if session.get('user', {}).get('role') != 'main_admin':
        cursor.execute("SELECT name, username, profile_pic FROM users WHERE status='active' AND is_deleted=0 AND role != 'main_admin'")
    else:
        cursor.execute("SELECT name, username, profile_pic FROM users WHERE status='active' AND is_deleted=0")
        
    users = cursor.fetchall()
    result = []
    
    for u in users:
        cursor.execute("SELECT COUNT(*) FROM messages WHERE sender=? AND receiver=? AND is_read=0", (u[1], curr_user))
        unread_cnt = cursor.fetchone()[0]
        result.append({
            'name': u[0],
            'username': u[1],
            'profile_pic': u[2],
            'unread_count': unread_cnt
        })
        
    conn.close()
    return jsonify(result)

@app.route('/api/mark_read')
def mark_read():
    if 'user' not in session: return jsonify({'status': 'error'})
    sender = request.args.get('sender')
    curr_user = session['user']['username']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET is_read=1 WHERE sender=? AND receiver=?", (sender, curr_user))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session: return jsonify({'error': 'Unauthorized'})
    msg = request.form.get('message', '')
    sender = session['user']['username']
    target = request.form.get('target', 'GROUP')
    file_url = ""

    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"chat_{sender}_{filename}")
            file.save(filepath)
            file_url = '/' + filepath

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, receiver, message, file_url, is_group, is_read) VALUES (?, ?, ?, ?, ?, 0)", 
                   (sender, target, msg, file_url, 1 if target=='GROUP' else 0))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/messages')
def api_messages():
    if 'user' not in session: return jsonify([])
    curr_user = session['user']['username']
    target = request.args.get('target', 'GROUP')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if target == 'GROUP':
        cursor.execute("""SELECT m.id, m.sender, u.name, m.message, m.timestamp, u.role, m.file_url 
                          FROM messages m LEFT JOIN users u ON m.sender=u.username 
                          WHERE m.receiver='GROUP' ORDER BY m.id ASC""")
    else:
        cursor.execute("""SELECT m.id, m.sender, u.name, m.message, m.timestamp, u.role, m.file_url 
                          FROM messages m LEFT JOIN users u ON m.sender=u.username 
                          WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) 
                          ORDER BY m.id ASC""", (curr_user, target, target, curr_user))
    raw = cursor.fetchall()
    conn.close()
    
    msgs = []
    for r in raw:
        t_str = datetime.strptime(r[4], "%Y-%m-%d %H:%M:%S").strftime("%I:%M:%S %p") if r[4] else ""
        sender_display_name = "সাপোর্ট টিম / এডমিন" if (r[5] == 'main_admin' and session.get('user',{}).get('role') != 'main_admin') else (r[2] or r[1])
        msgs.append({'id': r[0], 'sender': r[1], 'sender_name': sender_display_name, 'message': r[3], 'timestamp_time': t_str, 'file_url': r[6]})
        
    return jsonify(msgs)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)