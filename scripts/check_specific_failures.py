#!/usr/bin/env python3
"""
检查具体的失败行
"""

import re

def check_specific_lines():
    """检查具体的失败行"""
    file_path = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    print("检查具体的导入失败行...\n")
    
    # 查找可能失败的区域（从30万行开始）
    start_line = 300000
    check_count = 100
    
    failed_examples = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line_num < start_line:
                continue
            
            if len(failed_examples) >= check_count:
                break
            
            line = line.strip()
            if not line:
                continue
            
            # 标准格式
            standard_pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
            
            match = re.match(standard_pattern, line)
            if not match:
                # 尝试分析为什么失败
                failed_examples.append((line_num, line))
    
    print(f"在 {start_line:,} 行之后检查了 {len(failed_examples)} 个失败行\n")
    
    if failed_examples:
        print("=== 失败行分类分析 ===")
        
        categories = {
            '缺少括号': [],
            '时间格式错误': [],
            '缺少冒号': [],
            '其他问题': []
        }
        
        for line_num, line in failed_examples[:50]:  # 分析前50个
            # 检查括号
            if '(' not in line or ')' not in line:
                categories['缺少括号'].append((line_num, line))
                continue
            
            # 检查时间格式
            time_patterns = [
                r'\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM)',
                r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}',
                r'\d{4}/\d{2}/\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM)',
                r'\d{4}年\d{2}月\d{2}日 \d{1,2}:\d{2}:\d{2}'
            ]
            
            has_time = False
            for pattern in time_patterns:
                if re.search(pattern, line):
                    has_time = True
                    break
            
            if not has_time:
                categories['时间格式错误'].append((line_num, line))
                continue
            
            # 检查冒号
            if ':' not in line:
                categories['缺少冒号'].append((line_num, line))
                continue
            
            categories['其他问题'].append((line_num, line))
        
        # 输出分类结果
        for category, items in categories.items():
            if items:
                print(f"\n{category} ({len(items)} 行):")
                for i, (line_num, line) in enumerate(items[:3], 1):
                    print(f"  {i}. 第 {line_num} 行: {line[:80]}...")
        
        # 显示一些具体的修复示例
        print("\n=== 修复示例 ===")
        
        for line_num, line in failed_examples[:5]:
            print(f"\n原始行 {line_num}: {line}")
            
            # 尝试修复
            fixed = try_fix_line(line)
            if fixed:
                print(f"修复建议: {fixed}")
            else:
                print("无法自动修复")

def try_fix_line(line):
    """尝试修复失败的行"""
    
    # 情况1: 有括号但格式不对
    if '(' in line and ')' in line:
        # 提取括号内容
        start = line.find('(')
        end = line.find(')')
        if start < end:
            inside = line[start+1:end]
            
            # 检查是否是时间
            time_patterns = [
                (r'(\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2}) (AM|PM)', "%Y-%m-%d %I:%M:%S %p"),
                (r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', "%Y-%m-%d %H:%M:%S"),
                (r'(\d{4}/\d{2}/\d{2} \d{1,2}:\d{2}:\d{2}) (AM|PM)', "%Y/%m/%d %I:%M:%S %p"),
            ]
            
            for pattern, time_format in time_patterns:
                match = re.match(pattern, inside.strip())
                if match:
                    # 尝试标准化时间
                    from datetime import datetime
                    try:
                        if len(match.groups()) == 2:
                            time_str = f"{match.group(1)} {match.group(2)}"
                        else:
                            time_str = match.group(1)
                        
                        # 这里可以添加时间转换逻辑
                        return f"标准格式: 发送者 ({time_str}):内容"
                    except:
                        pass
    
    # 情况2: 没有括号但有时间
    time_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2} \d{1,2}:\d{2}:\d{2})', line)
    if time_match:
        time_str = time_match.group(1)
        # 假设时间前面是发送者
        parts = line.split(time_str)
        if len(parts) == 2:
            sender = parts[0].strip()
            rest = parts[1].strip()
            if rest.startswith(':'):
                content = rest[1:].strip()
                return f"{sender} ({time_str}):{content}"
    
    return None

def check_file_integrity():
    """检查文件完整性"""
    print("\n=== 检查文件完整性 ===")
    
    file_path = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    # 检查文件编码
    try:
        with open(file_path, 'rb') as f:
            header = f.read(100)
        
        print(f"文件头 (十六进制): {header[:50].hex()}")
        print(f"文件头 (ASCII): {header[:50]}")
        
        # 检查BOM
        if header.startswith(b'\xef\xbb\xbf'):
            print("编码: UTF-8 with BOM")
        elif header.startswith(b'\xff\xfe'):
            print("编码: UTF-16 LE")
        elif header.startswith(b'\xfe\xff'):
            print("编码: UTF-16 BE")
        else:
            print("编码: 可能是UTF-8 without BOM")
    
    except Exception as e:
        print(f"检查文件头失败: {e}")
    
    # 检查文件结尾
    try:
        with open(file_path, 'rb') as f:
            f.seek(-100, 2)  # 跳到文件末尾前100字节
            footer = f.read()
        
        print(f"\n文件尾 (最后100字节):")
        try:
            print(footer.decode('utf-8', errors='replace'))
        except:
            print("无法解码为UTF-8")

    except Exception as e:
        print(f"检查文件尾失败: {e}")

if __name__ == "__main__":
    check_specific_lines()
    check_file_integrity()