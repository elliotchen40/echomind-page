#!/bin/bash

# 每日记忆文件初始化脚本
# 每次新会话时运行，检查并创建当天的记忆文件

WORKSPACE="/root/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +"%Y-%m-%d")
DAILY_FILE="$MEMORY_DIR/$TODAY.md"

# 确保memory目录存在
mkdir -p "$MEMORY_DIR"

# 如果当天的记忆文件不存在，创建它
if [ ! -f "$DAILY_FILE" ]; then
    echo "# 记忆文件: $TODAY" > "$DAILY_FILE"
    echo "" >> "$DAILY_FILE"
    echo "## 会话记录" >> "$DAILY_FILE"
    echo "" >> "$DAILY_FILE"
    echo "### 上午" >> "$DAILY_FILE"
    echo "- " >> "$DAILY_FILE"
    echo "" >> "$DAILY_FILE"
    echo "### 下午" >> "$DAILY_FILE"
    echo "- " >> "$DAILY_FILE"
    echo "" >> "$DAILY_FILE"
    echo "## 重要事项" >> "$DAILY_FILE"
    echo "- " >> "$DAILY_FILE"
    echo "" >> "$DAILY_FILE"
    echo "## 重要文件记录" >> "$DAILY_FILE"
    echo "- " >> "$DAILY_FILE"
    echo "" >> "$DAILY_FILE"
    echo "## 待办事项" >> "$DAILY_FILE"
    echo "- " >> "$DAILY_FILE"
    echo "" >> "$DAILY_FILE"
    echo "---" >> "$DAILY_FILE"
    echo "" >> "$DAILY_FILE"
    echo "## Silent Replies" >> "$DAILY_FILE"
    echo "当你有话要说时，直接回复，不要说'NO_REPLY'。" >> "$DAILY_FILE"
    echo "" >> "$DAILY_FILE"
    echo "## Heartbeats" >> "$DAILY_FILE"
    echo "心跳检查提示词: 阅读 HEARTBEAT.md（如果存在）。严格执行。不要从之前的对话中推断或重复旧任务。如果没有问题需要关注，回复 'HEARTBEAT_OK'。" >> "$DAILY_FILE"
    echo "如果你收到心跳轮询（与上述心跳检查提示词匹配的用户消息），并且没有问题需要关注，请直接回复：" >> "$DAILY_FILE"
    echo "HEARTBEAT_OK" >> "$DAILY_FILE"
    echo "OpenClaw 将前导/尾随的 'HEARTBEAT_OK' 视为心跳确认（并可能丢弃它）。" >> "$DAILY_FILE"
    echo "如果有问题需要关注，请不要包含'HEARTBEAT_OK'；请回复提醒文字。" >> "$DAILY_FILE"
    echo "文件创建时间: $(date)" >> "$DAILY_FILE"
    echo "✅ 已创建当天记忆文件: $DAILY_FILE"
else
    echo "✅ 当天记忆文件已存在: $DAILY_FILE"
fi