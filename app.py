import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_btcl_kurigram_gold_pink_2026_v2")

MAIN_ADMIN_USERNAME = "Khushbu23"
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
            role TEXT DEFAULT 'user', -- 'main_admin', 'admin', 'user'
            status TEXT DEFAULT 'pending',
            added_by TEXT DEFAULT 'Self',
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
            added_by TEXT DEFAULT 'Khushbu23',
            is_deleted INTEGER DEFAULT 0
        )
    ''')
    
    # Messages Table (Supports Group & Private Chat)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT, -- 'GROUP' for group chat, or target username
            message TEXT,
            file_url TEXT,
            is_group INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_user TEXT DEFAULT 'ADMIN',
            type TEXT,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Activity History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Main Admin Creation
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

init_db()

# --- Full HTML/CSS/JS Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম - Advanced Messenger & Admin System</title>
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
            background: rgba(45, 10, 30, 0.95);
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
        .stat-number { font-size: 20px; font-weight: bold; color: #ffd700; }
        .stat-label { font-size: 11px; color: #ffccf2; }
        .offcanvas { background-color: #1f0012; color: #ffe6f2; border-right: 2px solid #d4af37; }
        .nav-link-custom { color: #ffd700; padding: 12px 15px; border-bottom: 1px solid #4a1525; display: block; text-decoration: none; cursor: pointer; }
        .nav-link-custom:hover { background-color: #ff66b2; color: #fff; }
        .chat-bubble-me { background: #ff66b2; color: #fff; border-radius: 12px 12px 0 12px; margin-left: auto; max-width: 80%; }
        .chat-bubble-them { background: #d4af37; color: #000; border-radius: 12px 12px 12px 0; margin-right: auto; max-width: 80%; }
        .chat-user-item { cursor: pointer; border-bottom: 1px solid #3d0e26; transition: 0.2s; }
        .chat-user-item:hover, .chat-user-item.active { background-color: #ff66b2; color: #fff !important; }
        .close-cross {
            font-size: 1.5rem;
            color: #ff66b2;
            cursor: pointer;
            transition: 0.2s;
        }
        .close-cross:hover { color: #ffd700; transform: scale(1.2); }
    </style>
</head>
<body>

<div class="gold-pink-header text-center py-2">
    <h3 class="m-0"><i class="fa-solid fa-phone-volume"></i> BTCL, কুড়িগ্রাম</h3>
    <small>Md Khushbu Alom - Admin Desk</small>
</div>

<div class="container py-3">
    {% if session.get('user') %}
    <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center gap-2">
            <button class="btn btn-gold btn-sm" data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu">
                <i class="fa-solid fa-bars"></i> মেনু
            </button>
            <a href="/" class="btn btn-pink btn-sm"><i class="fa-solid fa-house"></i> হোম</a>
            <button class="btn btn-outline-warning btn-sm" onclick="openMessenger()"><i class="fa-solid fa-comments"></i> মেসেঞ্জার</button>
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

            <button class="btn btn-gold btn-sm" onclick="openProfileModal()">
                <i class="fa-solid fa-circle-user"></i> প্রোফাইল
            </button>

            <a href="/logout" class="btn btn-danger btn-sm" title="লগআউট"><i class="fa-solid fa-power-off"></i></a>
        </div>
    </div>

    <div id="successAlert" class="alert alert-success alert-dismissible fade show" role="alert" style="display:none;">
        <strong>সাকসেসফুল!</strong> <span id="successMsg">নম্বরটি সফলভাবে যোগ করা হয়েছে।</span>
        <button type="button" class="btn-close" onclick="document.getElementById('successAlert').style.display='none'"></button>
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
            <div class="stat-card"><div class="stat-number" id="countTotal">0</div><div class="stat-label">টোটাল নম্বর</div></div>
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
        {% if session['user']['is_admin_or_sub'] %}
        <div class="col" onclick="showSection('users')">
            <div class="stat-card"><div class="stat-number" id="countUsers">0</div><div class="stat-label">ইউজার তালিকা</div></div>
        </div>
        {% endif %}
    </div>

    <div id="recordsSection" class="card-custom p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center border-bottom border-warning pb-2">
            <h5 class="m-0 text-warning"><i class="fa-solid fa-list"></i> গ্রাহক ও সংযোগ নম্বর তালিকা</h5>
            <button class="btn btn-gold btn-sm" onclick="openAddRecordModal()"><i class="fa-solid fa-plus"></i> নতুন নম্বর এড</button>
        </div>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle mt-2">
                <thead>
                    <tr>
                        <th>সিরিয়াল</th><th>নাম</th><th>মোবাইল</th><th>সেবার ধরন</th><th>সংযোগ নং</th><th>ঠিকানা</th><th>নোট</th><th>এড করেছেন</th>
                        {% if session['user']['is_admin_or_sub'] %}<th>অ্যাকশন</th>{% endif %}
                    </tr>
                </thead>
                <tbody id="recordsTableBody"></tbody>
            </table>
        </div>
    </div>

    {% if session['user']['is_admin_or_sub'] %}
    <div id="usersSection" class="card-custom p-3 mb-4" style="display:none;">
        <h5 class="text-warning border-bottom border-warning pb-2">নিবন্ধিত ইউজার ও এডমিন তালিকা</h5>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr><th>নাম</th><th>ইউজারনেম</th><th>মোবাইল</th><th>রোল (Role)</th><th>স্ট্যাটাস</th><th>অ্যাকশন</th></tr>
                </thead>
                <tbody id="usersTableBody"></tbody>
            </table>
        </div>
    </div>
    
    <div id="deletedRecordsSection" class="card-custom p-3 mb-4" style="display:none;">
        <h5 class="text-danger border-bottom border-danger pb-2">ডিলিট হওয়া নম্বর তালিকা</h5>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead><tr><th>নাম</th><th>মোবাইল</th><th>সেবা</th><th>সংযোগ নং</th></tr></thead>
                <tbody id="deletedTableBody"></tbody>
            </table>
        </div>
    </div>

    <div id="activitySection" class="card-custom p-3 mb-4" style="display:none;">
        <div class="d-flex justify-content-between align-items-center border-bottom border-warning pb-2">
            <h5 class="text-warning m-0">এডমিন অ্যাক্টিভিটি হিস্ট্রি</h5>
            {% if session['user']['role'] == 'main_admin' %}
            <button class="btn btn-danger btn-sm" onclick="clearActivityHistory()"><i class="fa-solid fa-trash"></i> হিস্ট্রি মুছুন (Clear)</button>
            {% endif %}
        </div>
        <div class="table-responsive mt-2">
            <table class="table table-dark table-striped align-middle">
                <thead><tr><th>সময়</th><th>ইউজারনেম</th><th>অ্যাকশন/বিবরণ</th></tr></thead>
                <tbody id="activityTableBody"></tbody>
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
                                <input type="text" name="username" class="form-control" required placeholder="ইউজারনেম বা মোবাইল নম্বর">
                            </div>
                            <div class="mb-3">
                                <label class="form-label">পাসওয়ার্ড</label>
                                <input type="password" name="password" class="form-control" required placeholder="পাসওয়ার্ড">
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
  <div class="offcanvas-header border-bottom border-warning d-flex justify-content-between">
    <h5 class="offcanvas-title text-warning">প্রধান মেনু</h5>
    <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="offcanvas"></i>
  </div>
  <div class="offcanvas-body p-0">
    <a class="nav-link-custom" onclick="showSection('records')">১. ওভারভিউ ও ডাটা</a>
    <a class="nav-link-custom" onclick="showNotifHistoryModal()">২. নোটিফিকেশন হিস্টরি</a>
    <a class="nav-link-custom" onclick="openAddRecordModal()">৩. নম্বর এড করুন</a>
    {% if session.get('user', {}).get('is_admin_or_sub') %}
    <a class="nav-link-custom" onclick="openProfileModal()">৪. নতুন এডমিন বিল্ড/তৈরি</a>
    <a class="nav-link-custom" onclick="showSection('users')">৫. নিবন্ধিত ইউজার তথ্য</a>
    <a class="nav-link-custom" onclick="openAdminSecurityModal()">৬. সিকিউরিটি ও পাসওয়ার্ড পরিবর্তন</a>
    <a class="nav-link-custom" onclick="verifyPinAndShowDeleted()">৭. ডিলিট হওয়া নম্বর</a>
    <a class="nav-link-custom" onclick="showSection('activity')">৮. এডমিন অ্যাক্টিভিটি হিস্ট্রি</a>
    {% endif %}
    <a class="nav-link-custom" onclick="openMessenger()">৯. মেসেঞ্জার (গ্রুপ ও সরাসরি চ্যাট)</a>
  </div>
</div>

<div class="modal fade" id="profileModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-gear"></i> প্রোফাইল ও এডমিন বিল্ডার</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="card bg-dark text-white p-3 mb-3 border-secondary">
            <h6 class="text-warning border-bottom pb-1">আমার প্রোফাইল তথ্য:</h6>
            <p class="mb-1"><strong>নাম:</strong> {{ session.get('user', {}).get('name') }}</p>
            <p class="mb-1"><strong>ইউজারনেম:</strong> {{ session.get('user', {}).get('username') }}</p>
            <p class="mb-0"><strong>রোল:</strong> <span class="badge bg-warning text-dark">{{ session.get('user', {}).get('role') }}</span></p>
        </div>

        {% if session.get('user', {}).get('role') == 'main_admin' %}
        <div class="card bg-dark text-white p-3 border-warning">
            <h6 class="text-warning border-bottom pb-2"><i class="fa-solid fa-user-plus"></i> নতুন এডমিন তৈরি করুন (Sub-Admin Builder)</h6>
            <form action="/admin/create_sub_admin" method="POST" class="row g-2">
                <div class="col-md-6"><label class="form-label">এডমিনের নাম *</label><input type="text" name="name" class="form-control" required></div>
                <div class="col-md-6"><label class="form-label">ইমেইল *</label><input type="email" name="email" class="form-control" required></div>
                <div class="col-md-6"><label class="form-label">মোবাইল নম্বর *</label><input type="text" name="phone" class="form-control" required></div>
                <div class="col-md-6"><label class="form-label">ইউজারনেম *</label><input type="text" name="username" class="form-control" required></div>
                <div class="col-md-6"><label class="form-label">পাসওয়ার্ড *</label><input type="password" name="password" class="form-control" required></div>
                <div class="col-md-6"><label class="form-label">এডমিন সিকিউরিটি পিন (137955) *</label><input type="password" name="security_code" class="form-control" required placeholder="পিন দিন"></div>
                <div class="col-12 text-end mt-3"><button type="submit" class="btn btn-gold w-100">নতুন এডমিন যুক্ত করুন</button></div>
            </form>
        </div>
        {% endif %}
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="addRecordModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning">নতুন নম্বর এড করুন</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form id="addRecordForm" onsubmit="submitAddRecord(event)" class="modal-body row g-3">
        <div class="col-md-6">
            <label class="form-label">গ্রাহকের নাম (বাধ্যতামূলক) *</label>
            <input type="text" id="add_name" name="customer_name" class="form-control" required placeholder="নাম লিখুন">
        </div>
        <div class="col-md-6">
            <label class="form-label">মোবাইল নম্বর</label>
            <input type="text" id="add_mobile" name="mobile" class="form-control" placeholder="মোবাইল নম্বর">
        </div>
        <div class="col-md-6">
            <label class="form-label">সেবার ধরন সিলেক্ট করুন *</label>
            <select id="add_service" name="service_type" class="form-select" required>
                <option value="টেলিফোন নম্বর">টেলিফোন নম্বর</option>
                <option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই নম্বর</option>
                <option value="ওয়াইফাই নম্বর">ওয়াইফাই নম্বর</option>
            </select>
        </div>
        <div class="col-md-6">
            <label class="form-label">সংযোগ নম্বর</label>
            <input type="text" id="add_conn" name="connection_num" class="form-control" placeholder="সংযোগ নম্বর">
        </div>
        <div class="col-md-6">
            <label class="form-label">ঠিকানা</label>
            <input type="text" id="add_address" name="address" class="form-control" placeholder="ঠিকানা">
        </div>
        <div class="col-md-6">
            <label class="form-label">অতিরিক্ত নোট</label>
            <input type="text" id="add_note" name="note" class="form-control" placeholder="নোট">
        </div>
        <div class="col-12 text-end mt-3">
            <button type="submit" class="btn btn-gold px-4 py-2">সংরক্ষণ করুন</button>
        </div>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="messengerModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-comments"></i> মেসেঞ্জার হেল্পডেস্ক (গ্রুপ ও চ্যাট)</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body row g-0">
        <div class="col-md-4 border-end border-warning pe-2" style="max-height: 400px; overflow-y:auto;">
            <div class="p-2 chat-user-item active rounded mb-1" onclick="selectChatTarget('GROUP', '📢 গ্রুপ চ্যাট (সকলের জন্য)')">
                <strong>📢 গ্রুপ চ্যাট (সকলের জন্য)</strong>
            </div>
            <div id="usersChatNav"></div>
        </div>
        
        <div class="col-md-8 ps-2 d-flex flex-column" style="min-height: 380px;">
            <div id="activeChatHeader" class="fw-bold text-warning pb-2 border-bottom border-secondary">📢 গ্রুপ চ্যাট (সকলের জন্য)</div>
            <div id="chatMessagesBox" class="flex-grow-1 p-2 my-2 border border-secondary rounded overflow-auto" style="height:270px; background:#12020d;"></div>
            
            <div class="input-group">
                <label class="btn btn-pink" title="ছবি / ভিডিও তুলুন বা পোস্ট করুন">
                    <i class="fa-solid fa-camera"></i>
                    <input type="file" id="chatFile" accept="image/*,video/*" capture="environment" style="display:none;" onchange="updateFileName()">
                </label>
                <input type="text" id="chatInputMsg" class="form-control" placeholder="মেসেজ লিখুন..." onkeypress="if(event.key==='Enter') sendChatMsg()">
                <button class="btn btn-gold" onclick="sendChatMsg()"><i class="fa-solid fa-paper-plane"></i></button>
            </div>
            <small id="selectedFileName" class="text-info mt-1" style="font-size: 11px;"></small>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="notifHistoryModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-bell"></i> নোটিফিকেশন হিস্টরি</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="list-group" id="notifHistoryList"></div>
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="adminSecModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning">সিকিউরিটি ও পাসওয়ার্ড পরিবর্তন</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/admin/change_password" method="POST" class="modal-body">
            <label class="form-label">নতুন ইউজারনেম</label>
            <input type="text" name="new_username" class="form-control mb-2" value="{{ session.get('user',{}).get('username') }}" required>
            <label class="form-label">নতুন পাসওয়ার্ড</label>
            <input type="password" name="new_password" class="form-control mb-2" required>
            <label class="form-label">সিকিউরিটি পিন (137955)</label>
            <input type="password" name="security_code" class="form-control" required placeholder="পিন দিন">
            <button type="submit" class="btn btn-gold w-100 mt-3">সংরক্ষণ করুন</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="deleteModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-danger d-flex justify-content-between">
        <h5 class="modal-title text-danger">ডিলিট কনফার্মেশন</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form id="deleteForm" method="POST" class="modal-body">
            <label class="form-label">এডমিন সিকিউরিটি পিন দিন (137955):</label>
            <input type="password" name="security_code" class="form-control" required placeholder="সিকিউরিটি পিন">
            <button type="submit" class="btn btn-danger w-100 mt-3">ডিলিট করুন</button>
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
                <td><small class="text-info">${row[7] || 'System'}</small></td>
                {% if session.get('user', {}).get('is_admin_or_sub') %}
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

function openAddRecordModal() {
    closeSidebar();
    new bootstrap.Modal(document.getElementById('addRecordModal')).show();
}

function openProfileModal() {
    closeSidebar();
    new bootstrap.Modal(document.getElementById('profileModal')).show();
}

function submitAddRecord(e) {
    e.preventDefault();
    let formData = new FormData(document.getElementById('addRecordForm'));
    fetch('/add_record', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
        if(data.status === 'success') {
            bootstrap.Modal.getInstance(document.getElementById('addRecordModal')).hide();
            document.getElementById('addRecordForm').reset();
            document.getElementById('successMsg').innerText = "নম্বরটি সফলভাবে ড্যাশবোর্ডে যোগ করা হয়েছে!";
            document.getElementById('successAlert').style.display = 'block';
            loadRecords();
        }
    });
}

function showNotifHistoryModal() {
    closeSidebar();
    new bootstrap.Modal(document.getElementById('notifHistoryModal')).show();
    fetch('/api/all_notifications')
    .then(res => res.json())
    .then(notifs => {
        let html = '';
        if(notifs.length === 0) html = '<div class="text-muted p-2">কোনো নোটিফিকেশন নেই।</div>';
        else {
            notifs.forEach(n => {
                html += `<div class="list-group-item bg-dark text-white border-secondary mb-1">
                    <small class="text-warning d-block">${n.timestamp}</small>
                    ${n.message}
                </div>`;
            });
        }
        document.getElementById('notifHistoryList').innerHTML = html;
    });
}

function verifyPinAndShowDeleted() {
    closeSidebar();
    let pin = prompt("এডমিন সিকিউরিটি পিন দিন (137955):");
    if(pin === '137955') {
        showSection('deleted');
    } else if(pin) {
        alert("ভুল সিকিউরিটি পিন!");
    }
}

function showSection(type) {
    document.getElementById('recordsSection').style.display = type === 'records' ? 'block' : 'none';
    if(document.getElementById('usersSection')) document.getElementById('usersSection').style.display = type === 'users' ? 'block' : 'none';
    if(document.getElementById('deletedRecordsSection')) document.getElementById('deletedRecordsSection').style.display = type === 'deleted' ? 'block' : 'none';
    if(document.getElementById('activitySection')) document.getElementById('activitySection').style.display = type === 'activity' ? 'block' : 'none';

    if(type === 'users') loadUsers();
    if(type === 'deleted') loadDeletedRecords();
    if(type === 'activity') loadActivityHistory();
    closeSidebar();
}

function closeSidebar() {
    let sidebar = document.getElementById('sidebarMenu');
    let bsOffcanvas = bootstrap.Offcanvas.getInstance(sidebar);
    if(bsOffcanvas) bsOffcanvas.hide();
}

function loadUsers() {
    fetch('/api/users')
    .then(res => res.json())
    .then(users => {
        let html = '';
        users.forEach(u => {
            let roleBadge = u[5] === 'main_admin' ? '<span class="badge bg-danger">Main Admin</span>' : (u[5] === 'admin' ? '<span class="badge bg-warning text-dark">Sub-Admin</span>' : '<span class="badge bg-info text-dark">User</span>');
            
            let actionBtn = '';
            if(u[2] !== 'Khushbu23') { // Main Admin Cannot Be Touched
                actionBtn = `<button class="btn btn-success btn-sm me-1" onclick="userAction(${u[0]}, 'approve')">Approve</button>
                             <button class="btn btn-warning btn-sm me-1" onclick="userAction(${u[0]}, 'block')">Block</button>
                             <button class="btn btn-danger btn-sm" onclick="userAction(${u[0]}, 'delete')">Delete</button>`;
            } else {
                actionBtn = `<small class="text-muted">সুরক্ষিত (Protected)</small>`;
            }

            html += `<tr>
                <td>${u[1]}</td><td>${u[2]}</td><td>${u[4]}</td><td>${roleBadge}</td>
                <td><span class="badge ${u[6]=='active'?'bg-success':'bg-danger'}">${u[6]}</span></td>
                <td>${actionBtn}</td>
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
    .then(res => res.json())
    .then(res => {
        if(res.status === 'error') alert(res.message);
        loadUsers();
    });
}

function loadDeletedRecords() {
    fetch('/api/deleted_records')
    .then(res => res.json())
    .then(recs => {
        let html = '';
        recs.forEach(r => {
            html += `<tr><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td><td>${r[4]}</td></tr>`;
        });
        document.getElementById('deletedTableBody').innerHTML = html;
    });
}

function loadActivityHistory() {
    fetch('/api/activity_logs')
    .then(res => res.json())
    .then(logs => {
        let html = '';
        logs.forEach(l => {
            html += `<tr><td>${l[3]}</td><td><strong>${l[1]}</strong></td><td>${l[2]}</td></tr>`;
        });
        document.getElementById('activityTableBody').innerHTML = html;
    });
}

function clearActivityHistory() {
    if(confirm("আপনি কি সমস্ত অ্যাক্টিভিটি হিস্ট্রি ডিলিট করতে চান?")) {
        fetch('/admin/clear_activity', { method: 'POST' })
        .then(() => loadActivityHistory());
    }
}

function openMessenger() {
    closeSidebar();
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
                html += `<div class="p-2 chat-user-item rounded mb-1 text-white" onclick="selectChatTarget('${u[2]}', '💬 ${u[1]} (${u[5]})')">
                            👤 ${u[1]} <small class="text-warning">(${u[2]})</small>
                         </div>`;
            }
        });
        if(document.getElementById('usersChatNav')) document.getElementById('usersChatNav').innerHTML = html;
    });
}

function selectChatTarget(target, name) {
    currentChatTarget = target;
    document.getElementById('activeChatHeader').innerText = name;
    loadMessages();
}

function updateFileName() {
    let file = document.getElementById('chatFile').files[0];
    if(file) document.getElementById('selectedFileName').innerText = "ফাইল: " + file.name;
}

function loadMessages() {
    fetch(`/api/messages?target=${currentChatTarget}`)
    .then(res => res.json())
    .then(msgs => {
        let html = '';
        msgs.forEach(m => {
            let isMe = m.sender === "{{ session.get('user', {}).get('username') }}";
            let mediaHtml = '';
            if(m.file_url) {
                if(m.file_url.endsWith('.mp4')) {
                    mediaHtml = `<video src="${m.file_url}" controls class="w-100 rounded mt-1"></video>`;
                } else {
                    mediaHtml = `<img src="${m.file_url}" class="img-fluid rounded mt-1" />`;
                }
            }
            html += `<div class="d-flex mb-2 ${isMe?'justify-content-end':'justify-content-start'}">
                <div class="${isMe?'chat-bubble-me':'chat-bubble-them'} p-2">
                    <small class="d-block fw-bold" style="font-size:10px;">${m.sender_name}</small>
                    ${m.message || ''}
                    ${mediaHtml}
                </div>
            </div>`;
        });
        let box = document.getElementById('chatMessagesBox');
        box.innerHTML = html;
        box.scrollTop = box.scrollHeight;
    });
}

function sendChatMsg() {
    let msg = document.getElementById('chatInputMsg').value;
    let fileInput = document.getElementById('chatFile');
    if(!msg && !fileInput.files[0]) return;

    let formData = new FormData();
    formData.append('message', msg);
    formData.append('target', currentChatTarget);
    if(fileInput.files[0]) formData.append('file', fileInput.files[0]);

    fetch('/send_message', { method: 'POST', body: formData })
    .then(() => {
        document.getElementById('chatInputMsg').value = '';
        fileInput.value = '';
        document.getElementById('selectedFileName').innerText = '';
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

function openAdminSecurityModal() { closeSidebar(); new bootstrap.Modal(document.getElementById('adminSecModal')).show(); }
function openDeleteModal(id) {
    document.getElementById('deleteForm').action = '/delete_record/' + id;
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}

if(document.getElementById('searchInput')) {
    loadRecords();
    setInterval(checkNotifications, 4000);
}
</script>
</body>
</html>
"""

# --- Server Routes ---

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
        if user[7] == 'pending':
            return "<script>alert('আপনার একাউন্টটি এখনও অনুমোদন করা হয়নি!'); window.location='/';</script>"
        elif user[7] == 'blocked':
            return "<script>alert('আপনার একাউন্টটি ব্লক করা হয়েছে!'); window.location='/';</script>"
        
        is_admin_or_sub = user[6] in ['main_admin', 'admin']
        session['user'] = {
            'id': user[0], 
            'name': user[1], 
            'username': user[2], 
            'role': user[6],
            'is_admin_or_sub': is_admin_or_sub
        }
        log_activity(user[2], "লগইন করেছেন")
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
        cursor.execute("INSERT INTO users (name, username, email, phone, password, role, status) VALUES (?, ?, ?, ?, ?, 'user', 'pending')",
                       (name, username, email, phone, hashed_pw))
        cursor.execute("INSERT INTO notifications (target_user, type, message) VALUES ('ADMIN', 'user_reg', ?)",
                       (f"নতুন ইউজার রেজিস্ট্রেশন: {name} ({username})",))
        conn.commit()
        conn.close()
        return "<script>alert('রেজিস্ট্রেশন সফল হয়েছে! এডমিন পারমিশন দিলে প্রবেশ করতে পারবেন।'); window.location='/';</script>"
    except:
        return "<script>alert('ইউজারনেম বা তথ্য আগে থেকেই ব্যবহৃত হচ্ছে!'); window.location='/';</script>"

@app.route('/admin/create_sub_admin', methods=['POST'])
def admin_create_sub_admin():
    if session.get('user', {}).get('role') != 'main_admin':
        return "<script>alert('কেবলমাত্র মূল এডমিন (Khushbu23) নতুন এডমিন বানাতে পারবেন!'); window.location='/';</script>"
    
    if request.form.get('security_code') != ADMIN_SECURITY_CODE:
        return "<script>alert('ভুল সিকিউরিটি পিন!'); window.location='/';</script>"

    hashed_pw = generate_password_hash(request.form['password'])
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, username, email, phone, password, role, status, added_by) VALUES (?, ?, ?, ?, ?, 'admin', 'active', ?)",
                   (request.form['name'], request.form['username'], request.form['email'], request.form['phone'], hashed_pw, session['user']['username']))
    conn.commit()
    conn.close()
    
    log_activity(session['user']['username'], f"নতুন এডমিন নিয়োগ করেছেন: {request.form['username']}")
    return "<script>alert('নতুন সাব-এডমিন সফলভাবে তৈরি হয়েছে!'); window.location='/';</script>"

@app.route('/admin/change_password', methods=['POST'])
def admin_change_password():
    if not session.get('user', {}).get('is_admin_or_sub'): return redirect(url_for('home'))
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
    if 'user' not in session: return jsonify({'status': 'error'})
    user_name = session['user']['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO phone_records (customer_name, mobile, service_type, connection_num, address, note, added_by) 
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                   (request.form['customer_name'], request.form.get('mobile', ''), request.form['service_type'],
                    request.form.get('connection_num', ''), request.form.get('address', ''), request.form.get('note', ''), user_name))
    conn.commit()
    conn.close()
    log_activity(user_name, f"নতুন নম্বর এড করেছেন: {request.form['customer_name']}")
    return jsonify({'status': 'success'})

@app.route('/delete_record/<int:id>', methods=['POST'])
def delete_record(id):
    if request.form.get('security_code') != ADMIN_SECURITY_CODE:
        return "<script>alert('সিকিউরিটি কোড ভুল!'); window.location='/';</script>"
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE phone_records SET is_deleted=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()
    log_activity(session['user']['username'], f"নম্বর আইডি {id} ডিলিট করেছেন")
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
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, phone, role, status FROM users WHERE is_deleted=0")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/api/deleted_records')
def api_deleted_records():
    if not session.get('user', {}).get('is_admin_or_sub'): return jsonify([])
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, mobile, service_type, connection_num FROM phone_records WHERE is_deleted=1")
    recs = cursor.fetchall()
    conn.close()
    return jsonify(recs)

@app.route('/api/activity_logs')
def api_activity_logs():
    if not session.get('user', {}).get('is_admin_or_sub'): return jsonify([])
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, action, timestamp FROM activity_logs ORDER BY id DESC LIMIT 50")
    logs = cursor.fetchall()
    conn.close()
    return jsonify(logs)

@app.route('/admin/clear_activity', methods=['POST'])
def clear_activity():
    if session.get('user', {}).get('role') != 'main_admin': return jsonify({'status': 'unauthorized'})
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activity_logs")
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
        f = request.files['file']
        if f.filename != '':
            os.makedirs('static/uploads', exist_ok=True)
            path = os.path.join('static/uploads', f.filename)
            f.save(path)
            file_url = '/' + path

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
        cursor.execute("""SELECT m.id, m.sender, u.name, m.message, m.file_url 
                          FROM messages m 
                          LEFT JOIN users u ON m.sender=u.username 
                          WHERE m.receiver='GROUP' 
                          ORDER BY m.id ASC""")
    else:
        cursor.execute("""SELECT m.id, m.sender, u.name, m.message, m.file_url 
                          FROM messages m 
                          LEFT JOIN users u ON m.sender=u.username 
                          WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?) 
                          ORDER BY m.id ASC""",
                       (curr_user, target, target, curr_user))
    raw = cursor.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'sender': r[1], 'sender_name': r[2] or r[1], 'message': r[3], 'file_url': r[4]} for r in raw])

@app.route('/api/notifications')
def api_notifications():
    if 'user' not in session: return jsonify([])
    curr_user = 'ADMIN' if session['user']['is_admin_or_sub'] else session['user']['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, message FROM notifications WHERE target_user=? AND is_read=0 ORDER BY id DESC", (curr_user,))
    notifs = cursor.fetchall()
    conn.close()
    return jsonify([{'id': n[0], 'message': n[1]} for n in notifs])

@app.route('/api/all_notifications')
def api_all_notifications():
    if 'user' not in session: return jsonify([])
    curr_user = 'ADMIN' if session['user']['is_admin_or_sub'] else session['user']['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, message, timestamp FROM notifications WHERE target_user=? ORDER BY id DESC LIMIT 20", (curr_user,))
    notifs = cursor.fetchall()
    conn.close()
    return jsonify([{'id': n[0], 'message': n[1], 'timestamp': n[2]} for n in notifs])

@app.route('/api/read_notif/<int:id>')
def read_notif(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET is_read=1 WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/admin/user_action/<int:id>/<string:action>', methods=['POST'])
def user_action(id, action):
    if not session.get('user', {}).get('is_admin_or_sub'): return jsonify({'status': 'unauthorized'})
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Check if target is Main Admin (Protected)
    cursor.execute("SELECT username, role FROM users WHERE id=?", (id,))
    target_user = cursor.fetchone()
    if target_user and target_user[0] == MAIN_ADMIN_USERNAME:
        conn.close()
        return jsonify({'status': 'error', 'message': 'মূল এডমিনকে ব্লক বা ডিলিট করা সম্ভব নয়!'})

    if action == 'approve':
        cursor.execute("UPDATE users SET status='active' WHERE id=?", (id,))
        log_activity(session['user']['username'], f"ইউজার এপ্রুভ করেছেন: {target_user[0]}")
    elif action in ['block', 'delete']:
        if request.form.get('security_code') != ADMIN_SECURITY_CODE:
            conn.close()
            return jsonify({'status': 'error', 'message': 'সিকিউরিটি পিন ভুল!'})
        
        if action == 'block':
            cursor.execute("UPDATE users SET status='blocked' WHERE id=?", (id,))
            log_activity(session['user']['username'], f"ইউজার/এডমিন ব্লক করেছেন: {target_user[0]}")
        elif action == 'delete':
            cursor.execute("UPDATE users SET is_deleted=1 WHERE id=?", (id,))
            log_activity(session['user']['username'], f"ইউজার/এডমিন স্থায়ীভাবে ডিলিট করেছেন: {target_user[0]}")

    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)