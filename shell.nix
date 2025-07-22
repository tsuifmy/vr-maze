{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.cryptography
    openssl
  ];
  
  shellHook = ''
    echo "VR Web 开发环境已加载"
    echo "可用命令："
    echo "  ./generate_cert.py     - 生成SSL证书"
    echo "  ./start-https-server.sh - 启动HTTPS服务器"
  '';
}
