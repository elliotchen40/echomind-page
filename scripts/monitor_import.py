#!/usr/bin/env python3
"""
监控导入进度
"""

import sqlite3
import os
import time

def monitor_import():
    """监控导入进度"""
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    file_path = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    # 获取文件总行数
    with open(file_path, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    print(f"文件总行数: {total_lines:,}")
    print(f"数据库路径: {db_path}")
    print("=" * 60)
    
    prev_count = 0
    start_time = time.time()
    
    while True:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            current_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM chat_history")
            min_time, max_time = cursor.fetchone()
            
            conn.close()
            
            elapsed = time.time() - start_time
            progress = current_count / total_lines * 100
            
            # 计算导入速度
            if elapsed > 0:
                speed = (current_count - prev_count) / elapsed if prev_count > 0 else current_count / elapsed
            else:
                speed = 0
            
            print(f"\r进度: {progress:.1f}% | 已导入: {current_count:,}/{total_lines:,} | "
                  f"速度: {speed:.1f} 条/秒 | 时间范围: {min_time} 到 {max_time}", end="")
            
            prev_count = current_count
            
            # 如果导入完成，退出循环
            if current_count >= total_lines * 0.985:  # 考虑到1.5%的特殊格式
                print(f"\n\n导入基本完成！当前记录数: {current_count:,}")
                print(f"预计缺失: {total_lines - current_count:,} 条（特殊格式）")
                break
            
            time.sleep(5)  # 每5秒更新一次
            
        except KeyboardInterrupt:
            print("\n\n监控被用户中断")
            break
        except Exception as e:
            print(f"\n监控错误: {e}")
            time.sleep(10)

def check_import_quality():
    """检查导入质量"""
    print("\n" + "=" * 60)
    print("检查导入质量")
    print("=" * 60)
    
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 基本统计
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT sender) FROM chat_history")
    senders = cursor.fetchone()[0]
    
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM chat_history")
    min_time, max_time = cursor.fetchone()
    
    # 消息类型统计
    cursor.execute("SELECT message_type, COUNT(*) FROM chat_history GROUP BY message_type")
    msg_types = cursor.fetchall()
    
    # 发送者统计
    cursor.execute("SELECT sender, COUNT(*) FROM chat_history GROUP BY sender ORDER BY COUNT(*) DESC")
    sender_stats = cursor.fetchall()
    
    print(f"总记录数: {total:,}")
    print(f"发送者数量: {senders}")
    print(f"时间范围: {min_time} 到 {max_time}")
    
    print(f"\n消息类型分布:")
    for msg_type, count in msg_types:
        percentage = count / total * 100
        print(f"  {msg_type}: {count:,} ({percentage:.1f}%)")
    
    print(f"\n发送者统计:")
    for sender, count in sender_stats:
        percentage = count / total * 100
        print(f"  {sender}: {count:,} ({percentage:.1f}%)")
    
    conn.close()

if __name__ == "__main__":
    print("开始监控导入进度...")
    monitor_import()
    check_import_quality()