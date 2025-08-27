import logging
import asyncio
import aiohttp
import json
from datetime import datetime, timezone, timedelta
from typing import Optional
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 硬编码的环境变量 - 转换为整数
BOT_TOKEN = "8278711187:AAFmsOqbzbYZweWG-7VTwBqPE6iKH0O-4E4"
GROUP2_ID = -1003073658115
GROUP4_ID = -1003014622661

# 签到配置
CHECKIN_DOMAIN = 'https://ikuuu.de'
CHECKIN_EMAIL = 'zzk6780051@gmail.com'
CHECKIN_PASSWORD = 'zzk6780051'
TG_CHAT_ID_SUCCESS = -1003014622661  # 成功签到和失败都发送至此
TG_CHAT_ID_ALREADY = -1002928740845  # 仅已签到过发送至此

# 设置日志记录
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 全局状态变量
forwarding_enabled = True

async def send_startup_message(bot):
    """发送启动消息到群聊4"""
    message = "🤖 机器人启动成功！\n\n✅ 功能已就绪：\n- 私聊消息将转发至群组2\n- 支持签到功能，在群组4发送'签到'即可"
    
    try:
        await bot.send_message(chat_id=GROUP4_ID, text=message)
        logger.info(f"已向群组4 ({GROUP4_ID}) 发送启动消息")
    except Exception as e:
        logger.error(f"向群组4发送启动消息失败: {e}")

async def forward_private_to_group2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """将用户私聊消息转发到群组2"""
    global forwarding_enabled
    
    if not forwarding_enabled:
        return  # 如果转发功能已禁用，直接返回
        
    try:
        # 检查消息是否来自私聊
        if update.message and update.message.chat.type == "private":
            # 转发消息到群组2
            await update.message.forward(chat_id=GROUP2_ID)
            logger.info(f"转发私聊消息到群组2: {update.message.text}")
    except Exception as e:
        logger.error(f"转发私聊消息时出错: {e}")

async def handle_group4_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """处理群聊4中的控制命令"""
    global forwarding_enabled
    
    # 检查消息是否来自群组4并且有文本内容
    if update.message and update.message.chat.id == GROUP4_ID and update.message.text:
        command = update.message.text.strip().lower()
        
        if command == "停止":
            forwarding_enabled = False
            await update.message.reply_text("🤖 机器人已停止转发功能")
            logger.info("转发功能已禁用")
            
        elif command == "启动":
            forwarding_enabled = True
            await update.message.reply_text("🤖 机器人已启动转发功能")
            logger.info("转发功能已启用")
            
        elif command == "状态":
            status = "正在运行" if forwarding_enabled else "已停止"
            await update.message.reply_text(f"🤖 机器人当前状态: {status}")
            logger.info(f"状态查询: {status}")
            
        elif command == "签到":
            # 处理签到命令
            await update.message.reply_text("🔄 正在执行签到，请稍候...")
            try:
                result = await checkin()
                
                # 根据签到结果选择不同的聊天ID
                target_chat_id = TG_CHAT_ID_ALREADY if result.get('already_checked', False) else TG_CHAT_ID_SUCCESS
                
                # 发送签到结果到相应群组
                await send_checkin_notification(
                    context.bot,
                    result.get('message', '未知结果'),
                    result.get('already_checked', False),
                    target_chat_id
                )
                
                # 回复用户
                status_emoji = "🔄" if result.get('already_checked', False) else "✅"
                await update.message.reply_text(f"{status_emoji} {result.get('message', '未知结果')}")
                
            except Exception as e:
                logger.error(f"签到失败: {e}")
                # 发送失败通知到成功频道
                await send_checkin_notification(
                    context.bot,
                    f"❌ 自动签到失败\n{str(e)}",
                    False,
                    TG_CHAT_ID_SUCCESS
                )
                await update.message.reply_text(f"❌ 签到失败: {str(e)}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """处理所有错误"""
    # 将 update 参数转换为适当的类型
    telegram_update = update if isinstance(update, Update) else None
    logger.error(f"错误: {context.error}")
    if telegram_update:
        logger.error(f"相关更新: {telegram_update}")

async def post_init(application: Application):
    """在机器人启动后执行的初始化任务"""
    # 发送启动消息到群聊4
    await send_startup_message(application.bot)

async def checkin():
    """执行签到功能"""
    try:
        logger.info(f"[{CHECKIN_EMAIL}] 进行登录...")
        
        # 创建会话
        async with aiohttp.ClientSession() as session:
            # 登录
            login_data = {
                "email": CHECKIN_EMAIL,
                "passwd": CHECKIN_PASSWORD
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'Origin': CHECKIN_DOMAIN,
                'Referer': f'{CHECKIN_DOMAIN}/auth/login'
            }
            
            async with session.post(
                f"{CHECKIN_DOMAIN}/auth/login",
                headers=headers,
                data=json.dumps(login_data)
            ) as response:
                # 获取响应文本内容
                response_text = await response.text()
                logger.info(f"登录响应原始内容: {response_text}")
                
                # 尝试解析JSON，无论Content-Type是什么
                try:
                    login_result = json.loads(response_text)
                    logger.info(f"登录结果: {login_result.get('msg', '未知消息')}")
                    
                    # 检查登录是否成功
                    if not login_result.get('ret', 0) == 1:
                        error_msg = login_result.get('msg', '登录失败')
                        logger.error(f"登录失败: {error_msg}")
                        raise Exception(f"登录失败: {error_msg}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"响应不是有效的JSON: {response_text[:200]}...")
                    raise Exception(f"登录失败: 服务器返回了无效的JSON响应")
                
                # 获取cookie
                cookies = response.cookies
                cookie_str = '; '.join([f"{key}={value.value}" for key, value in cookies.items()])
                await asyncio.sleep(1)
                
                # 签到
                checkin_headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Origin': CHECKIN_DOMAIN,
                    'Referer': f'{CHECKIN_DOMAIN}/user/panel',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Cookie': cookie_str
                }
                
                async with session.post(
                    f"{CHECKIN_DOMAIN}/user/checkin",
                    headers=checkin_headers
                ) as checkin_response:
                    # 获取签到响应文本内容
                    checkin_response_text = await checkin_response.text()
                    logger.info(f"签到响应原始内容: {checkin_response_text}")
                    
                    # 尝试解析JSON，无论Content-Type是什么
                    try:
                        checkin_result = json.loads(checkin_response_text)
                        logger.info(f"签到结果: {checkin_result.get('msg', '未知消息')}")
                        
                        # 检测是否已经签到过
                        msg = checkin_result.get('msg', '')
                        already_checked = any(phrase in msg for phrase in ['已签到', '已经签到', '重复签到'])
                        
                        return {
                            "message": msg,
                            "already_checked": already_checked
                        }
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"签到响应不是有效的JSON: {checkin_response_text[:200]}...")
                        raise Exception(f"签到失败: 服务器返回了无效的JSON响应")
                    
    except Exception as e:
        logger.error(f'签到失败: {e}')
        raise Exception(f'签到失败: {str(e)}')

async def send_checkin_notification(bot, message, already_checked, chat_id):
    """发送签到通知到Telegram"""
    # 获取当前北京时间 (UTC+8)
    utc_now = datetime.now(timezone.utc)
    beijing_time = utc_now.astimezone(timezone(timedelta(hours=8)))
    time_string = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
    
    # 掩码显示敏感信息
    def mask_string(s, visible_start=2, visible_end=2):
        if not s:
            return ''
        if len(s) <= visible_start + visible_end:
            return s
        return f"{s[:visible_start]}****{s[-visible_end:]}"
    
    status_emoji = "🔄" if already_checked else "✅"
    status_text = "今日已签到过" if already_checked else "自动签到成功"
    
    notification_text = (
        f"{status_emoji} {status_text}\n\n"
        f"🕒 执行时间: {time_string}\n"
        f"🌐 机场地址: {mask_string(CHECKIN_DOMAIN)}\n"
        f"📧 账户邮箱: {mask_string(CHECKIN_EMAIL)}\n\n"
        f"{message}"
    )
    
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=notification_text,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        logger.info(f"已向群组 {chat_id} 发送签到通知")
    except Exception as e:
        logger.error(f"发送签到通知失败: {e}")

def main():
    """主函数"""
    try:
        # 创建应用
        application = Application.builder().token(BOT_TOKEN).build()
        
        # 添加错误处理器
        application.add_error_handler(error_handler)
        
        # 添加消息处理器
        # 处理所有私聊消息
        application.add_handler(MessageHandler(filters.ChatType.PRIVATE, forward_private_to_group2))
        
        # 处理群组4的控制命令
        application.add_handler(MessageHandler(filters.Chat(chat_id=GROUP4_ID) & filters.TEXT, handle_group4_commands))
        
        # 添加启动后初始化任务
        application.post_init = post_init
        
        # 启动机器人
        logger.info("机器人启动中...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=["message", "edited_message"]
        )
        
    except Exception as e:
        logger.error(f"启动机器人时出错: {e}")
    finally:
        logger.info("机器人已停止")

if __name__ == "__main__":
    main()