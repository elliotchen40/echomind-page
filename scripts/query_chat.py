#!/usr/bin/env python3
"""
聊天记录查询工具
支持关键词搜索、时间范围查询、发送者过滤等
"""

import sqlite3
import argparse
from datetime import datetime
import re

def connect_db(db_path="/root/.openclaw/workspace/data/chat_history.db"):
    """连接数据库"""
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Exception as e:
        print(f"连接数据库失败: {e}")
        return None

def search_by_keyword(keyword, db_path="/root/.openclaw/workspace/data/chat_history.db", 
                     limit=50, sender=None, start_date=None, end_date=None):
    """按关键词搜索聊天记录"""
    conn = connect_db(db_path)
    if not conn:
        return []
    
    cursor = conn.cursor()
    
    # 构建查询条件
    conditions = ["content LIKE ?"]
    params = [f"%{keyword}%"]
    
    if sender:
        conditions.append("sender LIKE ?")
        params.append(f"%{sender}%")
    
    if start_date:
        conditions.append("timestamp >= ?")
        params.append(start_date)
    
    if end_date:
        conditions.append("timestamp <= ?")
        params.append(end_date)
    
    where_clause = " AND ".join(conditions)
    
    query = f"""
        SELECT timestamp, sender, receiver, content 
        FROM chat_history 
        WHERE {where_clause}
        ORDER BY timestamp DESC 
        LIMIT ?
    """
    params.append(limit)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return results

def get_statistics(db_path="/root/.openclaw/workspace/data/chat_history.db"):
    """获取统计信息"""
    conn = connect_db(db_path)
    if not conn:
        return {}
    
    cursor = conn.cursor()
    
    stats = {}
    
    # 总记录数
    cursor.execute("SELECT COUNT(*) FROM chat_history")
    stats['total_records'] = cursor.fetchone()[0]
    
    # 发送者统计
    cursor.execute("SELECT sender, COUNT(*) FROM chat_history GROUP BY sender ORDER BY COUNT(*) DESC")
    stats['sender_stats'] = cursor.fetchall()
    
    # 时间范围
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM chat_history")
    min_time, max_time = cursor.fetchone()
    stats['time_range'] = (min_time, max_time)
    
    # 每日消息统计
    cursor.execute("""
        SELECT DATE(timestamp), COUNT(*) 
        FROM chat_history 
        GROUP BY DATE(timestamp) 
        ORDER BY DATE(timestamp) DESC 
        LIMIT 10
    """)
    stats['recent_days'] = cursor.fetchall()
    
    # 消息类型统计
    cursor.execute("SELECT message_type, COUNT(*) FROM chat_history GROUP BY message_type")
    stats['message_types'] = cursor.fetchall()
    
    conn.close()
    return stats

def export_to_text(results, output_file=None):
    """将查询结果导出为文本格式"""
    output_lines = []
    for timestamp, sender, receiver, content in results:
        # 将时间戳转换为可读格式
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %I:%M:%S %p")
        except:
            time_str = timestamp
        
        output_lines.append(f"{sender} ({time_str}):{content}")
    
    output_text = "\n".join(output_lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_text)
        print(f"已导出 {len(results)} 条记录到 {output_file}")
    
    return output_text

def interactive_search(db_path="/root/.openclaw/workspace/data/chat_history.db"):
    """交互式搜索界面"""
    print("=== 聊天记录查询工具 ===")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'stats' 查看统计信息")
    print("输入 'help' 查看帮助")
    print()
    
    while True:
        try:
            user_input = input("搜索关键词 (或命令): ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            elif user_input.lower() in ['stats', '统计']:
                stats = get_statistics(db_path)
                print(f"\n=== 统计信息 ===")
                print(f"总记录数: {stats['total_records']:,}")
                print(f"时间范围: {stats['time_range'][0]} 到 {stats['time_range'][1]}")
                print(f"\n发送者统计:")
                for sender, count in stats['sender_stats']:
                    print(f"  {sender}: {count:,} 条 ({count/stats['total_records']*100:.1f}%)")
                print(f"\n最近10天消息统计:")
                for date, count in stats['recent_days']:
                    print(f"  {date}: {count} 条")
                print()
            elif user_input.lower() in ['help', '帮助']:
                print("\n=== 帮助 ===")
                print("搜索语法:")
                print("  关键词 - 搜索包含关键词的消息")
                print("  关键词 from:发送者 - 搜索指定发送者的消息")
                print("  关键词 date:YYYY-MM-DD - 搜索指定日期的消息")
                print("  关键词 date:YYYY-MM-DD..YYYY-MM-DD - 搜索日期范围")
                print("  关键词 limit:数字 - 限制结果数量")
                print("示例: '项目 from:Fanny date:2020-01-01..2020-12-31 limit:20'")
                print()
            else:
                # 解析搜索参数
                keyword = user_input
                sender = None
                start_date = None
                end_date = None
                limit = 20
                
                # 解析 from: 参数
                from_match = re.search(r'from:(\S+)', keyword)
                if from_match:
                    sender = from_match.group(1)
                    keyword = keyword.replace(from_match.group(0), '').strip()
                
                # 解析 date: 参数
                date_match = re.search(r'date:(\S+)', keyword)
                if date_match:
                    date_str = date_match.group(1)
                    keyword = keyword.replace(date_match.group(0), '').strip()
                    
                    if '..' in date_str:
                        start_date, end_date = date_str.split('..')
                    else:
                        start_date = date_str
                        end_date = date_str
                
                # 解析 limit: 参数
                limit_match = re.search(r'limit:(\d+)', keyword)
                if limit_match:
                    limit = int(limit_match.group(1))
                    keyword = keyword.replace(limit_match.group(0), '').strip()
                
                if not keyword:
                    keyword = "%"
                
                print(f"\n搜索条件:")
                print(f"  关键词: {keyword}")
                if sender:
                    print(f"  发送者: {sender}")
                if start_date:
                    print(f"  时间范围: {start_date} 到 {end_date}")
                print(f"  结果数量: {limit}")
                print()
                
                results = search_by_keyword(
                    keyword=keyword,
                    db_path=db_path,
                    limit=limit,
                    sender=sender,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if results:
                    print(f"找到 {len(results)} 条记录:")
                    print("-" * 80)
                    for i, (timestamp, sender, receiver, content) in enumerate(results, 1):
                        try:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            time_str = dt.strftime("%Y-%m-%d %I:%M:%S %p")
                        except:
                            time_str = timestamp
                        
                        print(f"{i}. {time_str} {sender} -> {receiver}:")
                        print(f"   {content}")
                        print()
                else:
                    print("未找到匹配的记录")
                print()
                
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="聊天记录查询工具")
    parser.add_argument("--keyword", "-k", help="搜索关键词")
    parser.add_argument("--sender", "-s", help="发送者过滤")
    parser.add_argument("--start-date", help="开始日期 (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="结束日期 (YYYY-MM-DD)")
    parser.add_argument("--limit", "-l", type=int, default=50, help="结果数量限制")
    parser.add_argument("--db", "-d", default="/root/.openclaw/workspace/data/chat_history.db",
                       help="数据库文件路径")
    parser.add_argument("--export", "-e", help="导出结果到文件")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    parser.add_argument("--interactive", "-i", action="store_true", help="交互式模式")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_search(args.db)
    elif args.stats:
        stats = get_statistics(args.db)
        print(f"=== 聊天记录统计 ===")
        print(f"总记录数: {stats['total_records']:,}")
        print(f"时间范围: {stats['time_range'][0]} 到 {stats['time_range'][1]}")
        print(f"\n发送者统计:")
        for sender, count in stats['sender_stats']:
            print(f"  {sender}: {count:,} 条 ({count/stats['total_records']*100:.1f}%)")
        print(f"\n消息类型统计:")
        for msg_type, count in stats['message_types']:
            print(f"  {msg_type}: {count:,} 条")
    elif args.keyword:
        results = search_by_keyword(
            keyword=args.keyword,
            db_path=args.db,
            limit=args.limit,
            sender=args.sender,
            start_date=args.start_date,
            end_date=args.end_date
        )
        
        if results:
            print(f"找到 {len(results)} 条记录:")
            print("=" * 80)
            for i, (timestamp, sender, receiver, content) in enumerate(results, 1):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%Y-%m-%d %I:%M:%S %p")
                except:
                    time_str = timestamp
                
                print(f"{i}. {time_str} {sender} -> {receiver}:")
                print(f"   {content}")
                print()
            
            if args.export:
                export_to_text(results, args.export)
        else:
            print("未找到匹配的记录")
    else:
        parser.print_help()