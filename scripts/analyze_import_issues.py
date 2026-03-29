#!/usr/bin/env python3
"""
分析导入失败的原因
"""

import re

def analyze_file_lines(file_path, sample_size=100):
    """分析文件中的行格式"""
    print(f"分析文件: {file_path}")
    print(f"采样大小: {sample_size} 行\n")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [next(f) for _ in range(sample_size)]
    
    # 标准格式：发送者 (YYYY-MM-DD HH:MM:SS AM/PM):内容
    standard_pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
    
    # 其他可能格式
    other_patterns = [
        r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (.+?):(.+)$',  # 时间在前
        r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (.+?):(.+)$',  # 方括号格式
        r'^(.+?) (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}):(.+)$',  # 发送者在前，24小时制
    ]
    
    stats = {
        'standard_format': 0,
        'other_formats': [],
        'empty_lines': 0,
        'unparsable': 0,
        'total_lines': len(lines)
    }
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        
        if not line:
            stats['empty_lines'] += 1
            continue
        
        # 检查标准格式
        match = re.match(standard_pattern, line)
        if match:
            stats['standard_format'] += 1
            continue
        
        # 检查其他格式
        parsed = False
        for pattern_idx, pattern in enumerate(other_patterns):
            match = re.match(pattern, line)
            if match:
                if pattern_idx >= len(stats['other_formats']):
                    stats['other_formats'].extend([0] * (pattern_idx - len(stats['other_formats']) + 1))
                stats['other_formats'][pattern_idx] += 1
                parsed = True
                break
        
        if not parsed:
            stats['unparsable'] += 1
            if stats['unparsable'] <= 5:  # 只显示前5个无法解析的行
                print(f"无法解析的行 {i}: {line[:100]}...")
    
    print("=== 格式分析结果 ===")
    print(f"总采样行数: {stats['total_lines']}")
    print(f"标准格式: {stats['standard_format']} ({stats['standard_format']/stats['total_lines']*100:.1f}%)")
    
    for i, count in enumerate(stats['other_formats']):
        if count > 0:
            print(f"其他格式{i+1}: {count} ({count/stats['total_lines']*100:.1f}%)")
    
    print(f"空行: {stats['empty_lines']} ({stats['empty_lines']/stats['total_lines']*100:.1f}%)")
    print(f"无法解析: {stats['unparsable']} ({stats['unparsable']/stats['total_lines']*100:.1f}%)")
    
    # 显示一些示例行
    print("\n=== 示例行 ===")
    for i, line in enumerate(lines[:10], 1):
        print(f"{i}. {line.strip()}")

def check_database_integrity(db_path):
    """检查数据库完整性"""
    import sqlite3
    
    print(f"\n=== 检查数据库完整性: {db_path} ===")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(chat_history)")
    columns = cursor.fetchall()
    print(f"表结构 ({len(columns)} 列):")
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # 检查是否有重复记录
    cursor.execute("""
        SELECT timestamp, sender, content, COUNT(*) as cnt 
        FROM chat_history 
        GROUP BY timestamp, sender, content 
        HAVING cnt > 1 
        LIMIT 5
    """)
    duplicates = cursor.fetchall()
    if duplicates:
        print(f"\n发现 {len(duplicates)} 组重复记录:")
        for dup in duplicates:
            print(f"  {dup[0]} {dup[1]}: {dup[2][:50]}... (重复 {dup[3]} 次)")
    else:
        print("\n未发现重复记录")
    
    # 检查时间顺序
    cursor.execute("""
        SELECT timestamp, sender, content 
        FROM chat_history 
        WHERE timestamp NOT LIKE '%AM%' AND timestamp NOT LIKE '%PM%'
        LIMIT 5
    """)
    non_standard_times = cursor.fetchall()
    if non_standard_times:
        print(f"\n发现 {len(non_standard_times)} 条非标准时间格式:")
        for row in non_standard_times:
            print(f"  {row[0]} {row[1]}: {row[2][:50]}...")
    
    conn.close()

def find_missing_records(file_path, db_path, limit=1000):
    """查找可能缺失的记录"""
    import sqlite3
    
    print(f"\n=== 查找可能缺失的记录 ===")
    print(f"比较文件: {file_path}")
    print(f"数据库: {db_path}")
    
    # 从文件中读取一些记录
    with open(file_path, 'r', encoding='utf-8') as f:
        file_lines = []
        for i, line in enumerate(f):
            if i >= limit:
                break
            file_lines.append(line.strip())
    
    # 从数据库查询
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, sender, content FROM chat_history LIMIT ?", (limit,))
    db_records = cursor.fetchall()
    conn.close()
    
    # 将数据库记录转换为字符串以便比较
    db_strings = []
    for timestamp, sender, content in db_records:
        # 尝试匹配不同的时间格式
        db_strings.append(f"{sender} ({timestamp}):{content}")
    
    print(f"\n文件中的前{len(file_lines)}行 vs 数据库中的前{len(db_records)}条记录")
    
    # 查找在文件中但不在数据库中的记录
    missing = []
    for line in file_lines[:50]:  # 只检查前50行
        found = False
        for db_str in db_strings:
            if line in db_str or db_str in line:
                found = True
                break
        
        if not found and line.strip():
            missing.append(line)
    
    if missing:
        print(f"\n发现 {len(missing)} 条可能缺失的记录:")
        for i, line in enumerate(missing[:10], 1):
            print(f"{i}. {line}")
    else:
        print("\n前50行记录都在数据库中")

if __name__ == "__main__":
    file_path = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    
    analyze_file_lines(file_path, sample_size=200)
    check_database_integrity(db_path)
    find_missing_records(file_path, db_path, limit=1000)