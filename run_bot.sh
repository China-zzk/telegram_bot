#!/bin/bash

# 设置错误时退出
set -e

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# 启动消息转发机器人
start_message_bot() {
    local restart_count=0
    local max_restarts=10
    
    while [ $restart_count -lt $max_restarts ]; do
        log "启动消息转发机器人 (尝试 #$((restart_count+1)))"
        
        cd bots
        python message_bot.py
        EXIT_CODE=$?
        
        if [ $EXIT_CODE -eq 0 ]; then
            log "消息转发机器人正常退出"
            break
        else
            restart_count=$((restart_count+1))
            log "消息转发机器人异常退出，代码: $EXIT_CODE"
            log "重启次数: $restart_count/$max_restarts"
            
            if [ $restart_count -lt $max_restarts ]; then
                log "10秒后重新启动消息转发机器人..."
                sleep 10
            else
                log "消息转发机器人达到最大重启次数，停止尝试"
            fi
        fi
    done
}

# 启动命令机器人
start_command_bot() {
    local restart_count=0
    local max_restarts=10
    
    while [ $restart_count -lt $max_restarts ]; do
        log "启动命令机器人 (尝试 #$((restart_count+1)))"
        
        cd bots
        python command_bot.py
        EXIT_CODE=$?
        
        if [ $EXIT_CODE -eq 0 ]; then
            log "命令机器人正常退出"
            break
        else
            restart_count=$((restart_count+1))
            log "命令机器人异常退出，代码: $EXIT_CODE"
            log "重启次数: $restart_count/$max_restarts"
            
            if [ $restart_count -lt $max_restarts ]; then
                log "10秒后重新启动命令机器人..."
                sleep 10
            else
                log "命令机器人达到最大重启次数，停止尝试"
            fi
        fi
    done
}

log "开始运行 Telegram 机器人"

# 在后台同时启动两个机器人
start_message_bot &
MESSAGE_BOT_PID=$!

start_command_bot &
COMMAND_BOT_PID=$!

# 设置信号处理，确保在脚本退出时终止所有子进程
cleanup() {
    log "接收到终止信号，停止所有机器人..."
    kill $MESSAGE_BOT_PID 2>/dev/null || true
    kill $COMMAND_BOT_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# 等待所有后台进程结束
wait $MESSAGE_BOT_PID $COMMAND_BOT_PID

log "所有机器人进程结束"