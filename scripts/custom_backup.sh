#!/bin/bash
# 自定义备份脚本
# 将OpenClaw备份文件移动到指定目录，并额外备份/root/claude目录

# 配置
BACKUP_TARGET="/root/.openclaw/mnt/sdb1/fanny2_backup"
RETENTION_DAYS=7

# 创建备份目录
mkdir -p "$BACKUP_TARGET"

# 1. 执行OpenClaw备份
echo "执行OpenClaw备份..."
BACKUP_FILE=$(openclaw backup create 2>&1 | grep -o "/root/[0-9]*\.tar\.gz" | tail -1)

if [ -z "$BACKUP_FILE" ]; then
    # 如果没找到标准输出，尝试其他方式
    BACKUP_FILE=$(find /root -name "*.tar.gz" -newer /tmp/.backup_check -type f 2>/dev/null | head -1)
    if [ -z "$BACKUP_FILE" ]; then
        # 创建时间戳文件
        touch /tmp/.backup_check
        openclaw backup create > /tmp/backup_output.txt 2>&1
        BACKUP_FILE=$(find /root -name "*.tar.gz" -newer /tmp/.backup_check -type f 2>/dev/null | head -1)
    fi
fi

if [ -n "$BACKUP_FILE" ] && [ -f "$BACKUP_FILE" ]; then
    echo "找到备份文件: $BACKUP_FILE"
    
    # 2. 备份额外目录
    for DIR in "/root/claude"; do
        if [ -d "$DIR" ]; then
            echo "备份额外目录: $DIR"
            ADDITIONAL_BACKUP="${BACKUP_TARGET}/$(basename "$DIR")-$(date +%Y%m%d_%H%M%S).tar.gz"
            tar -czf "$ADDITIONAL_BACKUP" -C / "$(echo "$DIR" | sed 's|^/||')" 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "额外目录备份完成: $(basename "$ADDITIONAL_BACKUP")"
                chmod 644 "$ADDITIONAL_BACKUP"
            else
                echo "警告: 备份目录 $DIR 失败"
            fi
        else
            echo "注意: 目录 $DIR 不存在，跳过备份"
        fi
    done
    
    # 3. 移动到目标目录
    FILENAME=$(basename "$BACKUP_FILE")
    TARGET_PATH="$BACKUP_TARGET/$FILENAME"
    
    mv "$BACKUP_FILE" "$TARGET_PATH"
    echo "OpenClaw备份文件已移动到: $TARGET_PATH"
    
    # 4. 设置权限
    chmod 644 "$TARGET_PATH"
    
    # 4. 清理旧备份
    echo "清理超过${RETENTION_DAYS}天的旧备份..."
    find "$BACKUP_TARGET" -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete
    
    # 5. 列出当前备份
    echo -e "\n当前备份文件:"
    ls -lh "$BACKUP_TARGET"/*.tar.gz 2>/dev/null || echo "暂无备份文件"
    
    # 6. 记录日志
    echo "$(date): 备份完成 - $FILENAME ($(du -h "$TARGET_PATH" | cut -f1))" >> /var/log/openclaw_backup.log
    
else
    echo "错误: 未找到备份文件"
    echo "$(date): 备份失败" >> /var/log/openclaw_backup.log
    exit 1
fi

echo "备份完成!"