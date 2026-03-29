#!/usr/bin/env python3
"""
内存使用分析
"""

import os
import psutil
import time

def analyze_memory_usage():
    """分析内存使用情况"""
    print("=" * 60)
    print("系统内存使用分析")
    print("=" * 60)
    
    # 获取内存信息
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    
    print(f"\n物理内存:")
    print(f"  总量: {memory.total / (1024**3):.1f} GB")
    print(f"  已用: {memory.used / (1024**3):.1f} GB ({memory.percent}%)")
    print(f"  可用: {memory.available / (1024**3):.1f} GB")
    print(f"  空闲: {memory.free / (1024**3):.1f} GB")
    
    print(f"\n交换空间:")
    print(f"  总量: {swap.total / (1024**3):.1f} GB")
    print(f"  已用: {swap.used / (1024**3):.1f} GB ({swap.percent}%)")
    print(f"  空闲: {swap.free / (1024**3):.1f} GB")
    
    # 检查进程内存使用
    print(f"\n当前进程内存使用:")
    current_process = psutil.Process()
    mem_info = current_process.memory_info()
    
    print(f"  RSS (常驻内存): {mem_info.rss / (1024**2):.1f} MB")
    print(f"  VMS (虚拟内存): {mem_info.vms / (1024**2):.1f} MB")
    
    # 检查Python进程
    print(f"\nPython进程内存使用:")
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            if 'python' in proc.info['name'].lower():
                mem = proc.info['memory_info']
                python_processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'rss_mb': mem.rss / (1024**2),
                    'vms_mb': mem.vms / (1024**2)
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    for proc in sorted(python_processes, key=lambda x: x['rss_mb'], reverse=True)[:5]:
        print(f"  PID {proc['pid']} ({proc['name']}): {proc['rss_mb']:.1f} MB RSS, {proc['vms_mb']:.1f} MB VMS")
    
    # 检查导入脚本的内存需求
    print(f"\n导入脚本内存需求估算:")
    file_path = "/root/.openclaw/mnt/sdb1/chat/聊天记录-1.txt"
    
    try:
        file_size = os.path.getsize(file_path) / (1024**2)  # MB
        print(f"  聊天记录文件大小: {file_size:.1f} MB")
        
        # 估算内存需求
        # 1. 文件读取缓冲区
        read_buffer = 10  # MB
        
        # 2. 解析后的数据结构
        with open(file_path, 'r', encoding='utf-8') as f:
            line_count = sum(1 for _ in f)
        
        print(f"  文件行数: {line_count:,}")
        
        # 每条记录大约占用内存估算
        # 假设每条记录平均100字节，加上Python对象开销约10倍
        record_size_estimate = 100 * 10  # 约1KB每条记录
        batch_size = 1000  # 默认批量大小
        
        batch_memory = batch_size * record_size_estimate / 1024  # KB
        total_memory_estimate = line_count * record_size_estimate / (1024**2)  # MB
        
        print(f"  单条记录内存估算: {record_size_estimate} 字节")
        print(f"  批量处理内存需求: {batch_memory:.1f} KB (每 {batch_size} 条)")
        print(f"  总内存需求估算: {total_memory_estimate:.1f} MB (全部记录)")
        
        # 3. 数据库内存
        db_path = "/root/.openclaw/workspace/data/chat_history.db"
        if os.path.exists(db_path):
            db_size = os.path.getsize(db_path) / (1024**2)  # MB
            print(f"  数据库文件大小: {db_size:.1f} MB")
            print(f"  数据库内存需求: {db_size * 2:.1f} MB (估算)")
        
        # 总内存需求
        total_required = read_buffer + batch_memory/1024 + db_size*2 if 'db_size' in locals() else read_buffer + batch_memory/1024
        print(f"\n  总内存需求估算: {total_required:.1f} MB")
        
        if total_required < memory.available / (1024**2):
            print(f"  ✓ 内存充足: 需要 {total_required:.1f} MB, 可用 {memory.available/(1024**2):.1f} MB")
        else:
            print(f"  ⚠ 内存可能不足: 需要 {total_required:.1f} MB, 可用 {memory.available/(1024**2):.1f} MB")
    
    except Exception as e:
        print(f"  分析文件失败: {e}")
    
    # 建议优化
    print(f"\n内存优化建议:")
    print(f"  1. 减小批量大小 (当前: 1000条)")
    print(f"  2. 使用生成器逐行处理，避免一次性加载")
    print(f"  3. 定期手动垃圾回收 (gc.collect())")
    print(f"  4. 使用更高效的数据结构")

def monitor_memory_trend():
    """监控内存趋势"""
    print(f"\n" + "=" * 60)
    print("内存使用趋势监控 (10秒)")
    print("=" * 60)
    
    samples = []
    for i in range(10):
        memory = psutil.virtual_memory()
        samples.append({
            'time': i,
            'used_gb': memory.used / (1024**3),
            'available_gb': memory.available / (1024**3),
            'percent': memory.percent
        })
        
        print(f"\r采样 {i+1}/10: 使用 {memory.percent}%, 可用 {memory.available/(1024**3):.1f} GB", end="")
        time.sleep(1)
    
    print(f"\n\n内存使用趋势:")
    print(f"  最高使用率: {max(s['percent'] for s in samples)}%")
    print(f"  最低使用率: {min(s['percent'] for s in samples)}%")
    print(f"  平均使用率: {sum(s['percent'] for s in samples)/len(samples):.1f}%")
    
    # 检查是否有内存泄漏趋势
    if samples[-1]['percent'] > samples[0]['percent'] + 5:
        print(f"  ⚠ 检测到内存使用上升趋势")
    else:
        print(f"  ✓ 内存使用稳定")

if __name__ == "__main__":
    try:
        import psutil
        analyze_memory_usage()
        monitor_memory_trend()
    except ImportError:
        print("需要安装psutil库: pip install psutil")
        print("\n使用系统命令检查内存:")
        os.system("free -h")
        os.system("cat /proc/meminfo | head -5")