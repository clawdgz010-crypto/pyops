#!/usr/bin/env python3
"""
进程管理工具 - 查看和管理系统进程
"""
import psutil
import argparse
from datetime import datetime
import signal


def list_processes(sort_by='cpu', limit=10):
    """列出进程"""
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'username', 'status']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    # 排序
    if sort_by == 'cpu':
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    elif sort_by == 'memory':
        processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
    elif sort_by == 'pid':
        processes.sort(key=lambda x: x['pid'])
    
    # 显示结果
    print(f"\n{'PID':<8} {'CPU%':<8} {'MEM%':<8} {'状态':<10} {'用户':<15} {'名称'}")
    print("=" * 80)
    
    for proc in processes[:limit]:
        pid = proc['pid']
        cpu = proc['cpu_percent'] or 0
        mem = proc['memory_percent'] or 0
        status = proc['status'] or 'N/A'
        user = (proc['username'] or 'N/A')[:12]
        name = proc['name'] or 'N/A'
        
        print(f"{pid:<8} {cpu:<8.1f} {mem:<8.1f} {status:<10} {user:<15} {name}")
    
    print(f"\n共 {len(processes)} 个进程，显示前 {min(limit, len(processes))} 个")


def find_process(keyword):
    """搜索进程"""
    print(f"\n🔍 搜索进程: '{keyword}'")
    print("=" * 80)
    
    found = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'] or ''
            cmdline = ' '.join(proc.info['cmdline'] or [])
            
            if keyword.lower() in name.lower() or keyword.lower() in cmdline.lower():
                found.append({
                    'pid': proc.info['pid'],
                    'name': name,
                    'cmdline': cmdline[:60]
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if found:
        for proc in found:
            print(f"PID: {proc['pid']:<8} 名称: {proc['name']}")
            print(f"  命令: {proc['cmdline']}")
    else:
        print(f"❌ 未找到匹配 '{keyword}' 的进程")
    
    return found


def kill_process(pid, force=False):
    """终止进程"""
    try:
        proc = psutil.Process(pid)
        
        print(f"\n🎯 终止进程:")
        print(f"  PID: {pid}")
        print(f"  名称: {proc.name()}")
        print(f"  状态: {proc.status()}")
        
        if force:
            proc.kill()
            print("  ✅ 已强制终止 (SIGKILL)")
        else:
            proc.terminate()
            print("  ✅ 已发送终止信号 (SIGTERM)")
        
        return True
        
    except psutil.NoSuchProcess:
        print(f"❌ 进程 {pid} 不存在")
        return False
    except psutil.AccessDenied:
        print(f"❌ 权限不足，无法终止进程 {pid}")
        return False


def get_process_info(pid):
    """获取进程详细信息"""
    try:
        proc = psutil.Process(pid)
        
        print(f"\n📋 进程详细信息 (PID: {pid})")
        print("=" * 60)
        print(f"名称: {proc.name()}")
        print(f"状态: {proc.status()}")
        print(f"用户: {proc.username()}")
        print(f"CPU 使用率: {proc.cpu_percent(interval=1)}%")
        print(f"内存使用率: {proc.memory_percent():.2f}%")
        print(f"内存占用: {proc.memory_info().rss / (1024**2):.2f} MB")
        print(f"创建时间: {datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 父进程
        try:
            parent = proc.parent()
            if parent:
                print(f"父进程: {parent.pid} ({parent.name()})")
        except:
            pass
        
        # 命令行
        cmdline = proc.cmdline()
        if cmdline:
            print(f"命令行: {' '.join(cmdline)}")
        
        # 打开的文件
        try:
            files = proc.open_files()[:5]
            if files:
                print(f"\n打开的文件 (前5个):")
                for f in files:
                    print(f"  - {f.path}")
        except:
            pass
        
        # 网络连接
        try:
            connections = proc.connections()[:5]
            if connections:
                print(f"\n网络连接 (前5个):")
                for conn in connections:
                    status = conn.status
                    laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                    raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                    print(f"  - {laddr} -> {raddr} ({status})")
        except:
            pass
        
    except psutil.NoSuchProcess:
        print(f"❌ 进程 {pid} 不存在")
    except psutil.AccessDenied:
        print(f"❌ 权限不足，无法获取进程 {pid} 的信息")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="进程管理工具")
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出进程')
    list_parser.add_argument('-s', '--sort', choices=['cpu', 'memory', 'pid'], default='cpu', help='排序方式')
    list_parser.add_argument('-n', '--limit', type=int, default=15, help='显示数量')
    
    # find 命令
    find_parser = subparsers.add_parser('find', help='搜索进程')
    find_parser.add_argument('keyword', help='搜索关键词')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='查看进程详情')
    info_parser.add_argument('pid', type=int, help='进程ID')
    
    # kill 命令
    kill_parser = subparsers.add_parser('kill', help='终止进程')
    kill_parser.add_argument('pid', type=int, help='进程ID')
    kill_parser.add_argument('-f', '--force', action='store_true', help='强制终止')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_processes(args.sort, args.limit)
    elif args.command == 'find':
        find_process(args.keyword)
    elif args.command == 'info':
        get_process_info(args.pid)
    elif args.command == 'kill':
        kill_process(args.pid, args.force)
    else:
        # 默认显示进程列表
        list_processes()
