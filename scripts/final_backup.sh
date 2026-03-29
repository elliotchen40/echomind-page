#!/bin/bash
# 备份脚本 - 备份整个 /root/.openclaw 文件夹（排除mnt）

echo "=== 备份脚本启动: $(date) ==="

# 配置
BACKUP_ROOT="/root/.openclaw/mnt/sdb1/fanny2_backup"
SOURCE_DIR="/root/.openclaw"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

echo "备份目录: $BACKUP_DIR"

# 1. 创建目录
mkdir -p "$BACKUP_DIR"

# 2. 复制整个openclaw目录，排除mnt
echo "开始备份 /root/.openclaw (排除mnt)..."
rsync -av --exclude='mnt' "$SOURCE_DIR/" "$BACKUP_DIR/" && echo "✅ 备份成功" || echo "❌ 备份失败"

# 3. 显示结果
echo ""
echo "=== 备份完成 ==="
echo "备份时间: $(date)"
echo "备份目录: $BACKUP_DIR"
echo ""
echo "目录内容:"
ls -la "$BACKUP_DIR/"