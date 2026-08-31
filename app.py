import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "super_secret_btcl_kurigram_key_2026")

ADMIN_USERNAME = "Khushbu23"
ADMIN_PASSWORD = "01751947523"
ADMIN_SECURITY_CODE = "137955"

# --- Database Setup ---
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
            sender_username TEXT,
            receiver_username TEXT,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Notifications Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT, -- 'user_reg' or 'message'
            reference_id INTEGER,
            message TEXT,
            is_read INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create Default Admin Account
    cursor.execute("SELECT * FROM users WHERE username = ?", (ADMIN_USERNAME,))
    if not cursor.fetchone():
        hashed_pw = generate_password_hash(ADMIN_PASSWORD)
        cursor.execute("INSERT INTO users (name, username, email, phone, password, status) VALUES (?, ?, ?, ?, ?, ?)",
                       ('Md Khushbu Alom', ADMIN_USERNAME, 'admin@btcl.com', '01751947523', hashed_pw, 'active'))

    conn.commit()
    conn.close()

init_db()

# --- Combined HTML Template ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #121212; color: #fff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { background-color: #1e1e1e; color: white; border: 1px solid #333; }
        .form-label { color: #00e676; font-weight: 500; margin-bottom: 2px; }
        .form-control, .form-select { background-color: #2b2b2b; color: #fff; border: 1px solid #444; }
        .form-control:focus, .form-select:focus { background-color: #333; color: #fff; border-color: #00e676; box-shadow: none; }
        .btn-success-custom { background-color: #00e676; border: none; color: #000; font-weight: bold; }
        .btn-success-custom:hover { background-color: #00c853; color: #000; }
        .stat-card { background-color: #1a271d; border: 1px solid #00e676; text-align: center; cursor: pointer; padding: 10px; border-radius: 8px; }
        .stat-card:hover { background-color: #253b2a; }
        .stat-number { font-size: 22px; font-weight: bold; color: #00e676; }
        .stat-label { font-size: 12px; color: #ccc; }
        .offcanvas { background-color: #181818; color: white; }
        .offcanvas .btn-close { filter: invert(1); }
        .nav-link-custom { color: #ddd; padding: 10px 15px; border-bottom: 1px solid #2a2a2a; display: block; text-decoration: none; }
        .nav-link-custom:hover { background-color: #2b2b2b; color: #00e676; }
        .badge-notification { position: absolute; top: 2px; right: 2px; font-size: 10px; }
    </style>
</head>
<body>

<!-- Header Banner -->
<div class="bg-dark text-center py-2 border-bottom border-success">
    <h3 class="m-0 text-success fw-bold">BTCL, কুড়িগ্রাম</h3>
    <small class="text-light">Md Khushbu Alom</small>
</div>

<div class="container py-3">
    {% if session.get('user') %}
    <!-- Top Action Bar -->
    <div class="d-flex justify-content-between align-items-center mb-3">
        <div class="d-flex align-items-center gap-2">
            <button class="btn btn-outline-success btn-sm" data-bs-toggle="offcanvas" data-bs-target="#sidebarMenu">
                <i class="fa-solid fa-bars"></i> মেনু
            </button>
            <a href="/" class="btn btn-outline-light btn-sm"><i class="fa-solid fa-house"></i> হোম</a>
        </div>
        
        <div class="d-flex align-items-center gap-2">
            <!-- Notifications Dropdown -->
            <div class="dropdown">
                <button class="btn btn-outline-warning btn-sm position-relative" id="notifBtn" data-bs-toggle="dropdown">
                    <i class="fa-solid fa-bell"></i>
                    <span id="notifBadge" class="badge bg-danger rounded-pill badge-notification" style="display:none;">0</span>
                </button>
                <ul class="dropdown-menu dropdown-menu-end dropdown-menu-dark p-2" id="notifList" style="width: 300px; max-height: 300px; overflow-y: auto;">
                    <li><small class="text-muted">কোনো নতুন নোটিফিকেশন নেই</small></li>
                </ul>
            </div>

            <!-- Profile Badge -->
            {% if session['user']['is_admin'] %}
                <span class="badge bg-danger p-2"><i class="fa-solid fa-user-shield"></i> ADMIN</span>
            {% else %}
                <span class="badge bg-primary p-2"><i class="fa-solid fa-user"></i> {{ session['user']['name'] }}</span>
            {% endif %}
            <a href="/logout" class="btn btn-danger btn-sm"><i class="fa-solid fa-right-from-bracket"></i></a>
        </div>
    </div>

    <!-- Live Search & Filter -->
    <div class="row g-2 mb-3">
        <div class="col-md-8">
            <label class="form-label">খুঁজুন (Search)</label>
            <input type="text" id="searchInput" class="form-control" placeholder="নাম, নম্বর, ঠিকানা বা নোট দিয়ে খুঁজুন..." onkeyup="loadRecords()">
        </div>
        <div class="col-md-4">
            <label class="form-label">সাজানো (Sort By)</label>
            <select id="sortSelect" class="form-select" onchange="loadRecords()">
                <option value="default">ডিফল্ট</option>
                <option value="num_asc">নম্বর (ছোট থেকে বড়)</option>
                <option value="num_desc">নম্বর (বড় থেকে ছোট)</option>
                <option value="name_asc">নাম (A to Z)</option>
                <option value="name_desc">নাম (Z to A)</option>
            </select>
        </div>
    </div>

    <!-- Summary Counters (Admin Only Sees Bills/Total Cards) -->
    <div class="row g-2 mb-3">
        <div class="col" onclick="filterService('')">
            <div class="stat-card">
                <div class="stat-number" id="countTotal">0</div>
                <div class="stat-label">টোটাল বিল/নম্বর</div>
            </div>
        </div>
        <div class="col" onclick="filterService('টেলিফোন')">
            <div class="stat-card">
                <div class="stat-number" id="countTel">0</div>
                <div class="stat-label">টেলিফোন</div>
            </div>
        </div>
        <div class="col" onclick="filterService('টেলিফোন+ওয়াইফাই')">
            <div class="stat-card">
                <div class="stat-number" id="countBoth">0</div>
                <div class="stat-label">টেলিফোন+ওয়াইফাই</div>
            </div>
        </div>
        <div class="col" onclick="filterService('ওয়াইফাই')">
            <div class="stat-card">
                <div class="stat-number" id="countWifi">0</div>
                <div class="stat-label">ওয়াইফাই</div>
            </div>
        </div>
        {% if session['user']['is_admin'] %}
        <div class="col" onclick="showUsersTab()">
            <div class="stat-card">
                <div class="stat-number" id="countUsers">0</div>
                <div class="stat-label">টোটাল ইউজার</div>
            </div>
        </div>
        {% endif %}
    </div>

    <!-- Dynamic Section: Phone Records Table -->
    <div id="recordsSection" class="card p-3 mb-4">
        <h5 class="text-success border-bottom pb-2">গ্রাহক ও সংযোগ তালিকা</h5>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle mt-2">
                <thead>
                    <tr>
                        <th>ক্র.নং</th>
                        <th>নাম</th>
                        <th>মোবাইল</th>
                        <th>সেবার ধরন</th>
                        <th>সংযোগ নম্বর</th>
                        <th>ঠিকানা</th>
                        <th>নোট</th>
                        {% if session['user']['is_admin'] %}<th>অ্যাকশন</th>{% endif %}
                    </tr>
                </thead>
                <tbody id="recordsTableBody"></tbody>
            </table>
        </div>
    </div>

    <!-- User Management Table (Admin Only) -->
    {% if session['user']['is_admin'] %}
    <div id="usersSection" class="card p-3 mb-4" style="display:none;">
        <h5 class="text-warning border-bottom pb-2">নিবন্ধিত ইউজার তালিকা</h5>
        <div class="table-responsive">
            <table class="table table-dark table-striped align-middle">
                <thead>
                    <tr>
                        <th>নাম</th>
                        <th>ইমেইল</th>
                        <th>ফোন</th>
                        <th>ইউজারনেম</th>
                        <th>স্ট্যাটাস</th>
                        <th>অ্যাকশন</th>
                    </tr>
                </thead>
                <tbody id="usersTableBody"></tbody>
            </table>
        </div>
    </div>
    {% endif %}

    <!-- Add Phone Record Section -->
    <div id="addRecordSection" class="card p-3 mb-4">
        <h5 class="text-success border-bottom pb-2">নতুন নম্বর এড করুন</h5>
        <form action="/add_record" method="POST" class="row g-3">
            <div class="col-md-6">
                <label class="form-label">গ্রাহকের নাম *</label>
                <input type="text" name="customer_name" class="form-control" placeholder="গ্রাহকের নাম লিখুন" required>
            </div>
            <div class="col-md-6">
                <label class="form-label">মোবাইল নম্বর (ঐচ্ছিক)</label>
                <input type="text" name="mobile" class="form-control" placeholder="মোবাইল নম্বর">
            </div>
            <div class="col-md-6">
                <label class="form-label">সেবার ধরন *</label>
                <select name="service_type" class="form-select" required>
                    <option value="টেলিফোন নম্বর">টেলিফোন নম্বর</option>
                    <option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই নম্বর</option>
                    <option value="ওয়াইফাই নম্বর">ওয়াইফাই নম্বর</option>
                </select>
            </div>
            <div class="col-md-6">
                <label class="form-label">সংযোগ নম্বর</label>
                <input type="text" name="connection_num" class="form-control" placeholder="সংযোগ নম্বর লিখুন">
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
                <button type="submit" class="btn btn-success-custom w-100 py-2">সংরক্ষণ করুন</button>
            </div>
        </form>
    </div>

    {% else %}

    <!-- Auth Section (Login & Registration) -->
    <div class="row justify-content-center mt-4">
        <div class="col-md-6">
            <div class="card p-4">
                <ul class="nav nav-tabs nav-justified mb-3" id="authTab">
                    <li class="nav-item">
                        <button class="nav-link active fw-bold text-success" data-bs-toggle="tab" data-bs-target="#loginTab">লগইন</button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link fw-bold text-success" data-bs-toggle="tab" data-bs-target="#regTab">রেজিস্ট্রেশন</button>
                    </li>
                </ul>
                <div class="tab-content">
                    <!-- Login Form -->
                    <div class="tab-pane fade show active" id="loginTab">
                        <form action="/login" method="POST">
                            <div class="mb-3">
                                <label class="form-label">ইউজারনেম / জিমেইল / ফোন</label>
                                <input type="text" name="username" class="form-control" placeholder="ইউজারনেম বা ফোন নাম্বার দিন" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">পাসওয়ার্ড</label>
                                <input type="password" name="password" class="form-control" placeholder="পাসওয়ার্ড দিন" required>
                            </div>
                            <button type="submit" class="btn btn-success-custom w-100 py-2">লগইন করুন</button>
                        </form>
                    </div>

                    <!-- Registration Form -->
                    <div class="tab-pane fade" id="regTab">
                        <form action="/register" method="POST">
                            <div class="mb-2">
                                <label class="form-label">আপনার নাম</label>
                                <input type="text" name="name" class="form-control" placeholder="পূর্ণ নাম" required>
                            </div>
                            <div class="mb-2">
                                <label class="form-label">সঠিক জিমেইল আইডি</label>
                                <input type="email" name="email" class="form-control" placeholder="example@gmail.com" required>
                            </div>
                            <div class="mb-2">
                                <label class="form-label">১১ ডিজিট মোবাইল নম্বর</label>
                                <input type="text" name="phone" class="form-control" placeholder="017xxxxxxxx" required>
                            </div>
                            <div class="mb-2">
                                <label class="form-label">ইউজারনেম</label>
                                <input type="text" name="username" class="form-control" placeholder="ইউজারনেম" required>
                            </div>
                            <div class="mb-2">
                                <label class="form-label">পাসওয়ার্ড</label>
                                <input type="password" name="password" class="form-control" placeholder="পাসওয়ার্ড" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">কনফার্ম পাসওয়ার্ড</label>
                                <input type="password" name="confirm_password" class="form-control" placeholder="আবার পাসওয়ার্ড লিখুন" required>
                            </div>
                            <button type="submit" class="btn btn-success-custom w-100 py-2">রেজিস্ট্রেশন করুন</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    {% endif %}
</div>

<!-- Offcanvas 9-Option Menu -->
<div class="offcanvas offcanvas-start" id="sidebarMenu">
  <div class="offcanvas-header border-bottom border-secondary">
    <h5 class="offcanvas-title text-success">প্রধান মেনু</h5>
    <button type="button" class="btn-close" data-bs-dismiss="offcanvas"></button>
  </div>
  <div class="offcanvas-body p-0">
    <a href="#" class="nav-link-custom" onclick="showSection('records')">১. ওভারভিউ ও ডাটা</a>
    <a href="#" class="nav-link-custom" onclick="showNotifModal()">২. নোটিফিকেশন হিস্টরি</a>
    <a href="#" class="nav-link-custom" onclick="showSection('add')">৩. নম্বর এড করুন</a>
    {% if session.get('user', {}).get('is_admin') %}
    <a href="#" class="nav-link-custom" onclick="showAdminUserCreate()">৪. নতুন ইউজার তৈরি করুন</a>
    <a href="#" class="nav-link-custom" onclick="showSection('users')">৫. নিবন্ধিত ইউজার তথ্য</a>
    <a href="#" class="nav-link-custom" onclick="showSecModal()">৬. সিকিউরিটি ও পাসওয়ার্ড</a>
    <a href="#" class="nav-link-custom" onclick="showDeletedNumbers()">৭. ডিলিট হওয়া নম্বর</a>
    <a href="#" class="nav-link-custom" onclick="showDeletedUsers()">৮. ডিলিট হওয়া ইউজার</a>
    {% endif %}
    <a href="#" class="nav-link-custom" onclick="showMessenger()">৯. মেসেঞ্জার</a>
    <a href="/logout" class="nav-link-custom text-danger fw-bold mt-3">লগআউট</a>
  </div>
</div>

<!-- Modal: Delete Confirmation (Security Pin Required) -->
<div class="modal fade" id="deleteModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content bg-dark text-white">
      <form id="deleteForm" method="POST">
          <div class="modal-header border-secondary"><h5 class="modal-title text-danger">ডিলেট নিশ্চিতকরণ</h5></div>
          <div class="modal-body">
            <label class="form-label">এডমিন সিকিউরিটি পিন দিন:</label>
            <input type="password" name="security_code" class="form-control" required placeholder="সিকিউরিটি পিন">
          </div>
          <div class="modal-footer border-secondary">
            <button type="submit" class="btn btn-danger">ডিলেট নিশ্চিত করুন</button>
          </div>
      </form>
    </div>
  </div>
</div>

<!-- Modal: Edit Record (No Pin Required) -->
<div class="modal fade" id="editModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content bg-dark text-white">
      <form id="editForm" method="POST">
          <div class="modal-header border-secondary"><h5 class="modal-title text-success">ডাটা এডিট করুন</h5></div>
          <div class="modal-body row g-2">
            <div class="col-12">
                <label class="form-label">গ্রাহকের নাম *</label>
                <input type="text" id="edit_name" name="customer_name" class="form-control" required>
            </div>
            <div class="col-12">
                <label class="form-label">মোবাইল নম্বর</label>
                <input type="text" id="edit_mobile" name="mobile" class="form-control">
            </div>
            <div class="col-12">
                <label class="form-label">সেবার ধরন</label>
                <select id="edit_service" name="service_type" class="form-select">
                    <option value="টেলিফোন নম্বর">টেলিফোন নম্বর</option>
                    <option value="টেলিফোন+ওয়াইফাই নম্বর">টেলিফোন+ওয়াইফাই নম্বর</option>
                    <option value="ওয়াইফাই নম্বর">ওয়াইফাই নম্বর</option>
                </select>
            </div>
            <div class="col-12">
                <label class="form-label">সংযোগ নম্বর</label>
                <input type="text" id="edit_conn" name="connection_num" class="form-control">
            </div>
            <div class="col-12">
                <label class="form-label">ঠিকানা</label>
                <input type="text" id="edit_address" name="address" class="form-control">
            </div>
            <div class="col-12">
                <label class="form-label">নোট</label>
                <input type="text" id="edit_note" name="note" class="form-control">
            </div>
          </div>
          <div class="modal-footer border-secondary">
            <button type="submit" class="btn btn-success-custom">আপডেট করুন</button>
          </div>
      </form>
    </div>
  </div>
</div>

<!-- Modal: Messenger -->
<div class="modal fade" id="messengerModal" tabindex="-1">
  <div class="modal-dialog modal-dialog-scrollable">
    <div class="modal-content bg-dark text-white">
      <div class="modal-header border-secondary">
        <h5 class="modal-title text-success"><i class="fa-solid fa-comments"></i> মেসেঞ্জার</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body" id="chatBox" style="background-color: #121212; min-height: 250px;">
        <!-- Dynamic Chat Messages -->
      </div>
      <div class="modal-footer border-secondary">
        <div class="input-group">
            <input type="text" id="chatInput" class="form-control" placeholder="মেসেজ লিখুন...">
            <button class="btn btn-success-custom" onclick="sendChatMessage()">পাঠান</button>
        </div>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
let activeServiceFilter = '';

function loadRecords() {
    let q = document.getElementById('searchInput') ? document.getElementById('searchInput').value : '';
    let sort = document.getElementById('sortSelect') ? document.getElementById('sortSelect').value : 'default';
    
    fetch(`/api/search?q=${q}&service=${activeServiceFilter}&sort=${sort}`)
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.records.forEach((row, index) => {
            html += `<tr>
                <td>${index + 1}</td>
                <td>${row[1]}</td>
                <td>${row[2] || '-'}</td>
                <td><span class="badge bg-secondary">${row[3]}</span></td>
                <td>${row[4] || '-'}</td>
                <td>${row[5] || '-'}</td>
                <td>${row[6] || '-'}</td>
                {% if session.get('user', {}).get('is_admin') %}
                <td>
                    <button class="btn btn-warning btn-sm me-1" onclick="openEditModal(${row[0]}, '${row[1]}', '${row[2]}', '${row[3]}', '${row[4]}', '${row[5]}', '${row[6]}')"><i class="fa-solid fa-pen"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="openDeleteModal(${row[0]})"><i class="fa-solid fa-trash"></i></button>
                </td>
                {% endif %}
            </tr>`;
        });
        if(document.getElementById('recordsTableBody')) document.getElementById('recordsTableBody').innerHTML = html;
        
        // Counters
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

function showSection(type) {
    if(type === 'records') {
        document.getElementById('recordsSection').style.display = 'block';
        if(document.getElementById('usersSection')) document.getElementById('usersSection').style.display = 'none';
    } else if(type === 'users') {
        document.getElementById('recordsSection').style.display = 'none';
        if(document.getElementById('usersSection')) document.getElementById('usersSection').style.display = 'block';
        loadUsers();
    }
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
                <td>${u[1]}</td><td>${u[3]}</td><td>${u[4]}</td><td>${u[2]}</td>
                <td><span class="badge ${u[6]=='active'?'bg-success':'bg-warning'}">${u[6]}</span></td>
                <td>
                    <button class="btn btn-success btn-sm me-1" onclick="userAction(${u[0]}, 'approve')">Approve</button>
                    <button class="btn btn-danger btn-sm" onclick="userAction(${u[0]}, 'block')">Block</button>
                </td>
            </tr>`;
        });
        if(document.getElementById('usersTableBody')) document.getElementById('usersTableBody').innerHTML = html;
    });
}

function userAction(id, action) {
    let code = '';
    if(action === 'block' || action === 'delete') {
        code = prompt("সিকিউরিটি পিন দিন:");
        if(!code) return;
    }
    let formData = new FormData();
    formData.append('security_code', code);
    fetch(`/admin/user_action/${id}/${action}`, { method: 'POST', body: formData })
    .then(() => loadUsers());
}

function openDeleteModal(id) {
    document.getElementById('deleteForm').action = '/delete_record/' + id;
    new bootstrap.Modal(document.getElementById('deleteModal')).show();
}

function openEditModal(id, name, mobile, service, conn, addr, note) {
    document.getElementById('editForm').action = '/edit_record/' + id;
    document.getElementById('edit_name').value = name;
    document.getElementById('edit_mobile').value = mobile;
    document.getElementById('edit_service').value = service;
    document.getElementById('edit_conn').value = conn;
    document.getElementById('edit_address').value = addr;
    document.getElementById('edit_note').value = note;
    new bootstrap.Modal(document.getElementById('editModal')).show();
}

function showMessenger() {
    new bootstrap.Modal(document.getElementById('messengerModal')).show();
    loadChat();
}

function loadChat() {
    fetch('/api/messages')
    .then(res => res.json())
    .then(msgs => {
        let html = '';
        msgs.forEach(m => {
            html += `<div class="mb-2 p-2 rounded ${m.sender==='Khushbu23'?'bg-secondary text-end':'bg-dark border border-success'}">
                <small class="text-success fw-bold">${m.sender_display}</small><br>${m.message}
            </div>`;
        });
        document.getElementById('chatBox').innerHTML = html;
    });
}

function sendChatMessage() {
    let input = document.getElementById('chatInput');
    if(!input.value) return;
    let formData = new FormData();
    formData.append('message', input.value);
    fetch('/send_message', { method: 'POST', body: formData })
    .then(() => { input.value = ''; loadChat(); });
}

// Notification Check Loop
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
    fetch('/api/read_notif/' + id).then(() => { checkNotifications(); showMessenger(); });
}

if(document.getElementById('searchInput')) {
    loadRecords();
    setInterval(checkNotifications, 4000);
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
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ? OR phone = ?", (username, username, username))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[5], password):
        if user[6] == 'pending':
            return "<script>alert('আপনার একাউন্টটি এখনও এডমিন অনুমোদন করেনি!'); window.location='/';</script>"
        elif user[6] == 'blocked':
            return "<script>alert('আপনার একাউন্টটি ব্লক করা হয়েছে!'); window.location='/';</script>"
        
        session['user'] = {
            'id': user[0],
            'name': user[1],
            'username': user[2],
            'is_admin': (user[2] == ADMIN_USERNAME)
        }
        return redirect(url_for('home'))
    return "<script>alert('ভুল ইউজারনেম অথবা পাসওয়ার্ড!'); window.location='/';</script>"

@app.route('/register', methods=['POST'])
def register():
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    if password != confirm_password:
        return "<script>alert('পাসওয়ার্ড দুটি মেলেনি!'); window.location='/';</script>"

    hashed_pw = generate_password_hash(password)
    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, username, email, phone, password) VALUES (?, ?, ?, ?, ?)",
                       (name, username, email, phone, hashed_pw))
        
        # Admin Notification
        cursor.execute("INSERT INTO notifications (type, message) VALUES ('user_reg', ?)",
                       (f"নতুন রেজিস্ট্রেশন: {name} ({username}) পারমিশন চান।",))
        conn.commit()
        conn.close()
        return "<script>alert('রেজিস্ট্রেশন সফল হয়েছে! এডমিন পারমিশন দিলে প্রবেশ করতে পারবেন।'); window.location='/';</script>"
    except:
        return "<script>alert('ইউজারনেম বা তথ্য আগে থেকেই ব্যবহৃত হচ্ছে!'); window.location='/';</script>"

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

@app.route('/edit_record/<int:id>', methods=['POST'])
def edit_record(id):
    if 'user' not in session: return redirect(url_for('home'))
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE phone_records SET customer_name=?, mobile=?, service_type=?, connection_num=?, address=?, note=?
                      WHERE id=?''', 
                   (request.form['customer_name'], request.form.get('mobile', ''), request.form['service_type'],
                    request.form.get('connection_num', ''), request.form.get('address', ''), request.form.get('note', ''), id))
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

# --- API Endpoints ---
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

    query = f"SELECT * FROM phone_records WHERE is_deleted=0 AND (customer_name LIKE ? OR mobile LIKE ? OR connection_num LIKE ? OR address LIKE ? OR note LIKE ?)"
    params = [f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%', f'%{q}%']

    if service:
        query += " AND service_type LIKE ?"
        params.append(f'%{service}%')

    query += f" ORDER BY {order_by}"
    cursor.execute(query, params)
    records = cursor.fetchall()

    # Counter Statistics
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type LIKE '%টেলিফোন%' AND service_type NOT LIKE '%ওয়াইফাই%'")
    tel = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type LIKE '%টেলিফোন+ওয়াইফাই%'")
    both = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM phone_records WHERE is_deleted=0 AND service_type LIKE '%ওয়াইফাই%' AND service_type NOT LIKE '%টেলিফোন+%'")
    wifi = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users")
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
    cursor.execute("SELECT id, name, username, email, phone, password, status FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify(users)

@app.route('/admin/user_action/<int:user_id>/<string:action>', methods=['POST'])
def user_action(user_id, action):
    if not session.get('user', {}).get('is_admin'): return jsonify({'status': 'denied'})
    sec_code = request.form.get('security_code')
    if action in ['block', 'delete'] and sec_code != ADMIN_SECURITY_CODE:
        return jsonify({'status': 'wrong_pin'})

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    if action == 'approve': cursor.execute("UPDATE users SET status='active' WHERE id=?", (user_id,))
    elif action == 'block': cursor.execute("UPDATE users SET status='blocked' WHERE id=?", (user_id,))
    elif action == 'delete': cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session: return jsonify({'error': 'Unauthorized'})
    msg = request.form['message']
    sender = session['user']['username']

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender_username, receiver_username, message) VALUES (?, ?, ?)",
                   (sender, 'ALL' if sender == ADMIN_USERNAME else ADMIN_USERNAME, msg))
    
    if sender != ADMIN_USERNAME:
        cursor.execute("INSERT INTO notifications (type, message) VALUES ('message', ?)",
                       (f"নতুন মেসেজ: {session['user']['name']} এর কাছ থেকে।",))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success'})

@app.route('/api/messages')
def api_messages():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT sender_username, message FROM messages ORDER BY id ASC")
    raw_msgs = cursor.fetchall()
    conn.close()

    msgs = []
    for m in raw_msgs:
        sender_display = "ADMIN" if m[0] == ADMIN_USERNAME else m[0]
        msgs.append({'sender': m[0], 'sender_display': sender_display, 'message': m[1]})
    return jsonify(msgs)

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