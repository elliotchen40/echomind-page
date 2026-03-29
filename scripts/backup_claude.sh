#!/bin/bash
# Claude工作目录备份脚本
# 备份Linda2.0的工作目录和配置

BACKUP_DIR="/root/.openclaw/mnt/sdb1/fanny2_backup"
DATE=$(date +%Y%m%d_%H%M)

echo "开始备份Claude工作目录..."
echo "备份时间: $(date)"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份目录列表
BACKUP_PATHS=(
    "/root/.claude"      # Claude配置和缓存
    "/root/claude"       # Linda2.0工作目录
    "/root/.openclaw/workspace"  # Fanny的工作空间
)

# 执行备份
for path in "${BACKUP_PATHS[@]}"; do
    if [ -d "$path" ]; then
        echo "备份: $path"
        tar -czf "$BACKUP_DIR/claude_backup_${DATE}.tar.gz" -C / "$(echo $path | sed 's|^/||')"
    else
        echo "警告: 目录不存在: $path"
    fi
done

echo "备份完成!"
echo "备份文件: $BACKUP_DIR/claude_backup_${DATE}.tar.gz"
ls -lh "$BACKUP_DIR/claude_backup_${DATE}.tar.gz" 2>/dev/null || echo "备份文件未创建"

# 清理旧备份（保留最近7天）
find "$BACKUP_DIR" -name "claude_backup_*.tar.gz" -mtime +7 -delete 2>/dev/null
echo "已清理7天前的旧备份"