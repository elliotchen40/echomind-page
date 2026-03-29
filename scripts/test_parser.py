#!/usr/bin/env python3
"""
测试解析逻辑
"""

import re

def test_parser():
    """测试解析逻辑"""
    print("=" * 80)
    print("解析逻辑测试")
    print("=" * 80)
    
    # 从import_memory_optimized.py中提取的解析逻辑
    pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
    
    # 测试用例
    test_cases = [
        # 标准格式
        "Fanny (2026-02-06 02:33:37 PM):不准",
        "EC (2023-12-12 09:15:00 AM):项目会议",
        
        # 源文件实际内容
        "Fanny - 微信聊天记录",
        "",
        "EC (2017-11-29 02:55:11 PM):[图片]",
        "Fanny (2017-11-29 02:55:11 PM):[图片]",
        
        # 可能的问题格式
        "文剑 (2023-01-01 10:00:00 AM):测试内容",
        "测试 (2023-01-01 10:00:00 AM):文剑说",
    ]
    
    print("\n测试解析逻辑:")
    for i, test_line in enumerate(test_cases, 1):
        print(f"\n测试 {i}: '{test_line}'")
        
        match = re.match(pattern, test_line)
        if match:
            sender = match.group(1)
            timestamp = match.group(2)
            content = match.group(3)
            
            print(f"  匹配成功!")
            print(f"  发送者: {sender}")
            print(f"  时间: {timestamp}")
            print(f"  内容: {content}")
            
            # 检查是否包含"文剑"
            if '文剑' in sender or '文剑' in content:
                print(f"  ⚠ 包含'文剑'!")
        else:
            print(f"  匹配失败")
    
    # 现在测试源文件的实际行
    print("\n" + "=" * 80)
    print("测试源文件实际内容")
    print("=" * 80)
    
    source_file = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    with open(source_file, 'r', encoding='utf-8') as f:
        # 跳过标题行
        title_line = f.readline().strip()
        print(f"文件标题: '{title_line}'")
        
        # 读取前10条实际记录
        print("\n前10条实际记录:")
        valid_count = 0
        total_tested = 0
        
        for i in range(1, 31):  # 多读一些，因为有空行
            line = f.readline().strip()
            if not line:
                continue
            
            total_tested += 1
            match = re.match(pattern, line)
            
            if match:
                valid_count += 1
                sender = match.group(1)
                content = match.group(3)
                
                print(f"{valid_count}. {sender}: {content[:50]}...")
                
                if '文剑' in content:
                    print(f"   ⚠ 包含'文剑'!")
            
            if valid_count >= 10:
                break
        
        print(f"\n统计: 测试{total_tested}行，有效{valid_count}条")
    
    # 检查是否有异常生成"文剑"的逻辑
    print("\n" + "=" * 80)
    print("检查可能的bug")
    print("=" * 80)
    
    # 检查import_memory_optimized.py中是否有生成"文剑"的代码
    import_script = "/root/.openclaw/workspace/scripts/import_memory_optimized.py"
    
    with open(import_script, 'r', encoding='utf-8') as f:
        content = f.read()
        
        # 检查是否有硬编码"文剑"
        if '文剑' in content:
            print("⚠ 在import_memory_optimized.py中发现'文剑'字符串")
            
            # 找到上下文
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if '文剑' in line:
                    print(f"  第{i+1}行: {line.strip()}")
        else:
            print("✓ import_memory_optimized.py中没有硬编码'文剑'")
        
        # 检查是否有异常的内容生成逻辑
        suspicious_patterns = [
            'content = "文剑"',
            'content = "文剑"',
            '文剑',
            '杜文剑'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in content:
                print(f"⚠ 发现可疑模式: '{pattern}'")

if __name__ == "__main__":
    test_parser()