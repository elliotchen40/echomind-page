#!/usr/bin/env python3
"""
聊天记录导入脚本示例
需要根据实际的聊天记录格式进行修改
"""

import sqlite3
import json
import csv
from datetime import datetime

def import_from_json(json_file, db_path="/root/.openclaw/workspace/data/chat_history.db"):
    """从JSON文件导入聊天记录"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"读取JSON文件失败: {e}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    imported = 0
    for record in data:
        try:
            # 根据实际JSON结构调整字段映射
            timestamp = record.get('timestamp', datetime.now().isoformat())
            sender = record.get('sender', 'unknown')
            receiver = record.get('receiver', 'unknown')
            content = record.get('content', '')
            message_type = record.get('message_type', 'text')
            platform = record.get('platform', 'unknown')
            tags = ','.join(record.get('tags', []))
            
            cursor.execute("""
                INSERT INTO chat_history 
                (timestamp, sender, receiver, message_type, content, platform, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, sender, receiver, message_type, content, platform, tags))
            
            imported += 1
        except Exception as e:
            print(f"导入记录失败: {e}")
            continue
    
    conn.commit()
    conn.close()
    print(f"成功导入 {imported} 条记录")
    return True

def import_from_csv(csv_file, db_path="/root/.openclaw/workspace/data/chat_history.db"):
    """从CSV文件导入聊天记录"""
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    imported = 0
    for record in data:
        try:
            # 根据实际CSV结构调整字段映射
            timestamp = record.get('timestamp', datetime.now().isoformat())
            sender = record.get('sender', 'unknown')
            receiver = record.get('receiver', 'unknown')
            content = record.get('content', '')
            message_type = record.get('message_type', 'text')
            platform = record.get('platform', 'unknown')
            tags = record.get('tags', '')
            
            cursor.execute("""
                INSERT INTO chat_history 
                (timestamp, sender, receiver, message_type, content, platform, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, sender, receiver, message_type, content, platform, tags))
            
            imported += 1
        except Exception as e:
            print(f"导入记录失败: {e}")
            continue
    
    conn.commit()
    conn.close()
    print(f"成功导入 {imported} 条记录")
    return True

def import_from_text(text_file, db_path="/root/.openclaw/workspace/data/chat_history.db"):
    """从纯文本文件导入聊天记录（简单格式）"""
    try:
        with open(text_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"读取文本文件失败: {e}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    imported = 0
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        try:
            # 简单格式：假设每行是"时间 发送者: 内容"
            # 需要根据实际格式调整解析逻辑
            parts = line.split(' ', 2)
            if len(parts) >= 3:
                timestamp = parts[0] + ' ' + parts[1]
                sender_content = parts[2].split(':', 1)
                if len(sender_content) >= 2:
                    sender = sender_content[0].strip()
                    content = sender_content[1].strip()
                    
                    cursor.execute("""
                        INSERT INTO chat_history 
                        (timestamp, sender, receiver, message_type, content, platform, tags)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (timestamp, sender, 'unknown', 'text', content, 'unknown', ''))
                    
                    imported += 1
        except Exception as e:
            print(f"导入记录失败: {e}")
            continue
    
    conn.commit()
    conn.close()
    print(f"成功导入 {imported} 条记录")
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="聊天记录导入工具")
    parser.add_argument("--file", "-f", required=True, help="聊天记录文件路径")
    parser.add_argument("--format", "-t", choices=['json', 'csv', 'text'], 
                       required=True, help="文件格式")
    
    args = parser.parse_args()
    
    if args.format == 'json':
        import_from_json(args.file)
    elif args.format == 'csv':
        import_from_csv(args.file)
    elif args.format == 'text':
        import_from_text(args.file)
    else:
        print("不支持的格式")