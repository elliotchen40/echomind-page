#!/usr/bin/env python3
"""
文剑相关记录详细分析
"""

import sqlite3
from datetime import datetime

def analyze_wenjian_records():
    """分析文剑相关记录"""
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    
    print("=" * 80)
    print("文剑相关聊天记录详细分析报告")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. 基本统计
    print("\n1. 基本统计:")
    
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE content LIKE '%文剑%'")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT sender) FROM chat_history WHERE content LIKE '%文剑%'")
    sender_count = cursor.fetchone()[0]
    
    print(f"   总记录数: {total_count:,}")
    print(f"   涉及发送者: {sender_count}")
    
    # 2. 时间分布
    print("\n2. 时间分布:")
    
    cursor.execute("""
        SELECT 
            SUBSTR(timestamp, 1, 4) as year,
            COUNT(*) as count
        FROM chat_history 
        WHERE content LIKE '%文剑%'
        GROUP BY year
        ORDER BY year
    """)
    
    yearly_dist = cursor.fetchall()
    
    if yearly_dist:
        print("   按年份分布:")
        for year, count in yearly_dist:
            percentage = count / total_count * 100
            print(f"     {year}年: {count:,} 条 ({percentage:.1f}%)")
    
    # 3. 发送者分布
    print("\n3. 发送者分布:")
    
    cursor.execute("""
        SELECT 
            sender,
            COUNT(*) as count
        FROM chat_history 
        WHERE content LIKE '%文剑%'
        GROUP BY sender
        ORDER BY count DESC
    """)
    
    sender_dist = cursor.fetchall()
    
    for sender, count in sender_dist:
        percentage = count / total_count * 100
        print(f"   {sender}: {count:,} 条 ({percentage:.1f}%)")
    
    # 4. 消息类型分布
    print("\n4. 消息类型分布:")
    
    cursor.execute("""
        SELECT 
            message_type,
            COUNT(*) as count
        FROM chat_history 
        WHERE content LIKE '%文剑%'
        GROUP BY message_type
        ORDER BY count DESC
    """)
    
    type_dist = cursor.fetchall()
    
    for msg_type, count in type_dist:
        percentage = count / total_count * 100
        print(f"   {msg_type}: {count:,} 条 ({percentage:.1f}%)")
    
    # 5. 高频上下文分析
    print("\n5. 高频上下文分析:")
    
    # 查找常见的文剑相关短语
    common_phrases = [
        ("文剑", "包含'文剑'"),
        ("杜文剑", "全名"),
        ("文剑说", "引用"),
        ("文剑的", "所属"),
        ("文剑在", "位置"),
        ("找文剑", "寻找"),
        ("文剑处理", "处理"),
        ("文剑负责", "负责"),
        ("文剑安排", "安排"),
    ]
    
    for phrase, description in common_phrases:
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE content LIKE ?", (f"%{phrase}%",))
        count = cursor.fetchone()[0]
        if count > 0:
            percentage = count / total_count * 100
            print(f"   {description}: {count:,} 条 ({percentage:.1f}%)")
    
    # 6. 最新记录分析
    print("\n6. 最新记录分析 (最近10条):")
    
    cursor.execute("""
        SELECT timestamp, sender, content 
        FROM chat_history 
        WHERE content LIKE '%文剑%'
        ORDER BY timestamp DESC 
        LIMIT 10
    """)
    
    recent_records = cursor.fetchall()
    
    for i, (timestamp, sender, content) in enumerate(recent_records, 1):
        # 简化显示
        display_content = content
        if len(display_content) > 80:
            display_content = display_content[:77] + "..."
        
        print(f"   {i}. {timestamp} {sender}: {display_content}")
    
    # 7. 对话模式分析
    print("\n7. 对话模式分析:")
    
    # 查找Fanny和EC关于文剑的对话
    cursor.execute("""
        SELECT timestamp, sender, content 
        FROM chat_history 
        WHERE content LIKE '%文剑%' 
          AND (sender LIKE '%Fanny%' OR sender LIKE '%EC%')
        ORDER BY timestamp DESC 
        LIMIT 5
    """)
    
    fanny_ec_records = cursor.fetchall()
    
    if fanny_ec_records:
        print("   Fanny和EC关于文剑的对话示例:")
        for i, (timestamp, sender, content) in enumerate(fanny_ec_records, 1):
            # 提取关键信息
            key_info = content
            if len(key_info) > 60:
                key_info = key_info[:57] + "..."
            print(f"     {i}. {timestamp} {sender}: {key_info}")
    
    # 8. 时间趋势分析
    print("\n8. 时间趋势分析:")
    
    cursor.execute("""
        SELECT 
            SUBSTR(timestamp, 1, 7) as month,
            COUNT(*) as count
        FROM chat_history 
        WHERE content LIKE '%文剑%'
          AND timestamp >= '2022-01-01'
        GROUP BY month
        ORDER BY month DESC
        LIMIT 12
    """)
    
    monthly_trend = cursor.fetchall()
    
    if monthly_trend:
        print("   最近12个月的趋势:")
        for month, count in monthly_trend:
            print(f"     {month}: {count:,} 条")
    
    # 9. 相关项目分析
    print("\n9. 相关项目/主题分析:")
    
    related_keywords = [
        "项目", "合同", "会议", "报告", "预算", 
        "审批", "进度", "问题", "解决", "安排"
    ]
    
    for keyword in related_keywords:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM chat_history 
            WHERE content LIKE '%文剑%' 
              AND content LIKE ?
        """, (f"%{keyword}%",))
        
        count = cursor.fetchone()[0]
        if count > 100:  # 只显示高频相关词
            percentage = count / total_count * 100
            print(f"   文剑+{keyword}: {count:,} 条 ({percentage:.1f}%)")
    
    conn.close()
    
    # 10. 总结
    print("\n" + "=" * 80)
    print("总结:")
    print(f"   • 文剑在聊天记录中出现频率极高，共 {total_count:,} 次")
    print(f"   • 占全部 {total_count:,} 条记录的 {(total_count/353599*100):.1f}%")
    print(f"   • 主要涉及工作安排、项目协调、问题处理等场景")
    print(f"   • 是Fanny和EC工作对话的核心话题之一")
    print("=" * 80)

def export_wenjian_samples():
    """导出文剑记录样本"""
    print("\n" + "=" * 80)
    print("文剑记录样本导出")
    print("=" * 80)
    
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 导出不同类型的样本
    sample_types = [
        ("工作安排", "安排"),
        ("问题处理", "问题"),
        ("会议相关", "会议"),
        ("项目协调", "项目"),
        ("进度汇报", "进度"),
    ]
    
    for category, keyword in sample_types:
        print(f"\n{category}样本:")
        
        cursor.execute("""
            SELECT timestamp, sender, content 
            FROM chat_history 
            WHERE content LIKE '%文剑%' 
              AND content LIKE ?
            ORDER BY timestamp DESC 
            LIMIT 3
        """, (f"%{keyword}%",))
        
        samples = cursor.fetchall()
        
        for i, (timestamp, sender, content) in enumerate(samples, 1):
            print(f"  {i}. {timestamp} {sender}: {content[:80]}...")
    
    conn.close()

if __name__ == "__main__":
    analyze_wenjian_records()
    export_wenjian_samples()