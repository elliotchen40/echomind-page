#!/bin/bash
# bypy 百度网盘同步脚本
# 功能：检查bypy文件夹中的文件，有更新则下载到本地

# 设置环境变量（cron环境下需要）
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/root/.local/bin
export HOME=/root

DOWNLOAD_DIR="/root/.openclaw/mnt/airdiskshare/download"
LOG_DIR="/root/.openclaw/workspace/logs"
LOG_FILE="$LOG_DIR/bypy-sync.log"

# 创建目录
mkdir -p "$DOWNLOAD_DIR"
mkdir -p "$LOG_DIR"

# 记录开始时间
echo "========== $(date '+%Y-%m-%d %H:%M:%S') 开始同步百度网盘 ==========" >> "$LOG_FILE"

# 切换到下载目录
cd "$DOWNLOAD_DIR" || exit 1

# 执行bypy同步命令
# -v 显示详细信息
# -d 下载文件
# --shorten 缩短显示路径
bypy syncdown bypy >> "$LOG_FILE" 2>&1

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') 同步完成" >> "$LOG_FILE"
else
    echo "$(date '+%Y-%m-%d %H:%M:%S') 同步失败，错误代码: $?" >> "$LOG_FILE"
fi

echo "========== 同步结束 ==========" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"