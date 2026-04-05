#!/usr/bin/env python3
"""
SSH 配置管理工具 - 管理 SSH 连接和密钥
"""
import os
import subprocess
from pathlib import Path
import argparse
from datetime import datetime


SSH_DIR = Path.home() / '.ssh'
SSH_CONFIG = SSH_DIR / 'config'
KNOWN_HOSTS = SSH_DIR / 'known_hosts'


def ensure_ssh_dir():
    """确保 SSH 目录存在"""
    SSH_DIR.mkdir(parents=True, exist_ok=True)
    SSH_DIR.chmod(0o700)


def list_ssh_keys():
    """列出 SSH 密钥"""
    ensure_ssh_dir()
    
    print(f"\n🔑 SSH 密钥列表")
    print("=" * 70)
    
    keys = []
    for key_file in SSH_DIR.glob('*'):
        if key_file.is_file() and not key_file.name.endswith('.pub') and not key_file.name in ['known_hosts', 'config', 'authorized_keys']:
            pub_key = key_file.with_suffix('.pub') if key_file.suffix else SSH_DIR / f"{key_file.name}.pub"
            
            key_info = {
                'file': key_file.name,
                'path': str(key_file),
                'has_public': pub_key.exists(),
                'type': 'Unknown'
            }
            
            # 获取密钥类型
            try:
                result = subprocess.run(['ssh-keygen', '-l', '-f', str(key_file)], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    parts = result.stdout.strip().split()
                    if len(parts) >= 4:
                        key_info['type'] = parts[-1]
                        key_info['bits'] = parts[0]
            except:
                pass
            
            keys.append(key_info)
    
    if keys:
        for key in keys:
            status = "✅" if key['has_public'] else "⚠️ "
            print(f"{status} {key['file']:<30} {key['type']:<10} {key.get('bits', 'N/A')}")
    else:
        print("📭 暂无 SSH 密钥")
    
    return keys


def generate_ssh_key(key_name, key_type='ed25519', email=None, passphrase=None):
    """生成 SSH 密钥"""
    ensure_ssh_dir()
    
    key_path = SSH_DIR / key_name
    
    if key_path.exists():
        print(f"❌ 密钥已存在: {key_path}")
        return False
    
    print(f"🔐 生成 SSH 密钥...")
    print(f"  名称: {key_name}")
    print(f"  类型: {key_type}")
    print(f"  路径: {key_path}")
    
    cmd = ['ssh-keygen', '-t', key_type, '-f', str(key_path), '-N', passphrase or '']
    
    if email:
        cmd.extend(['-C', email])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n✅ 密钥生成成功!")
            print(f"\n公钥内容:")
            pub_key_path = key_path.with_suffix('.pub') if key_path.suffix else SSH_DIR / f"{key_name}.pub"
            with open(pub_key_path) as f:
                print(f.read().strip())
            return True
        else:
            print(f"❌ 密钥生成失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def list_ssh_hosts():
    """列出 SSH 配置的主机"""
    if not SSH_CONFIG.exists():
        print("📭 暂无 SSH 配置文件")
        return []
    
    print(f"\n🖥️  SSH 主机配置")
    print("=" * 70)
    print(f"{'主机名':<20} {'地址':<30} {'用户':<10} {'端口'}")
    print("=" * 70)
    
    hosts = []
    current_host = None
    
    with open(SSH_CONFIG) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.lower().startswith('host '):
                if current_host:
                    hosts.append(current_host)
                host_name = line.split()[1]
                current_host = {
                    'host': host_name,
                    'hostname': '',
                    'user': '',
                    'port': '22'
                }
            elif current_host:
                parts = line.split()
                if len(parts) >= 2:
                    key = parts[0].lower()
                    value = ' '.join(parts[1:])
                    if key == 'hostname':
                        current_host['hostname'] = value
                    elif key == 'user':
                        current_host['user'] = value
                    elif key == 'port':
                        current_host['port'] = value
        
        if current_host:
            hosts.append(current_host)
    
    for host in hosts:
        print(f"{host['host']:<20} {host['hostname']:<30} {host['user']:<10} {host['port']}")
    
    return hosts


def add_ssh_host(host_name, hostname, user=None, port=None, identity_file=None):
    """添加 SSH 主机配置"""
    ensure_ssh_dir()
    
    # 检查是否已存在
    if SSH_CONFIG.exists():
        with open(SSH_CONFIG) as f:
            if f"Host {host_name}" in f.read():
                print(f"❌ 主机配置已存在: {host_name}")
                return False
    
    print(f"➕ 添加 SSH 主机配置: {host_name}")
    
    with open(SSH_CONFIG, 'a') as f:
        f.write(f"\nHost {host_name}\n")
        f.write(f"    HostName {hostname}\n")
        if user:
            f.write(f"    User {user}\n")
        if port:
            f.write(f"    Port {port}\n")
        if identity_file:
            f.write(f"    IdentityFile {identity_file}\n")
    
    print("✅ 主机配置已添加")
    return True


def test_ssh_connection(host_name):
    """测试 SSH 连接"""
    print(f"🔌 测试 SSH 连接: {host_name}")
    
    try:
        result = subprocess.run(
            ['ssh', '-o', 'ConnectTimeout=5', '-o', 'BatchMode=yes', host_name, 'echo', 'OK'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and 'OK' in result.stdout:
            print("✅ 连接成功!")
            return True
        else:
            print(f"❌ 连接失败: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 连接超时")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def copy_ssh_key(host_name):
    """复制公钥到远程主机"""
    print(f"📋 复制公钥到: {host_name}")
    
    try:
        result = subprocess.run(['ssh-copy-id', host_name], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ 公钥已复制")
            return True
        else:
            print(f"❌ 复制失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SSH 配置管理工具")
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # keys 命令
    keys_parser = subparsers.add_parser('keys', help='列出 SSH 密钥')
    
    # gen-key 命令
    gen_parser = subparsers.add_parser('gen-key', help='生成 SSH 密钥')
    gen_parser.add_argument('-n', '--name', required=True, help='密钥名称')
    gen_parser.add_argument('-t', '--type', default='ed25519', choices=['rsa', 'ed25519', 'ecdsa'], help='密钥类型')
    gen_parser.add_argument('-e', '--email', help='邮箱注释')
    
    # hosts 命令
    hosts_parser = subparsers.add_parser('hosts', help='列出 SSH 主机配置')
    
    # add-host 命令
    add_parser = subparsers.add_parser('add-host', help='添加 SSH 主机配置')
    add_parser.add_argument('-n', '--name', required=True, help='主机别名')
    add_parser.add_argument('-H', '--hostname', required=True, help='主机地址')
    add_parser.add_argument('-u', '--user', help='用户名')
    add_parser.add_argument('-p', '--port', type=int, help='端口')
    add_parser.add_argument('-i', '--identity', help='密钥文件路径')
    
    # test 命令
    test_parser = subparsers.add_parser('test', help='测试 SSH 连接')
    test_parser.add_argument('host', help='主机名')
    
    # copy-id 命令
    copy_parser = subparsers.add_parser('copy-id', help='复制公钥到远程主机')
    copy_parser.add_argument('host', help='主机名')
    
    args = parser.parse_args()
    
    if args.command == 'keys':
        list_ssh_keys()
    elif args.command == 'gen-key':
        generate_ssh_key(args.name, args.type, args.email)
    elif args.command == 'hosts':
        list_ssh_hosts()
    elif args.command == 'add-host':
        add_ssh_host(args.name, args.hostname, args.user, args.port, args.identity)
    elif args.command == 'test':
        test_ssh_connection(args.host)
    elif args.command == 'copy-id':
        copy_ssh_key(args.host)
    else:
        # 默认显示主机列表
        list_ssh_hosts()
