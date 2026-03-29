#!/usr/bin/env python3
"""
创建干净的聊天记录数据库
"""

import sqlite3
import os

def create_database(db_path="/root/.openclaw/workspace/data/chat_history.db"):
    """创建干净的数据库"""
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 删除旧数据库（如果存在）
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"已删除旧数据库: {db_path}")
    
    # 创建新数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建聊天记录表
    cursor.execute("""
        CREATE TABLE chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT,
            message_type TEXT DEFAULT 'text',
            content TEXT NOT NULL,
            platform TEXT DEFAULT 'chat',
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX idx_timestamp ON chat_history(timestamp)")
    cursor.execute("CREATE INDEX idx_sender ON chat_history(sender)")
    cursor.execute("CREATE INDEX idx_content ON chat_history(content)")
    
    # 创建关键词索引表
    cursor.execute("""
        CREATE TABLE keyword_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            record_id INTEGER NOT NULL,
            FOREIGN KEY (record_id) REFERENCES chat_history(id)
        )
    """)
    
    cursor.execute("CREATE INDEX idx_keyword ON keyword_index(keyword)")
    
    conn.commit()
    conn.close()
    
    print(f"已创建干净的数据库: {db_path}")
    print("表结构:")
    print("  - chat_history: 聊天记录主表")
    print("  - keyword_index: 关键词索引表")
    
    return True

if __name__ == "__main__":
    print("开始创建干净的聊天记录数据库...")
    success = create_database()
    if success:
        print("数据库创建成功！")
    else:
        print("数据库创建失败！")