import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "btcl_kurigram_gold_pink_ultimate_2026")

MAIN_ADMIN_USERNAME = "Khushbu23"
SECURITY_DELETE_PASSWORD = "137955"
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
            raw_pass TEXT,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'pending',
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

    # Ensure Main Admin Khushbu23 exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (MAIN_ADMIN_USERNAME,))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("01751947523")
        cursor.execute('''INSERT INTO users (name, username, email, phone, password, raw_pass, role, status) 
                          VALUES (?, ?, ?, ?, ?, ?, 'main_admin', 'active')''',
                       ('Md Khushbu Alom', MAIN_ADMIN_USERNAME, 'admin@btcl.com', '01751947523', hashed_pw, '01751947523'))

    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম - Smart Control Desk & Messenger</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: linear-gradient(135deg, #2b001e 0%, #4a1525 50%, #1f0010 100%); color: #ffe6f2; font-family: 'Segoe UI', sans-serif; min-height: 100vh; padding-bottom: 70px; }
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
        .notification-badge { position: absolute; top: -5px; right: -5px; font-size: 11px; padding: 3px 7px; border-radius: 50%; background: #ff1493; color: white; font-weight: bold; }
        .chat-box { height: 380px; overflow-y: auto; background: #15030d; padding: 15px; border-radius: 8px; border: 1px solid #ff66b2; }
        .message-bubble { padding: 8px 12px; border-radius: 10px; margin-bottom: 8px; max-width: 75%; word-break: break-word; }
        .msg-incoming { background: #3b0d26; color: #fff; align-self: flex-start; }
        .msg-outgoing { background: #d4af37; color: #000; align-self: flex-end; margin-left: auto; }
        .clickable-name { color: #ffd700; cursor: pointer; text-decoration: underline; }
        .chat-file-preview { max-width: 150px; border-radius: 5px; margin-top: 5px; display: block; }
        .floating-add-btn { position: fixed; bottom: 25px; right: 25px; width: 65px; height: 65px; border-radius: 50%; background: linear-gradient(45deg, #d4af37, #ff66b2); color: #000; font-size: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(255,102,178,0.7); border: none; z-index: 1000; cursor: pointer; transition: 0.3s; }
        .floating-add-btn:hover { transform: scale(1.1); color: #fff; }
    </style>
</head>
<body>

<div class="gold-pink-header text-center py-2">
    <h3 class="m-0"><i class="fa-solid fa-phone-volume"></i> BTCL, কুড়িগ্রাম</h3>
    <small>Smart Management Portal & Messenger</small>
</div>

<div class="container py-3">
    {% if session.get('user') %}

    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div class="d-flex align-items-center gap-2 flex-wrap">
            <button class="btn btn-pink btn-sm" onclick="showHome()"><i class="fa-solid fa-house"></i> হোম</button>

            <div class="dropdown">
                <button class="btn btn-gold btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-bars"></i> মেনু অপশন
                </button>
                <ul class="dropdown-menu dropdown-menu-dark">
                    <li><a class="dropdown-item" href="#" onclick="openUserListModal()"><i class="fa-solid fa-users me-2"></i>ইউজার ও এডমিন তালিকা</a></li>
                    <li><a class="dropdown-item" href="#" onclick="openCreateUserModal()"><i class="fa-solid fa-user-plus me-2"></i>ইউজার এড করা</a></li>
                    {% if session.get('user').get('username') == 'Khushbu23' %}
                    <li><a class="dropdown-item text-warning" href="#" onclick="openAccountRequestsModal()"><i class="fa-solid fa-user-check me-2"></i>রেজিস্ট্রেশন রিকোয়েস্ট</a></li>
                    {% endif %}
                </ul>
            </div>
            
            <button class="btn btn-outline-warning btn-sm position-relative" onclick="openMessengerModal()">
                <i class="fa-solid fa-comments"></i> মেসেঞ্জার
                <span id="msgBadge" class="notification-badge" style="display:none;">0</span>
            </button>

            {% if session.get('user').get('username') == 'Khushbu23' %}
            <button class="btn btn-outline-danger btn-sm position-relative" onclick="openNotificationModal()">
                <i class="fa-solid fa-bell"></i> নোটিফিকেশন
                <span id="notifBadge" class="notification-badge" style="display:none;">0</span>
            </button>
            {% endif %}
        </div>
        
        <div class="d-flex align-items-center gap-2">
            <div class="dropdown">
                <button class="btn btn-gold btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-circle-user"></i> প্রোফাইল
                </button>
                <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                    <li><a class="dropdown-item" href="#" onclick="openProfileModal()"><i class="fa-solid fa-user-gear me-2"></i>প্রোফাইল আপডেট</a></li>
                    {% if session.get('user').get('username') == 'Khushbu23' %}
                    <li><a class="dropdown-item text-warning" href="#" onclick="openCreateAdminModal()"><i class="fa-solid fa-user-shield me-2"></i>এডমিন তৈরি (শুধুমাত্র মেইন এডমিন)</a></li>
                    <li><a class="dropdown-item text-warning" href="#" onclick="openAdminHistoryModal()"><i class="fa-solid fa-clock-rotate-left me-2"></i>এডমিন হিস্ট্রি ও অ্যাক্টিভিটি</a></li>
                    {% endif %}
                </ul>
            </div>

            {% if session.get('user').get('username') == 'Khushbu23' %}
            <div class="dropdown">
                <button class="btn btn-outline-light btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-ellipsis-vertical"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                    <li><a class="dropdown-item text-danger" href="#" onclick="openTrashBinModal()"><i class="fa-solid fa-trash-arrow-up me-2"></i>রিসাইকেল বিন / রিস্টোর</a></li>
                </ul>
            </div>
            {% endif %}

            <a href="/logout" class="btn btn-danger btn-sm"><i class="fa-solid fa-right-from-bracket"></i> লগআউট</a>
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
                    <option value="id_desc">সর্বশেষ যোগ করা নম্বর আগে (New to Old)</option>
                    <option value="id_asc">পুরাতন থেকে নতুন (1 to N - ছোট থেকে বড়)</option>
                    <option value="id_high_low">বড় সংখ্যা থেকে ছোট সংখ্যা (N to 1)</option>
                    <option value="name_asc">নাম অনুযায়ী (A to Z)</option>
                    <option value="name_desc">নাম অনুযায়ী (Z to A)</option>
                </select>
            </div>
        </div>
    </div>

    {% if session.get('user').get('role') in ['admin', 'main_admin'] %}
    <div class="row g-2 mb-3">
        <div class="col" onclick="filterService('')"><div class="stat-card"><div class="stat-number" id="countTotal">0</div><div style="font-size:12px; font-weight:bold;">সকল নম্বর</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন নাম্বার')"><div class="stat-card"><div class="stat-number" id="countTel">0</div><div style="font-size:12px; font-weight:bold;">টেলিফোন নাম্বার</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন+ওয়াইফাই নম্বর')"><div class="stat-card"><div class="stat-number" id="countBoth">0</div><div style="font-size:12px; font-weight:bold;">টেলিফোন+ওয়াইফাই</div></div></div>
        <div class="col" onclick="filterService('ওয়াইফাই নাম্বার')"><div class="stat-card"><div class="stat-number" id="countWifi">0</div><div style="font-size:12px; font-weight:bold;">ওয়াইফাই নাম্বার</div></div></div>
    </div>
    {% endif %}

    <div id="recordsSection" class="card-custom p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center border-bottom border-warning pb-2">
            <h5 class="text-warning mb-0"><i class="fa-solid fa-list"></i> গ্রাহক ও সংযোগ নম্বরসমূহ</h5>
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
                        <th>যুক্ত করেছেন</th>
                        {% if session.get('user').get('role') in ['admin', 'main_admin'] %}
                        <th>অ্যাকশন</th>
                        {% endif %}
                    </tr>
                </thead>
                <tbody id="recordsTableBody"></tbody>
            </table>
        </div>
    </div>

    <div id="userListSection" class="card-custom p-3 mb-4" style="display:none;">
        <div class="d-flex justify-content-between align-items-center border-bottom border-warning pb-2">
            <h5 class="text-warning mb-0"><i class="fa-solid fa-users"></i> রেজিস্টার্ড ইউজার ও এডমিন তালিকা</h5>
            <button class="btn btn-sm btn-outline-warning" onclick="showHome()">বন্ধ করুন</button>
        </div>
        <div class="table-responsive mt-2">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr><th>নাম</th><th>ইউজারনেম</th><th>জিমেইল</th><th>মোবাইল</th><th>পাসওয়ার্ড</th><th>রোল</th><th>স্ট্যাটাস</th><th>অ্যাকশন</th></tr>
                </thead>
                <tbody id="userTableBody"></tbody>
            </table>
        </div>
    </div>

    {% if session.get('user').get('role') in ['admin', 'main_admin'] %}
    <button class="floating-add-btn" onclick="openAddRecordModal()" title="নতুন নম্বর যোগ করুন">
        <i class="fa-solid fa-plus"></i>
    </button>
    {% endif %}

    {% else %}
    <div class="row justify-content-center mt-5">
        <div class="col-md-5">
            <div class="card-custom p-4 text-center shadow-lg">
                <h4 class="text-warning mb-3"><i class="fa-solid fa-lock"></i> লগইন করুন</h4>
                <form action="/login" method="POST">
                    <div class="mb-3 text-start"><label class="form-label">ইউজারনেম / জিমেইল / মোবাইল</label><input type="text" name="username" class="form-control" required></div>
                    <div class="mb-3 text-start"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
                    <button type="submit" class="btn btn-gold w-100 py-2">প্রবেশ করুন</button>
                </form>
                <div class="mt-3">
                    <button class="btn btn-outline-warning btn-sm" onclick="openRegisterModal()">নতুন অ্যাকাউন্ট রিকোয়েস্ট পাঠান</button>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>

<div class="modal fade" id="customerDetailsModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-id-card"></i> গ্রাহকের বিস্তারিত তথ্য</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body" id="customerDetailsBody"></div>
    </div>
  </div>
</div>

<div class="modal fade" id="adminDetailModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning" id="adminDetailModalTitle"><i class="fa-solid fa-user-shield"></i> এডমিন অ্যাক্টিভিটি রিপোর্ট</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body" id="adminDetailBody">
        <p class="text-muted text-center">লোড হচ্ছে...</p>
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="accountRequestsModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-check"></i> অ্যাকাউন্ট রেজিস্ট্রেশন রিকোয়েস্ট</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead><tr><th>নাম</th><th>ইউজারনেম</th><th>জিমেইল</th><th>মোবাইল</th><th>পাসওয়ার্ড</th><th>সময়</th><th>অ্যাকশন</th></tr></thead>
                <tbody id="requestTableBody"></tbody>
            </table>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="registerModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-plus"></i> অ্যাকাউন্ট রেজিস্ট্রেশন ফরম</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/api/register_request" method="POST" class="modal-body">
        <div class="mb-2"><label class="form-label">আপনার নাম</label><input type="text" name="name" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">জিমেইল (Gmail) *</label><input type="email" name="email" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">মোবাইল নম্বর</label><input type="text" name="phone" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
        <button type="submit" class="btn btn-gold w-100 py-2">রিকোয়েস্ট পাঠান</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="messengerModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-comments"></i> রিয়েল-টাইম মেসেঞ্জার (গ্রুপ ও ইনবক্স)</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="row">
            <div class="col-md-4 border-end border-warning">
                <div class="d-flex gap-1 mb-2">
                    <button class="btn btn-sm btn-gold w-50" onclick="switchChatTab('users')">ইউজার ইনবক্স</button>
                    <button class="btn btn-sm btn-pink w-50" onclick="switchChatTab('group')">গ্রুপ চ্যাট</button>
                </div>
                <div id="chatUserList" class="list-group list-group-flush bg-transparent" style="max-height: 380px; overflow-y: auto;"></div>
            </div>
            <div class="col-md-8 d-flex flex-column">
                <div id="activeChatTitle" class="text-warning fw-bold mb-2 pb-1 border-bottom border-warning">চ্যাট নির্বাচন করুন</div>
                <div id="chatMessages" class="chat-box d-flex flex-column mb-2">
                    <p class="text-muted text-center m-auto">মেসেজ দেখতে বা পাঠাতে বামপাশ থেকে ইউজার বা গ্রুপ সিলেক্ট করুন।</p>
                </div>
                <form id="chatForm" onsubmit="sendMessage(event)" class="input-group" style="display:none;">
                    <input type="text" id="chatInput" class="form-control" placeholder="একটি মেসেজ লিখুন...">
                    <input type="file" id="chatFile" class="d-none" onchange="previewFile()">
                    <button type="button" class="btn btn-outline-warning" onclick="document.getElementById('chatFile').click()"><i class="fa-solid fa-paperclip"></i></button>
                    <button type="submit" class="btn btn-gold"><i class="fa-solid fa-paper-plane"></i></button>
                </form>
                <div id="selectedFilePreview" class="small text-warning mt-1" style="display:none;"></div>
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
        <h5 class="modal-title text-warning"><i class="fa-solid fa-bell"></i> নোটিফিকেশন ও রিকোয়েস্ট</h5>
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
                <option value="টেলিফোন নাম্বার">টেলিফোন নাম্বার</option>
                <option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই নম্বর</option>
                <option value="ওয়াইফাই নাম্বার">ওয়াইফাই নাম্বার</option>
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
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-plus"></i> ইউজার বা এডমিন তৈরি করুন</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/api/create_user" method="POST" class="modal-body">
        <div class="mb-2"><label class="form-label">নাম</label><input type="text" name="name" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">জিমেইল</label><input type="email" name="email" class="form-control"></div>
        <div class="mb-2"><label class="form-label">মোবাইল</label><input type="text" name="phone" class="form-control"></div>
        <div class="mb-2"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
        <div class="mb-3">
            <label class="form-label">রোল</label>
            <select name="role" class="form-select">
                <option value="user">সাধারণ ইউজার</option>
                <option value="admin">সাব-এডমিন</option>
            </select>
        </div>
        <button type="submit" class="btn btn-gold w-100 py-2">তৈরি করুন</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="editUserModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-pen"></i> ইউজার/এডমিন তথ্য পরিবর্তন</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/api/update_user_credentials" method="POST" class="modal-body">
        <input type="hidden" id="edit_user_id" name="user_id">
        <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" id="edit_username" name="username" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">নতুন পাসওয়ার্ড</label><input type="text" id="edit_password" name="password" class="form-control" placeholder="নতুন পাসওয়ার্ড দিন" required></div>
        <button type="submit" class="btn btn-gold w-100 py-2">পরিবর্তন সেভ করুন</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="adminHistoryModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-clock-rotate-left"></i> এডমিন হিস্ট্রি ও সার্বিক পরিসংখ্যান</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr><th>এডমিন নাম</th><th>ইউজারনেম</th><th>সক্রিয় সময়</th><th>ইউজার যোগ</th><th>নম্বর যোগ</th></tr>
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
        <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" value="{{ session.get('user',{}).get('username') }}" required></div>
        <div class="mb-2"><label class="form-label">আপনার নাম</label><input type="text" name="name" class="form-control" value="{{ session.get('user',{}).get('name') }}" required></div>
        <div class="mb-2"><label class="form-label">জিমেইল</label><input type="email" name="email" class="form-control" value="{{ session.get('user',{}).get('email', '') }}"></div>
        <div class="mb-2"><label class="form-label">মোবাইল নম্বর</label><input type="text" name="phone" class="form-control" value="{{ session.get('user',{}).get('phone') }}"></div>
        <div class="mb-3"><label class="form-label">নতুন পাসওয়ার্ড</label><input type="password" name="password" class="form-control" placeholder="নতুন পাসওয়ার্ড"></div>
        <button type="submit" class="btn btn-gold w-100 py-2">সেভ করুন</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="trashBinModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-warning d-flex justify-content-between">
        <h5 class="modal-title text-danger"><i class="fa-solid fa-trash-arrow-up"></i> রিসাইকেল বিন (রিস্টোর অপশন)</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead><tr><th>গ্রাহকের নাম</th><th>সংযোগ নম্বর</th><th>অ্যাকশন</th></tr></thead>
                <tbody id="trashTableBody"></tbody>
            </table>
        </div>
      </div>
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
    activeServiceFilter = '';
    document.getElementById('currentFilterLabel').innerText = 'সকল নম্বর';
    if(document.getElementById('searchInput')) document.getElementById('searchInput').value = '';
    loadRecords();
}

function filterService(service) {
    activeServiceFilter = service;
    document.getElementById('currentFilterLabel').innerText = service || 'সকল নম্বর';
    loadRecords();
}

function loadRecords() {
    let q = document.getElementById('searchInput') ? document.getElementById('searchInput').value : '';
    let sort = document.getElementById('sortSelect') ? document.getElementById('sortSelect').value : 'id_desc';
    
    fetch(`/api/search?q=${q}&service=${encodeURIComponent(activeServiceFilter)}&sort=${sort}`)
    .then(res => res.json())
    .then(data => {
        let html = '';
        let isAdmin = data.is_admin;
        
        data.records.forEach((row, idx) => {
            let displayIndex = (sort === 'id_asc') ? (idx + 1) : (data.records.length - idx);
            if (sort === 'id_high_low') {
                displayIndex = idx + 1;
            }
            
            let actionTd = isAdmin ? `
                <td>
                    <button class="btn btn-warning btn-sm me-1" onclick="openEditRecordModal(${row[0]})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="deleteRecord(${row[0]})"><i class="fa-solid fa-trash"></i></button>
                </td>` : '';

            html += `<tr>
                <td><strong>${displayIndex}</strong></td>
                <td><span class="clickable-name" onclick="openCustomerDetails(${row[0]})">${row[1]}</span></td>
                <td>${row[2] || '-'}</td>
                <td><span class="badge bg-warning text-dark">${row[3]}</span></td>
                <td>${row[4] || '-'}</td>
                <td>${row[5] || '-'}</td>
                <td><span class="badge bg-info text-dark">${row[7] || 'Khushbu23'}</span></td>
                ${actionTd}
            </tr>`;
        });
        if(document.getElementById('recordsTableBody')) document.getElementById('recordsTableBody').innerHTML = html;
        
        if(document.getElementById('countTotal')) document.getElementById('countTotal').innerText = data.counts.total;
        if(document.getElementById('countTel')) document.getElementById('countTel').innerText = data.counts.tel;
        if(document.getElementById('countBoth')) document.getElementById('countBoth').innerText = data.counts.both;
        if(document.getElementById('countWifi')) document.getElementById('countWifi').innerText = data.counts.wifi;
    });
}

function openCustomerDetails(id) {
    fetch(`/api/get_record?id=${id}`)
    .then(res => res.json())
    .then(data => {
        let html = `
            <p><strong>গ্রাহকের নাম:</strong> <span class="text-warning">${data.customer_name}</span></p>
            <p><strong>মোবাইল নম্বর:</strong> ${data.mobile || '-'}</p>
            <p><strong>সেবার ধরন:</strong> ${data.service_type}</p>
            <p><strong>সংযোগ নম্বর:</strong> ${data.connection_num || '-'}</p>
            <p><strong>ঠিকানা:</strong> ${data.address || '-'}</p>
            <p><strong>নোট:</strong> ${data.note || '-'}</p>
            <p><strong>যুক্ত করেছেন:</strong> <span class="badge bg-info text-dark">${data.added_by}</span></p>
        `;
        document.getElementById('customerDetailsBody').innerHTML = html;
        new bootstrap.Modal(document.getElementById('customerDetailsModal')).show();
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

function openAccountRequestsModal() {
    new bootstrap.Modal(document.getElementById('accountRequestsModal')).show();
    fetch('/api/account_requests')
    .then(res => res.json())
    .then(data => {
        let html = '';
        if(data.length === 0) {
            html = '<tr><td colspan="7" class="text-center text-muted">কোনো রিকোয়েস্ট নেই।</td></tr>';
        } else {
            data.forEach(u => {
                html += `<tr>
                    <td>${u.name}</td>
                    <td>${u.username}</td>
                    <td>${u.email || '-'}</td>
                    <td>${u.phone || '-'}</td>
                    <td><span class="text-warning">${u.raw_pass || '-'}</span></td>
                    <td>${u.created_at}</td>
                    <td>
                        <button class="btn btn-success btn-sm me-1" onclick="approveUser(${u.id})">গ্রহণ</button>
                        <button class="btn btn-danger btn-sm" onclick="rejectUser(${u.id})">বাতিল</button>
                    </td>
                </tr>`;
            });
        }
        document.getElementById('requestTableBody').innerHTML = html;
    });
}

function approveUser(id) {
    fetch(`/api/approve_user?id=${id}`).then(() => openAccountRequestsModal());
}

function rejectUser(id) {
    fetch(`/api/reject_user?id=${id}`).then(() => openAccountRequestsModal());
}

function openRegisterModal() {
    new bootstrap.Modal(document.getElementById('registerModal')).show();
}

function openUserListModal() {
    document.getElementById('recordsSection').style.display = 'none';
    document.getElementById('userListSection').style.display = 'block';
    
    fetch('/api/users_list')
    .then(res => res.json())
    .then(data => {
        let users = data.users;
        let isMainAdmin = data.is_main_admin;
        let html = '';
        users.forEach(u => {
            let roleBadge = u.role === 'main_admin' ? '<span class="badge bg-danger">মেইন এডমিন (Khushbu23)</span>' : (u.role === 'admin' ? '<span class="badge bg-warning text-dark">সাব-এডমিন</span>' : '<span class="badge bg-secondary">সাধারণ ইউজার</span>');
            
            let actionTd = '';
            if(isMainAdmin && u.username !== 'Khushbu23') {
                actionTd = `<td>
                    <button class="btn btn-info btn-sm me-1" onclick="openEditUserModal(${u.id}, '${u.username}')" title="ইউজারনেম বা পাসওয়ার্ড বদলান"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="deleteUser(${u.id})" title="মুছে ফেলুন"><i class="fa-solid fa-trash"></i></button>
                </td>`;
            } else {
                actionTd = `<td>-</td>`;
            }

            html += `<tr>
                <td>${u.name}</td>
                <td>${u.username}</td>
                <td>${u.email || '-'}</td>
                <td>${u.phone || '-'}</td>
                <td><span class="text-warning">${u.raw_pass || '******'}</span></td>
                <td>${roleBadge}</td>
                <td><span class="badge bg-success">${u.status}</span></td>
                ${actionTd}
            </tr>`;
        });
        document.getElementById('userTableBody').innerHTML = html;
    });
}

function openEditUserModal(id, username) {
    document.getElementById('edit_user_id').value = id;
    document.getElementById('edit_username').value = username;
    document.getElementById('edit_password').value = '';
    new bootstrap.Modal(document.getElementById('editUserModal')).show();
}

function deleteUser(id) {
    let pin = prompt("সিকিউরিটি পাসওয়ার্ড (137955) দিন:");
    if(pin) {
        fetch(`/api/delete_user?id=${id}&pin=${pin}`)
        .then(res => res.json())
        .then(res => {
            if(res.status === 'success') {
                alert('সফলভাবে মুছে ফেলা হয়েছে!');
                openUserListModal();
            } else {
                alert('ভুল সিকিউরিটি পাসওয়ার্ড!');
            }
        });
    }
}

function openTrashBinModal() {
    new bootstrap.Modal(document.getElementById('trashBinModal')).show();
    fetch('/api/trash_records')
    .then(res => res.json())
    .then(data => {
        let html = '';
        if(data.length === 0) {
            html = '<tr><td colspan="3" class="text-center text-muted">রিসাইকেল বিন খালি।</td></tr>';
        } else {
            data.forEach(r => {
                html += `<tr>
                    <td>${r.customer_name}</td>
                    <td>${r.connection_num || '-'}</td>
                    <td><button class="btn btn-success btn-sm" onclick="restoreRecord(${r.id})">রিস্টোর করুন</button></td>
                </tr>`;
            });
        }
        document.getElementById('trashTableBody').innerHTML = html;
    });
}

function restoreRecord(id) {
    let pin = prompt("সিকিউরিটি পাসওয়ার্ড (137955) দিন:");
    if(pin) {
        fetch(`/api/restore_record?id=${id}&pin=${pin}`)
        .then(res => res.json())
        .then(res => {
            if(res.status === 'success') {
                alert('সফলভাবে রিস্টোর হয়েছে!');
                openTrashBinModal();
                loadRecords();
            } else {
                alert('ভুল সিকিউরিটি পাসওয়ার্ড!');
            }
        });
    }
}

function openAdminHistoryModal() {
    new bootstrap.Modal(document.getElementById('adminHistoryModal')).show();
    fetch('/api/admin_history')
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.forEach(h => {
            html += `<tr>
                <td><span class="clickable-name fw-bold" onclick="openAdminDetail('${h.username}', '${h.name}')">${h.name}</span></td>
                <td>${h.username}</td>
                <td><span class="text-warning">${h.active_minutes} মিনিট</span></td>
                <td><span class="badge bg-primary">${h.users_added} জন</span></td>
                <td><span class="badge bg-success">${h.records_added} টি</span></td>
            </tr>`;
        });
        document.getElementById('adminHistoryTableBody').innerHTML = html;
    });
}

function openAdminDetail(username, name) {
    document.getElementById('adminDetailModalTitle').innerText = `এডমিন বিস্তারিত: ${name} (${username})`;
    new bootstrap.Modal(document.getElementById('adminDetailModal')).show();
    
    fetch(`/api/admin_detail_report?username=${username}`)
    .then(res => res.json())
    .then(data => {
        let recHtml = '<h6 class="text-warning mt-2">যোগ করা নম্বরসমূহ:</h6><ul class="list-group list-group-dark mb-3">';
        if(data.records.length === 0) recHtml += '<li class="list-group-item bg-dark text-muted">কোনো নম্বর যোগ করেনি।</li>';
        else data.records.forEach(r => { recHtml += `<li class="list-group-item bg-dark text-white border-warning">নাম: <strong>${r.customer_name}</strong> | নম্বর: ${r.connection_num || '-'} | তারিখ: ${r.created_at}</li>`; });
        recHtml += '</ul>';

        let msgHtml = '<h6 class="text-warning mt-2">সাম্প্রতিক চ্যাট ও মেসেজসমূহ:</h6><ul class="list-group list-group-dark">';
        if(data.messages.length === 0) msgHtml += '<li class="list-group-item bg-dark text-muted">কোনো মেসেজ নেই।</li>';
        else data.messages.forEach(m => { msgHtml += `<li class="list-group-item bg-dark text-white border-warning">কাকে/গ্রুপে: <strong>${m.receiver}</strong> | মেসেজ: ${m.message || '[ফাইল]'} | সময়: ${m.timestamp}</li>`; });
        msgHtml += '</ul>';

        document.getElementById('adminDetailBody').innerHTML = recHtml + msgHtml;
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
                    let roleTag = u.is_admin ? '<span class="badge bg-warning text-dark ms-1">এডমিন</span>' : '';
                    html += `<a href="#" class="list-group-item list-group-item-action bg-dark text-white border-warning mb-1 rounded d-flex justify-content-between align-items-center" onclick="selectChatUser('${u.username}', '${u.name}', 0)">
                        <div>
                            <div><strong>${u.name}</strong> ${roleTag}</div>
                            <div class="text-muted small">${u.last_msg || 'চ্যাট শুরু করুন'}</div>
                        </div>
                        ${badgeHtml}
                    </a>`;
                });
            }
            listEl.innerHTML = html;
        });
    } else {
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

function previewFile() {
    let fileInput = document.getElementById('chatFile');
    let previewEl = document.getElementById('selectedFilePreview');
    if(fileInput.files.length > 0) {
        previewEl.style.display = 'block';
        previewEl.innerText = `সংযুক্ত ফাইল: ${fileInput.files[0].name}`;
    } else {
        previewEl.style.display = 'none';
    }
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
                let senderName = !m.is_mine && currentChatIsGroup ? `<div class="small text-warning fw-bold mb-1">${m.sender_display}</div>` : '';
                
                let fileContent = '';
                if(m.file_url) {
                    if(m.file_url.match(/\.(jpeg|jpg|gif|png)$/i)) {
                        fileContent = `<a href="${m.file_url}" target="_blank"><img src="${m.file_url}" class="chat-file-preview"></a>`;
                    } else {
                        fileContent = `<div class="mt-1"><a href="${m.file_url}" target="_blank" class="btn btn-sm btn-outline-light"><i class="fa-solid fa-download me-1"></i>ফাইল ডাউনলোড</a></div>`;
                    }
                }

                html += `<div class="message-bubble ${bubbleClass}">
                    ${senderName}
                    <div>${m.message || ''}</div>
                    ${fileContent}
                    <div style="font-size: 9px; opacity: 0.7; text-align: right; margin-top: 3px;">${m.timestamp}</div>
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
    let fileInput = document.getElementById('chatFile');
    
    if(!text.trim() && fileInput.files.length === 0) return;

    let formData = new FormData();
    formData.append('receiver', currentChatTarget);
    formData.append('message', text);
    formData.append('is_group', currentChatIsGroup);
    if(fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
    }

    fetch('/api/chat/send', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(res => {
        if(res.status === 'success') {
            document.getElementById('chatInput').value = '';
            fileInput.value = '';
            document.getElementById('selectedFilePreview').style.display = 'none';
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
                        <h6 class="mb-1 text-warning">${n.sender_display} ${n.is_group ? '(গ্রুপ)' : ''}</h6>
                        <small>${n.timestamp}</small>
                    </div>
                    <p class="mb-1">${n.message || '[ফাইল/ছবি]'}</p>
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
            msgBadge.style.display = data.msg_count > 0 ? 'inline-block' : 'none';
            msgBadge.innerText = data.msg_count;
        }
        if(notifBadge) {
            notifBadge.style.display = data.notif_count > 0 ? 'inline-block' : 'none';
            notifBadge.innerText = data.notif_count;
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
    let pin = prompt("সিকিউরিটি পাসওয়ার্ড (137955) দিন:");
    if(pin) {
        fetch(`/api/delete_record?id=${id}&pin=${pin}`)
        .then(res => res.json())
        .then(res => {
            if(res.status === 'success') {
                loadRecords();
            } else {
                alert('ভুল সিকিউরিটি পাসওয়ার্ড!');
            }
        });
    }
}

function openProfileModal() {
    new bootstrap.Modal(document.getElementById('profileModal')).show();
}

if(document.getElementById('searchInput')) {
    loadRecords();
    setInterval(checkNotifications, 7000);
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
    cursor.execute("SELECT * FROM users WHERE (username = ? OR email = ? OR phone = ?) AND is_deleted=0", (username, username, username))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[5], password):
        if user[8] != 'active':
            return "<script>alert('আপনার অ্যাকাউন্টটি এখনো মেইন এডমিন কর্তৃক অনুমোদিত হয়নি!'); window.location='/';</script>"
        session['user'] = {
            'id': user[0], 
            'name': user[1], 
            'username': user[2], 
            'email': user[3],
            'phone': user[4],
            'role': user[7],
            'profile_pic': user[9]
        }
        return redirect(url_for('home'))
    return "<script>alert('ভুল তথ্য বা অ্যাকাউন্ট অনুমোদিত নয়!'); window.location='/';</script>"

@app.route('/api/register_request', methods=['POST'])
def register_request():
    name = request.form.get('name')
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    raw_password = request.form.get('password')
    password = generate_password_hash(raw_password)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO users (name, username, email, phone, password, raw_pass, role, status) 
                          VALUES (?, ?, ?, ?, ?, ?, 'user', 'pending')""", 
                       (name, username, email, phone, password, raw_password))
        conn.commit()
    except:
        pass
    conn.close()
    return "<script>alert('আপনার রেজিস্ট্রেশন রিকোয়েস্ট সফলভাবে পাঠানো হয়েছে। এডমিন অ্যাপ্রুভ করলে লগইন করতে পারবেন।'); window.location='/';</script>"

@app.route('/api/account_requests')
def account_requests():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME: return jsonify([])
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, phone, raw_pass, created_at FROM users WHERE status='pending' AND is_deleted=0")
    rows = cursor.fetchall()
    conn.close()
    reqs = [{'id': r[0], 'name': r[1], 'username': r[2], 'email': r[3], 'phone': r[4], 'raw_pass': r[5], 'created_at': r[6]} for r in rows]
    return jsonify(reqs)

@app.route('/api/approve_user')
def approve_user():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME: return jsonify({'status': 'unauthorized'})
    user_id = request.args.get('id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status='active' WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/reject_user')
def reject_user():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME: return jsonify({'status': 'unauthorized'})
    user_id = request.args.get('id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_deleted=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/search')
def api_search():
    if 'user' not in session: return jsonify({'records': [], 'counts': {}})
    
    current_role = session['user']['role']
    is_admin = current_role in ['admin', 'main_admin']

    q = request.args.get('q', '')
    service = request.args.get('service', '')
    sort = request.args.get('sort', 'id_desc')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    order_sql = "ORDER BY id DESC"
    if sort == 'id_asc': order_sql = "ORDER BY id ASC"
    elif sort == 'id_high_low': order_sql = "ORDER BY id DESC"
    elif sort == 'name_asc': order_sql = "ORDER BY customer_name ASC"
    elif sort == 'name_desc': order_sql = "ORDER BY customer_name DESC"

    query = "SELECT id, customer_name, mobile, service_type, connection_num, address, note, added_by FROM phone_records WHERE is_deleted=0"
    params = []

    if q:
        query += " AND (customer_name LIKE ? OR mobile LIKE ? OR connection_num LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])

    if service and is_admin:
        query += " AND service_type = ?"
        params.append(service)

    query += f" {order_sql}"
    cursor.execute(query, params)
    records = cursor.fetchall()

    total = tel = both = wifi = 0
    if is_admin:
        cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type='টেলিফোন নাম্বার'")
        tel = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type='টেলিফোন+ওয়াইফাই নম্বর'")
        both = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type='ওয়াইফাই নাম্বার'")
        wifi = cursor.fetchone()[0]

    conn.close()
    return jsonify({
        'records': records,
        'is_admin': is_admin,
        'counts': {'total': total, 'tel': tel, 'both': both, 'wifi': wifi}
    })

# --- CHAT & NOTIFICATION APIS ---

@app.route('/api/chat/users')
def chat_users():
    if 'user' not in session: return jsonify([])
    current_user = session['user']['username']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, role FROM users WHERE username != ? AND is_deleted=0 AND status='active'", (current_user,))
    users = cursor.fetchall()
    
    result = []
    for u in users:
        u_username, u_name, u_role = u[0], u[1], u[2]
        is_admin = u_role in ('admin', 'main_admin')
        
        cursor.execute("SELECT COUNT(*) FROM messages WHERE sender = ? AND receiver = ? AND is_group = 0 AND is_read = 0", (u_username, current_user))
        unread = cursor.fetchone()[0]
        
        cursor.execute("SELECT message, sender FROM messages WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?) AND is_group = 0 ORDER BY id DESC LIMIT 1", (u_username, current_user, current_user, u_username))
        last_m = cursor.fetchone()
        
        last_msg_text = last_m[0] if last_m and last_m[0] else ('[ফাইল]' if last_m else 'চ্যাট শুরু করুন')
        
        result.append({
            'username': u_username,
            'name': u_name,
            'is_admin': is_admin,
            'unread': unread,
            'last_msg': last_msg_text
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
        cursor.execute("SELECT sender, message, file_url, timestamp FROM messages WHERE is_group = 1 ORDER BY id ASC")
    else:
        cursor.execute("""SELECT sender, message, file_url, timestamp FROM messages 
                          WHERE is_group = 0 AND ((sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)) 
                          ORDER BY id ASC""", (current_user, target, target, current_user))
        cursor.execute("UPDATE messages SET is_read = 1 WHERE sender = ? AND receiver = ? AND is_group = 0", (target, current_user))
        conn.commit()
        
    rows = cursor.fetchall()
    
    messages = []
    for r in rows:
        sender_username = r[0]
        cursor.execute("SELECT role FROM users WHERE username=?", (sender_username,))
        u_role_row = cursor.fetchone()
        is_sender_admin = u_role_row and u_role_row[0] in ('admin', 'main_admin')
        sender_display = "রিয়েল এডমিন" if is_sender_admin else sender_username
        
        messages.append({
            'sender': sender_username,
            'sender_display': sender_display,
            'message': r[1],
            'file_url': r[2],
            'timestamp': r[3],
            'is_mine': sender_username == current_user
        })
    conn.close()
    return jsonify(messages)

@app.route('/api/chat/send', methods=['POST'])
def chat_send():
    if 'user' not in session: return jsonify({'status': 'unauthorized'})
    current_user = session['user']['username']
    receiver = request.form.get('receiver')
    message = request.form.get('message', '')
    is_group = int(request.form.get('is_group', 0))
    
    file_url = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
            file_url = f"/static/uploads/{unique_filename}"
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""INSERT INTO messages (sender, receiver, message, file_url, is_group, is_read) 
                      VALUES (?, ?, ?, ?, ?, 0)""", (current_user, receiver, message, file_url, is_group))
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
    
    req_count = 0
    if username == MAIN_ADMIN_USERNAME:
        cursor.execute("SELECT COUNT(*) FROM users WHERE status='pending' AND is_deleted=0")
        req_count = cursor.fetchone()[0]
        
    conn.close()
    total_notif = msg_count + req_count
    return jsonify({'msg_count': msg_count, 'notif_count': total_notif})

@app.route('/api/notifications')
def notifications():
    if 'user' not in session: return jsonify([])
    username = session['user']['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    notifs = []
    if username == MAIN_ADMIN_USERNAME:
        cursor.execute("SELECT id, name, username, created_at FROM users WHERE status='pending' AND is_deleted=0")
        pending_users = cursor.fetchall()
        for pu in pending_users:
            notifs.append({
                'sender': pu[2],
                'sender_display': f"নতুন অ্যাকাউন্ট রিকোয়েস্ট: {pu[1]}",
                'message': "অ্যাকাউন্ট অনুমোদন করতে ক্লিক করুন",
                'timestamp': pu[3],
                'is_group': 0,
                'is_request': True
            })

    cursor.execute("SELECT sender, message, timestamp, is_group FROM messages WHERE receiver = ? AND is_read = 0 ORDER BY id DESC LIMIT 20", (username,))
    rows = cursor.fetchall()
    
    for r in rows:
        s_username = r[0]
        cursor.execute("SELECT role FROM users WHERE username=?", (s_username,))
        u_role_row = cursor.fetchone()
        is_s_admin = u_role_row and u_role_row[0] in ('admin', 'main_admin')
        s_display = "রিয়েল এডমিন" if is_s_admin else s_username
        
        notifs.append({
            'sender': s_username, 
            'sender_display': s_display, 
            'message': r[1] or '[ফাইল/ছবি]', 
            'timestamp': r[2], 
            'is_group': r[3],
            'is_request': False
        })
        
    conn.close()
    return jsonify(notifs)

@app.route('/api/save_record', methods=['POST'])
def save_record():
    if 'user' not in session or session['user']['role'] not in ['admin', 'main_admin']: 
        return jsonify({'status': 'unauthorized'})
        
    rec_id = request.form.get('id')
    name = request.form.get('customer_name')
    mobile = request.form.get('mobile')
    service = request.form.get('service_type')
    conn_num = request.form.get('connection_num')
    address = request.form.get('address')
    note = request.form.get('note')
    current_user = session['user']['username']

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
    role_to_create = request.form.get('role', 'user')
    
    # Only Real / Main Admin can create admins
    if role_to_create in ('admin', 'main_admin') and session['user']['username'] != MAIN_ADMIN_USERNAME:
        return "<script>alert('শুধুমাত্র রিয়েল এডমিন (Khushbu23) নতুন এডমিন তৈরি করতে পারবেন!'); window.location='/';</script>"

    name = request.form.get('name')
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    raw_password = request.form.get('password')
    password = generate_password_hash(raw_password)
    current_user = session['user']['username']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO users (name, username, email, phone, password, raw_pass, role, added_by, status) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active')""", 
                       (name, username, email, phone, password, raw_password, role_to_create, current_user))
        conn.commit()
    except:
        pass
    conn.close()
    return "<script>alert('ইউজার সফলভাবে তৈরি করা হয়েছে!'); window.location='/';</script>"

@app.route('/api/update_user_credentials', methods=['POST'])
def update_user_credentials():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return "<script>alertঅনুমোদিত নয়!'); window.location='/';</script>"
    
    user_id = request.form.get('user_id')
    new_username = request.form.get('username')
    new_raw_pass = request.form.get('password')
    new_hashed_pass = generate_password_hash(new_raw_pass)

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET username=?, password=?, raw_pass=? WHERE id=?", (new_username, new_hashed_pass, new_raw_pass, user_id))
    conn.commit()
    conn.close()
    return "<script>alert('ইউজারনেম ও পাসওয়ার্ড সফলভাবে আপডেট করা হয়েছে!'); window.location='/';</script>"

@app.route('/api/users_list')
def users_list():
    if 'user' not in session: return jsonify({'users': [], 'is_main_admin': False})
    is_main_admin = session['user']['username'] == MAIN_ADMIN_USERNAME
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, phone, raw_pass, role, status FROM users WHERE is_deleted=0")
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    for r in rows:
        users.append({
            'id': r[0], 
            'name': r[1], 
            'username': r[2], 
            'email': r[3], 
            'phone': r[4], 
            'raw_pass': r[5] if is_main_admin else '******', 
            'role': r[6], 
            'status': r[7]
        })
    return jsonify({'users': users, 'is_main_admin': is_main_admin})

@app.route('/api/delete_user')
def delete_user():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return jsonify({'status': 'unauthorized'})
        
    user_id = request.args.get('id')
    pin = request.args.get('pin')
    if pin != SECURITY_DELETE_PASSWORD:
        return jsonify({'status': 'error', 'message': 'wrong pin'})
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_deleted=1 WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/trash_records')
def trash_records():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME: return jsonify([])
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, connection_num FROM phone_records WHERE is_deleted=1")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'customer_name': r[1], 'connection_num': r[2]} for r in rows])

@app.route('/api/restore_record')
def restore_record():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME: return jsonify({'status': 'unauthorized'})
    rec_id = request.args.get('id')
    pin = request.args.get('pin')
    if pin != SECURITY_DELETE_PASSWORD:
        return jsonify({'status': 'error'})
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE phone_records SET is_deleted=0 WHERE id=?", (rec_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/admin_history')
def admin_history():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME: return jsonify([])
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

@app.route('/api/admin_detail_report')
def admin_detail_report():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME: return jsonify({})
    username = request.args.get('username')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT customer_name, connection_num, created_at FROM phone_records WHERE added_by=? AND is_deleted=0 ORDER BY id DESC LIMIT 30", (username,))
    rec_rows = cursor.fetchall()
    records = [{'customer_name': r[0], 'connection_num': r[1], 'created_at': r[2]} for r in rec_rows]

    cursor.execute("SELECT receiver, message, timestamp FROM messages WHERE sender=? ORDER BY id DESC LIMIT 30", (username,))
    msg_rows = cursor.fetchall()
    messages = [{'receiver': m[0], 'message': m[1], 'timestamp': m[2]} for m in msg_rows]

    conn.close()
    return jsonify({'records': records, 'messages': messages})

@app.route('/api/get_record')
def get_record():
    rec_id = request.args.get('id')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, mobile, service_type, connection_num, address, note, added_by FROM phone_records WHERE id=?", (rec_id,))
    row = cursor.fetchone()
    conn.close()
    return jsonify({'id': row[0], 'customer_name': row[1], 'mobile': row[2], 'service_type': row[3], 'connection_num': row[4], 'address': row[5], 'note': row[6], 'added_by': row[7]})

@app.route('/api/delete_record')
def delete_record():
    if 'user' not in session or session['user']['role'] not in ['admin', 'main_admin']: 
        return jsonify({'status': 'unauthorized'})
        
    rec_id = request.args.get('id')
    pin = request.args.get('pin')
    if pin != SECURITY_DELETE_PASSWORD:
        return jsonify({'status': 'error'})
    
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
    username = request.form.get('username')
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if password and password.strip() != "":
        hashed = generate_password_hash(password)
        cursor.execute("UPDATE users SET username=?, name=?, email=?, phone=?, password=?, raw_pass=? WHERE id=?", (username, name, email, phone, hashed, password, user_id))
    else:
        cursor.execute("UPDATE users SET username=?, name=?, email=?, phone=? WHERE id=?", (username, name, email, phone, user_id))
        
    session['user']['username'] = username
    session['user']['name'] = name
    session['user']['email'] = email
    session['user']['phone'] = phone
    conn.commit()
    conn.close()
    return "<script>alert('ಪ್ರೊফাইল তথ্য সফলভাবে আপডেট করা হয়েছে!'); window.location='/';</script>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)