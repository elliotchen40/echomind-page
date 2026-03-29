#!/usr/bin/env python3
"""
将项目清单.xlsx导入到SQLite数据库
"""
import pandas as pd
import sqlite3
import os

EXCEL_FILE = '/root/.openclaw/workspace/document/项目清单.xlsx'
DB_FILE = '/root/.openclaw/workspace/data/projects.db'
TABLE_NAME = 'projects'

def import_excel_to_sqlite():
    # 读取Excel文件
    print(f'读取Excel文件: {EXCEL_FILE}')
    df = pd.read_excel(EXCEL_FILE)
    print(f'Excel行数: {len(df)}')
    print(f'列名: {list(df.columns)}')
    
    # 连接数据库
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 清空现有数据（可选，注释掉则追加）
    # cursor.execute(f'DELETE FROM {TABLE_NAME}')
    
    # 插入数据
    for index, row in df.iterrows():
        # 将NaN替换为None
        values = [None if pd.isna(v) else v for v in row.values]
        placeholders = ','.join(['?' for _ in values])
        columns = ', '.join(df.columns)
        sql = f'INSERT INTO {TABLE_NAME} ({columns}) VALUES ({placeholders})'
        cursor.execute(sql, values)
    
    conn.commit()
    
    # 验证
    cursor.execute(f'SELECT COUNT(*) FROM {TABLE_NAME}')
    count = cursor.fetchone()[0]
    print(f'导入后数据库行数: {count}')
    
    conn.close()
    print('导入完成!')

if __name__ == '__main__':
    import_excel_to_sqlite()