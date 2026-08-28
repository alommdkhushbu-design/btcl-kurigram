
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL Kurigram System</title>
    <style>
        * { box-sizing: border-box; font-family: Arial, sans-serif; }
        body { background: #f4f7f6; margin: 0; padding: 15px; }
        .container { max-width: 800px; margin: 0 auto; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 10px; margin-bottom: 20px; }
        .header h2 { color: #007bff; margin: 0; font-size: 20px; }
        .header h3 { color: #333; margin: 5px 0 0; font-size: 16px; }
        .card { background: #fafafa; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
        input, select, textarea, button { width: 100%; padding: 10px; margin: 6px 0; border: 1px solid #ccc; border-radius: 4px; }
        button { background: #28a745; color: white; font-weight: bold; cursor: pointer; border: none; }
        button:hover { opacity: 0.9; }
        .btn-danger { background: #dc3545; }
        .btn-warning { background: #ffc107; color: #000; }
        .btn-secondary { background: #6c757d; }
        .hidden { display: none; }
        .search-box { display: flex; gap: 5px; }
        .search-box input { flex: 1; }
        .search-box button { width: auto; }
        .data-item { background: #fff; border-left: 4px solid #007bff; padding: 10px; margin: 10px 0; border: 1px solid #eee; }
        .badge { background: #17a2b8; color: white; padding: 2px 6px; border-radius: 3px; font-size: 12px; }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h2>বাংলাদেশ টেলিকমিউনিকেশন্স কোম্পানী লিমিটেড (বিটিসিএল), কুড়িগ্রাম</h2>
        <h3>Welcome to admin Md.Khushbu Alom</h3>
    </div>

    <!-- Auth Section -->
    <div id="authSection">
        <div class="card" id="loginBox">
            <h3>লগইন করুন</h3>
            <input type="text" id="loginUser" placeholder="ইউজার নেম">
            <input type="password" id="loginPass" placeholder="পাসওয়ার্ড">
            <button onclick="login()">লগইন</button>
            <p>নতুন অ্যাকাউন্ট প্রয়োজন? <a href="#" onclick="toggleAuth(true)">রেজিস্ট্রেশন করুন</a></p>
        </div>

        <div class="card hidden" id="registerBox">
            <h3>রেজিস্ট্রেশন করুন</h3>
            <input type="text" id="regName" placeholder="নাম">
            <input type="email" id="regEmail" placeholder="জিমেইল">
            <input type="text" id="regPhone" placeholder="মোবাইল নাম্বার">
            <input type="password" id="regPass" placeholder="পাসওয়ার্ড">
            <input type="password" id="regConfirmPass" placeholder="কনফার্ম পাসওয়ার্ড">
            <button onclick="register()">রেজিস্টার</button>
            <p>আগে থেকেই অ্যাকাউন্ট আছে? <a href="#" onclick="toggleAuth(false)">লগইন করুন</a></p>
        </div>
    </div>

    <!-- Main Dashboard -->
    <div id="dashboardSection" class="hidden">
        <div style="text-align: right; margin-bottom: 10px;">
            <button class="btn-secondary" style="width: auto;" onclick="logout()">লগআউট</button>
        </div>

        <!-- Admin Only Data Entry -->
        <div id="adminEntry" class="card hidden">
            <h3>নতুন ডাটা যোগ করুন (অ্যাডমিন)</h3>
            <label>সার্ভিস টাইপ:</label>
            <select id="serviceType">
                <option value="নাম">নাম</option>
                <option value="টেলিফোন নাম্বার">টেলিফোন নাম্বার</option>
                <option value="টেলিফোন+ওয়াইফাই">টেলিফোন+ওয়াইফাই</option>
                <option value="ওয়াই ফাই">ওয়াই ফাই</option>
            </select>
            <input type="text" id="entryPhone" placeholder="মোবাইল নাম্বার">
            <input type="text" id="entryAddress" placeholder="ঠিকানা">
            <textarea id="entryInfo" placeholder="অন্যান্য তথ্য"></textarea>
            <button onclick="addEntry()">ডাটা সেভ করুন</button>
        </div>

        <!-- User Management (Admin Only) -->
        <div id="adminUserMgmt" class="card hidden">
            <h3>ইউজার পারমিশন কন্ট্রোল</h3>
            <div id="userList"></div>
        </div>

        <!-- Search Box -->
        <div class="card">
            <h3>ডাটা সার্চ করুন</h3>
            <div class="search-box">
                <input type="text" id="searchInput" onkeyup="searchData()" placeholder="নাম, মোবাইল বা তথ্য দিয়ে সার্চ করুন...">
                <button class="btn-secondary" onclick="clearSearch()">ক্যানসেল</button>
            </div>
            <div id="searchResults"></div>
        </div>

        <!-- Recycle Bin (Admin Only) -->
        <div id="adminBin" class="card hidden">
            <h3>রিসাইকেল বিন (ডিলিট করা ডাটা)</h3>
            <div id="binResults"></div>
        </div>
    </div>
</div>

<script>
    // System Credentials & Storage Initialization
    const ADMIN_USER = "Khushbu23";
    const ADMIN_PASS = "01751947523";
    const SECURITY_PIN = "137955";

    let currentUser = null;
    let dbEntries = JSON.parse(localStorage.getItem('dbEntries')) || [];
    let dbBin = JSON.parse(localStorage.getItem('dbBin')) || [];
    let dbUsers = JSON.parse(localStorage.getItem('dbUsers')) || [];

    function saveAll() {
        localStorage.setItem('dbEntries', JSON.stringify(dbEntries));
        localStorage.setItem('dbBin', JSON.stringify(dbBin));
        localStorage.setItem('dbUsers', JSON.stringify(dbUsers));
    }

    function toggleAuth(showReg) {
        document.getElementById('loginBox').classList.toggle('hidden', showReg);
        document.getElementById('registerBox').classList.toggle('hidden', !showReg);
    }

    function register() {
        const name = document.getElementById('regName').value;
        const email = document.getElementById('regEmail').value;
        const phone = document.getElementById('regPhone').value;
        const pass = document.getElementById('regPass').value;
        const cpass = document.getElementById('regConfirmPass').value;

        if(!name || !email || !phone || !pass) return alert("সব তথ্য পূরণ করুন!");
        if(pass !== cpass) return alert("পাসওয়ার্ড মেলেনি!");

        dbUsers.push({ id: Date.now(), name, email, phone, pass, active: false });
        saveAll();
        alert("রেজিস্ট্রেশন সফল! অ্যাডমিনের অনুমোদনের জন্য অপেক্ষা করুন।");
        toggleAuth(false);
    }

    function login() {
        const u = document.getElementById('loginUser').value;
        const p = document.getElementById('loginPass').value;

        if(u === ADMIN_USER && p === ADMIN_PASS) {
            currentUser = { role: 'admin', name: 'Md.Khushbu Alom' };
            loadDashboard();
            return;
        }

        const user = dbUsers.find(x => x.email === u || x.phone === u);
        if(user) {
            if(!user.active) return alert("আপনার আইডিটি এখনো একটিভ করা হয়নি। অ্যাডমিনের সাথে যোগাযোগ করুন।");
            if(user.pass !== p) return alert("ভুল পাসওয়ার্ড!");
            currentUser = { role: 'user', name: user.name };
            loadDashboard();
            return;
        }

        alert("ইউজার পাওয়া যায়নি বা তথ্য ভুল!");
    }

    function logout() {
        currentUser = null;
        document.getElementById('authSection').classList.remove('hidden');
        document.getElementById('dashboardSection').classList.add('hidden');
    }

    function loadDashboard() {
        document.getElementById('authSection').classList.add('hidden');
        document.getElementById('dashboardSection').classList.remove('hidden');

        const isAdmin = currentUser.role === 'admin';
        document.getElementById('adminEntry').classList.toggle('hidden', !isAdmin);
        document.getElementById('adminUserMgmt').classList.toggle('hidden', !isAdmin);
        document.getElementById('adminBin').classList.toggle('hidden', !isAdmin);

        if(isAdmin) {
            renderUsers();
            renderBin();
        }
        searchData();
    }

    function addEntry() {
        const type = document.getElementById('serviceType').value;
        const phone = document.getElementById('entryPhone').value;
        const address = document.getElementById('entryAddress').value;
        const info = document.getElementById('entryInfo').value;

        if(!phone) return alert("মোবাইল নাম্বার দিন!");

        dbEntries.push({ id: Date.now(), type, phone, address, info });
        saveAll();
        alert("ডাটা সফলভাবে যুক্ত হয়েছে!");
        document.getElementById('entryPhone').value = '';
        document.getElementById('entryAddress').value = '';
        document.getElementById('entryInfo').value = '';
        searchData();
    }

    function searchData() {
        const query = document.getElementById('searchInput').value.toLowerCase();
        const container = document.getElementById('searchResults');
        container.innerHTML = '';

        const results = dbEntries.filter(item => 
            item.phone.toLowerCase().includes(query) ||
            item.type.toLowerCase().includes(query) ||
            item.address.toLowerCase().includes(query) ||
            item.info.toLowerCase().includes(query)
        );

        results.forEach(item => {
            const div = document.createElement('div');
            div.className = 'data-item';
            div.innerHTML = `
                <div><span class="badge">${item.type}</span> <strong>ফোন:</strong> ${item.phone}</div>
                <div><strong>ঠিকানা:</strong> ${item.address || 'N/A'}</div>
                <div><strong>তথ্য:</strong> ${item.info || 'N/A'}</div>
                ${currentUser.role === 'admin' ? `<button class="btn-danger" style="width:auto; margin-top:5px;" onclick="moveToBin(${item.id})">ডিলিট</button>` : ''}
            `;
            container.appendChild(div);
        });
    }

    function clearSearch() {
        document.getElementById('searchInput').value = '';
        searchData();
    }

    function moveToBin(id) {
        const pin = prompt("ডিলিট করতে সিকিউরিটি পাসওয়ার্ড দিন:");
        if(pin !== SECURITY_PIN) return alert("ভুল সিকিউরিটি পাসওয়ার্ড!");

        const idx = dbEntries.findIndex(x => x.id === id);
        if(idx > -1) {
            dbBin.push(dbEntries[idx]);
            dbEntries.splice(idx, 1);
            saveAll();
            searchData();
            renderBin();
        }
    }

    function restoreItem(id) {
        const pin = prompt("ফিরে আনতে সিকিউরিটি পাসওয়ার্ড দিন:");
        if(pin !== SECURITY_PIN) return alert("ভুল সিকিউরিটি পাসওয়ার্ড!");

        const idx = dbBin.findIndex(x => x.id === id);
        if(idx > -1) {
            dbEntries.push(dbBin[idx]);
            dbBin.splice(idx, 1);
            saveAll();
            searchData();
            renderBin();
        }
    }

    function renderBin() {
        const container = document.getElementById('binResults');
        container.innerHTML = '';
        dbBin.forEach(item => {
            const div = document.createElement('div');
            div.className = 'data-item';
            div.innerHTML = `
                <div><span class="badge">${item.type}</span> <strong>ফোন:</strong> ${item.phone}</div>
                <button class="btn-warning" style="width:auto; margin-top:5px;" onclick="restoreItem(${item.id})">রিস্টোর (ফিরে আনুন)</button>
            `;
            container.appendChild(div);
        });
    }

    function renderUsers() {
        const container = document.getElementById('userList');
        container.innerHTML = '';
        dbUsers.forEach(u => {
            const div = document.createElement('div');
            div.className = 'data-item';
            div.innerHTML = `
                <div><strong>নাম:</strong> ${u.name} (${u.phone})</div>
                <div><strong>ইমেইল:</strong> ${u.email}</div>
                <div><strong>স্ট্যাটাস:</strong> ${u.active ? '<b style="color:green">Active</b>' : '<b style="color:red">Pending</b>'}</div>
                <button class="btn-warning" style="width:auto;" onclick="toggleUser(${u.id})">${u.active ? 'ডিঅ্যাক্টিভ করুন' : 'একটিভ করুন'}</button>
                <button class="btn-danger" style="width:auto;" onclick="deleteUser(${u.id})">ইউজার ডিলিট</button>
            `;
            container.appendChild(div);
        });
    }

    function toggleUser(id) {
        const u = dbUsers.find(x => x.id === id);
        if(u) {
            u.active = !u.active;
            saveAll();
            renderUsers();
        }
    }

    function deleteUser(id) {
        const pin = prompt("ইউজার ডিলিট করতে সিকিউরিটি পাসওয়ার্ড দিন:");
        if(pin !== SECURITY_PIN) return alert("ভুল সিকিউরিটি পাসওয়ার্ড!");
        dbUsers = dbUsers.filter(x => x.id !== id);
        saveAll();
        renderUsers();
    }
</script>
</body>
</html>