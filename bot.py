import os
import logging
import asyncio
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
BOT_TOKEN = os.environ.get("BOT_TOKEN")
YOUR_CHAT_ID = os.environ.get("YOUR_CHAT_ID")

# 检查必要的环境变量
if not BOT_TOKEN or not YOUR_CHAT_ID:
    logger.error("请设置 BOT_TOKEN 和 YOUR_CHAT_ID 环境变量")
    exit(1)

# 健康检查计数器
health_check_count = 0

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
        
        # 处理文本消息
        if update.message.text:
            message_text = f"{user_info}\n\n消息内容:\n{update.message.text}"
            await context.bot.send_message(chat_id=YOUR_CHAT_ID, text=message_text)
        
        # 处理图片消息
        elif update.message.photo:
            # 获取最高质量的图片
            photo = update.message.photo[-1].file_id
            caption = f"{user_info}\n\n发送了一张图片"
            if update.message.caption:
                caption += f"\n描述: {update.message.caption}"
            
            await context.bot.send_photo(
                chat_id=YOUR_CHAT_ID, 
                photo=photo, 
                caption=caption
            )
        
        # 处理文档消息
        elif update.message.document:
            document = update.message.document.file_id
            caption = f"{user_info}\n\n发送了一个文件: {update.message.document.file_name}"
            if update.message.caption:
                caption += f"\n描述: {update.message.caption}"
            
            await context.bot.send_document(
                chat_id=YOUR_CHAT_ID, 
                document=document, 
                caption=caption
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
        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=f"🤖 机器人正常运行 - 健康检查 #{health_check_count}\n"
                 f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"运行环境: GitHub Actions (Ubuntu Linux)"
        )
        logger.info(f"健康检查 #{health_check_count} 已发送")
    except Exception as e:
        logger.error(f"发送健康检查时出错: {e}")

async def post_init(application: Application):
    """机器人初始化后执行"""
    # 发送启动通知
    try:
        await application.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text="🚀 Telegram 机器人已启动!\n"
                 f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 "环境: GitHub Actions"
        )
    except Exception as e:
        logger.error(f"发送启动通知时出错: {e}")

def main():
    """启动机器人"""
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
        logger.info("机器人启动中...")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"启动机器人时发生错误: {e}")
        # 重新抛出异常以便run_bot.sh可以捕获
        raise

if __name__ == "__main__":
    main()
