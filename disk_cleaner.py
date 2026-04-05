#!/usr/bin/env python3
"""
磁盘清理工具 - 清理系统垃圾文件
"""
import os
import shutil
from pathlib import Path
import argparse
from datetime import datetime, timedelta


def get_dir_size(path):
    """计算目录大小"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat(follow_symlinks=False).st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_dir_size(entry.path)
    except (PermissionError, OSError):
        pass
    return total


def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def scan_cache_dirs():
    """扫描常见缓存目录"""
    home = Path.home()
    
    cache_dirs = [
        ('用户缓存', home / '.cache'),
        ('pip缓存', home / '.cache/pip'),
        ('npm缓存', home / '.npm'),
        ('yarn缓存', home / '.cache/yarn'),
        ('gradle缓存', home / '.gradle/caches'),
        ('maven缓存', home / '.m2/repository'),
        ('go模块缓存', home / 'go/pkg/mod'),
        ('cargo缓存', home / '.cargo/registry'),
        ('thumbnails缓存', home / '.cache/thumbnails'),
        ('trash', home / '.local/share/Trash'),
    ]
    
    print("\n📦 缓存目录扫描")
    print("=" * 70)
    print(f"{'目录':<30} {'路径':<25} {'大小'}")
    print("=" * 70)
    
    total_size = 0
    found = []
    
    for name, path in cache_dirs:
        if path.exists():
            size = get_dir_size(path)
            total_size += size
            found.append({
                'name': name,
                'path': path,
                'size': size
            })
            print(f"{name:<30} {str(path)[:25]:<25} {format_size(size)}")
    
    print("-" * 70)
    print(f"总计: {format_size(total_size)}")
    
    return found


def scan_old_files(directory, days=30, extensions=None):
    """扫描旧文件"""
    directory = Path(directory)
    cutoff = datetime.now() - timedelta(days=days)
    
    print(f"\n🗓️  扫描 {days} 天前的文件")
    print("=" * 70)
    
    old_files = []
    total_size = 0
    
    try:
        for path in directory.rglob('*'):
            if path.is_file():
                try:
                    mtime = datetime.fromtimestamp(path.stat().st_mtime)
                    if mtime < cutoff:
                        if extensions is None or path.suffix.lower() in extensions:
                            size = path.stat().st_size
                            total_size += size
                            old_files.append({
                                'path': path,
                                'mtime': mtime,
                                'size': size
                            })
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError):
        print(f"❌ 无法访问目录: {directory}")
        return []
    
    # 按修改时间排序
    old_files.sort(key=lambda x: x['mtime'])
    
    # 显示前20个
    for f in old_files[:20]:
        print(f"{f['mtime'].strftime('%Y-%m-%d')} {format_size(f['size']):<12} {f['path']}")
    
    if len(old_files) > 20:
        print(f"... 还有 {len(old_files) - 20} 个文件")
    
    print(f"\n共 {len(old_files)} 个文件, 总计 {format_size(total_size)}")
    
    return old_files


def scan_large_files(directory, min_size_mb=100, limit=20):
    """扫描大文件"""
    directory = Path(directory)
    min_size = min_size_mb * 1024 * 1024
    
    print(f"\n🐘 扫描大于 {min_size_mb}MB 的文件")
    print("=" * 70)
    
    large_files = []
    
    try:
        for path in directory.rglob('*'):
            if path.is_file():
                try:
                    size = path.stat().st_size
                    if size >= min_size:
                        large_files.append({
                            'path': path,
                            'size': size
                        })
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError):
        print(f"❌ 无法访问目录: {directory}")
        return []
    
    # 按大小排序
    large_files.sort(key=lambda x: x['size'], reverse=True)
    
    for f in large_files[:limit]:
        print(f"{format_size(f['size']):<12} {f['path']}")
    
    if len(large_files) > limit:
        print(f"... 还有 {len(large_files) - limit} 个文件")
    
    print(f"\n共 {len(large_files)} 个大文件")
    
    return large_files


def clean_cache(confirm=True):
    """清理缓存"""
    cache_dirs = scan_cache_dirs()
    
    if not cache_dirs:
        print("\n没有可清理的缓存目录")
        return
    
    if confirm:
        answer = input("\n是否清理以上缓存? [y/N] ")
        if answer.lower() != 'y':
            print("已取消")
            return
    
    print("\n🗑️  开始清理...")
    
    for item in cache_dirs:
        try:
            if item['path'].is_dir():
                shutil.rmtree(item['path'])
            else:
                item['path'].unlink()
            print(f"✅ 已清理: {item['name']}")
        except Exception as e:
            print(f"❌ 清理失败 {item['name']}: {e}")


def clean_empty_dirs(directory):
    """清理空目录"""
    directory = Path(directory)
    empty_dirs = []
    
    print(f"\n📂 扫描空目录: {directory}")
    print("=" * 70)
    
    for path in directory.rglob('*'):
        if path.is_dir():
            try:
                if not any(path.iterdir()):
                    empty_dirs.append(path)
            except (PermissionError, OSError):
                continue
    
    if empty_dirs:
        for d in empty_dirs[:20]:
            print(f"  {d}")
        
        if len(empty_dirs) > 20:
            print(f"  ... 还有 {len(empty_dirs) - 20} 个")
        
        print(f"\n共 {len(empty_dirs)} 个空目录")
        
        answer = input("\n是否删除这些空目录? [y/N] ")
        if answer.lower() == 'y':
            for d in empty_dirs:
                try:
                    d.rmdir()
                except:
                    pass
            print("✅ 清理完成")
    else:
        print("没有找到空目录")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="磁盘清理工具")
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # cache 命令
    cache_parser = subparsers.add_parser('cache', help='扫描/清理缓存目录')
    cache_parser.add_argument('-c', '--clean', action='store_true', help='清理缓存')
    cache_parser.add_argument('-y', '--yes', action='store_true', help='跳过确认')
    
    # old-files 命令
    old_parser = subparsers.add_parser('old-files', help='扫描旧文件')
    old_parser.add_argument('directory', help='扫描目录')
    old_parser.add_argument('-d', '--days', type=int, default=30, help='天数阈值')
    old_parser.add_argument('-e', '--ext', help='文件扩展名 (如 .log,.tmp)')
    
    # large-files 命令
    large_parser = subparsers.add_parser('large-files', help='扫描大文件')
    large_parser.add_argument('directory', help='扫描目录')
    large_parser.add_argument('-s', '--size', type=int, default=100, help='最小大小(MB)')
    large_parser.add_argument('-n', '--limit', type=int, default=20, help='显示数量')
    
    # empty-dirs 命令
    empty_parser = subparsers.add_parser('empty-dirs', help='扫描空目录')
    empty_parser.add_argument('directory', help='扫描目录')
    
    args = parser.parse_args()
    
    if args.command == 'cache':
        if args.clean:
            clean_cache(not args.yes)
        else:
            scan_cache_dirs()
    elif args.command == 'old-files':
        extensions = args.ext.split(',') if args.ext else None
        scan_old_files(args.directory, args.days, extensions)
    elif args.command == 'large-files':
        scan_large_files(args.directory, args.size, args.limit)
    elif args.command == 'empty-dirs':
        clean_empty_dirs(args.directory)
    else:
        # 默认扫描缓存
        scan_cache_dirs()
