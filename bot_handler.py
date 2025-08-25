import os
import requests
import logging
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from datetime import datetime

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=os.environ.get('LOG_LEVEL', 'INFO')
)
logger = logging.getLogger(__name__)

# 配置参数
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TARGET_GROUP_ID = os.environ.get('TARGET_GROUP_ID')  # 用户消息转发目标群组
MONITOR_GROUP_ID = os.environ.get('MONITOR_GROUP_ID')  # 监控关键词的群组
RESPONSE_GROUP_ID = os.environ.get('RESPONSE_GROUP_ID')  # 响应/open命令的群组
KEYWORDS = [k.strip() for k in os.environ.get('KEYWORDS', '').split(',') if k.strip()]  # 关键词列表
ALLOWED_USER_ID = os.environ.get('ALLOWED_USER_ID')  # 允许触发Action的用户
MESSAGE_FORMAT = os.environ.get('MESSAGE_FORMAT', '来自用户 {user_name} 的消息: {message}')
KEYWORD_MATCH_MODE = os.environ.get('KEYWORD_MATCH_MODE', 'contains').lower()
FORWARD_BOT_MESSAGES = os.environ.get('FORWARD_BOT_MESSAGES', 'true').lower() == 'true'  # 是否转发其他机器人的消息

# 初始化机器人
bot = Bot(token=BOT_TOKEN)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.message
        if not message:
            return
        
        chat_id = str(message.chat_id)
        user_id = str(message.from_user.id) if message.from_user else "unknown"
        user_name = "未知用户"
        
        if message.from_user:
            user_name = message.from_user.username or f"{message.from_user.first_name} {message.from_user.last_name or ''}"
        
        # 获取消息文本（包括其他机器人发送的消息）
        text = ""
        if message.text:
            text = message.text
        elif message.caption:
            text = message.caption
        
        logger.info(f"收到消息: 来自用户 {user_id}, 内容: {text}")
        
        # 检查是否来自其他机器人
        is_from_bot = message.from_user and message.from_user.is_bot if message.from_user else False
        
        # 用户私聊消息 → 转发至目标群组
        if message.chat.type == 'private' and not is_from_bot:
            formatted_message = MESSAGE_FORMAT.format(
                user_id=user_id,
                user_name=user_name,
                first_name=message.from_user.first_name if message.from_user else "",
                last_name=message.from_user.last_name or '' if message.from_user else "",
                message=text,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            await bot.send_message(chat_id=TARGET_GROUP_ID, text=formatted_message)
            logger.info(f"已转发用户消息到群组 {TARGET_GROUP_ID}")
        
        # 监控群组 关键词检测 → 转发至响应群组
        if chat_id == MONITOR_GROUP_ID and KEYWORDS:
            # 检查是否允许转发机器人消息
            if is_from_bot and not FORWARD_BOT_MESSAGES:
                logger.info("忽略来自其他机器人的消息")
                return
            
            keyword_detected = False
            
            if KEYWORD_MATCH_MODE == 'exact':
                keyword_detected = any(keyword.lower() == text.lower() for keyword in KEYWORDS)
            elif KEYWORD_MATCH_MODE == 'startswith':
                keyword_detected = any(text.lower().startswith(keyword.lower()) for keyword in KEYWORDS)
            elif KEYWORD_MATCH_MODE == 'regex':
                import re
                for keyword in KEYWORDS:
                    if re.search(keyword, text, re.IGNORECASE):
                        keyword_detected = True
                        break
            else:  # contains (default)
                keyword_detected = any(keyword.lower() in text.lower() for keyword in KEYWORDS)
            
            if keyword_detected:
                sender_type = "机器人" if is_from_bot else "用户"
                await bot.send_message(
                    chat_id=RESPONSE_GROUP_ID, 
                    text=f"关键词 '{', '.join(KEYWORDS)}' 触发消息:\n\n来自{sender_type}: {user_name}\n内容: {text}"
                )
                logger.info(f"检测到关键词，已转发消息到群组 {RESPONSE_GROUP_ID}")
        
        # 响应群组 中特定用户的 /open 命令
        if (chat_id == RESPONSE_GROUP_ID and text.strip() == "/open" and 
            user_id == ALLOWED_USER_ID and not is_from_bot):
            logger.info(f"用户 {user_id} 尝试触发 GitHub Action")
            
            # 触发 GitHub Action
            github_token = os.environ.get('GITHUB_TOKEN')
            repo = os.environ.get('GITHUB_REPOSITORY')
            
            if github_token and repo:
                headers = {
                    'Authorization': f'token {github_token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                data = {
                    'event_type': 'trigger-open-command'
                }
                
                # 触发 GitHub Actions workflow
                response = requests.post(
                    f'https://api.github.com/repos/{repo}/dispatches',
                    headers=headers,
                    json=data
                )
                
                if response.status_code == 204:
                    await message.reply_text("✅ 已成功触发 GitHub Action!")
                    logger.info("GitHub Action 触发成功")
                else:
                    error_msg = f"触发 GitHub Action 失败! 状态码: {response.status_code}, 响应: {response.text}"
                    await message.reply_text(error_msg)
                    logger.error(error_msg)
            else:
                error_msg = "GitHub 配置缺失，无法触发 Action!"
                await message.reply_text(error_msg)
                logger.error(error_msg)
                
    except Exception as e:
        logger.error(f"处理消息时出错: {str(e)}")
        try:
            await message.reply_text(f"处理消息时出错: {str(e)}")
        except:
            pass

def main():
    try:
        # 验证必要环境变量
        required_vars = ['TELEGRAM_BOT_TOKEN', 'TARGET_GROUP_ID', 'MONITOR_GROUP_ID', 'RESPONSE_GROUP_ID', 'ALLOWED_USER_ID']
        for var in required_vars:
            if not os.environ.get(var):
                logger.error(f"必需的环境变量 {var} 未设置")
                return
        
        # 创建应用
        application = Application.builder().token(BOT_TOKEN).build()
        
        # 添加消息处理器 - 处理所有类型的消息，包括其他机器人发送的消息
        application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
        
        # 启动轮询
        logger.info("机器人启动成功，等待消息...")
        print("机器人启动成功，等待消息...")
        print(f"转发其他机器人消息: {'启用' if FORWARD_BOT_MESSAGES else '禁用'}")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"机器人启动失败: {str(e)}")

if __name__ == "__main__":
    main()
