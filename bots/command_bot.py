import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 设置日志记录
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 配置信息 - 使用环境变量
COMMAND_BOT_TOKEN = os.environ.get("COMMAND_BOT_TOKEN")
GITHUB_TOKEN = os.environ.get("TOKEN")
REPO_FULL_NAME = os.environ.get("REPO_FULL_NAME")
COMMAND_GROUP_ID = os.environ.get("COMMAND_GROUP_ID")  # 必需的环境变量，无默认值

# 检查必要的环境变量
if not all([COMMAND_BOT_TOKEN, GITHUB_TOKEN, REPO_FULL_NAME, COMMAND_GROUP_ID]):
    logger.error("请设置 COMMAND_BOT_TOKEN, TOKEN, REPO_FULL_NAME 和 COMMAND_GROUP_ID 环境变量")
    exit(1)

# 将字符串转换为整数
try:
    COMMAND_GROUP_ID = int(COMMAND_GROUP_ID)
except ValueError:
    logger.error(f"COMMAND_GROUP_ID 必须是有效的整数，当前值: {COMMAND_GROUP_ID}")
    exit(1)

async def run_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理/run命令"""
    # 检查是否来自指定群聊
    if update.effective_chat.id != COMMAND_GROUP_ID:
        await update.message.reply_text("此命令仅限在特定群聊使用。")
        return
    
    # 检查发送者是否是群组管理员
    try:
        member = await context.bot.get_chat_member(COMMAND_GROUP_ID, update.effective_user.id)
        if member.status not in ["creator", "administrator"]:
            await update.message.reply_text("只有群组管理员可以使用此命令。")
            return
    except Exception as e:
        logger.error(f"检查用户权限时出错: {e}")
        await update.message.reply_text("检查权限时出错，请稍后再试。")
        return
    
    try:
        # 发送处理中消息
        processing_msg = await update.message.reply_text("🔄 正在触发工作流...")
        
        # 调用 GitHub API 触发工作流
        url = f"https://api.github.com/repos/{REPO_FULL_NAME}/actions/workflows/telegram_bot.yml/dispatches"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        data = {
            "ref": "main"  # 触发main分支的工作流
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 204:
            await context.bot.edit_message_text(
                chat_id=COMMAND_GROUP_ID,
                message_id=processing_msg.message_id,
                text="✅ 已成功触发部署命令！工作流即将开始运行。\n\n您可以在 GitHub Actions 页面查看运行状态。"
            )
            logger.info("成功触发 GitHub Actions 工作流")
        else:
            await context.bot.edit_message_text(
                chat_id=COMMAND_GROUP_ID,
                message_id=processing_msg.message_id,
                text=f"❌ 触发失败 (状态码: {response.status_code})\n\n错误信息: {response.text}"
            )
            logger.error(f"GitHub API 错误: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"触发工作流时出错: {e}")
        try:
            await context.bot.edit_message_text(
                chat_id=COMMAND_GROUP_ID,
                message_id=processing_msg.message_id,
                text="❌ 触发过程中出现错误，请稍后再试。"
            )
        except:
            await update.message.reply_text("❌ 触发过程中出现错误，请稍后再试。")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理/start命令"""
    if update.effective_chat.id != COMMAND_GROUP_ID:
        return
    
    await update.message.reply_text(
        "🤖 命令机器人已就绪！\n\n"
        "可用命令:\n"
        "/run - 触发 Telegram 机器人部署工作流\n"
        "/status - 检查机器人状态"
    )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理/status命令"""
    if update.effective_chat.id != COMMAND_GROUP_ID:
        return
    
    # 检查发送者是否是群组管理员
    try:
        member = await context.bot.get_chat_member(COMMAND_GROUP_ID, update.effective_user.id)
        if member.status not in ["creator", "administrator"]:
            return
    except:
        return
    
    await update.message.reply_text("✅ 命令机器人运行正常！")

def run_command_bot():
    """启动命令机器人"""
    logger.info(f"命令机器人将监听群聊 ID: {COMMAND_GROUP_ID}")
    
    # 创建Application实例
    application = Application.builder().token(COMMAND_BOT_TOKEN).build()
    
    # 添加命令处理器
    application.add_handler(CommandHandler("run", run_command))
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # 启动机器人
    logger.info("命令机器人已启动...")
    application.run_polling()

if __name__ == "__main__":
    run_command_bot()