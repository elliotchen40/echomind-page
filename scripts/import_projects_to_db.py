#!/usr/bin/env python3
"""
将项目清单Excel导入SQLite数据库
"""
import pandas as pd
import sqlite3
import os

EXCEL_FILE = '/root/.openclaw/workspace/document/项目清单.xlsx'
DB_FILE = '/root/.openclaw/workspace/data/projects.db'

def import_excel_to_sqlite():
    # 读取Excel文件
    print(f"读取Excel文件: {EXCEL_FILE}")
    df = pd.read_excel(EXCEL_FILE)
    print(f"共 {len(df)} 条记录")
    print(f"列名: {df.columns.tolist()}")
    
    # 连接数据库（如果不存在则创建）
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"已删除旧数据库: {DB_FILE}")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 创建表
    columns = df.columns.tolist()
    column_defs = []
    
    for col in columns:
        # 根据数据类型决定字段类型
        dtype = df[col].dtype
        if pd.api.types.is_integer_dtype(dtype):
            sql_type = 'INTEGER'
        elif pd.api.types.is_float_dtype(dtype):
            sql_type = 'REAL'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            sql_type = 'TEXT'
        else:
            sql_type = 'TEXT'
        column_defs.append(f'"{col}" {sql_type}')
    
    create_table_sql = f'''CREATE TABLE projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {', '.join(column_defs)}
    )'''
    
    print("\n创建表...")
    cursor.execute(create_table_sql)
    
    # 插入数据
    print("插入数据...")
    for idx, row in df.iterrows():
        cols_str = ', '.join([f'"{c}"' for c in columns])
        placeholders = ', '.join(['?'] * len(columns))
        insert_sql = f'INSERT INTO projects ({cols_str}) VALUES ({placeholders})'
        
        # 处理值
        values = []
        for val in row.values:
            if pd.isna(val):
                values.append(None)
            elif pd.api.types.is_datetime64_any_dtype(type(val)):
                values.append(str(val))
            else:
                values.append(val)
        
        try:
            cursor.execute(insert_sql, values)
        except Exception as e:
            print(f"插入第 {idx+1} 行时出错: {e}")
            print(f"值: {values}")
    
    conn.commit()
    
    # 验证
    cursor.execute("SELECT COUNT(*) FROM projects")
    count = cursor.fetchone()[0]
    print(f"\n导入完成！共导入 {count} 条记录")
    print(f"数据库位置: {DB_FILE}")
    
    # 显示表结构
    cursor.execute("PRAGMA table_info(projects)")
    print("\n表结构:")
    for col in cursor.fetchall():
        print(f"  {col[1]}: {col[2]}")
    
    conn.close()

if __name__ == '__main__':
    import_excel_to_sqlite()