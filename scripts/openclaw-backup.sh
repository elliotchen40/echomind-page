#!/bin/bash
# OpenClaw 每日备份脚本
# 直接复制文件到 /mnt/sdb1/fanny2_backup/YYYY-MM-DD/ 目录
# 保留原始文件结构，方便直接浏览

BACKUP_ROOT="/mnt/sdb1/fanny2_backup"
DATE_DIR=$(date +%Y-%m-%d)
TARGET_DIR="$BACKUP_ROOT/$DATE_DIR"
LOG_FILE="/root/.openclaw/workspace/logs/backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 创建当日备份目录
mkdir -p "$TARGET_DIR"

log "开始备份..."

# 复制 OpenClaw 配置（排除大目录）
log "备份 OpenClaw 配置..."
mkdir -p "$TARGET_DIR/openclaw"
rsync -a --exclude='workspace' --exclude='mnt' --exclude='media' \
    /root/.openclaw/ \
    "$TARGET_DIR/openclaw/" 2>/dev/null

# 复制 workspace（排除 mnt 和媒体文件）
log "备份 Workspace..."
mkdir -p "$TARGET_DIR/workspace"
rsync -a --exclude='mnt' --exclude='media/fanny' --exclude='logs/*.log' \
    /root/.openclaw/workspace/ \
    "$TARGET_DIR/workspace/" 2>/dev/null

# 保留策略：只保留最近14天的备份
log "清理旧备份（保留14天）..."
find "$BACKUP_ROOT" -type d -name "20*" -mtime +14 -exec rm -rf {} \; 2>/dev/null

log "备份完成！"
du -sh "$TARGET_DIR"/*
