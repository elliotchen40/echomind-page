#!/usr/bin/env python3
"""
调试源文件，查看真实内容
"""

def debug_source_file():
    """调试源文件"""
    source_file = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    print("=" * 80)
    print("源文件内容调试")
    print("=" * 80)
    
    with open(source_file, 'r', encoding='utf-8') as f:
        # 读取前50行
        print("\n前50行内容:")
        print("-" * 40)
        
        for i in range(1, 51):
            line = f.readline().rstrip('\n')
            print(f"{i:3}: {line}")
        
        print("\n" + "=" * 80)
        print("格式分析:")
        print("=" * 80)
        
        # 回到文件开头
        f.seek(0)
        
        # 分析前100行的格式
        pattern_counts = {
            'standard': 0,  # 标准格式: 发送者 (时间):内容
            'no_time': 0,   # 没有时间
            'no_colon': 0,  # 没有冒号
            'other': 0      # 其他格式
        }
        
        for i in range(100):
            line = f.readline().rstrip('\n')
            
            # 检查标准格式
            if '):' in line and '(' in line.split('):')[0]:
                pattern_counts['standard'] += 1
            elif ':' in line:
                pattern_counts['no_time'] += 1
            elif '(' in line and ')' in line:
                pattern_counts['no_colon'] += 1
            else:
                pattern_counts['other'] += 1
        
        print(f"\n前100行格式分布:")
        for pattern, count in pattern_counts.items():
            print(f"  {pattern}: {count} 行 ({count/100*100:.1f}%)")
        
        # 检查特定关键词
        print(f"\n关键词检查:")
        f.seek(0)
        
        keywords = ['文剑', '项目', '会议', 'Fanny', 'EC', '微信']
        keyword_counts = {k: 0 for k in keywords}
        
        # 检查前1000行
        for i in range(1000):
            line = f.readline()
            if not line:
                break
            
            for keyword in keywords:
                if keyword in line:
                    keyword_counts[keyword] += 1
        
        for keyword, count in keyword_counts.items():
            print(f"  '{keyword}': {count} 次")
        
        # 检查文件编码和特殊字符
        print(f"\n文件编码检查:")
        f.seek(0)
        
        # 读取前200个字符
        sample = f.read(200)
        
        print(f"  文件开头200字符:")
        print(f"  {repr(sample)}")
        
        # 检查是否有异常字符
        unusual_chars = []
        for char in sample:
            if ord(char) > 127 and char not in '中文标点等':
                unusual_chars.append(f"'{char}' (U+{ord(char):04X})")
        
        if unusual_chars:
            print(f"  发现异常字符: {', '.join(unusual_chars[:5])}")
        else:
            print(f"  字符编码正常")

if __name__ == "__main__":
    debug_source_file()