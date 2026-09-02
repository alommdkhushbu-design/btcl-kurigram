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
    </style>
</head>
<body>

<div class="green-vibrant-header text-center py-2">
    <h3 class="m-0"><i class="fa-solid fa-phone-volume"></i> BTCL, কুড়িগ্রাম</h3>
    <small>Smart Management Portal & Messenger</small>
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
                    <li><a class="dropdown-item" href="#" onclick="openCreateUserModal()"><i class="fa-solid fa-user-plus me-2"></i>ইউজার এড করা</a></li>
                    
                    {% if session.get('user').get('username') == MAIN_ADMIN_USERNAME %}
                    <li><a class="dropdown-item text-warning" href="#" onclick="openAccountRequestsModal()"><i class="fa-solid fa-user-check me-2"></i>রেজিস্ট্রেশন রিকোয়েস্ট ও ডকুমেন্ট <span id="reqMenuBadge" class="badge bg-danger ms-1" style="display:none;">0</span></a></li>
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
            <div class="dropdown">
                <button class="btn btn-green-gold btn-sm dropdown-toggle" type="button" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-circle-user"></i> প্রোফাইল
                </button>
                <ul class="dropdown-menu dropdown-menu-dark dropdown-menu-end">
                    <li><a class="dropdown-item" href="#" onclick="openProfileModal()"><i class="fa-solid fa-image me-2"></i>প্রোফাইল ছবি আপডেট</a></li>
                    
                    {% if session.get('user').get('username') == MAIN_ADMIN_USERNAME %}
                    <li><a class="dropdown-item text-warning" href="#" onclick="openAdminHistoryModal()"><i class="fa-solid fa-clock-rotate-left me-2"></i>এডমিন হিস্ট্রি (অ্যাক্টিভিটি রিপোর্ট)</a></li>
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
                    <option value="id_asc">পুরাতন থেকে নতুন (1 to N - ছোট থেকে বড়)</option>
                    <option value="id_high_low">বড় সংখ্যা থেকে ছোট সংখ্যা (N to 1)</option>
                    <option value="name_asc">নাম অনুযায়ী (A to Z)</option>
                    <option value="name_desc">নাম অনুযায়ী (Z to A)</option>
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
            <h5 class="text-warning mb-0"><i class="fa-solid fa-list"></i> গ্রাহক ও সংযোগ নম্বরসমূহ</h5>
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
                    <tr><th>নাম</th><th>ইউজারনেম</th><th>জিমেইল</th><th>মোবাইল</th><th>পাসওয়ার্ড</th><th>রোল</th><th>স্ট্যাটাস</th><th>অ্যাকশন</th></tr>
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

<div class="modal fade" id="adminDetailModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning" id="adminDetailModalTitle"><i class="fa-solid fa-user-shield"></i> এডমিন ডিটেইলড অ্যাক্টিভিটি</h5>
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
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-check"></i> অ্যাকাউন্ট রেজিস্ট্রেশন রিকোয়েস্ট ও ডকুমেন্ট (শুধুমাত্র রিয়েল এডমিন)</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead><tr><th>নাম</th><th>ইউজারনেম</th><th>জিমেইল</th><th>মোবাইল</th><th>পাসওয়ার্ড</th><th>সময়</th><th>অ্যাকশন</th></tr></thead>
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
        <div class="mb-2"><label class="form-label">জিমেইল (Gmail) *</label><input type="email" name="email" class="form-control" required></div>
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
                <div id="groupPermissionNotice" class="text-danger small text-center mt-1" style="display:none;">সাধারণ ইউজাররা গ্রুপে মেসেজ পাঠাতে পারবেন না, কেবল দেখতে পারবেন।</div>
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
        <h5 class="modal-title text-warning"><i class="fa-solid fa-bell"></i> নোটিফিকেশন ও মেসেজ রিকোয়েস্ট</h5>
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
            <label class="form-label text-warning mb-2"><i class="fa-solid fa-camera"></i> গ্রাহক বা ডকুমেন্টের ছবি যুক্ত করুন:</label>
            <div class="d-flex gap-2 flex-wrap mb-2">
                <button type="button" class="btn btn-outline-warning btn-sm" onclick="document.getElementById('cameraInput').click()"><i class="fa-solid fa-camera-retro me-1"></i> সরাসরি ক্যামেরা ব্যবহার করুন</button>
                <button type="button" class="btn btn-outline-emerald btn-sm" onclick="document.getElementById('galleryInput').click()"><i class="fa-solid fa-image me-1"></i> গ্যালারি থেকে ছবি সিলেক্ট করুন</button>
            </div>
            <input type="file" id="cameraInput" name="record_image_camera" accept="image/*" capture="environment" class="d-none" onchange="previewRecordImage(this)">
            <input type="file" id="galleryInput" name="record_image_gallery" accept="image/*" class="d-none" onchange="previewRecordImage(this)">
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
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-plus"></i> ইউজার তৈরি করুন</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/api/create_user" method="POST" class="modal-body">
        <input type="hidden" name="role" value="user">
        <div class="mb-2"><label class="form-label">নাম</label><input type="text" name="name" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" name="username" class="form-control" required></div>
        <div class="mb-2"><label class="form-label">জিমেইল</label><input type="email" name="email" class="form-control"></div>
        <div class="mb-2"><label class="form-label">মোবাইল</label><input type="text" name="phone" class="form-control"></div>
        <div class="mb-3"><label class="form-label">পাসওয়ার্ড</label><input type="password" name="password" class="form-control" required></div>
        <button type="submit" class="btn btn-green-gold w-100 py-2">তৈরি করুন</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="editUserModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content card-custom">
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-user-pen"></i> ইউজার/এডমিন তথ্য পরিবর্তন</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <form action="/api/update_user_credentials" method="POST" class="modal-body">
        <input type="hidden" id="edit_user_id" name="user_id">
        <div class="mb-2"><label class="form-label">ইউজারনেম</label><input type="text" id="edit_username" name="username" class="form-control" required></div>
        <div class="mb-3"><label class="form-label">নতুন পাসওয়ার্ড</label><input type="text" id="edit_password" name="password" class="form-control" placeholder="নতুন পাসওয়ার্ড দিন" required></div>
        <button type="submit" class="btn btn-green-gold w-100 py-2">পরিবর্তন সেভ করুন</button>
      </form>
    </div>
  </div>
</div>

<div class="modal fade" id="adminHistoryModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content card-custom">
      <div class="modal-header border-success d-flex justify-content-between">
        <h5 class="modal-title text-warning"><i class="fa-solid fa-clock-rotate-left"></i> এডমিন হিস্ট্রি ও অ্যাক্টিভিটি (রিয়েল এডমিন প্যানেল)</h5>
        <i class="fa-solid fa-xmark close-cross" data-bs-dismiss="modal"></i>
      </div>
      <div class="modal-body">
        <p class="small text-warning mb-2">যেকোনো এডমিনের নামের ওপর ক্লিক করে তাদের বিস্তারিত কাজ, তারিখ, সময় ও মিনিটভিত্তিক অ্যাক্টিভিটি দেখুন:</p>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr><th>এডমিন নাম</th><th>ইউজারনেম</th><th>সর্বশেষ অ্যাক্টিভ সময়</th><th>মোট ইউজার যোগ</th><th>মোট নম্বর যোগ</th></tr>
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
            <label class="form-label">আপনার নতুন প্রোফাইল ছবি সিলেক্ট করুন</label>
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
let activeServiceFilter = '';
let currentChatTarget = '';
let currentChatIsGroup = 0;
let currentChatTabType = 'users';
let chatInterval = null;
let globalPollInterval = null;

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
            
            // নামের ওপর ক্লিক করলেই সব ডিটেলস দেখা যাবে (সবার জন্য কার্যকর)
            let nameCell = `<span class="clickable-name" onclick="openCustomerDetails(${row[0]})">${row[1]}</span>`;

            let actionTd = isAdmin ? `
                <td>
                    <button class="btn btn-warning btn-sm me-1" onclick="openEditRecordModal(${row[0]})" title="এডিট করুন"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="deleteRecord(${row[0]})" title="ডিলিট করুন"><i class="fa-solid fa-trash"></i></button>
                </td>` : '';

            html += `<tr>
                <td><strong>${displayIndex}</strong></td>
                <td>${nameCell}</td>
                <td>${row[2] || '-'}</td>
                <td><span class="badge bg-warning text-dark">${row[3]}</span></td>
                <td>${row[4] || '-'}</td>
                <td>${row[5] || '-'}</td>
                <td><span class="badge bg-success text-dark">${row[8] || 'Khushbu23'}</span></td>
                ${actionTd}
            </tr>`;
        });
        if(document.getElementById('recordsTableBody')) {
            document.getElementById('recordsTableBody').innerHTML = html;
        }
        
        if(data.counts) {
            if(document.getElementById('countTotal')) document.getElementById('countTotal').innerText = data.counts.total;
            if(document.getElementById('countTel')) document.getElementById('countTel').innerText = data.counts.tel;
            if(document.getElementById('countBoth')) document.getElementById('countBoth').innerText = data.counts.both;
            if(document.getElementById('countWifi')) document.getElementById('countWifi').innerText = data.counts.wifi;
        }
    })
    .catch(err => console.error('Error loading records:', err));
}

function openAddRecordModal() {
    document.getElementById('recordForm').reset();
    document.getElementById('rec_id').value = '';
    document.getElementById('imagePreviewContainer').style.display = 'none';
    document.getElementById('recordModalTitle').innerText = 'গ্রাহক নম্বর যোগ করুন';
    new bootstrap.Modal(document.getElementById('recordModal')).show();
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

function openEditRecordModal(id) {
    fetch(`/api/get_record/${id}`)
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            let r = data.record;
            document.getElementById('rec_id').value = r.id;
            document.getElementById('rec_name').value = r.customer_name;
            document.getElementById('rec_mobile').value = r.mobile || '';
            document.getElementById('rec_service').value = r.service_type;
            document.getElementById('rec_conn').value = r.connection_num || '';
            document.getElementById('rec_address').value = r.address || '';
            document.getElementById('rec_note').value = r.note || '';
            
            if(r.record_image) {
                document.getElementById('recImagePreview').src = r.record_image;
                document.getElementById('imagePreviewContainer').style.display = 'block';
            } else {
                document.getElementById('imagePreviewContainer').style.display = 'none';
            }
            
            document.getElementById('recordModalTitle').innerText = 'গ্রাহক নম্বর পরিবর্তন করুন';
            new bootstrap.Modal(document.getElementById('recordModal')).show();
        }
    });
}

function saveRecord(e) {
    e.preventDefault();
    let formData = new FormData(document.getElementById('recordForm'));
    fetch('/api/save_record', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            bootstrap.Modal.getInstance(document.getElementById('recordModal')).hide();
            loadRecords();
        } else {
            alert(data.message || 'সংরক্ষণ করতে সমস্যা হয়েছে!');
        }
    });
}

function deleteRecord(id) {
    if(confirm('আপনি কি নিশ্চিত এই নম্বরটি ডিলিট করতে চান?')) {
        let secPass = prompt('নিরাপত্তা পাসওয়ার্ড দিন:');
        if(!secPass) return;
        fetch(`/api/delete_record/${id}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({security_password: secPass})
        })
        .then(res => res.json())
        .then(data => {
            if(data.success) {
                loadRecords();
            } else {
                alert(data.message);
            }
        });
    }
}

function openCustomerDetails(id) {
    fetch(`/api/get_record/${id}`)
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            let r = data.record;
            let imgHtml = r.record_image ? `<div class="mt-3 text-center"><p class="text-warning mb-1">যুক্ত করা ছবি / ডকুমেন্ট:</p><a href="${r.record_image}" target="_blank"><img src="${r.record_image}" style="max-width: 100%; max-height: 200px; border-radius: 8px; border: 1px solid #34d399;"></a></div>` : '';
            let html = `
                <p><strong>গ্রাহকের নাম:</strong> ${r.customer_name}</p>
                <p><strong>মোবাইল:</strong> ${r.mobile || '-'}</p>
                <p><strong>সেবার ধরন:</strong> ${r.service_type}</p>
                <p><strong>সংযোগ নম্বর:</strong> ${r.connection_num || '-'}</p>
                <p><strong>ঠিকানা:</strong> ${r.address || '-'}</p>
                <p><strong>নোট:</strong> ${r.note || '-'}</p>
                <p><strong>যুক্ত করেছেন:</strong> ${r.added_by}</p>
                <p><strong>তারিখ ও সময়:</strong> ${r.created_at}</p>
                ${imgHtml}
            `;
            document.getElementById('customerDetailsBody').innerHTML = html;
            new bootstrap.Modal(document.getElementById('customerDetailsModal')).show();
        }
    });
}

function openUserListModal() {
    document.getElementById('recordsSection').style.display = 'none';
    document.getElementById('userListSection').style.display = 'block';
    
    fetch('/api/get_users')
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.users.forEach(u => {
            let actionBtn = '';
            if(data.is_main_admin && u.username !== 'Khushbu23') {
                actionBtn = `<button class="btn btn-warning btn-sm me-1" onclick="openEditUserCredentials(${u.id}, '${u.username}')"><i class="fa-solid fa-pen"></i></button>
                             <button class="btn btn-danger btn-sm" onclick="deleteUserAccount(${u.id})"><i class="fa-solid fa-trash"></i></button>`;
            }
            html += `<tr>
                <td>${u.name}</td>
                <td>${u.username}</td>
                <td>${u.email || '-'}</td>
                <td>${u.phone || '-'}</td>
                <td>${u.raw_pass || '***'}</td>
                <td><span class="badge bg-secondary">${u.role}</span></td>
                <td><span class="badge bg-${u.status === 'active' ? 'success' : 'warning'}">${u.status}</span></td>
                <td>${actionBtn}</td>
            </tr>`;
        });
        document.getElementById('userTableBody').innerHTML = html;
    });
}

function openCreateUserModal() {
    new bootstrap.Modal(document.getElementById('createUserModal')).show();
}

function openRegisterModal() {
    new bootstrap.Modal(document.getElementById('registerModal')).show();
}

function openEditUserCredentials(id, uname) {
    document.getElementById('edit_user_id').value = id;
    document.getElementById('edit_username').value = uname;
    document.getElementById('edit_password').value = '';
    new bootstrap.Modal(document.getElementById('editUserModal')).show();
}

function deleteUserAccount(id) {
    if(confirm('এই ইউজার অ্যাকাউন্টটি ডিলিট করতে চান?')) {
        fetch(`/api/delete_user/${id}`, {method: 'POST'})
        .then(res => res.json())
        .then(data => {
            if(data.success) openUserListModal();
            else alert(data.message);
        });
    }
}

function openAccountRequestsModal() {
    fetch('/api/get_account_requests')
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.requests.forEach(r => {
            html += `<tr>
                <td>${r.name}</td>
                <td>${r.username}</td>
                <td>${r.email}</td>
                <td>${r.phone}</td>
                <td>${r.raw_pass}</td>
                <td>${r.created_at}</td>
                <td>
                    <button class="btn btn-success btn-sm me-1" onclick="approveUser(${r.id})">অনুমোদন</button>
                    <button class="btn btn-danger btn-sm" onclick="rejectUser(${r.id})">বাতিল</button>
                </td>
            </tr>`;
        });
        document.getElementById('requestTableBody').innerHTML = html || '<tr><td colspan="7" class="text-center text-muted">কোনো রিকোয়েস্ট নেই</td></tr>';
        new bootstrap.Modal(document.getElementById('accountRequestsModal')).show();
    });
}

function approveUser(id) {
    fetch(`/api/approve_user/${id}`, {method: 'POST'}).then(() => {
        openAccountRequestsModal();
        checkGlobalNotifications();
    });
}

function rejectUser(id) {
    fetch(`/api/reject_user/${id}`, {method: 'POST'}).then(() => {
        openAccountRequestsModal();
        checkGlobalNotifications();
    });
}

function openNotificationModal() {
    fetch('/api/get_notifications')
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.notifications.forEach(n => {
            let actionBtn = '';
            if(n.type === 'message') {
                actionBtn = `<button class="btn btn-sm btn-green-gold float-end" onclick="bootstrap.Modal.getInstance(document.getElementById('notificationModal')).hide(); openMessengerModal(); selectUserChat('${n.sender}', '${n.sender_name}')">উত্তর দিন</button>`;
            } else if(n.type === 'request') {
                actionBtn = `<button class="btn btn-sm btn-success float-end" onclick="bootstrap.Modal.getInstance(document.getElementById('notificationModal')).hide(); openAccountRequestsModal();">অনুমোদন প্যানেল</button>`;
            }
            html += `<div class="list-group-item bg-transparent text-white border-bottom border-success py-2">
                <div class="d-flex w-100 justify-content-between align-items-center">
                    <h6 class="mb-1 text-warning">${n.title}</h6>
                    <small>${n.time}</small>
                </div>
                <p class="mb-1">${n.body}</p>
                ${actionBtn}
            </div>`;
        });
        document.getElementById('notificationList').innerHTML = html || '<p class="text-muted text-center">কোনো নতুন নোটিফিকেশন নেই।</p>';
        new bootstrap.Modal(document.getElementById('notificationModal')).show();
    });
}

function openProfileModal() {
    new bootstrap.Modal(document.getElementById('profileModal')).show();
}

function previewAvatar(event) {
    let reader = new FileReader();
    reader.onload = function(){
        let output = document.getElementById('profilePreviewImg');
        output.src = reader.result;
    };
    reader.readAsDataURL(event.target.files[0]);
}

function openTrashBinModal() {
    fetch('/api/get_trash')
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.records.forEach(r => {
            html += `<tr>
                <td>${r[1]}</td>
                <td>${r[4] || '-'}</td>
                <td><button class="btn btn-success btn-sm" onclick="restoreRecord(${r[0]})">রিস্টোর করুন</button></td>
            </tr>`;
        });
        document.getElementById('trashTableBody').innerHTML = html || '<tr><td colspan="3" class="text-center text-muted">রিসাইকেল বিন খালি</td></tr>';
        new bootstrap.Modal(document.getElementById('trashBinModal')).show();
    });
}

function restoreRecord(id) {
    fetch(`/api/restore_record/${id}`, {method: 'POST'})
    .then(res => res.json())
    .then(data => {
        if(data.success) openTrashBinModal();
    });
}

// এডমিন হিস্ট্রি ও অ্যাক্টিভিটি রিপোর্ট (শুধুমাত্র রিয়েল এডমিন দেখতে পাবে)
function openAdminHistoryModal() {
    fetch('/api/admin_history')
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.history.forEach(h => {
            // এডমিন নামের ওপর ক্লিক করলেই তার সুনির্দিষ্ট অ্যাক্টিভিটি ও ডিটেইলস পপআপে দেখাবে
            html += `<tr>
                <td><span class="clickable-name" onclick="openAdminDetail('${h.username}', '${h.name}')">${h.name}</span></td>
                <td>${h.username}</td>
                <td><span class="badge bg-dark text-warning">${h.last_active}</span></td>
                <td><span class="badge bg-info">${h.users_added}</span></td>
                <td><span class="badge bg-warning text-dark">${h.records_added}</span></td>
            </tr>`;
        });
        document.getElementById('adminHistoryTableBody').innerHTML = html;
        new bootstrap.Modal(document.getElementById('adminHistoryModal')).show();
    });
}

// সুনির্দিষ্ট এডমিনের ডিটেইলড অ্যাক্টিভিটি (তারিখ, সময় ও মিনিটসহ)
function openAdminDetail(username, name) {
    fetch(`/api/admin_detail/${username}`)
    .then(res => res.json())
    .then(data => {
        document.getElementById('adminDetailModalTitle').innerText = `এডমিন অ্যাক্টিভিটি: ${name} (@${username})`;
        let html = `<h6 class="text-warning mb-2">এই এডমিন কর্তৃক এন্ট্রি করা সমস্ত রেকর্ড ও কাজের সময়তালিকা:</h6>`;
        html += `<div class="table-responsive"><table class="table table-dark table-striped align-middle"><thead><tr><th>গ্রাহকের নাম</th><th>সেবার ধরন</th><th>সংযোগ নম্বর</th><th>তারিখ ও সময়</th></tr></thead><tbody>`;
        
        if(data.records.length > 0) {
            data.records.forEach(r => {
                html += `<tr><td>${r.customer_name}</td><td>${r.service_type}</td><td>${r.connection_num || '-'}</td><td>${r.created_at}</td></tr>`;
            });
        } else {
            html += `<tr><td colspan="4" class="text-center text-muted">এই এডমিন এখনো কোনো নম্বর বা রেকর্ড যোগ করেননি।</td></tr>`;
        }
        html += `</tbody></table></div>`;
        
        document.getElementById('adminDetailBody').innerHTML = html;
        new bootstrap.Modal(document.getElementById('adminDetailModal')).show();
    });
}

function checkGlobalNotifications() {
    fetch('/api/global_status')
    .then(res => res.json())
    .then(data => {
        let msgBadge = document.getElementById('msgBadge');
        if(data.unread_msg_count > 0) {
            msgBadge.style.display = 'block';
            msgBadge.innerText = data.unread_msg_count;
        } else {
            msgBadge.style.display = 'none';
        }

        let notifBadge = document.getElementById('notifBadge');
        if(notifBadge) {
            let totalNotif = data.pending_requests_count + data.unread_msg_count;
            if(totalNotif > 0) {
                notifBadge.style.display = 'block';
                notifBadge.innerText = totalNotif;
            } else {
                notifBadge.style.display = 'none';
            }
        }

        let reqMenuBadge = document.getElementById('reqMenuBadge');
        if(reqMenuBadge) {
            if(data.pending_requests_count > 0) {
                reqMenuBadge.style.display = 'inline';
                reqMenuBadge.innerText = data.pending_requests_count;
            } else {
                reqMenuBadge.style.display = 'none';
            }
        }

        let banner = document.getElementById('latestGroupAnnouncement');
        let bannerText = document.getElementById('announcementText');
        if(data.latest_group_msg && banner && bannerText) {
            bannerText.innerHTML = `<strong>${data.latest_group_msg.sender}:</strong> ${data.latest_group_msg.message}`;
            banner.style.display = 'block';
        }
    });
}

function openMessengerModal() {
    new bootstrap.Modal(document.getElementById('messengerModal')).show();
    switchChatTab('users');
    if(chatInterval) clearInterval(chatInterval);
    chatInterval = setInterval(refreshActiveChat, 3000);
}

document.getElementById('messengerModal').addEventListener('hidden.bs.modal', function () {
    if(chatInterval) clearInterval(chatInterval);
    checkGlobalNotifications();
});

function switchChatTab(type) {
    currentChatTabType = type;
    let listContainer = document.getElementById('chatUserList');
    if(type === 'group') {
        currentChatIsGroup = 1;
        currentChatTarget = 'BTCL_GLOBAL_GROUP';
        document.getElementById('activeChatTitle').innerText = 'অফিসিয়াল গ্রুপ চ্যাট';
        
        fetch('/api/check_admin_role')
        .then(res => res.json())
        .then(isAdmin => {
            if(isAdmin) {
                document.getElementById('chatForm').style.display = 'flex';
                document.getElementById('groupPermissionNotice').style.display = 'none';
            } else {
                document.getElementById('chatForm').style.display = 'none';
                document.getElementById('groupPermissionNotice').style.display = 'block';
            }
        });

        listContainer.innerHTML = `<button class="list-group-item list-group-item-action active bg-success text-white border-0 rounded my-1" onclick="selectGroupChat()">👥 কুড়িগ্রাম অফিস গ্রুপ</button>`;
        loadMessages();
    } else {
        currentChatIsGroup = 0;
        document.getElementById('groupPermissionNotice').style.display = 'none';
        fetch('/api/chat_users')
        .then(res => res.json())
        .then(data => {
            let html = '';
            data.users.forEach(u => {
                let badgeHtml = u.unread > 0 ? `<span class="badge bg-danger float-end">${u.unread}</span>` : '';
                html += `<button class="list-group-item list-group-item-action text-white bg-transparent border-bottom border-success mb-1" onclick="selectUserChat('${u.username}', '${u.name}')">👤 ${u.name} ${badgeHtml}</button>`;
            });
            listContainer.innerHTML = html || '<p class="text-muted small p-2">কোনো ইনবক্স নেই</p>';
        });
    }
}

function selectUserChat(username, name) {
    currentChatTarget = username;
    currentChatIsGroup = 0;
    document.getElementById('activeChatTitle').innerText = `ইনবক্স: ${name}`;
    document.getElementById('chatForm').style.display = 'flex';
    document.getElementById('groupPermissionNotice').style.display = 'none';
    
    fetch(`/api/mark_read?sender=${username}`).then(() => {
        loadMessages();
        checkGlobalNotifications();
    });
}

function selectGroupChat() {
    currentChatTarget = 'BTCL_GLOBAL_GROUP';
    currentChatIsGroup = 1;
    document.getElementById('activeChatTitle').innerText = 'অফিসিয়াল গ্রুপ চ্যাট';
    
    fetch('/api/check_admin_role')
    .then(res => res.json())
    .then(isAdmin => {
        if(isAdmin) {
            document.getElementById('chatForm').style.display = 'flex';
            document.getElementById('groupPermissionNotice').style.display = 'none';
        } else {
            document.getElementById('chatForm').style.display = 'none';
            document.getElementById('groupPermissionNotice').style.display = 'block';
        }
    });
    loadMessages();
}

function loadMessages() {
    if(!currentChatTarget) return;
    fetch(`/api/get_messages?target=${encodeURIComponent(currentChatTarget)}&is_group=${currentChatIsGroup}`)
    .then(res => res.json())
    .then(data => {
        let box = document.getElementById('chatMessages');
        let html = '';
        data.messages.forEach(m => {
            let bubbleClass = m.is_mine ? 'msg-outgoing' : 'msg-incoming';
            let senderName = m.is_mine ? 'আপনি' : m.sender_display;
            let fileHtml = m.file_url ? `<a href="${m.file_url}" target="_blank"><img src="${m.file_url}" class="chat-file-preview"></a>` : '';
            let defaultAvatar = 'https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.4.0/svgs/solid/circle-user.svg';
            let profilePic = m.profile_pic ? m.profile_pic : defaultAvatar;

            html += `<div class="message-bubble ${bubbleClass}">
                <img src="${profilePic}" class="msg-avatar">
                <div>
                    <div style="font-size: 11px; font-weight: bold; opacity: 0.9;">${senderName}</div>
                    <div>${m.message || ''}</div>
                    ${fileHtml}
                    <div style="font-size: 9px; text-align: right; opacity: 0.8;">${m.timestamp}</div>
                </div>
            </div>`;
        });
        box.innerHTML = html || '<p class="text-muted text-center m-auto">কোনো মেসেজ নেই।</p>';
        box.scrollTop = box.scrollHeight;
    });
}

function refreshActiveChat() {
    if(document.getElementById('messengerModal').classList.contains('show') && currentChatTarget) {
        loadMessages();
    }
    checkGlobalNotifications();
}

function previewFile() {
    let fileInput = document.getElementById('chatFile');
    let preview = document.getElementById('selectedFilePreview');
    if(fileInput.files.length > 0) {
        preview.style.display = 'block';
        preview.innerText = `ফাইল যুক্ত হয়েছে: ${fileInput.files[0].name}`;
    } else {
        preview.style.display = 'none';
    }
}

function sendMessage(e) {
    e.preventDefault();
    let textInput = document.getElementById('chatInput');
    let fileInput = document.getElementById('chatFile');
    
    let formData = new FormData();
    formData.append('receiver', currentChatTarget);
    formData.append('is_group', currentChatIsGroup);
    formData.append('message', textInput.value);
    if(fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
    }
    
    fetch('/api/send_message', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if(data.success) {
            textInput.value = '';
            fileInput.value = '';
            document.getElementById('selectedFilePreview').style.display = 'none';
            loadMessages();
            checkGlobalNotifications();
        } else {
            alert(data.message || 'মেসেজ পাঠানো যায়নি!');
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    loadRecords();
    checkGlobalNotifications();
    globalPollInterval = setInterval(checkGlobalNotifications, 4000);
});
</script>
</body>
</html>
"""

# Flask Routes for Backend Logic
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ? OR phone = ?", (username, username, username))
    user = cursor.fetchone()
    
    if user and (check_password_hash(user[5], password) or password == user[6]):
        if user[8] != 'active' and user[2] != MAIN_ADMIN_USERNAME:
            conn.close()
            return "অ্যাকাউন্টটি এখনো মেইন এডমিন কর্তৃক অনুমোদিত হয়নি।"
        
        # লগইন করার সাথে সাথে লাস্ট অ্যাক্টিভ টাইম আপডেট
        cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE id = ?", (user[0],))
        conn.commit()
        conn.close()
        
        session['user'] = {
            'id': user[0],
            'name': user[1],
            'username': user[2],
            'email': user[3],
            'phone': user[4],
            'role': user[7],
            'status': user[8],
            'profile_pic': user[9]
        }
        return redirect(url_for('index'))
    conn.close()
    return "লগইন ব্যর্থ হয়েছে! সঠিক তথ্য দিন।"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/search')
def api_search():
    if 'user' not in session:
        return jsonify({'records': [], 'is_admin': False})
    
    user = session['user']
    q = request.args.get('q', '')
    service = request.args.get('service', '')
    sort = request.args.get('sort', 'id_desc')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    query = "SELECT * FROM phone_records WHERE is_deleted = 0"
    params = []
    
    if user['role'] == 'user':
        query += " AND (added_by = ? OR added_by = 'Khushbu23')"
        params.append(user['username'])
        
    if q:
        query += " AND (customer_name LIKE ? OR mobile LIKE ? OR connection_num LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])
        
    if service:
        query += " AND service_type = ?"
        params.append(service)
        
    if sort == 'id_asc':
        query += " ORDER BY id ASC"
    elif sort == 'id_high_low':
        query += " ORDER BY id DESC"
    elif sort == 'name_asc':
        query += " ORDER BY customer_name ASC"
    elif sort == 'name_desc':
        query += " ORDER BY customer_name DESC"
    else:
        query += " ORDER BY id DESC"
        
    cursor.execute(query, params)
    records = cursor.fetchall()
    
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted = 0")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted = 0 AND service_type = 'টেলিফোন নাম্বার'")
    tel = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted = 0 AND service_type = 'টেলিফোন+ওয়াইফাই নম্বর'")
    both = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted = 0 AND service_type = 'ওয়াইফাই নাম্বার'")
    wifi = cursor.fetchone()[0]
    
    conn.close()
    
    is_admin = user['role'] in ['admin', 'main_admin']
    return jsonify({
        'records': records,
        'is_admin': is_admin,
        'counts': {'total': total, 'tel': tel, 'both': both, 'wifi': wifi}
    })

@app.route('/api/get_record/<int:rec_id>')
def get_record(rec_id):
    if 'user' not in session:
        return jsonify({'success': False, 'message': 'অনুমতি নেই!'})
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM phone_records WHERE id = ?", (rec_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        record = {
            'id': row[0],
            'customer_name': row[1],
            'mobile': row[2],
            'service_type': row[3],
            'connection_num': row[4],
            'address': row[5],
            'note': row[6],
            'record_image': row[7],
            'added_by': row[8],
            'created_at': row[10]
        }
        return jsonify({'success': True, 'record': record})
    return jsonify({'success': False})

@app.route('/api/save_record', methods=['POST'])
def save_record():
    if 'user' not in session or session['user']['role'] not in ['admin', 'main_admin']:
        return jsonify({'success': False, 'message': 'অনুমতি নেই!'})
        
    rec_id = request.form.get('id')
    customer_name = request.form.get('customer_name')
    mobile = request.form.get('mobile')
    service_type = request.form.get('service_type')
    connection_num = request.form.get('connection_num')
    address = request.form.get('address')
    note = request.form.get('note')
    added_by = session['user']['username']
    
    record_image = ''
    # ক্যামেরা অথবা গ্যালারি থেকে আপলোড করা ফাইল হ্যান্ডেল করা
    file = None
    if 'record_image_camera' in request.files and request.files['record_image_camera'].filename:
        file = request.files['record_image_camera']
    elif 'record_image_gallery' in request.files and request.files['record_image_gallery'].filename:
        file = request.files['record_image_gallery']
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        record_image = f'/{filepath}'
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # এডমিনের লাস্ট অ্যাক্টিভিটি আপডেট করা
    cursor.execute("UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE username = ?", (added_by,))
    
    if rec_id:
        if record_image:
            cursor.execute('''UPDATE phone_records SET customer_name=?, mobile=?, service_type=?, connection_num=?, address=?, note=?, record_image=? WHERE id=?''',
                           (customer_name, mobile, service_type, connection_num, address, note, record_image, rec_id))
        else:
            cursor.execute('''UPDATE phone_records SET customer_name=?, mobile=?, service_type=?, connection_num=?, address=?, note=? WHERE id=?''',
                           (customer_name, mobile, service_type, connection_num, address, note, rec_id))
    else:
        cursor.execute('''INSERT INTO phone_records (customer_name, mobile, service_type, connection_num, address, note, record_image, added_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                       (customer_name, mobile, service_type, connection_num, address, note, record_image, added_by))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/delete_record/<int:rec_id>', methods=['POST'])
def delete_record(rec_id):
    if 'user' not in session or session['user']['role'] not in ['admin', 'main_admin']:
        return jsonify({'success': False, 'message': 'অনুমতি নেই!'})
        
    data = request.get_json()
    if data.get('security_password') != SECURITY_DELETE_PASSWORD:
        return jsonify({'success': False, 'message': 'ভুল নিরাপত্তা পাসওয়ার্ড!'})
        
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE phone_records SET is_deleted = 1 WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/create_user', methods=['POST'])
def create_user():
    if 'user' not in session or session['user']['role'] not in ['admin', 'main_admin']:
        return redirect(url_for('index'))
        
    name = request.form.get('name')
    username = request.form.get('username')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    # সাব-এডমিন বা সাধারণ ইউজাররা কোনো নতুন এডমিন অ্যাড করতে পারবেন না, কেবল সাধারণ ইউজার তৈরি করতে পারবেন
    role = 'user'
    
    hashed_pw = generate_password_hash(password)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO users (name, username, email, phone, password, raw_pass, role, status, added_by) VALUES (?, ?, ?, ?, ?, ?, ?, 'active', ?)''',
                       (name, username, email, phone, hashed_pw, password, role, session['user']['username']))
        conn.commit()
    except Exception as e:
        print("Error:", e)
    conn.close()
    return redirect(url_for('index'))

@app.route('/api/get_users')
def get_users():
    if 'user' not in session:
        return jsonify({'users': [], 'is_main_admin': False})
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, phone, raw_pass, role, status FROM users WHERE is_deleted = 0")
    users = []
    for row in cursor.fetchall():
        users.append({
            'id': row[0], 'name': row[1], 'username': row[2], 'email': row[3], 'phone': row[4], 'raw_pass': row[5], 'role': row[6], 'status': row[7]
        })
    conn.close()
    is_main_admin = session['user']['username'] == MAIN_ADMIN_USERNAME
    return jsonify({'users': users, 'is_main_admin': is_main_admin})

@app.route('/api/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return jsonify({'success': False, 'message': 'অনুমতি নেই'})
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_deleted = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

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
        cursor.execute('''INSERT INTO users (name, username, email, phone, password, raw_pass, role, status) VALUES (?, ?, ?, ?, ?, ?, 'user', 'pending')''',
                       (name, username, email, phone, hashed_pw, password))
        conn.commit()
    except:
        pass
    conn.close()
    return redirect(url_for('index'))

@app.route('/api/get_account_requests')
def get_account_requests():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return jsonify({'requests': []})
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, email, phone, raw_pass, created_at FROM users WHERE status = 'pending' AND is_deleted = 0")
    reqs = []
    for r in cursor.fetchall():
        reqs.append({'id': r[0], 'name': r[1], 'username': r[2], 'email': r[3], 'phone': r[4], 'raw_pass': r[5], 'created_at': r[6]})
    conn.close()
    return jsonify({'requests': reqs})

@app.route('/api/approve_user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return jsonify({'success': False})
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET status = 'active' WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/reject_user/<int:user_id>', methods=['POST'])
def reject_user(user_id):
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return jsonify({'success': False})
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_deleted = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/check_admin_role')
def check_admin_role():
    if 'user' not in session:
        return jsonify(False)
    role = session['user']['role']
    return jsonify(role in ['admin', 'main_admin'])

@app.route('/api/chat_users')
def chat_users():
    if 'user' not in session:
        return jsonify({'users': []})
    current_user = session['user']
    current_uname = current_user['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if current_user['role'] in ['admin', 'main_admin']:
        cursor.execute("SELECT username, name FROM users WHERE username != ? AND is_deleted = 0", (current_uname,))
    else:
        cursor.execute("SELECT username, name FROM users WHERE role IN ('admin', 'main_admin') AND is_deleted = 0", ())
        
    users = []
    for r in cursor.fetchall():
        uname = r[0]
        cursor.execute("SELECT COUNT(*) FROM messages WHERE sender = ? AND receiver = ? AND is_read = 0", (uname, current_uname))
        unread = cursor.fetchone()[0]
        users.append({'username': uname, 'name': r[1], 'unread': unread})
    conn.close()
    return jsonify({'users': users})

@app.route('/api/mark_read')
def mark_read():
    if 'user' not in session:
        return jsonify({'success': False})
    current_uname = session['user']['username']
    sender = request.args.get('sender')
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET is_read = 1 WHERE sender = ? AND receiver = ? AND is_read = 0", (sender, current_uname))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/get_messages')
def get_messages():
    if 'user' not in session:
        return jsonify({'messages': []})
    
    current_user = session['user']
    current_uname = current_user['username']
    is_current_admin = current_user['role'] in ['admin', 'main_admin']
    target = request.args.get('target')
    is_group = int(request.args.get('is_group', 0))
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if is_group:
        cursor.execute("""
            SELECT m.sender, m.receiver, m.message, m.file_url, m.timestamp, u.profile_pic, u.role, u.name 
            FROM messages m 
            LEFT JOIN users u ON m.sender = u.username 
            WHERE m.is_group = 1 ORDER BY m.id ASC
        """)
    else:
        cursor.execute("UPDATE messages SET is_read = 1 WHERE sender = ? AND receiver = ? AND is_read = 0", (target, current_uname))
        conn.commit()
        
        cursor.execute("""
            SELECT m.sender, m.receiver, m.message, m.file_url, m.timestamp, u.profile_pic, u.role, u.name 
            FROM messages m 
            LEFT JOIN users u ON m.sender = u.username 
            WHERE m.is_group = 0 AND ((m.sender = ? AND m.receiver = ?) OR (m.sender = ? AND m.receiver = ?))
            ORDER BY m.id ASC
        """, (current_uname, target, target, current_uname))
        
    messages = []
    for r in cursor.fetchall():
        sender_username = r[0]
        sender_role = r[6]
        sender_name_db = r[7]
        profile_pic = r[5]
        
        if not is_current_admin:
            if sender_username == current_uname:
                sender_display = 'আপনি'
            elif sender_role in ['admin', 'main_admin']:
                sender_display = 'এডমিন'
            else:
                sender_display = sender_name_db or sender_username
        else:
            if sender_username == current_uname:
                sender_display = 'আপনি'
            elif sender_username == MAIN_ADMIN_USERNAME:
                sender_display = f"রিয়েল এডমিন ({sender_name_db})"
            elif sender_role in ['admin', 'main_admin']:
                sender_display = f"এডমিন ({sender_name_db})"
            else:
                sender_display = sender_name_db or sender_username

        messages.append({
            'sender': sender_username,
            'receiver': r[1],
            'message': r[2],
            'file_url': r[3],
            'timestamp': r[4],
            'profile_pic': profile_pic,
            'sender_display': sender_display,
            'is_mine': (sender_username == current_uname)
        })
    conn.close()
    return jsonify({'messages': messages})

@app.route('/api/send_message', methods=['POST'])
def send_message():
    if 'user' not in session:
        return jsonify({'success': False})
    
    current_user = session['user']
    current_uname = current_user['username']
    receiver = request.form.get('receiver')
    is_group = int(request.form.get('is_group', 0))
    message = request.form.get('message', '')
    
    if is_group == 1 and current_user['role'] not in ['admin', 'main_admin']:
        return jsonify({'success': False, 'message': 'সাধারণ ইউজাররা গ্রুপে মেসেজ পাঠাতে পারবেন না!'})
    
    file_url = ''
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            file_url = f'/{filepath}'
            
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO messages (sender, receiver, message, file_url, is_group, is_read) VALUES (?, ?, ?, ?, ?, 0)''',
                   (current_uname, receiver, message, file_url, is_group))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/global_status')
def global_status():
    if 'user' not in session:
        return jsonify({'unread_msg_count': 0, 'pending_requests_count': 0, 'latest_group_msg': None})
    
    current_user = session['user']
    current_uname = current_user['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM messages WHERE receiver = ? AND is_group = 0 AND is_read = 0", (current_uname,))
    unread_msg_count = cursor.fetchone()[0]
    
    pending_requests_count = 0
    if current_uname == MAIN_ADMIN_USERNAME:
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'pending' AND is_deleted = 0")
        pending_requests_count = cursor.fetchone()[0]
        
    cursor.execute("SELECT sender, message, timestamp FROM messages WHERE is_group = 1 ORDER BY id DESC LIMIT 1")
    g_msg = cursor.fetchone()
    latest_group_msg = None
    if g_msg:
        latest_group_msg = {'sender': g_msg[0], 'message': g_msg[1], 'timestamp': g_msg[2]}
        
    conn.close()
    return jsonify({
        'unread_msg_count': unread_msg_count,
        'pending_requests_count': pending_requests_count,
        'latest_group_msg': latest_group_msg
    })

@app.route('/api/get_notifications')
def get_notifications():
    if 'user' not in session:
        return jsonify({'notifications': []})
    
    current_user = session['user']
    current_uname = current_user['username']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    notifications = []
    
    if current_uname == MAIN_ADMIN_USERNAME:
        cursor.execute("SELECT id, name, username, created_at FROM users WHERE status = 'pending' AND is_deleted = 0")
        for r in cursor.fetchall():
            notifications.append({
                'type': 'request',
                'title': 'নতুন অ্যাকাউন্ট রেজিস্ট্রেশন রিকোয়েস্ট',
                'body': f'{r[1]} ({r[2]}) অ্যাকাউন্ট অনুমোদনের অপেক্ষা করছে।',
                'time': r[3]
            })
            
    cursor.execute("""
        SELECT m.sender, u.name, m.message, m.timestamp FROM messages m 
        JOIN users u ON m.sender = u.username
        WHERE m.receiver = ? AND m.is_group = 0 AND m.is_read = 0
        ORDER BY m.id DESC
    """, (current_uname,))
    for r in cursor.fetchall():
        notifications.append({
            'type': 'message',
            'title': f'নতুন মেসেজ: {r[1]} (@{r[0]})',
            'body': r[2] or '[ফাইল সংযুক্ত]',
            'time': r[3],
            'sender': r[0],
            'sender_name': r[1]
        })
        
    conn.close()
    return jsonify({'notifications': notifications})

@app.route('/api/get_trash')
def get_trash():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM phone_records WHERE is_deleted = 1")
    records = cursor.fetchall()
    conn.close()
    return jsonify({'records': records})

@app.route('/api/restore_record/<int:rec_id>', methods=['POST'])
def restore_record(rec_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE phone_records SET is_deleted = 0 WHERE id = ?", (rec_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/admin_history')
def admin_history():
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return jsonify({'history': []})
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, username, last_active FROM users WHERE role IN ('admin', 'main_admin') AND is_deleted = 0")
    history = []
    for r in cursor.fetchall():
        uname = r[1]
        cursor.execute("SELECT COUNT(*) FROM phone_records WHERE added_by = ? AND is_deleted = 0", (uname,))
        recs_added = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM users WHERE added_by = ? AND is_deleted = 0", (uname,))
        users_added = cursor.fetchone()[0]
        history.append({
            'name': r[0], 'username': uname, 'last_active': r[2], 'users_added': users_added, 'records_added': recs_added
        })
    conn.close()
    return jsonify({'history': history})

@app.route('/api/admin_detail/<username>')
def admin_detail(username):
    if 'user' not in session or session['user']['username'] != MAIN_ADMIN_USERNAME:
        return jsonify({'records': []})
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT customer_name, service_type, connection_num, created_at FROM phone_records WHERE added_by = ? AND is_deleted = 0 ORDER BY id DESC", (username,))
    records = []
    for r in cursor.fetchall():
        records.append({
            'customer_name': r[0],
            'service_type': r[1],
            'connection_num': r[2],
            'created_at': r[3]
        })
    conn.close()
    return jsonify({'records': records})

@app.route('/update_profile_pic', methods=['POST'])
def update_profile_pic():
    if 'user' not in session:
        return redirect(url_for('index'))
    user_id = session['user']['id']
    
    profile_pic_url = ''
    if 'profile_pic' in request.files:
        file = request.files['profile_pic']
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            profile_pic_url = f'/{filepath}'
            
    if profile_pic_url:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET profile_pic = ? WHERE id = ?", (profile_pic_url, user_id))
        conn.commit()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        session['user'] = {
            'id': user[0],
            'name': user[1],
            'username': user[2],
            'email': user[3],
            'phone': user[4],
            'role': user[7],
            'status': user[8],
            'profile_pic': user[9]
        }
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)