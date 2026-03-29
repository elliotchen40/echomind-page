#!/bin/bash
# 聊天记录查询工具

DB_PATH="/root/.openclaw/workspace/date/chat_records.db"
SCRIPT_PATH="/root/.openclaw/workspace/scripts/import_chat_to_sqlite.py"

echo "=== 聊天记录查询工具 ==="

if [ ! -f "$DB_PATH" ]; then
    echo "错误: 数据库文件不存在: $DB_PATH"
    exit 1
fi

case "$1" in
    "search")
        if [ -z "$2" ]; then
            echo "用法: $0 search <关键词>"
            exit 1
        fi
        echo "搜索关键词: $2"
        python3 "$SCRIPT_PATH" --query --keyword "$2"
        ;;
        
    "sender")
        if [ -z "$2" ]; then
            echo "用法: $0 sender <发送者名称>"
            exit 1
        fi
        echo "搜索发送者: $2"
        python3 "$SCRIPT_PATH" --query --sender "$2"
        ;;
        
    "stats")
        echo "数据库统计信息:"
        sqlite3 "$DB_PATH" <<EOF
SELECT 
    COUNT(*) as "总消息数",
    COUNT(DISTINCT sender) as "发送者数量",
    MIN(timestamp) as "最早消息",
    MAX(timestamp) as "最新消息"
FROM chat_messages;
EOF
        ;;
        
    "senders")
        echo "所有发送者列表:"
        sqlite3 "$DB_PATH" "SELECT sender, COUNT(*) as count FROM chat_messages GROUP BY sender ORDER BY count DESC LIMIT 20;"
        ;;
        
    "recent")
        echo "最近消息:"
        sqlite3 "$DB_PATH" "SELECT timestamp, sender, substr(content, 1, 50) as preview FROM chat_messages ORDER BY timestamp DESC LIMIT 10;"
        ;;
        
    *)
        echo "用法:"
        echo "  $0 search <关键词>      # 搜索包含关键词的消息"
        echo "  $0 sender <发送者>      # 搜索特定发送者的消息"
        echo "  $0 stats               # 显示数据库统计"
        echo "  $0 senders             # 显示发送者列表"
        echo "  $0 recent              # 显示最近消息"
        echo ""
        echo "数据库位置: $DB_PATH"
        echo "总消息数: $(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM chat_messages;" 2>/dev/null)"
        ;;
esac