#!/usr/bin/env python3
"""
Excel文件转数据库导入脚本
将Excel文件转换为SQLite数据库或生成SQL导入脚本
"""

import openpyxl
import sqlite3
import csv
import json
import os
from datetime import datetime

class ExcelToDatabase:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.wb = None
        self.analysis_results = {}
        
    def analyze_excel(self):
        """分析Excel文件结构"""
        print(f"正在分析Excel文件: {self.excel_path}")
        
        # 使用openpyxl读取Excel文件
        self.wb = openpyxl.load_workbook(self.excel_path, read_only=True, data_only=True)
        
        analysis = {
            "file_info": {
                "filename": os.path.basename(self.excel_path),
                "size_bytes": os.path.getsize(self.excel_path),
                "sheet_count": len(self.wb.sheetnames),
                "sheets": self.wb.sheetnames
            },
            "sheets": {}
        }
        
        for sheet_name in self.wb.sheetnames:
            print(f"\n分析工作表: {sheet_name}")
            ws = self.wb[sheet_name]
            
            # 获取最大行和列
            max_row = ws.max_row
            max_column = ws.max_column
            
            # 获取列标题
            headers = []
            if max_row >= 1:
                for cell in ws[1]:
                    value = cell.value
                    if value is None or str(value).strip() == "":
                        value = f"column_{cell.column}"
                    headers.append(str(value).strip())
            
            # 分析数据类型和样本数据
            data_types = {}
            sample_data = []
            
            # 读取前10行数据作为样本
            sample_rows = min(20, max_row)
            for row_idx in range(2, min(sample_rows + 1, max_row + 1)):
                row_data = {}
                for col_idx, header in enumerate(headers, 1):
                    cell = ws.cell(row=row_idx, column=col_idx)
                    row_data[header] = cell.value
                sample_data.append(row_data)
            
            # 分析每列的数据类型
            for header in headers:
                values = [row.get(header) for row in sample_data if row.get(header) is not None]
                
                if not values:
                    data_types[header] = {"type": "unknown", "nullable": True}
                    continue
                
                # 判断数据类型
                type_counts = {
                    "string": 0,
                    "integer": 0,
                    "float": 0,
                    "datetime": 0,
                    "boolean": 0
                }
                
                for val in values:
                    if isinstance(val, str):
                        type_counts["string"] += 1
                    elif isinstance(val, int):
                        type_counts["integer"] += 1
                    elif isinstance(val, float):
                        type_counts["float"] += 1
                    elif isinstance(val, datetime):
                        type_counts["datetime"] += 1
                    elif isinstance(val, bool):
                        type_counts["boolean"] += 1
                
                # 确定主要数据类型
                main_type = max(type_counts.items(), key=lambda x: x[1])[0]
                
                # 检查是否可为空
                nullable = any(row.get(header) is None for row in sample_data)
                
                data_types[header] = {
                    "type": main_type,
                    "nullable": nullable,
                    "sample_values": values[:3] if values else []
                }
            
            analysis["sheets"][sheet_name] = {
                "headers": headers,
                "total_rows": max_row - 1,  # 减去标题行
                "total_columns": max_column,
                "data_types": data_types,
                "sample_data": sample_data[:5]  # 只保留前5行样本
            }
        
        self.analysis_results = analysis
        return analysis
    
    def generate_sql_schema(self, output_file=None):
        """生成SQL表结构"""
        if not self.analysis_results:
            self.analyze_excel()
        
        sql_statements = []
        
        for sheet_name, sheet_data in self.analysis_results["sheets"].items():
            table_name = self._sanitize_table_name(sheet_name)
            
            # 生成CREATE TABLE语句
            columns = []
            for header in sheet_data["headers"]:
                data_type = sheet_data["data_types"][header]["type"]
                nullable = sheet_data["data_types"][header]["nullable"]
                
                # 映射到SQL数据类型
                sql_type = self._map_to_sql_type(data_type)
                column_name = self._sanitize_column_name(header)
                
                null_constraint = "NULL" if nullable else "NOT NULL"
                columns.append(f"    {column_name} {sql_type} {null_constraint}")
            
            create_table = f"CREATE TABLE {table_name} (\n"
            create_table += ",\n".join(columns)
            create_table += "\n);"
            
            sql_statements.append(create_table)
            
            # 生成INSERT语句示例
            if sheet_data["sample_data"]:
                insert_example = f"\n-- 示例数据插入 (工作表: {sheet_name})\n"
                column_names = [self._sanitize_column_name(h) for h in sheet_data["headers"]]
                insert_example += f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES\n"
                
                value_lines = []
                for row in sheet_data["sample_data"][:3]:  # 只取3行示例
                    values = []
                    for header in sheet_data["headers"]:
                        value = row.get(header)
                        if value is None:
                            values.append("NULL")
                        elif isinstance(value, str):
                            values.append(f"'{value.replace(\"'\", \"''\")}'")
                        elif isinstance(value, (int, float)):
                            values.append(str(value))
                        elif isinstance(value, datetime):
                            values.append(f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'")
                        elif isinstance(value, bool):
                            values.append("1" if value else "0")
                        else:
                            values.append(f"'{str(value)}'")
                    value_lines.append(f"    ({', '.join(values)})")
                
                insert_example += ",\n".join(value_lines) + ";"
                sql_statements.append(insert_example)
        
        sql_content = "\n\n".join(sql_statements)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(sql_content)
            print(f"SQL架构已保存到: {output_file}")
        
        return sql_content
    
    def export_to_csv(self, output_dir):
        """导出每个工作表为CSV文件"""
        if not self.wb:
            self.wb = openpyxl.load_workbook(self.excel_path, read_only=True, data_only=True)
        
        os.makedirs(output_dir, exist_ok=True)
        
        csv_files = []
        for sheet_name in self.wb.sheetnames:
            ws = self.wb[sheet_name]
            
            # 获取所有数据
            all_data = []
            headers = []
            
            # 读取标题行
            if ws.max_row >= 1:
                for cell in ws[1]:
                    value = cell.value
                    if value is None or str(value).strip() == "":
                        value = f"column_{cell.column}"
                    headers.append(str(value).strip())
            
            # 读取所有数据行
            for row in ws.iter_rows(min_row=2, values_only=True):
                row_dict = {}
                for i, value in enumerate(row):
                    if i < len(headers):
                        row_dict[headers[i]] = value
                all_data.append(row_dict)
            
            # 导出为CSV
            csv_filename = f"{self._sanitize_table_name(sheet_name)}.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                if headers:
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    writer.writerows(all_data)
            
            csv_files.append(csv_path)
            print(f"工作表 '{sheet_name}' 已导出为: {csv_path}")
        
        return csv_files
    
    def create_sqlite_database(self, db_path):
        """创建SQLite数据库并导入数据"""
        if not self.wb:
            self.wb = openpyxl.load_workbook(self.excel_path, read_only=True, data_only=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for sheet_name in self.wb.sheetnames:
            ws = self.wb[sheet_name]
            table_name = self._sanitize_table_name(sheet_name)
            
            # 获取标题行
            headers = []
            if ws.max_row >= 1:
                for cell in ws[1]:
                    value = cell.value
                    if value is None or str(value).strip() == "":
                        value = f"column_{cell.column}"
                    headers.append(str(value).strip())
            
            if not headers:
                continue
            
            # 创建表
            column_defs = []
            for header in headers:
                column_name = self._sanitize_column_name(header)
                column_defs.append(f"{column_name} TEXT")
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)});"
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            cursor.execute(create_sql)
            
            # 插入数据
            insert_sql = f"INSERT INTO {table_name} ({', '.join([self._sanitize_column_name(h) for h in headers])}) VALUES ({', '.join(['?'] * len(headers))})"
            
            data_rows = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                # 确保每行的值数量与标题数量一致
                row_values = list(row)[:len(headers)]
                if len(row_values) < len(headers):
                    row_values.extend([None] * (len(headers) - len(row_values)))
                data_rows.append(row_values)
            
            cursor.executemany(insert_sql, data_rows)
            print(f"工作表 '{sheet_name}' 已导入到表 '{table_name}'，共 {len(data_rows)} 行")
        
        conn.commit()
        conn.close()
        print(f"\nSQLite数据库已创建: {db_path}")
        
        # 显示表信息
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[t[0] for t in tables]}")
        conn.close()
    
    def _sanitize_table_name(self, name):
        """清理表名，使其符合SQL命名规范"""
        # 替换空格和特殊字符为下划线，转换为小写
        sanitized = name.replace(" ", "_").replace("-", "_").replace(".", "_")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
        return sanitized.lower()
    
    def _sanitize_column_name(self, name):
        """清理列名，使其符合SQL命名规范"""
        # 替换空格和特殊字符为下划线，转换为小写
        sanitized = str(name).replace(" ", "_").replace("-", "_").replace(".", "_")
        sanitized = "".join(c for c in sanitized if c.isalnum() or c == "_")
        return sanitized.lower()
    
    def _map_to_sql_type(self, data_type):
        """将数据类型映射到SQL类型"""
        type_map = {
            "string": "VARCHAR(255)",
            "integer": "INTEGER",
            "float": "DECIMAL(15,2)",
            "datetime": "DATETIME",
            "boolean": "BOOLEAN",
            "unknown": "VARCHAR(255)"
        }
        return type_map.get(data_type, "VARCHAR(255)")
    
    def save_analysis_report(self, output_file):
        """保存详细分析报告"""
        if not self.analysis_results:
            self.analyze_excel()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"详细分析报告已保存到: {output_file}")


def main():
    excel_path = "/root/.openclaw/workspace/document/2026年项目情况.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"错误: 文件不存在 - {excel_path}")
        return
    
    converter = ExcelToDatabase(excel_path)
    
    print("=" * 60)
    print("Excel文件数据库导入工具")
    print("=" * 60)
    
    # 1. 分析Excel文件
    analysis = converter.analyze_excel()
    
    print(f"\n文件信息:")
    print(f"  文件名: {analysis['file_info']['filename']}")
    print(f"  文件大小: {analysis['file_info']['size_bytes']} bytes")
    print(f"  工作表数量: {analysis['file_info']['sheet_count']}")
    
    # 2. 生成SQL架构
    sql_schema_file = "/root/.openclaw/workspace/document/excel_schema.sql"
    sql_content = converter.generate_sql_schema(sql_schema_file)
    
    # 3. 导出为CSV
    csv_dir = "/root/.openclaw/workspace/document/csv_export"
    csv_files = converter.export_to_csv(csv_dir)
    
    # 4. 创建SQLite数据库
    db_file = "/root/.openclaw/workspace/document/excel_data.db"
    converter.create_sqlite_database(db_file)
    
    # 5. 保存详细分析报告
    report_file = "/root/.openclaw/workspace/document/excel_analysis_report.json"
    converter.save_analysis_report(report_file)
    
    print("\n" + "=" * 60)
    print("处理完成！生成的文件:")
    print(f"  1. SQL架构文件: {sql_schema_file}")
    print(f"  2. CSV导出目录: {csv_dir}")
    print(f"  3. SQLite数据库: {db_file}")
    print(f"  4. 详细分析报告: {report_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()