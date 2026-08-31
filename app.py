import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_btcl_kurigram_gold_pink_2026")

ADMIN_USERNAME = "Khushbu23"
ADMIN_SECURITY_CODE = "137955"

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            username TEXT UNIQUE,
            email TEXT,
            phone TEXT,
            password TEXT,
            status TEXT DEFAULT 'pending',
            is_deleted INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Phone Records Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS phone_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            mobile TEXT,
            service_type TEXT,
            connection_num TEXT,
            address TEXT,
            note TEXT,
            is_deleted INTEGER DEFAULT 0
        )
    ''')
    
    # Messages Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            file_url TEXT,
            is_group INTEGER DEFAULT 0,
            is_deleted_by_sender INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            reference_id INTEGER,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Admin Creation
    cursor.execute("SELECT * FROM users WHERE username = ?", (ADMIN_USERNAME,))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("01751947523")
        cursor.execute("INSERT INTO users (name, username, email, phone, password, status) VALUES (?, ?, ?, ?, ?, ?)",
                       ('Md Khushbu Alom', ADMIN_USERNAME, 'admin@btcl.com', '01751947523', hashed_pw, 'active'))

    conn.commit()
    conn.close()

init_db()

# --- Single File HTML/CSS/JS Template (Golden Pink Theme) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম - Md Khushbu Alom</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { 
            background: linear-gradient(135deg, #2b001e 0%, #4a1525 50%, #1f0010 100%); 
            color: #ffe6f2; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .gold-pink-header {
            background: linear-gradient(90deg, #d4af37 0%, #ff66b2 50%, #d4af37 100%);
            color: #1a000d;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4);
        }
        .card-custom {
            background: rgba(45, 10, 30, 0.85);
            border: 1px solid #d4af37;
            border-radius: 12px;
            box-shadow: 0 4px 10px rgba(255, 102, 178, 0.2);
        }
        .form-label { color: #ffd700; font-weight: bold; }
        .form-control, .form-select { 
            background-color: #1a0512; 
            color: #fff; 
            border: 1px solid #ff66b2; 
        }
        .form-control:focus, .form-select:focus { 
            background-color: #2b001e; 
            color: #fff; 
            border-color: #d4af37; 
            box-shadow: 0 0 8px rgba(212, 175, 55, 0.6); 
        }
        .btn-gold {
            background: linear-gradient(45deg, #d4af37, #f3e5ab);
            color: #000;
            font-weight: bold;
            border: none;
        }
        .btn-gold:hover { background: linear-gradient(45deg, #f3e5ab, #d4af37); color: #000; }
        .btn-pink {
            background: linear-gradient(45deg, #ff66b2, #ff1493);
            color: #fff;
            font-weight: bold;
            border: none;
        }
        .btn-pink:hover { background: linear-gradient(45deg, #ff1493, #ff66b2); color: #fff; }
        .stat-card {
            background: rgba(212, 175, 55, 0.15);
            border: 1px solid #d4af37;
            text-align: center;
            cursor: pointer;
            padding: 10px;
            border-radius: 10px;
            transition: 0.3s;
        }
        .stat-card:hover { background: rgba(255, 102, 178, 0.3); transform: translateY(-2px); }
        .stat-number { font-size: 22px; font-weight: bold; color: #ffd700; }
        .stat-label { font-size: 11px; color: #ffccf2; }
        .offcanvas { background-color: #1f0012; color: #ffe6f2; border-right: 2px solid #d4af37; }
        .nav-link-custom { color: #ffd700; padding: 12px 15px; border-bottom: 1px solid #4a1525; display: block; text-decoration: none; }
        .nav-link-custom:hover { background-color: #ff66b2; color: #fff; }
        .chat-bubble-me { background: #ff66b2; color: #fff; border-radius: 12px 12px 0 12px; margin-left: auto; max-width: 75%; }
        .chat-bubble-them { background: #d4af37; color: #000; border-radius: 12px 12px 12px 0; margin-right: auto; max-width: 75%; }
    </style>
</head>
<body>

<div class="gold-pink-header text-center py-2">
    <h3 class="m-0"><i class="fa-solid fa-phone-volume"></i> BTCL, কুড়িগ্রাম</h3>
    <small>Md Khushbu Alom</small>
</div>

<div class="container py-3">
    {% if session.get('user') %}
    <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center gap-2">
            <button class="btn btn-gold btn-sm" data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu">
                <i class="fa-solid fa-bars"></i> মেনু
            </button>
            <a href="/" class="btn btn-pink btn-sm"><i class="fa-solid fa-house"></i> হোম</a>
        </div>
        
        <div class="d-flex align-items-center gap-2">
            <div class="dropdown">
                <button class="btn btn-outline-warning btn-sm position-relative" id="notifBtn" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-bell"></i>
                    <span id="notifBadge" class="badge bg-danger rounded-pill position-absolute top-0 start-100 translate-middle" style="display:none;">0</span>
                </button>
                <ul class="dropdown-menu dropdown-menu-end dropdown-menu-dark p-2" id="notifList" style="width: 280px; max-height: 300px; overflow-y: auto;">
                    <li><small class="text-muted p-2">কোনো নতুন নোটিফিকেশন নেই</small></li>
                </ul>
            </div>

            {% if session['user']['is_admin'] %}
                <span class="badge btn-gold p-2">ADMIN</span>
            {% else %}
                <span class="badge btn-pink p-2">{{ session['user']['name'] }}</span>
            {% endif %}
            <a href="/logout" class="btn btn-danger btn-sm"><i class="fa-solid fa-power-off"></i></a>
        </div>
    </div>

    <div id="groupBroadcast" class="card-custom p-2 mb-3 border-warning" style="display:none;">
        <span class="badge bg-warning text-dark"><i class="fa-solid fa-bullhorn"></i> এডমিন নোটিশ</span>
        <p id="broadcastMsg" class="m-0 mt-1 small text-white"></p>
    </div>

    <div class="row g-2 mb-3">
        <div class="col-md-8">
            <label class="form-label">খুঁজুন (Search)</label>
            <input type="text" id="searchInput" class="form-control" placeholder="নাম, নম্বর, ঠিকানা বা নোট দিয়ে খুঁজুন..." onkeyup="loadRecords()">
        </div>
        <div class="col-md-4">
            <label class="form-label">সিরিয়াল সর্টিং</label>
            <select id="sortSelect" class="form-select" onchange="loadRecords()">
                <option value="default">ডিফল্ট ক্রমানুসারে</option>
                <option value="name_asc">নামের আদ্যক্ষর (A to Z)</option>
                <option value="name_desc">নামের আদ্যক্ষর (Z to A)</option>
                <option value="num_asc">নম্বর (১ - ১০০)</option>
                <option value="num_desc">নম্বর (১০০ - ১)</option>
            </select>
        </div>
    </div>

    <div class="row g-2 mb-3">
        <div class="col" onclick="filterService('')">
            <div class="stat-card"><div class="stat-number" id="countTotal">0</div><div class="stat-label">টোটাল বিল/নম্বর</div></div>
        </div>
        <div class="col" onclick="filterService('টেলিফোন নম্বর')">
            <div class="stat-card"><div class="stat-number" id="countTel">0</div><div class="stat-label">টেলিফোন</div></div>
        </div>
        <div class="col" onclick="filterService('টেলিফোন+ওয়াইফাই নম্বর')">
            <div class="stat-card"><div class="stat-number" id="countBoth">0</div><div class="stat-label">টেলিফোন+ওয়াইফাই</div></div>
        </div>
        <div class="col" onclick="filterService('ওয়াইফাই নম্বর')">
            <div class="stat-card"><div class="stat-number" id="countWifi">0</div><div class="stat-label">ওয়াইফাই</div></div>
        </div>
        {% if session['user']['is_admin'] %}
        <div class="col" onclick="showSection('users')">
            <div class="stat-card"><div class="stat-number" id="countUsers">0</div><div class="stat-label">টোটাল ইউজার</div></div>
        </div>
        {% endif %}
    </div>

    <div id="recordsSection" class="card-custom p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center border-bottom border-warning pb-2">
            <h5 class="m-0 text-warning"><i class="fa-solid fa-list"></i> গ্রাহক ও সংযোগ তালিকা</h5>
            <button class="btn btn-gold btn-sm" onclick="toggleAddForm()"><i class="fa-solid fa-plus"></i> নতুন এড</button>
        </div>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle mt-2">
                <thead>
                    <tr>
                        <th>সিরিয়াল</th><th>নাম</th><th>মোবাইল</th><th>সেবার ধরন</th><th>সংযোগ নং</th><th>ঠিকানা</th><th>নোট</th>
                        {% if session['user']['is_admin'] %}<th>অ্যাকশন</th>{% endif %}
                    </tr>
                </thead>
                <tbody id="recordsTableBody"></tbody>
            </table>
        </div>
    </div>

    <div id="addRecordSection" class="card-custom p-3 mb-4" style="display:none;">
        <h5 class="text-warning border-bottom border-warning pb-2">নতুন নম্বর এড করুন</h5>
        <form action="/add_record" method="POST" class="row g-3">
            <div class="col-md-6">
                <label class="form-label">গ্রাহকের নাম (বাধ্যতামূলক) *</label>
                <input type="text" name="customer_name" class="form-control" required placeholder="নাম লিখুন">
            </div>
            <div class="col-md-6">
                <label class="form-label">মোবাইল নম্বর (ঐচ্ছিক)</label>
                <input type="text" name="mobile" class="form-control" placeholder="মোবাইল নম্বর">
            </div>
            <div class="col-md-6">
                <label class="form-label">সেবার ধরন সিলেক্ট করুন *</label>
                <select name="service_type" class="form-select" required>
                    <option value="টেলিফোন নম্বর">টেলিফোন নম্বর</option>
                    <option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই নম্বর</option>
                    <option value="ওয়াইফাই নম্বর">ওয়াইফাই নম্বর</option>
                </select>
            </div>
            <div class="col-md-6">
                <label class="form-label">সংযোগ নম্বর (ঐচ্ছিক)</label>
                <input type="text" name="connection_num" class="form-control" placeholder="সংযোগ নম্বর">
            </div>
            <div class="col-md-6">
                <label class="form-label">ঠিকানা (ঐচ্ছিক)</label>
                <input type="text" name="address" class="form-control" placeholder="ঠিকানা">
            </div>
            <div class="col-md-6">
                <label class="form-label">অতিরিক্ত নোট (ঐচ্ছিক)</label>
                <input type="text" name="note" class="form-control" placeholder="নোট">
            </div>
            <div class="col-12">
                <button type="submit" class="btn btn-gold w-100 py-2">সংরক্ষণ করুন</button>
            </div>
        </form>
    </div>

    {% if session['user']['is_admin'] %}
    <div id="usersSection" class="card-custom p-3 mb-4" style="display:none;">
        <h5 class="text-warning border-bottom border-warning pb-2">নিবন্ধিত ইউজার তালিকা</h5>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr><th>নাম</th><th>ইউজারনেম</th><th>ইমেইল</th><th>ফোন</th><th>স্ট্যাটাস</th><th>অ্যাকশন</th></tr>
                </thead>
                <tbody id="usersTableBody"></tbody>
            </table>
        </div>
    </div>
    
    <div id="deletedRecordsSection" class="card-custom p-3 mb-4" style="display:none;">
        <h5 class="text-danger border-bottom border-danger pb-2">ডিলিট হওয়া নম্বর তালিকা</h5>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead><tr><th>নাম</th><th>মোবাইল</th><th>সেবা</th><th>মুছে ফেলার পিন</th></tr></thead>
                <tbody id="deletedTableBody"></tbody>
            </table>
        </div>
    </div>
    {% endif %}

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
                            <div class="mb-3">
                                <label class="form-label">ইউজারনেম / মোবাইল</label>
                                <input type="text" name="username" class="form-control" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">পাসওয়ার্ড</label>
                                <input type="password" name="password" class="form-control" required>
                            </div>
                            <button type="submit" class="btn btn-gold w-100 py-2">লগইন করুন</button>
                        </form>
                    </div>
                    <div class="tab-pane fade" id="regTab">
                        <form action="/register" method="POST">
                            <div class="mb-2"><label class="form-label">আপনার নাম</label><input type="text" name="name" class="form-control" required></div>
                            <div class="mb-2"><label class="form-label">জিমেইল আইডি</label><input type="email" name="email" class="form-control" required></div>
                            <div class="mb-2"><label class="form-label">মোবাইল নম্বর</label><input type="text" name="phone" class="form-control" required></div>
                            <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" required></div>
                            <div class="mb-2"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
                            <div class="mb-3"><label class="form-label">কনফার্ম পাসওয়ার্ড</label><input type="password" name="confirm_password" class="form-control" required></div>
                            <button type="submit" class="btn btn-pink w-100 py-2">রেজিস্ট্রেশন করুন</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>

<div class="offcanvas offcanvas-start" id="sidebarMenu">
  <div class="offcanvas-header border-bottom border-warning">
    <h5 class="offcanvas-title text-warning">প্রধান মেনু</h5>
    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="offcanvas"></button>
  </div>
  <div class="offcanvas-body p-0">
    <a href="#" class="nav-link-custom" onclick="showSection('records')">১. ওভারভিউ ও ডাটা</a>
    <a href="#" class="nav-link-custom" onclick="showNotifHistory()">২. নোটিফিকেশন হিস্টরি</a>
    <a href="#" class="nav-link-custom" onclick="toggleAddForm()">৩. নম্বর এড করুন</a>
    {% if session.get('user', {}).get('is_admin') %}
    <a href="#" class="nav-link-custom" onclick="openCreateUserModal()">৪. নতুন ইউজার তৈরি করুন</a>
    <a href="#" class="nav-link-custom" onclick="showSection('users')">৫. নিবন্ধিত ইউজার তথ্য</a>
    <a href="#" class="nav-link-custom" onclick="openAdminSecurityModal()">৬. সিকিউরিটি ও পাসওয়ার্ড পরিবর্তন</a>
    <a href="#" class="nav-link-custom" onclick="showSection('deleted')">৭. ডিলিট হওয়া নম্বর</a>
    <a href="#" class="nav-link-custom" onclick="showSection('users')">৮. ডিলিট হওয়া ইউজার</a>
    {% endif %}
    <a href="#" class="nav-link-custom" onclick="openMessenger()">৯. মেসেঞ্জার</a>
  </div>
</div>

<div class="modal fade" id="createUserModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <form action="/admin/create_user" method="POST">
        <div class="modal-header border-warning"><h5 class="modal-title text-warning">নতুন ইউজার তৈরি করুন</h5></div>
        <div class="modal-body row g-2">
            <div class="col-12"><label class="form-label">ইউজারের নাম</label><input type="text" name="name" class="form-control" required></div>
            <div class="col-12"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" required></div>
            <div class="col-12"><label class="form-label">মোবাইল</label><input type="text" name="phone" class="form-control" required></div>
            <div class="col-12"><label class="form-label">ইমেইল</label><input type="email" name="email" class="form-control" required></div>
            <div class="col-12"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
        </div>
        <div class="modal-footer border-warning"><button type="submit" class="btn btn-gold">ইউজার তৈরি করুন</button></div>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="adminSecModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <form action="/admin/change_password" method="POST">
        <div class="modal-header border-warning"><h5 class="modal-title text-warning">এডমিন পাসওয়ার্ড পরিবর্তন</h5></div>
        <div class="modal-body">
            <label class="form-label">নতুন ইউজারনেম</label>
            <input type="text" name="new_username" class="form-control mb-2" value="Khushbu23" required>
            <label class="form-label">নতুন পাসওয়ার্ড</label>
            <input type="password" name="new_password" class="form-control mb-2" required>
            <label class="form-label">সিকিউরিটি পিন (137955)</label>
            <input type="password" name="security_code" class="form-control" required placeholder="পিন দিন">
        </div>
        <div class="modal-footer border-warning"><button type="submit" class="btn btn-gold">পরিবর্তন সংরক্ষণ করুন</button></div>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="messengerModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-comments"></i> মেসেঞ্জার</h5>
        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body row g-0">
        <div class="col-md-4 border-end border-warning pe-2" id="chatUserList">
            <small class="text-warning">চ্যাট শুরু করতে সিলেক্ট করুন:</small>
            <div class="list-group list-group-flush mt-2" id="usersChatNav"></div>
        </div>
        <div class="col-md-8 ps-2 d-flex flex-column" style="min-height: 350px;">
            <div id="activeChatHeader" class="fw-bold text-pink pb-2 border-bottom border-secondary">গ্রুপ মেসেঞ্জার (ব্রডকাস্ট)</div>
            <div id="chatMessagesBox" class="flex-grow-1 p-2 my-2 border border-secondary rounded overflow-auto" style="height:250px;"></div>
            <div class="input-group">
                <input type="text" id="chatInputMsg" class="form-control" placeholder="মেসেজ লিখুন...">
                <button class="btn btn-gold" onclick="sendChatMsg()"><i class="fa-solid fa-paper-plane"></i></button>
            </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="deleteModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <form id="deleteForm" method="POST">
          <div class="modal-header border-danger"><h5 class="modal-title text-danger">ডিলিট কনফার্মেশন</h5></div>
          <div class="modal-body">
            <label class="form-label">এডমিন সিকিউরিটি পিন দিন (137955):</label>
            <input type="password" name="security_code" class="form-control" required placeholder="সিকিউরিটি পিন">
          </div>
          <div class="modal-footer border-danger"><button type="submit" class="btn btn-danger">ডিলিট নিশ্চিত করুন</button></div>
      </form>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
let activeServiceFilter = '';
let currentChatTarget = 'GROUP';

function loadRecords() {
    let q = document.getElementById('searchInput') ? document.getElementById('searchInput').value : '';
    let sort = document.getElementById('sortSelect') ? document.getElementById('sortSelect').value : 'default';
    
    fetch(`/api/search?q=${q}&service=${activeServiceFilter}&sort=${sort}`)
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.records.forEach((row, idx) => {
            html += `<tr>
                <td>${idx + 1}</td>
                <td>${row[1]}</td>
                <td>${row[2] || '-'}</td>
                <td><span class="badge bg-warning text-dark">${row[3]}</span></td>
                <td>${row[4] || '-'}</td>
                <td>${row[5] || '-'}</td>
                <td>${row[6] || '-'}</td>
                {% if session.get('user', {}).get('is_admin') %}
                <td>
                    <button class="btn btn-danger btn-sm" onclick="openDeleteModal(${row[0]})"><i class="fa-solid fa-trash"></i></button>
                </td>
                {% endif %}
            </tr>`;
        });
        if(document.getElementById('recordsTableBody')) document.getElementById('recordsTableBody').innerHTML = html;
        if(document.getElementById('countTotal')) document.getElementById('countTotal').innerText = data.counts.total;
        if(document.getElementById('countTel')) document.getElementById('countTel').innerText = data.counts.tel;
        if(document.getElementById('countBoth')) document.getElementById('countBoth').innerText = data.counts.both;
        if(document.getElementById('countWifi')) document.getElementById('countWifi').innerText = data.counts.wifi;
        if(document.getElementById('countUsers')) document.getElementById('countUsers').innerText = data.counts.users;
    });
}

function filterService(type) {
    activeServiceFilter = type;
    showSection('records');
    loadRecords();
}

function toggleAddForm() {
    let form = document.getElementById('addRecordSection');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
    if(form.style.display === 'block') form.scrollIntoView({ behavior: 'smooth' });
}

function showSection(type) {
    document.getElementById('recordsSection').style.display = type === 'records' ? 'block' : 'none';
    if(document.getElementById('usersSection')) document.getElementById('usersSection').style.display = type === 'users' ? 'block' : 'none';
    if(document.getElementById('deletedRecordsSection')) document.getElementById('deletedRecordsSection').style.display = type === 'deleted' ? 'block' : 'none';
    
    if(type === 'users') loadUsers();
    if(type === 'deleted') loadDeleted();
    
    let offcanvas = bootstrap.Offcanvas.getInstance(document.getElementById('sidebarMenu'));
    if(offcanvas) offcanvas.hide();
}

function loadUsers() {
    fetch('/api/users')
    .then(res => res.json())
    .then(users => {
        let html = '';
        users.forEach(u => {
            html += `<tr>
                <td>${u[1]}</td><td>${u[2]}</td><td>${u[3]}</td><td>${u[4]}</td>
                <td><span class="badge ${u[6]=='active'?'bg-success':'bg-danger'}">${u[6]}</span></td>
                <td>
                    <button class="btn btn-success btn-sm me-1" onclick="userAction(${u[0]}, 'approve')">Approve</button>
                    <button class="btn btn-warning btn-sm" onclick="userAction(${u[0]}, 'block')">Block</button>
                </td>
            </tr>`;
        });
        document.getElementById('usersTableBody').innerHTML = html;
    });
}

function userAction(id, action) {
    let code = '';
    if(action === 'block' || action === 'delete') {
        code = prompt("এডমিন সিকিউরিটি পিন দিন (137955):");
        if(!code) return;
    }
    let formData = new FormData();
    formData.append('security_code', code);
    fetch(`/admin/user_action/${id}/${action}`, { method: 'POST', body: formData })
    .then(() => loadUsers());
}

function openMessenger() {
    new bootstrap.Modal(document.getElementById('messengerModal')).show();
    loadChatUsers();
    loadMessages();
}

function loadChatUsers() {
    fetch('/api/users')
    .then(res => res.json())
    .then(users => {
        let html = `<a href="#" class="list-group-item list-group-item-action bg-dark text-warning border-secondary active" onclick="selectChatTarget('GROUP', 'গ্রুপ মেসেঞ্জার (এডমিন ব্রডকাস্ট)')">📢 গ্রুপ মেসেঞ্জার</a>`;
        users.forEach(u => {
            html += `<a href="#" class="list-group-item list-group-item-action bg-dark text-white border-secondary" onclick="selectChatTarget('${u[2]}', '${u[1]}')">👤 ${u[1]}</a>`;
        });
        document.getElementById('usersChatNav').innerHTML = html;
    });
}

function selectChatTarget(target, name) {
    currentChatTarget = target;
    document.getElementById('activeChatHeader').innerText = name;
    loadMessages();
}

function loadMessages() {
    fetch(`/api/messages?target=${currentChatTarget}`)
    .then(res => res.json())
    .then(msgs => {
        let html = '';
        msgs.forEach(m => {
            let isMe = m.sender === "{{ session.get('user', {}).get('username') }}";
            html += `<div class="d-flex mb-2 ${isMe?'justify-content-end':'justify-content-start'}">
                <div class="${isMe?'chat-bubble-me':'chat-bubble-them'} p-2" oncontextmenu="deleteMsg(event, ${m.id})">
                    <small class="d-block fw-bold">${m.sender_name}</small>
                    ${m.message}
                </div>
            </div>`;
        });
        document.getElementById('chatMessagesBox').innerHTML = html;
    });
}

function sendChatMsg() {
    let msg = document.getElementById('chatInputMsg').value;
    if(!msg) return;
    let formData = new FormData();
    formData.append('message', msg);
    formData.append('target', currentChatTarget);
    fetch('/send_message', { method: 'POST', body: formData })
    .then(() => {
        document.getElementById('chatInputMsg').value = '';
        loadMessages();
    });
}

function checkNotifications() {
    fetch('/api/notifications')
    .then(res => res.json())
    .then(notifs => {
        let badge = document.getElementById('notifBadge');
        let list = document.getElementById('notifList');
        if(notifs.length > 0) {
            badge.style.display = 'inline';
            badge.innerText = notifs.length;
            let html = '';
            notifs.forEach(n => {
                html += `<li><a class="dropdown-item text-wrap border-bottom border-secondary" href="#" onclick="readNotif(${n.id})">${n.message}</a></li>`;
            });
            list.innerHTML = html;
        } else {
            badge.style.display = 'none';
            list.innerHTML = '<li><small class="text-muted p-2">কোনো নতুন নোটিফিকেশন নেই</small></li>';
        }
    });
}

function readNotif(id) {
    fetch('/api/read_notif/' + id).then(() => { checkNotifications(); openMessenger(); });
}

function openCreateUserModal() { new bootstrap.Modal(document.getElementById('createUserModal')).show(); }
function openAdminSecurityModal() { new bootstrap.Modal(document.getElementById('adminSecModal')).show(); }
function openDeleteModal(id) {
    document.getElementById('deleteForm').action = '/delete_record/' + id;
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}

if(document.getElementById('searchInput')) {
    loadRecords();
    setInterval(checkNotifications, 3000);
}
</script>
</body>
</html>
"""

# --- Routes ---
@app.route('/')
def home():
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
        if user[6] == 'pending':
            return "<script>alert('আপনার একাউন্টটি এখনও এডমিন অনুমোদন করেনি!'); window.location='/';</script>"
        elif user[6] == 'blocked':
            return "<script>alert('আপনার একাউন্টটি ব্লক করা হয়েছে!'); window.location='/';</script>"
        
        session['user'] = {'id': user[0], 'name': user[1], 'username': user[2], 'is_admin': (user[2] == ADMIN_USERNAME)}
        return redirect(url_for('home'))
    return "<script>alert('ভুল ইউজারনেম অথবা পাসওয়ার্ড!'); window.location='/';</script>"

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    username = request.form['username']
    password = request.form['password']
    
    if password != request.form['confirm_password']:
        return "<script>alert('পাসওয়ার্ড দুটি মেলেনি!'); window.location='/';</script>"

    hashed_pw = generate_password_hash(password)
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, username, email, phone, password) VALUES (?, ?, ?, ?, ?)",
                       (name, username, email, phone, hashed_pw))
        cursor.execute("INSERT INTO notifications (type, message) VALUES ('user_reg', ?)",
                       (f"নতুন রেজিস্ট্রেশন: {name} ({username}) অনুমোদন চান।",))
        conn.commit()
        conn.close()
        return "<script>alert('রেজিস্ট্রেশন সফল হয়েছে! এডমিন পারমিশন দিলে প্রবেশ করতে পারবেন।'); window.location='/';</script>"
    except:
        return "<script>alert('ইউজারনেম বা তথ্য আগে থেকেই ব্যবহৃত হচ্ছে!'); window.location='/';</script>"

@app.route('/admin/create_user', methods=['POST'])
def admin_create_user():
    if not session.get('user', {}).get('is_admin'): return redirect(url_for('home'))
    hashed_pw = generate_password_hash(request.form['password'])
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, username, email, phone, password, status) VALUES (?, ?, ?, ?, ?, 'active')",
                   (request.form['name'], request.form['username'], request.form['email'], request.form['phone'], hashed_pw))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/admin/change_password', methods=['POST'])
def admin_change_password():
    if not session.get('user', {}).get('is_admin'): return redirect(url_for('home'))
    if request.form.get('security_code') != ADMIN_SECURITY_CODE:
        return "<script>alert('সিকিউরিটি পিন ভুল!'); window.location='/';</script>"
    
    new_user = request.form['new_username']
    hashed_pw = generate_password_hash(request.form['new_password'])
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username=?, password=? WHERE id=?", (new_user, hashed_pw, session['user']['id']))
    conn.commit()
    conn.close()
    return redirect(url_for('logout'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/add_record', methods=['POST'])
def add_record():
    if 'user' not in session: return redirect(url_for('home'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO phone_records (customer_name, mobile, service_type, connection_num, address, note) 
                      VALUES (?, ?, ?, ?, ?, ?)''', 
                   (request.form['customer_name'], request.form.get('mobile', ''), request.form['service_type'],
                    request.form.get('connection_num', ''), request.form.get('address', ''), request.form.get('note', '')))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/delete_record/<int:id>', methods=['POST'])
def delete_record(id):
    if request.form.get('security_code') != ADMIN_SECURITY_CODE:
        return "<script>alert('সিকিউরিটি কোড ভুল!'); window.location='/';</script>"
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE phone_records SET is_deleted=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    service = request.args.get('service', '')
    sort = request.args.get('sort', 'default')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    order_by = "id DESC"
    if sort == 'num_asc': order_by = "mobile ASC"
    elif sort == 'num_desc': order_by = "mobile DESC"
    elif sort == 'name_asc': order_by = "customer_name ASC"
    elif sort == 'name_desc': order_by = "customer_name DESC"

    query = "SELECT * FROM phone_records WHERE is_deleted=0 AND (customer_name LIKE ? OR mobile LIKE ? OR connection_num LIKE ? OR address LIKE ? OR note LIKE ?)"
    params = [f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%']

    if service:
        query += " AND service_type LIKE ?"
        params.append(f'%{service}%')

    query += f" ORDER BY {order_by}"
    cursor.execute(query, params)
    records = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type LIKE '%টেলিফোন নম্বর%'")
    tel = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type LIKE '%টেলিফোন+ওয়াইফাই নম্বর%'")
    both = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type LIKE '%ওয়াইফাই নম্বর%'")
    wifi = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_deleted=0")
    users = cursor.fetchone()[0]

    conn.close()
    return jsonify({
        'records': records,
        'counts': {'total': total, 'tel': tel, 'both': both, 'wifi': wifi, 'users': users}
    })

@app.route('/api/users')
def api_users():
    if not session.get('user', {}).get('is_admin'): return jsonify([])
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, phone, password, status FROM users WHERE is_deleted=0")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session: return jsonify({'error': 'Unauthorized'})
    msg = request.form['message']
    target = request.form.get('target', 'GROUP')
    sender = session['user']['username']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if target == 'GROUP':
        cursor.execute("INSERT INTO messages (sender, receiver, message, is_group) VALUES (?, 'ALL', ?, 1)", (sender, msg))
    else:
        cursor.execute("INSERT INTO messages (sender, receiver, message, is_group) VALUES (?, ?, ?, 0)", (sender, target, msg))
        if sender != ADMIN_USERNAME:
            cursor.execute("INSERT INTO notifications (type, message) VALUES ('message', ?)", (f"নতুন মেসেজ: {session['user']['name']} থেকে।",))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/messages')
def api_messages():
    target = request.args.get('target', 'GROUP')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if target == 'GROUP':
        cursor.execute("SELECT m.id, m.sender, u.name, m.message FROM messages m LEFT JOIN users u ON m.sender=u.username WHERE is_group=1 ORDER BY m.id ASC")
    else:
        cursor.execute("SELECT m.id, m.sender, u.name, m.message FROM messages m LEFT JOIN users u ON m.sender=u.username WHERE is_group=0 AND ((sender=? AND receiver=?) OR (sender=? AND receiver=?)) ORDER BY m.id ASC",
                       (session['user']['username'], target, target, session['user']['username']))
    raw = cursor.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'sender': r[1], 'sender_name': r[2] or 'Admin', 'message': r[3]} for r in raw])

@app.route('/api/notifications')
def api_notifications():
    if not session.get('user', {}).get('is_admin'): return jsonify([])
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, message FROM notifications WHERE is_read=0 ORDER BY id DESC")
    notifs = cursor.fetchall()
    conn.close()
    return jsonify([{'id': n[0], 'message': n[1]} for n in notifs])

@app.route('/api/read_notif/<int:id>')
def read_notif(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)