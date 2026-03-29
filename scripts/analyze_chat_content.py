#!/usr/bin/env python3
"""
详细分析聊天记录内容
"""

def analyze_chat_content():
    """分析聊天记录内容"""
    source_file = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    print("=" * 80)
    print("聊天记录内容详细分析")
    print("=" * 80)
    
    with open(source_file, 'r', encoding='utf-8') as f:
        # 1. 文件基本信息
        print("\n1. 文件基本信息:")
        
        # 读取所有行
        lines = f.readlines()
        total_lines = len(lines)
        
        print(f"   总行数: {total_lines:,}")
        
        # 2. 分析前50行
        print("\n2. 前50行详细内容:")
        print("-" * 40)
        
        for i in range(min(50, total_lines)):
            line = lines[i].rstrip('\n')
            print(f"{i+1:3}: {line}")
        
        # 3. 格式分析
        print("\n3. 格式分析:")
        
        import re
        pattern = r'^(.+?) \((\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}:\d{2} (?:AM|PM))\):(.+)$'
        
        valid_count = 0
        invalid_samples = []
        
        # 检查前200行
        for i in range(min(200, total_lines)):
            line = lines[i].rstrip('\n')
            
            # 跳过空行
            if not line:
                continue
            
            # 跳过标题行
            if i == 0 and "微信聊天记录" in line:
                continue
            
            match = re.match(pattern, line)
            if match:
                valid_count += 1
            else:
                if len(invalid_samples) < 5:
                    invalid_samples.append((i+1, line))
        
        print(f"   前200行中有效格式: {valid_count} 行")
        print(f"   无效格式样本:")
        for line_num, content in invalid_samples:
            print(f"     第{line_num}行: {content[:60]}...")
        
        # 4. 内容关键词分析
        print("\n4. 关键词分析:")
        
        keywords = ['文剑', '项目', '会议', '合同', '预算', 
                   '财务', '工作', '问题', '解决', '安排']
        
        keyword_counts = {k: 0 for k in keywords}
        
        # 检查整个文件（抽样）
        sample_size = min(10000, total_lines)
        import random
        sample_indices = random.sample(range(total_lines), sample_size)
        
        for idx in sample_indices:
            line = lines[idx]
            for keyword in keywords:
                if keyword in line:
                    keyword_counts[keyword] += 1
        
        print(f"   随机抽样{sample_size:,}行的关键词出现次数:")
        for keyword in keywords:
            count = keyword_counts[keyword]
            percentage = count / sample_size * 100
            if count > 0:
                print(f"     '{keyword}': {count} 次 ({percentage:.2f}%)")
        
        # 5. 发送者分析
        print("\n5. 发送者分析:")
        
        senders = {}
        # 检查前1000行
        for i in range(min(1000, total_lines)):
            line = lines[i].rstrip('\n')
            match = re.match(pattern, line)
            if match:
                sender = match.group(1)
                senders[sender] = senders.get(sender, 0) + 1
        
        print(f"   前1000行中的发送者:")
        for sender, count in sorted(senders.items(), key=lambda x: x[1], reverse=True):
            percentage = count / sum(senders.values()) * 100
            print(f"     {sender}: {count} 次 ({percentage:.1f}%)")
        
        # 6. 内容类型分析
        print("\n6. 内容类型分析:")
        
        content_types = {
            'text': 0,
            'image': 0,
            'link': 0,
            'voice': 0,
            'video': 0,
            'other': 0
        }
        
        # 检查前500行
        for i in range(min(500, total_lines)):
            line = lines[i].rstrip('\n')
            match = re.match(pattern, line)
            if match:
                content = match.group(3)
                
                if '[图片]' in content:
                    content_types['image'] += 1
                elif '[链接]' in content:
                    content_types['link'] += 1
                elif '[语音]' in content:
                    content_types['voice'] += 1
                elif '[视频]' in content:
                    content_types['video'] += 1
                elif len(content.strip()) > 0:
                    content_types['text'] += 1
                else:
                    content_types['other'] += 1
        
        total_checked = sum(content_types.values())
        if total_checked > 0:
            print(f"   前500行内容类型分布:")
            for ctype, count in content_types.items():
                if count > 0:
                    percentage = count / total_checked * 100
                    print(f"     {ctype}: {count} 次 ({percentage:.1f}%)")
        
        # 7. 时间范围分析
        print("\n7. 时间范围分析:")
        
        timestamps = []
        # 检查前200行
        for i in range(min(200, total_lines)):
            line = lines[i].rstrip('\n')
            match = re.match(pattern, line)
            if match:
                timestamp = match.group(2)
                timestamps.append(timestamp)
        
        if timestamps:
            print(f"   时间范围: {timestamps[0]} 到 {timestamps[-1]}")
            
            # 提取年份
            years = {}
            for ts in timestamps:
                year = ts[:4]
                years[year] = years.get(year, 0) + 1
            
            print(f"   年份分布:")
            for year, count in sorted(years.items()):
                percentage = count / len(timestamps) * 100
                print(f"     {year}年: {count} 条 ({percentage:.1f}%)")
        
        # 8. 特殊内容检查
        print("\n8. 特殊内容检查:")
        
        special_patterns = [
            ('撤回', '撤回消息'),
            ('转账', '转账记录'),
            ('红包', '红包'),
            ('位置', '位置分享'),
            ('名片', '名片分享'),
            ('文件', '文件传输')
        ]
        
        for pattern, description in special_patterns:
            count = 0
            # 检查前1000行
            for i in range(min(1000, total_lines)):
                if pattern in lines[i]:
                    count += 1
            
            if count > 0:
                print(f"   {description}: {count} 次")

if __name__ == "__main__":
    analyze_chat_content()