#!/usr/bin/env python3
"""
管理后台 API - 简化版本
"""
from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='/var/www/gdxcsh-admin', static_url_path='')
DATABASE = '/var/www/gdxcsh-admin/data/admin.db'

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'message': '管理后台运行中'})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        return jsonify({'success': True, 'token': 'admin_token', 'user': {'username': 'admin'}})
    return jsonify({'error': '用户名或密码错误'}), 401

@app.route('/')
def index():
    return send_from_directory('/var/www/gdxcsh-admin', 'index.html')

if __name__ == '__main__':
    os.makedirs('/var/www/gdxcsh-admin/data', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=False)
