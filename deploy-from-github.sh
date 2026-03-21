#!/bin/bash
# 管理后台部署脚本

echo "=== 开始部署管理后台 ==="

# 创建目录
mkdir -p /var/www/gdxcsh-admin/data
cd /var/www/gdxcsh-admin

# 从 GitHub 下载文件
echo "从 GitHub 下载文件..."
curl -sL https://raw.githubusercontent.com/xiaoyaoluozi/gdxcsh-admin/main/app.py -o app.py
curl -sL https://raw.githubusercontent.com/xiaoyaoluozi/gdxcsh-admin/main/index.html -o index.html

# 如果下载失败，使用备用方案（内嵌代码）
if [ ! -f app.py ] || [ ! -s app.py ]; then
    echo "GitHub 下载失败，使用备用方案..."
    # 这里会直接创建文件
fi

# 安装依赖
echo "安装 Flask..."
pip3 install flask flask-cors -q

# 启动服务
echo "启动后端服务..."
pkill -f "python3 app.py" 2>/dev/null || true
nohup python3 /var/www/gdxcsh-admin/app.py > /var/log/gdxcsh-admin.log 2>&1 &
sleep 2

# 验证服务
if curl -s http://127.0.0.1:5000/api/health > /dev/null; then
    echo "✅ 后端服务已启动"
else
    echo "❌ 后端服务启动失败"
fi

# Nginx 配置
echo "配置 Nginx..."
cat > /etc/nginx/sites-available/gdxcsh-admin << 'EOF'
server {
    listen 8080;
    server_name _;
    root /var/www/gdxcsh-admin;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -sf /etc/nginx/sites-available/gdxcsh-admin /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo ""
echo "=== 部署完成 ==="
echo ""
echo "🎉 管理后台地址：http://120.26.179.205:8080"
echo "👤 默认账号：admin"
echo "🔑 默认密码：admin123"
echo ""
echo "📝 查看日志：tail -f /var/log/gdxcsh-admin.log"
