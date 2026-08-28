import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_NAME = "database.db"
SECURITY_PIN = "137955"

# ---------------------------------------------------------
# ডাটাবেস ইনিশিয়ালাইজেশন
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT UNIQUE, username TEXT UNIQUE, password TEXT, status TEXT DEFAULT 'pending'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, service TEXT, phone TEXT, amount TEXT, address TEXT, note TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT, receiver TEXT, message TEXT, file_url TEXT, file_type TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # ডিফল্ট এডমিন একাউন্ট (কোনো ভেরিফিকেশন লাগবে না)
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (name, email, phone, username, password, status) VALUES (?, ?, ?, ?, ?, ?)",
                       ("Admin", "admin@btcl.gov.bd", "01700000000", "admin", "admin123", "admin"))
    
    conn.commit()
    conn.close()

init_db()

# ---------------------------------------------------------
# UI (HTML, CSS, JS)
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

        /* হেডার */
        .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
        .header-left { display: flex; align-items: center; gap: 8px; }
        .menu-btn, .group-btn, .direct-btn { font-size: 14px; color: #00ff66; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; padding: 6px 10px; cursor: pointer; font-weight: bold; }
        .header-title { color: #00ff66; font-size: 15px; font-weight: bold; background: #1e1e1e; padding: 6px 12px; border-radius: 6px; border: 1px solid #2a2a2a; }
        
        /* সার্চ বক্স */
        .search-container { position: relative; margin-bottom: 15px; }
        .search-box { width: 100%; padding: 12px 15px 12px 35px; background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 20px; color: #fff; font-size: 14px; }
        .search-icon { position: absolute; left: 12px; top: 12px; color: #888; }

        /* সাইডবার */
        .sidebar { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: #1e1e1e; z-index: 1000; transition: 0.3s; padding: 15px; border-right: 1px solid #333; box-shadow: 5px 0 15px rgba(0,0,0,0.5); }
        .sidebar.active { left: 0; }
        .close-btn { color: #ff4d4d; background: none; border: none; font-size: 16px; cursor: pointer; float: right; font-weight: bold; }
        
        .menu-title { color: #888; font-size: 13px; margin: 20px 0 10px 0; }
        .menu-list { display: flex; flex-direction: column; gap: 8px; }
        .menu-item { background: #2a2a2a; color: #fff; padding: 12px; border-radius: 6px; font-size: 14px; border: none; text-align: left; width: 100%; cursor: pointer; }
        .menu-item.active { background: #00e65c; color: #000; font-weight: bold; }
        .logout-btn { background: #ff4d4d; color: #fff; width: 100%; padding: 12px; border-radius: 6px; border: none; margin-top: 20px; font-weight: bold; cursor: pointer; }

        /* কার্ড থিম */
        .card { background: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #2a2a2a; margin-bottom: 15px; }
        .card-title { font-size: 15px; font-weight: bold; text-align: center; margin-bottom: 12px; }
        
        .grid-stats { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: center; }
        .stat-box { background: #2a2a2a; padding: 10px; border-radius: 8px; }
        .stat-box.green { background: #003311; border: 1px solid #00e65c; grid-column: span 2; }
        .stat-box h2 { color: #00ff66; margin-top: 5px; font-size: 18px; }
        .stat-box p { font-size: 12px; color: #ccc; }

        /* ইনপুট ও বাটন */
        .input-box { width: 100%; padding: 12px; margin-bottom: 10px; background: #2a2a2a; border: 1px solid #333; border-radius: 6px; color: #fff; font-size: 14px; }
        .submit-btn { width: 100%; padding: 12px; background: #00e65c;