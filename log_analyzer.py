#!/usr/bin/env python3
"""
日志分析工具 - 统计日志中的错误、警告等信息
"""
import re
from collections import Counter, defaultdict
from datetime import datetime
import argparse


def analyze_log_file(log_file, patterns=None):
    """分析日志文件"""
    if patterns is None:
        patterns = {
            'ERROR': r'\bERROR\b|\berror\b',
            'WARNING': r'\bWARNING\b|\bwarn\b',
            'INFO': r'\bINFO\b',
            'DEBUG': r'\bDEBUG\b',
        }
    
    results = defaultdict(list)
    line_count = 0
    
    try:
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line_count += 1
                for level, pattern in patterns.items():
                    if re.search(pattern, line):
                        results[level].append({
                            'line': line_num,
                            'content': line.strip()[:200]  # 限制长度
                        })
    except FileNotFoundError:
        print(f"❌ 文件不存在: {log_file}")
        return None
    
    # 输出结果
    print("=" * 60)
    print(f"日志分析报告 - {log_file}")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"\n📄 总行数: {line_count}")
    
    for level in ['ERROR', 'WARNING', 'INFO', 'DEBUG']:
        count = len(results[level])
        if count > 0:
            print(f"\n{get_level_emoji(level)} {level}: {count} 条")
            
            # 显示前5条
            for item in results[level][:5]:
                print(f"  行 {item['line']}: {item['content'][:100]}")
            
            if count > 5:
                print(f"  ... 还有 {count - 5} 条")
    
    # 统计关键词
    print(f"\n📈 统计摘要:")
    total_issues = len(results['ERROR']) + len(results['WARNING'])
    if total_issues > 0:
        print(f"  ⚠️  需要关注的问题: {total_issues} 条")
    
    return results


def get_level_emoji(level):
    """获取日志级别对应的 emoji"""
    emojis = {
        'ERROR': '❌',
        'WARNING': '⚠️',
        'INFO': 'ℹ️',
        'DEBUG': '🔍'
    }
    return emojis.get(level, '📝')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="日志分析工具")
    parser.add_argument("log_file", help="日志文件路径")
    parser.add_argument("-p", "--pattern", help="自定义搜索模式")
    
    args = parser.parse_args()
    
    patterns = None
    if args.pattern:
        patterns = {'CUSTOM': args.pattern}
    
    analyze_log_file(args.log_file, patterns)
