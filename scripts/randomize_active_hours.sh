#!/bin/bash
# 每天随机设定主动联系的时间窗口
# 这样heartbeat触发时发消息的时间就变得随机了

# 早上送女儿后（6:50-8:30）- 随机选择6:50到8:30之间的一个时间
MORNING_START=$((RANDOM % 100 + 410))  # 4:10 AM to 5:50 AM in minutes from midnight
MORNING_END=$((MORNING_START + 30))

# 中午（11:30-13:00）- 扩大窗口，包含午前和午后
NOON_START=$((11 * 60 + 30 + RANDOM % 30))  # 11:30-12:00
NOON_END=$((13 * 60))  # 固定13:00结束

# 下午休息时（14:00-15:00）
AFTERNOON_START=$((14 * 60 + RANDOM % 60))
AFTERNOON_END=$((AFTERNOON_START + 30))

# 傍晚下班（17:30-18:30）
EVENING_START=$((17 * 60 + 30 + RANDOM % 60))
EVENING_END=$((EVENING_START + 30))

# 晚饭（18:30-19:30）
DINNER_START=$((18 * 60 + 30 + RANDOM % 60))
DINNER_END=$((DINNER_START + 30))

# 睡觉前（22:00-23:00）
NIGHT_START=$((22 * 60 + RANDOM % 60))
NIGHT_END=$((NIGHT_START + 30))

# 写入配置文件
cat > /root/.openclaw/workspace/.active_hours.json << EOF
{
  "morning": {"start": $MORNING_START, "end": $MORNING_END},
  "noon": {"start": $NOON_START, "end": $NOON_END},
  "afternoon": {"start": $AFTERNOON_START, "end": $AFTERNOON_END},
  "evening": {"start": $EVENING_START, "end": $EVENING_END},
  "dinner": {"start": $DINNER_START, "end": $DINNER_END},
  "night": {"start": $NIGHT_START, "end": $NIGHT_END},
  "updated": "$(date -Iseconds)"
}
EOF

echo "Active hours randomized at $(date)"
