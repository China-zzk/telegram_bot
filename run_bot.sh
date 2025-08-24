#!/bin/bash

# 设置错误时退出
set -e

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 最大重启次数
MAX_RESTARTS=10
RESTART_COUNT=0

log "开始运行 Telegram 机器人"

while [ $RESTART_COUNT -lt $MAX_RESTARTS ]; do
    log "启动机器人 (尝试 #$((RESTART_COUNT+1)))"
    
    # 运行 Python 脚本
    python bot.py
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
        log "机器人正常退出"
        break
    else
        RESTART_COUNT=$((RESTART_COUNT+1))
        log "机器人异常退出，代码: $EXIT_CODE"
        log "重启次数: $RESTART_COUNT/$MAX_RESTARTS"
        
        if [ $RESTART_COUNT -lt $MAX_RESTARTS ]; then
            log "10秒后重新启动..."
            sleep 10
        else
            log "达到最大重启次数，停止尝试"
        fi
    fi
done

log "脚本结束"
