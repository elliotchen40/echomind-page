#!/usr/bin/env python3
"""
聊天记录导入脚本
将格式为 'Sender (YYYY-MM-DD HH:MM:SS AM/PM): Content' 的聊天记录导入SQLite数据库
"""

import sqlite3
import re
from datetime import datetime
import sys
import os

def parse_chat_line(line):
    """解析聊天记录行"""
    line = line.strip()
    if not line:
        return None
    
    # 尝试格式1: [时间] 发送者: 内容
    pattern1 = r'^\[(.+?)\] (.+?): (.+)$'
    match = re.match(pattern1, line)
    
    if match:
        timestamp_str = match.group(1).strip()
        sender = match.group(2).strip()
        content = match.group(3).strip()
        
        # 尝试多种时间格式
        time_formats = [
            '%Y-%m-%d %I:%M:%S %p',  # 2024-01-01 12:00:00 PM
            '%Y/%m/%d %I:%M:%S %p',  # 2024/01/01 12:00:00 PM
            '%Y-%m-%d %H:%M:%S',     # 2024-01-01 12:00:00
            '%Y/%m/%d %H:%M:%S',     # 2024/01/01 12:00:00
        ]
        
        for time_format in time_formats:
            try:
                dt = datetime.strptime(timestamp_str, time_format)
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                return sender, timestamp, content
            except ValueError:
                continue
        
        # 如果无法解析时间，使用原始时间戳
        return sender, timestamp_str, content
    
    # 尝试格式2: Sender (YYYY-MM-DD HH:MM:SS AM/PM): Content
    pattern2 = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [AP]M)\): (.+)$'
    match = re.match(pattern2, line)
    
    if match:
        sender = match.group(1).strip()
        timestamp_str = match.group(2)
        content = match.group(3).strip()
        
        try:
            dt = datetime.strptime(timestamp_str, '%Y-%m-%d %I:%M:%S %p')
            timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            return sender, timestamp, content
        except ValueError:
            return sender, timestamp_str, content
    
    return None

def create_database(db_path='chat_records.db'):
    """创建数据库和表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # 创建索引以便快速查询
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sender ON chat_messages(sender)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_messages(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_content ON chat_messages(content)')
    
    conn.commit()
    return conn

def import_chat_file(chat_file_path, db_path='chat_records.db'):
    """导入聊天记录文件到数据库"""
    if not os.path.exists(chat_file_path):
        print(f"错误: 聊天记录文件不存在: {chat_file_path}")
        return False
    
    conn = create_database(db_path)
    cursor = conn.cursor()
    
    imported_count = 0
    error_count = 0
    
    print(f"开始导入聊天记录文件: {chat_file_path}")
    
    with open(chat_file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
                
            parsed = parse_chat_line(line)
            if parsed:
                sender, timestamp, content = parsed
                
                # 检查是否已存在相同记录
                cursor.execute('''
                    SELECT COUNT(*) FROM chat_messages 
                    WHERE sender=? AND timestamp=? AND content=?
                ''', (sender, timestamp, content))
                
                if cursor.fetchone()[0] == 0:
                    cursor.execute('''
                        INSERT INTO chat_messages (sender, timestamp, content)
                        VALUES (?, ?, ?)
                    ''', (sender, timestamp, content))
                    imported_count += 1
                    
                    if imported_count % 1000 == 0:
                        print(f"已导入 {imported_count} 条记录...")
            else:
                error_count += 1
                if error_count <= 10:  # 只显示前10个错误
                    print(f"第 {line_num} 行格式错误: {line[:50]}...")
    
    conn.commit()
    conn.close()
    
    print(f"\n导入完成!")
    print(f"成功导入: {imported_count} 条记录")
    print(f"格式错误: {error_count} 行")
    print(f"数据库文件: {db_path}")
    
    return True

def query_database(db_path='/root/.openclaw/workspace/date/chat_records.db', keyword=None, sender=None, date_range=None):
    """查询数据库"""
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = 'SELECT * FROM chat_messages'
    conditions = []
    params = []
    
    if keyword:
        conditions.append('content LIKE ?')
        params.append(f'%{keyword}%')
    
    if sender:
        conditions.append('sender = ?')
        params.append(sender)
    
    if date_range:
        start_date, end_date = date_range
        conditions.append('timestamp BETWEEN ? AND ?')
        params.extend([start_date, end_date])
    
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY timestamp LIMIT 100'
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    print(f"\n查询结果 ({len(results)} 条):")
    print("-" * 80)
    
    for row in results:
        msg_id, msg_sender, msg_time, msg_content, created_at = row
        print(f"[{msg_time}] {msg_sender}: {msg_content[:100]}...")
    
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法:")
        print("  导入聊天记录: python import_chat_to_sqlite.py <聊天记录文件路径>")
        print("  查询数据库: python import_chat_to_sqlite.py --query [--keyword 关键词] [--sender 发送者]")
        sys.exit(1)
    
    if sys.argv[1] == '--query':
        # 查询模式
        import argparse
        parser = argparse.ArgumentParser(description='查询聊天记录数据库')
        parser.add_argument('--keyword', help='搜索关键词')
        parser.add_argument('--sender', help='发送者名称')
        parser.add_argument('--start-date', help='开始日期 (YYYY-MM-DD)')
        parser.add_argument('--end-date', help='结束日期 (YYYY-MM-DD)')
        
        args = parser.parse_args(sys.argv[2:])
        
        date_range = None
        if args.start_date and args.end_date:
            date_range = (args.start_date, args.end_date)
        
        query_database(
            keyword=args.keyword,
            sender=args.sender,
            date_range=date_range
        )
    else:
        # 导入模式
        chat_file = sys.argv[1]
        db_file = sys.argv[2] if len(sys.argv) > 2 else 'chat_records.db'
        import_chat_file(chat_file, db_file)