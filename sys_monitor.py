#!/usr/bin/env python3
"""
系统监控工具 - 查看系统资源使用情况
"""
import psutil
import time
from datetime import datetime
from typing import Dict, Any, Optional


def get_cpu_info() -> Dict[str, Any]:
    """获取 CPU 信息"""
    return {
        "cores": psutil.cpu_count(),
        "percent": psutil.cpu_percent(interval=1),
        "per_cpu": psutil.cpu_percent(interval=1, percpu=True),
    }


def get_memory_info() -> Dict[str, Any]:
    """获取内存信息"""
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024**3), 2),
        "used_gb": round(mem.used / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
        "percent": mem.percent,
    }


def get_disk_info() -> list:
    """获取磁盘信息"""
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "mountpoint": partition.mountpoint,
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "percent": usage.percent,
            })
        except PermissionError:
            continue
    return disks


def get_network_info() -> Dict[str, float]:
    """获取网络信息"""
    net = psutil.net_io_counters()
    return {
        "sent_mb": round(net.bytes_sent / (1024**2), 2),
        "recv_mb": round(net.bytes_recv / (1024**2), 2),
    }


def get_system_info() -> Dict[str, Any]:
    """获取系统信息（返回字典格式）"""
    return {
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "network": get_network_info(),
    }


def print_system_info() -> None:
    """打印系统信息（友好格式）"""
    print("=" * 50)
    print(f"系统监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # CPU 信息
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    print(f"\n📊 CPU:")
    print(f"  核心数: {cpu_count}")
    print(f"  使用率: {cpu_percent}%")
    
    # 内存信息
    memory = psutil.virtual_memory()
    print(f"\n💾 内存:")
    print(f"  总计: {memory.total / (1024**3):.2f} GB")
    print(f"  已用: {memory.used / (1024**3):.2f} GB")
    print(f"  可用: {memory.available / (1024**3):.2f} GB")
    print(f"  使用率: {memory.percent}%")
    
    # 磁盘信息
    print(f"\n💿 磁盘:")
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            print(f"  {partition.mountpoint}:")
            print(f"    总计: {usage.total / (1024**3):.2f} GB")
            print(f"    已用: {usage.used / (1024**3):.2f} GB")
            print(f"    使用率: {usage.percent}%")
        except PermissionError:
            continue
    
    # 网络信息
    net_io = psutil.net_io_counters()
    print(f"\n🌐 网络:")
    print(f"  发送: {net_io.bytes_sent / (1024**2):.2f} MB")
    print(f"  接收: {net_io.bytes_recv / (1024**2):.2f} MB")
    
    print("=" * 50)


def monitor_loop(interval: int = 5) -> None:
    """持续监控"""
    try:
        while True:
            print_system_info()
            time.sleep(interval)
            print("\n" * 2)
    except KeyboardInterrupt:
        print("\n监控已停止")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="系统监控工具")
    parser.add_argument("-l", "--loop", action="store_true", help="持续监控")
    parser.add_argument("-i", "--interval", type=int, default=5, help="监控间隔(秒)")
    parser.add_argument("-j", "--json", action="store_true", help="JSON格式输出")
    
    args = parser.parse_args()
    
    if args.json:
        import json
        print(json.dumps(get_system_info(), indent=2, ensure_ascii=False))
    elif args.loop:
        monitor_loop(args.interval)
    else:
        print_system_info()
