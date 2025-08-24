"""
bots 包 - 包含 Telegram 机器人模块

这个包包含两个主要的机器人：
- message_bot: 消息转发机器人
- command_bot: 命令处理机器人
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = ["message_bot", "command_bot"]

# 包初始化代码
import logging

# 设置包级别的日志记录
logging.getLogger(__name__).addHandler(logging.NullHandler())

# 提供便捷的导入方式
from .message_bot import run_message_bot
from .command_bot import run_command_bot