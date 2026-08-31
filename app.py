import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "btcl_kurigram_gold_pink_super_secret_2026")

MAIN_ADMIN_USERNAME = "Khushbu23"
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
            status TEXT DEFAULT 'active',
            profile_pic TEXT DEFAULT '',
            added_by TEXT DEFAULT 'Khushbu23',
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

    cursor.execute("SELECT * FROM users WHERE username = ?", (MAIN_ADMIN_USERNAME,))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("01751947523")
        cursor.execute('''INSERT INTO users (name, username, email, phone, password, role, status) 
                          VALUES (?, ?, ?, ?, ?, 'main_admin', 'active')''',
                       ('Md Khushbu Alom', MAIN_ADMIN_USERNAME, 'admin@btcl.com', '01751947523', hashed_pw))

    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম - Smart Control Desk & Chat</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: linear-gradient(135deg, #2b001e 0%, #4a1525 50%, #1f0010 100%); color: #ffe6f2; font-family: 'Segoe UI', sans-serif; min-height: 100vh; }
        .gold-pink-header { background: linear-gradient(90deg, #d4af37 0%, #ff66b2 50%, #d4af37 100%); color: #1a000d; font-weight: bold; }
        .card-custom { background: rgba(45, 10, 30, 0.95); border: 1px solid #d4af37; border-radius: 12px; }
        .form-label { color: #ffd700; font-weight: bold; }
        .form-control, .form-select { background-color: #1a0512; color: #fff; border: 1px solid #ff66b2; }
        .btn-gold { background: linear-gradient(45deg, #d4af37, #f3e5ab); color: #000; font-weight: bold; border: none; }
        .btn-pink { background: linear-gradient(45deg, #ff66b2, #ff1493); color: #fff; font-weight: bold; border: none; }
        .stat-card { background: rgba(212, 175, 55, 0.15); border: 1px solid #d4af37; text-align: center; cursor: pointer; padding: 10px; border-radius: 10px; transition: 0.3s; }
        .stat-card:hover { background: rgba(255, 102, 178, 0.3); transform: scale(1.02); }
        .stat-number { font-size: 18px; font-weight: bold; color: #ffd700; }
        .close-cross { font-size: 1.5rem; color: #ff66b2; cursor: pointer; }
        .dropdown-menu-dark { background-color: #2b001e; border: 1px solid #d4af37; }
        .dropdown-item { color: #ffe6f2; }
        .dropdown-item:hover { background-color: #ff66b2; color: #000; }
        .notification-badge { position: absolute; top: -5px; right: -5px; font-size: 10px; padding: 3px 6px; border-radius: 50%; background: #ff1493; color: white; }
        .chat-box { height: 350px; overflow-y: auto; background: #15030d; padding: 15px; border-radius: 8px; border: 1px solid #ff66b2; }
        .message-bubble { padding: 8px 12px; border-radius: 10px; margin-bottom: 8px; max-width: 75%; word-break: break-word; }
        .msg-incoming { background: #3b0d26; color: #fff; align-self: flex-start; }
        .msg-outgoing { background: #d4af37; color: #000; align-self: flex-end; margin-left: auto; }
    </style>
</head>
<body>

<div class="gold-pink-header text-center py-2">
    <h3 class="m-0"><i class="fa-solid fa-phone-volume"></i> BTCL, কুড়িগ্রাম</h3>
    <small>Smart Management Portal & Messenger</small>
</div>

<div class="container py-3">
    {% if session.get('user') %}

    <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center gap-2">
            <div class="dropdown">
                <button class="btn btn-gold btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-bars"></i> মেনু অপশন
                </button>
                <ul class="dropdown-menu dropdown-menu-dark">
                    <li><a class="dropdown-item" href="#" onclick="showHome()"><i class="fa-solid fa-house me-2"></i>হোম</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openAddRecordModal()"><i class="fa-solid fa-plus me-2"></i>নম্বর এড করা</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openCreateUserModal()"><i class="fa-solid fa-user-plus me-2"></i>ইউজার এড করা</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openUserListModal()"><i class="fa-solid fa-users me-2"></i>ইউজার তালিকা</a></li>
                </ul>
            </div>

            <button class="btn btn-pink btn-sm" onclick="showHome()"><i class="fa-solid fa-house"></i> হোম</button>
            
            <button class="btn btn-outline-warning btn-sm position-relative" onclick="openMessengerModal()">
                <i class="fa-solid fa-comments"></i> মেসেজ
                <span id="msgBadge" class="notification-badge" style="display:none;">0</span>
            </button>

            <button class="btn btn-outline-danger btn-sm position-relative" onclick="openNotificationModal()">
                <i class="fa-solid fa-bell"></i> নোটিফিকেশন
                <span id="notifBadge" class="notification-badge" style="display:none;">0</span>
            </button>
        </div>
        
        <div>
            <div class="dropdown d-inline-block">
                <button class="btn btn-gold btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-circle-user"></i> প্রোফাইল
                </button>
                <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                    <li><a class="dropdown-item" href="#" onclick="openProfileModal()"><i class="fa-solid fa-user-gear me-2"></i>প্রোফাইল আপডেট</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openCreateAdminModal()"><i class="fa-solid fa-user-shield me-2"></i>এডমিন তৈরি</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openAdminHistoryModal()"><i class="fa-solid fa-clock-rotate-left me-2"></i>এডমিন হিস্ট্রি</a></li>
                </ul>
            </div>
            <a href="/logout" class="btn btn-danger btn-sm ms-1"><i class="fa-solid fa-right-from-bracket"></i></a>
        </div>
    </div>

    <div class="row g-2 mb-3">
        <div class="col-md-6">
            <div class="input-group">
                <input type="text" id="searchInput" class="form-control" placeholder="নাম, মোবাইল বা সংযোগ নম্বর লিখে খুঁজুন..." oninput="loadRecords()">
                <button class="btn btn-gold" onclick="loadRecords()"><i class="fa-solid fa-magnifying-glass"></i> খুঁজুন</button>
            </div>
        </div>
        <div class="col-md-6">
            <div class="input-group">
                <span class="input-group-text bg-dark text-warning"><i class="fa-solid fa-arrow-down-a-z"></i> সাজান:</span>
                <select id="sortSelect" class="form-select" onchange="loadRecords()">
                    <option value="id_asc">সিরিয়াল নম্বর (১, ২, ৩...)</option>
                    <option value="id_desc">সর্বশেষ যোগ করা নম্বর আগে</option>
                    <option value="name_asc">নাম অনুযায়ী (A to Z)</option>
                </select>
            </div>
        </div>
    </div>

    <div class="row g-2 mb-3">
        <div class="col" onclick="filterService('')"><div class="stat-card"><div class="stat-number" id="countTotal">0</div><div style="font-size:12px; font-weight:bold;">সকল নম্বর</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন নম্বর')"><div class="stat-card"><div class="stat-number" id="countTel">0</div><div style="font-size:12px; font-weight:bold;">শুধুমাত্র টেলিফোন</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন+ওয়াইফাই নম্বর')"><div class="stat-card"><div class="stat-number" id="countBoth">0</div><div style="font-size:12px; font-weight:bold;">টেলিফোন+ওয়াইফাই</div></div></div>
        <div class="col" onclick="filterService('ওয়াইফাই নম্বর')"><div class="stat-card"><div class="stat-number" id="countWifi">0</div><div style="font-size:12px; font-weight:bold;">শুধুমাত্র ওয়াইফাই</div></div></div>
    </div>

    <div id="recordsSection" class="card-custom p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center border-bottom border-warning pb-2">
            <h5 class="text-warning mb-0"><i class="fa-solid fa-list"></i> গ্রাহک ও সংযোগ নম্বরসমূহ</h5>
            <span class="badge bg-warning text-dark" id="currentFilterLabel">সকল নম্বর</span>
        </div>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle mt-2">
                <thead>
                    <tr>
                        <th>সিরিয়াল</th>
                        <th>গ্রাহকের নাম</th>
                        <th>মোবাইল</th>
                        <th>সেবার ধরন</th>
                        <th>সংযোগ নম্বর</th>
                        <th>ঠিকানা</th>
                        <th>নোট</th>
                        <th>যুক্ত করেছেন</th>
                        <th>অ্যাকশন</th>
                    </tr>
                </thead>
                <tbody id="recordsTableBody"></tbody>
            </table>
        </div>
    </div>

    <div id="userListSection" class="card-custom p-3 mb-4" style="display:none;">
        <div class="d-flex justify-content-between align-items-center border-bottom border-warning pb-2">
            <h5 class="text-warning mb-0"><i class="fa-solid fa-users"></i> রেজিস্টার্ড ইউজার তালিকা</h5>
            <button class="btn btn-sm btn-outline-warning" onclick="showHome()">বন্ধ করুন</button>
        </div>
        <div class="table-responsive mt-2">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr><th>নাম</th><th>ইউজারনেম</th><th>মোবাইল</th><th>রোল</th><th>স্ট্যাটাস</th></tr>
                </thead>
                <tbody id="userTableBody"></tbody>
            </table>
        </div>
    </div>

    {% else %}
    <div class="row justify-content-center mt-4">
        <div class="col-md-5">
            <div class="card-custom p-4 text-center">
                <h4 class="text-warning mb-3">লগইন করুন</h4>
                <form action="/login" method="POST">
                    <div class="mb-3 text-start"><label class="form-label">ইউজারনেম / মোবাইল</label><input type="text" name="username" class="form-control" required></div>
                    <div class="mb-3 text-start"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
                    <button type="submit" class="btn btn-gold w-100 py-2">প্রবেশ করুন</button>
                </form>
            </div>
        </div>
    </div>
    {% endif %}
</div>

<div class="modal fade" id="messengerModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-comments"></i> মেসেঞ্জার চ্যাট</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="row">
            <div class="col-md-4 border-end border-warning">
                <div class="d-flex gap-1 mb-2">
                    <button class="btn btn-sm btn-gold w-50" onclick="switchChatTab('users')">ইনবক্স</button>
                    <button class="btn btn-sm btn-pink w-50" onclick="switchChatTab('group')">গ্রুপ চ্যাট</button>
                </div>
                <div id="chatUserList" class="list-group list-group-flush bg-transparent" style="max-height: 350px; overflow-y: auto;">
                    </div>
            </div>
            <div class="col-md-8 d-flex flex-column">
                <div id="activeChatTitle" class="text-warning fw-bold mb-2 pb-1 border-bottom border-warning">চ্যাট নির্বাচন করুন</div>
                <div id="chatMessages" class="chat-box d-flex flex-column mb-2">
                    <p class="text-muted text-center m-auto">মেসেজ দেখতে বা পাঠাতে বামপাশ থেকে ইউজার বা গ্রুপ সিলেক্ট করুন।</p>
                </div>
                <form id="chatForm" onsubmit="sendMessage(event)" class="input-group" style="display:none;">
                    <input type="text" id="chatInput" class="form-control" placeholder="একটি মেসেজ লিখুন..." required>
                    <button type="submit" class="btn btn-gold"><i class="fa-solid fa-paper-plane"></i></button>
                </form>
            </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="notificationModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-bell"></i> নোটিফিকেশনসমূহ</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div id="notificationList" class="list-group list-group-flush bg-transparent">
            <p class="text-muted text-center">কোনো নতুন নোটিফিকেশন নেই।</p>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="recordModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning" id="recordModalTitle">গ্রাহক নম্বর যোগ করুন</h5>
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

<div class="modal fade" id="createUserModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-plus"></i> নতুন ইউজার তৈরি করুন</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/api/create_user" method="POST" class="modal-body">
        <div class="mb-2"><label class="form-label">নাম</label><input type="text" name="name" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">মোবাইল</label><input type="text" name="phone" class="form-control"></div>
        <div class="mb-2"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
        <div class="mb-3">
            <label class="form-label">রোল</label>
            <select name="role" class="form-select">
                <option value="user">সাধারণ ইউজার</option>
                <option value="admin">এডমিন / সাব-এডমিন</option>
            </select>
        </div>
        <button type="submit" class="btn btn-gold w-100 py-2">ইউজার তৈরি করুন</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="adminHistoryModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-clock-rotate-left"></i> এডমিন হিস্ট্রি ও পরিসংখ্যান</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr>
                        <th>এডমিন নাম</th>
                        <th>ইউজারনেম</th>
                        <th>সক্রিয় সময় (মিনিট)</th>
                        <th>ইউজার যোগ করেছেন</th>
                        <th>নম্বর যোগ করেছেন</th>
                    </tr>
                </thead>
                <tbody id="adminHistoryTableBody"></tbody>
            </table>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="profileModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-gear"></i> প্রোফাইল আপডেট</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/update_profile" method="POST" enctype="multipart/form-data" class="modal-body text-start">
        <div class="mb-2"><label class="form-label">আপনার নাম</label><input type="text" name="name" class="form-control" value="{{ session.get('user',{}).get('name') }}" required></div>
        <div class="mb-2"><label class="form-label">মোবাইল নম্বর</label><input type="text" name="phone" class="form-control" value="{{ session.get('user',{}).get('phone') }}"></div>
        <div class="mb-2"><label class="form-label">নতুন পাসওয়ার্ড (ঐচ্ছিক)</label><input type="password" name="password" class="form-control" placeholder="নতুন পাসওয়ার্ড"></div>
        <div class="mb-3"><label class="form-label">ছবি পরিবর্তন</label><input type="file" name="pic" class="form-control" accept="image/*"></div>
        <button type="submit" class="btn btn-gold w-100 py-2">সেভ করুন</button>
      </form>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
let activeServiceFilter = '';
let currentChatTarget = '';
let currentChatIsGroup = 0;
let currentChatTabType = 'users';

function showHome() {
    document.getElementById('recordsSection').style.display = 'block';
    document.getElementById('userListSection').style.display = 'none';
    loadRecords();
}

function filterService(service) {
    activeServiceFilter = service;
    document.getElementById('currentFilterLabel').innerText = service || 'সকল নম্বর';
    loadRecords();
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
                <td><span class="badge bg-info text-dark">${row[7] || 'Khushbu23'}</span></td>
                <td>
                    <button class="btn btn-warning btn-sm me-1" onclick="openEditRecordModal(${row[0]})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="deleteRecord(${row[0]})"><i class="fa-solid fa-trash"></i></button>
                </td>
            </tr>`;
        });
        if(document.getElementById('recordsTableBody')) document.getElementById('recordsTableBody').innerHTML = html;
        if(document.getElementById('countTotal')) document.getElementById('countTotal').innerText = data.counts.total;
        if(document.getElementById('countTel')) document.getElementById('countTel').innerText = data.counts.tel;
        if(document.getElementById('countBoth')) document.getElementById('countBoth').innerText = data.counts.both;
        if(document.getElementById('countWifi')) document.getElementById('countWifi').innerText = data.counts.wifi;
    });
}

function openAddRecordModal() {
    document.getElementById('recordForm').reset();
    document.getElementById('rec_id').value = '';
    document.getElementById('recordModalTitle').innerText = 'নতুন নম্বর যোগ করুন';
    new bootstrap.Modal(document.getElementById('recordModal')).show();
}

function openCreateUserModal() {
    new bootstrap.Modal(document.getElementById('createUserModal')).show();
}

function openCreateAdminModal() {
    openCreateUserModal();
}

function openUserListModal() {
    document.getElementById('recordsSection').style.display = 'none';
    document.getElementById('userListSection').style.display = 'block';
    
    fetch('/api/users_list')
    .then(res => res.json())
    .then(users => {
        let html = '';
        users.forEach(u => {
            html += `<tr>
                <td>${u.name}</td>
                <td>${u.username}</td>
                <td>${u.phone || '-'}</td>
                <td><span class="badge bg-warning text-dark">${u.role}</span></td>
                <td><span class="badge bg-success">${u.status}</span></td>
            </tr>`;
        });
        document.getElementById('userTableBody').innerHTML = html;
    });
}

function openAdminHistoryModal() {
    new bootstrap.Modal(document.getElementById('adminHistoryModal')).show();
    fetch('/api/admin_history')
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.forEach(h => {
            html += `<tr>
                <td><strong>${h.name}</strong></td>
                <td>${h.username}</td>
                <td><span class="text-warning">${h.active_minutes} মিনিট</span></td>
                <td><span class="badge bg-primary">${h.users_added} জন</span></td>
                <td><span class="badge bg-success">${h.records_added} টি</span></td>
            </tr>`;
        });
        document.getElementById('adminHistoryTableBody').innerHTML = html;
    });
}

// --- MESSENGER & NOTIFICATION SYSTEM ---

function openMessengerModal() {
    new bootstrap.Modal(document.getElementById('messengerModal')).show();
    switchChatTab('users');
}

function switchChatTab(tab) {
    currentChatTabType = tab;
    let listEl = document.getElementById('chatUserList');
    listEl.innerHTML = '<p class="text-muted text-center p-2">লোড হচ্ছে...</p>';
    
    if(tab === 'users') {
        fetch('/api/chat/users')
        .then(res => res.json())
        .then(data => {
            let html = '';
            if(data.length === 0) {
                html = '<p class="text-muted text-center">কোনো ইউজার নেই।</p>';
            } else {
                data.forEach(u => {
                    let badgeHtml = u.unread > 0 ? `<span class="badge bg-danger rounded-pill">${u.unread}</span>` : '';
                    let subTextClass = u.replied ? 'text-muted small' : 'fw-bold text-warning small';
                    html += `<a href="#" class="list-group-item list-group-item-action bg-dark text-white border-warning mb-1 rounded d-flex justify-content-between align-items-center" onclick="selectChatUser('${u.username}', '${u.name}', 0)">
                        <div>
                            <div><strong>${u.name}</strong></div>
                            <div class="${subTextClass}">${u.last_msg || 'চ্যাট শুরু করুন'}</div>
                        </div>
                        ${badgeHtml}
                    </a>`;
                });
            }
            listEl.innerHTML = html;
        });
    } else {
        // Group chat
        listEl.innerHTML = `<a href="#" class="list-group-item list-group-item-action bg-dark text-white border-warning mb-1 rounded d-flex justify-content-between align-items-center" onclick="selectChatUser('BTCL_Group', 'অফিসিয়াল গ্রুপ চ্যাট', 1)">
            <div>
                <div><strong><i class="fa-solid fa-users"></i> অফিসিয়াল গ্রুপ চ্যাট</strong></div>
                <div class="text-muted small">গ্রুপ মেসেজিং</div>
            </div>
        </a>`;
    }
}

function selectChatUser(target, name, isGroup) {
    currentChatTarget = target;
    currentChatIsGroup = isGroup;
    document.getElementById('activeChatTitle').innerText = name;
    document.getElementById('chatForm').style.display = 'flex';
    loadMessages();
}

function loadMessages() {
    if(!currentChatTarget) return;
    fetch(`/api/chat/messages?target=${encodeURIComponent(currentChatTarget)}&is_group=${currentChatIsGroup}`)
    .then(res => res.json())
    .then(data => {
        let html = '';
        if(data.length === 0) {
            html = '<p class="text-muted text-center m-auto">কোনো মেসেজ নেই। প্রথম মেসেজ পাঠান!</p>';
        } else {
            data.forEach(m => {
                let bubbleClass = m.is_mine ? 'msg-outgoing' : 'msg-incoming';
                let senderName = !m.is_mine && currentChatIsGroup ? `<div class="small text-warning fw-bold mb-1">${m.sender}</div>` : '';
                html += `<div class="message-bubble ${bubbleClass}">
                    ${senderName}
                    <div>${m.message}</div>
                    <div style="font-size: 9px; opacity: 0.7; text-align: right;">${m.timestamp}</div>
                </div>`;
            });
        }
        let box = document.getElementById('chatMessages');
        box.innerHTML = html;
        box.scrollTop = box.scrollHeight;
        checkNotifications();
    });
}

function sendMessage(e) {
    e.preventDefault();
    let text = document.getElementById('chatInput').value;
    if(!text.trim()) return;

    let formData = new FormData();
    formData.append('receiver', currentChatTarget);
    formData.append('message', text);
    formData.append('is_group', currentChatIsGroup);

    fetch('/api/chat/send', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(res => {
        if(res.status === 'success') {
            document.getElementById('chatInput').value = '';
            loadMessages();
            if(currentChatTabType === 'users') switchChatTab('users');
        }
    });
}

function openNotificationModal() {
    new bootstrap.Modal(document.getElementById('notificationModal')).show();
    fetch('/api/notifications')
    .then(res => res.json())
    .then(data => {
        let html = '';
        if(data.length === 0) {
            html = '<p class="text-muted text-center">কোনো নতুন নোটিফিকেশন নেই।</p>';
        } else {
            data.forEach(n => {
                html += `<div class="list-group-item bg-dark text-white border-warning mb-1 rounded cursor-pointer" onclick="goToChatFromNotification('${n.sender}', ${n.is_group})">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1 text-warning">${n.sender} ${n.is_group ? '(গ্রুপ)' : ''}</h6>
                        <small>${n.timestamp}</small>
                    </div>
                    <p class="mb-1">${n.message}</p>
                </div>`;
            });
        }
        document.getElementById('notificationList').innerHTML = html;
        checkNotifications();
    });
}

function goToChatFromNotification(sender, isGroup) {
    bootstrap.Modal.getInstance(document.getElementById('notificationModal')).hide();
    openMessengerModal();
    if(isGroup) {
        switchChatTab('group');
        selectChatUser('BTCL_Group', 'অফিসিয়াল গ্রুপ চ্যাট', 1);
    } else {
        switchChatTab('users');
        selectChatUser(sender, sender, 0);
    }
}

function checkNotifications() {
    fetch('/api/notifications/count')
    .then(res => res.json())
    .then(data => {
        let msgBadge = document.getElementById('msgBadge');
        let notifBadge = document.getElementById('notifBadge');
        
        if(msgBadge) {
            if(data.msg_count > 0) {
                msgBadge.innerText = data.msg_count;
                msgBadge.style.display = 'inline-block';
            } else {
                msgBadge.style.display = 'none';
            }
        }
        if(notifBadge) {
            if(data.notif_count > 0) {
                notifBadge.innerText = data.notif_count;
                notifBadge.style.display = 'inline-block';
            } else {
                notifBadge.style.display = 'none';
            }
        }
    });
}

function openEditRecordModal(id) {
    fetch(`/api/get_record?id=${id}`)
    .then(res => res.json())
    .then(data => {
        document.getElementById('rec_id').value = data.id;
        document.getElementById('rec_name').value = data.customer_name;
        document.getElementById('rec_mobile').value = data.mobile;
        document.getElementById('rec_service').value = data.service_type;
        document.getElementById('rec_conn').value = data.connection_num;
        document.getElementById('rec_address').value = data.address;
        document.getElementById('rec_note').value = data.note;
        document.getElementById('recordModalTitle').innerText = 'গ্রাহকের নম্বর সংশোধন করুন';
        new bootstrap.Modal(document.getElementById('recordModal')).show();
    });
}

function saveRecord(e) {
    e.preventDefault();
    let formData = new FormData(document.getElementById('recordForm'));
    fetch('/api/save_record', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(res => {
        bootstrap.Modal.getInstance(document.getElementById('recordModal')).hide();
        loadRecords();
    });
}

function deleteRecord(id) {
    if(confirm('আপনি কি এই গ্রাহক নম্বরটি মুছে ফেলতে চান?')) {
        fetch(`/api/delete_record?id=${id}`)
        .then(() => loadRecords());
    }
}

function openProfileModal() {
    new bootstrap.Modal(document.getElementById('profileModal')).show();
}

if(document.getElementById('searchInput')) {
    loadRecords();
    setInterval(checkNotifications, 10000);
    checkNotifications();
}
</script>
</body>
</html>
"""

# --- BACKEND API ROUTES ---

@app.route('/')
def home():
    if 'user' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE username = ?", (session['user']['username'],))
        conn.commit()
        conn.close()
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
        session['user'] = {
            'id': user[0], 
            'name': user[1], 
            'username': user[2], 
            'phone': user[4],
            'role': user[6],
            'profile_pic': user[8],
            'is_admin_or_sub': True
        }
        return redirect(url_for('home'))
    return "<script>alert('ভুল তথ্য!'); window.location='/';</script>"

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    service = request.args.get('service', '')
    sort = request.args.get('sort', 'id_asc')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    order_sql = "ORDER BY id ASC"
    if sort == 'id_desc': order_sql = "ORDER BY id DESC"
    elif sort == 'name_asc': order_sql = "ORDER BY customer_name ASC"

    query = "SELECT id, customer_name, mobile, service_type, connection_num, address, note, added_by FROM phone_records WHERE is_deleted=0"
    params = []

    if q:
        query += " AND (customer_name LIKE ? OR mobile LIKE ? OR connection_num LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])

    if service:
        query += " AND service_type = ?"
        params.append(service)

    query += f" {order_sql}"
    cursor.execute(query, params)
    records = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type='টেলিফোন নম্বর'")
    tel = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type='টেলিফোন+ওয়াইফাই নম্বর'")
    both = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type='ওয়াইফাই নম্বর'")
    wifi = cursor.fetchone()[0]

    conn.close()
    return jsonify({
        'records': records,
        'counts': {'total': total, 'tel': tel, 'both': both, 'wifi': wifi}
    })

# --- CHAT & NOTIFICATION APIS ---

@app.route('/api/chat/users')
def chat_users():
    if 'user' not in session: return jsonify([])
    current_user = session['user']['username']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, name FROM users WHERE username != ? AND is_deleted=0", (current_user,))
    users = cursor.fetchall()
    
    result = []
    for u in users:
        u_username, u_name = u[0], u[1]
        
        # Unread count
        cursor.execute("SELECT COUNT(*) FROM messages WHERE sender = ? AND receiver = ? AND is_group = 0 AND is_read = 0", (u_username, current_user))
        unread = cursor.fetchone()[0]
        
        # Last message & reply status check
        cursor.execute("SELECT message, sender FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) AND is_group = 0 ORDER BY id DESC LIMIT 1", (u_username, current_user, current_user, u_username))
        last_m = cursor.fetchone()
        
        last_msg_text = last_m[0] if last_m else ''
        replied = last_m and last_m[1] == current_user if last_m else True
        
        result.append({
            'username': u_username,
            'name': u_name,
            'unread': unread,
            'last_msg': last_msg_text,
            'replied': replied
        })
    conn.close()
    return jsonify(result)

@app.route('/api/chat/messages')
def chat_messages():
    if 'user' not in session: return jsonify([])
    current_user = session['user']['username']
    target = request.args.get('target')
    is_group = int(request.args.get('is_group', 0))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if is_group:
        cursor.execute("SELECT sender, message, timestamp FROM messages WHERE is_group = 1 ORDER BY id ASC")
    else:
        cursor.execute("""SELECT sender, message, timestamp FROM messages 
                          WHERE is_group = 0 AND ((sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)) 
                          ORDER BY id ASC""", (current_user, target, target, current_user))
        # Mark as read for this target
        cursor.execute("UPDATE messages SET is_read = 1 WHERE sender = ? AND receiver = ? AND is_group = 0", (target, current_user))
        conn.commit()
        
    rows = cursor.fetchall()
    conn.close()
    
    messages = []
    for r in rows:
        messages.append({
            'sender': r[0],
            'message': r[1],
            'timestamp': r[2],
            'is_mine': r[0] == current_user
        })
    return jsonify(messages)

@app.route('/api/chat/send', methods=['POST'])
def chat_send():
    if 'user' not in session: return jsonify({'status': 'unauthorized'})
    current_user = session['user']['username']
    receiver = request.form.get('receiver')
    message = request.form.get('message')
    is_group = int(request.form.get('is_group', 0))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO messages (sender, receiver, message, is_group, is_read) 
                      VALUES (?, ?, ?, ?, 0)""", (current_user, receiver, message, is_group))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/notifications/count')
def notif_count():
    if 'user' not in session: return jsonify({'msg_count': 0, 'notif_count': 0})
    username = session['user']['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM messages WHERE receiver = ? AND is_read = 0", (username,))
    msg_count = cursor.fetchone()[0]
    
    conn.close()
    return jsonify({'msg_count': msg_count, 'notif_count': msg_count})

@app.route('/api/notifications')
def notifications():
    if 'user' not in session: return jsonify([])
    username = session['user']['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message, timestamp, is_group FROM messages WHERE receiver = ? ORDER BY id DESC LIMIT 20", (username,))
    rows = cursor.fetchall()
    conn.close()

    notifs = [{'sender': r[0], 'message': r[1], 'timestamp': r[2], 'is_group': r[3]} for r in rows]
    return jsonify(notifs)

@app.route('/api/save_record', methods=['POST'])
def save_record():
    rec_id = request.form.get('id')
    name = request.form.get('customer_name')
    mobile = request.form.get('mobile')
    service = request.form.get('service_type')
    conn_num = request.form.get('connection_num')
    address = request.form.get('address')
    note = request.form.get('note')
    current_user = session['user']['username'] if 'user' in session else 'Khushbu23'

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    if rec_id:
        cursor.execute("""UPDATE phone_records 
                          SET customer_name=?, mobile=?, service_type=?, connection_num=?, address=?, note=? 
                          WHERE id=?""", (name, mobile, service, conn_num, address, note, rec_id))
    else:
        cursor.execute("""INSERT INTO phone_records (customer_name, mobile, service_type, connection_num, address, note, added_by) 
                          VALUES (?, ?, ?, ?, ?, ?, ?)""", (name, mobile, service, conn_num, address, note, current_user))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/create_user', methods=['POST'])
def create_user():
    if 'user' not in session: return redirect(url_for('home'))
    name = request.form.get('name')
    username = request.form.get('username')
    phone = request.form.get('phone')
    password = generate_password_hash(request.form.get('password'))
    role = request.form.get('role', 'user')
    current_user = session['user']['username']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO users (name, username, phone, password, role, added_by, status) 
                          VALUES (?, ?, ?, ?, ?, ?, 'active')""", 
                       (name, username, phone, password, role, current_user))
        conn.commit()
    except:
        pass
    conn.close()
    return "<script>alert('ইউজার সফলভাবে তৈরি করা হয়েছে!'); window.location='/';</script>"

@app.route('/api/users_list')
def users_list():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, phone, role, status FROM users WHERE is_deleted=0")
    rows = cursor.fetchall()
    conn.close()
    users = [{'name': r[0], 'username': r[1], 'phone': r[2], 'role': r[3], 'status': r[4]} for r in rows]
    return jsonify(users)

@app.route('/api/admin_history')
def admin_history():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, role, last_active FROM users WHERE is_deleted=0 AND (role IN ('admin', 'main_admin') OR username=?)", (MAIN_ADMIN_USERNAME,))
    admins = cursor.fetchall()
    
    history = []
    for adm in admins:
        adm_name, adm_username, role, last_active = adm[0], adm[1], adm[2], adm[3]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE added_by=?", (adm_username,))
        users_added = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM phone_records WHERE added_by=?", (adm_username,))
        records_added = cursor.fetchone()[0]
        
        active_mins = 10
        if last_active:
            try:
                dt = datetime.strptime(last_active, "%Y-%m-%d %H:%M:%S")
                diff = datetime.now() - dt
                active_mins = max(1, int(diff.total_seconds() / 60))
            except:
                active_mins = 10

        history.append({
            'name': adm_name,
            'username': adm_username,
            'active_minutes': active_mins,
            'users_added': users_added,
            'records_added': records_added
        })
        
    conn.close()
    return jsonify(history)

@app.route('/api/get_record')
def get_record():
    rec_id = request.args.get('id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, mobile, service_type, connection_num, address, note FROM phone_records WHERE id=?", (rec_id,))
    row = cursor.fetchone()
    conn.close()
    return jsonify({'id': row[0], 'customer_name': row[1], 'mobile': row[2], 'service_type': row[3], 'connection_num': row[4], 'address': row[5], 'note': row[6]})

@app.route('/api/delete_record')
def delete_record():
    rec_id = request.args.get('id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE phone_records SET is_deleted=1 WHERE id=?", (rec_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session: return redirect(url_for('home'))
    user_id = session['user']['id']
    name = request.form.get('name')
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET name=?, phone=? WHERE id=?", (name, phone, user_id))
    session['user']['name'] = name
    session['user']['phone'] = phone

    if password and password.strip() != "":
        hashed_pw = generate_password_hash(password)
        cursor.execute("UPDATE users SET password=? WHERE id=?", (hashed_pw, user_id))

    if 'pic' in request.files:
        file = request.files['pic']
        if file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session['user']['username']}_{filename}")
            file.save(filepath)
            cursor.execute("UPDATE users SET profile_pic=? WHERE id=?", ('/' + filepath, user_id))
            session['user']['profile_pic'] = '/' + filepath

    conn.commit()
    conn.close()
    return "<script>alert('প্রোফাইল তথ্য সেভ হয়েছে!'); window.location='/';</script>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)