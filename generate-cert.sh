#!/usr/bin/env bash

# 生成自签名SSL证书脚本

echo "正在生成自签名SSL证书..."

# 获取本机IP地址 - 优先获取无线网卡(wlo1)的IP
LOCAL_IP=$(ip addr show wlo1 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d'/' -f1)

# 如果无线网卡没有IP，尝试有线网卡
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ip addr show enp5s0 2>/dev/null | grep "inet " | awk '{print $2}' | cut -d'/' -f1)
fi

# 如果还是没有，尝试任何活跃的网络接口
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP=$(ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K\S+')
fi

# 最后的默认值
if [ -z "$LOCAL_IP" ]; then
    LOCAL_IP="192.168.0.1"
fi

# 生成私钥
openssl genrsa -out server.key 2048

# 创建证书请求配置文件
cat > cert.conf <<EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
C = CN
ST = Local
L = Local
O = VR Web Server
OU = Development
CN = localhost

[v3_req]
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = *.local
IP.1 = 127.0.0.1
IP.2 = $LOCAL_IP
EOF

# 生成自签名证书（有效期365天）
openssl req -new -x509 -sha256 -key server.key -out server.crt -days 365 -config cert.conf

# 清理配置文件
rm cert.conf

echo "================================"
echo "✅ SSL证书生成完成！"
echo "================================"
echo "证书文件: server.crt"
echo "私钥文件: server.key"
echo "本机IP: $LOCAL_IP"
echo "================================"
