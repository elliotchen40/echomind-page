#!/usr/bin/env python3
"""
导入memOS格式的聊天记录
格式：[YYYY-MM-DD HH:MM] 内容
"""

import sqlite3
import re
from datetime import datetime

def parse_memos_line(line):
    """解析memOS格式的行"""
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    
    # 匹配格式：[YYYY-MM-DD HH:MM] 内容
    pattern = r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\] (.+)$'
    match = re.match(pattern, line)
    
    if match:
        timestamp_str = match.group(1)
        content = match.group(2)
        
        # 将时间戳转换为标准格式
        try:
            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
            timestamp = dt.isoformat()
        except ValueError:
            timestamp = timestamp_str
        
        return {
            'timestamp': timestamp,
            'content': content,
            'sender': 'system',  # 默认为系统记录
            'receiver': 'user',
            'message_type': 'text',
            'platform': 'memos',
            'tags': ''
        }
    
    return None

def extract_sender_from_content(content):
    """从内容中提取发送者信息"""
    # 尝试从内容中提取发送者
    sender_patterns = [
        r'^用户(.+)$',  # "用户偏好..."
        r'^助手(.+)$',  # "助手..."
        r'^(.+?)：',    # "发送者：内容"
        r'^(.+?) ',     # "发送者 内容"
    ]
    
    for pattern in sender_patterns:
        match = re.match(pattern, content)
        if match:
            return match.group(1).strip()
    
    # 根据内容类型判断
    if '用户' in content:
        return 'user'
    elif '助手' in content or 'Fanny' in content:
        return 'assistant'
    else:
        return 'system'

def import_memos_file(file_path, db_path="/root/.openclaw/workspace/data/chat_history.db"):
    """导入memOS格式的文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    imported = 0
    skipped = 0
    
    for line_num, line in enumerate(lines, 1):
        record = parse_memos_line(line)
        if not record:
            skipped += 1
            continue
        
        # 从内容中提取发送者
        sender = extract_sender_from_content(record['content'])
        record['sender'] = sender
        
        # 如果是用户相关的内容，接收者为助手
        if '用户' in record['content'] or sender == 'user':
            record['receiver'] = 'assistant'
        else:
            record['receiver'] = 'user'
        
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
            
            # 获取插入的ID并添加关键词索引
            chat_id = cursor.lastrowid
            add_keywords(cursor, chat_id, record['content'])
            
            imported += 1
            
            if imported % 100 == 0:
                print(f"已导入 {imported} 条记录...")
                
        except Exception as e:
            print(f"第 {line_num} 行导入失败: {e}")
            skipped += 1
            continue
    
    conn.commit()
    conn.close()
    
    print(f"导入完成！")
    print(f"成功导入: {imported} 条记录")
    print(f"跳过: {skipped} 行（空行或注释）")
    
    return True

def add_keywords(cursor, chat_id, content):
    """添加关键词索引"""
    # 提取中文关键词（长度大于1的中文字符）
    import jieba
    words = jieba.cut(content)
    
    keywords = set()
    for word in words:
        word = word.strip()
        if len(word) > 1 and is_chinese(word):
            keywords.add(word)
    
    # 如果没有jieba，使用简单方法
    if not keywords:
        # 简单提取：按空格和标点分割
        import re
        words = re.findall(r'[\u4e00-\u9fff]{2,}', content)
        keywords = set(words)
    
    for keyword in keywords:
        try:
            cursor.execute(
                "INSERT INTO keyword_index (keyword, chat_id) VALUES (?, ?)",
                (keyword, chat_id)
            )
        except:
            pass  # 忽略重复关键词

def is_chinese(text):
    """检查是否为中文字符"""
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def test_parse():
    """测试解析函数"""
    test_lines = [
        "[2026-03-14 21:50] 用户偏好与Fanny以老朋友般的随意语气交流，不用说太多套话和客气话",
        "[2026-03-14 22:03] 用户的本地记忆文件存储在 /root/.openclaw/workspace/ 目录中",
        "# 这是一个注释",
        "",
        "普通文本行"
    ]
    
    for line in test_lines:
        result = parse_memos_line(line)
        if result:
            print(f"解析成功: {result['timestamp']} - {result['content'][:50]}...")
        else:
            print(f"跳过: {line}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="导入memOS格式的聊天记录")
    parser.add_argument("--file", "-f", required=True, 
                       help="memOS格式的聊天记录文件路径")
    parser.add_argument("--test", action="store_true",
                       help="测试解析功能")
    
    args = parser.parse_args()
    
    if args.test:
        test_parse()
    else:
        print(f"开始导入文件: {args.file}")
        success = import_memos_file(args.file)
        if success:
            print("导入成功！")
        else:
            print("导入失败！")