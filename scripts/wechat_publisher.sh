#!/bin/bash
# 微信公众号发布脚本 - 调用Python版
# 用法: bash wechat_publisher.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd /root/.openclaw/workspace

python3 "${SCRIPT_DIR}/wechat_publisher.py"
