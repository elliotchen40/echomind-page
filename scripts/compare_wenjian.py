#!/usr/bin/env python3
"""
对比源文件和数据库中的"文剑"记录
"""

import sqlite3
import re

def compare_wenjian():
    """对比文剑记录"""
    source_file = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    
    print("=" * 80)
    print("源文件 vs 数据库：文剑记录对比")
    print("=" * 80)
    
    # 1. 在源文件中查找"文剑"
    print("\n1. 在源文件中查找'文剑':")
    
    source_wenjian_lines = []
    line_numbers = []
    
    with open(source_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if '文剑' in line:
                source_wenjian_lines.append(line.strip())
                line_numbers.append(i)
    
    print(f"   找到 {len(source_wenjian_lines)} 行包含'文剑'")
    
    if source_wenjian_lines:
        print("   前5行:")
        for i, (line_num, content) in enumerate(zip(line_numbers[:5], source_wenjian_lines[:5]), 1):
            print(f"     {i}. 第{line_num}行: {content[:80]}...")
    else:
        print("   ✓ 源文件中没有'文剑'")
    
    # 2. 在数据库中查找"文剑"
    print("\n2. 在数据库中查找'文剑':")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE content LIKE '%文剑%'")
    db_wenjian_count = cursor.fetchone()[0]
    
    print(f"   数据库中有 {db_wenjian_count} 条包含'文剑'的记录")
    
    if db_wenjian_count > 0:
        cursor.execute("""
            SELECT timestamp, sender, content 
            FROM chat_history 
            WHERE content LIKE '%文剑%'
            ORDER BY timestamp 
            LIMIT 5
        """)
        
        db_samples = cursor.fetchall()
        
        print("   前5条记录:")
        for i, (timestamp, sender, content) in enumerate(db_samples, 1):
            print(f"     {i}. {timestamp} {sender}: {content[:60]}...")
    
    # 3. 对比分析
    print("\n3. 对比分析:")
    
    if len(source_wenjian_lines) == 0 and db_wenjian_count == 0:
        print("   ✓ 一致：源文件和数据库都没有'文剑'")
    elif len(source_wenjian_lines) == 0 and db_wenjian_count > 0:
        print("   ⚠ **不一致**：源文件没有'文剑'，但数据库有")
        print(f"      源文件: 0 行")
        print(f"      数据库: {db_wenjian_count} 条")
        
        # 检查数据库中的"文剑"是否可能是误解析
        print("\n   检查数据库'文剑'记录详情:")
        cursor.execute("""
            SELECT content, COUNT(*) as cnt
            FROM chat_history 
            WHERE content LIKE '%文剑%'
            GROUP BY content
            ORDER BY cnt DESC
            LIMIT 10
        """)
        
        common_contents = cursor.fetchall()
        
        print("   最常见的'文剑'内容:")
        for content, count in common_contents:
            percentage = count / db_wenjian_count * 100
            print(f"     '{content}': {count} 次 ({percentage:.1f}%)")
            
    elif len(source_wenjian_lines) > 0 and db_wenjian_count == 0:
        print("   ⚠ **不一致**：源文件有'文剑'，但数据库没有")
        print(f"      源文件: {len(source_wenjian_lines)} 行")
        print(f"      数据库: 0 条")
    else:
        # 都有文剑，检查数量是否匹配
        print(f"   ✓ 都有'文剑'记录")
        print(f"      源文件: {len(source_wenjian_lines)} 行")
        print(f"      数据库: {db_wenjian_count} 条")
        
        if abs(len(source_wenjian_lines) - db_wenjian_count) > 100:
            print(f"   ⚠ 数量差异较大")
    
    # 4. 检查数据库中的其他关键词
    print("\n4. 其他关键词对比:")
    
    keywords = ['项目', '会议', '合同', '预算', '财务']
    
    for keyword in keywords:
        # 源文件
        source_count = 0
        with open(source_file, 'r', encoding='utf-8') as f:
            for line in f:
                if keyword in line:
                    source_count += 1
        
        # 数据库
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE content LIKE ?", (f"%{keyword}%",))
        db_count = cursor.fetchone()[0]
        
        print(f"   '{keyword}': 源文件 {source_count} 次, 数据库 {db_count} 次")
        
        if source_count == 0 and db_count > 100:
            print(f"     ⚠ 异常：源文件没有，但数据库很多")
        elif abs(source_count - db_count) > source_count * 0.5:  # 差异超过50%
            print(f"     ⚠ 数量差异较大")
    
    conn.close()
    
    # 5. 结论
    print("\n" + "=" * 80)
    print("结论:")
    
    if len(source_wenjian_lines) == 0 and db_wenjian_count > 100:
        print("   🚨 **严重问题**：数据库中的'文剑'记录是错误生成的")
        print("   可能原因:")
        print("   1. 之前的导入脚本有bug，错误生成了'文剑'内容")
        print("   2. 数据库被其他数据污染")
        print("   3. 解析逻辑错误")
        print("\n   解决方案:")
        print("   1. 使用新的simple_import.py重新导入（已做）")
        print("   2. 验证新数据库的正确性")
    elif db_wenjian_count <= 172:  # 根据之前输出
        print("   ✓ 新导入的数据库看起来正常")
        print(f"     数据库有 {db_wenjian_count} 条'文剑'记录（可能是真实的少量记录）")
    else:
        print("   ⚠ 需要进一步调查")
    
    print("=" * 80)

if __name__ == "__main__":
    compare_wenjian()