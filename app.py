import os
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "btcl_kurigram_green_vibrant_pro_2026")

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
            record_image TEXT DEFAULT '',
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
    <title>BTCL, কুড়িগ্রাম - Smart Control Desk & Messenger</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background: linear-gradient(135deg, #052e16 0%, #064e3b 50%, #022c22 100%); color: #ecfdf5; font-family: 'Segoe UI', sans-serif; min-height: 100vh; padding-bottom: 70px; }
        .green-vibrant-header { background: linear-gradient(90deg, #10b981 0%, #34d399 50%, #059669 100%); color: #022c22; font-weight: bold; box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4); }
        .card-custom { background: rgba(6, 78, 59, 0.95); border: 1px solid #34d399; border-radius: 12px; box-shadow: 0 4px 20px rgba(52, 211, 153, 0.15); }
        .form-label { color: #a7f3d0; font-weight: bold; }
        .form-control, .form-select { background-color: #022c22; color: #fff; border: 1px solid #10b981; }
        .form-control:focus, .form-select:focus { background-color: #022c22; color: #fff; border-color: #34d399; box-shadow: 0 0 10px rgba(52, 211, 153, 0.5); }
        .btn-green-gold { background: linear-gradient(45deg, #10b981, #fbbf24); color: #000; font-weight: bold; border: none; }
        .btn-green-gold:hover { background: linear-gradient(45deg, #059669, #f59e0b); color: #fff; }
        .btn-emerald { background: linear-gradient(45deg, #34d399, #059669); color: #000; font-weight: bold; border: none; }
        .btn-emerald:hover { color: #fff; }
        .stat-card { background: rgba(16, 185, 129, 0.2); border: 1px solid #34d399; text-align: center; cursor: pointer; padding: 10px; border-radius: 10px; transition: 0.3s; }
        .stat-card:hover { background: rgba(52, 211, 153, 0.4); transform: scale(1.02); }
        .stat-number { font-size: 18px; font-weight: bold; color: #fde047; text-shadow: 0 0 8px rgba(253, 224, 71, 0.5); }
        .close-cross { font-size: 1.5rem; color: #34d399; cursor: pointer; }
        .dropdown-menu-dark { background-color: #064e3b; border: 1px solid #34d399; }
        .dropdown-item { color: #ecfdf5; }
        .dropdown-item:hover { background-color: #10b981; color: #000; font-weight: bold; }
        .notification-badge { position: absolute; top: -5px; right: -5px; font-size: 11px; padding: 3px 7px; border-radius: 50%; background: #ef4444; color: white; font-weight: bold; box-shadow: 0 0 10px rgba(239, 68, 68, 0.8); }
        .chat-box { height: 380px; overflow-y: auto; background: #022c22; padding: 15px; border-radius: 8px; border: 1px solid #10b981; display: flex; flex-direction: column; }
        .message-bubble { padding: 8px 12px; border-radius: 10px; margin-bottom: 8px; max-width: 75%; word-break: break-word; display: flex; gap: 8px; align-items: flex-start; }
        .msg-incoming { background: #064e3b; color: #fff; align-self: flex-start; border: 1px solid #34d399; }
        .msg-outgoing { background: #10b981; color: #000; align-self: flex-end; flex-direction: row-reverse; font-weight: 500; }
        .msg-avatar { width: 30px; height: 30px; border-radius: 50%; object-fit: cover; border: 1px solid #fde047; }
        .clickable-name { color: #fde047; cursor: pointer; text-decoration: underline; text-shadow: 0 0 5px rgba(253, 224, 71, 0.4); }
        .chat-file-preview { max-width: 150px; border-radius: 5px; margin-top: 5px; display: block; }
        .floating-add-btn { position: fixed; bottom: 25px; right: 25px; width: 65px; height: 65px; border-radius: 50%; background: linear-gradient(45deg, #10b981, #fbbf24); color: #000; font-size: 28px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 20px rgba(16,185,129,0.7); border: none; z-index: 1000; cursor: pointer; transition: 0.3s; }
        .floating-add-btn:hover { transform: scale(1.1); color: #fff; }
        .announcement-banner { background: linear-gradient(45deg, #10b981, #f59e0b); color: #000; font-weight: bold; border-radius: 8px; padding: 12px; margin-bottom: 15px; box-shadow: 0 0 15px rgba(16, 185, 129, 0.5); }
        .profile-avatar-preview { width: 90px; height: 90px; border-radius: 50%; border: 2px solid #34d399; object-fit: cover; margin-bottom: 10px; box-shadow: 0 0 10px rgba(52, 211, 153, 0.6); }
        .status-dot { width: 10px; height: 10px; background-color: #22c55e; border-radius: 50%; display: inline-block; box-shadow: 0 0 6px #22c55e; }
        .status-dot-offline { width: 10px; height: 10px; background-color: #64748b; border-radius: 50%; display: inline-block; }
    </style>
</head>
<body>

<div class="green-vibrant-header text-center py-2">
    <h3 class="m-0"><i class="fa-solid fa-phone-volume"></i> BTCL, কুড়িগ্রাম</h3>
    <small>Smart Control Desk & Messenger Pro</small>
</div>

<div class="container py-3">
    {% if session.get('user') %}

    <div id="latestGroupAnnouncement" class="announcement-banner text-center" style="display:none;">
        <i class="fa-solid fa-bullhorn me-2"></i> <span id="announcementText"></span>
        <button class="btn btn-dark btn-sm float-end py-0 text-warning" onclick="openMessengerModal(); switchChatTab('group');">গ্রুপে দেখুন</button>
    </div>

    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div class="d-flex align-items-center gap-2 flex-wrap">
            <button class="btn btn-emerald btn-sm" onclick="showHome()"><i class="fa-solid fa-house"></i> হোম</button>

            {% if session.get('user').get('role') in ['admin', 'main_admin'] %}
            <div class="dropdown">
                <button class="btn btn-green-gold btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-bars"></i> মেনু অপশন
                </button>
                <ul class="dropdown-menu dropdown-menu-dark">
                    <li><a class="dropdown-item" href="#" onclick="openUserListModal()"><i class="fa-solid fa-users me-2"></i>ইউজার ও এডমিন তালিকা</a></li>
                    
                    {% if session.get('user').get('username') == MAIN_ADMIN_USERNAME %}
                    <li><a class="dropdown-item" href="#" onclick="openCreateUserModal()"><i class="fa-solid fa-user-plus me-2"></i>নতুন এডমিন/ইউজার এড করুন</a></li>
                    <li><a class="dropdown-item text-warning" href="#" onclick="openAccountRequestsModal()"><i class="fa-solid fa-user-check me-2"></i>রেজিস্ট্রেশন রিকোয়েস্ট <span id="reqMenuBadge" class="badge bg-danger ms-1" style="display:none;">0</span></a></li>
                    {% endif %}
                </ul>
            </div>
            {% endif %}
            
            <button class="btn btn-outline-warning btn-sm position-relative fw-bold" onclick="openMessengerModal()">
                <i class="fa-solid fa-comments"></i> মেসেঞ্জার
                <span id="msgBadge" class="notification-badge" style="display:none;">0</span>
            </button>

            <button class="btn btn-outline-danger btn-sm position-relative fw-bold" onclick="openNotificationModal()">
                <i class="fa-solid fa-bell"></i> নোটিফিকেশন
                <span id="notifBadge" class="notification-badge" style="display:none;">0</span>
            </button>
        </div>
        
        <div class="d-flex align-items-center gap-2">
            <span class="badge bg-success border border-warning px-2 py-1" id="adminCountBadge" style="font-size: 12px;" title="মোট এডমিন সংখ্যা">
                <i class="fa-solid fa-shield-halved"></i> এডমিন: <span id="totalAdminCount">0</span> জন
            </span>

            <div class="dropdown">
                <button class="btn btn-green-gold btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-circle-user"></i> প্রোফাইল
                </button>
                <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                    <li><a class="dropdown-item" href="#" onclick="openProfileModal()"><i class="fa-solid fa-image me-2"></i>প্রোফাইল ছবি আপডেট</a></li>
                    
                    {% if session.get('user').get('username') == MAIN_ADMIN_USERNAME %}
                    <li><a class="dropdown-item text-warning" href="#" onclick="openAdminHistoryModal()"><i class="fa-solid fa-clock-rotate-left me-2"></i>এডমিন হিস্ট্রি রিপোর্ট</a></li>
                    {% endif %}
                </ul>
            </div>

            {% if session.get('user').get('username') == MAIN_ADMIN_USERNAME %}
            <div class="dropdown">
                <button class="btn btn-outline-light btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-ellipsis-vertical"></i>
                </button>
                <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                    <li><a class="dropdown-item text-danger" href="#" onclick="openTrashBinModal()"><i class="fa-solid fa-trash-arrow-up me-2"></i>রিসাইকেল বিন / রিস্টোর</a></li>
                </ul>
            </div>
            {% endif %}

            <a href="/logout" class="btn btn-danger btn-sm fw-bold"><i class="fa-solid fa-right-from-bracket"></i> লগআউট</a>
        </div>
    </div>

    <div class="row g-2 mb-3">
        <div class="col-md-6">
            <div class="input-group">
                <input type="text" id="searchInput" class="form-control" placeholder="নাম, মোবাইল বা সংযোগ নম্বর লিখে খুঁজুন..." oninput="loadRecords()">
                <button class="btn btn-green-gold" onclick="loadRecords()"><i class="fa-solid fa-magnifying-glass"></i> খুঁজুন</button>
            </div>
        </div>
        <div class="col-md-6">
            <div class="input-group">
                <span class="input-group-text bg-dark text-warning"><i class="fa-solid fa-arrow-down-a-z"></i> সাজান:</span>
                <select id="sortSelect" class="form-select" onchange="loadRecords()">
                    <option value="id_desc">সর্বশেষ যোগ করা নম্বর আগে (New to Old)</option>
                    <option value="id_asc">ক্রমিক নম্বর ১ থেকে হাজার (1 to N - ছোট থেকে বড়)</option>
                    <option value="id_high_low">হাজার থেকে ১ (N to 1 - বড় থেকে ছোট)</option>
                    <option value="name_asc">নাম অনুযায়ী (A to Z)</option>
                    <option value="name_desc">নাম অনুযায়ী (Z to A)</option>
                </select>
            </div>
        </div>
    </div>

    {% if session.get('user').get('role') in ['admin', 'main_admin'] %}
    <div class="row g-2 mb-3">
        <div class="col" onclick="filterService('')"><div class="stat-card"><div class="stat-number" id="countTotal">0</div><div style="font-size:12px; font-weight:bold; color:#a7f3d0;">সকল নম্বর</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন নাম্বার')"><div class="stat-card"><div class="stat-number" id="countTel">0</div><div style="font-size:12px; font-weight:bold; color:#a7f3d0;">টেলিফোন নাম্বার</div></div></div>
        <div class="col" onclick="filterService('টেলিফোন+ওয়াইফাই নম্বর')"><div class="stat-card"><div class="stat-number" id="countBoth">0</div><div style="font-size:12px; font-weight:bold; color:#a7f3d0;">টেলিফোন+ওয়াইফাই</div></div></div>
        <div class="col" onclick="filterService('ওয়াইফাই নাম্বার')"><div class="stat-card"><div class="stat-number" id="countWifi">0</div><div style="font-size:12px; font-weight:bold; color:#a7f3d0;">ওয়াইফাই নাম্বার</div></div></div>
    </div>
    {% endif %}

    <div id="recordsSection" class="card-custom p-3 mb-4">
        <div class="d-flex justify-content-between align-items-center border-bottom border-success pb-2">
            <h5 class="text-warning mb-0"><i class="fa-solid fa-list"></i> গ্রাহक ও সংযোগ নম্বরসমূহ</h5>
            <span class="badge bg-warning text-dark" id="currentFilterLabel">সকল নম্বর</span>
        </div>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle mt-2">
                <thead>
                    <tr>
                        <th>সিরিয়াল</th>
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
        <div class="d-flex justify-content-between align-items-center border-bottom border-success pb-2">
            <h5 class="text-warning mb-0"><i class="fa-solid fa-users"></i> রেজিস্টার্ড ইউজার ও এডমিন তালিকা</h5>
            <button class="btn btn-sm btn-outline-warning" onclick="showHome()">বন্ধ করুন</button>
        </div>
        <div class="table-responsive mt-2">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr><th>নাম</th><th>ইউজারনেম</th><th>জিমেইল</th><th>মোবাইল</th><th>রোল</th><th>স্ট্যাটাস</th><th>অ্যাকশন</th></tr>
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
                    <div class="mb-3 text-start"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
                    <button type="submit" class="btn btn-green-gold w-100 py-2">প্রবেশ করুন</button>
                </form>
                <div class="mt-3">
                    <button class="btn btn-outline-warning btn-sm" onclick="openRegisterModal()">নতুন অ্যাকাউন্ট রিকোয়েস্ট পাঠান</button>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>

<!-- Modals -->
<div class="modal fade" id="customerDetailsModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-id-card"></i> গ্রাহকের বিস্তারিত তথ্য</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body" id="customerDetailsBody"></div>
    </div>
  </div>
</div>

<div class="modal fade" id="adminHistoryModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-clock-rotate-left"></i> এডমিন হিস্ট্রি ও অ্যাক্টিভিটি রিপোর্ট</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr><th>এডমিন নাম</th><th>ইউজারনেম</th><th>সর্বশেষ অ্যাক্টিভ সময়</th><th>মোট নম্বর যোগ</th></tr>
                </thead>
                <tbody id="adminHistoryTableBody"></tbody>
            </table>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="accountRequestsModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-check"></i> অ্যাকাউন্ট রেজিস্ট্রেশন রিকোয়েস্ট</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead><tr><th>নাম</th><th>ইউজারনেম</th><th>জিমেইল</th><th>মোবাইল</th><th>সময়</th><th>অ্যাকশন</th></tr></thead>
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
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-plus"></i> অ্যাকাউন্ট রেজিস্ট্রেশন ফরম</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/api/register_request" method="POST" class="modal-body">
        <div class="mb-2"><label class="form-label">আপনার নাম</label><input type="text" name="name" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">জিমেইল (Gmail)</label><input type="email" name="email" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">মোবাইল নম্বর</label><input type="text" name="phone" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
        <button type="submit" class="btn btn-green-gold w-100 py-2">রিকোয়েস্ট পাঠান</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="messengerModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-comments"></i> রিয়েল-টাইম মেসেঞ্জার (গ্রুপ ও ইনবক্স)</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="row">
            <div class="col-md-4 border-end border-success">
                <div class="d-flex gap-1 mb-2">
                    <button class="btn btn-sm btn-green-gold w-50" onclick="switchChatTab('users')">ইনবক্স</button>
                    <button class="btn btn-sm btn-emerald w-50" onclick="switchChatTab('group')">গ্রুপ চ্যাট</button>
                </div>
                <div id="chatUserList" class="list-group list-group-flush bg-transparent" style="max-height: 380px; overflow-y: auto;"></div>
            </div>
            <div class="col-md-8 d-flex flex-column">
                <div id="activeChatTitle" class="text-warning fw-bold mb-2 pb-1 border-bottom border-success">চ্যাট নির্বাচন করুন</div>
                <div id="chatMessages" class="chat-box mb-2">
                    <p class="text-muted text-center m-auto">মেসেজ দেখতে বা পাঠাতে বামপাশ থেকে ইউজার বা গ্রুপ সিলেক্ট করুন।</p>
                </div>
                <form id="chatForm" onsubmit="sendMessage(event)" class="input-group" style="display:none;">
                    <input type="text" id="chatInput" class="form-control" placeholder="একটি মেসেজ লিখুন...">
                    <input type="file" id="chatFile" class="d-none" onchange="previewFile()">
                    <button type="button" class="btn btn-outline-warning" onclick="document.getElementById('chatFile').click()"><i class="fa-solid fa-paperclip"></i></button>
                    <button type="submit" class="btn btn-green-gold"><i class="fa-solid fa-paper-plane"></i></button>
                </form>
                <div id="selectedFilePreview" class="small text-warning mt-1" style="display:none;"></div>
            </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="modal fade" id="notificationModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-bell"></i> নোটিফিকেশন</h5>
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
      <div class="modal-header border-success d-flex justify-content-between">
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
                <option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই নম্বর</option>
                <option value="ওয়াইফাই নাম্বার">ওয়াইফাই নাম্বার</option>
            </select>
        </div>
        <div class="col-md-6"><label class="form-label">সংযোগ নম্বর</label><input type="text" id="rec_conn" name="connection_num" class="form-control"></div>
        <div class="col-md-6"><label class="form-label">ঠিকানা</label><input type="text" id="rec_address" name="address" class="form-control"></div>
        <div class="col-md-6"><label class="form-label">নোট</label><input type="text" id="rec_note" name="note" class="form-control"></div>
        
        <div class="col-12 border border-success p-3 rounded bg-dark">
            <label class="form-label text-warning mb-2"><i class="fa-solid fa-camera"></i> ছবি যুক্ত করুন:</label>
            <input type="file" id="galleryInput" name="record_image_gallery" accept="image/*" class="form-control" onchange="previewRecordImage(this)">
            <div id="imagePreviewContainer" class="mt-2" style="display:none;">
                <img id="recImagePreview" src="" style="max-height: 120px; border-radius: 5px; border: 1px solid #34d399;">
            </div>
        </div>
        <div class="col-12 text-end"><button type="submit" class="btn btn-green-gold px-4">সেভ করুন</button></div>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="createUserModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-plus"></i> নতুন এডমিন বা ইউজার তৈরি</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/api/create_user" method="POST" class="modal-body">
        <div class="mb-2"><label class="form-label">নাম</label><input type="text" name="name" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">জিমেইল</label><input type="email" name="email" class="form-control"></div>
        <div class="mb-2"><label class="form-label">মোবাইল</label><input type="text" name="phone" class="form-control"></div>
        <div class="mb-2"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
        <div class="mb-3">
            <label class="form-label">রোল নির্ধারণ করুন</label>
            <select name="role" class="form-select">
                <option value="user">সাধারণ ইউজার</option>
                <option value="admin">এডমিন</option>
            </select>
        </div>
        <button type="submit" class="btn btn-green-gold w-100 py-2">তৈরি করুন</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="profileModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom text-center">
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-gear"></i> প্রোফাইল ছবি আপডেট</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/update_profile_pic" method="POST" enctype="multipart/form-data" class="modal-body">
        <div class="mb-3">
            <img id="profilePreviewImg" src="{{ session.get('user',{}).get('profile_pic') or 'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/svgs/solid/circle-user.svg' }}" class="profile-avatar-preview">
            <h5 class="text-warning">{{ session.get('user',{}).get('name') }}</h5>
            <p class="text-muted small">@{{ session.get('user',{}).get('username') }}</p>
        </div>
        <div class="mb-3 text-start">
            <label class="form-label">আপনার নতুন ছবি সিলেক্ট করুন</label>
            <input type="file" name="profile_pic" class="form-control" accept="image/*" required onchange="previewAvatar(event)">
        </div>
        <button type="submit" class="btn btn-green-gold w-100 py-2">ছবি আপডেট করুন</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="trashBinModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-success d-flex justify-content-between">
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
let currentFilter = '';
let currentChatUser = '';
let currentChatTab = 'users';

document.addEventListener("DOMContentLoaded", () => {
    {% if session.get('user') %}
    loadRecords();
    loadStats();
    loadAdminCount();
    setInterval(updateActivity, 10000);
    setInterval(pollData, 4000);
    {% endif %}
});

function updateActivity() {
    fetch('/api/ping').catch(err => console.log(err));
}

function loadStats() {
    fetch('/api/stats').then(res => res.json()).then(data => {
        if(document.getElementById('countTotal')) {
            document.getElementById('countTotal').innerText = data.total;
            document.getElementById('countTel').innerText = data.tel;
            document.getElementById('countBoth').innerText = data.both;
            document.getElementById('countWifi').innerText = data.wifi;
        }
    });
}

function loadAdminCount() {
    fetch('/api/admin_count').then(res => res.json()).then(data => {
        if(document.getElementById('totalAdminCount')) {
            document.getElementById('totalAdminCount').innerText = data.count;
        }
    });
}

function loadRecords() {
    let q = document.getElementById('searchInput').value;
    let sort = document.getElementById('sortSelect').value;
    let url = `/api/records?search=${encodeURIComponent(q)}&service=${encodeURIComponent(currentFilter)}&sort=${sort}`;
    
    fetch(url).then(res => res.json()).then(data => {
        let tbody = document.getElementById('recordsTableBody');
        tbody.innerHTML = '';
        if(data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted">কোনো রেকর্ড পাওয়া যায়নি।</td></tr>`;
            return;
        }
        data.forEach((r, index) => {
            let tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${index + 1}</td>
                <td><span class="clickable-name" onclick="openCustomerDetails(${r.id})">${r.customer_name}</span></td>
                <td>${r.mobile || '-'}</td>
                <td><span class="badge bg-success">${r.service_type}</span></td>
                <td>${r.connection_num || '-'}</td>
                <td>${r.address || '-'}</td>
                <td><span class="badge bg-dark border border-success">${r.added_by}</span></td>
                {% if session.get('user').get('role') in ['admin', 'main_admin'] %}
                <td>
                    <button class="btn btn-sm btn-outline-warning py-0 px-1" onclick="openEditRecordModal(${r.id})"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn btn-sm btn-outline-danger py-0 px-1" onclick="deleteRecord(${r.id})"><i class="fa-solid fa-trash"></i></button>
                </td>
                {% endif %}
            `;
            tbody.appendChild(tr);
        });
    });
}

function filterService(service) {
    currentFilter = service;
    document.getElementById('currentFilterLabel').innerText = service ? service : 'সকল নম্বর';
    loadRecords();
}

function openCustomerDetails(id) {
    fetch(`/api/record/${id}`).then(res => res.json()).then(r => {
        let body = document.getElementById('customerDetailsBody');
        let imgHtml = r.record_image ? `<div class="mt-2 text-center"><img src="/${r.record_image}" class="img-fluid rounded border border-success" style="max-height:200px;"></div>` : '';
        body.innerHTML = `
            <p><strong>গ্রাহকের নাম:</strong> ${r.customer_name}</p>
            <p><strong>মোবাইল:</strong> ${r.mobile || '-'}</p>
            <p><strong>সেবার ধরন:</strong> ${r.service_type}</p>
            <p><strong>সংযোগ নম্বর:</strong> ${r.connection_num || '-'}</p>
            <p><strong>ঠিকানা:</strong> ${r.address || '-'}</p>
            <p><strong>নোট:</strong> ${r.note || '-'}</p>
            <p><strong>যুক্ত করেছেন:</strong> ${r.added_by}</p>
            <p><strong>তারিখ:</strong> ${r.created_at}</p>
            ${imgHtml}
        `;
        new bootstrap.Modal(document.getElementById('customerDetailsModal')).show();
    });
}

function openAddRecordModal() {
    document.getElementById('recordForm').reset();
    document.getElementById('rec_id').value = '';
    document.getElementById('recordModalTitle').innerText = 'গ্রাহক নম্বর যোগ করুন';
    document.getElementById('imagePreviewContainer').style.display = 'none';
    new bootstrap.Modal(document.getElementById('recordModal')).show();
}

function openEditRecordModal(id) {
    fetch(`/api/record/${id}`).then(res => res.json()).then(r => {
        document.getElementById('rec_id').value = r.id;
        document.getElementById('rec_name').value = r.customer_name;
        document.getElementById('rec_mobile').value = r.mobile || '';
        document.getElementById('rec_service').value = r.service_type;
        document.getElementById('rec_conn').value = r.connection_num || '';
        document.getElementById('rec_address').value = r.address || '';
        document.getElementById('rec_note').value = r.note || '';
        document.getElementById('recordModalTitle').innerText = 'গ্রাহক নম্বর এডিট ও আপডেট করুন';
        if(r.record_image) {
            document.getElementById('recImagePreview').src = '/' + r.record_image;
            document.getElementById('imagePreviewContainer').style.display = 'block';
        } else {
            document.getElementById('imagePreviewContainer').style.display = 'none';
        }
        new bootstrap.Modal(document.getElementById('recordModal')).show();
    });
}

function saveRecord(e) {
    e.preventDefault();
    let formData = new FormData(document.getElementById('recordForm'));
    fetch('/api/save_record', { method: 'POST', body: formData }).then(res => res.json()).then(data => {
        if(data.success) {
            bootstrap.Modal.getInstance(document.getElementById('recordModal')).hide();
            loadRecords();
            loadStats();
        } else {
            alert('ত্রুটি হয়েছে!');
        }
    });
}

function deleteRecord(id) {
    if(confirm('আপনি কি এই রেকর্ডটি রিসাইকেল বিনে পাঠাতে চান?')) {
        fetch(`/api/delete_record/${id}`, { method: 'POST' }).then(res => res.json()).then(data => {
            if(data.success) { loadRecords(); loadStats(); }
        });
    }
}

function previewRecordImage(input) {
    if (input.files && input.files[0]) {
        let reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById('recImagePreview').src = e.target.result;
            document.getElementById('imagePreviewContainer').style.display = 'block';
        }
        reader.readAsDataURL(input.files[0]);
    }
}

function openUserListModal() {
    document.getElementById('recordsSection').style.display = 'none';
    document.getElementById('userListSection').style.display = 'block';
    fetch('/api/users').then(res => res.json()).then(data => {
        let tbody = document.getElementById('userTableBody');
        tbody.innerHTML = '';
        data.forEach(u => {
            let tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${u.name}</td>
                <td>@${u.username}</td>
                <td>${u.email || '-'}</td>
                <td>${u.phone || '-'}</td>
                <td><span class="badge bg-success">${u.role}</span></td>
                <td><span class="badge bg-warning text-dark">${u.status}</span></td>
                <td>
                    {% if session.get('user').get('username') == MAIN_ADMIN_USERNAME %}
                    <button class="btn btn-sm btn-outline-danger py-0 px-1" onclick="deleteUser(${u.id})" title="সম্পূর্ণ ডিলিট (ব্লক)">ডিলিট</button>
                    {% else %}
                    -
                    {% endif %}
                </td>
            `;
            tbody.appendChild(tr);
        });
    });
}

function showHome() {
    document.getElementById('userListSection').style.display = 'none';
    document.getElementById('recordsSection').style.display = 'block';
    loadRecords();
}

function deleteUser(id) {
    let secPass = prompt('ইউজার ডিলিট করতে সিকিউরিটি পাসওয়ার্ড দিন:');
    if(secPass) {
        fetch(`/api/delete_user/${id}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({security_password: secPass})
        }).then(res => res.json()).then(data => {
            if(data.success) { openUserListModal(); loadAdminCount(); }
            else { alert(data.error || 'ভুল পাসওয়ার্ড!'); }
        });
    }
}

function openCreateUserModal() {
    new bootstrap.Modal(document.getElementById('createUserModal')).show();
}

function openAccountRequestsModal() {
    fetch('/api/account_requests').then(res => res.json()).then(data => {
        let tbody = document.getElementById('requestTableBody');
        tbody.innerHTML = '';
        if(data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted">কোনো রিকোয়েস্ট নেই।</td></tr>`;
        }
        data.forEach(r => {
            let tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${r.name}</td>
                <td>@${r.username}</td>
                <td>${r.email || '-'}</td>
                <td>${r.phone || '-'}</td>
                <td>${r.created_at}</td>
                <td>
                    <button class="btn btn-sm btn-success py-0 px-1" onclick="approveUser(${r.id})">অনুমোদন</button>
                    <button class="btn btn-sm btn-danger py-0 px-1" onclick="rejectUser(${r.id})">বাতিল</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
        new bootstrap.Modal(document.getElementById('accountRequestsModal')).show();
    });
}

function approveUser(id) {
    fetch(`/api/approve_user/${id}`, {method: 'POST'}).then(res => res.json()).then(data => {
        if(data.success) { openAccountRequestsModal(); loadAdminCount(); }
    });
}

function rejectUser(id) {
    fetch(`/api/reject_user/${id}`, {method: 'POST'}).then(res => res.json()).then(data => {
        if(data.success) { openAccountRequestsModal(); }
    });
}

function openAdminHistoryModal() {
    fetch('/api/admin_history').then(res => res.json()).then(data => {
        let tbody = document.getElementById('adminHistoryTableBody');
        tbody.innerHTML = '';
        data.forEach(a => {
            let tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${a.name}</td>
                <td>@${a.username}</td>
                <td>${a.last_active}</td>
                <td><span class="badge bg-warning text-dark">${a.total_records} টি</span></td>
            `;
            tbody.appendChild(tr);
        });
        new bootstrap.Modal(document.getElementById('adminHistoryModal')).show();
    });
}

function openTrashBinModal() {
    fetch('/api/trash_records').then(res => res.json()).then(data => {
        let tbody = document.getElementById('trashTableBody');
        tbody.innerHTML = '';
        data.forEach(r => {
            let tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${r.customer_name}</td>
                <td>${r.connection_num || '-'}</td>
                <td><button class="btn btn-sm btn-success py-0 px-1" onclick="restoreRecord(${r.id})">রিস্টোর</button></td>
            `;
            tbody.appendChild(tr);
        });
        new bootstrap.Modal(document.getElementById('trashBinModal')).show();
    });
}

function restoreRecord(id) {
    fetch(`/api/restore_record/${id}`, {method: 'POST'}).then(res => res.json()).then(data => {
        if(data.success) { openTrashBinModal(); loadRecords(); loadStats(); }
    });
}

function openMessengerModal() {
    new bootstrap.Modal(document.getElementById('messengerModal')).show();
    loadChatUsers();
}

function switchChatTab(tab) {
    currentChatTab = tab;
    loadChatUsers();
}

function loadChatUsers() {
    fetch(`/api/chat_users?tab=${currentChatTab}`).then(res => res.json()).then(data => {
        let list = document.getElementById('chatUserList');
        list.innerHTML = '';
        if(currentChatTab === 'group') {
            let item = document.createElement('a');
            item.className = `list-group-item list-group-item-action bg-transparent text-white border-success d-flex align-items-center gap-2 ${currentChatUser === 'GROUP_CHAT' ? 'active' : ''}`;
            item.innerHTML = `<i class="fa-solid fa-users-rectangle text-warning fa-lg"></i> <div><strong>অফিসিয়াল গ্রুপ চ্যাট</strong><br><small class="text-success">সকলের জন্য উন্মুক্ত</small></div>`;
            item.onclick = () => selectChat('GROUP_CHAT', 'অফিসিয়াল গ্রুপ চ্যাট');
            list.appendChild(item);
            if(currentChatUser === '') selectChat('GROUP_CHAT', 'অফিসিয়াল গ্রুপ চ্যাট');
        } else {
            data.forEach(u => {
                let statusBadge = u.is_online ? '<span class="status-dot" title="অ্যাক্টিভ আছেন"></span>' : '<span class="status-dot-offline" title="অফলাইন"></span>';
                let item = document.createElement('a');
                item.className = `list-group-item list-group-item-action bg-transparent text-white border-success d-flex align-items-center justify-content-between ${currentChatUser === u.username ? 'active' : ''}`;
                item.innerHTML = `
                    <div class="d-flex align-items-center gap-2">
                        <img src="${u.profile_pic || 'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/svgs/solid/circle-user.svg'}" class="msg-avatar">
                        <div><strong>${u.name}</strong><br><small class="text-muted">@${u.username}</small></div>
                    </div>
                    <div>${statusBadge}</div>
                `;
                item.onclick = () => selectChat(u.username, u.name);
                list.appendChild(item);
            });
        }
    });
}

function selectChat(target, title) {
    currentChatUser = target;
    document.getElementById('activeChatTitle').innerText = title;
    document.getElementById('chatForm').style.display = 'flex';
    loadMessages();
}

function loadMessages() {
    if(!currentChatUser) return;
    let isGroup = currentChatUser === 'GROUP_CHAT' ? 1 : 0;
    fetch(`/api/messages?target=${encodeURIComponent(currentChatUser)}&is_group=${isGroup}`).then(res => res.json()).then(data => {
        let box = document.getElementById('chatMessages');
        box.innerHTML = '';
        data.forEach(m => {
            let isOutgoing = m.sender === "{{ session.get('user',{}).get('username') }}";
            let div = document.createElement('div');
            div.className = `message-bubble ${isOutgoing ? 'msg-outgoing' : 'msg-incoming'}`;
            let fileHtml = m.file_url ? `<a href="/${m.file_url}" target="_blank"><img src="/${m.file_url}" class="chat-file-preview"></a>` : '';
            div.innerHTML = `
                <div>
                    ${!isOutgoing && isGroup ? `<small class="text-warning d-block">@${m.sender}</small>` : ''}
                    <span>${m.message || ''}</span>
                    ${fileHtml}
                    <small class="d-block text-end text-muted" style="font-size:9px;">${m.timestamp}</small>
                </div>
            `;
            box.appendChild(div);
        });
        box.scrollTop = box.scrollHeight;
    });
}

function sendMessage(e) {
    e.preventDefault();
    let text = document.getElementById('chatInput').value;
    let fileInput = document.getElementById('chatFile');
    let formData = new FormData();
    formData.append('receiver', currentChatUser);
    formData.append('message', text);
    formData.append('is_group', currentChatUser === 'GROUP_CHAT' ? 1 : 0);
    if(fileInput.files[0]) {
        formData.append('file', fileInput.files[0]);
    }
    fetch('/api/send_message', { method: 'POST', body: formData }).then(res => res.json()).then(data => {
        if(data.success) {
            document.getElementById('chatInput').value = '';
            fileInput.value = '';
            document.getElementById('selectedFilePreview').style.display = 'none';
            loadMessages();
        }
    });
}

function previewFile() {
    let file = document.getElementById('chatFile').files[0];
    if(file) {
        let prev = document.getElementById('selectedFilePreview');
        prev.innerText = 'ফাইল যুক্ত হয়েছে: ' + file.name;
        prev.style.display = 'block';
    }
}

function pollData() {
    fetch('/api/notifications_count').then(res => res.json()).then(data => {
        let msgBadge = document.getElementById('msgBadge');
        if(data.messages > 0) { msgBadge.innerText = data.messages; msgBadge.style.display = 'inline-block'; }
        else { msgBadge.style.display = 'none'; }
        
        let notifBadge = document.getElementById('notifBadge');
        if(data.notifications > 0) { notifBadge.innerText = data.notifications; notifBadge.style.display = 'inline-block'; }
        else { notifBadge.style.display = 'none'; }

        {% if session.get('user').get('username') == MAIN_ADMIN_USERNAME %}
        let reqBadge = document.getElementById('reqMenuBadge');
        if(data.requests > 0) { reqBadge.innerText = data.requests; reqBadge.style.display = 'inline-block'; }
        else { reqBadge.style.display = 'none'; }
        {% endif %}
    });
    if(currentChatUser) loadMessages();
}

function openNotificationModal() {
    fetch('/api/notifications').then(res => res.json()).then(data => {
        let list = document.getElementById('notificationList');
        list.innerHTML = '';
        if(data.length === 0) {
            list.innerHTML = `<p class="text-muted text-center">কোনো নতুন নোটিফিকেশন নেই।</p>`;
        }
        data.forEach(n => {
            let item = document.createElement('div');
            item.className = 'list-group-item bg-transparent text-white border-success mb-1';
            item.innerHTML = `<i class="fa-solid fa-circle-info text-warning me-2"></i> ${n.message} <small class="text-muted float-end">${n.timestamp}</small>`;
            list.appendChild(item);
        });
        new bootstrap.Modal(document.getElementById('notificationModal')).show();
    });
}
</script>
</body>
</html>
"""

# Flask Backend Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, MAIN_ADMIN_USERNAME=MAIN_ADMIN_USERNAME)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE (username = ? OR email = ? OR phone = ?) AND is_deleted = 0", (username, username, username))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[5], password):
        if user[8] != 'active' and user[2] != MAIN_ADMIN_USERNAME:
            return "<script>alert('আপনার অ্যাকাউন্টটি এখনো এডমিন কর্তৃক অনুমোদিত হয়নি!'); window.location='/';</script>"
        session['user'] = {
            'id': user[0],
            'name': user[1],
            'username': user[2],
            'email': user[3],
            'phone': user[4],
            'role': user[7],
            'profile_pic': user[9]
        }
        return redirect(url_for('index'))
    return "<script>alert('ভুল ইউজারনেম অথবা পাসওয়ার্ড!'); window.location='/';</script>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/api/ping')
def ping():
    if 'user' in session:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE username = ?", (session['user']['username'],))
        conn.commit()
        conn.close()
    return jsonify({'success': True})

@app.route('/api/stats')
def stats():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted = 0")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE service_type = 'টেলিফোন নাম্বার' AND is_deleted = 0")
    tel = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE service_type = 'টেলিফোন+ওয়াইফাই নম্বর' AND is_deleted = 0")
    both = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE service_type = 'ওয়াইফাই নাম্বার' AND is_deleted = 0")
    wifi = cursor.fetchone()[0]
    conn.close()
    return jsonify({'total': total, 'tel': tel, 'both': both, 'wifi': wifi})

@app.route('/api/admin_count')
def admin_count():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE role IN ('admin', 'main_admin') AND is_deleted = 0")
    count = cursor.fetchone()[0]
    conn.close()
    return jsonify({'count': count})

@app.route('/api/records')
def get_records():
    search = request.args.get('search', '')
    service = request.args.get('service', '')
    sort = request.args.get('sort', 'id_desc')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    query = "SELECT id, customer_name, mobile, service_type, connection_num, address, added_by FROM phone_records WHERE is_deleted = 0"
    params = []
    
    if search:
        query += " AND (customer_name LIKE ? OR mobile LIKE ? OR connection_num LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    
    if service:
        query += " AND service_type = ?"
        params.append(service)
        
    if sort == 'id_desc':
        query += " ORDER BY id DESC"
    elif sort == 'id_asc':
        query += " ORDER BY id ASC"
    elif sort == 'id_high_low':
        query += " ORDER BY CAST(connection_num AS INTEGER) DESC"
    elif sort == 'name_asc':
        query += " ORDER BY customer_name ASC"
    elif sort == 'name_desc':
        query += " ORDER BY customer_name DESC"
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    records = []
    for r in rows:
        records.append({
            'id': r[0], 'customer_name': r[1], 'mobile': r[2],
            'service_type': r[3], 'connection_num': r[4], 'address': r[5], 'added_by': r[6]
        })
    return jsonify(records)

@app.route('/api/record/<int:id>')
def get_record(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, mobile, service_type, connection_num, address, note, record_image, added_by, created_at FROM phone_records WHERE id = ?", (id,))
    r = cursor.fetchone()
    conn.close()
    if r:
        return jsonify({
            'id': r[0], 'customer_name': r[1], 'mobile': r[2], 'service_type': r[3],
            'connection_num': r[4], 'address': r[5], 'note': r[6], 'record_image': r[7],
            'added_by': r[8], 'created_at': r[9]
        })
    return jsonify({}), 404

@app.route('/api/save_record', methods=['POST'])
def save_record():
    if 'user' not in session or session['user']['role'] not in ['admin', 'main_admin']:
        return jsonify({'success': False}), 403
        
    rec_id = request.form.get('id')
    customer_name = request.form.get('customer_name')
    mobile = request.form.get('mobile')
    service_type = request.form.get('service_type')
    connection_num = request.form.get('connection_num')
    address = request.form.get('address')
    note = request.form.get('note')
    added_by = session['user']['username']
    
    image_path = ''
    if 'record_image_gallery' in request.files:
        file = request.files['record_image_gallery']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = f"static/uploads/{filename}"

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if rec_id:
        if image_path:
            cursor.execute('''UPDATE phone_records SET customer_name=?, mobile=?, service_type=?, connection_num=?, address=?, note=?, record_image=? WHERE id=?''',
                           (customer_name, mobile, service_type, connection_num, address, note, image_path, rec_id))
        else:
            cursor.execute('''UPDATE phone_records SET customer_name=?, mobile=?, service_type=?, connection_num=?, address=?, note=? WHERE id=?''',
                           (customer_name, mobile, service_type, connection_num, address, note, rec_id))
    else:
        cursor.execute('''INSERT INTO phone_records (customer_name, mobile, service_type, connection_num, address, note, record_image, added_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (customer_name, mobile, service_type, connection_num, address, note, image_path, added_by))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/delete_record/<int:id>', methods=['POST'])
def delete_record(id):
    if 'user' not in session or session['user']['role'] not in ['admin', 'main_admin']:
        return jsonify({'success': False}), 403
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE phone_records SET is_deleted = 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/trash_records')
def trash_records():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, customer_name, connection_num FROM phone_records WHERE is_deleted = 1")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'customer_name': r[1], 'connection_num': r[2]} for r in rows])

@app.route('/api/restore_record/<int:id>', methods=['POST'])
def restore_record(id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE phone_records SET is_deleted = 0 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/users')
def get_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, phone, role, status FROM users WHERE is_deleted = 0")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'name': r[1], 'username': r[2], 'email': r[3], 'phone': r[4], 'role': r[5], 'status': r[6]} for r in rows])

@app.route('/api/create_user', methods=['POST'])
def create_user():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return "<script>alert('শুধুমাত্র মূল এডমিন নতুন অ্যাকাউন্ট তৈরি করতে পারবেন!'); window.location='/';</script>"
    
    name = request.form.get('name')
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    hashed_pw = generate_password_hash(password)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, username, email, phone, password, raw_pass, role, status, added_by) VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)",
                       (name, username, email, phone, hashed_pw, password, role, session['user']['username']))
        conn.commit()
    except Exception as e:
        print(e)
    conn.close()
    return redirect(url_for('index'))

@app.route('/api/delete_user/<int:id>', methods=['POST'])
def delete_user(id):
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return jsonify({'success': False, 'error': 'অনুমতি নেই'}), 403
    data = request.get_json()
    if data.get('security_password') != SECURITY_DELETE_PASSWORD:
        return jsonify({'success': False, 'error': 'ভুল সিকিউরিটি পাসওয়ার্ড!'})
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_deleted = 1 WHERE id = ? AND username != ?", (id, MAIN_ADMIN_USERNAME))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/account_requests')
def account_requests():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, phone, created_at FROM users WHERE status = 'pending' AND is_deleted = 0")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'name': r[1], 'username': r[2], 'email': r[3], 'phone': r[4], 'created_at': r[5]} for r in rows])

@app.route('/api/register_request', methods=['POST'])
def register_request():
    name = request.form.get('name')
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    hashed_pw = generate_password_hash(password)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, username, email, phone, password, raw_pass, role, status) VALUES (?, ?, ?, ?, ?, ?, 'user', 'pending')",
                       (name, username, email, phone, hashed_pw, password))
        conn.commit()
    except Exception as e:
        print(e)
    conn.close()
    return "<script>alert('আপনার রেজিস্ট্রেশন রিকোয়েস্ট সফলভাবে পাঠানো হয়েছে!'); window.location='/';</script>"

@app.route('/api/approve_user/<int:id>', methods=['POST'])
def approve_user(id):
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return jsonify({'success': False}), 403
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'active' WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/reject_user/<int:id>', methods=['POST'])
def reject_user(id):
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return jsonify({'success': False}), 403
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_deleted = 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin_history')
def admin_history():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, last_active FROM users WHERE role IN ('admin', 'main_admin') AND is_deleted = 0")
    admins = cursor.fetchall()
    
    history = []
    for a in admins:
        cursor.execute("SELECT COUNT(*) FROM phone_records WHERE added_by = ? AND is_deleted = 0", (a[1],))
        total_rec = cursor.fetchone()[0]
        history.append({
            'name': a[0], 'username': a[1], 'last_active': a[2], 'total_records': total_rec
        })
    conn.close()
    return jsonify(history)

@app.route('/update_profile_pic', methods=['POST'])
def update_profile_pic():
    if 'user' not in session:
        return redirect(url_for('index'))
    file = request.files['profile_pic']
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        path = f"static/uploads/{filename}"
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET profile_pic = ? WHERE username = ?", (path, session['user']['username']))
        conn.commit()
        conn.close()
        session['user']['profile_pic'] = path
    return redirect(url_for('index'))

@app.route('/api/chat_users')
def chat_users():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, name, profile_pic, last_active FROM users WHERE username != ? AND is_deleted = 0", (session['user']['username'],))
    rows = cursor.fetchall()
    conn.close()
    
    users = []
    now = datetime.now()
    for r in rows:
        # Check active status within last 30 seconds
        last_active_time = datetime.strptime(r[3], '%Y-%m-%d %H:%M:%S') if r[3] else now
        is_online = (now - last_active_time).total_seconds() < 35
        users.append({
            'username': r[0], 'name': r[1], 'profile_pic': r[2], 'is_online': is_online
        })
    # Sort active users to top
    users.sort(key=lambda x: x['is_online'], reverse=True)
    return jsonify(users)

@app.route('/api/messages')
def get_messages():
    target = request.args.get('target')
    is_group = int(request.args.get('is_group', 0))
    username = session['user']['username']
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if is_group:
        cursor.execute("SELECT sender, receiver, message, file_url, timestamp FROM messages WHERE is_group = 1 ORDER BY timestamp ASC")
    else:
        cursor.execute("""SELECT sender, receiver, message, file_url, timestamp FROM messages 
                          WHERE is_group = 0 AND ((sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)) 
                          ORDER BY timestamp ASC""", (username, target, target, username))
    rows = cursor.fetchall()
    conn.close()
    
    messages = []
    for r in rows:
        messages.append({
            'sender': r[0], 'receiver': r[1], 'message': r[2], 'file_url': r[3], 'timestamp': r[4]
        })
    return jsonify(messages)

@app.route('/api/send_message', methods=['POST'])
def send_message():
    if 'user' not in session:
        return jsonify({'success': False}), 403
    sender = session['user']['username']
    receiver = request.form.get('receiver')
    message = request.form.get('message', '')
    is_group = int(request.form.get('is_group', 0))
    
    file_url = ''
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = f"static/uploads/{filename}"
            
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, receiver, message, file_url, is_group) VALUES (?, ?, ?, ?, ?)",
                   (sender, receiver, message, file_url, is_group))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/notifications_count')
def notifications_count():
    if 'user' not in session:
        return jsonify({'messages': 0, 'notifications': 0, 'requests': 0})
    username = session['user']['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM messages WHERE receiver = ? AND is_read = 0", (username,))
    msg_count = cursor.fetchone()[0]
    
    req_count = 0
    if username == MAIN_ADMIN_USERNAME:
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'pending' AND is_deleted = 0")
        req_count = cursor.fetchone()[0]
    conn.close()
    return jsonify({'messages': msg_count, 'notifications': 0, 'requests': req_count})

@app.route('/api/notifications')
def notifications():
    return jsonify([])

if __name__ == '__main__':
    app.run(debug=True, port=5000)