import os
import logging
import re
from datetime import datetime
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# 设置日志记录
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
BOT_TOKEN = os.environ.get("MESSAGE_BOT_TOKEN")
YOUR_CHAT_ID = os.environ.get("YOUR_CHAT_ID")
KEYWORD_GROUP_ID = os.environ.get("KEYWORD_GROUP_ID")  # 关键词转发群聊ID
KEYWORDS = os.environ.get("KEYWORDS", "紧急,重要,urgent,important").split(",")  # 关键词列表

# 检查必要的环境变量
if not BOT_TOKEN or not YOUR_CHAT_ID:
    logger.error("请设置 MESSAGE_BOT_TOKEN 和 YOUR_CHAT_ID 环境变量")
    exit(1)

# 健康检查计数器
health_check_count = 0

def contains_keywords(text):
    """检查文本是否包含关键词"""
    if not text:
        return False
    
    text_lower = text.lower()
    for keyword in KEYWORDS:
        if keyword.strip().lower() in text_lower:
            return True
    return False

async def forward_to_keyword_group(context, user_info, message_text, message_type, content=None, caption=None):
    """转发消息到关键词群聊"""
    try:
        if not KEYWORD_GROUP_ID:
            return
        
        alert_message = f"🚨 关键词警报！\n{user_info}\n\n消息类型: {message_type}"
        
        if message_text:
            alert_message += f"\n\n消息内容:\n{message_text}"
        
        if caption:
            alert_message += f"\n\n描述: {caption}"
        
        # 发送警报消息
        await context.bot.send_message(
            chat_id=KEYWORD_GROUP_ID,
            text=alert_message
        )
        
        # 转发原始内容（图片、文档等）
        if content and message_type == "图片":
            await context.bot.send_photo(
                chat_id=KEYWORD_GROUP_ID,
                photo=content,
                caption=f"关键词警报图片 - {user_info}"
            )
        elif content and message_type == "文档":
            await context.bot.send_document(
                chat_id=KEYWORD_GROUP_ID,
                document=content,
                caption=f"关键词警报文档 - {user_info}"
            )
            
        logger.info(f"已转发关键词消息到群聊 {KEYWORD_GROUP_ID}")
        
    except Exception as e:
        logger.error(f"转发到关键词群聊时出错: {e}")

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理所有收到的消息并转发给指定用户"""
    try:
        # 获取发送者信息
        user = update.message.from_user
        user_info = f"来自: {user.first_name}"
        if user.last_name:
            user_info += f" {user.last_name}"
        if user.username:
            user_info += f" (@{user.username})"
        
        user_info += f"\n用户ID: {user.id}"
        
        message_text = None
        content = None
        message_type = "文本"
        caption = None
        
        # 处理文本消息
        if update.message.text:
            message_text = update.message.text
            message_type = "文本"
            
            # 检查关键词
            if contains_keywords(message_text):
                await forward_to_keyword_group(context, user_info, message_text, message_type)
        
        # 处理图片消息
        elif update.message.photo:
            # 获取最高质量的图片
            content = update.message.photo[-1].file_id
            message_type = "图片"
            caption = update.message.caption or ""
            
            # 检查图片描述中的关键词
            if contains_keywords(caption):
                await forward_to_keyword_group(context, user_info, None, message_type, content, caption)
        
        # 处理文档消息
        elif update.message.document:
            content = update.message.document.file_id
            message_type = "文档"
            caption = update.message.caption or ""
            file_name = update.message.document.file_name or ""
            
            # 检查文件名或描述中的关键词
            if contains_keywords(caption) or contains_keywords(file_name):
                await forward_to_keyword_group(context, user_info, None, message_type, content, caption)
        
        # 转发给指定用户
        if message_text:
            final_message = f"{user_info}\n\n消息内容:\n{message_text}"
            await context.bot.send_message(chat_id=YOUR_CHAT_ID, text=final_message)
        elif content:
            if message_type == "图片":
                await context.bot.send_photo(
                    chat_id=YOUR_CHAT_ID, 
                    photo=content, 
                    caption=f"{user_info}\n\n发送了一张图片{caption and ': ' + caption or ''}"
                )
            elif message_type == "文档":
                await context.bot.send_document(
                    chat_id=YOUR_CHAT_ID, 
                    document=content, 
                    caption=f"{user_info}\n\n发送了一个文件: {update.message.document.file_name}{caption and '\n描述: ' + caption or ''}"
                )
        
        # 回复发送者
        await update.message.reply_text("✅ 已收到您的消息，我会尽快回复！")
        
    except Exception as e:
        logger.error(f"处理消息时出错: {e}")
        # 尝试通知用户出错
        try:
            await update.message.reply_text("❌ 消息处理失败，请稍后再试。")
        except:
            pass

async def health_check(context: ContextTypes.DEFAULT_TYPE):
    """定期发送健康状态"""
    global health_check_count
    health_check_count += 1
    
    try:
        health_message = (
            f"🤖 消息机器人正常运行 - 健康检查 #{health_check_count}\n"
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"运行环境: GitHub Actions (Ubuntu Linux)\n"
            f"监控关键词: {', '.join(KEYWORDS)}"
        )
        
        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=health_message
        )
        
        # 同时发送到关键词群聊
        if KEYWORD_GROUP_ID:
            await context.bot.send_message(
                chat_id=KEYWORD_GROUP_ID,
                text=f"📊 机器人健康状态检查 #{health_check_count}\n机器人运行正常"
            )
            
        logger.info(f"消息机器人健康检查 #{health_check_count} 已发送")
    except Exception as e:
        logger.error(f"发送健康检查时出错: {e}")

async def post_init(application: Application):
    """机器人初始化后执行"""
    # 发送启动通知
    try:
        startup_message = (
            "🚀 消息转发机器人已启动!\n"
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            "环境: GitHub Actions\n"
            f"关键词监控已启用: {', '.join(KEYWORDS)}"
        )
        
        await application.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=startup_message
        )
        
        # 同时发送到关键词群聊
        if KEYWORD_GROUP_ID:
            await application.bot.send_message(
                chat_id=KEYWORD_GROUP_ID,
                text="🔔 关键词监控机器人已启动！\n当收到包含关键词的消息时会自动转发到此群聊。"
            )
            
    except Exception as e:
        logger.error(f"发送启动通知时出错: {e}")

def run_message_bot():
    """启动消息转发机器人"""
    try:
        # 创建Application实例
        application = Application.builder().token(BOT_TOKEN).build()
        
        # 设置初始化后回调
        application.post_init = post_init
        
        # 添加消息处理器，处理所有非命令消息
        application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_message))
        
        # 添加定期健康检查（每4小时一次）
        job_queue = application.job_queue
        if job_queue:
            job_queue.run_repeating(health_check, interval=14400, first=10)  # 4小时 = 14400秒
        
        # 启动机器人
        logger.info("消息转发机器人启动中...")
        logger.info(f"监控关键词: {KEYWORDS}")
        if KEYWORD_GROUP_ID:
            logger.info(f"关键词转发群聊ID: {KEYWORD_GROUP_ID}")
        
        application.run_polling()
        
    except Exception as e:
        logger.error(f"启动消息转发机器人时发生错误: {e}")
        # 重新抛出异常以便run_bots.sh可以捕获
        raise

if __name__ == "__main__":
    run_message_bot()