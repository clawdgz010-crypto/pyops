#!/usr/bin/env python3
"""
配置文件解析工具 - 解析和编辑常见配置文件格式
"""
import json
import yaml
import configparser
from pathlib import Path
import argparse


def parse_json(file_path):
    """解析 JSON 配置文件"""
    with open(file_path) as f:
        return json.load(f)


def parse_yaml(file_path):
    """解析 YAML 配置文件"""
    with open(file_path) as f:
        return yaml.safe_load(f)


def parse_ini(file_path):
    """解析 INI 配置文件"""
    config = configparser.ConfigParser()
    config.read(file_path)
    
    result = {}
    for section in config.sections():
        result[section] = dict(config.items(section))
    
    return result


def parse_env_file(file_path):
    """解析 .env 文件"""
    result = {}
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    result[key.strip()] = value.strip().strip('"\'')
    return result


def detect_format(file_path):
    """检测配置文件格式"""
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    format_map = {
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.ini': 'ini',
        '.conf': 'ini',
        '.env': 'env',
    }
    
    return format_map.get(suffix, 'text')


def display_config(data, indent=0):
    """美观显示配置"""
    prefix = '  ' * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{prefix}{key}:")
                display_config(value, indent + 1)
            else:
                print(f"{prefix}{key}: {value}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, (dict, list)):
                display_config(item, indent)
            else:
                print(f"{prefix}- {item}")
    else:
        print(f"{prefix}{data}")


def read_config(file_path):
    """读取配置文件"""
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return None
    
    format_type = detect_format(file_path)
    
    print(f"\n📄 配置文件: {file_path.name}")
    print(f"格式: {format_type.upper()}")
    print("=" * 70)
    
    try:
        if format_type == 'json':
            data = parse_json(file_path)
        elif format_type == 'yaml':
            data = parse_yaml(file_path)
        elif format_type == 'ini':
            data = parse_ini(file_path)
        elif format_type == 'env':
            data = parse_env_file(file_path)
        else:
            with open(file_path) as f:
                print(f.read())
            return None
        
        display_config(data)
        return data
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        return None


def get_value(data, keys):
    """获取嵌套键值"""
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return None
        
        if data is None:
            return None
    
    return data


def search_config(file_path, key_path):
    """搜索配置项"""
    data = read_config(file_path)
    
    if data is None:
        return None
    
    keys = key_path.split('.')
    value = get_value(data, keys)
    
    if value is not None:
        print(f"\n🔍 查找: {key_path}")
        print("=" * 70)
        print(f"值: {value}")
        return value
    else:
        print(f"❌ 未找到配置项: {key_path}")
        return None


def convert_config(input_path, output_format, output_path=None):
    """转换配置文件格式"""
    input_path = Path(input_path)
    
    # 读取源配置
    data = read_config(input_path)
    
    if data is None:
        return False
    
    # 确定输出路径
    if output_path is None:
        suffix_map = {
            'json': '.json',
            'yaml': '.yaml',
            'ini': '.ini',
        }
        output_path = input_path.with_suffix(suffix_map.get(output_format, '.txt'))
    else:
        output_path = Path(output_path)
    
    # 转换并写入
    try:
        with open(output_path, 'w') as f:
            if output_format == 'json':
                json.dump(data, f, indent=2)
            elif output_format == 'yaml':
                yaml.dump(data, f, default_flow_style=False)
            elif output_format == 'ini':
                config = configparser.ConfigParser()
                for section, values in data.items():
                    config.add_section(section)
                    for key, value in values.items():
                        config.set(section, key, str(value))
                config.write(f)
        
        print(f"\n✅ 转换成功: {input_path.name} -> {output_path.name}")
        return True
        
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="配置文件解析工具")
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # read 命令
    read_parser = subparsers.add_parser('read', help='读取配置文件')
    read_parser.add_argument('file', help='配置文件路径')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索配置项')
    search_parser.add_argument('file', help='配置文件路径')
    search_parser.add_argument('key', help='配置项路径 (如: database.host)')
    
    # convert 命令
    convert_parser = subparsers.add_parser('convert', help='转换配置格式')
    convert_parser.add_argument('input', help='输入文件')
    convert_parser.add_argument('-f', '--format', required=True, choices=['json', 'yaml', 'ini'], help='输出格式')
    convert_parser.add_argument('-o', '--output', help='输出文件')
    
    args = parser.parse_args()
    
    if args.command == 'read':
        read_config(args.file)
    elif args.command == 'search':
        search_config(args.file, args.key)
    elif args.command == 'convert':
        convert_config(args.input, args.format, args.output)
    else:
        parser.print_help()
