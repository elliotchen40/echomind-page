#!/usr/bin/env python3
"""
导入标准聊天记录格式
格式：YYYY-MM-DD HH:MM:SS 发送者: 内容
"""

import sqlite3
import re
from datetime import datetime

def parse_chat_line(line):
    """解析标准聊天记录格式的行"""
    line = line.strip()
    if not line:
        return None
    
    # 匹配格式：YYYY-MM-DD HH:MM:SS 发送者: 内容
    pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (.+?): (.+)$'
    match = re.match(pattern, line)
    
    if match:
        timestamp_str = match.group(1)
        sender = match.group(2).strip()
        content = match.group(3).strip()
        
        # 将时间戳转换为标准格式
        try:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            timestamp = dt.isoformat()
        except ValueError:
            timestamp = timestamp_str
        
        return {
            'timestamp': timestamp,
            'sender': sender,
            'content': content,
            'receiver': 'unknown',  # 需要根据上下文推断
            'message_type': 'text',
            'platform': 'chat',
            'tags': ''
        }
    
    # 尝试其他格式：YYYY-MM-DD HH:MM 发送者: 内容
    pattern2 = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}) (.+?): (.+)$'
    match2 = re.match(pattern2, line)
    
    if match2:
        timestamp_str = match2.group(1)
        sender = match2.group(2).strip()
        content = match2.group(3).strip()
        
        try:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
            timestamp = dt.isoformat()
        except ValueError:
            timestamp = timestamp_str
        
        return {
            'timestamp': timestamp,
            'sender': sender,
            'content': content,
            'receiver': 'unknown',
            'message_type': 'text',
            'platform': 'chat',
            'tags': ''
        }
    
    return None

def import_chat_file(file_path, db_path="/root/.openclaw/workspace/data/chat_history.db", 
                    batch_size=1000, max_records=None):
    """导入聊天记录文件"""
    try:
        # 统计文件总行数
        print("正在统计文件行数...")
        with open(file_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)
        print(f"文件总行数: {total_lines}")
    except Exception as e:
        print(f"读取文件失败: {e}")
        return False
    
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
            
            record = parse_chat_line(line)
            if not record:
                skipped += 1
                continue
            
            # 推断接收者（简单逻辑：如果发送者是用户，接收者是助手，反之亦然）
            if 'elliot' in record['sender'].lower() or '用户' in record['sender']:
                record['receiver'] = 'assistant'
            elif 'fanny' in record['sender'].lower() or '助手' in record['sender']:
                record['receiver'] = 'user'
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
    print(f"成功率: {imported/(imported+skipped)*100:.1f}%")
    
    return True

def test_parse():
    """测试解析函数"""
    test_lines = [
        "2026-03-14 21:50:00 Elliot: 用户偏好与Fanny以老朋友般的随意语气交流",
        "2026-03-14 22:03:00 Fanny: 用户的本地记忆文件存储在目录中",
        "2026-03-14 22:04:00 System: 用户因疲劳暂时休息",
        "2023-01-15 14:30:00 张三: 你好，最近怎么样？",
        "2023-01-15 14:31:00 李四: 我很好，谢谢！",
        "无效格式行",
        "",
        "2023-01-15 14:32:00 王五: 我们什么时候开会？"
    ]
    
    for i, line in enumerate(test_lines, 1):
        result = parse_chat_line(line)
        if result:
            print(f"{i}. 解析成功: {result['timestamp']} - {result['sender']}: {result['content'][:30]}...")
        else:
            print(f"{i}. 跳过: {line}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="导入标准聊天记录格式")
    parser.add_argument("--file", "-f", required=True, 
                       help="聊天记录文件路径")
    parser.add_argument("--test", action="store_true",
                       help="测试解析功能")
    parser.add_argument("--batch", type=int, default=1000,
                       help="批量提交大小（默认：1000）")
    parser.add_argument("--max", type=int, default=None,
                       help="最大导入记录数（测试用）")
    
    args = parser.parse_args()
    
    if args.test:
        test_parse()
    else:
        print(f"开始导入文件: {args.file}")
        print(f"批量大小: {args.batch}")
        if args.max:
            print(f"最大导入记录: {args.max}")
        
        success = import_chat_file(args.file, batch_size=args.batch, max_records=args.max)
        if success:
            print("导入成功！")
        else:
            print("导入失败！")