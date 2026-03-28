#!/usr/bin/env python3
"""
广东省安徽宣城商会 - 管理后台 API
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime

app = Flask(__name__, static_folder='/var/www/gdxcsh-admin', static_url_path='')
CORS(app)

DB_PATH = '/var/www/gdxcsh-admin/data/admin.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db_if_not_exists():
    if not os.path.exists(DB_PATH):
        os.system('python3 /var/www/gdxcsh-admin/init_db.py')

# ============ 认证 ============
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        return jsonify({
            'success': True,
            'token': 'admin_token_' + datetime.now().strftime('%Y%m%d%H%M%S'),
            'user': {'username': 'admin', 'role': 'admin'}
        })
    return jsonify({'error': '用户名或密码错误'}), 401

# ============ 仪表盘 ============
@app.route('/api/dashboard')
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM news')
    news_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM events')
    event_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM companies')
    company_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM applications WHERE status='pending'")
    pending_count = cursor.fetchone()[0]
    conn.close()
    return jsonify({
        'news': news_count,
        'events': event_count,
        'companies': company_count,
        'pending_applications': pending_count
    })

# ============ 新闻管理 ============
@app.route('/api/news', methods=['GET'])
def get_news():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM news ORDER BY publish_date DESC')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/news', methods=['POST'])
def create_news():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO news (title, summary, content, category, image_url, link_url, publish_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('title'), data.get('summary'), data.get('content'),
          data.get('category'), data.get('image_url'), data.get('link_url'), data.get('publish_date')))
    conn.commit()
    news_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': news_id})

@app.route('/api/news/<int:id>', methods=['PUT'])
def update_news(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE news SET title=?, summary=?, content=?, category=?, image_url=?, link_url=?, publish_date=?
        WHERE id=?
    ''', (data.get('title'), data.get('summary'), data.get('content'),
          data.get('category'), data.get('image_url'), data.get('link_url'), data.get('publish_date'), id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/news/<int:id>', methods=['DELETE'])
def delete_news(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM news WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ============ 活动管理 ============
@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM events ORDER BY start_time DESC')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (title, description, location, start_time, end_time, organizer, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('title'), data.get('description'), data.get('location'),
          data.get('start_time'), data.get('end_time'), data.get('organizer'), data.get('status', 'pending')))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': event_id})

@app.route('/api/events/<int:id>', methods=['PUT'])
def update_event(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE events SET title=?, description=?, location=?, start_time=?, end_time=?, organizer=?, status=?
        WHERE id=?
    ''', (data.get('title'), data.get('description'), data.get('location'),
          data.get('start_time'), data.get('end_time'), data.get('organizer'), data.get('status'), id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/events/<int:id>', methods=['DELETE'])
def delete_event(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM events WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ============ 会员企业管理 ============
@app.route('/api/companies', methods=['GET'])
def get_companies():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM companies ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/companies', methods=['POST'])
def create_company():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO companies (name, industry, contact_person, phone, address, description, member_level, join_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data.get('name'), data.get('industry'), data.get('contact_person'),
          data.get('phone'), data.get('address'), data.get('description'), data.get('member_level'), data.get('join_date')))
    conn.commit()
    company_id = cursor.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': company_id})

@app.route('/api/companies/<int:id>', methods=['PUT'])
def update_company(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE companies SET name=?, industry=?, contact_person=?, phone=?, address=?, description=?, member_level=?
        WHERE id=?
    ''', (data.get('name'), data.get('industry'), data.get('contact_person'),
          data.get('phone'), data.get('address'), data.get('description'), data.get('member_level'), id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/companies/<int:id>', methods=['DELETE'])
def delete_company(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM companies WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ============ 入会申请管理 ============
@app.route('/api/applications', methods=['GET'])
def get_applications():
    conn = get_db()
    cursor = conn.cursor()
    status = request.args.get('status')
    if status:
        cursor.execute('SELECT * FROM applications WHERE status=? ORDER BY created_at DESC', (status,))
    else:
        cursor.execute('SELECT * FROM applications ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/api/applications/<int:id>', methods=['PUT'])
def review_application(id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE applications SET status=?, reviewed_at=?, reviewed_by=?
        WHERE id=?
    ''', (data.get('status'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'admin', id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/applications/<int:id>', methods=['DELETE'])
def delete_application(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM applications WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ============ 静态文件 ============
@app.route('/')
def index():
    return send_from_directory('/var/www/gdxcsh-admin', 'index.html')

if __name__ == '__main__':
    init_db_if_not_exists()
    app.run(host='0.0.0.0', port=5000, debug=False)
