#!/usr/bin/env python3
"""
导入微信聊天记录格式
格式：发送者 (YYYY-MM-DD HH:MM:SS AM/PM):内容
"""

import sqlite3
import re
from datetime import datetime
import os

def parse_wechat_line(line):
    """解析微信聊天记录格式的行"""
    line = line.strip()
    if not line:
        return None
    
    # 匹配格式：发送者 (YYYY-MM-DD HH:MM:SS AM/PM):内容
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
            'receiver': 'unknown',  # 需要根据上下文推断
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

def import_wechat_file(file_path, db_path="/root/.openclaw/workspace/data/chat_history.db", 
                      batch_size=1000, max_records=None):
    """导入微信聊天记录文件"""
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
            
            # 跳过文件头
            if line_num <= 2 and ("微信聊天记录" in line or "Fanny" in line):
                continue
            
            record = parse_wechat_line(line)
            if not record:
                skipped += 1
                continue
            
            # 推断接收者（简单逻辑：如果发送者是EC，接收者是Fanny，反之亦然）
            if 'EC' in record['sender']:
                record['receiver'] = 'Fanny'
            elif 'Fanny' in record['sender']:
                record['receiver'] = 'EC'
            else:
                record['receiver'] = 'unknown'
            
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

def test_parse():
    """测试解析函数"""
    test_lines = [
        "Fanny - 微信聊天记录",
        "",
        "EC (2017-11-29 02:55:11 PM):[图片]",
        "Fanny (2017-11-29 02:57:17 PM):恩",
        "EC (2017-11-29 06:21:11 PM):[链接]",
        "EC (2017-11-29 06:21:45 PM):帮忙看下有没有错",
        "Fanny (2017-11-29 06:22:49 PM):不对",
        "Fanny (2017-11-29 06:22:58 PM):[图片]",
        "Fanny (2017-11-29 06:23:06 PM):这部分由物业找地产收就好",
        "Fanny (2026-02-06 02:33:37 PM):不准",
        "EC (2026-02-06 02:33:47 PM):也是",
        "Fanny (2026-03-02 09:18:14 AM):[语音]",
        "EC (2026-03-02 09:18:49 AM):好",
        "无效格式行",
        "",
        "Fanny (2026-02-25 06:48:34 PM):最左边是谁啊"
    ]
    
    for i, line in enumerate(test_lines, 1):
        result = parse_wechat_line(line)
        if result:
            print(f"{i}. 解析成功: {result['sender']} - {result['timestamp']}: {result['content'][:30]}...")
        else:
            print(f"{i}. 跳过: {line[:50]}...")

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

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="导入微信聊天记录格式")
    parser.add_argument("--file", "-f", required=True, 
                       help="聊天记录文件路径")
    parser.add_argument("--db", "-d", default="/root/.openclaw/workspace/data/chat_history.db",
                       help="数据库文件路径（默认：/root/.openclaw/workspace/data/chat_history.db）")
    parser.add_argument("--test", action="store_true",
                       help="测试解析功能")
    parser.add_argument("--batch", type=int, default=1000,
                       help="批量提交大小（默认：1000）")
    parser.add_argument("--max", type=int, default=None,
                       help="最大导入记录数（测试用）")
    parser.add_argument("--query", "-q", action="store_true",
                       help="查询数据库内容")
    parser.add_argument("--limit", type=int, default=10,
                       help="查询时显示的最大记录数（默认：10）")
    
    args = parser.parse_args()
    
    if args.test:
        test_parse()
    elif args.query:
        query_database(args.db, args.limit)
    else:
        print(f"开始导入文件: {args.file}")
        print(f"数据库路径: {args.db}")
        print(f"批量大小: {args.batch}")
        if args.max:
            print(f"最大导入记录: {args.max}")
        
        success = import_wechat_file(args.file, db_path=args.db, 
                                   batch_size=args.batch, max_records=args.max)
        if success:
            print("导入成功！")
            # 显示导入统计
            query_database(args.db, 5)
        else:
            print("导入失败！")