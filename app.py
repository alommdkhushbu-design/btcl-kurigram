<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL, কুড়িগ্রাম</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #121212; color: #fff; font-family: sans-serif; }
        .bg-dark-custom { background-color: #1e1e1e; }
        .card { background-color: #242424; color: white; border: 1px solid #333; }
        .form-control, .form-select { background-color: #333; color: #fff; border: 1px solid #444; }
        .form-control:focus { background-color: #333; color: #fff; }
        .btn-success-custom { background-color: #00e676; border: none; color: #000; font-weight: bold; }
    </style>
</head>
<body>

<div class="container py-3">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h4 class="text-success">BTCL, কুড়িগ্রাম</h4>
        {% if session.get('user') %}
            <div>
                <span class="me-2">স্বাগতম, {{ session['user']['name'] }}</span>
                <a href="/logout" class="btn btn-danger btn-sm">লগআউট</a>
            </div>
        {% endif %}
    </div>

    {% if not session.get('user') %}
    <div class="row justify-content-center">
        <div class="col-md-6">
            <div class="card p-4">
                <ul class="nav nav-tabs mb-3" id="authTab">
                    <li class="nav-item">
                        <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#loginTab">লগইন</button>
                    </li>
                    <li class="nav-item">
                        <button class="nav-link" data-bs-toggle="tab" data-bs-target="#regTab">রেজিস্ট্রেশন</button>
                    </li>
                </ul>
                <div class="tab-content">
                    <div class="tab-pane fade show active" id="loginTab">
                        <form action="/login" method="POST">
                            <input type="text" name="username" class="form-control mb-2" placeholder="ইউজারনেম / জিমেইল / ফোন" required>
                            <input type="password" name="password" class="form-control mb-3" placeholder="পাসওয়ার্ড" required>
                            <button type="submit" class="btn btn-success-custom w-100">লগইন করুন</button>
                        </form>
                    </div>
                    <div class="tab-pane fade" id="regTab">
                        <form action="/register" method="POST">
                            <input type="text" name="name" class="form-control mb-2" placeholder="আপনার নাম" required>
                            <input type="email" name="email" class="form-control mb-2" placeholder="সঠিক জিমেইল আইডি" required>
                            <input type="text" name="phone" class="form-control mb-2" placeholder="১১ ডিজিট মোবাইল নম্বর" required>
                            <input type="text" name="username" class="form-control mb-2" placeholder="ইউজারনেম" required>
                            <input type="password" name="password" class="form-control mb-2" placeholder="পাসওয়ার্ড" required>
                            <input type="password" name="confirm_password" class="form-control mb-3" placeholder="কনফার্ম পাসওয়ার্ড" required>
                            <button type="submit" class="btn btn-success-custom w-100">রেজিস্ট্রেশন করুন</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    {% else %}
    <div class="mb-3">
        <input type="text" id="searchInput" class="form-control" placeholder="যেকোনো কিছু দিয়ে সার্চ করুন (নাম, নম্বর, ঠিকানা...)" onkeyup="performSearch()">
    </div>

    <div class="card p-3 mb-4">
        <h5>গ্রাহক ও সংযোগ তালিকা</h5>
        <div class="table-responsive">
            <table class="table table-dark table-striped mt-2">
                <thead>
                    <tr>
                        <th>নাম</th>
                        <th>মোবাইল</th>
                        <th>সেবার ধরন</th>
                        <th>সংযোগ নম্বর</th>
                        <th>ঠিকানা</th>
                        <th>নোট</th>
                        <th>অ্যাকশন</th>
                    </tr>
                </thead>
                <tbody id="searchResults">
                    </tbody>
            </table>
        </div>
    </div>

    <div class="card p-3 mb-4">
        <h5>নতুন নম্বর এড করুন</h5>
        <form action="/add_record" method="POST" class="row g-2">
            <div class="col-md-4"><input type="text" name="customer_name" class="form-control" placeholder="গ্রাহকের নাম" required></div>
            <div class="col-md-4"><input type="text" name="mobile" class="form-control" placeholder="মোবাইল নম্বর" required></div>
            <div class="col-md-4">
                <select name="service_type" class="form-select">
                    <option value="টেলিফোন">টেলিফোন</option>
                    <option value="ওয়াইফাই">ওয়াইফাই</option>
                    <option value="টেলিফোন+ওয়াইফাই">টেলিফোন+ওয়াইফাই</option>
                </select>
            </div>
            <div class="col-md-4"><input type="text" name="connection_num" class="form-control" placeholder="সংযোগ নম্বর"></div>
            <div class="col-md-4"><input type="text" name="address" class="form-control" placeholder="ঠিকানা"></div>
            <div class="col-md-4"><input type="text" name="note" class="form-control" placeholder="অতিরিক্ত নোট"></div>
            <div class="col-12 mt-2">
                <button type="submit" class="btn btn-success-custom w-100">সংরক্ষণ করুন</button>
            </div>
        </form>
    </div>

    <div class="card p-3">
        <h5>মেসেঞ্জার</h5>
        <div id="chatBox" class="border p-2 mb-2" style="height: 150px; overflow-y: scroll; background-color: #1a1a1a;">
            </div>
        <div class="input-group">
            <input type="text" id="msgInput" class="form-control" placeholder="মেসেজ টাইপ করুন...">
            <button class="btn btn-success" onclick="sendMessage()">পাঠান</button>
        </div>
    </div>

    {% endif %}
</div>

<div class="modal fade" id="deleteModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content bg-dark text-white">
      <form id="deleteForm" method="POST">
          <div class="modal-header">
            <h5 class="modal-title">ডিলেটের নিশ্চিতকরণ</h5>
          </div>
          <div class="modal-body">
            <p>ডিলেট করার জন্য এডমিন সিকিউরিটি কোড প্রদান করুন:</p>
            <input type="password" name="security_code" class="form-control" required placeholder="সিকিউরিটি কোড">
          </div>
          <div class="modal-footer">
            <button type="submit" class="btn btn-danger">ডিলেট নিশ্চিত করুন</button>
          </div>
      </form>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
function performSearch() {
    let q = document.getElementById('searchInput').value;
    fetch('/api/search?q=' + q)
    .then(res => res.json())
    .then(data => {
        let html = '';
        data.forEach(row => {
            html += `<tr>
                <td>${row[1]}</td>
                <td>${row[2]}</td>
                <td>${row[3]}</td>
                <td>${row[4]}</td>
                <td>${row[5]}</td>
                <td>${row[6]}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="promptDelete(${row[0]})">ডিলেট</button>
                </td>
            </tr>`;
        });
        document.getElementById('searchResults').innerHTML = html;
    });
}

function promptDelete(id) {
    document.getElementById('deleteForm').action = '/delete_record/' + id;
    var myModal = new bootstrap.Modal(document.getElementById('deleteModal'));
    myModal.show();
}

function sendMessage() {
    let msg = document.getElementById('msgInput').value;
    let formData = new FormData();
    formData.append('message', msg);
    fetch('/send_message', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
        document.getElementById('msgInput').value = '';
    });
}

// Initial Search Load
if (document.getElementById('searchInput')) {
    performSearch();
}
</script>
</body>
</html>