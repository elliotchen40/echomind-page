#!/bin/bash
# 检查Linda回复的脚本

LOG_FILE="/root/.openclaw/workspace/linda_response.log"
TMUX_SESSION="linda_session"

echo "=== 检查时间: $(date) ===" >> "$LOG_FILE"

# 获取tmux会话内容
tmux capture-pane -t "$TMUX_SESSION" -p -S -50 | tail -20 >> "$LOG_FILE"

echo "=== 检查结束 ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 如果有新回复，发送邮件通知
if tail -20 "$LOG_FILE" | grep -q "Linda\|确认\|接受\|修改"; then
    echo "Linda有回复！" | mutt -s "Linda回复通知" -- 9244569@qq.com
fi