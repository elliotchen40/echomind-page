#!/usr/bin/env python3
"""
聊天记录查询工具
可以按关键词、发送者、时间范围等条件查询
"""

import sqlite3
import argparse
from datetime import datetime
import sys

class ChatQuery:
    def __init__(self, db_path="/root/.openclaw/workspace/data/chat_history.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # 返回字典格式的结果
    
    def search_by_keyword(self, keyword, limit=20, sender=None, start_date=None, end_date=None):
        """按关键词搜索聊天记录"""
        query = """
            SELECT timestamp, sender, receiver, content 
            FROM chat_history 
            WHERE content LIKE ?
        """
        params = [f"%{keyword}%"]
        
        if sender:
            query += " AND sender LIKE ?"
            params.append(f"%{sender}%")
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return results
    
    def search_by_sender(self, sender, limit=20, keyword=None):
        """按发送者搜索聊天记录"""
        query = """
            SELECT timestamp, sender, receiver, content 
            FROM chat_history 
            WHERE sender LIKE ?
        """
        params = [f"%{sender}%"]
        
        if keyword:
            query += " AND content LIKE ?"
            params.append(f"%{keyword}%")
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        return results
    
    def get_statistics(self):
        """获取数据库统计信息"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # 总记录数
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        stats['total_records'] = cursor.fetchone()[0]
        
        # 发送者统计
        cursor.execute("SELECT sender, COUNT(*) as count FROM chat_history GROUP BY sender ORDER BY count DESC")
        stats['senders'] = cursor.fetchall()
        
        # 消息类型统计
        cursor.execute("SELECT message_type, COUNT(*) as count FROM chat_history GROUP BY message_type")
        stats['message_types'] = cursor.fetchall()
        
        # 时间范围
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM chat_history")
        min_time, max_time = cursor.fetchone()
        stats['time_range'] = (min_time, max_time)
        
        # 热门关键词（按词频）
        cursor.execute("""
            SELECT content, COUNT(*) as count 
            FROM chat_history 
            WHERE LENGTH(content) > 2 
            GROUP BY content 
            ORDER BY count DESC 
            LIMIT 10
        """)
        stats['common_content'] = cursor.fetchall()
        
        return stats
    
    def export_results(self, results, format='text'):
        """导出查询结果"""
        if format == 'text':
            for i, row in enumerate(results, 1):
                print(f"{i}. {row['timestamp']} {row['sender']} -> {row['receiver']}:")
                print(f"   {row['content']}")
                print()
        elif format == 'csv':
            import csv
            writer = csv.writer(sys.stdout)
            writer.writerow(['序号', '时间', '发送者', '接收者', '内容'])
            for i, row in enumerate(results, 1):
                writer.writerow([i, row['timestamp'], row['sender'], row['receiver'], row['content']])
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description="聊天记录查询工具")
    parser.add_argument("--keyword", "-k", type=str, help="搜索关键词")
    parser.add_argument("--sender", "-s", type=str, help="发送者名称")
    parser.add_argument("--limit", "-l", type=int, default=20, help="显示结果数量（默认：20）")
    parser.add_argument("--start", type=str, help="开始日期（格式：YYYY-MM-DD）")
    parser.add_argument("--end", type=str, help="结束日期（格式：YYYY-MM-DD）")
    parser.add_argument("--stats", action="store_true", help="显示数据库统计信息")
    parser.add_argument("--export", type=str, choices=['text', 'csv'], default='text', 
                       help="导出格式（默认：text）")
    parser.add_argument("--db", type=str, default="/root/.openclaw/workspace/data/chat_history.db",
                       help="数据库路径（默认：/root/.openclaw/workspace/data/chat_history.db）")
    
    args = parser.parse_args()
    
    query = ChatQuery(args.db)
    
    try:
        if args.stats:
            print("=== 数据库统计信息 ===")
            stats = query.get_statistics()
            
            print(f"\n总记录数: {stats['total_records']:,}")
            print(f"时间范围: {stats['time_range'][0]} 到 {stats['time_range'][1]}")
            
            print("\n发送者统计:")
            for sender, count in stats['senders']:
                print(f"  {sender}: {count:,} 条")
            
            print("\n消息类型统计:")
            for msg_type, count in stats['message_types']:
                print(f"  {msg_type}: {count:,} 条")
            
            print("\n常见内容（前10）:")
            for content, count in stats['common_content']:
                if len(content) > 50:
                    content_display = content[:50] + "..."
                else:
                    content_display = content
                print(f"  {content_display}: {count} 次")
        
        elif args.keyword or args.sender:
            if args.keyword:
                print(f"=== 搜索关键词: '{args.keyword}' ===")
                results = query.search_by_keyword(
                    args.keyword, 
                    limit=args.limit,
                    sender=args.sender,
                    start_date=args.start,
                    end_date=args.end
                )
            else:
                print(f"=== 搜索发送者: '{args.sender}' ===")
                results = query.search_by_sender(
                    args.sender,
                    limit=args.limit,
                    keyword=args.keyword
                )
            
            if results:
                print(f"找到 {len(results)} 条记录:\n")
                query.export_results(results, args.export)
            else:
                print("未找到匹配的记录")
        
        else:
            print("请指定搜索条件（--keyword 或 --sender）或使用 --stats 查看统计信息")
            print("\n示例:")
            print("  python3 chat_query.py --keyword 项目")
            print("  python3 chat_query.py --sender Fanny --limit 10")
            print("  python3 chat_query.py --keyword 会议 --start 2017-11-01 --end 2017-11-30")
            print("  python3 chat_query.py --stats")
    
    finally:
        query.close()

if __name__ == "__main__":
    main()