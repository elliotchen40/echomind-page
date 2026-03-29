#!/usr/bin/env python3
"""
改进版的聊天记录导入脚本
解决格式解析问题和进程稳定性问题
"""

import sqlite3
import re
import os
import sys
import time
from datetime import datetime

class ChatImporter:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # 多种时间格式模式
        self.patterns = [
            # 标准格式：发送者 (YYYY-MM-DD HH:MM:SS AM/PM):内容
            r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$',
            
            # 发送者在前，24小时制：发送者 YYYY-MM-DD HH:MM:SS:内容
            r'^(.+?) (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}):(.+)$',
            
            # 时间在前：YYYY-MM-DD HH:MM:SS 发送者:内容
            r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (.+?):(.+)$',
            
            # 方括号格式：[YYYY-MM-DD HH:MM:SS] 发送者:内容
            r'^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (.+?):(.+)$',
            
            # 简化格式：发送者:内容 (无时间戳)
            r'^(.+?):(.+)$',
        ]
    
    def connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def setup_database(self):
        """设置数据库表结构"""
        # 创建聊天记录表
        self.cursor.execute("""
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
                UNIQUE(timestamp, sender, content)  -- 防止重复导入
            )
        """)
        
        # 创建索引
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history(timestamp)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_sender ON chat_history(sender)")
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_content ON chat_history(content)")
        
        self.conn.commit()
        print(f"数据库表已设置: {self.db_path}")
    
    def parse_line(self, line):
        """解析聊天记录行，支持多种格式"""
        line = line.strip()
        if not line:
            return None
        
        # 尝试所有格式模式
        for pattern in self.patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                
                if len(groups) == 3:
                    # 格式1-4：有时间戳
                    if pattern == self.patterns[0]:
                        # 格式1：发送者 (时间 AM/PM):内容
                        sender, timestamp_str, content = groups
                        # 转换12小时制到24小时制
                        try:
                            dt = datetime.strptime(timestamp_str, "%Y-%m-%d %I:%M:%S %p")
                            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                        except ValueError:
                            timestamp = timestamp_str
                    elif pattern == self.patterns[1]:
                        # 格式2：发送者 时间(24h):内容
                        sender, timestamp, content = groups
                    elif pattern == self.patterns[2]:
                        # 格式3：时间 发送者:内容
                        timestamp, sender, content = groups
                    elif pattern == self.patterns[3]:
                        # 格式4：[时间] 发送者:内容
                        timestamp, sender, content = groups
                elif len(groups) == 2:
                    # 格式5：发送者:内容 (无时间戳)
                    sender, content = groups
                    timestamp = "1970-01-01 00:00:00"  # 默认时间
                else:
                    continue
                
                # 清理发送者名称
                sender = sender.strip()
                
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
                elif '[文件]' in content or '文件' in content_lower:
                    message_type = 'file'
                
                return {
                    'timestamp': timestamp,
                    'sender': sender,
                    'receiver': receiver,
                    'message_type': message_type,
                    'content': content,
                    'platform': 'wechat',
                    'tags': ''
                }
        
        # 无法解析的行
        return None
    
    def import_file(self, file_path, batch_size=500, resume_from=0, max_records=None):
        """导入聊天记录文件"""
        print(f"开始导入文件: {file_path}")
        print(f"数据库: {self.db_path}")
        print(f"批量大小: {batch_size}")
        print(f"从第 {resume_from} 行开始")
        
        # 统计文件总行数
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                total_lines = sum(1 for _ in f)
            print(f"文件总行数: {total_lines:,}")
        except Exception as e:
            print(f"读取文件失败: {e}")
            return False
        
        # 设置数据库
        self.connect()
        self.setup_database()
        
        imported = 0
        skipped = 0
        batch_count = 0
        duplicates = 0
        start_time = time.time()
        
        print("开始导入聊天记录...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                # 跳过已处理的行
                if line_num < resume_from:
                    continue
                
                # 检查最大记录限制
                if max_records and imported >= max_records:
                    print(f"达到最大导入限制 {max_records} 条，停止导入")
                    break
                
                # 解析行
                record = self.parse_line(line)
                if not record:
                    skipped += 1
                    continue
                
                # 尝试插入记录（使用唯一约束防止重复）
                try:
                    self.cursor.execute("""
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
                    
                    if self.cursor.rowcount > 0:
                        imported += 1
                        batch_count += 1
                    else:
                        duplicates += 1
                    
                    # 批量提交
                    if batch_count >= batch_size:
                        self.conn.commit()
                        elapsed = time.time() - start_time
                        progress = line_num / total_lines * 100
                        print(f"进度: {progress:.1f}% | 已导入: {imported:,} | 跳过: {skipped:,} | 重复: {duplicates:,} | 耗时: {elapsed:.1f}s")
                        batch_count = 0
                    
                    # 每5000条显示一次进度
                    if imported % 5000 == 0:
                        elapsed = time.time() - start_time
                        rate = imported / elapsed if elapsed > 0 else 0
                        print(f"已导入 {imported:,} 条记录 | 速率: {rate:.1f} 条/秒")
                        
                except Exception as e:
                    skipped += 1
                    if skipped % 1000 == 0:
                        print(f"跳过 {skipped} 行（解析或插入失败）")
                    continue
        
        # 最后提交
        self.conn.commit()
        self.close()
        
        elapsed = time.time() - start_time
        print(f"\n导入完成！")
        print(f"总耗时: {elapsed:.1f} 秒")
        print(f"成功导入: {imported:,} 条记录")
        print(f"跳过: {skipped:,} 行（无法解析的格式）")
        print(f"重复: {duplicates:,} 条（已存在）")
        
        if imported + skipped + duplicates > 0:
            success_rate = imported / (imported + skipped) * 100 if (imported + skipped) > 0 else 0
            print(f"成功率: {success_rate:.1f}%")
        
        return True
    
    def get_import_status(self):
        """获取导入状态"""
        self.connect()
        
        self.cursor.execute("SELECT COUNT(*) FROM chat_history")
        total = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM chat_history")
        min_time, max_time = self.cursor.fetchone()
        
        self.cursor.execute("SELECT COUNT(DISTINCT sender) FROM chat_history")
        senders = self.cursor.fetchone()[0]
        
        self.close()
        
        return {
            'total_records': total,
            'time_range': (min_time, max_time),
            'senders': senders
        }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="改进版聊天记录导入工具")
    parser.add_argument("--file", "-f", required=True, 
                       help="聊天记录文件路径")
    parser.add_argument("--db", "-d", default="/root/.openclaw/workspace/data/chat_history.db",
                       help="数据库文件路径")
    parser.add_argument("--batch", type=int, default=500,
                       help="批量提交大小（默认：500）")
    parser.add_argument("--resume", type=int, default=0,
                       help="从第几行开始导入（用于恢复）")
    parser.add_argument("--max", type=int, default=None,
                       help="最大导入记录数（测试用）")
    parser.add_argument("--status", action="store_true",
                       help="显示当前导入状态")
    
    args = parser.parse_args()
    
    importer = ChatImporter(args.db)
    
    if args.status:
        status = importer.get_import_status()
        print("=== 当前导入状态 ===")
        print(f"总记录数: {status['total_records']:,}")
        print(f"时间范围: {status['time_range'][0]} 到 {status['time_range'][1]}")
        print(f"发送者数量: {status['senders']}")
    else:
        success = importer.import_file(
            args.file, 
            batch_size=args.batch,
            resume_from=args.resume,
            max_records=args.max
        )
        
        if success:
            print("\n导入成功！")
            # 显示最终状态
            status = importer.get_import_status()
            print(f"数据库现在有 {status['total_records']:,} 条记录")
        else:
            print("\n导入失败！")

if __name__ == "__main__":
    main()