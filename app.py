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
        .notif-badge { position: absolute; top: -5px; right: -5px; background: red; color: white; border-radius: 50%; padding: 2px 6px; font-size: 10px; }
    </style>
</head>
<body>

<div class="gold-pink-header text-center py-2 position-relative">
    <h3 class="m-0"><i class="fa-solid fa-phone-volume"></i> BTCL, কুড়িগ্রাম</h3>
    <small>Md Khushbu Alom - Admin Panel</small>
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
                    <li><a class="dropdown-item" href="#" onclick="showSection('records')"><i class="fa-solid fa-house me-2"></i>হোম (গ্রাহক তালিকা)</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openMessenger()"><i class="fa-solid fa-comments me-2"></i>মেসেঞ্জার</a></li>
                    {% if session['user']['is_admin_or_sub'] %}
                    <li><a class="dropdown-item" href="#" onclick="openAddRecordModal()"><i class="fa-solid fa-plus me-2"></i>নতুন নম্বর যোগ</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openCreateUserModal()"><i class="fa-solid fa-user-plus me-2"></i>নতুন ইউজার তৈরি</a></li>
                    <li><a class="dropdown-item" href="#" onclick="showSection('users')"><i class="fa-solid fa-users me-2"></i>ইউজার তালিকা</a></li>
                    <li>
                        <a class="dropdown-item d-flex justify-content-between align-items-center" href="#" onclick="showSection('pending_users')">
                            <span><i class="fa-solid fa-bell me-2"></i>ইউজার রিকোয়েস্ট</span>
                            <span class="badge bg-danger" id="menuPendingBadge">0</span>
                        </a>
                    </li>
                    {% endif %}
                    <li><hr class="dropdown-divider border-secondary"></li>
                    <li><a class="dropdown-item text-danger" href="/logout"><i class="fa-solid fa-right-from-bracket me-2"></i>লগআউট</a></li>
                </ul>
            </div>
            
            <button class="btn btn-pink btn-sm" onclick="showSection('records')"><i class="fa-solid fa-house"></i> হোম</button>
            <button class="btn btn-outline-warning btn-sm" onclick="openMessenger()"><i class="fa-solid fa-comments"></i> মেসেঞ্জার</button>
            
            {% if session['user']['is_admin_or_sub'] %}
            <button class="btn btn-outline-danger btn-sm position-relative" onclick="showSection('pending_users')" title="নতুন রেজিস্ট্রেশন রিকোয়েস্ট">
                <i class="fa-solid fa-bell"></i> রিকোয়েস্ট
                <span class="notif-badge" id="navPendingBadge" style="display:none;">0</span>
            </button>
            {% endif %}
        </div>
        
        <div>
            <button class="btn btn-gold btn-sm" onclick="openProfileModal()">
                <i class="fa-solid fa-circle-user"></i> প্রোফাইল
            </button>
        </div>
    </div>

    <!-- Search Box -->
    <div class="row g-2 mb-3">
        <div class="col-md-7 position-relative">
            <div class="input-group">
                <input type="text" id="searchInput" class="form-control" placeholder="নাম, মোবাইল বা সংযোগ নম্বর লিখে খুঁজুন..." oninput="handleSearchInput()" autocomplete="off">
                <button class="btn btn-gold" onclick="loadRecords()"><i class="fa-solid fa-magnifying-glass"></i> খুঁজুন</button>
            </div>
            <div id="suggestionsBox" class="suggestions-box"></div>
        </div>
        <div class="col-md-5">
            <select id="sortSelect" class="form-select" onchange="loadRecords()">
                <option value="id_asc">১ থেকে শুরু (সিরিয়াল নম্বর ১, ২, ৩...)</option>
                <option value="id_desc">সর্বশেষ যোগ করা নম্বর উপরে</option>
                <option value="name_asc">নামের ক্রমানুসারে (A to Z)</option>
            </select>
        </div>
    </div>

    <!-- Strict Filter Counters -->
    <div class="row g-2 mb-3">
        <div class="col" onclick="filterService('')"><div class="stat-card"><div class="stat-number" id="countTotal">0</div><div style="font-size:11px">টোটাল নম্বর</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন নম্বর')"><div class="stat-card"><div class="stat-number" id="countTel">0</div><div style="font-size:11px">শুধুমাত্র টেলিফোন</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন+ওয়াইফাই নম্বর')"><div class="stat-card"><div class="stat-number" id="countBoth">0</div><div style="font-size:11px">টেলিফোন+ওয়াইফাই</div></div></div>
        <div class="col" onclick="filterService('ওয়াইফাই নম্বর')"><div class="stat-card"><div class="stat-number" id="countWifi">0</div><div style="font-size:11px">শুধুমাত্র ওয়াইফাই</div></div></div>
        {% if session['user']['is_admin_or_sub'] %}
        <div class="col" onclick="showSection('pending_users')"><div class="stat-card border-danger"><div class="stat-number text-danger" id="countPending">0</div><div style="font-size:11px">নতুন রিকোয়েস্ট</div></div></div>
        {% endif %}
    </div>

    <!-- Customer Records Section -->
    <div id="recordsSection" class="card-custom p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center border-bottom border-warning pb-2">
            <h5 class="text-warning mb-0"><i class="fa-solid fa-list"></i> গ্রাহক ও সংযোগ তালিকা</h5>
            <span class="badge bg-gold text-dark" id="currentFilterLabel">সকল নম্বর</span>
        </div>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle mt-2">
                <thead>
                    <tr>
                        <th>সিরিয়াল</th><th>গ্রাহকের নাম</th><th>মোবাইল</th><th>সেবার ধরন</th><th>সংযোগ নম্বর</th><th>ঠিকানা</th><th>নোট</th><th>এডমিন</th>
                        {% if session['user']['is_admin_or_sub'] %}<th>অ্যাকশন</th>{% endif %}
                    </tr>
                </thead>
                <tbody id="recordsTableBody"></tbody>
            </table>
        </div>
    </div>

    <!-- Pending User Requests Section -->
    {% if session['user']['is_admin_or_sub'] %}
    <div id="pendingUsersSection" class="card-custom p-3 mb-4" style="display:none;">
        <h5 class="text-danger border-bottom border-danger pb-2"><i class="fa-solid fa-user-clock"></i> নতুন রেজিস্টার্ড ইউজার রিকোয়েস্ট (অনুমোদনের অপেক্ষায়)</h5>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr><th>নাম</th><th>ইউজারনেম</th><th>ইমেইল</th><th>মোবাইল</th><th>তারিখ</th><th>সিদ্ধান্ত</th></tr>
                </thead>
                <tbody id="pendingUsersTableBody"></tbody>
            </table>
        </div>
    </div>

    <!-- User Management Section -->
    <div id="usersSection" class="card-custom p-3 mb-4" style="display:none;">
        <div class="d-flex justify-content-between align-items-center mb-2 border-bottom border-warning pb-2">
            <h5 class="text-warning mb-0">অনুমোদিত ইউজার তালিকা</h5>
            <input type="text" id="userSearchInput" class="form-control w-50" placeholder="ইউজারনেম বা নাম লিখে খুঁজুন..." onkeyup="loadUsers()">
        </div>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr><th>ছবি</th><th>নাম</th><th>ইউজারনেম</th><th>মোবাইল</th><th>রোল</th><th>স্ট্যাটাস</th><th>অ্যাকশন</th></tr>
                </thead>
                <tbody id="usersTableBody"></tbody>
            </table>
        </div>
    </div>
    {% endif %}

    {% else %}
    <!-- Public Login / Register Section -->
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

<!-- PROFILE MODAL -->
<div class="modal fade" id="profileModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user"></i> প্রোফাইল অপশনসমূহ</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <ul class="nav nav-pills nav-justified mb-3">
          <li class="nav-item"><button class="nav-link active btn-gold me-1" data-bs-toggle="pill" data-bs-target="#opt1">আমার প্রোফাইল</button></li>
          {% if session.get('user',{}).get('role') == 'main_admin' %}
          <li class="nav-item"><button class="nav-link btn-pink me-1" data-bs-toggle="pill" data-bs-target="#opt2">নতুন এডমিন যুক্ত করুন</button></li>
          <li class="nav-item"><button class="nav-link btn-outline-warning" data-bs-toggle="pill" data-bs-target="#opt4">সিস্টেম হিস্ট্রি</button></li>
          {% endif %}
          <li class="nav-item"><a href="/logout" class="nav-link btn-danger ms-1">লগআউট</a></li>
        </ul>
        
        <div class="tab-content">
          <div class="tab-pane fade show active" id="opt1">
            <div class="card bg-dark text-white p-3 border-secondary text-center">
                {% if session.get('user',{}).get('profile_pic') %}
                <img src="{{ session['user']['profile_pic'] }}" class="rounded-circle mx-auto mb-2" style="width:90px; height:90px; object-fit:cover; border:2px solid #ffd700;">
                {% else %}
                <i class="fa-solid fa-circle-user fa-4x text-warning mb-2"></i>
                {% endif %}
                <h5>{{ session.get('user',{}).get('name') }}</h5>
                <p class="text-warning mb-1"><strong>ইউজারনেম:</strong> {{ session.get('user',{}).get('username') }}</p>
                <p class="mb-2"><strong>রোল:</strong> {{ session.get('user',{}).get('role') }}</p>
                
                <form action="/upload_profile_pic" method="POST" enctype="multipart/form-data" class="mt-2">
                    <label class="form-label" style="font-size:12px;">প্রোফাইল ছবি আপলোড/পরিবর্তন</label>
                    <input type="file" name="pic" class="form-control mb-2" accept="image/*" required>
                    <button type="submit" class="btn btn-gold btn-sm">ছবি সেভ করুন</button>
                </form>
            </div>
          </div>

          {% if session.get('user',{}).get('role') == 'main_admin' %}
          <div class="tab-pane fade" id="opt2">
            <div class="card bg-dark text-white p-3 border-warning mb-3">
                <h6 class="text-warning border-bottom pb-2">নতুন সাব-এডমিন তৈরি</h6>
                <form action="/admin/create_sub_admin" method="POST" class="row g-2">
                    <div class="col-md-6"><label class="form-label">নাম *</label><input type="text" name="name" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">ইমেইল *</label><input type="email" name="email" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">মোবাইল *</label><input type="text" name="phone" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">ইউজারনেম *</label><input type="text" name="username" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">পাসওয়ার্ড *</label><input type="password" name="password" class="form-control" required></div>
                    <div class="col-md-6"><label class="form-label">সিকিউরিটি পিন *</label><input type="password" name="security_code" class="form-control" required placeholder="137955"></div>
                    <div class="col-12 mt-3"><button type="submit" class="btn btn-gold w-100">এডমিন তৈরি করুন</button></div>
                </form>
            </div>
          </div>

          <div class="tab-pane fade" id="opt4">
            <div class="card bg-dark text-white p-3 border-secondary">
                <h6 class="text-warning border-bottom pb-2">অ্যাক্টিভিটি লগ / কাজের ইতিহাস</h6>
                <div id="adminHistoryContent" style="max-height: 250px; overflow-y:auto;"></div>
            </div>
          </div>
          {% endif %}
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Create User Modal -->
<div class="modal fade" id="createUserModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-plus"></i> সরাসরি নতুন ইউজার তৈরি করুন</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/admin/create_user_direct" method="POST" class="modal-body row g-3">
        <div class="col-12"><label class="form-label">নাম *</label><input type="text" name="name" class="form-control" required></div>
        <div class="col-6"><label class="form-label">ইউজারনেম *</label><input type="text" name="username" class="form-control" required></div>
        <div class="col-6"><label class="form-label">মোবাইল *</label><input type="text" name="phone" class="form-control" required></div>
        <div class="col-12"><label class="form-label">ইমেইল *</label><input type="email" name="email" class="form-control" required></div>
        <div class="col-12"><label class="form-label">পাসওয়ার্ড *</label><input type="password" name="password" class="form-control" required></div>
        <div class="col-12 text-end"><button type="submit" class="btn btn-gold px-4">ইউজার তৈরি করুন</button></div>
      </form>
    </div>
  </div>
</div>

<!-- Add/Edit Record Modal -->
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

<!-- Messenger Modal -->
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
                📢 গ্রুপ চ্যাট (সকলের জন্য)
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

function handleSearchInput() {
    let q = document.getElementById('searchInput').value.trim();
    let suggestionsBox = document.getElementById('suggestionsBox');
    
    if (q.length === 0) {
        suggestionsBox.style.display = 'none';
        loadRecords();
        return;
    }

    fetch(`/api/suggestions?q=${q}`)
    .then(res => res.json())
    .then(list => {
        if(list.length > 0) {
            let html = '';
            list.forEach(item => {
                html += `<div class="suggestion-item" onclick="selectSuggestion('${item}')"><i class="fa-solid fa-magnifying-glass me-2 text-warning"></i>${item}</div>`;
            });
            suggestionsBox.innerHTML = html;
            suggestionsBox.style.display = 'block';
        } else {
            suggestionsBox.style.display = 'none';
        }
    });
    loadRecords();
}

function selectSuggestion(val) {
    document.getElementById('searchInput').value = val;
    document.getElementById('suggestionsBox').style.display = 'none';
    loadRecords();
}

function loadRecords() {
    let q = document.getElementById('searchInput') ? document.getElementById('searchInput').value : '';
    let sort = document.getElementById('sortSelect') ? document.getElementById('sortSelect').value : 'id_asc';
    
    fetch(`/api/search?q=${q}&service=${activeServiceFilter}&sort=${sort}`)
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.records.forEach((row, idx) => {
            let displayIndex = (sort === 'id_desc') ? (data.records.length - idx) : (idx + 1);
            html += `<tr>
                <td><strong>${displayIndex}</strong></td>
                <td><a href="#" class="text-warning text-decoration-none">${row[1]}</a></td>
                <td>${row[2] || '-'}</td>
                <td><span class="badge bg-warning text-dark">${row[3]}</span></td>
                <td>${row[4] || '-'}</td>
                <td>${row[5] || '-'}</td>
                <td>${row[6] || '-'}</td>
                <td><small class="text-info">${row[7] || 'System'}</small></td>
                {% if session.get('user', {}).get('is_admin_or_sub') %}
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
        if(document.getElementById('countPending')) {
            document.getElementById('countPending').innerText = data.counts.pending;
            let navBadge = document.getElementById('navPendingBadge');
            let menuBadge = document.getElementById('menuPendingBadge');
            if(data.counts.pending > 0) {
                navBadge.innerText = data.counts.pending;
                navBadge.style.display = 'inline-block';
                menuBadge.innerText = data.counts.pending;
            } else {
                navBadge.style.display = 'none';
                menuBadge.innerText = '0';
            }
        }
    });
}

function filterService(type) { 
    activeServiceFilter = type; 
    let label = 'সকল নম্বর';
    if(type === 'টেলিফোন নম্বর') label = 'শুধুমাত্র টেলিফোন নম্বর';
    else if(type === 'টেলিফোন+ওয়াইফাই নম্বর') label = 'শুধুমাত্র টেলিফোন + ওয়াইফাই নম্বর';
    else if(type === 'ওয়াইফাই নম্বর') label = 'শুধুমাত্র ওয়াইফাই নম্বর';
    
    document.getElementById('currentFilterLabel').innerText = label;
    loadRecords(); 
}

function showSection(sec) {
    document.getElementById('recordsSection').style.display = (sec === 'records') ? 'block' : 'none';
    if(document.getElementById('usersSection')) document.getElementById('usersSection').style.display = (sec === 'users') ? 'block' : 'none';
    if(document.getElementById('pendingUsersSection')) document.getElementById('pendingUsersSection').style.display = (sec === 'pending_users') ? 'block' : 'none';
    
    if(sec === 'users') loadUsers();
    if(sec === 'pending_users') loadPendingUsers();
}

function loadPendingUsers() {
    fetch('/api/pending_users')
    .then(res => res.json())
    .then(users => {
        let html = '';
        users.forEach(u => {
            html += `<tr>
                <td><strong>${u[1]}</strong></td>
                <td>${u[2]}</td>
                <td>${u[3]}</td>
                <td>${u[4]}</td>
                <td><small class="text-muted">${u[7]}</small></td>
                <td>
                    <button class="btn btn-success btn-sm me-1" onclick="userAction(${u[0]}, 'approve')"><i class="fa-solid fa-check"></i> Accept</button>
                    <button class="btn btn-danger btn-sm" onclick="userAction(${u[0]}, 'delete')"><i class="fa-solid fa-xmark"></i> Reject/Delete</button>
                </td>
            </tr>`;
        });
        if(users.length === 0) html = '<tr><td colspan="6" class="text-center text-muted">কোনো নতুন রেজিস্ট্রেশন আবেদন নেই।</td></tr>';
        document.getElementById('pendingUsersTableBody').innerHTML = html;
    });
}

function loadUsers() {
    let q = document.getElementById('userSearchInput') ? document.getElementById('userSearchInput').value : '';
    fetch('/api/users?q=' + q)
    .then(res => res.json())
    .then(users => {
        let html = '';
        users.forEach(u => {
            let img = u[8] ? `<img src="${u[8]}" class="avatar-img">` : `<i class="fa-solid fa-user text-secondary"></i>`;
            let actionBtn = u[2] !== 'Khushbu23' ? 
                `<button class="btn btn-danger btn-sm" onclick="userAction(${u[0]}, 'delete')">ডিলিট</button>` : 'সুরক্ষিত';

            html += `<tr>
                <td>${img}</td>
                <td>${u[1]}</td>
                <td>${u[2]}</td>
                <td>${u[4]}</td>
                <td><span class="badge bg-info text-dark">${u[5]}</span></td>
                <td><span class="badge ${u[6]=='active'?'bg-success':'bg-warning'}">${u[6]}</span></td>
                <td>${actionBtn}</td>
            </tr>`;
        });
        document.getElementById('usersTableBody').innerHTML = html;
    });
}

function userAction(id, action) {
    let formData = new FormData();
    if(action === 'delete') {
        if(!confirm("আপনি কি নিশ্চিতভাবে এই অ্যাকাউন্টটি মুছে ফেলতে চান?")) return;
        formData.append('security_code', '137955');
    }
    fetch(`/admin/user_action/${id}/${action}`, { method: 'POST', body: formData })
    .then(() => {
        loadRecords();
        loadPendingUsers();
        loadUsers();
    });
}

function openCreateUserModal() {
    new bootstrap.Modal(document.getElementById('createUserModal')).show();
}

function openAddRecordModal() {
    document.getElementById('recordForm').reset();
    document.getElementById('rec_id').value = '';
    document.getElementById('recordModalTitle').innerText = "নতুন নম্বর যোগ করুন";
    new bootstrap.Modal(document.getElementById('recordModal')).show();
}

function openEditRecordModal(id) {
    fetch('/api/get_record/' + id)
    .then(res => res.json())
    .then(data => {
        document.getElementById('rec_id').value = data[0];
        document.getElementById('rec_name').value = data[1];
        document.getElementById('rec_mobile').value = data[2];
        document.getElementById('rec_service').value = data[3];
        document.getElementById('rec_conn').value = data[4];
        document.getElementById('rec_address').value = data[5];
        document.getElementById('rec_note').value = data[6];
        document.getElementById('recordModalTitle').innerText = "নম্বর এডিট করুন";
        new bootstrap.Modal(document.getElementById('recordModal')).show();
    });
}

function saveRecord(e) {
    e.preventDefault();
    let formData = new FormData(document.getElementById('recordForm'));
    fetch('/save_record', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
        bootstrap.Modal.getInstance(document.getElementById('recordModal')).hide();
        loadRecords();
    });
}

function deleteRecord(id) {
    let pin = prompt("সিকিউরিটি পিন দিন (137955):");
    if(pin === '137955') {
        let formData = new FormData();
        formData.append('security_code', pin);
        fetch('/delete_record/' + id, { method: 'POST', body: formData })
        .then(() => loadRecords());
    }
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
        let html = '';
        users.forEach(u => {
            if(u[2] !== "{{ session.get('user', {}).get('username') }}") {
                let img = u[8] ? `<img src="${u[8]}" class="avatar-img me-1">` : '';
                html += `<div class="p-2 border-bottom border-secondary d-flex align-items-center justify-content-between text-white" style="cursor:pointer;" onclick="selectChatTarget('${u[2]}', '${u[1]}')">
                            <div>${img} <strong>${u[1]}</strong></div>
                            <small class="text-info" style="font-size:10px;">${u[9]}</small>
                         </div>`;
            }
        });
        document.getElementById('usersChatNav').innerHTML = html;
    });
}

function selectChatTarget(target, name) {
    currentChatTarget = target;
    document.getElementById('activeChatHeader').innerText = name;
    loadMessages();
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
    });
}

function openProfileModal() {
    new bootstrap.Modal(document.getElementById('profileModal')).show();
    loadAdminHistory();
}

function loadAdminHistory() {
    fetch('/api/activity_logs')
    .then(res => res.json())
    .then(logs => {
        let html = '<ul class="list-group bg-dark">';
        logs.forEach(l => {
            html += `<li class="list-group-item bg-dark text-white border-secondary">
                        <small class="text-warning">${l[3]}</small><br>
                        <strong>${l[1]}:</strong> ${l[2]}
                     </li>`;
        });
        html += '</ul>';
        if(document.getElementById('adminHistoryContent')) document.getElementById('adminHistoryContent').innerHTML = html;
    });
}

if(document.getElementById('searchInput')) {
    loadRecords();
    setInterval(loadRecords, 5000);
}
</script>
</body>
</html>
"""

# --- BACKEND SERVER ROUTES ---

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
            return "<script>alert('আপনার রেজিস্ট্রেশন আবেদন এখনও অনুমোদিত হয়নি! এডমিন একসেপ্ট করলে লগইন করতে পারবেন।'); window.location='/';</script>"
        
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

@app.route('/register', methods=['POST'])
def register():
    hashed_pw = generate_password_hash(request.form['password'])
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, username, email, phone, password, role, status) VALUES (?, ?, ?, ?, ?, 'user', 'pending')",
                       (request.form['name'], request.form['username'], request.form['email'], request.form['phone'], hashed_pw))
        conn.commit()
        conn.close()
        return "<script>alert('রেজিস্ট্রেশন আবেদন জমা হয়েছে! এডমিন একসেপ্ট করার পর লগইন করতে পারবেন।'); window.location='/';</script>"
    except:
        return "<script>alert('ইউজারনেম বা তথ্য আগে থেকেই ব্যবহৃত হচ্ছে!'); window.location='/';</script>"

@app.route('/admin/create_user_direct', methods=['POST'])
def create_user_direct():
    if not session.get('user', {}).get('is_admin_or_sub'): return redirect(url_for('home'))
    hashed_pw = generate_password_hash(request.form['password'])
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, username, email, phone, password, role, status, added_by) VALUES (?, ?, ?, ?, ?, 'user', 'active', ?)",
                       (request.form['name'], request.form['username'], request.form['email'], request.form['phone'], hashed_pw, session['user']['username']))
        conn.commit()
        conn.close()
        log_activity(session['user']['username'], f"নতুন ইউজার তৈরি করেছেন: {request.form['username']}")
        return "<script>alert('নতুন ইউজার সফলভাবে তৈরি ও একসেপ্ট করা হয়েছে!'); window.location='/';</script>"
    except:
        return "<script>alert('ইউজার তৈরিতে সমস্যা হয়েছে বা ইউজারনেম আগে থেকেই আছে!'); window.location='/';</script>"

@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'user' not in session: return redirect(url_for('home'))
    if 'pic' in request.files:
        file = request.files['pic']
        if file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{session['user']['username']}_{filename}")
            file.save(filepath)
            
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET profile_pic=? WHERE id=?", ('/' + filepath, session['user']['id']))
            conn.commit()
            conn.close()
            session['user']['profile_pic'] = '/' + filepath
    return redirect(url_for('home'))

@app.route('/admin/create_sub_admin', methods=['POST'])
def admin_create_sub_admin():
    if session.get('user', {}).get('role') != 'main_admin':
        return "<script>alert('শুধুমাত্র মূল এডমিন তৈরি করতে পারবেন!'); window.location='/';</script>"
    
    if request.form.get('security_code') != ADMIN_SECURITY_CODE:
        return "<script>alert('ভুল সিকিউরিটি পিন!'); window.location='/';</script>"

    hashed_pw = generate_password_hash(request.form['password'])
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, username, email, phone, password, role, status, added_by) VALUES (?, ?, ?, ?, ?, 'admin', 'active', ?)",
                   (request.form['name'], request.form['username'], request.form['email'], request.form['phone'], hashed_pw, session['user']['username']))
    conn.commit()
    conn.close()
    
    log_activity(session['user']['username'], f"নতুন এডমিন তৈরি করেছেন: {request.form['username']}")
    return "<script>alert('নতুন এডমিন সফলভাবে তৈরি হয়েছে!'); window.location='/';</script>"

@app.route('/save_record', methods=['POST'])
def save_record():
    if not session.get('user', {}).get('is_admin_or_sub'): return jsonify({'status': 'unauthorized'})
    rec_id = request.form.get('id')
    user_name = session['user']['username']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if rec_id:
        cursor.execute('''UPDATE phone_records SET customer_name=?, mobile=?, service_type=?, connection_num=?, address=?, note=? WHERE id=?''',
                       (request.form['customer_name'], request.form.get('mobile', ''), request.form['service_type'],
                        request.form.get('connection_num', ''), request.form.get('address', ''), request.form.get('note', ''), rec_id))
        log_activity(user_name, f"নম্বর আপডেট করেছেন (ID: {rec_id})")
    else:
        cursor.execute('''INSERT INTO phone_records (customer_name, mobile, service_type, connection_num, address, note, added_by) VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                       (request.form['customer_name'], request.form.get('mobile', ''), request.form['service_type'],
                        request.form.get('connection_num', ''), request.form.get('address', ''), request.form.get('note', ''), user_name))
        log_activity(user_name, f"নতুন নম্বর এড করেছেন: {request.form['customer_name']}")
        
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/delete_record/<int:id>', methods=['POST'])
def delete_record(id):
    if request.form.get('security_code') != ADMIN_SECURITY_CODE:
        return jsonify({'status': 'error'})
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE phone_records SET is_deleted=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_activity(session['user']['username'], f"নম্বর ডিলিট করেছেন (ID: {id})")
    return jsonify({'status': 'success'})

@app.route('/api/get_record/<int:id>')
def get_record(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, mobile, service_type, connection_num, address, note, added_by FROM phone_records WHERE id=?", (id,))
    data = cursor.fetchone()
    conn.close()
    return jsonify(data)

@app.route('/api/suggestions')
def api_suggestions():
    q = request.args.get('q', '')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT customer_name FROM phone_records WHERE is_deleted=0 AND customer_name LIKE ? LIMIT 6", (f'%{q}%',))
    suggestions = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify(suggestions)

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    service = request.args.get('service', '')
    sort = request.args.get('sort', 'id_asc')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    order_by = "id ASC"
    if sort == 'id_desc': order_by = "id DESC"
    elif sort == 'name_asc': order_by = "customer_name ASC"

    query = "SELECT id, customer_name, mobile, service_type, connection_num, address, note, added_by FROM phone_records WHERE is_deleted=0 AND (customer_name LIKE ? OR mobile LIKE ? OR connection_num LIKE ? OR address LIKE ? OR note LIKE ?)"
    params = [f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%']

    # Exact Matching Logic for Filter Buttons
    if service != '':
        query += " AND service_type = ?"
        params.append(service)

    query += f" ORDER BY {order_by}"
    cursor.execute(query, params)
    records = cursor.fetchall()

    # Exact Counters for Stats Bar
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type = 'টেলিফোন নম্বর'")
    tel = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type = 'টেলিফোন+ওয়াইফাই নম্বর'")
    both = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type = 'ওয়াইফাই নম্বর'")
    wifi = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE status='pending' AND is_deleted=0")
    pending = cursor.fetchone()[0]

    conn.close()
    return jsonify({'records': records, 'counts': {'total': total, 'tel': tel, 'both': both, 'wifi': wifi, 'pending': pending}})

@app.route('/api/pending_users')
def api_pending_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, phone, role, status, created_at FROM users WHERE status='pending' AND is_deleted=0")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/api/users')
def api_users():
    q = request.args.get('q', '')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, phone, role, status, last_active, profile_pic FROM users WHERE status='active' AND is_deleted=0 AND (name LIKE ? OR username LIKE ?)", (f'%{q}%', f'%{q}%'))
    raw = cursor.fetchall()
    
    users = []
    for u in raw:
        last_act = datetime.strptime(u[7], "%Y-%m-%d %H:%M:%S") if u[7] else datetime.now()
        diff_mins = int((datetime.now() - last_act).total_seconds() / 60)
        status_str = "অনলাইন" if diff_mins < 3 else f"{diff_mins} মিনিট আগে"
        users.append([u[0], u[1], u[2], u[3], u[4], u[5], u[6], u[7], u[8], status_str])
        
    conn.close()
    return jsonify(users)

@app.route('/admin/user_action/<int:id>/<string:action>', methods=['POST'])
def user_action(id, action):
    if not session.get('user', {}).get('is_admin_or_sub'): return jsonify({'status': 'unauthorized'})
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if action == 'approve':
        cursor.execute("UPDATE users SET status='active' WHERE id=?", (id,))
        log_activity(session['user']['username'], f"ইউজার রিকোয়েস্ট একসেপ্ট করেছেন (ID: {id})")
    elif action == 'delete':
        if request.form.get('security_code') != ADMIN_SECURITY_CODE:
            conn.close()
            return jsonify({'status': 'error'})
        cursor.execute("UPDATE users SET is_deleted=1 WHERE id=?", (id,))
        log_activity(session['user']['username'], f"ইউজার ডিলিট/রিজেক্ট করেছেন (ID: {id})")

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
    cursor.execute("INSERT INTO messages (sender, receiver, message, file_url, is_group) VALUES (?, ?, ?, ?, ?)", 
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
        msgs.append({'id': r[0], 'sender': r[1], 'sender_name': r[2] or r[1], 'message': r[3], 'timestamp_time': t_str, 'sender_role': r[5], 'file_url': r[6]})
        
    return jsonify(msgs)

@app.route('/api/activity_logs')
def api_activity_logs():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, action, timestamp FROM activity_logs ORDER BY id DESC LIMIT 50")
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)