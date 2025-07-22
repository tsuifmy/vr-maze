#!/usr/bin/env python3
"""
生成自签名SSL证书 - 使用Python内置库
"""

import os
import socket
import subprocess
import datetime
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import ipaddress

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 尝试从网络接口获取
        result = subprocess.run(['ip', 'route', 'get', '8.8.8.8'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # 从输出中提取 src 后面的IP
            for part in result.stdout.split():
                if prev_was_src:
                    return part
                prev_was_src = (part == 'src')
    except:
        pass
    
    # 备用方法
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.0.1"

def generate_self_signed_cert():
    """生成自签名证书"""
    
    print("正在生成自签名SSL证书...")
    
    # 获取本机IP
    local_ip = get_local_ip()
    print(f"检测到本机IP: {local_ip}")
    
    # 生成私钥
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # 证书主题
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Local"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "VR Web Server"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Development"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    # 创建证书
    cert_builder = x509.CertificateBuilder()
    cert_builder = cert_builder.subject_name(subject)
    cert_builder = cert_builder.issuer_name(issuer)
    cert_builder = cert_builder.public_key(private_key.public_key())
    cert_builder = cert_builder.serial_number(x509.random_serial_number())
    cert_builder = cert_builder.not_valid_before(datetime.datetime.utcnow())
    cert_builder = cert_builder.not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    )
    
    # 添加扩展 - Subject Alternative Names
    san_list = [
        x509.DNSName("localhost"),
        x509.DNSName("*.local"),
        x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
    ]
    
    # 添加检测到的本机IP
    try:
        san_list.append(x509.IPAddress(ipaddress.IPv4Address(local_ip)))
    except:
        pass
    
    cert_builder = cert_builder.add_extension(
        x509.SubjectAlternativeName(san_list),
        critical=False,
    )
    
    # 添加密钥用途
    cert_builder = cert_builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            content_commitment=False,
            key_encipherment=True,
            data_encipherment=False,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )
    
    # 添加扩展密钥用途
    cert_builder = cert_builder.add_extension(
        x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]),
        critical=True,
    )
    
    # 签名证书
    cert = cert_builder.sign(private_key, hashes.SHA256())
    
    # 保存私钥
    with open("server.key", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # 保存证书
    with open("server.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print("=" * 60)
    print("✅ SSL证书生成完成！")
    print("=" * 60)
    print("证书文件: server.crt")
    print("私钥文件: server.key")
    print(f"本机IP: {local_ip}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        generate_self_signed_cert()
    except ImportError:
        print("错误：需要安装 cryptography 库")
        print("请运行: pip install cryptography")
        print("\n或者在 NixOS 上使用 nix-shell:")
        print("nix-shell -p python3Packages.cryptography")
        exit(1)
