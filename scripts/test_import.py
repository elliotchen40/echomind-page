#!/usr/bin/env python3
"""
测试导入脚本的快速版本
"""

import sqlite3
import re
from datetime import datetime

def test_parse():
    """测试解析功能"""
    test_lines = [
        "Fanny (2017-11-29 02:33:37 PM):不准",
        "EC (2017-11-29 02:55:11 PM):[图片]",
        "Fanny - 微信聊天记录 (2017-11-29 06:21:45 PM):这部分由物业找地产收就好",
        "Fanny (2017-11-29 06:22:58 PM):[图片]",
        "Fanny (2017-11-29 06:23:06 PM):这部分由物业找地产收就好",
    ]
    
    pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
    
    for line in test_lines:
        match = re.match(pattern, line)
        if match:
            sender = match.group(1).strip()
            timestamp_str = match.group(2).strip()
            content = match.group(3).strip()
            
            print(f"✓ 成功解析: {sender} | {timestamp_str} | {content[:30]}...")
        else:
            print(f"✗ 无法解析: {line}")

def check_database():
    """检查数据库状态"""
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_history'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✓ 数据库表已存在")
            
            # 统计记录数
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            count = cursor.fetchone()[0]
            print(f"✓ 当前记录数: {count:,}")
            
            # 显示最新5条记录
            cursor.execute("SELECT timestamp, sender, content FROM chat_history ORDER BY timestamp DESC LIMIT 5")
            print("\n最新5条记录:")
            for row in cursor.fetchall():
                timestamp, sender, content = row
                print(f"  {timestamp} {sender}: {content[:50]}...")
        else:
            print("✗ 数据库表不存在")
        
        conn.close()
    except Exception as e:
        print(f"✗ 检查数据库失败: {e}")

def quick_import_sample():
    """快速导入少量样本数据"""
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    file_path = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    print(f"从文件导入样本数据: {file_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 确保表存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            content TEXT NOT NULL,
            platform TEXT DEFAULT 'wechat',
            tags TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    imported = 0
    pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 2:  # 跳过前2行
                continue
            
            if imported >= 100:  # 只导入100条
                break
            
            line = line.strip()
            if not line:
                continue
            
            match = re.match(pattern, line)
            if match:
                sender = match.group(1).strip()
                timestamp_str = match.group(2).strip()
                content = match.group(3).strip()
                
                # 推断接收者
                if 'EC' in sender:
                    receiver = 'Fanny'
                elif 'Fanny' in sender:
                    receiver = 'EC'
                else:
                    receiver = 'unknown'
                
                # 判断消息类型
                message_type = 'text'
                if '[图片]' in content:
                    message_type = 'image'
                elif '[链接]' in content:
                    message_type = 'link'
                elif '[语音]' in content:
                    message_type = 'voice'
                elif '[视频]' in content:
                    message_type = 'video'
                
                try:
                    cursor.execute("""
                        INSERT INTO chat_history 
                        (timestamp, sender, receiver, message_type, content, platform)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        timestamp_str,  # 保持原始格式
                        sender,
                        receiver,
                        message_type,
                        content,
                        'wechat'
                    ))
                    imported += 1
                except Exception as e:
                    continue
    
    conn.commit()
    conn.close()
    
    print(f"✓ 快速导入完成: {imported} 条记录")

if __name__ == "__main__":
    print("=== 测试聊天记录导入 ===")
    
    print("\n1. 测试解析功能:")
    test_parse()
    
    print("\n2. 检查数据库状态:")
    check_database()
    
    print("\n3. 快速导入样本数据:")
    quick_import_sample()
    
    print("\n4. 再次检查数据库:")
    check_database()
    
    print("\n=== 测试完成 ===")