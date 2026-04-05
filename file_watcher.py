#!/usr/bin/env python3
"""
文件监控工具 - 监控文件或目录的变更
"""
import os
import time
import hashlib
from datetime import datetime
from pathlib import Path
import argparse


class FileWatcher:
    """文件监控器"""
    
    def __init__(self, path, ignore_patterns=None):
        self.path = Path(path)
        self.ignore_patterns = ignore_patterns or ['.git', '__pycache__', '*.pyc', '.DS_Store']
        self.file_hashes = {}
        
    def should_ignore(self, path):
        """检查是否应该忽略该文件"""
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
        return False
    
    def get_file_hash(self, file_path):
        """计算文件 MD5 哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except (IOError, OSError):
            return None
    
    def scan_files(self):
        """扫描所有文件"""
        files = {}
        
        if self.path.is_file():
            if not self.should_ignore(self.path):
                file_hash = self.get_file_hash(self.path)
                if file_hash:
                    files[str(self.path)] = {
                        'hash': file_hash,
                        'size': self.path.stat().st_size,
                        'mtime': datetime.fromtimestamp(self.path.stat().st_mtime)
                    }
        else:
            for root, dirs, filenames in os.walk(self.path):
                # 过滤忽略的目录
                dirs[:] = [d for d in dirs if not self.should_ignore(d)]
                
                for filename in filenames:
                    if self.should_ignore(filename):
                        continue
                    
                    file_path = Path(root) / filename
                    file_hash = self.get_file_hash(file_path)
                    
                    if file_hash:
                        files[str(file_path)] = {
                            'hash': file_hash,
                            'size': file_path.stat().st_size,
                            'mtime': datetime.fromtimestamp(file_path.stat().st_mtime)
                        }
        
        return files
    
    def check_changes(self):
        """检查文件变更"""
        current_files = self.scan_files()
        changes = {
            'added': [],
            'modified': [],
            'deleted': []
        }
        
        # 检查新增和修改的文件
        for file_path, info in current_files.items():
            if file_path not in self.file_hashes:
                changes['added'].append(file_path)
            elif self.file_hashes[file_path]['hash'] != info['hash']:
                changes['modified'].append(file_path)
        
        # 检查删除的文件
        for file_path in self.file_hashes:
            if file_path not in current_files:
                changes['deleted'].append(file_path)
        
        # 更新文件哈希
        self.file_hashes = current_files
        
        return changes
    
    def watch(self, interval=2, callback=None):
        """持续监控"""
        print(f"🔍 开始监控: {self.path}")
        print(f"⏱️  检查间隔: {interval} 秒")
        print("按 Ctrl+C 停止监控\n")
        
        # 初始扫描
        self.file_hashes = self.scan_files()
        print(f"📁 初始文件数: {len(self.file_hashes)}")
        
        try:
            while True:
                time.sleep(interval)
                changes = self.check_changes()
                
                has_changes = any(changes.values())
                
                if has_changes:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"\n[{timestamp}] 检测到变更:")
                    
                    if changes['added']:
                        print(f"  ➕ 新增: {len(changes['added'])} 个文件")
                        for f in changes['added'][:5]:
                            print(f"     - {f}")
                    
                    if changes['modified']:
                        print(f"  ✏️  修改: {len(changes['modified'])} 个文件")
                        for f in changes['modified'][:5]:
                            print(f"     - {f}")
                    
                    if changes['deleted']:
                        print(f"  ➖ 删除: {len(changes['deleted'])} 个文件")
                        for f in changes['deleted'][:5]:
                            print(f"     - {f}")
                    
                    if callback:
                        callback(changes)
        
        except KeyboardInterrupt:
            print("\n\n监控已停止")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="文件监控工具")
    parser.add_argument("path", help="要监控的文件或目录路径")
    parser.add_argument("-i", "--interval", type=int, default=2, help="检查间隔(秒)")
    
    args = parser.parse_args()
    
    watcher = FileWatcher(args.path)
    watcher.watch(args.interval)
