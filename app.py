import os
import sqlite3
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
DB_NAME = "btcl_system.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users Table
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
    
    # Customers Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            service_type TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            address TEXT NOT NULL,
            bill_amount REAL DEFAULT 0,
            details TEXT,
            is_deleted INTEGER DEFAULT 0
        )
    ''')

    # Messages Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sender_name TEXT,
            message TEXT,
            file_url TEXT,
            file_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0
        )
    ''')
    
    # Default Admin User
    cursor.execute("SELECT * FROM users WHERE username = 'Khushbu23'")
    if not cursor.fetchone():
        cursor.execute('''
            INSERT INTO users (name, email, phone, username, password, is_admin, is_approved)
            VALUES (?, ?, ?, ?, ?, 1, 1)
        ''', ("Md. Khushbu Alom", "admin@btcl.gov.bd", "01751947523", "Khushbu23", "01751947523"))
        
    conn.commit()
    conn.close()

init_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BTCL Kurigram System</title>
    <style>
        :root { --primary: #00e676; --bg: #121212; --card: #1e1e1e; --text: #ffffff; --sidebar: #181818; --chat-bg: #252525; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; }
        
        /* Sticky Top Navbar & Global Search Bar */
        .top-navbar-container { position: sticky; top: 0; z-index: 1000; background: #000; border-bottom: 2px solid var(--primary); }
        .top-navbar { display: flex; align-items: center; justify-content: space-between; padding: 8px 15px; }
        .menu-btn { font-size: 22px; cursor: pointer; color: var(--primary); background: none; border: none; }
        .header-title { font-size: 15px; font-weight: bold; color: var(--primary); text-align: center; }
        .notif-box { position: relative; cursor: pointer; font-size: 20px; }
        .notif-badge { position: absolute; top: -5px; right: -8px; background: #ff5252; color: white; border-radius: 50%; padding: 2px 6px; font-size: 10px; font-weight: bold; }

        /* Global Persistent Search Bar (YouTube Style) */
        .global-search-box { padding: 5px 15px 10px 15px; background: #000; position: relative; }
        .search-input-wrapper { position: relative; max-width: 800px; margin: 0 auto; }
        .search-input-wrapper input { width: 100%; padding: 10px 15px; border-radius: 20px; border: 1px solid #333; background: #1a1a1a; color: #fff; font-size: 14px; outline: none; }
        .search-input-wrapper input:focus { border-color: var(--primary); box-shadow: 0 0 8px rgba(0,230,118,0.3); }
        
        .search-results-dropdown { position: absolute; top: 45px; left: 0; right: 0; background: var(--card); border: 1px solid #333; border-radius: 8px; max-height: 350px; overflow-y: auto; box-shadow: 0 10px 20px rgba(0,0,0,0.8); z-index: 2000; display: none; }
        .search-item { padding: 10px 15px; border-bottom: 1px solid #2e2e2e; cursor: pointer; transition: 0.2s; }
        .search-item:hover { background: #2a2a2a; }
        .search-item-title { font-weight: bold; color: var(--primary); font-size: 14px; }
        .search-item-sub { font-size: 12px; color: #aaa; margin-top: 3px; }

        .auth-container { max-width: 400px; margin: 40px auto; background: var(--card); padding: 25px; border-radius: 10px; }
        input, select, textarea { width: 100%; padding: 12px; margin: 8px 0; border-radius: 6px; border: 1px solid #333; background: #2a2a2a; color: #fff; box-sizing: border-box; }
        button { width: 100%; padding: 12px; border: none; border-radius: 6px; background: var(--primary); color: #000; font-weight: bold; cursor: pointer; margin-top: 10px; }
        .btn-danger { background: #ff5252; color: #fff; }
        .btn-warning { background: #ffb74d; color: #000; }

        .sidebar-overlay { position: fixed; top: 0; left: -280px; width: 260px; height: 100%; background: var(--sidebar); z-index: 3000; transition: 0.3s; padding: 15px; box-sizing: border-box; display: flex; flex-direction: column; }
        .sidebar-overlay.active { left: 0; }
        .close-sidebar { align-self: flex-end; font-size: 18px; cursor: pointer; color: #888; margin-bottom: 10px; }
        .nav-item { padding: 12px; margin: 5px 0; background: #222; border-radius: 6px; cursor: pointer; font-size: 14px; }
        .nav-item:hover, .nav-item.active { background: var(--primary); color: #000; font-weight: bold; }

        .main-content { padding: 15px; max-width: 900px; margin: 0 auto; }
        .card { background: var(--card); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; }
        .stat-card { background: #222; border-left: 4px solid var(--primary); padding: 10px; border-radius: 8px; text-align: center; cursor: pointer; }
        .stat-card h4 { margin: 0; color: #aaa; font-size: 11px; }
        .stat-card .number { font-size: 18px; font-weight: bold; color: var(--primary); margin-top: 5px; }

        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #333; padding: 10px; text-align: left; font-size: 13px; }
        th { background: #2a2a2a; color: var(--primary); }

        /* Messenger Premium UI */
        .chat-container { display: flex; flex-direction: column; height: 500px; background: var(--chat-bg); border-radius: 10px; overflow: hidden; border: 1px solid #333; }
        .chat-header { padding: 12px 15px; background: #1a1a1a; border-bottom: 1px solid #333; display: flex; align-items: center; justify-content: space-between; }
        .chat-body { flex-grow: 1; padding: 15px; overflow-y: auto; display: flex; flex-direction: column; gap: 10px; }
        .chat-bubble { max-width: 75%; padding: 10px 14px; border-radius: 15px; font-size: 13px; line-height: 1.4; word-wrap: break-word; }
        .chat-bubble.me { background: var(--primary); color: #000; align-self: flex-end; border-bottom-right-radius: 2px; }
        .chat-bubble.other { background: #333; color: #fff; align-self: flex-start; border-bottom-left-radius: 2px; }
        .chat-bubble img, .chat-bubble video { max-width: 100%; border-radius: 8px; margin-top: 5px; }
        .typing-indicator { font-size: 11px; color: var(--primary); padding: 0 15px 5px 15px; font-style: italic; }
        .chat-footer { padding: 10px; background: #1a1a1a; display: flex; align-items: center; gap: 8px; }
        .chat-footer input[type="text"] { margin: 0; border-radius: 20px; }
        .file-btn { cursor: pointer; font-size: 20px; padding: 0 8px; }

        .backdrop { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 2500; display: none; }
        .backdrop.active { display: block; }
        .hidden { display: none !important; }
    </style>
</head>
<body>

    <div class="top-navbar-container">
        <div class="top-navbar">
            <button id="hamburger-btn" class="menu-btn hidden" onclick="toggleSidebar()">☰</button>
            <div class="header-title">বিটিসিএল (BTCL), কুড়িগ্রাম</div>
            <div id="notif-icon" class="notif-box hidden" onclick="openMessages()">
                🔔 <span id="notif-count" class="notif-badge hidden">0</span>
            </div>
        </div>

        <div id="global-search-container" class="global-search-box hidden">
            <div class="search-input-wrapper">
                <input type="text" id="global-search-input" placeholder="🔍 নাম, মোবাইল,