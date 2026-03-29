#!/usr/bin/env python3
"""
Excel文件内容查看器
使用office-document-specialist-suite技能查看Excel文件的实际内容
"""

import openpyxl
import pandas as pd
from datetime import datetime
import json
import os

class ExcelViewer:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.wb = None
        
    def open_file(self):
        """打开Excel文件"""
        print(f"📂 打开文件: {os.path.basename(self.excel_path)}")
        print(f"📏 文件大小: {os.path.getsize(self.excel_path):,} bytes")
        
        try:
            self.wb = openpyxl.load_workbook(self.excel_path, read_only=True, data_only=True)
            print(f"✅ 文件打开成功")
            return True
        except Exception as e:
            print(f"❌ 打开文件失败: {e}")
            return False
    
    def show_sheet_overview(self):
        """显示工作表概览"""
        if not self.wb:
            return
        
        print(f"\n📊 工作表概览")
        print("=" * 80)
        
        for i, sheet_name in enumerate(self.wb.sheetnames, 1):
            ws = self.wb[sheet_name]
            print(f"\n{i}. 📋 工作表: {sheet_name}")
            print(f"   📈 数据范围: A1:{openpyxl.utils.get_column_letter(ws.max_column)}{ws.max_row}")
            print(f"   📊 数据量: {ws.max_row - 1} 行 × {ws.max_column} 列")
            
            # 显示列标题
            if ws.max_row >= 1:
                headers = []
                for cell in ws[1]:
                    value = cell.value
                    if value is None:
                        value = f"Column_{cell.column}"
                    headers.append(str(value))
                
                print(f"   🏷️  列标题 ({len(headers)}列):")
                for j, header in enumerate(headers, 1):
                    print(f"      {j:2d}. {header}")
    
    def show_sample_data(self, sheet_name, rows=10, cols=10):
        """显示样本数据"""
        if not self.wb:
            return
        
        print(f"\n📋 工作表: {sheet_name} - 样本数据")
        print("=" * 80)
        
        ws = self.wb[sheet_name]
        
        # 获取列标题
        headers = []
        if ws.max_row >= 1:
            for cell in ws[1]:
                value = cell.value
                if value is None:
                    value = f"Column_{cell.column}"
                headers.append(str(value))
        
        # 显示表格格式的数据
        print("\n" + "─" * 100)
        
        # 显示列标题
        header_line = "│ "
        for i in range(min(cols, len(headers))):
            header = headers[i][:15]  # 截断长标题
            header_line += f"{header:15} │ "
        print(header_line)
        print("├" + "─" * 98 + "┤")
        
        # 显示数据行
        for row_idx in range(2, min(rows + 2, ws.max_row + 1)):
            row_line = "│ "
            for col_idx in range(1, min(cols + 1, ws.max_column + 1)):
                cell = ws.cell(row=row_idx, column=col_idx)
                value = cell.value
                
                # 格式化值
                if value is None:
                    display_value = ""
                elif isinstance(value, datetime):
                    display_value = value.strftime("%Y-%m-%d")
                elif isinstance(value, float):
                    display_value = f"{value:,.2f}"
                elif isinstance(value, int):
                    display_value = f"{value:,}"
                elif isinstance(value, bool):
                    display_value = "是" if value else "否"
                else:
                    display_value = str(value)
                
                # 截断长文本
                display_value = display_value[:15]
                row_line += f"{display_value:15} │ "
            
            print(row_line)
        
        print("└" + "─" * 98 + "┘")
        
        # 显示统计信息
        print(f"\n📊 数据统计:")
        print(f"  显示行数: {min(rows, ws.max_row - 1)} / {ws.max_row - 1}")
        print(f"  显示列数: {min(cols, ws.max_column)} / {ws.max_column}")
        
        if ws.max_row > rows + 1:
            print(f"  ⚠️  还有 {ws.max_row - rows - 1} 行数据未显示")
        
        if ws.max_column > cols:
            print(f"  ⚠️  还有 {ws.max_column - cols} 列数据未显示")
    
    def analyze_data_types(self, sheet_name, sample_size=50):
        """分析数据类型"""
        if not self.wb:
            return
        
        print(f"\n🔍 工作表: {sheet_name} - 数据类型分析")
        print("=" * 80)
        
        ws = self.wb[sheet_name]
        
        if ws.max_row < 2:
            print("⚠️  无数据行")
            return
        
        # 获取列标题
        headers = []
        if ws.max_row >= 1:
            for cell in ws[1]:
                value = cell.value
                if value is None:
                    value = f"Column_{cell.column}"
                headers.append(str(value))
        
        print(f"\n📊 每列数据类型分析 (基于前{sample_size}行样本):")
        print("─" * 100)
        
        for col_idx, header in enumerate(headers, 1):
            # 收集样本数据
            sample_values = []
            for row_idx in range(2, min(sample_size + 2, ws.max_row + 1)):
                cell = ws.cell(row=row_idx, column=col_idx)
                sample_values.append(cell.value)
            
            # 统计数据类型
            type_stats = {
                "文本": 0,
                "整数": 0,
                "小数": 0,
                "日期": 0,
                "布尔": 0,
                "空值": 0
            }
            
            sample_count = 0
            for value in sample_values:
                sample_count += 1
                if value is None:
                    type_stats["空值"] += 1
                elif isinstance(value, str):
                    type_stats["文本"] += 1
                elif isinstance(value, int):
                    type_stats["整数"] += 1
                elif isinstance(value, float):
                    # 判断是整数还是小数
                    if value.is_integer():
                        type_stats["整数"] += 1
                    else:
                        type_stats["小数"] += 1
                elif isinstance(value, datetime):
                    type_stats["日期"] += 1
                elif isinstance(value, bool):
                    type_stats["布尔"] += 1
            
            # 确定主要数据类型
            if sample_count > 0:
                main_type = max(type_stats.items(), key=lambda x: x[1])[0]
                null_percent = (type_stats["空值"] / sample_count) * 100
                
                # 显示统计结果
                stats_str = []
                for type_name, count in type_stats.items():
                    if count > 0:
                        percent = (count / sample_count) * 100
                        stats_str.append(f"{type_name}:{percent:.1f}%")
                
                print(f"  {header:20} | 主要类型: {main_type:8} | 空值率: {null_percent:5.1f}% | 分布: {', '.join(stats_str)}")
    
    def show_summary_statistics(self, sheet_name):
        """显示汇总统计"""
        if not self.wb:
            return
        
        print(f"\n📈 工作表: {sheet_name} - 汇总统计")
        print("=" * 80)
        
        try:
            # 使用pandas进行统计
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name, nrows=1000)
            
            print(f"\n📊 基本统计:")
            print(f"  总行数: {len(df)}")
            print(f"  总列数: {len(df.columns)}")
            
            print(f"\n📋 列信息:")
            for i, col in enumerate(df.columns, 1):
                dtype = df[col].dtype
                null_count = df[col].isnull().sum()
                null_percent = (null_count / len(df)) * 100
                unique_count = df[col].nunique()
                
                print(f"  {i:2d}. {col:20} | 类型: {str(dtype):10} | 空值: {null_count:4d}({null_percent:5.1f}%) | 唯一值: {unique_count:4d}")
            
            print(f"\n🎯 数值列统计:")
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                for col in numeric_cols:
                    stats = df[col].describe()
                    print(f"  {col:20}: 均值={stats['mean']:.2f}, 标准差={stats['std']:.2f}, 最小={stats['min']:.2f}, 最大={stats['max']:.2f}")
            else:
                print("  无数值列")
            
            print(f"\n📅 日期列统计:")
            date_cols = df.select_dtypes(include=['datetime64']).columns
            if len(date_cols) > 0:
                for col in date_cols:
                    min_date = df[col].min()
                    max_date = df[col].max()
                    print(f"  {col:20}: 最早={min_date}, 最晚={max_date}")
            else:
                print("  无日期列")
                
        except Exception as e:
            print(f"⚠️  统计时出错: {e}")
    
    def export_preview(self, sheet_name, output_file=None):
        """导出数据预览"""
        if not self.wb:
            return
        
        print(f"\n💾 工作表: {sheet_name} - 数据预览导出")
        print("=" * 80)
        
        ws = self.wb[sheet_name]
        
        # 收集前100行数据
        preview_data = []
        headers = []
        
        # 获取列标题
        if ws.max_row >= 1:
            for cell in ws[1]:
                value = cell.value
                if value is None:
                    value = f"Column_{cell.column}"
                headers.append(str(value))
        
        # 收集数据
        for row_idx in range(2, min(102, ws.max_row + 1)):
            row_data = {}
            for col_idx, header in enumerate(headers, 1):
                if col_idx <= ws.max_column:
                    cell = ws.cell(row=row_idx, column=col_idx)
                    value = cell.value
                    
                    # 格式化值
                    if isinstance(value, datetime):
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                    elif isinstance(value, bool):
                        value = "是" if value else "否"
                    
                    row_data[header] = value
                else:
                    row_data[header] = None
            
            preview_data.append(row_data)
        
        # 创建预览文件
        preview = {
            "file_info": {
                "filename": os.path.basename(self.excel_path),
                "sheet_name": sheet_name,
                "total_rows": ws.max_row - 1,
                "total_columns": ws.max_column,
                "preview_rows": len(preview_data)
            },
            "headers": headers,
            "preview_data": preview_data
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(preview, f, ensure_ascii=False, indent=2, default=str)
            print(f"✅ 预览数据已导出到: {output_file}")
        
        return preview


def main():
    excel_path = "/root/.openclaw/workspace/document/2026年项目情况.xlsx"
    
    if not os.path.exists(excel_path):
        print(f"❌ 文件不存在: {excel_path}")
        return
    
    viewer = ExcelViewer(excel_path)
    
    if not viewer.open_file():
        return
    
    print("\n" + "=" * 80)
    print("📊 EXCEL文件内容查看器")
    print("=" * 80)
    
    # 1. 显示工作表概览
    viewer.show_sheet_overview()
    
    # 2. 对每个工作表显示样本数据
    for sheet_name in viewer.wb.sheetnames:
        # 显示样本数据
        viewer.show_sample_data(sheet_name, rows=15, cols=8)
        
        # 分析数据类型
        viewer.analyze_data_types(sheet_name, sample_size=100)
        
        # 显示汇总统计
        viewer.show_summary_statistics(sheet_name)
        
        # 导出预览
        preview_file = f"/root/.openclaw/workspace/document/{sheet_name}_preview.json"
        viewer.export_preview(sheet_name, preview_file)
        
        print("\n" + "=" * 80)
    
    print("\n🎯 查看完成！")
    print(f"📁 原始文件: {excel_path}")
    print(f"📄 预览文件: /root/.openclaw/workspace/document/*_preview.json")


if __name__ == "__main__":
    main()