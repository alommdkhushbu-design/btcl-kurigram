import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB_NAME = "btcl_system.db"

# Database Initialization
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table
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
    
    # Customer Data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            service_type TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            address TEXT NOT NULL,
            details TEXT,
            is_deleted INTEGER DEFAULT 0
        )
    ''')
    
    # Default Admin Setup
    cursor.execute("SELECT * FROM users WHERE username = 'Khushbu23'")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash("01751947523")
        cursor.execute('''
            INSERT INTO users (name, email, phone, username, password, is_admin, is_approved)
            VALUES (?, ?, ?, ?, ?, 1, 1)
        ''', ("Md. Khushbu Alom", "admin@btcl.gov.bd", "01751947523", "Khushbu23", hashed_pw))
        
    conn.commit()
    conn.close()

init_db()

SECURITY_PIN = "137955"

# Frontend HTML Template (Fixed Modal Issue)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL Kurigram Dashboard</title>
    <style>
        :root { --primary: #00e676; --bg: #121212; --card: #1e1e1e; --text: #ffffff; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 15px; }
        .container { max-width: 800px; margin: 0 auto; }
        .header { text-align: center; border-bottom: 2px solid var(--primary); padding-bottom: 15px; margin-bottom: 20px; }
        .header h1 { color: var(--primary); font-size: 20px; margin: 0 0 8px 0; }
        .header h2 { color: #bbb; font-size: 15px; margin: 0; font-weight: normal; }
        .card { background: var(--card); padding: 20px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); margin-bottom: 20px; }
        input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 6px; border: 1px solid #333; background: #2a2a2a; color: #fff; box-sizing: border-box; }
        button { width: 100%; padding: 12px; border: none; border-radius: 6px; background: var(--primary); color: #000; font-weight: bold; cursor: pointer; margin-top: 10px; }
        button:hover { opacity: 0.9; }
        .btn-danger { background: #ff5252; color: #fff; }
        .btn-warning { background: #ffb74d; color: #000; }
        .search-box { position: relative; }
        .clear-btn { position: absolute; right: 12px; top: 18px; cursor: pointer; color: #888; font-weight: bold; display: none; }
        .result-item { background: #2a2a2a; padding: 12px; border-radius: 6px; margin-top: 8px; cursor: pointer; border-left: 4px solid var(--primary); }
        .result-item:hover { background: #333; }
        .hidden { display: none !important; }
        .badge { background: #333; padding: 3px 8px; border-radius: 4px; font-size: 12px; color: var(--primary); }
        .flex { display: flex; gap: 10px; }
        .modal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); display: flex; justify-content: center; align-items: center; z-index: 999; }
        .modal-content { background: var(--card); padding: 25px; border-radius: 10px; max-width: 500px; width: 90%; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>বাংলাদেশ টেলিকমিউনিকেশন্স কোম্পানী লিমিটেড (বিটিসিএল), কুড়িগ্রাম</h1>
            <h2>Welcome to admin Md.Khushbu Alom</h2>
        </div>

        <!-- Auth Section -->
        <div id="auth-section" class="card">
            <div class="flex" style="margin-bottom: 15px;">
                <button onclick="toggleAuth('login')" id="tab-login" style="background: var(--primary)">লগইন</button>
                <button onclick="toggleAuth('register')" id="tab-reg" style="background: #333; color: #fff">রেজিস্ট্রেশন</button>
            </div>

            <form id="login-form">
                <input type="text" id="login-user" placeholder="ইউজার নেম" value="Khushbu23" required>
                <input type="password" id="login-pass" placeholder="পাসওয়ার্ড" value="01751947523" required>
                <button type="submit">লগইন করুন</button>
            </form>

            <form id="reg-form" class="hidden">
                <input type="text" id="reg-name" placeholder="আপনার নাম" required>
                <input type="email" id="reg-email" placeholder="জিমেইল আইডি" required>
                <input type="text" id="reg-phone" placeholder="মোবাইল নম্বর" required>
                <input type="text" id="reg-username" placeholder="নতুন ইউজার নেম" required>
                <input type="password" id="reg-pass" placeholder="পাসওয়ার্ড" required>
                <button type="submit">একউন্ট তৈরি করুন</button>
            </form>
        </div>

        <!-- Dashboard Section -->
        <div id="dashboard" class="hidden">
            <div style="text-align: right; margin-bottom: 10px;">
                <span id="user-display" class="badge"></span>
                <button onclick="logout()" style="width: auto; padding: 5px 15px; margin: 0; background: #555; color: #fff;">লগআউট</button>
            </div>

            <!-- Search Section -->
            <div class="card">
                <h3>লাইভ সার্চ (নাম বা ফোন নম্বর)</h3>
                <div class="search-box">
                    <input type="text" id="search-input" placeholder="খুঁজতে এখানে নাম বা ফোন নম্বর লিখুন..." oninput="handleSearch()">
                    <span id="clear-search" class="clear-btn" onclick="clearSearch()">✕</span>
                </div>
                <div id="search-results"></div>
            </div>

            <!-- Admin Add Entry Section -->
            <div id="admin-add-section" class="card hidden">
                <h3>নতুন তথ্য যুক্ত করুন (শুধুমাত্র এডমিন)</h3>
                <form id="add-data-form">
                    <input type="text" id="cust-name" placeholder="গ্রাহকের নাম" required>
                    <select id="cust-service" required>
                        <option value="">সেবা নির্বাচন করুন</option>
                        <option value="টেলিফোন">টেলিফোন</option>
                        <option value="টেলিফোন+ওয়াইফাই">টেলিফোন+ওয়াইফাই</option>
                        <option value="ওয়াইফাই">ওয়াইফাই</option>
                    </select>
                    <input type="text" id="cust-phone" placeholder="ফোন নম্বর" required>
                    <textarea id="cust-address" placeholder="ঠিকানা" required></textarea>
                    <textarea id="cust-details" placeholder="অতিরিক্ত তথ্য"></textarea>
                    <button type="submit">ডাটা সংরক্ষণ করুন</button>
                </form>
            </div>

            <!-- Admin Management Section -->
            <div id="admin-manage-section" class="card hidden">
                <h3>ইউজার রিকুয়েস্ট ও পারমিশন</h3>
                <div id="user-requests-list"></div>
                
                <h3 style="margin-top: 25px;">রিসাইকেল বিন (ডিলিট করা ফাইল)</h3>
                <div id="recycle-bin-list"></div>
            </div>
        </div>
    </div>

    <!-- Modal for Details View (Hidden by default) -->
    <div id="details-modal" class="modal hidden">
        <div class="modal-content">
            <h3 id="modal-title" style="color: var(--primary);"></h3>
            <div id="modal-body"></div>
            <div id="admin-actions" class="hidden" style="margin-top: 15px;">
                <button class="btn-danger" onclick="deleteEntry()">ডিলিট করুন (পিন লাগবে)</button>
            </div>
            <button onclick="closeModal()" style="background: #444; color: #fff; margin-top: 10px;">বন্ধ করুন</button>
        </div>
    </div>

    <script>
        let currentUser = null;
        let selectedEntryId = null;

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
                    username: document.getElementById('login-user').value,
                    password: document.getElementById('login-pass').value
                })
            });
            const data = await res.json();
            if(data.success) {
                currentUser = data.user;
                loadDashboard();
            } else {
                alert(data.message);
            }
        };

        document.getElementById('reg-form').onsubmit = async (e) => {
            e.preventDefault();
            const res = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: document.getElementById('reg-name').value,
                    email: document.getElementById('reg-email').value,
                    phone: document.getElementById('reg-phone').value,
                    username: document.getElementById('reg-username').value,
                    password: document.getElementById('reg-pass').value
                })
            });
            const data = await res.json();
            alert(data.message);
            if(data.success) toggleAuth('login');
        };

        function loadDashboard() {
            document.getElementById('auth-section').classList.add('hidden');
            document.getElementById('dashboard').classList.remove('hidden');
            document.getElementById('user-display').innerText = currentUser.name + (currentUser.is_admin ? " (Admin)" : " (User)");

            if(currentUser.is_admin) {
                document.getElementById('admin-add-section').classList.remove('hidden');
                document.getElementById('admin-manage-section').classList.remove('hidden');
                loadPendingUsers();
                loadRecycleBin();
            }
        }

        function logout() {
            location.reload();
        }

        async function handleSearch() {
            const query = document.getElementById('search-input').value;
            const clearBtn = document.getElementById('clear-search');
            clearBtn.style.display = query ? 'block' : 'none';

            if(!query) {
                document.getElementById('search-results').innerHTML = '';
                return;
            }

            const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const results = await res.json();
            
            let html = '';
            results.forEach(item => {
                html += `<div class="result-item" onclick="viewDetails(${item.id})">
                    <strong>${item.name}</strong> (${item.service_type}) - ${item.phone_number}
                </div>`;
            });
            document.getElementById('search-results').innerHTML = html || '<p style="color:#888;">কোনো তথ্য পাওয়া যায়নি</p>';
        }

        function clearSearch() {
            document.getElementById('search-input').value = '';
            handleSearch();
        }

        async function viewDetails(id) {
            selectedEntryId = id;
            const res = await fetch(`/api/details/${id}`);
            const data = await res.json();

            document.getElementById('modal-title').innerText = data.name;
            document.getElementById('modal-body').innerHTML = `
                <p><strong>সেবার ধরণ:</strong> ${data.service_type}</p>
                <p><strong>মোবাইল/ফোন নম্বর:</strong> ${data.phone_number}</p>
                <p><strong>ঠিকানা:</strong> ${data.address}</p>
                <p><strong>অতিরিক্ত তথ্য:</strong> ${data.details || 'নেই'}</p>
            `;

            if(currentUser.is_admin) {
                document.getElementById('admin-actions').classList.remove('hidden');
            }
            document.getElementById('details-modal').classList.remove('hidden');
        }

        function closeModal() {
            document.getElementById('details-modal').classList.add('hidden');
        }

        document.getElementById('add-data-form').onsubmit = async (e) => {
            e.preventDefault();
            const res = await fetch('/api/add-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: document.getElementById('cust-name').value,
                    service_type: document.getElementById('cust-service').value,
                    phone_number: document.getElementById('cust-phone').value,
                    address: document.getElementById('cust-address').value,
                    details: document.getElementById('cust-details').value
                })
            });
            const data = await res.json();
            alert(data.message);
            if(data.success) {
                document.getElementById('add-data-form').reset();
            }
        };

        async function deleteEntry() {
            const pin = prompt("ডিলিট করতে সিকিউরিটি পাসওয়ার্ড (PIN) দিন:");
            if(!pin) return;

            const res = await fetch('/api/delete-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id: selectedEntryId, pin: pin })
            });
            const data = await res.json();
            alert(data.message);
            if(data.success) {
                closeModal();
                handleSearch();
                loadRecycleBin();
            }
        }

        async function loadPendingUsers() {
            const res = await fetch('/api/admin/users');
            const users = await res.json();
            let html = '';
            users.forEach(u => {
                html += `<div style="display:flex; justify-between; align-items:center; background:#2a2a2a; padding:10px; margin-top:5px; border-radius:5px;">
                    <div>${u.name} (${u.username}) - ${u.phone}</div>
                    <div>
                        <button onclick="approveUser(${u.id})" style="width:auto; padding:5px 10px; margin:0;" class="btn-warning">Approve</button>
                        <button onclick="deleteUser(${u.id})" style="width:auto; padding:5px 10px; margin:0;" class="btn-danger">Delete</button>
                    </div>
                </div>`;
            });
            document.getElementById('user-requests-list').innerHTML = html || '<p style="color:#888;">কোনো পেন্ডিং ইউজার নেই</p>';
        }

        async function approveUser(id) {
            await fetch(`/api/admin/approve-user/${id}`, {method: 'POST'});
            loadPendingUsers();
        }

        async function deleteUser(id) {
            if(confirm("ইউজারকে ডিলিট করে দিতে চান?")) {
                await fetch(`/api/admin/delete-user/${id}`, {method: 'POST'});
                loadPendingUsers();
            }
        }

        async function loadRecycleBin() {
            const res = await fetch('/api/admin/recycle-bin');
            const items = await res.json();
            let html = '';
            items.forEach(i => {
                html += `<div style="display:flex; justify-between; align-items:center; background:#2a2a2a; padding:10px; margin-top:5px; border-radius:5px;">
                    <div>${i.name} - ${i.phone_number}</div>
                    <button onclick="restoreCustomer(${i.id})" style="width:auto; padding:5px 10px; margin:0; background:var(--primary);">Restore</button>
                </div>`;
            });
            document.getElementById('recycle-bin-list').innerHTML = html || '<p style="color:#888;">রিসাইকেল বিন ফাঁকা</p>';
        }

        async function restoreCustomer(id) {
            const pin = prompt("পুনরুদ্ধার করতে সিকিউরিটি পাসওয়ার্ড (PIN) দিন:");
            if(!pin) return;

            const res = await fetch('/api/admin/restore-customer', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id: id, pin: pin })
            });
            const data = await res.json();
            alert(data.message);
            if(data.success) loadRecycleBin();
        }
    </script>
</body>
</html>
"""

# API Routes
@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/register", methods=["POST"])
def register():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        hashed_pw = generate_password_hash(data['password'])
        cursor.execute('''
            INSERT INTO users (name, email, phone, username, password)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['name'], data['email'], data['phone'], data['username'], hashed_pw))
        conn.commit()
        return jsonify({"success": True, "message": "রেজিস্ট্রেশন সফল হয়েছে! এডমিনের অনুমোদনের জন্য অপেক্ষা করুন।"})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "ইউজার নেম বা জিমেইলটি আগে থেকেই ব্যবহৃত হচ্ছে।"})
    finally:
        conn.close()

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (data['username'],))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[5], data['password']):
        if user[7] == 0:  # is_approved == 0
            return jsonify({"success": False, "message": "এডমিন এখনও আপনার আইডিটি একটিভ করেনি!"})
        return jsonify({
            "success": True,
            "user": {
                "id": user[0],
                "name": user[1],
                "username": user[4],
                "is_admin": user[6]
            }
        })
    return jsonify({"success": False, "message": "ভুল ইউজার নেম বা পাসওয়ার্ড!"})

@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get('q', '')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, service_type, phone_number FROM customers 
        WHERE is_deleted = 0 AND (name LIKE ? OR phone_number LIKE ?)
        LIMIT 20
    ''', (f'%{query}%', f'%{query}%'))
    rows = cursor.fetchall()
    conn.close()
    
    results = [{"id": r[0], "name": r[1], "service_type": r[2], "phone_number": r[3]} for r in rows]
    return jsonify(results)

@app.route("/api/details/<int:cust_id>", methods=["GET"])
def details(cust_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers WHERE id = ?", (cust_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({
            "id": row[0], "name": row[1], "service_type": row[2],
            "phone_number": row[3], "address": row[4], "details": row[5]
        })
    return jsonify({}), 404

@app.route("/api/add-customer", methods=["POST"])
def add_customer():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO customers (name, service_type, phone_number, address, details)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data['service_type'], data['phone_number'], data['address'], data['details']))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "তথ্য সফলভাবে সংরক্ষিত হয়েছে!"})

@app.route("/api/delete-customer", methods=["POST"])
def delete_customer():
    data = request.json
    if data.get('pin') != SECURITY_PIN:
        return jsonify({"success": False, "message": "ভুল সিকিউরিটি পাসওয়ার্ড!"})
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET is_deleted = 1 WHERE id = ?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "তথ্যটি সফলভাবে ডিলিট (রিসাইকেল বিন) করা হয়েছে।"})

@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, username, phone FROM users WHERE is_approved = 0")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "username": r[2], "phone": r[3]} for r in rows])

@app.route("/api/admin/approve-user/<int:user_id>", methods=["POST"])
def approve_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_approved = 1 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/admin/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route("/api/admin/recycle-bin", methods=["GET"])
def recycle_bin():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, phone_number FROM customers WHERE is_deleted = 1")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "phone_number": r[2]} for r in rows])

@app.route("/api/admin/restore-customer", methods=["POST"])
def restore_customer():
    data = request.json
    if data.get('pin') != SECURITY_PIN:
        return jsonify({"success": False, "message": "ভুল সিকিউরিটি পাসওয়ার্ড!"})
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE customers SET is_deleted = 0 WHERE id = ?", (data['id'],))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "তথ্যটি সফলভাবে পুনঃপ্রতিষ্ঠা করা হয়েছে।"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port))