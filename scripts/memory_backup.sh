#!/bin/bash
# 记忆文件定时备份脚本
# 备份workspace中的重要文件到指定目录

# 配置
BACKUP_ROOT="/root/.openclaw/mnt/sdb1/fanny2_backup/memory"
SOURCE_DIR="/root/.openclaw/workspace"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

# 要备份的文件列表
FILES_TO_BACKUP=(
    "AGENTS.md"
    "SOUL.md" 
    "USER.md"
    "TOOLS.md"
    "MEMORY.md"
    "memory"
)

echo "=== 开始记忆文件备份: $(date) ==="

# 1. 创建备份目录
mkdir -p "$BACKUP_DIR"
if [ $? -ne 0 ]; then
    echo "错误: 无法创建备份目录 $BACKUP_DIR"
    exit 1
fi
echo "备份目录: $BACKUP_DIR"

# 2. 备份单个文件（特别处理MEMORY.md）
for file in "${FILES_TO_BACKUP[@]}"; do
    SOURCE_PATH="$SOURCE_DIR/$file"
    
    if [ -e "$SOURCE_PATH" ]; then
        if [ -f "$SOURCE_PATH" ]; then
            # 备份单个文件
            echo "正在备份: $file"
            echo "  源: $SOURCE_PATH"
            echo "  目标: $BACKUP_DIR/"
            
            # 特别处理MEMORY.md，确保备份成功
            if [ "$file" = "MEMORY.md" ]; then
                echo "  特别处理: MEMORY.md"
                cp -v "$SOURCE_PATH" "$BACKUP_DIR/" 2>&1 | while read line; do echo "  $line"; done
                if [ $? -eq 0 ]; then
                    echo "✓ 备份文件: $file (特别处理成功)"
                    # 验证文件确实被复制
                    if [ -f "$BACKUP_DIR/$file" ]; then
                        echo "  验证: 文件已存在 ($(ls -la "$BACKUP_DIR/$file" | awk '{print $5}')字节)"
                    else
                        echo "  警告: 文件复制但目标不存在"
                    fi
                else
                    echo "❌ 备份失败: $file (错误代码: $?)"
                fi
            else
                if cp "$SOURCE_PATH" "$BACKUP_DIR/"; then
                    echo "✓ 备份文件: $file"
                else
                    echo "❌ 备份失败: $file (错误代码: $?)"
                fi
            fi
        elif [ -d "$SOURCE_PATH" ]; then
            # 备份目录
            if cp -r "$SOURCE_PATH" "$BACKUP_DIR/"; then
                echo "✓ 备份目录: $file"
            else
                echo "❌ 备份失败: $file (目录)"
            fi
        fi
    else
        echo "⚠️ 文件不存在: $file"
    fi
    echo ""
done

# 3. 创建备份信息文件
BACKUP_INFO="$BACKUP_DIR/backup_info.txt"
cat > "$BACKUP_INFO" << EOF
备份时间: $(date)
备份目录: $BACKUP_DIR
源目录: $SOURCE_DIR
备份文件列表:
$(for file in "${FILES_TO_BACKUP[@]}"; do echo "  - $file"; done)

磁盘使用情况:
$(df -h /root/.openclaw/mnt/sdb1/fanny2_backup 2>/dev/null || echo "无法获取磁盘信息")

备份文件统计:
$(find "$BACKUP_DIR" -type f | wc -l) 个文件
$(du -sh "$BACKUP_DIR" 2>/dev/null || echo "无法计算大小")
EOF

echo "备份信息已保存到: $BACKUP_INFO"

# 4. 清理旧备份（保留最近30天的备份）
echo "=== 清理旧备份 ==="
find "$BACKUP_ROOT" -type d -name "202*" -mtime +30 -exec rm -rf {} \; 2>/dev/null
echo "已清理30天前的备份"

# 5. 显示备份结果
echo "=== 备份完成 ==="
echo "备份位置: $BACKUP_DIR"
echo "备份时间: $(date)"
echo "备份大小: $(du -sh "$BACKUP_DIR" 2>/dev/null || echo "未知")"
echo "备份文件数: $(find "$BACKUP_DIR" -type f | wc -l)"

# 6. 记录到日志
LOG_FILE="/var/log/memory_backup.log"
echo "[$(date)] 备份完成: $BACKUP_DIR ($(find "$BACKUP_DIR" -type f | wc -l)个文件)" >> "$LOG_FILE"