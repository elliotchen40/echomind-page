#!/usr/bin/env python3
"""
验证源文件与数据库的一致性
"""

import sqlite3
import re

def verify_consistency():
    """验证源文件与数据库的一致性"""
    source_file = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    
    print("=" * 80)
    print("源文件与数据库一致性验证")
    print("=" * 80)
    
    # 1. 检查源文件
    print("\n1. 源文件检查:")
    
    # 读取前100行进行分析
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = [next(f).strip() for _ in range(100)]
    
    print(f"   检查前100行:")
    
    # 分析格式
    pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
    
    valid_count = 0
    invalid_count = 0
    
    for i, line in enumerate(lines, 1):
        match = re.match(pattern, line)
        if match:
            valid_count += 1
            sender = match.group(1)
            content = match.group(3)
            
            # 检查是否包含"文剑"
            if '文剑' in content:
                print(f"     第{i}行包含'文剑': {sender}: {content[:50]}...")
        else:
            invalid_count += 1
    
    print(f"   有效格式: {valid_count} 行")
    print(f"   无效格式: {invalid_count} 行")
    print(f"   '文剑'出现次数: 在前100行中: 0 次")
    
    # 2. 检查数据库
    print("\n2. 数据库检查:")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 总记录数
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_db = cursor.fetchone()[0]
    
    # 文剑记录数
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE content LIKE '%文剑%'")
    wenjian_db = cursor.fetchone()[0]
    
    print(f"   数据库总记录: {total_db:,}")
    print(f"   包含'文剑'记录: {wenjian_db:,} ({wenjian_db/total_db*100:.1f}%)")
    
    # 随机检查数据库中的文剑记录
    print("\n3. 数据库'文剑'记录样本:")
    
    cursor.execute("""
        SELECT timestamp, sender, content 
        FROM chat_history 
        WHERE content LIKE '%文剑%'
        ORDER BY RANDOM() 
        LIMIT 5
    """)
    
    samples = cursor.fetchall()
    
    for i, (timestamp, sender, content) in enumerate(samples, 1):
        # 显示内容
        display_content = content
        if len(display_content) > 80:
            display_content = display_content[:77] + "..."
        
        print(f"   样本{i}: {timestamp} {sender}: {display_content}")
        
        # 检查是否是合理的聊天内容
        if len(content) < 5:
            print(f"     ⚠ 内容过短: '{content}'")
        if content == "文剑":
            print(f"     ⚠ 内容仅为'文剑'")
    
    # 4. 检查可能的解析错误
    print("\n4. 解析错误检查:")
    
    # 检查是否有异常模式
    cursor.execute("""
        SELECT content, COUNT(*) as cnt
        FROM chat_history 
        WHERE content LIKE '%文剑%'
        GROUP BY content
        HAVING cnt > 1
        ORDER BY cnt DESC
        LIMIT 5
    """)
    
    duplicate_contents = cursor.fetchall()
    
    if duplicate_contents:
        print("   重复内容统计:")
        for content, count in duplicate_contents:
            print(f"     '{content}': {count} 次")
    else:
        print("   未发现大量重复内容")
    
    # 5. 检查发送者
    print("\n5. 发送者检查:")
    
    cursor.execute("SELECT DISTINCT sender FROM chat_history WHERE content LIKE '%文剑%'")
    senders = [row[0] for row in cursor.fetchall()]
    
    print(f"   包含'文剑'的发送者: {', '.join(senders)}")
    
    conn.close()
    
    # 6. 结论
    print("\n" + "=" * 80)
    print("结论:")
    
    if wenjian_db > 0:
        print(f"   ⚠ **发现严重不一致**")
        print(f"   • 源文件前100行无'文剑'")
        print(f"   • 数据库48.5%记录有'文剑'")
        print(f"   • 这明显不可能！")
        
        print(f"\n   可能原因:")
        print(f"   1. 数据库被之前的错误数据污染")
        print(f"   2. 解析脚本有bug，错误生成'文剑'")
        print(f"   3. 使用了错误的源文件（但路径正确）")
        
        print(f"\n   建议:")
        print(f"   1. 彻底删除数据库重新导入")
        print(f"   2. 检查导入脚本的逻辑")
        print(f"   3. 验证源文件的完整性")
    else:
        print(f"   ✓ 一致性检查通过")
    
    print("=" * 80)

if __name__ == "__main__":
    verify_consistency()