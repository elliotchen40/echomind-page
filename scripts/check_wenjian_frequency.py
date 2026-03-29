#!/usr/bin/env python3
"""
检查文剑出现的真实频率
"""

import sqlite3
import re

def check_real_frequency():
    """检查文剑的真实出现频率"""
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    
    print("=" * 80)
    print("文剑出现频率真实性检查")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 检查数据库基本信息
    print("\n1. 数据库基本信息:")
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total_records = cursor.fetchone()[0]
    print(f"   总记录数: {total_records:,}")
    
    # 2. 检查文剑出现次数
    print("\n2. 文剑出现统计:")
    
    # 方法1: LIKE查询
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE content LIKE '%文剑%'")
    like_count = cursor.fetchone()[0]
    print(f"   LIKE查询结果: {like_count:,} 条")
    
    # 方法2: 抽样检查
    print("\n3. 抽样检查:")
    
    # 随机抽样100条记录
    cursor.execute("SELECT content FROM chat_history ORDER BY RANDOM() LIMIT 100")
    samples = cursor.fetchall()
    
    wenjian_in_samples = 0
    for content, in samples:
        if '文剑' in content:
            wenjian_in_samples += 1
    
    print(f"   随机抽样100条，包含'文剑'的: {wenjian_in_samples} 条")
    print(f"   抽样比例: {wenjian_in_samples/100*100:.1f}%")
    
    # 方法3: 检查具体内容
    print("\n4. 具体内容检查:")
    
    cursor.execute("""
        SELECT content 
        FROM chat_history 
        WHERE content LIKE '%文剑%'
        ORDER BY RANDOM() 
        LIMIT 10
    """)
    
    sample_contents = cursor.fetchall()
    
    print("   随机10条包含'文剑'的记录:")
    for i, (content,) in enumerate(sample_contents, 1):
        # 提取文剑出现的上下文
        if len(content) > 100:
            # 找到文剑位置
            pos = content.find('文剑')
            start = max(0, pos - 30)
            end = min(len(content), pos + 30)
            snippet = content[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(content):
                snippet = snippet + "..."
        else:
            snippet = content
        
        print(f"   {i}. {snippet}")
    
    # 方法4: 检查发送者分布
    print("\n5. 发送者分布检查:")
    
    cursor.execute("""
        SELECT sender, COUNT(*) 
        FROM chat_history 
        WHERE content LIKE '%文剑%'
        GROUP BY sender 
        ORDER BY COUNT(*) DESC
    """)
    
    sender_dist = cursor.fetchall()
    
    for sender, count in sender_dist:
        percentage = count / like_count * 100
        print(f"   {sender}: {count:,} 条 ({percentage:.1f}%)")
    
    # 方法5: 检查时间分布
    print("\n6. 时间分布检查:")
    
    cursor.execute("""
        SELECT SUBSTR(timestamp, 1, 4) as year, COUNT(*)
        FROM chat_history 
        WHERE content LIKE '%文剑%'
        GROUP BY year
        ORDER BY year
    """)
    
    year_dist = cursor.fetchall()
    
    for year, count in year_dist:
        percentage = count / like_count * 100
        print(f"   {year}年: {count:,} 条 ({percentage:.1f}%)")
    
    # 方法6: 检查是否可能是数据重复
    print("\n7. 重复记录检查:")
    
    cursor.execute("""
        SELECT COUNT(DISTINCT timestamp || sender || content) as unique_records,
               COUNT(*) as total_records
        FROM chat_history 
        WHERE content LIKE '%文剑%'
    """)
    
    unique_count, total_wenjian = cursor.fetchone()
    
    print(f"   包含'文剑'的总记录: {total_wenjian:,}")
    print(f"   唯一记录: {unique_count:,}")
    
    if unique_count < total_wenjian:
        duplicate_rate = (total_wenjian - unique_count) / total_wenjian * 100
        print(f"   ⚠ 发现重复记录: {total_wenjian - unique_count:,} 条 ({duplicate_rate:.1f}%)")
    else:
        print(f"   ✓ 无重复记录")
    
    conn.close()
    
    # 8. 结论分析
    print("\n" + "=" * 80)
    print("结论分析:")
    
    if like_count == 171432:
        print(f"   • 数据库确实包含171,432条'文剑'记录")
        print(f"   • 占全部记录的 {like_count/total_records*100:.1f}%")
        
        if wenjian_in_samples >= 40:  # 抽样中超过40%包含文剑
            print(f"   • 抽样验证: 文剑出现频率确实很高 ({wenjian_in_samples}%)")
            print(f"   • 文剑是聊天记录的核心话题")
        else:
            print(f"   • 抽样验证: 实际频率可能低于统计 ({wenjian_in_samples}%)")
            print(f"   • 可能存在统计误差或数据异常")
    else:
        print(f"   • 统计不一致: 当前查询到 {like_count:,} 条，之前报告 171,432 条")
        print(f"   • 可能数据库已更新或查询有误")
    
    print("=" * 80)

if __name__ == "__main__":
    check_real_frequency()