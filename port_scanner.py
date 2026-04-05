#!/usr/bin/env python3
"""
端口扫描工具 - 检查端口占用和网络连接
"""
import socket
import psutil
from datetime import datetime
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed


def check_port(port, host='localhost', timeout=1):
    """检查单个端口"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def scan_ports(host='localhost', start_port=1, end_port=1024, max_workers=100):
    """扫描端口范围"""
    print(f"\n🔍 扫描端口: {host}:{start_port}-{end_port}")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    open_ports = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_port, port, host): port for port in range(start_port, end_port + 1)}
        
        for future in as_completed(futures):
            port = futures[future]
            if future.result():
                open_ports.append(port)
    
    # 排序并显示结果
    open_ports.sort()
    
    if open_ports:
        print(f"\n✅ 发现 {len(open_ports)} 个开放端口:\n")
        for port in open_ports:
            service = get_service_name(port)
            print(f"  {port:<8} {service}")
    else:
        print(f"\n❌ 未发现开放端口")
    
    print(f"\n扫描完成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return open_ports


def get_service_name(port):
    """获取端口号对应的服务名称"""
    common_ports = {
        20: 'FTP-DATA',
        21: 'FTP',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        993: 'IMAPS',
        995: 'POP3S',
        3306: 'MySQL',
        3389: 'RDP',
        5432: 'PostgreSQL',
        6379: 'Redis',
        8080: 'HTTP-Proxy',
        8443: 'HTTPS-Alt',
        27017: 'MongoDB',
    }
    return common_ports.get(port, 'Unknown')


def list_listening_ports():
    """列出所有监听端口"""
    print(f"\n🎧 系统监听端口")
    print("=" * 70)
    print(f"{'协议':<6} {'本地地址':<25} {'状态':<15} {'进程'}")
    print("=" * 70)
    
    connections = psutil.net_connections(kind='inet')
    listening = [c for c in connections if c.status == 'LISTEN']
    
    # 按端口号排序
    listening.sort(key=lambda x: x.laddr.port if x.laddr else 0)
    
    for conn in listening:
        proto = 'TCP' if conn.type == socket.SOCK_STREAM else 'UDP'
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else 'N/A'
        status = conn.status
        
        # 获取进程名
        try:
            proc = psutil.Process(conn.pid)
            proc_name = proc.name()
        except:
            proc_name = 'N/A'
        
        print(f"{proto:<6} {laddr:<25} {status:<15} {proc_name}")
    
    print(f"\n共 {len(listening)} 个监听端口")


def check_port_occupancy(port):
    """检查端口占用情况"""
    print(f"\n🔍 检查端口 {port} 占用情况")
    print("=" * 60)
    
    # 检查端口是否被占用
    is_listening = False
    occupied_by = None
    
    for conn in psutil.net_connections(kind='inet'):
        if conn.laddr and conn.laddr.port == port:
            is_listening = True
            try:
                proc = psutil.Process(conn.pid)
                occupied_by = {
                    'pid': conn.pid,
                    'name': proc.name(),
                    'user': proc.username(),
                    'cmdline': ' '.join(proc.cmdline()[:5])
                }
            except:
                pass
            break
    
    if is_listening:
        print(f"✅ 端口 {port} 已被占用")
        if occupied_by:
            print(f"\n占用进程:")
            print(f"  PID: {occupied_by['pid']}")
            print(f"  名称: {occupied_by['name']}")
            print(f"  用户: {occupied_by['user']}")
            print(f"  命令: {occupied_by['cmdline']}")
    else:
        print(f"❌ 端口 {port} 未被占用（可用）")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="端口扫描工具")
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # scan 命令
    scan_parser = subparsers.add_parser('scan', help='扫描端口范围')
    scan_parser.add_argument('host', nargs='?', default='localhost', help='目标主机')
    scan_parser.add_argument('-p', '--ports', default='1-1024', help='端口范围 (如: 1-1024 或 80,443,8080)')
    
    # listen 命令
    listen_parser = subparsers.add_parser('listen', help='列出所有监听端口')
    
    # check 命令
    check_parser = subparsers.add_parser('check', help='检查端口占用')
    check_parser.add_argument('port', type=int, help='端口号')
    
    args = parser.parse_args()
    
    if args.command == 'scan':
        # 解析端口范围
        if '-' in args.ports:
            start, end = map(int, args.ports.split('-'))
            scan_ports(args.host, start, end)
        else:
            ports = [int(p) for p in args.ports.split(',')]
            for port in ports:
                if check_port(port, args.host):
                    print(f"✅ {args.host}:{port} - 开放 ({get_service_name(port)})")
                else:
                    print(f"❌ {args.host}:{port} - 关闭")
    
    elif args.command == 'listen':
        list_listening_ports()
    
    elif args.command == 'check':
        check_port_occupancy(args.port)
    
    else:
        # 默认显示监听端口
        list_listening_ports()
