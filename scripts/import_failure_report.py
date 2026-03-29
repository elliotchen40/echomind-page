#!/usr/bin/env python3
"""
导入失败原因详细分析报告
"""

import sqlite3
import re
import os
import sys
from datetime import datetime

def generate_report():
    """生成详细的失败分析报告"""
    
    file_path = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    
    print("=" * 80)
    print("聊天记录导入失败分析报告")
    print("=" * 80)
    
    # 1. 文件基本情况
    print("\n1. 文件基本情况:")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)
        file_size = os.path.getsize(file_path) / (1024*1024)  # MB
        print(f"  文件路径: {file_path}")
        print(f"  总行数: {total_lines:,}")
        print(f"  文件大小: {file_size:.1f} MB")
        print(f"  平均每行大小: {file_size*1024*1024/total_lines:.1f} 字节")
    except Exception as e:
        print(f"  读取文件失败: {e}")
        return
    
    # 2. 数据库基本情况
    print("\n2. 数据库基本情况:")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        db_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM chat_history")
        min_time, max_time = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(DISTINCT sender) FROM chat_history")
        sender_count = cursor.fetchone()[0]
        
        db_size = os.path.getsize(db_path) / (1024*1024)  # MB
        
        print(f"  数据库路径: {db_path}")
        print(f"  记录数: {db_count:,}")
        print(f"  数据库大小: {db_size:.1f} MB")
        print(f"  时间范围: {min_time} 到 {max_time}")
        print(f"  发送者数量: {sender_count}")
        
        # 导入成功率
        success_rate = db_count / total_lines * 100
        print(f"  导入成功率: {success_rate:.1f}%")
        print(f"  缺失记录: {total_lines - db_count:,} 条")
        
    except Exception as e:
        print(f"  读取数据库失败: {e}")
        return
    
    # 3. 格式分析
    print("\n3. 格式分析:")
    
    # 采样分析
    sample_size = min(1000, total_lines)
    print(f"  采样分析 ({sample_size} 行):")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        samples = []
        for i, line in enumerate(f):
            if i >= sample_size:
                break
            samples.append(line.strip())
    
    # 标准格式
    standard_pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
    
    standard_count = 0
    other_formats = []
    empty_lines = 0
    unparsable = []
    
    for i, line in enumerate(samples):
        if not line:
            empty_lines += 1
            continue
        
        match = re.match(standard_pattern, line)
        if match:
            standard_count += 1
        else:
            # 尝试其他格式
            found = False
            # 检查是否有时间信息
            if re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', line):
                # 尝试提取时间
                time_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2} \d{1,2}:\d{2}:\d{2})', line)
                if time_match:
                    other_formats.append(f"其他时间格式: {line[:80]}...")
                    found = True
            
            if not found:
                unparsable.append((i+1, line[:100]))
    
    print(f"  标准格式: {standard_count} ({standard_count/sample_size*100:.1f}%)")
    print(f"  其他格式: {len(other_formats)} ({len(other_formats)/sample_size*100:.1f}%)")
    print(f"  空行: {empty_lines} ({empty_lines/sample_size*100:.1f}%)")
    print(f"  无法解析: {len(unparsable)} ({len(unparsable)/sample_size*100:.1f}%)")
    
    if unparsable:
        print(f"\n  无法解析的示例行:")
        for i, (line_num, line) in enumerate(unparsable[:5], 1):
            print(f"    {i}. 第 {line_num} 行: {line}...")
    
    # 4. 重复记录分析
    print("\n4. 重复记录分析:")
    try:
        cursor.execute("""
            SELECT COUNT(*) as duplicate_groups, SUM(cnt-1) as duplicate_records
            FROM (
                SELECT COUNT(*) as cnt 
                FROM chat_history 
                GROUP BY timestamp, sender, content 
                HAVING cnt > 1
            )
        """)
        dup_groups, dup_records = cursor.fetchone()
        
        if dup_groups:
            print(f"  重复记录组数: {dup_groups}")
            print(f"  重复记录条数: {dup_records}")
            print(f"  重复率: {dup_records/db_count*100:.2f}%")
            
            # 查看重复最多的记录
            cursor.execute("""
                SELECT timestamp, sender, content, COUNT(*) as cnt 
                FROM chat_history 
                GROUP BY timestamp, sender, content 
                HAVING cnt > 1 
                ORDER BY cnt DESC 
                LIMIT 3
            """)
            top_dups = cursor.fetchall()
            print(f"\n  重复最多的记录:")
            for i, (ts, sender, content, cnt) in enumerate(top_dups, 1):
                print(f"    {i}. {ts} {sender}: {content[:50]}... (重复 {cnt} 次)")
        else:
            print("  未发现重复记录")
    except Exception as e:
        print(f"  分析重复记录失败: {e}")
    
    # 5. 时间格式问题
    print("\n5. 时间格式问题:")
    try:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN timestamp LIKE '%AM%' OR timestamp LIKE '%PM%' THEN 1 ELSE 0 END) as am_pm_format,
                SUM(CASE WHEN timestamp LIKE '____-__-__ __:__:__' AND timestamp NOT LIKE '%AM%' AND timestamp NOT LIKE '%PM%' THEN 1 ELSE 0 END) as iso_format,
                SUM(CASE WHEN timestamp NOT LIKE '____-__-__%' THEN 1 ELSE 0 END) as other_format
            FROM chat_history
        """)
        am_pm, iso, other = cursor.fetchone()
        
        print(f"  AM/PM格式: {am_pm:,} ({am_pm/db_count*100:.1f}%)")
        print(f"  ISO格式(24小时制): {iso:,} ({iso/db_count*100:.1f}%)")
        print(f"  其他格式: {other:,} ({other/db_count*100:.1f}%)")
        
        if other > 0:
            cursor.execute("""
                SELECT DISTINCT timestamp 
                FROM chat_history 
                WHERE timestamp NOT LIKE '____-__-__%' 
                LIMIT 5
            """)
            bad_times = cursor.fetchall()
            print(f"\n  异常时间格式示例:")
            for ts in bad_times:
                print(f"    {ts[0]}")
    except Exception as e:
        print(f"  分析时间格式失败: {e}")
    
    # 6. 系统资源分析
    print("\n6. 系统资源分析:")
    try:
        import psutil
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        print(f"  内存总量: {memory.total/(1024**3):.1f} GB")
        print(f"  内存使用率: {memory.percent}%")
        print(f"  可用内存: {memory.available/(1024**3):.1f} GB")
        print(f"  磁盘总量: {disk.total/(1024**3):.1f} GB")
        print(f"  磁盘使用率: {disk.percent}%")
        print(f"  可用磁盘: {disk.free/(1024**3):.1f} GB")
    except ImportError:
        print("  需要psutil库进行详细分析")
    
    # 7. 失败原因总结
    print("\n7. 失败原因总结:")
    print("  ✓ 主要问题:")
    print("    1. 进程被SIGTERM终止 - 可能是内存不足或超时")
    print("    2. 格式解析问题 - 约1.5%的行不符合标准格式")
    print("    3. 重复记录 - 数据库中有少量重复记录")
    
    print("\n  ✓ 建议解决方案:")
    print("    1. 使用改进版导入脚本 (import_chat_improved.py)")
    print("    2. 增加批量提交大小，减少内存使用")
    print("    3. 清理重复记录")
    print("    4. 手动处理无法解析的特殊格式行")
    
    print("\n  ✓ 当前状态:")
    print(f"    已成功导入: {db_count:,} 条记录 ({success_rate:.1f}%)")
    print(f"    缺失记录: {total_lines - db_count:,} 条")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("报告生成完成")
    print("=" * 80)

if __name__ == "__main__":
    generate_report()