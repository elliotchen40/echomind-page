#!/usr/bin/env python3
"""
验证导入结果
"""

import sqlite3
import os

def verify_import():
    """验证导入结果"""
    db_path = "/root/.openclaw/workspace/data/chat_history.db"
    file_path = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    print("=" * 80)
    print("导入结果验证")
    print("=" * 80)
    
    # 1. 检查文件基本信息
    print("\n1. 原始文件信息:")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)
        file_size = os.path.getsize(file_path) / (1024*1024)  # MB
        print(f"   行数: {total_lines:,}")
        print(f"   大小: {file_size:.1f} MB")
    except Exception as e:
        print(f"   读取文件失败: {e}")
        return
    
    # 2. 检查数据库基本信息
    print("\n2. 数据库信息:")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 记录数
        cursor.execute("SELECT COUNT(*) FROM chat_history")
        db_count = cursor.fetchone()[0]
        
        # 时间范围
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM chat_history")
        min_time, max_time = cursor.fetchone()
        
        # 发送者统计
        cursor.execute("SELECT COUNT(DISTINCT sender) FROM chat_history")
        sender_count = cursor.fetchone()[0]
        
        db_size = os.path.getsize(db_path) / (1024*1024)  # MB
        
        print(f"   记录数: {db_count:,}")
        print(f"   数据库大小: {db_size:.1f} MB")
        print(f"   时间范围: {min_time} 到 {max_time}")
        print(f"   发送者数量: {sender_count}")
        
        # 导入率
        import_rate = db_count / total_lines * 100
        print(f"   导入率: {import_rate:.1f}%")
        print(f"   缺失记录: {total_lines - db_count:,} 条")
        
    except Exception as e:
        print(f"   读取数据库失败: {e}")
        return
    
    # 3. 检查重复记录
    print("\n3. 重复记录检查:")
    try:
        cursor.execute("""
            SELECT COUNT(*) as duplicate_groups, SUM(cnt-1) as duplicate_records
            FROM (
                SELECT COUNT(*) as cnt 
                FROM chat_history 
                GROUP BY timestamp, sender, content 
                HAVING cnt > 1
            )
        """)
        dup_groups, dup_records = cursor.fetchone()
        
        if dup_groups == 0:
            print(f"   ✓ 无重复记录")
        else:
            print(f"   ⚠ 发现 {dup_groups} 组重复记录，共 {dup_records} 条")
            print(f"     重复率: {dup_records/db_count*100:.3f}%")
    
    except Exception as e:
        print(f"   检查重复记录失败: {e}")
    
    # 4. 检查索引
    print("\n4. 索引检查:")
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='chat_history'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        required_indexes = ['idx_timestamp', 'idx_sender', 'idx_content']
        missing = [idx for idx in required_indexes if idx not in indexes]
        
        if not missing:
            print(f"   ✓ 所有必要索引已创建: {', '.join(indexes)}")
        else:
            print(f"   ⚠ 缺失索引: {', '.join(missing)}")
            print(f"     现有索引: {', '.join(indexes)}")
    
    except Exception as e:
        print(f"   检查索引失败: {e}")
    
    # 5. 数据质量检查
    print("\n5. 数据质量检查:")
    try:
        # 检查空内容
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE content = '' OR content IS NULL")
        empty_content = cursor.fetchone()[0]
        
        # 检查无效时间
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE timestamp NOT LIKE '____-__-__%'")
        invalid_time = cursor.fetchone()[0]
        
        print(f"   空内容记录: {empty_content} 条")
        print(f"   无效时间格式: {invalid_time} 条")
        
        if empty_content == 0 and invalid_time == 0:
            print(f"   ✓ 数据质量良好")
        else:
            print(f"   ⚠ 发现数据质量问题")
    
    except Exception as e:
        print(f"   数据质量检查失败: {e}")
    
    # 6. 测试查询功能
    print("\n6. 查询功能测试:")
    try:
        # 测试关键词搜索
        test_keyword = "项目"
        cursor.execute("SELECT COUNT(*) FROM chat_history WHERE content LIKE ?", (f"%{test_keyword}%",))
        test_count = cursor.fetchone()[0]
        
        print(f"   测试关键词 '{test_keyword}': 找到 {test_count} 条记录")
        
        if test_count > 0:
            print(f"   ✓ 查询功能正常")
        else:
            print(f"   ⚠ 未找到测试关键词记录（可能数据不包含该关键词）")
    
    except Exception as e:
        print(f"   查询测试失败: {e}")
    
    conn.close()
    
    # 7. 总体评估
    print("\n7. 总体评估:")
    
    if import_rate >= 98.0:
        print(f"   ✓ 导入成功 (导入率: {import_rate:.1f}%)")
    elif import_rate >= 95.0:
        print(f"   ⚠ 导入基本成功 (导入率: {import_rate:.1f}%)")
    else:
        print(f"   ✗ 导入不完整 (导入率: {import_rate:.1f}%)")
    
    if dup_groups == 0:
        print(f"   ✓ 无重复记录")
    else:
        print(f"   ⚠ 有重复记录需要处理")
    
    print(f"\n数据库已就绪，可以使用查询工具进行搜索。")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    verify_import()