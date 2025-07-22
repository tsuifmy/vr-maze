#!/usr/bin/env python3
"""
HTTPS服务器 - 支持WebXR的VR Web应用
"""

import http.server
import ssl
import socket
import os
import sys
from urllib.parse import unquote

PORT = 8443  # HTTPS标准备用端口

class MyHTTPSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # 添加CORS头，支持跨域访问
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        # 添加安全头，支持WebXR
        self.send_header('Feature-Policy', 'xr-spatial-tracking *')
        self.send_header('Permissions-Policy', 'xr-spatial-tracking=(self)')
        # HTTPS安全头
        self.send_header('Strict-Transport-Security', 'max-age=3600')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()

    def do_GET(self):
        # 解码中文路径
        self.path = unquote(self.path)
        
        # 如果访问根路径，自动跳转到index.html
        if self.path == '/':
            self.path = '/index.html'
        
        return super().do_GET()

    def log_message(self, format, *args):
        # 自定义日志格式
        client_ip = self.client_address[0]
        print(f"[{client_ip}] {format % args}")

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 创建一个UDP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 连接到一个外部地址（不会真正发送数据）
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def check_cert_files():
    """检查SSL证书文件是否存在"""
    cert_file = 'server.crt'
    key_file = 'server.key'
    
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("❌ 错误：SSL证书文件不存在！")
        print("请先运行: ./generate-cert.sh 生成证书")
        sys.exit(1)
    
    return cert_file, key_file

def main():
    # 切换到脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 检查证书文件
    cert_file, key_file = check_cert_files()
    
    # 创建服务器 - 明确绑定到所有接口
    handler = MyHTTPSRequestHandler
    httpd = http.server.HTTPServer(('0.0.0.0', PORT), handler)
    
    # 配置SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert_file, key_file)
    
    # 包装socket
    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    
    local_ip = get_local_ip()
    
    print("=" * 60)
    print("🔒 VR Web HTTPS服务器已启动！")
    print("=" * 60)
    print(f"本地访问: https://localhost:{PORT}")
    print(f"局域网访问: https://{local_ip}:{PORT}")
    print("=" * 60)
    print("⚠️  注意：使用的是自签名证书，浏览器会显示安全警告")
    print("📱 在浏览器中需要点击\"高级\"然后\"继续访问\"")
    print("🥽 支持WebXR的VR设备：Quest 2/3, Pico, HTC Vive等")
    print("💡 确保防火墙允许端口", PORT, "的访问")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)

if __name__ == "__main__":
    main()
