#!/usr/bin/env python3
"""
导入当前聊天记录文件格式
格式：发送者 (YYYY-MM-DD HH:MM:SS AM/PM):内容
示例：Fanny (2026-02-06 02:33:37 PM):不准
"""

import sqlite3
import re
from datetime import datetime
import os
import sys

def parse_chat_line(line):
    """解析聊天记录格式的行"""
    line = line.strip()
    if not line:
        return None
    
    # 匹配格式：发送者 (YYYY-MM-DD HH:MM:SS AM/PM):内容
    # 注意：发送者可能包含空格，如 "Fanny - 微信聊天记录"
    pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
    match = re.match(pattern, line)
    
    if match:
        sender = match.group(1).strip()
        timestamp_str = match.group(2).strip()
        content = match.group(3).strip()
        
        # 将12小时制时间转换为24小时制
        try:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %I:%M:%S %p")
            timestamp = dt.isoformat()
        except ValueError:
            # 如果转换失败，使用原始字符串
            timestamp = timestamp_str
        
        return {
            'timestamp': timestamp,
            'sender': sender,
            'content': content,
            'receiver': 'unknown',
            'message_type': 'text',
            'platform': 'wechat',
            'tags': ''
        }
    
    return None

def create_database(db_path):
    """创建数据库和表结构"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建聊天记录表
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
    
    # 创建索引以提高查询性能
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sender ON chat_history(sender)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_content ON chat_history(content)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_platform ON chat_history(platform)")
    
    conn.commit()
    conn.close()
    print(f"数据库已创建/更新: {db_path}")

def import_chat_file(file_path, db_path="/root/.openclaw/workspace/data/chat_history.db", 
                    batch_size=1000, max_records=None):
    """导入聊天记录文件"""
    try:
        # 统计文件总行数
        print("正在统计文件行数...")
        with open(file_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)
        print(f"文件总行数: {total_lines:,}")
    except Exception as e:
        print(f"读取文件失败: {e}")
        return False
    
    # 创建数据库
    create_database(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    imported = 0
    skipped = 0
    batch_count = 0
    
    print("开始导入聊天记录...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if max_records and imported >= max_records:
                print(f"达到最大导入限制 {max_records} 条，停止导入")
                break
            
            # 跳过文件头（前2行）
            if line_num <= 2:
                continue
            
            record = parse_chat_line(line)
            if not record:
                skipped += 1
                continue
            
            # 推断接收者
            if 'EC' in record['sender']:
                record['receiver'] = 'Fanny'
            elif 'Fanny' in record['sender']:
                record['receiver'] = 'EC'
            else:
                record['receiver'] = 'unknown'
            
            # 判断消息类型
            if '[图片]' in record['content']:
                record['message_type'] = 'image'
            elif '[链接]' in record['content']:
                record['message_type'] = 'link'
            elif '[语音]' in record['content']:
                record['message_type'] = 'voice'
            elif '[视频]' in record['content']:
                record['message_type'] = 'video'
            
            try:
                cursor.execute("""
                    INSERT INTO chat_history 
                    (timestamp, sender, receiver, message_type, content, platform, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    record['timestamp'],
                    record['sender'],
                    record['receiver'],
                    record['message_type'],
                    record['content'],
                    record['platform'],
                    record['tags']
                ))
                
                imported += 1
                batch_count += 1
                
                # 批量提交
                if batch_count >= batch_size:
                    conn.commit()
                    print(f"已导入 {imported:,} 条记录 (进度: {line_num/total_lines*100:.1f}%)")
                    batch_count = 0
                
                # 进度显示
                if imported % 5000 == 0:
                    print(f"已导入 {imported:,} 条记录...")
                    
            except Exception as e:
                skipped += 1
                if skipped % 1000 == 0:
                    print(f"跳过 {skipped} 行无法解析的记录...")
                continue
    
    # 最后提交
    conn.commit()
    conn.close()
    
    print(f"\n导入完成！")
    print(f"成功导入: {imported:,} 条记录")
    print(f"跳过: {skipped:,} 行（无法解析的格式）")
    if imported + skipped > 0:
        print(f"成功率: {imported/(imported+skipped)*100:.1f}%")
    
    return True

def query_database(db_path, limit=10):
    """查询数据库内容"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n数据库中的最新 {limit} 条记录:")
    cursor.execute("""
        SELECT timestamp, sender, receiver, content 
        FROM chat_history 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    for row in cursor.fetchall():
        timestamp, sender, receiver, content = row
        print(f"{timestamp} {sender} -> {receiver}: {content[:50]}...")
    
    # 统计信息
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total = cursor.fetchone()[0]
    print(f"\n总记录数: {total:,}")
    
    cursor.execute("SELECT COUNT(DISTINCT sender) FROM chat_history")
    senders = cursor.fetchone()[0]
    print(f"发送者数量: {senders}")
    
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM chat_history")
    min_time, max_time = cursor.fetchone()
    print(f"时间范围: {min_time} 到 {max_time}")
    
    conn.close()

def search_by_keyword(db_path, keyword, limit=20):
    """按关键词搜索聊天记录"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"\n搜索关键词: '{keyword}'")
    
    cursor.execute("""
        SELECT timestamp, sender, receiver, content 
        FROM chat_history 
        WHERE content LIKE ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (f"%{keyword}%", limit))
    
    results = cursor.fetchall()
    
    if not results:
        print("未找到匹配的记录")
    else:
        print(f"找到 {len(results)} 条匹配记录:")
        for i, row in enumerate(results, 1):
            timestamp, sender, receiver, content = row
            print(f"{i}. {timestamp} {sender}: {content}")
    
    conn.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="导入聊天记录文件")
    parser.add_argument("--file", "-f", required=True, 
                       help="聊天记录文件路径")
    parser.add_argument("--db", "-d", default="/root/.openclaw/workspace/data/chat_history.db",
                       help="数据库文件路径（默认：/root/.openclaw/workspace/data/chat_history.db）")
    parser.add_argument("--batch", type=int, default=1000,
                       help="批量提交大小（默认：1000）")
    parser.add_argument("--max", type=int, default=None,
                       help="最大导入记录数（测试用）")
    parser.add_argument("--query", "-q", action="store_true",
                       help="查询数据库内容")
    parser.add_argument("--limit", type=int, default=10,
                       help="查询时显示的最大记录数（默认：10）")
    parser.add_argument("--search", "-s", type=str,
                       help="按关键词搜索聊天记录")
    
    args = parser.parse_args()
    
    if args.search:
        search_by_keyword(args.db, args.search, args.limit)
    elif args.query:
        query_database(args.db, args.limit)
    else:
        print(f"开始导入文件: {args.file}")
        print(f"数据库路径: {args.db}")
        print(f"批量大小: {args.batch}")
        if args.max:
            print(f"最大导入记录: {args.max}")
        
        success = import_chat_file(args.file, db_path=args.db, 
                                 batch_size=args.batch, max_records=args.max)
        if success:
            print("导入成功！")
            # 显示导入统计
            query_database(args.db, 5)
        else:
            print("导入失败！")