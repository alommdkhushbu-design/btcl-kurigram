import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_NAME = "btcl_system.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users Table (আপনার ফাইলের আগের টেবিল অনুযায়ী)
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
    
    # Customers Table (বিল ও ডকুমেন্ট ডাটা রাখার জন্য)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bill_no TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            address TEXT NOT NULL,
            amount TEXT NOT NULL
        )
    ''')
    
    # ডিফল্ট অ্যাডমিন একাউন্ট
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (name, email, phone, username, password, is_admin, is_approved)
            VALUES ('Admin Md.Khushbu Alom', 'admin@btcl.com', '01700000000', 'admin', 'admin123', 1, 1)
        ''')
    
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# HTML, CSS & JavaScript (আপনার পছন্দ অনুযায়ী লেআউট)
# ---------------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL System Dashboard</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: Arial, sans-serif; }
        body { display: flex; height: 100vh; background: #f4f6f9; }
        
        .sidebar { width: 260px; background: #2c3e50; color: white; padding: 20px 0; }
        .sidebar h2 { text-align: center; padding-bottom: 20px; border-bottom: 1px solid #34495e; }
        .sidebar ul { list-style: none; margin-top: 20px; }
        .sidebar ul li { padding: 15px 20px; cursor: pointer; border-bottom: 1px solid #34495e; font-size: 15px; }
        .sidebar ul li:hover, .sidebar ul li.active { background: #1abc9c; }
        
        .main-content { flex: 1; padding: 20px; overflow-y: auto; }
        .header { background: #fff; padding: 15px; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; justify-content: space-between; align-items: center; }
        .admin-banner { font-size: 20px; font-weight: bold; color: #2c3e50; }
        
        .card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        table, th, td { border: 1px solid #ddd; }
        th, td { padding: 10px; text-align: left; }
        th { background: #f2f2f2; }
        
        .btn { padding: 6px 12px; border: none; border-radius: 4px; cursor: pointer; color: white; margin-right: 5px; font-weight: bold; }
        .btn-accept { background: #2ecc71; }
        .btn-block { background: #e67e22; }
        .btn-delete { background: #e74c3c; }
        .btn-unblock { background: #3498db; }
        .badge { padding: 4px 8px; border-radius: 4px; color: white; font-size: 12px; }
        .bg-active { background: #2ecc71; }
        .bg-blocked { background: #e74c3c; }
        .bg-pending { background: #f1c40f; color: #333; }

        .input-field { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 4px; }
        .hidden { display: none; }
    </style>
</head>
<body>

    <!-- বাম পাশের থ্রি-ডট মেনু বার -->
    <div class="sidebar">
        <h2>মেনু বার (≡)</h2>
        <ul>
            <li id="menu-1" onclick="showTab('notif-tab', 1)" class="active">১. নোটিফিকেশন রিকোয়েস্ট & মেসেঞ্জার</li>
            <li id="menu-2" onclick="showTab('users-tab', 2)">২. মোট ইউজার</li>
            <li id="menu-3" onclick="showTab('bills-tab', 3)">৩. বিল ও ডকুমেন্ট সার্চ (ইউজার ভিউ)</li>
            <li id="menu-4" onclick="showTab('add-doc-tab', 4)">৪. বিল ও ডকুমেন্ট অ্যাড করুন (অ্যাডমিন)</li>
        </ul>
    </div>

    <div class="main-content">
        <!-- অ্যাডমিন ব্যানার -->
        <div class="header">
            <div class="admin-banner">Admin Md.Khushbu Alom</div>
            <div style="color: green; font-weight: bold;">● অনলাইন</div>
        </div>

        <!-- ১. নোটিফিকেশন রিকোয়েস্ট -->
        <div id="notif-tab" class="card">
            <h3>১. নোটিফিকেশন সেন্টার</h3>
            <br>
            <div style="margin-bottom: 15px;">
                <button class="btn btn-accept" onclick="alert('রেজিস্ট্রেশন রিকোয়েস্ট দেখাচ্ছে')">রেজিস্ট্রেশন রিকোয়েস্ট</button>
                <button class="btn btn-unblock" onclick="alert('মেসেঞ্জার নোটিফিকেশন')">মেসেঞ্জার নোটিফিকেশন</button>
            </div>

            <h4>নতুন রেজিস্ট্রেশন রিকোয়েস্ট:</h4>
            <table>
                <thead>
                    <tr>
                        <th>নাম</th>
                        <th>ইউজারনেম</th>
                        <th>পাসওয়ার্ড</th>
                        <th>ফোন & ইমেইল</th>
                        <th>অ্যাকশন</th>
                    </tr>
                </thead>
                <tbody id="pending-users-list"></tbody>
            </table>
        </div>

        <!-- ২. মোট ইউজার (মেনু বারের দ্বিতীয় অপশন) -->
        <div id="users-tab" class="card hidden">
            <h3>২. মোট ইউজার তালিকা (এক্সেপ্ট করা ইউজার)</h3>
            <p style="margin-top: 5px;">মোট এক্টিভ/ব্লকড ইউজার সংখ্যা: <b id="total-user-count">0</b> জন</p>
            <table>
                <thead>
                    <tr>
                        <th>ক্রমিক নং</th>
                        <th>নাম</th>
                        <th>ইউজারনেম</th>
                        <th>পাসওয়ার্ড</th>
                        <th>অবস্থা (Status)</th>
                        <th>অ্যাকশন</th>
                    </tr>
                </thead>
                <tbody id="accepted-users-list"></tbody>
            </table>
        </div>

        <!-- ৩. বিল সার্চ ও লিস্ট (ইউজারদের দেখার জন্য) -->
        <div id="bills-tab" class="card hidden">
            <h3>৩. কাস্টমার বিল ও ডকুমেন্ট তালিকা (সার্চ করুন)</h3>
            <br>
            <input type="text" id="searchInput" class="input-field" onkeyup="searchBills()" placeholder="বিল নম্বর, নাম বা ঠিকানা দিয়ে সার্চ করুন...">
            
            <table>
                <thead>
                    <tr>
                        <th>সিরিয়াল</th>
                        <th>বিল নম্বর</th>
                        <th>কাস্টমার নাম</th>
                        <th>ঠিকানা</th>
                        <th>টাকার পরিমাণ</th>
                    </tr>
                </thead>
                <tbody id="billsTable"></tbody>
            </table>
        </div>

        <!-- ৪. নতুন বিল/ডকুমেন্ট এন্ট্রি -->
        <div id="add-doc-tab" class="card hidden">
            <h3>৪. নতুন বিল বা ডকুমেন্ট অ্যাড করুন</h3>
            <br>
            <form onsubmit="submitBill(event)">
                <label><b>বিল নম্বর:</b></label>
                <input type="text" id="bill_no" class="input-field" required placeholder="যেমন: BILL-1001">
                
                <label><b>কাস্টমারের নাম:</b></label>
                <input type="text" id="customer_name" class="input-field" required placeholder="কাস্টমারের পূর্ণ নাম">
                
                <label><b>ঠিকানা:</b></label>
                <input type="text" id="address" class="input-field" required placeholder="ঠিকানা">
                
                <label><b>টাকার পরিমাণ:</b></label>
                <input type="text" id="amount" class="input-field" required placeholder="যেমন: ১৫০০ টাকা">
                
                <button type="submit" class="btn btn-accept" style="padding: 10px 20px;">ডাটা সেভ করুন</button>
            </form>
        </div>
    </div>

    <script>
        async function fetchUsers() {
            const res = await fetch('/api/users');
            const users = await res.json();
            
            const pendingBody = document.getElementById('pending-users-list');
            const acceptedBody = document.getElementById('accepted-users-list');
            
            pendingBody.innerHTML = '';
            acceptedBody.innerHTML = '';
            let count = 0;

            users.forEach((u) => {
                if (u.is_approved === 0) {
                    pendingBody.innerHTML += `
                        <tr>
                            <td>${u.name}</td>
                            <td><b>${u.username}</b></td>
                            <td><code>${u.password}</code></td>
                            <td>${u.phone}<br>${u.email}</td>
                            <td>
                                <button class="btn btn-accept" onclick="updateStatus(${u.id}, 1, '${u.username}', '${u.password}')">Accept (এক্সেপ্ট)</button>
                            </td>
                        </tr>
                    `;
                } else {
                    count++;
                    acceptedBody.innerHTML += `
                        <tr>
                            <td>${count}</td>
                            <td>${u.name}</td>
                            <td>${u.username}</td>
                            <td><code>${u.password}</code></td>
                            <td>
                                <span class="badge ${u.is_approved === 1 ? 'bg-active' : 'bg-blocked'}">
                                    ${u.is_approved === 1 ? 'এক্টিভ' : 'ব্লকড'}
                                </span>
                            </td>
                            <td>
                                ${u.is_approved === 1 
                                    ? `<button class="btn btn-block" onclick="updateStatus(${u.id}, -1)">Block (ব্লক)</button>` 
                                    : `<button class="btn btn-unblock" onclick="updateStatus(${u.id}, 1)">Unblock</button>`
                                }
                                <button class="btn btn-delete" onclick="deleteUser(${u.id})">Delete (ডিলিট)</button>
                            </td>
                        </tr>
                    `;
                }
            });
            document.getElementById('total-user-count').innerText = count;
        }

        async function fetchCustomers() {
            const res = await fetch('/api/customers');
            const data = await res.json();
            const billsTable = document.getElementById('billsTable');
            billsTable.innerHTML = '';

            data.forEach((b, i) => {
                billsTable.innerHTML += `
                    <tr>
                        <td>${i + 1}</td>
                        <td>${b.bill_no}</td>
                        <td>${b.customer_name}</td>
                        <td>${b.address}</td>
                        <td>${b.amount}</td>
                    </tr>
                `;
            });
        }

        async function submitBill(e) {
            e.preventDefault();
            const payload = {
                bill_no: document.getElementById('bill_no').value,
                customer_name: document.getElementById('customer_name').value,
                address: document.getElementById('address').value,
                amount: document.getElementById('amount').value
            };

            const res = await fetch('/api/customer/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const result = await res.json();
            alert(result.message);
            if(result.success) {
                document.getElementById('bill_no').value = '';
                document.getElementById('customer_name').value = '';
                document.getElementById('address').value = '';
                document.getElementById('amount').value = '';
                fetchCustomers();
            }
        }

        async function updateStatus(id, status, username = '', password = '') {
            if (status === 1 && username) {
                alert(`ইউজার এক্সেপ্ট করা হয়েছে!\n\nইউজারনেম: ${username}\nপাসওয়ার্ড: ${password}`);
            }
            await fetch('/api/user/status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, status })
            });
            fetchUsers();
        }

        async function deleteUser(id) {
            if (confirm("আপনি কি নিশ্চিত এই ইউজার ডিলিট করবেন? ডিলিট করলে সে আর ঢুকতে পারবে না।")) {
                await fetch(`/api/user/delete/${id}`, { method: 'DELETE' });
                fetchUsers();
            }
        }

        function showTab(tabId, menuNo) {
            document.querySelectorAll('.main-content > div:not(.header)').forEach(d => d.classList.add('hidden'));
            document.getElementById(tabId).classList.remove('hidden');
            
            document.querySelectorAll('.sidebar ul li').forEach(l => l.classList.remove('active'));
            document.getElementById('menu-' + menuNo).classList.add('active');
        }

        function searchBills() {
            let filter = document.getElementById('searchInput').value.toLowerCase();
            let rows = document.querySelectorAll('#billsTable tr');
            rows.forEach(row => {
                row.style.display = row.innerText.toLowerCase().includes(filter) ? '' : 'none';
            });
        }

        fetchUsers();
        fetchCustomers();
    </script>
</body>
</html>
"""

# ---------------------------------------------------------
# Flask Backend Routes
# ---------------------------------------------------------

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/users', methods=['GET'])
def get_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, username, password, is_approved FROM users WHERE is_admin = 0")
    rows = cursor.fetchall()
    conn.close()
    
    users_list = []
    for r in rows:
        users_list.append({
            "id": r[0], "name": r[1], "email": r[2], "phone": r[3], 
            "username": r[4], "password": r[5], "is_approved": r[6]
        })
    return jsonify(users_list)

@app.route('/api/user/status', methods=['POST'])
def update_user_status():
    data = request.json
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_approved = ? WHERE id = ?", (data['status'], data['id']))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/user/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/customer/add', methods=['POST'])
def add_customer():
    data = request.json
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO customers (bill_no, customer_name, address, amount)
            VALUES (?, ?, ?, ?)
        ''', (data['bill_no'], data['customer_name'], data['address'], data['amount']))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "বিল ও কাস্টমার ডাটা সফলভাবে যুক্ত হয়েছে!"})
    except Exception as e:
        return jsonify({"success": False, "message": "বিল নম্বর পূর্বে যুক্ত করা হয়েছে।"}), 400

@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, bill_no, customer_name, address, amount FROM customers")
    rows = cursor.fetchall()
    conn.close()
    
    customer_list = []
    for r in rows:
        customer_list.append({
            "id": r[0], "bill_no": r[1], "customer_name": r[2], "address": r[3], "amount": r[4]
        })
    return jsonify(customer_list)

if __name__ == '__main__':
    app.run(debug=True)