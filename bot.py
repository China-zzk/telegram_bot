import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 设置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 从环境变量获取配置
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROUP2_ID = int(os.environ.get('GROUP2_ID'))
GROUP3_ID = int(os.environ.get('GROUP3_ID'))
GROUP4_ID = int(os.environ.get('GROUP4_ID'))
KEYWORD = os.environ.get('KEYWORD', '关键词').lower()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.effective_message
        chat = update.effective_chat
        user = update.effective_user
        
        # 获取机器人信息
        bot_info = await context.bot.get_me()
        bot_id = bot_info.id
        
        # 忽略机器人自己发送的消息
        if user.id == bot_id:
            logger.info("忽略机器人自己发送的消息")
            return
        
        # 规则1: 私聊消息转发到群聊2
        if chat.type == 'private':
            logger.info(f"收到来自用户 {user.id} 的私聊消息")
            
            # 构建转发消息文本
            forward_text = f"来自用户 {user.id} 的消息:\n\n{message.text if message.text else '非文本消息'}"
            
            # 根据消息类型转发
            if message.text:
                await context.bot.send_message(chat_id=GROUP2_ID, text=forward_text)
            elif message.photo:
                await context.bot.send_photo(chat_id=GROUP2_ID, photo=message.photo[-1].file_id, caption=forward_text)
            elif message.document:
                await context.bot.send_document(chat_id=GROUP2_ID, document=message.document.file_id, caption=forward_text)
            elif message.video:
                await context.bot.send_video(chat_id=GROUP2_ID, video=message.video.file_id, caption=forward_text)
            else:
                await context.bot.send_message(chat_id=GROUP2_ID, text=f"收到来自用户 {user.id} 的未处理类型消息")
            
            logger.info(f"已转发用户 {user.id} 的消息到群聊 {GROUP2_ID}")
        
        # 规则2: 群聊3中关键词消息转发到群聊4
        elif chat.id == GROUP3_ID:
            logger.info(f"收到群聊 {GROUP3_ID} 中的消息")
            
            # 检查消息是否包含关键词
            message_text = (message.text or message.caption or "").lower()
            if KEYWORD in message_text:
                logger.info(f"检测到关键词 '{KEYWORD}'，准备转发到群聊 {GROUP4_ID}")
                
                # 转发原消息
                await message.forward(chat_id=GROUP4_ID)
                
                # 添加提示信息
                sender_name = user.first_name + (f" {user.last_name}" if user.last_name else "")
                await context.bot.send_message(
                    chat_id=GROUP4_ID, 
                    text=f"🚨 检测到关键词 '{KEYWORD}'\n来自: {sender_name} (@{user.username or '无用户名'})"
                )
                
    except Exception as e:
        logger.error(f"处理消息时出错: {e}")

def main():
    # 创建应用
    application = Application.builder().token(BOT_TOKEN).build()
    
    # 添加消息处理器
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    
    # 启动轮询
    logger.info("机器人启动...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
