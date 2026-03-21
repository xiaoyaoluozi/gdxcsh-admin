#!/usr/bin/env python3
"""
广东省安徽宣城商会 - 管理后台 API 服务
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3, hashlib, os

app = Flask(__name__)
CORS(app)
DATABASE = '/var/www/gdxcsh-admin/data/admin.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # 创建表
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, role TEXT DEFAULT "admin")')
    c.execute('CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, title TEXT, content TEXT, publish_date DATE, source_url TEXT, status TEXT DEFAULT "draft")')
    c.execute('CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, title TEXT, location TEXT, start_time DATETIME, status TEXT DEFAULT "upcoming")')
    c.execute('CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, company_name TEXT, industry TEXT, contact_person TEXT, position TEXT, status TEXT DEFAULT "active")')
    c.execute('CREATE TABLE IF NOT EXISTS applications (id INTEGER PRIMARY KEY, company_name TEXT, applicant_name TEXT, phone TEXT, city TEXT, status TEXT DEFAULT "pending")')
    c.execute('CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, key TEXT UNIQUE, value TEXT)')
    
    # 默认管理员 admin/admin123
    c.execute('INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)', 
              ('admin', hashlib.sha256('admin123'.encode()).hexdigest()))
    
    # 导入现有新闻数据
    if c.execute('SELECT COUNT(*) FROM news').fetchone()[0] == 0:
        c.executemany('INSERT INTO news (title, content, publish_date, source_url, status) VALUES (?,?,?,?,?)', [
            ('第三届三次常务理事会会议：务实高效，引领商会新发展', '会议讨论激烈，务实高效，为商会未来的发展指明了方向。确定了一系列公益活动...', '2025-09-23', 'https://mp.weixin.qq.com/s/0vNYMHIMqKmHFxoX_DCBcA', 'published'),
            ('广东宣城商会双节活动：情暖他乡，共筑团圆梦', '掼蛋联谊，情系桑梓。二十多位东莞片区的成员和乡友们齐聚一堂...', '2025-10-09', 'https://mp.weixin.qq.com/s/-tn23wzcqqG_545LJOKNkg', 'published'),
            ('广东宣城商会成立两周年庆典暨春茗会隆重举行', '近 500 余人共同见证了此次盛典，与 30 多家兄弟商会举行友好合作签约...', '2019-03-16', 'https://mp.weixin.qq.com/s/JSJoC9E9TsLcrlGvqu0GNQ', 'published'),
        ])
    
    # 导入现有活动数据
    if c.execute('SELECT COUNT(*) FROM events').fetchone()[0] == 0:
        c.executemany('INSERT INTO events (title, location, start_time, status) VALUES (?,?,?,?)', [
            ('敬老院慰问关怀活动', '旌德、绩溪两县敬老院', '2026-09-24 09:00:00', 'upcoming'),
            ('广东名医专家宣城义诊活动', '宣城市中心医院', '2026-10-24 09:00:00', 'upcoming'),
            ('掼蛋联谊活动', '东莞/广州/深圳', '2026-04-01 19:00:00', 'upcoming'),
        ])
    
    # 导入现有会员数据
    if c.execute('SELECT COUNT(*) FROM members').fetchone()[0] == 0:
        c.executemany('INSERT INTO members (company_name, industry, contact_person, position, status) VALUES (?,?,?,?,?)', [
            ('深圳市筑福环保科技', '制造业', '朱财福', '董事长', 'active'),
            ('粤宣投资集团', '金融业', '', '', 'active'),
            ('华南商贸集团', '商贸业', '', '', 'active'),
            ('芯丰园老字号', '商贸业', '刘团结', '创始人', 'active'),
        ])
    
    # 导入网站配置
    if c.execute('SELECT COUNT(*) FROM settings').fetchone()[0] == 0:
        c.executemany('INSERT INTO settings (key, value) VALUES (?,?)', [
            ('site_name', '广东省安徽宣城商会'),
            ('site_phone', '13603046717'),
            ('site_email', 'info@gdxcsh.org'),
            ('site_address', '深圳市南山区南海大道海王大厦 A 座 19C'),
        ])
    
    conn.commit()
    conn.close()
    print('数据库初始化完成')

# ============= API 路由 =============

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': '管理后台 API 运行中'})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    password_hash = hashlib.sha256(data.get('password', '').encode()).hexdigest()
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ? AND password_hash = ?', 
                        (data.get('username'), password_hash)).fetchone()
    conn.close()
    if user:
        return jsonify({
            'success': True, 
            'token': f'Bearer_{user["id"]}', 
            'user': {'id': user['id'], 'username': user['username'], 'role': user.get('role', 'admin')}
        })
    return jsonify({'error': '用户名或密码错误'}), 401

@app.route('/api/dashboard')
def dashboard():
    conn = get_db()
    stats = {
        'news': conn.execute('SELECT COUNT(*) FROM news WHERE status = "published"').fetchone()[0],
        'events': conn.execute('SELECT COUNT(*) FROM events WHERE status = "upcoming"').fetchone()[0],
        'members': conn.execute('SELECT COUNT(*) FROM members').fetchone()[0],
        'pending': conn.execute('SELECT COUNT(*) FROM applications WHERE status = "pending"').fetchone()[0],
    }
    recent_news = [dict(r) for r in conn.execute('SELECT title, publish_date as created_at FROM news ORDER BY publish_date DESC LIMIT 3').fetchall()]
    conn.close()
    return jsonify({'stats': stats, 'recent_news': recent_news})

@app.route('/api/news')
def get_news():
    conn = get_db()
    news = [dict(r) for r in conn.execute('SELECT * FROM news ORDER BY publish_date DESC').fetchall()]
    conn.close()
    return jsonify(news)

@app.route('/api/news', methods=['POST'])
def create_news():
    d = request.json
    conn = get_db()
    conn.execute('INSERT INTO news (title, content, publish_date, source_url, status) VALUES (?,?,?,?,?)',
                 (d.get('title'), d.get('content'), d.get('publish_date'), d.get('source_url'), d.get('status', 'draft')))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/news/<int:id>', methods=['DELETE'])
def delete_news(id):
    conn = get_db()
    conn.execute('DELETE FROM news WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/events')
def get_events():
    conn = get_db()
    events = [dict(r) for r in conn.execute('SELECT * FROM events ORDER BY start_time').fetchall()]
    conn.close()
    return jsonify(events)

@app.route('/api/members')
def get_members():
    conn = get_db()
    members = [dict(r) for r in conn.execute('SELECT * FROM members').fetchall()]
    conn.close()
    return jsonify(members)

@app.route('/api/applications')
def get_applications():
    conn = get_db()
    apps = [dict(r) for r in conn.execute('SELECT * FROM applications ORDER BY id DESC').fetchall()]
    conn.close()
    return jsonify(apps)

@app.route('/api/applications/<int:id>/status', methods=['PUT'])
def update_application_status(id):
    d = request.json
    conn = get_db()
    conn.execute('UPDATE applications SET status = ? WHERE id = ?', (d.get('status'), id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/settings')
def get_settings():
    conn = get_db()
    settings = {r['key']: r['value'] for r in conn.execute('SELECT * FROM settings').fetchall()}
    conn.close()
    return jsonify(settings)

@app.route('/api/settings', methods=['PUT'])
def update_settings():
    d = request.json
    conn = get_db()
    for k, v in d.items():
        conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (k, v))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
