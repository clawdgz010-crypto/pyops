#!/usr/bin/env python3
"""
定时任务管理工具 - 管理 crontab 定时任务
"""
import subprocess
import re
from datetime import datetime
import argparse
import tempfile
import os


def list_cron_jobs(user=None):
    """列出定时任务"""
    print("\n📋 Crontab 定时任务")
    print("=" * 70)
    
    cmd = ['crontab', '-l']
    if user:
        cmd = ['crontab', '-u', user, '-l']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            if 'no crontab' in result.stderr.lower():
                print("📭 暂无定时任务")
                return []
            else:
                print(f"❌ 读取失败: {result.stderr}")
                return []
        
        lines = result.stdout.strip().split('\n')
        jobs = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if line and not line.startswith('#'):
                # 解析 cron 表达式
                parts = line.split()
                if len(parts) >= 6:
                    schedule = ' '.join(parts[:5])
                    command = ' '.join(parts[5:])
                    
                    jobs.append({
                        'line': i,
                        'schedule': schedule,
                        'command': command,
                        'raw': line
                    })
        
        if jobs:
            print(f"{'序号':<6} {'调度':<20} {'命令'}")
            print("-" * 70)
            
            for job in jobs:
                cmd_display = job['command'][:50] + '...' if len(job['command']) > 50 else job['command']
                print(f"{job['line']:<6} {job['schedule']:<20} {cmd_display}")
        else:
            print("📭 暂无定时任务")
        
        return jobs
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def parse_cron_schedule(schedule):
    """解析 cron 调度表达式"""
    parts = schedule.split()
    if len(parts) != 5:
        return None
    
    minute, hour, day, month, weekday = parts
    
    descriptions = []
    
    # 解析分钟
    if minute == '*':
        descriptions.append("每分钟")
    elif '/' in minute:
        interval = minute.split('/')[1]
        descriptions.append(f"每 {interval} 分钟")
    else:
        descriptions.append(f"第 {minute} 分钟")
    
    # 解析小时
    if hour != '*':
        if '/' in hour:
            interval = hour.split('/')[1]
            descriptions.append(f"每 {interval} 小时")
        else:
            descriptions.append(f" {hour} 点")
    
    # 解析日期
    if day != '*':
        descriptions.append(f"每月 {day} 号")
    
    # 解析月份
    if month != '*':
        descriptions.append(f" {month} 月")
    
    # 解析星期
    weekday_names = ['日', '一', '二', '三', '四', '五', '六']
    if weekday != '*':
        try:
            wd = int(weekday)
            descriptions.append(f"周{weekday_names[wd]}")
        except:
            pass
    
    return ' '.join(descriptions)


def add_cron_job(schedule, command, comment=None, user=None):
    """添加定时任务"""
    print(f"\n➕ 添加定时任务")
    print(f"  调度: {schedule}")
    print(f"  命令: {command}")
    
    # 验证调度表达式
    if len(schedule.split()) != 5:
        print("❌ 调度表达式格式错误，应为: 分 时 日 月 周")
        return False
    
    # 解析调度说明
    desc = parse_cron_schedule(schedule)
    if desc:
        print(f"  说明: {desc}")
    
    # 获取现有任务
    existing = ""
    cmd = ['crontab', '-l']
    if user:
        cmd = ['crontab', '-u', user, '-l']
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        existing = result.stdout
    
    # 构建新任务
    new_job = ""
    if comment:
        new_job += f"# {comment}\n"
    new_job += f"{schedule} {command}\n"
    
    # 写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.crontab') as f:
        f.write(existing)
        if not existing.endswith('\n') and existing:
            f.write('\n')
        f.write(new_job)
        temp_file = f.name
    
    # 安装新的 crontab
    cmd = ['crontab', temp_file]
    if user:
        cmd = ['crontab', '-u', user, temp_file]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        os.unlink(temp_file)
        
        if result.returncode == 0:
            print("✅ 添加成功")
            return True
        else:
            print(f"❌ 添加失败: {result.stderr}")
            return False
            
    except Exception as e:
        os.unlink(temp_file)
        print(f"❌ 错误: {e}")
        return False


def remove_cron_job(line_number, user=None):
    """删除定时任务"""
    print(f"\n🗑️  删除第 {line_number} 个定时任务")
    
    # 获取现有任务
    cmd = ['crontab', '-l']
    if user:
        cmd = ['crontab', '-u', user, '-l']
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ 读取 crontab 失败")
        return False
    
    lines = result.stdout.strip().split('\n')
    
    # 过滤掉要删除的任务行
    new_lines = []
    current_line = 0
    removed = False
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            current_line += 1
            if current_line == line_number:
                removed = True
                print(f"  删除: {line}")
                continue
        new_lines.append(line)
    
    if not removed:
        print(f"❌ 未找到第 {line_number} 个任务")
        return False
    
    # 写入临时文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.crontab') as f:
        f.write('\n'.join(new_lines) + '\n')
        temp_file = f.name
    
    # 安装新的 crontab
    cmd = ['crontab', temp_file]
    if user:
        cmd = ['crontab', '-u', user, temp_file]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        os.unlink(temp_file)
        
        if result.returncode == 0:
            print("✅ 删除成功")
            return True
        else:
            print(f"❌ 删除失败: {result.stderr}")
            return False
            
    except Exception as e:
        os.unlink(temp_file)
        print(f"❌ 错误: {e}")
        return False


def show_cron_templates():
    """显示常用 cron 模板"""
    print("\n📝 常用 Cron 调度模板")
    print("=" * 70)
    
    templates = [
        ("每分钟执行", "* * * * *"),
        ("每小时执行", "0 * * * *"),
        ("每天 0 点执行", "0 0 * * *"),
        ("每天 6 点执行", "0 6 * * *"),
        ("每天 8:30 执行", "30 8 * * *"),
        ("每小时 30 分执行", "30 * * * *"),
        ("每 5 分钟执行", "*/5 * * * *"),
        ("每 2 小时执行", "0 */2 * * *"),
        ("每周一 0 点执行", "0 0 * * 1"),
        ("每周日 0 点执行", "0 0 * * 0"),
        ("每月 1 号 0 点执行", "0 0 1 * *"),
        ("每月 15 号 0 点执行", "0 0 15 * *"),
        ("工作日 9 点执行", "0 9 * * 1-5"),
        ("周末 10 点执行", "0 10 * * 0,6"),
        ("每年 1 月 1 日执行", "0 0 1 1 *"),
    ]
    
    for desc, schedule in templates:
        print(f"  {desc:<20} {schedule}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="定时任务管理工具")
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出定时任务')
    list_parser.add_argument('-u', '--user', help='用户')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加定时任务')
    add_parser.add_argument('schedule', help='调度表达式 (分 时 日 月 周)')
    add_parser.add_argument('command', help='要执行的命令')
    add_parser.add_argument('-c', '--comment', help='注释')
    add_parser.add_argument('-u', '--user', help='用户')
    
    # remove 命令
    remove_parser = subparsers.add_parser('remove', help='删除定时任务')
    remove_parser.add_argument('line', type=int, help='任务序号')
    remove_parser.add_argument('-u', '--user', help='用户')
    
    # templates 命令
    templates_parser = subparsers.add_parser('templates', help='显示常用模板')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_cron_jobs(args.user)
    elif args.command == 'add':
        add_cron_job(args.schedule, args.command, args.comment, args.user)
    elif args.command == 'remove':
        remove_cron_job(args.line, args.user)
    elif args.command == 'templates':
        show_cron_templates()
    else:
        list_cron_jobs()
