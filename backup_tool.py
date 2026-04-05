#!/usr/bin/env python3
"""
备份工具 - 文件和目录备份
"""
import os
import shutil
import tarfile
import hashlib
from datetime import datetime
from pathlib import Path
import argparse
import json


BACKUP_DIR = Path.home() / '.backups'
BACKUP_INDEX = BACKUP_DIR / 'backup_index.json'


def ensure_backup_dir():
    """确保备份目录存在"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not BACKUP_INDEX.exists():
        with open(BACKUP_INDEX, 'w') as f:
            json.dump({'backups': []}, f)


def get_file_hash(file_path):
    """计算文件哈希值"""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except:
        return None


def create_backup(source, name=None, compress=True):
    """创建备份"""
    source = Path(source)
    
    if not source.exists():
        print(f"❌ 源路径不存在: {source}")
        return None
    
    ensure_backup_dir()
    
    # 生成备份名称
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if name:
        backup_name = f"{name}_{timestamp}"
    else:
        backup_name = f"{source.name}_{timestamp}"
    
    backup_file = BACKUP_DIR / f"{backup_name}.tar.gz" if compress else BACKUP_DIR / backup_name
    
    print(f"📦 创建备份...")
    print(f"  源路径: {source}")
    print(f"  备份位置: {backup_file}")
    
    try:
        if compress:
            with tarfile.open(backup_file, 'w:gz') as tar:
                tar.add(source, arcname=source.name)
        else:
            if source.is_file():
                shutil.copy2(source, backup_file)
            else:
                shutil.copytree(source, backup_file)
        
        # 计算备份大小
        backup_size = backup_file.stat().st_size / (1024**2)
        
        # 记录备份信息
        record = {
            'name': backup_name,
            'source': str(source.absolute()),
            'backup_file': str(backup_file),
            'size_mb': round(backup_size, 2),
            'created': timestamp,
            'compressed': compress
        }
        
        # 更新索引
        with open(BACKUP_INDEX, 'r') as f:
            index = json.load(f)
        index['backups'].append(record)
        with open(BACKUP_INDEX, 'w') as f:
            json.dump(index, f, indent=2)
        
        print(f"\n✅ 备份完成!")
        print(f"  备份大小: {backup_size:.2f} MB")
        
        return backup_file
        
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return None


def list_backups():
    """列出所有备份"""
    ensure_backup_dir()
    
    with open(BACKUP_INDEX, 'r') as f:
        index = json.load(f)
    
    backups = index.get('backups', [])
    
    if not backups:
        print("📭 暂无备份记录")
        return []
    
    print(f"\n📋 备份列表 ({len(backups)} 个)")
    print("=" * 80)
    print(f"{'编号':<6} {'名称':<30} {'大小':<12} {'创建时间'}")
    print("=" * 80)
    
    for i, backup in enumerate(backups, 1):
        name = backup['name'][:28]
        size = f"{backup['size_mb']} MB"
        created = backup['created']
        print(f"{i:<6} {name:<30} {size:<12} {created}")
    
    return backups


def restore_backup(backup_id, target_dir=None):
    """恢复备份"""
    ensure_backup_dir()
    
    with open(BACKUP_INDEX, 'r') as f:
        index = json.load(f)
    
    backups = index.get('backups', [])
    
    if backup_id < 1 or backup_id > len(backups):
        print(f"❌ 无效的备份编号: {backup_id}")
        return False
    
    backup = backups[backup_id - 1]
    backup_file = Path(backup['backup_file'])
    
    if not backup_file.exists():
        print(f"❌ 备份文件不存在: {backup_file}")
        return False
    
    if target_dir:
        target = Path(target_dir)
    else:
        target = Path(backup['source']).parent
    
    print(f"📦 恢复备份...")
    print(f"  备份文件: {backup_file}")
    print(f"  恢复位置: {target}")
    
    try:
        if backup['compressed']:
            with tarfile.open(backup_file, 'r:gz') as tar:
                tar.extractall(target)
        else:
            if backup_file.is_file():
                shutil.copy2(backup_file, target / backup_file.name)
            else:
                shutil.copytree(backup_file, target / backup['name'])
        
        print(f"\n✅ 恢复完成!")
        return True
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        return False


def delete_backup(backup_id):
    """删除备份"""
    ensure_backup_dir()
    
    with open(BACKUP_INDEX, 'r') as f:
        index = json.load(f)
    
    backups = index.get('backups', [])
    
    if backup_id < 1 or backup_id > len(backups):
        print(f"❌ 无效的备份编号: {backup_id}")
        return False
    
    backup = backups[backup_id - 1]
    backup_file = Path(backup['backup_file'])
    
    print(f"🗑️  删除备份: {backup['name']}")
    
    try:
        if backup_file.exists():
            if backup_file.is_file():
                backup_file.unlink()
            else:
                shutil.rmtree(backup_file)
        
        # 更新索引
        backups.pop(backup_id - 1)
        index['backups'] = backups
        with open(BACKUP_INDEX, 'w') as f:
            json.dump(index, f, indent=2)
        
        print("✅ 备份已删除")
        return True
        
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        return False


def cleanup_old_backups(keep_days=30):
    """清理旧备份"""
    ensure_backup_dir()
    
    with open(BACKUP_INDEX, 'r') as f:
        index = json.load(f)
    
    backups = index.get('backups', [])
    cutoff = datetime.now().timestamp() - (keep_days * 86400)
    
    deleted_count = 0
    remaining = []
    
    for backup in backups:
        created = datetime.strptime(backup['created'], '%Y%m%d_%H%M%S').timestamp()
        
        if created < cutoff:
            backup_file = Path(backup['backup_file'])
            try:
                if backup_file.exists():
                    if backup_file.is_file():
                        backup_file.unlink()
                    else:
                        shutil.rmtree(backup_file)
                deleted_count += 1
                print(f"🗑️  已删除: {backup['name']}")
            except Exception as e:
                print(f"⚠️  删除失败 {backup['name']}: {e}")
                remaining.append(backup)
        else:
            remaining.append(backup)
    
    # 更新索引
    index['backups'] = remaining
    with open(BACKUP_INDEX, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"\n✅ 清理完成，删除了 {deleted_count} 个旧备份")
    return deleted_count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="备份工具")
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # create 命令
    create_parser = subparsers.add_parser('create', help='创建备份')
    create_parser.add_argument('source', help='要备份的文件或目录')
    create_parser.add_argument('-n', '--name', help='备份名称')
    create_parser.add_argument('--no-compress', action='store_true', help='不压缩')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出备份')
    
    # restore 命令
    restore_parser = subparsers.add_parser('restore', help='恢复备份')
    restore_parser.add_argument('backup_id', type=int, help='备份编号')
    restore_parser.add_argument('-d', '--dir', help='恢复目录')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除备份')
    delete_parser.add_argument('backup_id', type=int, help='备份编号')
    
    # cleanup 命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧备份')
    cleanup_parser.add_argument('-d', '--days', type=int, default=30, help='保留天数')
    
    args = parser.parse_args()
    
    if args.command == 'create':
        create_backup(args.source, args.name, not args.no_compress)
    elif args.command == 'list':
        list_backups()
    elif args.command == 'restore':
        restore_backup(args.backup_id, args.dir)
    elif args.command == 'delete':
        delete_backup(args.backup_id)
    elif args.command == 'cleanup':
        cleanup_old_backups(args.days)
    else:
        list_backups()
