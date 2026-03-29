#!/usr/bin/env python3
"""
调试聊天记录格式
"""

import re

def analyze_line(line, line_num):
    """分析单行格式"""
    line = line.strip()
    if not line:
        return
    
    print(f"\n第 {line_num} 行分析:")
    print(f"原始内容: {line[:100]}...")
    
    # 尝试多种格式
    patterns = [
        # 格式1: Sender (YYYY-MM-DD HH:MM:SS AM/PM): Content
        r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [AP]M)\): (.+)$',
        
        # 格式2: [时间] 发送者: 内容
        r'^\[(.+?)\] (.+?): (.+)$',
        
        # 格式3: 发送者 时间: 内容
        r'^(.+?) (\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2}): (.+)$',
        
        # 格式4: 发送者 - 时间: 内容
        r'^(.+?) - (\d{4}[-/]\d{2}[-/]\d{2} \d{2}:\d{2}:\d{2}): (.+)$',
    ]
    
    for i, pattern in enumerate(patterns, 1):
        match = re.match(pattern, line)
        if match:
            print(f"✓ 匹配格式{i}: {pattern}")
            print(f"  组数: {len(match.groups())}")
            for j, group in enumerate(match.groups(), 1):
                print(f"  组{j}: {group[:50]}...")
            return True
    
    print("✗ 未匹配任何已知格式")
    
    # 尝试分割
    if ':' in line:
        parts = line.split(':', 2)
        print(f"用':'分割: {len(parts)} 部分")
        for j, part in enumerate(parts, 1):
            print(f"  部分{j}: {part[:50]}...")
    
    return False

def main():
    chat_file = '/root/.openclaw/mnt/sdb1/聊天记录-1.txt'
    
    print("=== 聊天记录格式分析 ===")
    print(f"文件: {chat_file}")
    print("=" * 80)
    
    with open(chat_file, 'r', encoding='utf-8') as f:
        for i in range(1, 11):  # 分析前10行
            line = f.readline()
            if not line:
                break
            analyze_line(line, i)

if __name__ == '__main__':
    main()