import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_NAME = "database.db"
SECURITY_PIN = "137955"

# ---------------------------------------------------------
# ডাটাবেস সেটআপ
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # ইউজার টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT UNIQUE, username TEXT UNIQUE, password TEXT, status TEXT DEFAULT 'pending'
        )
    ''')
    
    # গ্রাহক ডাটা টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, service TEXT, phone TEXT, amount TEXT, address TEXT, note TEXT
        )
    ''')
    
    # মেসেঞ্জার টেবিল
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT, receiver TEXT, message TEXT, file_url TEXT, file_type TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ডিফল্ট এডমিন একাউন্ট
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, phone, username, password, status) VALUES (?, ?, ?, ?, ?, ?)",
                       ("Admin", "admin@btcl.gov.bd", "01700000000", "admin", "admin123", "admin"))
    
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print("Database Init Error:", e)

# ---------------------------------------------------------
# UI টেমপ্লেট
# ---------------------------------------------------------
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>বিটিসিএল (BTCL), কুড়িগ্রাম</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: system-ui, -apple-system, sans-serif; }
        body { background-color: #121212; color: #ffffff; padding: 12px; }

        .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
        .header-left { display: flex; align-items: center; gap: 8px; }
        .menu-btn, .group-btn { font-size: 18px; color: #00ff66; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; padding: 6px 10px; cursor: pointer; }
        .header-title { color: #00ff66; font-size: 14px; font-weight: bold; background: #1e1e1e; padding: 6px 10px; border-radius: 6px; border: 1px solid #2a2a2a; }
        
        .search-container { position: relative; margin-bottom: 15px; }
        .search-box { width: 100%; padding: 10px 12px 10px 35px; background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 20px; color: #fff; font-size: 13px; }
        .search-icon { position: absolute; left: 12px; top: 10px; color: #888; }

        .sidebar { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: #1e1e1e; z-index: 1000; transition: 0.3s; padding: 15px; border-right: 1px solid #333; }
        .sidebar.active { left: 0; }
        .close-btn { color: #ff4d4d; background: none; border: none; font-size: 15px; cursor: pointer; float: right; font-weight: bold; }
        
        .menu-title { color: #888; font-size: 12px; margin: 20px 0 10px 0; }
        .menu-list { display: flex; flex-direction: column; gap: 8px; }
        .menu-item { background: #2a2a2a; color: #fff; padding: 10px; border-radius: 6px; font-size: 13px; border: none; text-align: left; width: 100%; cursor: pointer; }
        .menu-item.active { background: #00e65c; color: #000; font-weight: bold; }
        .logout-btn { background: #ff4d4d; color: #fff; width: 100%; padding: 10px; border-radius: 6px; border: none; margin-top: 20px; font-weight: bold; cursor: pointer; }

        .card { background: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #2a2a2a; margin-bottom: 15px; }
        .card-title { font-size: 14px; font-weight: bold; text-align: center; margin-bottom: 12px; }
        
        .grid-stats { display: grid; grid-template-columns: 1fr; gap: 10px; text-align: center; }
        .stat-box { background: #003311; border: 1px solid #00e65c; padding: 12px; border-radius: 8px; }
        .stat-box h2 { color: #00ff66; margin-top: 5px; font-size: 20px; }
        .stat-box p { font-size: 12px; color: #ccc; }

        .input-box { width: 100%; padding: 10px; margin-bottom: 10px; background: #2a2a2a; border: 1px solid #333; border-radius: 6px; color: #fff; font-size: 13px; }
        .submit-btn { width: 100%; padding: 10px; background: #00e65c; color: #000; font-weight: bold; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }
        .btn-danger { background: #ff4d4d; color: #fff; border: none; padding: 5px 8px; border-radius: 4px; cursor: pointer; }
        .btn-edit { background: #ffaa00; color: #000; border: none; padding: 5px 8px; border-radius: 4px; cursor: pointer; margin-right: 5px; }

        .table-responsive { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
        th, td { border: 1px solid #333; padding: 8px; text-align: left; }
        th { background: #2a2a2a; color: #00ff66; }

        .auth-container { max-width: 400px; margin: 20px auto; background: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #2a2a2a; }
        .tab-buttons { display: flex; gap: 10px; margin-bottom: 15px; }
        .tab-btn { flex: 1; padding: 10px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        
        .chat-box { height: 200px; overflow-y: auto; border: 1px solid #333; border-radius: 6px; padding: 10px; margin-bottom: 10px; background: #121212;