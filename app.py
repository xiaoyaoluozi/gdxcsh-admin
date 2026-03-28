#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import sqlite3, os
from datetime import datetime

app = Flask(__name__, static_folder='/var/www/gdxcsh-admin', static_url_path='')
CORS(app)
DB_PATH = '/var/www/gdxcsh-admin/data/admin.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        return jsonify({'success': True, 'token': 'admin_token', 'user': {'username': 'admin'}})
    return jsonify({'error': '用户名或密码错误'}), 401

@app.route('/api/dashboard')
def dashboard():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM news'); news = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM events'); events = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM companies'); companies = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM applications WHERE status='pending'"); pending = c.fetchone()[0]
    conn.close()
    return jsonify({'news': news, 'events': events, 'companies': companies, 'pending_applications': pending})

@app.route('/api/news', methods=['GET'])
def get_news():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM news ORDER BY publish_date DESC')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/news', methods=['POST'])
def create_news():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO news (title, summary, category, publish_date) VALUES (?,?,?,?)',
              (data.get('title'), data.get('summary'), data.get('category'), data.get('publish_date')))
    conn.commit()
    nid = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': nid})

@app.route('/api/news/<int:id>', methods=['PUT'])
def update_news(id):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE news SET title=?, summary=?, category=?, publish_date=? WHERE id=?',
              (data.get('title'), data.get('summary'), data.get('category'), data.get('publish_date'), id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/news/<int:id>', methods=['DELETE'])
def delete_news(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM news WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM events ORDER BY start_time DESC')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO events (title, description, location, start_time, organizer, status) VALUES (?,?,?,?,?,?)',
              (data.get('title'), data.get('description'), data.get('location'), data.get('start_time'), data.get('organizer'), data.get('status','pending')))
    conn.commit()
    eid = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': eid})

@app.route('/api/events/<int:id>', methods=['PUT'])
def update_event(id):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE events SET title=?, description=?, location=?, start_time=?, organizer=?, status=? WHERE id=?',
              (data.get('title'), data.get('description'), data.get('location'), data.get('start_time'), data.get('organizer'), data.get('status'), id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/events/<int:id>', methods=['GET'])
def get_event(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM events WHERE id=?', (id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/events/<int:id>', methods=['DELETE'])
def delete_event(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM events WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/companies', methods=['GET'])
def get_companies():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM companies ORDER BY created_at DESC')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/companies', methods=['POST'])
def create_company():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO companies 
        (member_no, company_name, chamber_position, name, company_position, shenzhen_district, jiguang, industry, contact_person, member_level) 
        VALUES (?,?,?,?,?,?,?,?,?,?)''',
              (data.get('member_no'), data.get('company_name'), data.get('chamber_position'), 
               data.get('name'), data.get('company_position'), data.get('shenzhen_district'),
               data.get('jiguang'), data.get('industry'), data.get('contact_person'), data.get('member_level')))
    conn.commit()
    cid = c.lastrowid
    conn.close()
    return jsonify({'success': True, 'id': cid})

@app.route('/api/companies/<int:id>', methods=['PUT'])
def update_company(id):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('''UPDATE companies SET member_no=?, company_name=?, chamber_position=?, name=?, 
        company_position=?, shenzhen_district=?, jiguang=?, industry=?, contact_person=?, member_level=? WHERE id=?''',
              (data.get('member_no'), data.get('company_name'), data.get('chamber_position'),
               data.get('name'), data.get('company_position'), data.get('shenzhen_district'),
               data.get('jiguang'), data.get('industry'), data.get('contact_person'), data.get('member_level'), id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/companies/<int:id>', methods=['GET'])
def get_company(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM companies WHERE id=?', (id,))
    row = c.fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/companies/<int:id>', methods=['DELETE'])
def delete_company(id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM companies WHERE id=?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/applications', methods=['GET'])
def get_applications():
    conn = get_db()
    c = conn.cursor()
    status = request.args.get('status')
    if status:
        c.execute('SELECT * FROM applications WHERE status=? ORDER BY created_at DESC', (status,))
    else:
        c.execute('SELECT * FROM applications ORDER BY created_at DESC')
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify(rows)

@app.route('/api/applications/<int:id>', methods=['PUT'])
def review_application(id):
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE applications SET status=?, reviewed_at=?, reviewed_by=? WHERE id=?',
              (data.get('status'), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'admin', id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/')
def index():
    return send_from_directory('/var/www/gdxcsh-admin', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
