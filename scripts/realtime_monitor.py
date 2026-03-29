#!/usr/bin/env python3
"""
实时监控导入进度
"""

import sqlite3
import os
import time
import sys

def monitor_import_realtime():
    """实时监控导入进度"""
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    file_path = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    # 获取文件总行数
    with open(file_path, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    print(f"文件总行数: {total_lines:,}")
    print(f"目标导入率: >98.5% (跳过约1.5%格式问题行)")
    print("=" * 70)
    
    last_count = 0
    start_time = time.time()
    last_update = start_time
    
    while True:
        try:
            # 检查数据库文件是否存在
            if not os.path.exists(db_path):
                print("等待数据库文件创建...")
                time.sleep(2)
                continue
            
            # 连接数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 获取当前记录数
            cursor.execute("SELECT COUNT(*) FROM chat_history")
            current_count = cursor.fetchone()[0]
            
            # 获取时间范围
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM chat_history")
            result = cursor.fetchone()
            min_time, max_time = result if result else (None, None)
            
            conn.close()
            
            # 计算进度
            elapsed = time.time() - start_time
            progress = current_count / total_lines * 100
            
            # 计算速度
            time_since_last = time.time() - last_update
            if time_since_last > 0:
                speed = (current_count - last_count) / time_since_last
            else:
                speed = 0
            
            # 估算剩余时间
            if speed > 0 and progress < 100:
                remaining = (total_lines - current_count) / speed
                remaining_str = f"{remaining/60:.1f}分钟"
            else:
                remaining_str = "计算中..."
            
            # 显示进度
            sys.stdout.write(f"\r进度: {progress:.1f}% | 已导入: {current_count:,}/{total_lines:,} | "
                           f"速度: {speed:.1f} 条/秒 | 耗时: {elapsed/60:.1f}分钟 | "
                           f"剩余: {remaining_str}")
            sys.stdout.flush()
            
            last_count = current_count
            last_update = time.time()
            
            # 检查是否完成
            if progress >= 98.5:  # 考虑到1.5%的格式问题
                print(f"\n\n导入基本完成！当前进度: {progress:.1f}%")
                print(f"已导入记录: {current_count:,}")
                print(f"预计缺失: {total_lines - current_count:,} 条（格式问题）")
                
                # 显示最终统计
                print("\n" + "=" * 70)
                print("最终统计:")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(DISTINCT sender) FROM chat_history")
                senders = cursor.fetchone()[0]
                
                cursor.execute("SELECT sender, COUNT(*) FROM chat_history GROUP BY sender")
                sender_stats = cursor.fetchall()
                
                print(f"发送者数量: {senders}")
                for sender, count in sender_stats:
                    percentage = count / current_count * 100
                    print(f"  {sender}: {count:,} ({percentage:.1f}%)")
                
                conn.close()
                break
            
            time.sleep(5)  # 每5秒更新一次
            
        except KeyboardInterrupt:
            print("\n\n监控被用户中断")
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                # 数据库被锁定，等待重试
                time.sleep(2)
                continue
            else:
                print(f"\n数据库错误: {e}")
                break
        except Exception as e:
            print(f"\n监控错误: {e}")
            time.sleep(5)

if __name__ == "__main__":
    print("开始实时监控导入进度...")
    monitor_import_realtime()