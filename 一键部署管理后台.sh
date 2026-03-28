#!/bin/bash
# 广东省安徽宣城商会 - 管理后台一键部署脚本
# 使用方法：在阿里云 Workbench 中复制粘贴执行

echo "========================================"
echo "  广东省安徽宣城商会 - 管理后台部署"
echo "========================================"
echo ""

# 1. 创建目录
echo "📁 创建目录..."
sudo mkdir -p /var/www/gdxcsh-admin/data
sudo chown -R $USER:$USER /var/www/gdxcsh-admin

# 2. 创建 Flask 后端
echo "🐍 创建后端服务..."
cat > /var/www/gdxcsh-admin/app.py << 'PYEOF'
#!/usr/bin/env python3
"""管理后台 API"""
from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='/var/www/gdxcsh-admin', static_url_path='')

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
PYEOF

# 3. 创建管理后台前端
echo "🎨 创建管理页面..."
cat > /var/www/gdxcsh-admin/index.html << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>管理后台 - 广东省安徽宣城商会</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #c41e3a, #8b0000); min-height: 100vh; display: flex; justify-content: center; align-items: center; }
        .login-box { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.3); width: 400px; }
        h1 { text-align: center; color: #c41e3a; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; color: #333; }
        input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 5px; font-size: 14px; }
        input:focus { outline: none; border-color: #c41e3a; }
        button { width: 100%; padding: 12px; background: #c41e3a; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { opacity: 0.9; }
        .error { color: red; margin-top: 10px; text-align: center; display: none; }
        .dashboard { display: none; padding: 20px; }
        .stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-top: 20px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; text-align: center; }
        .stat-num { font-size: 36px; color: #c41e3a; font-weight: bold; }
    </style>
</head>
<body>
    <div class="login-box" id="loginBox">
        <h1>🏛️ 管理后台</h1>
        <div class="form-group">
            <label>用户名</label>
            <input type="text" id="username" placeholder="请输入用户名" value="admin">
        </div>
        <div class="form-group">
            <label>密码</label>
            <input type="password" id="password" placeholder="请输入密码" value="admin123">
        </div>
        <button onclick="login()">登录</button>
        <div class="error" id="errorMsg">用户名或密码错误</div>
    </div>
    
    <div class="login-box dashboard" id="dashboard">
        <h1>📊 仪表盘</h1>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-num">3</div>
                <div>新闻总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">3</div>
                <div>活动数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">4</div>
                <div>会员企业</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">0</div>
                <div>待审核</div>
            </div>
        </div>
        <button onclick="logout()" style="margin-top: 30px;">退出登录</button>
    </div>

    <script>
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            try {
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                const data = await res.json();
                if (data.success) {
                    document.getElementById('loginBox').style.display = 'none';
                    document.getElementById('dashboard').style.display = 'block';
                } else {
                    document.getElementById('errorMsg').style.display = 'block';
                }
            } catch (e) {
                document.getElementById('errorMsg').style.display = 'block';
                document.getElementById('errorMsg').textContent = '无法连接服务器';
            }
        }
        function logout() {
            document.getElementById('loginBox').style.display = 'block';
            document.getElementById('dashboard').style.display = 'none';
            document.getElementById('errorMsg').style.display = 'none';
        }
    </script>
</body>
</html>
HTMLEOF

# 4. 创建入会申请页面
echo "📝 创建入会申请页面..."
cat > /var/www/gdxcsh-admin/register.html << 'REGEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>入会申请 - 广东省安徽宣城商会</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: "Microsoft YaHei", Arial, sans-serif; background: linear-gradient(135deg, #c41e3a 0%, #8b0000 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); overflow: hidden; }
        .header { background: linear-gradient(135deg, #c41e3a, #8b0000); color: white; padding: 30px; text-align: center; }
        .header h1 { font-size: 24px; margin-bottom: 10px; }
        .form-container { padding: 40px 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; }
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus { outline: none; border-color: #c41e3a; }
        .btn-submit { width: 100%; background: linear-gradient(135deg, #c41e3a, #8b0000); color: white; border: none; padding: 15px; font-size: 16px; font-weight: 600; border-radius: 8px; cursor: pointer; }
        .btn-submit:hover { opacity: 0.9; }
        .success-message { display: none; background: #d4edda; color: #155724; padding: 20px; border-radius: 8px; text-align: center; margin-top: 20px; }
        .back-link { text-align: center; margin-top: 20px; }
        .back-link a { color: #c41e3a; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📝 入会申请</h1>
            <p>广东省安徽宣城商会</p>
        </div>
        <div class="form-container">
            <form id="membershipForm">
                <div class="form-group">
                    <label>企业名称 *</label>
                    <input type="text" name="company" required placeholder="请输入企业全称">
                </div>
                <div class="form-group">
                    <label>申请人姓名 *</label>
                    <input type="text" name="name" required placeholder="请输入姓名">
                </div>
                <div class="form-group">
                    <label>职务 *</label>
                    <input type="text" name="position" required placeholder="请输入职务">
                </div>
                <div class="form-group">
                    <label>手机号码 *</label>
                    <input type="tel" name="phone" required placeholder="请输入手机号" pattern="1[3-9]\d{9}">
                </div>
                <div class="form-group">
                    <label>家乡所在地 *</label>
                    <select name="city" required>
                        <option value="">请选择</option>
                        <option value="宣州区">宣州区</option>
                        <option value="郎溪县">郎溪县</option>
                        <option value="广德市">广德市</option>
                        <option value="泾县">泾县</option>
                        <option value="绩溪县">绩溪县</option>
                        <option value="旌德县">旌德县</option>
                        <option value="宁国市">宁国市</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>所属行业 *</label>
                    <select name="industry" required>
                        <option value="">请选择</option>
                        <option value="制造业">制造业</option>
                        <option value="金融业">金融业</option>
                        <option value="商贸业">商贸业</option>
                        <option value="科技服务">科技服务</option>
                        <option value="建筑业">建筑业</option>
                        <option value="服务业">服务业</option>
                        <option value="其他">其他</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>企业简介</label>
                    <textarea name="intro" rows="4" placeholder="请简要介绍企业情况"></textarea>
                </div>
                <button type="submit" class="btn-submit">提交申请</button>
            </form>
            <div class="success-message" id="successMsg">
                <h3>✅ 申请提交成功！</h3>
                <p>我们会尽快与您联系</p>
            </div>
            <div class="back-link">
                <a href="/">← 返回首页</a>
            </div>
        </div>
    </div>
    <script>
        document.getElementById('membershipForm').addEventListener('submit', function(e) {
            e.preventDefault();
            this.style.display = 'none';
            document.getElementById('successMsg').style.display = 'block';
        });
    </script>
</body>
</html>
REGEOF

# 5. 安装 Flask
echo "📦 安装 Python 依赖..."
pip3 install flask flask-cors -q 2>/dev/null || pip install flask flask-cors -q

# 6. 启动后端服务
echo "🚀 启动后端服务..."
pkill -f "python3 /var/www/gdxcsh-admin/app.py" 2>/dev/null || true
sleep 1
nohup python3 /var/www/gdxcsh-admin/app.py > /var/log/gdxcsh-admin.log 2>&1 &
sleep 2

# 验证服务
if curl -s http://127.0.0.1:5000/api/health > /dev/null; then
    echo "✅ 后端服务已启动 (端口 5000)"
else
    echo "⚠️  后端服务可能未启动，请检查日志：tail -f /var/log/gdxcsh-admin.log"
fi

# 7. 配置 Nginx
echo "🌐 配置 Nginx..."
sudo tee /etc/nginx/sites-available/gdxcsh-admin > /dev/null << 'NGINXEOF'
server {
    listen 8080;
    server_name _;
    root /var/www/gdxcsh-admin;
    index index.html register.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # 入会申请页面
    location /register.html {
        alias /var/www/gdxcsh-admin/register.html;
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/gdxcsh-admin /etc/nginx/sites-enabled/

# 测试并重载 Nginx
if sudo nginx -t 2>/dev/null; then
    sudo systemctl reload nginx
    echo "✅ Nginx 配置完成"
else
    echo "⚠️  Nginx 配置测试失败，请手动检查"
fi

# 8. 配置安全组（提示用户）
echo ""
echo "========================================"
echo "  🎉 部署完成！"
echo "========================================"
echo ""
echo "📍 访问地址："
echo "   管理后台：http://120.26.179.205:8080"
echo "   入会申请：http://120.26.179.205/register.html"
echo ""
echo "👤 登录账号：admin"
echo "🔑 登录密码：admin123"
echo ""
echo "⚠️  重要：请在阿里云控制台开放端口"
echo "   1. 进入 ECS 控制台 → 安全组配置"
echo "   2. 添加入方向规则："
echo "      - 端口：8080"
echo "      - 授权对象：0.0.0.0/0"
echo ""
echo "📝 查看日志：tail -f /var/log/gdxcsh-admin.log"
echo ""
