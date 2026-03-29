#!/usr/bin/env python3
"""
内存优化的聊天记录导入脚本
专门针对4GB内存系统优化
"""

import sqlite3
import re
import gc
import os
import sys
import time
from datetime import datetime

class MemoryOptimizedImporter:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # 内存优化配置
        self.batch_size = 200  # 减小批量大小
        self.max_memory_mb = 500  # 最大内存使用限制
        self.gc_frequency = 1000  # 每处理1000条记录执行一次垃圾回收
        
        # 格式模式
        self.pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
    
    def connect(self):
        """连接数据库（使用内存优化设置）"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA journal_mode = WAL")  # 写前日志，减少锁
        self.conn.execute("PRAGMA synchronous = NORMAL")  # 平衡性能和数据安全
        self.conn.execute("PRAGMA cache_size = -2000")  # 2MB缓存
        self.cursor = self.conn.cursor()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
        gc.collect()  # 强制垃圾回收
    
    def setup_database(self):
        """设置数据库表结构"""
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
                UNIQUE(timestamp, sender, content)
            )
        """)
        
        # 先不创建索引，导入完成后再创建
        # self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history(timestamp)")
        # self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_sender ON chat_history(sender)")
        # self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_content ON chat_history(content)")
        
        self.conn.commit()
    
    def parse_line_memory_efficient(self, line):
        """内存高效的解析函数"""
        line = line.strip()
        if not line:
            return None
        
        match = re.match(self.pattern, line)
        if not match:
            return None
        
        sender = match.group(1).strip()
        timestamp_str = match.group(2).strip()
        content = match.group(3).strip()
        
        # 简化时间转换
        try:
            # 直接字符串处理，避免datetime对象创建
            if 'PM' in timestamp_str.upper():
                # 简单转换：PM时小时+12
                parts = timestamp_str.split()
                time_part = parts[1]
                hour, minute, second = time_part.split(':')
                hour_int = int(hour)
                if hour_int < 12:
                    hour_int += 12
                time_part = f"{hour_int:02d}:{minute}:{second}"
                timestamp = f"{parts[0]} {time_part}"
            elif 'AM' in timestamp_str.upper():
                # AM时，12点转为0点
                parts = timestamp_str.split()
                time_part = parts[1]
                hour, minute, second = time_part.split(':')
                hour_int = int(hour)
                if hour_int == 12:
                    hour_int = 0
                time_part = f"{hour_int:02d}:{minute}:{second}"
                timestamp = f"{parts[0]} {time_part}"
            else:
                timestamp = timestamp_str
        except:
            timestamp = timestamp_str
        
        # 推断接收者（使用简单判断）
        receiver = 'unknown'
        if 'EC' in sender.upper():
            receiver = 'Fanny'
        elif 'FANNY' in sender.upper():
            receiver = 'EC'
        
        # 判断消息类型
        message_type = 'text'
        if '[图片]' in content:
            message_type = 'image'
        elif '[链接]' in content or 'http://' in content.lower() or 'https://' in content.lower():
            message_type = 'link'
        elif '[语音]' in content:
            message_type = 'voice'
        elif '[视频]' in content:
            message_type = 'video'
        
        # 返回元组而不是字典，减少内存
        return (timestamp, sender, receiver, message_type, content, 'wechat', '')
    
    def import_file_memory_optimized(self, file_path, resume_from=0):
        """内存优化的文件导入"""
        print(f"开始内存优化导入: {file_path}")
        print(f"批量大小: {self.batch_size}")
        print(f"从第 {resume_from} 行开始")
        print(f"最大内存限制: {self.max_memory_mb} MB\n")
        
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
        duplicates = 0
        batch_count = 0
        start_time = time.time()
        last_gc_time = time.time()
        
        # 准备插入语句
        insert_sql = """
            INSERT OR IGNORE INTO chat_history 
            (timestamp, sender, receiver, message_type, content, platform, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        print("开始导入...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num < resume_from:
                    continue
                
                # 解析行
                record = self.parse_line_memory_efficient(line)
                if not record:
                    skipped += 1
                    continue
                
                # 插入记录
                try:
                    self.cursor.execute(insert_sql, record)
                    
                    if self.cursor.rowcount > 0:
                        imported += 1
                        batch_count += 1
                    else:
                        duplicates += 1
                    
                    # 批量提交
                    if batch_count >= self.batch_size:
                        self.conn.commit()
                        
                        # 进度显示
                        elapsed = time.time() - start_time
                        progress = line_num / total_lines * 100
                        
                        # 内存检查
                        import psutil
                        memory = psutil.virtual_memory()
                        memory_mb = memory.used / (1024**2)
                        
                        print(f"进度: {progress:.1f}% | 导入: {imported:,} | 跳过: {skipped:,} | "
                              f"重复: {duplicates:,} | 内存: {memory_mb:.0f} MB | 耗时: {elapsed:.0f}s")
                        
                        batch_count = 0
                        
                        # 内存保护：如果使用过多内存，强制垃圾回收
                        if memory_mb > self.max_memory_mb:
                            print(f"内存使用过高 ({memory_mb:.0f} MB)，执行垃圾回收...")
                            gc.collect()
                            last_gc_time = time.time()
                    
                    # 定期垃圾回收
                    if imported % self.gc_frequency == 0:
                        gc.collect()
                
                except Exception as e:
                    skipped += 1
                    continue
        
        # 最后提交
        self.conn.commit()
        
        # 创建索引（导入完成后）
        print("\n导入完成，开始创建索引...")
        index_start = time.time()
        
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history(timestamp)")
        self.conn.commit()
        print(f"  创建索引 idx_timestamp: {(time.time() - index_start):.1f}s")
        
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_sender ON chat_history(sender)")
        self.conn.commit()
        print(f"  创建索引 idx_sender: {(time.time() - index_start):.1f}s")
        
        self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_content ON chat_history(content)")
        self.conn.commit()
        print(f"  创建索引 idx_content: {(time.time() - index_start):.1f}s")
        
        self.close()
        
        elapsed = time.time() - start_time
        print(f"\n导入完成!")
        print(f"总耗时: {elapsed:.1f} 秒")
        print(f"平均速度: {imported/elapsed:.1f} 条/秒")
        print(f"成功导入: {imported:,} 条记录")
        print(f"跳过: {skipped:,} 行（无法解析）")
        print(f"重复: {duplicates:,} 条（已存在）")
        
        if imported + skipped > 0:
            success_rate = imported / (imported + skipped) * 100
            print(f"成功率: {success_rate:.1f}%")
        
        return True
    
    def check_existing_data(self):
        """检查已有数据"""
        self.connect()
        self.cursor.execute("SELECT COUNT(*) FROM chat_history")
        count = self.cursor.fetchone()[0]
        self.close()
        return count

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="内存优化的聊天记录导入")
    parser.add_argument("--file", "-f", required=True, 
                       help="聊天记录文件路径")
    parser.add_argument("--db", "-d", default="/root/.openclaw/workspace/data/chat_history.db",
                       help="数据库文件路径")
    parser.add_argument("--batch", type=int, default=200,
                       help="批量提交大小（默认：200）")
    parser.add_argument("--resume", type=int, default=0,
                       help="从第几行开始导入")
    parser.add_argument("--check", action="store_true",
                       help="检查当前数据量")
    
    args = parser.parse_args()
    
    importer = MemoryOptimizedImporter(args.db)
    importer.batch_size = args.batch
    
    if args.check:
        count = importer.check_existing_data()
        print(f"当前数据库记录数: {count:,}")
    else:
        print(f"系统内存: 4GB")
        print(f"优化设置: 批量大小={args.batch}, 内存限制={importer.max_memory_mb}MB")
        
        success = importer.import_file_memory_optimized(
            args.file, 
            resume_from=args.resume
        )
        
        if success:
            print("\n导入成功！现在可以使用查询工具了。")
        else:
            print("\n导入失败！")

if __name__ == "__main__":
    main()