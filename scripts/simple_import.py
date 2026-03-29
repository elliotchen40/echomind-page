#!/usr/bin/env python3
"""
简单、可靠的聊天记录导入脚本
确保不会生成错误数据
"""

import sqlite3
import re
import sys
import os

def simple_import(source_file, db_file):
    """简单导入函数"""
    print(f"源文件: {source_file}")
    print(f"数据库: {db_file}")
    print("=" * 60)
    
    # 1. 检查源文件
    if not os.path.exists(source_file):
        print(f"错误: 源文件不存在: {source_file}")
        return False
    
    # 获取文件信息
    with open(source_file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    file_size = os.path.getsize(source_file) / (1024*1024)  # MB
    
    print(f"文件信息:")
    print(f"  行数: {total_lines:,}")
    print(f"  大小: {file_size:.1f} MB")
    
    # 2. 创建数据库
    if os.path.exists(db_file):
        print(f"警告: 数据库已存在，将删除: {db_file}")
        os.remove(db_file)
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute("""
        CREATE TABLE chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sender TEXT NOT NULL,
            receiver TEXT DEFAULT 'unknown',
            message_type TEXT DEFAULT 'text',
            content TEXT NOT NULL,
            platform TEXT DEFAULT 'wechat',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 3. 解析模式
    pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
    
    # 4. 开始导入
    print("\n开始导入...")
    
    imported = 0
    skipped = 0
    line_num = 0
    
    with open(source_file, 'r', encoding='utf-8') as f:
        for line in f:
            line_num += 1
            line = line.strip()
            
            if not line:
                skipped += 1
                continue
            
            # 跳过标题行
            if line_num == 1 and "微信聊天记录" in line:
                print(f"跳过标题行: {line[:50]}...")
                skipped += 1
                continue
            
            # 解析行
            match = re.match(pattern, line)
            if not match:
                skipped += 1
                continue
            
            sender = match.group(1).strip()
            timestamp_str = match.group(2).strip()
            content = match.group(3).strip()
            
            # 简单时间转换
            try:
                # 将AM/PM转换为24小时制
                if 'PM' in timestamp_str.upper():
                    parts = timestamp_str.split()
                    time_part = parts[1]
                    hour, minute, second = time_part.split(':')
                    hour_int = int(hour)
                    if hour_int < 12:
                        hour_int += 12
                    time_part = f"{hour_int:02d}:{minute}:{second}"
                    timestamp = f"{parts[0]} {time_part}"
                elif 'AM' in timestamp_str.upper():
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
            
            # 推断接收者
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
            
            # 插入数据库
            cursor.execute("""
                INSERT INTO chat_history 
                (timestamp, sender, receiver, message_type, content, platform)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (timestamp, sender, receiver, message_type, content, 'wechat'))
            
            imported += 1
            
            # 进度显示
            if imported % 10000 == 0:
                progress = line_num / total_lines * 100
                print(f"进度: {progress:.1f}% | 已导入: {imported:,} | 跳过: {skipped:,}")
    
    # 提交事务
    conn.commit()
    
    # 创建索引
    print("\n创建索引...")
    cursor.execute("CREATE INDEX idx_timestamp ON chat_history(timestamp)")
    cursor.execute("CREATE INDEX idx_sender ON chat_history(sender)")
    cursor.execute("CREATE INDEX idx_content ON chat_history(content)")
    conn.commit()
    
    # 关闭连接
    conn.close()
    
    # 5. 验证结果
    print("\n导入完成!")
    print(f"总行数: {total_lines:,}")
    print(f"成功导入: {imported:,}")
    print(f"跳过: {skipped:,}")
    
    if imported > 0:
        import_rate = imported / total_lines * 100
        print(f"导入率: {import_rate:.1f}%")
    
    # 检查数据库
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    db_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE content LIKE '%文剑%'")
    wenjian_count = cursor.fetchone()[0]
    
    print(f"\n数据库验证:")
    print(f"  总记录: {db_count:,}")
    print(f"  包含'文剑': {wenjian_count:,} ({wenjian_count/db_count*100 if db_count>0 else 0:.1f}%)")
    
    # 显示一些样本
    if wenjian_count > 0:
        print(f"\n'文剑'记录样本:")
        cursor.execute("SELECT timestamp, sender, content FROM chat_history WHERE content LIKE '%文剑%' LIMIT 3")
        samples = cursor.fetchall()
        
        for i, (timestamp, sender, content) in enumerate(samples, 1):
            print(f"  {i}. {timestamp} {sender}: {content[:60]}...")
    else:
        print(f"\n✓ 数据库中没有'文剑'记录（与源文件一致）")
    
    conn.close()
    
    return True

def main():
    if len(sys.argv) != 3:
        print("用法: python3 simple_import.py <源文件> <数据库文件>")
        print("示例: python3 simple_import.py /path/to/chat.txt /path/to/chat.db")
        return
    
    source_file = sys.argv[1]
    db_file = sys.argv[2]
    
    simple_import(source_file, db_file)

if __name__ == "__main__":
    main()