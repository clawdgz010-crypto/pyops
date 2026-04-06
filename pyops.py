#!/usr/bin/env python3
"""
pyops - Python 运维工具箱统一入口

Usage:
    pyops <tool> [options]
    
Examples:
    pyops monitor              # 系统监控
    pyops monitor --loop       # 持续监控
    pyops log /var/log/syslog  # 日志分析
    pyops proc list            # 进程列表
    pyops port listen          # 端口监听
    pyops --help               # 帮助信息
"""
import sys
import subprocess
import os
from typing import List, Dict, Optional

# 工具映射
TOOLS: Dict[str, str] = {
    "monitor": "sys_monitor.py",
    "log": "log_analyzer.py",
    "watch": "file_watcher.py",
    "proc": "process_manager.py",
    "port": "port_scanner.py",
    "backup": "backup_tool.py",
    "ssh": "ssh_manager.py",
    "config": "config_parser.py",
    "clean": "disk_cleaner.py",
    "net": "network_diag.py",
    "cron": "cron_manager.py",
}

# 工具描述
TOOL_DESC: Dict[str, str] = {
    "monitor": "系统监控 - CPU、内存、磁盘、网络",
    "log": "日志分析 - 统计ERROR/WARNING等",
    "watch": "文件监控 - 实时检测文件变更",
    "proc": "进程管理 - 列表、搜索、终止进程",
    "port": "端口扫描 - 检查端口占用",
    "backup": "备份工具 - 文件备份与恢复",
    "ssh": "SSH管理 - 密钥和主机配置",
    "config": "配置解析 - JSON/YAML/INI/ENV",
    "clean": "磁盘清理 - 缓存、旧文件、大文件",
    "net": "网络诊断 - Ping/DNS/HTTP检查",
    "cron": "定时任务 - crontab管理",
}


def get_script_dir() -> str:
    """获取脚本所在目录"""
    return os.path.dirname(os.path.abspath(__file__))


def print_help() -> None:
    """打印帮助信息"""
    print("pyops - Python 运维工具箱\n")
    print("用法: pyops <tool> [options]\n")
    print("可用工具:")
    for name in sorted(TOOLS.keys()):
        print(f"  {name:<10} {TOOL_DESC[name]}")
    print("\n示例:")
    print("  pyops monitor              # 查看系统信息")
    print("  pyops monitor --loop       # 持续监控")
    print("  pyops log /var/log/syslog  # 分析日志")
    print("  pyops proc list            # 进程列表")
    print("  pyops port listen          # 监听端口")
    print("\n查看各工具详细帮助: pyops <tool> --help")


def main(args: Optional[List[str]] = None) -> int:
    """主入口"""
    if args is None:
        args = sys.argv[1:]
    
    if not args or args[0] in ["-h", "--help", "help"]:
        print_help()
        return 0
    
    tool = args[0]
    
    if tool not in TOOLS:
        print(f"错误: 未知工具 '{tool}'")
        print(f"可用工具: {', '.join(sorted(TOOLS.keys()))}")
        return 1
    
    script_path = os.path.join(get_script_dir(), TOOLS[tool])
    
    if not os.path.exists(script_path):
        print(f"错误: 工具脚本不存在: {script_path}")
        return 1
    
    # 执行对应的工具脚本
    cmd = [sys.executable, script_path] + args[1:]
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
