#!/bin/bash

while true; do
    echo "启动 Telegram 机器人..."
    python bot.py
    EXIT_CODE=$?
    echo "机器人退出，代码: $EXIT_CODE"
    
    if [ $EXIT_CODE -eq 0 ]; then
        echo "正常退出，不再重启"
        break
    else
        echo "异常退出，5秒后重新启动..."
        sleep 5
    fi
done
