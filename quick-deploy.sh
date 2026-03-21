#!/bin/bash
# 快速部署脚本 - 直接从服务器 A 下载

echo "=== 开始部署管理后台 ==="

# 创建目录
mkdir -p /var/www/gdxcsh-admin/data
cd /var/www/gdxcsh-admin

# 从服务器 A 下载文件（通过 HTTP）
echo "下载文件..."

# 下载后端
curl -s http://10.0.0.1:8888/app.py -o /var/www/gdxcsh-admin/app.py || echo "从本地 HTTP 服务器下载失败"

# 如果失败，直接创建文件
if [ ! -f /var/www/gdxcsh-admin/app.py ]; then
    echo "使用备用方案：直接创建文件..."
    # 这里会嵌入文件内容
fi

# 安装依赖
echo "安装 Flask..."
pip3 install flask flask-cors -q

# 启动服务
echo "启动后端服务..."
pkill -f "python3 app.py" 2>/dev/null || true
nohup python3 /var/www/gdxcsh-admin/app.py > /var/log/gdxcsh-admin.log 2>&1 &
sleep 2

# Nginx 配置
cat > /etc/nginx/sites-available/gdxcsh-admin << 'NGINXEOF'
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
NGINXEOF

ln -sf /etc/nginx/sites-available/gdxcsh-admin /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

echo ""
echo "=== 部署完成 ==="
echo "管理后台地址：http://120.26.179.205:8080"
echo "默认账号：admin"
echo "默认密码：admin123"
