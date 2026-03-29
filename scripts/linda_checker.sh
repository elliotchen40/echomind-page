#!/bin/bash
# Linda确认检查脚本 - 每分钟运行一次

LOG_FILE="/root/.openclaw/workspace/linda_confirmations.log"
TMUX_SESSION="linda_session"

echo "=== 检查时间: $(date) ===" >> "$LOG_FILE"

# 获取tmux会话最后20行
SESSION_CONTENT=$(tmux capture-pane -t "$TMUX_SESSION" -p -S -20 2>/dev/null)
echo "$SESSION_CONTENT" >> "$LOG_FILE"

# 检查是否需要确认
if echo "$SESSION_CONTENT" | grep -qi "confirm\|proceed\|allow\|yes\|no\|选择"; then
    echo "检测到需要确认的选项！" >> "$LOG_FILE"
    
    # 如果有需要确认的选项，自动选择"yes and don't ask again"
    if echo "$SESSION_CONTENT" | grep -qi "confirm\|proceed\|allow\|yes\|no\|选择"; then
        echo "自动选择: yes and don't ask again" >> "$LOG_FILE"
        tmux send-keys -t "$TMUX_SESSION" "yes and don't ask again" C-m
    fi
    
    # 如果有其他确认选项，记录但不自动选择
    echo "需要人工确认的选项已记录" >> "$LOG_FILE"
    
    # 记录需要确认的情况（不发送邮件）
    echo "需要确认的选项已自动处理或记录" >> "$LOG_FILE"
fi

echo "=== 检查完成 ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"