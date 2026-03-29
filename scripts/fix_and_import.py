#!/usr/bin/env python3
"""
修复并导入有问题的聊天记录
"""

import re
import sqlite3
from datetime import datetime

class ChatFixer:
    def __init__(self, db_path):
        self.db_path = db_path
    
    def fix_problematic_line(self, line):
        """修复有问题的行"""
        line = line.strip()
        if not line:
            return None
        
        # 尝试多种修复策略
        
        # 策略1: 标准格式但可能有多余空格
        pattern1 = r'^(.+?)\s*\(\s*(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM))\s*\)\s*:\s*(.+)$'
        match = re.match(pattern1, line, re.IGNORECASE)
        if match:
            sender = match.group(1).strip()
            timestamp = match.group(2).strip()
            content = match.group(3).strip()
            return self._create_record(sender, timestamp, content)
        
        # 策略2: 时间在发送者前面
        pattern2 = r'^(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM))\s+(.+?):(.+)$'
        match = re.match(pattern2, line, re.IGNORECASE)
        if match:
            timestamp = match.group(1).strip()
            sender = match.group(2).strip()
            content = match.group(3).strip()
            return self._create_record(sender, timestamp, content)
        
        # 策略3: 24小时制
        pattern3 = r'^(.+?)\s*\(\s*(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s*\)\s*:\s*(.+)$'
        match = re.match(pattern3, line)
        if match:
            sender = match.group(1).strip()
            timestamp = match.group(2).strip() + " PM"  # 假设是下午
            content = match.group(3).strip()
            return self._create_record(sender, timestamp, content)
        
        # 策略4: 没有括号但有冒号分隔
        if ':' in line:
            parts = line.split(':', 1)
            left = parts[0].strip()
            content = parts[1].strip()
            
            # 尝试从左边提取时间和发送者
            time_patterns = [
                r'(.+?)\s+(\d{4}-\d{2}-\d{2}\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM))$',
                r'(.+?)\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})$',
            ]
            
            for pattern in time_patterns:
                match = re.match(pattern, left)
                if match:
                    sender = match.group(1).strip()
                    timestamp = match.group(2).strip()
                    if 'AM' not in timestamp.upper() and 'PM' not in timestamp.upper():
                        timestamp += " PM"  # 默认下午
                    return self._create_record(sender, timestamp, content)
            
            # 如果左边没有时间，可能是简单的发送者:内容格式
            if left and content:
                return self._create_record(left, "1970-01-01 00:00:00 PM", content)
        
        return None
    
    def _create_record(self, sender, timestamp, content):
        """创建记录字典"""
        # 标准化时间格式
        try:
            # 尝试解析时间
            time_formats = [
                "%Y-%m-%d %I:%M:%S %p",
                "%Y-%m-%d %H:%M:%S %p",
                "%Y-%m-%d %I:%M:%S",
                "%Y-%m-%d %H:%M:%S",
            ]
            
            dt = None
            for fmt in time_formats:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    break
                except ValueError:
                    continue
            
            if dt:
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 保持原始时间
                pass
        except:
            # 时间解析失败，保持原样
            pass
        
        # 推断接收者
        if 'EC' in sender or 'ec' in sender.lower():
            receiver = 'Fanny'
        elif 'Fanny' in sender or 'fanny' in sender.lower():
            receiver = 'EC'
        else:
            receiver = 'unknown'
        
        # 判断消息类型
        message_type = 'text'
        content_lower = content.lower()
        if '[图片]' in content or '图片' in content_lower:
            message_type = 'image'
        elif '[链接]' in content or 'http://' in content_lower or 'https://' in content_lower:
            message_type = 'link'
        elif '[语音]' in content or '语音' in content_lower:
            message_type = 'voice'
        elif '[视频]' in content or '视频' in content_lower:
            message_type = 'video'
        
        return {
            'timestamp': timestamp,
            'sender': sender,
            'receiver': receiver,
            'message_type': message_type,
            'content': content,
            'platform': 'wechat',
            'tags': ''
        }
    
    def import_fixed_lines(self, file_path, start_line=300000, max_lines=10000):
        """导入修复后的行"""
        print(f"开始修复并导入文件: {file_path}")
        print(f"从第 {start_line} 行开始")
        print(f"最大处理行数: {max_lines}\n")
        
        # 连接数据库
        conn = sqlite3.connect(self.db_path)
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(timestamp, sender, content)
            )
        """)
        
        processed = 0
        fixed = 0
        failed = 0
        duplicates = 0
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num < start_line:
                    continue
                
                if processed >= max_lines:
                    break
                
                processed += 1
                
                # 尝试修复
                record = self.fix_problematic_line(line)
                if not record:
                    failed += 1
                    if failed <= 10:  # 只显示前10个失败
                        print(f"无法修复第 {line_num} 行: {line[:80]}...")
                    continue
                
                # 尝试插入数据库
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO chat_history 
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
                    
                    if cursor.rowcount > 0:
                        fixed += 1
                    else:
                        duplicates += 1
                    
                    # 每100条提交一次
                    if fixed % 100 == 0:
                        conn.commit()
                        print(f"已修复 {fixed} 条，失败 {failed} 条，重复 {duplicates} 条")
                
                except Exception as e:
                    failed += 1
                    if failed <= 10:
                        print(f"插入失败第 {line_num} 行: {e}")
        
        # 最后提交
        conn.commit()
        conn.close()
        
        print(f"\n修复完成!")
        print(f"处理行数: {processed}")
        print(f"成功修复: {fixed}")
        print(f"修复失败: {failed}")
        print(f"重复记录: {duplicates}")
        
        if processed > 0:
            success_rate = fixed / processed * 100
            print(f"修复成功率: {success_rate:.1f}%")
        
        return fixed

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="修复并导入有问题的聊天记录")
    parser.add_argument("--file", "-f", required=True, 
                       help="聊天记录文件路径")
    parser.add_argument("--db", "-d", default="/root/.openclaw/workspace/data/chat_history.db",
                       help="数据库文件路径")
    parser.add_argument("--start", type=int, default=300000,
                       help="从第几行开始修复")
    parser.add_argument("--max", type=int, default=10000,
                       help="最大处理行数")
    
    args = parser.parse_args()
    
    fixer = ChatFixer(args.db)
    fixed_count = fixer.import_fixed_lines(args.file, args.start, args.max)
    
    if fixed_count > 0:
        print(f"\n成功修复并导入了 {fixed_count} 条记录!")
        print("现在可以使用查询工具搜索这些记录了。")
    else:
        print("\n没有成功修复任何记录。")

if __name__ == "__main__":
    main()