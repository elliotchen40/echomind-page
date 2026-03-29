#!/usr/bin/env python3
"""
分析导入失败的具体行
"""

import re

def find_failed_lines(file_path, start_line=300000, sample_size=1000):
    """查找导入失败的行"""
    print(f"分析文件: {file_path}")
    print(f"从第 {start_line} 行开始，分析 {sample_size} 行\n")
    
    # 标准格式模式
    standard_pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
    
    failed_lines = []
    total_checked = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line_num < start_line:
                continue
            
            if total_checked >= sample_size:
                break
            
            line = line.strip()
            total_checked += 1
            
            if not line:
                continue
            
            # 检查是否能匹配标准格式
            match = re.match(standard_pattern, line)
            if not match:
                failed_lines.append((line_num, line))
    
    print(f"检查了 {total_checked} 行")
    print(f"发现 {len(failed_lines)} 行无法匹配标准格式 ({len(failed_lines)/total_checked*100:.1f}%)\n")
    
    if failed_lines:
        print("=== 无法解析的行示例 ===")
        for i, (line_num, line) in enumerate(failed_lines[:20], 1):
            print(f"{i}. 第 {line_num} 行: {line[:100]}...")
        
        # 分析失败行的常见模式
        print("\n=== 失败行模式分析 ===")
        patterns = {}
        
        for line_num, line in failed_lines[:50]:
            # 尝试识别常见模式
            if ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    left_part = parts[0]
                    # 检查左边部分是否包含时间信息
                    if re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', left_part):
                        pattern = "时间在发送者中"
                    elif '(' in left_part and ')' in left_part:
                        pattern = "括号格式但时间格式错误"
                    else:
                        pattern = "简单冒号分隔"
                else:
                    pattern = "无冒号分隔"
            else:
                pattern = "无冒号"
            
            patterns[pattern] = patterns.get(pattern, 0) + 1
        
        for pattern, count in patterns.items():
            print(f"{pattern}: {count} 行")
    
    return failed_lines

def check_file_encoding_issues(file_path, sample_lines=50):
    """检查文件编码问题"""
    print(f"\n=== 检查文件编码问题 ===")
    
    with open(file_path, 'rb') as f:
        raw_data = f.read(1000)  # 读取前1000字节
    
    print(f"文件前1000字节的十六进制表示:")
    hex_str = raw_data.hex()
    for i in range(0, len(hex_str), 32):
        print(f"  {hex_str[i:i+32]}")
    
    # 尝试用不同编码解码
    encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'latin1']
    
    print(f"\n尝试用不同编码解码前{sample_lines}行:")
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                lines = []
                for i in range(sample_lines):
                    line = f.readline()
                    if not line:
                        break
                    lines.append(line.strip())
            
            # 检查是否能正确解析
            valid_count = 0
            standard_pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
            
            for line in lines:
                if re.match(standard_pattern, line):
                    valid_count += 1
            
            print(f"{encoding}: {valid_count}/{len(lines)} 行有效 ({valid_count/len(lines)*100:.1f}%)")
            
        except UnicodeDecodeError:
            print(f"{encoding}: 解码失败")
        except Exception as e:
            print(f"{encoding}: 错误: {e}")

if __name__ == "__main__":
    file_path = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    # 分析导入失败的行（从大约30万行开始）
    failed = find_failed_lines(file_path, start_line=300000, sample_size=2000)
    
    # 检查编码问题
    check_file_encoding_issues(file_path)