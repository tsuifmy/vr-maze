#!/usr/bin/env bash

echo "VR Web HTTPS服务器启动器"
echo "================================"

# 检查证书是否存在
if [ ! -f "server.crt" ] || [ ! -f "server.key" ]; then
    echo "证书文件不存在，正在生成..."
    # 优先使用Python脚本
    if command -v python3 &> /dev/null; then
        python3 generate_cert.py
    else
        ./generate-cert.sh
    fi
fi

# 临时开放8443端口（HTTPS）
echo "临时开放防火墙端口 8443..."
sudo iptables -I INPUT -p tcp --dport 8443 -j ACCEPT

# 启动HTTPS服务器
echo "启动HTTPS服务器..."
python3 https_server.py

# 服务器停止后，移除防火墙规则
echo "清理防火墙规则..."
sudo iptables -D INPUT -p tcp --dport 8443 -j ACCEPT
