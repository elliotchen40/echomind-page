#!/bin/bash

# 每日记忆整理脚本
# 每天晚上1点运行，将当天重要记忆提炼到MEMORY.md

set -e

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
MEMORY_FILE="$WORKSPACE/MEMORY.md"
LOG_FILE="/var/log/memory_consolidation.log"

# 创建日志目录
mkdir -p /var/log

echo "=== 记忆整理开始: $(date) ===" >> "$LOG_FILE"

# 检查文件是否存在
if [ ! -d "$MEMORY_DIR" ]; then
    echo "错误: memory目录不存在: $MEMORY_DIR" >> "$LOG_FILE"
    exit 1
fi

if [ ! -f "$MEMORY_FILE" ]; then
    echo "错误: MEMORY.md文件不存在: $MEMORY_FILE" >> "$LOG_FILE"
    exit 1
fi

# 获取昨天的日期（因为晚上1点整理的是前一天的记忆）
YESTERDAY=$(date -d "yesterday" +"%Y-%m-%d")
DAILY_FILE="$MEMORY_DIR/$YESTERDAY.md"

echo "整理日期: $YESTERDAY" >> "$LOG_FILE"
echo "每日记忆文件: $DAILY_FILE" >> "$LOG_FILE"

# 检查每日记忆文件是否存在
if [ ! -f "$DAILY_FILE" ]; then
    echo "警告: 每日记忆文件不存在: $DAILY_FILE" >> "$LOG_FILE"
    echo "可能原因: 1) 当天没有对话 2) 文件尚未创建" >> "$LOG_FILE"
    exit 0
fi

# 创建临时整理文件
TEMP_FILE="/tmp/memory_consolidation_$YESTERDAY.md"

# 从每日文件中提取重要内容（这里可以根据需要调整提取逻辑）
echo "# 记忆整理: $YESTERDAY" > "$TEMP_FILE"
echo "## 整理时间: $(date)" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 提取重要部分（示例逻辑，可以根据需要调整）
grep -E "^(###|##|重要|关键|承诺|工作|情感)" "$DAILY_FILE" >> "$TEMP_FILE" 2>/dev/null || true

# 检查是否提取到内容
if [ ! -s "$TEMP_FILE" ] || [ $(wc -l < "$TEMP_FILE") -le 3 ]; then
    echo "警告: 没有提取到重要内容，可能当天没有重要对话" >> "$LOG_FILE"
    rm -f "$TEMP_FILE"
    exit 0
fi

echo "" >> "$TEMP_FILE"
echo "---" >> "$TEMP_FILE"
echo "" >> "$TEMP_FILE"

# 将整理内容追加到MEMORY.md
cat "$TEMP_FILE" >> "$MEMORY_FILE"

# 记录整理结果
LINES_ADDED=$(wc -l < "$TEMP_FILE")
echo "整理完成: 添加了 $LINES_ADDED 行到 MEMORY.md" >> "$LOG_FILE"
echo "整理内容预览:" >> "$LOG_FILE"
head -20 "$TEMP_FILE" >> "$LOG_FILE"

# 清理临时文件
rm -f "$TEMP_FILE"

echo "=== 记忆整理结束: $(date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 备份MEMORY.md文件
BACKUP_DIR="/root/.openclaw/mnt/sdb1/fanny2_backup/memory"
if [ -d "$BACKUP_DIR" ]; then
    cp "$MEMORY_FILE" "$BACKUP_DIR/MEMORY_$(date +%Y%m%d_%H%M%S).md"
    echo "MEMORY.md已备份到: $BACKUP_DIR" >> "$LOG_FILE"
fi

exit 0