#!/usr/bin/env python3
"""
搜索"碧云"及相关关键词的详细报告
"""

import sqlite3

def search_biyun_comprehensive():
    """综合搜索碧云相关记录"""
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    
    print("=" * 80)
    print("碧云相关聊天记录搜索报告")
    print("=" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 搜索关键词列表
    keywords = [
        "碧云",
        "碧云路",
        "碧云社区",
        "碧云花园",
        "碧云小区",
        "碧云国际",
        "碧云公寓"
    ]
    
    total_results = 0
    
    for keyword in keywords:
        print(f"\n搜索关键词: '{keyword}'")
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM chat_history 
            WHERE content LIKE ?
        """, (f"%{keyword}%",))
        
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"  找到 {count} 条记录")
            
            # 显示前5条记录
            cursor.execute("""
                SELECT timestamp, sender, content 
                FROM chat_history 
                WHERE content LIKE ? 
                ORDER BY timestamp DESC 
                LIMIT 5
            """, (f"%{keyword}%",))
            
            results = cursor.fetchall()
            for i, (timestamp, sender, content) in enumerate(results, 1):
                # 高亮显示关键词
                highlighted = content.replace(keyword, f"【{keyword}】")
                print(f"  {i}. {timestamp} {sender}: {highlighted[:100]}...")
            
            total_results += count
        else:
            print(f"  未找到相关记录")
    
    # 按时间分布分析
    print(f"\n" + "=" * 80)
    print("碧云相关记录时间分布分析")
    print("=" * 80)
    
    cursor.execute("""
        SELECT 
            SUBSTR(timestamp, 1, 4) as year,
            COUNT(*) as count
        FROM chat_history 
        WHERE content LIKE '%碧云%'
        GROUP BY year
        ORDER BY year
    """)
    
    yearly_dist = cursor.fetchall()
    
    if yearly_dist:
        print("按年份分布:")
        for year, count in yearly_dist:
            print(f"  {year}年: {count} 条")
    
    # 按发送者分析
    print(f"\n按发送者分布:")
    cursor.execute("""
        SELECT 
            sender,
            COUNT(*) as count
        FROM chat_history 
        WHERE content LIKE '%碧云%'
        GROUP BY sender
        ORDER BY count DESC
    """)
    
    sender_dist = cursor.fetchall()
    
    for sender, count in sender_dist:
        percentage = count / total_results * 100 if total_results > 0 else 0
        print(f"  {sender}: {count} 条 ({percentage:.1f}%)")
    
    # 相关上下文分析
    print(f"\n" + "=" * 80)
    print("碧云相关记录上下文分析")
    print("=" * 80)
    
    # 查找碧云出现的上下文（前后几条记录）
    cursor.execute("""
        SELECT timestamp, sender, content 
        FROM chat_history 
        WHERE content LIKE '%碧云%'
        ORDER BY timestamp DESC 
        LIMIT 3
    """)
    
    recent_records = cursor.fetchall()
    
    if recent_records:
        print("最近的碧云相关记录:")
        for i, (timestamp, sender, content) in enumerate(recent_records, 1):
            print(f"\n记录 {i}:")
            print(f"  时间: {timestamp}")
            print(f"  发送者: {sender}")
            print(f"  内容: {content}")
            
            # 查找这条记录前后的对话
            cursor.execute("""
                SELECT timestamp, sender, content 
                FROM chat_history 
                WHERE timestamp < ? 
                ORDER BY timestamp DESC 
                LIMIT 2
            """, (timestamp,))
            
            before = cursor.fetchall()
            
            cursor.execute("""
                SELECT timestamp, sender, content 
                FROM chat_history 
                WHERE timestamp > ? 
                ORDER BY timestamp ASC 
                LIMIT 2
            """, (timestamp,))
            
            after = cursor.fetchall()
            
            if before:
                print(f"\n  之前的对话:")
                for ts, snd, cnt in reversed(before):
                    print(f"    {ts} {snd}: {cnt[:80]}...")
            
            print(f"\n  → 当前记录: {content}")
            
            if after:
                print(f"\n  之后的对话:")
                for ts, snd, cnt in after:
                    print(f"    {ts} {snd}: {cnt[:80]}...")
    
    conn.close()
    
    print(f"\n" + "=" * 80)
    print(f"总结: 共找到 {total_results} 条碧云相关记录")
    print("=" * 80)

if __name__ == "__main__":
    search_biyun_comprehensive()