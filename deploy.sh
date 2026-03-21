#!/bin/bash
# 管理后台部署脚本

echo "=== 开始部署管理后台 ==="

# 创建目录
mkdir -p /var/www/gdxcsh-admin/data
cd /var/www/gdxcsh-admin

# 安装依赖
echo "安装 Flask..."
pip3 install flask flask-cors -q

# 启动后端服务（后台运行）
echo "启动后端服务..."
pkill -f "python3 app.py" 2>/dev/null || true
nohup python3 /var/www/gdxcsh-admin/app.py > /var/log/gdxcsh-admin.log 2>&1 &
sleep 2

# 创建 Nginx 配置
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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# 启用配置
ln -sf /etc/nginx/sites-available/gdxcsh-admin /etc/nginx/sites-enabled/

# 重载 Nginx
echo "配置 Nginx..."
nginx -t && systemctl reload nginx

echo ""
echo "=== 部署完成 ==="
echo "管理后台地址：http://120.26.179.205:8080"
echo "默认账号：admin"
echo "默认密码：admin123"
echo ""
echo "查看日志：tail -f /var/log/gdxcsh-admin.log"
