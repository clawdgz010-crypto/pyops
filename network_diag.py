#!/usr/bin/env python3
"""
网络诊断工具 - 网络连接诊断和测试
"""
import socket
import subprocess
import platform
import time
import re
from datetime import datetime
import argparse


def ping_host(host, count=4):
    """Ping 主机"""
    print(f"\n🌐 Ping: {host}")
    print("=" * 60)
    
    # 根据系统选择参数
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    
    try:
        result = subprocess.run(
            ['ping', param, str(count), host],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(result.stdout)
        
        # 解析统计信息
        if platform.system().lower() != 'windows':
            # Linux/Mac 解析
            match = re.search(r'(\d+)% packet loss', result.stdout)
            if match:
                loss = match.group(1)
                print(f"📊 丢包率: {loss}%")
            
            match = re.search(r'rtt min/avg/max/mdev = ([\d.]+)/([\d.]+)/([\d.]+)', result.stdout)
            if match:
                print(f"📊 延迟: 最小 {match.group(1)}ms, 平均 {match.group(2)}ms, 最大 {match.group(3)}ms")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ 超时")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def check_dns(domain):
    """检查 DNS 解析"""
    print(f"\n🔍 DNS 解析: {domain}")
    print("=" * 60)
    
    try:
        # 使用 nslookup
        result = subprocess.run(
            ['nslookup', domain],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # 解析 IP 地址
        ips = re.findall(r'Address:\s*([\d.]+)', result.stdout)
        ips = [ip for ip in ips if not ip.startswith('127.') and not ip.startswith('192.168.1.')]
        
        if ips:
            print(f"✅ 解析成功:")
            for ip in ips:
                print(f"   📍 {ip}")
            return ips
        else:
            print("❌ 解析失败")
            return []
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def check_http(url, timeout=10):
    """检查 HTTP 连接"""
    print(f"\n🌐 HTTP 检查: {url}")
    print("=" * 60)
    
    try:
        import urllib.request
        import urllib.error
        
        start_time = time.time()
        
        try:
            response = urllib.request.urlopen(url, timeout=timeout)
            elapsed = (time.time() - start_time) * 1000
            
            print(f"✅ 状态码: {response.status}")
            print(f"📊 响应时间: {elapsed:.2f}ms")
            print(f"📄 内容类型: {response.headers.get('Content-Type', 'N/A')}")
            print(f"📏 内容大小: {response.headers.get('Content-Length', 'N/A')}")
            
            return True
            
        except urllib.error.HTTPError as e:
            print(f"⚠️  HTTP 错误: {e.code} {e.reason}")
            return False
        except urllib.error.URLError as e:
            print(f"❌ 连接失败: {e.reason}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def trace_route(host, max_hops=30):
    """路由追踪"""
    print(f"\n🛤️  路由追踪: {host}")
    print("=" * 60)
    
    # 根据系统选择命令
    if platform.system().lower() == 'windows':
        cmd = ['tracert', '-d', '-h', str(max_hops), host]
    else:
        cmd = ['traceroute', '-n', '-m', str(max_hops), host]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ 超时")
        return False
    except FileNotFoundError:
        print("❌ 未安装 traceroute/tracert 命令")
        return False
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def get_network_info():
    """获取网络信息"""
    import psutil
    
    print("\n📡 网络接口信息")
    print("=" * 60)
    
    # 获取网络接口
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    
    for iface, addrs in interfaces.items():
        if iface == 'lo':
            continue
            
        stat = stats.get(iface)
        if stat and stat.isup:
            print(f"\n🔌 {iface}")
            print(f"   状态: {'UP' if stat.isup else 'DOWN'}")
            print(f"   速度: {stat.speed} Mbps" if stat.speed > 0 else "")
            
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    print(f"   IPv4: {addr.address}")
                    print(f"   掩码: {addr.netmask}")
                elif addr.family == socket.AF_INET6:
                    if not addr.address.startswith('fe80'):
                        print(f"   IPv6: {addr.address[:30]}...")
    
    # 默认网关
    try:
        result = subprocess.run(
            ['ip', 'route', 'show', 'default'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            match = re.search(r'via ([\d.]+)', result.stdout)
            if match:
                print(f"\n🚪 默认网关: {match.group(1)}")
    except:
        pass
    
    # DNS 服务器
    try:
        with open('/etc/resolv.conf') as f:
            dns_servers = re.findall(r'nameserver\s+([\d.]+)', f.read())
            if dns_servers:
                print(f"\n🌐 DNS 服务器:")
                for dns in dns_servers:
                    print(f"   {dns}")
    except:
        pass


def check_connectivity():
    """检查网络连通性"""
    print("\n🌐 网络连通性测试")
    print("=" * 60)
    
    test_hosts = [
        ('百度', 'www.baidu.com'),
        ('阿里云', 'www.aliyun.com'),
        ('腾讯', 'www.qq.com'),
        ('Google', 'www.google.com'),
        ('GitHub', 'github.com'),
    ]
    
    results = []
    
    for name, host in test_hosts:
        start_time = time.time()
        try:
            socket.setdefaulttimeout(5)
            socket.getaddrinfo(host, None)
            elapsed = (time.time() - start_time) * 1000
            print(f"✅ {name:<12} {host:<20} {elapsed:.0f}ms")
            results.append((name, True, elapsed))
        except:
            print(f"❌ {name:<12} {host:<20} 失败")
            results.append((name, False, 0))
    
    success = sum(1 for r in results if r[1])
    print(f"\n📊 连通性: {success}/{len(results)} 成功")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="网络诊断工具")
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # ping 命令
    ping_parser = subparsers.add_parser('ping', help='Ping 主机')
    ping_parser.add_argument('host', help='主机地址')
    ping_parser.add_argument('-c', '--count', type=int, default=4, help='次数')
    
    # dns 命令
    dns_parser = subparsers.add_parser('dns', help='检查 DNS 解析')
    dns_parser.add_argument('domain', help='域名')
    
    # http 命令
    http_parser = subparsers.add_parser('http', help='检查 HTTP 连接')
    http_parser.add_argument('url', help='URL')
    http_parser.add_argument('-t', '--timeout', type=int, default=10, help='超时(秒)')
    
    # trace 命令
    trace_parser = subparsers.add_parser('trace', help='路由追踪')
    trace_parser.add_argument('host', help='主机地址')
    trace_parser.add_argument('-m', '--max-hops', type=int, default=30, help='最大跳数')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='显示网络信息')
    
    # check 命令
    check_parser = subparsers.add_parser('check', help='检查网络连通性')
    
    args = parser.parse_args()
    
    if args.command == 'ping':
        ping_host(args.host, args.count)
    elif args.command == 'dns':
        check_dns(args.domain)
    elif args.command == 'http':
        check_http(args.url, args.timeout)
    elif args.command == 'trace':
        trace_route(args.host, args.max_hops)
    elif args.command == 'info':
        get_network_info()
    elif args.command == 'check':
        check_connectivity()
    else:
        # 默认检查连通性
        check_connectivity()
