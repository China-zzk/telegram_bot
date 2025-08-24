# Telegram 机器人设置指南

## 1. 创建 Telegram 机器人
1. 在 Telegram 中搜索 @BotFather
2. 发送 `/newbot` 命令并按指示操作
3. 保存生成的 bot token

## 2. 获取聊天 ID
1. 将机器人添加到所有相关群组
2. 在浏览器中访问: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. 在群组中发送一条消息，然后刷新页面
4. 查找聊天 ID (chat id)

## 3. 获取用户 ID
1. 让用户在 Telegram 中发送消息给 @userinfobot
2. 该机器人会回复用户的 ID

## 4. 配置 GitHub Secrets
在仓库设置中添加以下 secrets:

### 必需的环境变量
- `TELEGRAM_BOT_TOKEN`: 你的机器人 token
- `TARGET_GROUP_ID`: 用户消息转发目标群组的 ID
- `MONITOR_GROUP_ID`: 监控关键词的群组 ID
- `RESPONSE_GROUP_ID`: 响应/open命令的群组 ID
- `ALLOWED_USER_ID`: 允许触发 /open 命令的用户 ID

### 可选的环境变量
- `KEYWORDS`: 逗号分隔的关键词列表 (例如: "urgent,important,alert")
- `LOG_LEVEL`: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `KEYWORD_MATCH_MODE`: 关键词匹配模式 (contains, exact, startswith, regex)
- `MESSAGE_FORMAT`: 转发消息的格式模板
- `GITHUB_TOKEN`: 用于触发 GitHub Action 的 token (默认使用 `secrets.GITHUB_TOKEN`)

## 5. 启用 GitHub Actions
工作流将自动在推送代码后启用，或通过 `/open` 命令触发

## 6. 测试设置
1. 向机器人发送私聊消息，检查是否转发到目标群组
2. 在监控群组中发送包含关键词的消息，检查是否转发到响应群组
3. 在响应群组中使用授权用户发送 `/open` 命令，检查是否触发 GitHub Action

## 故障排除
1. 确保机器人有权限在所有群组中发送消息
2. 检查所有聊天 ID 是否正确（群组 ID 通常是负数）
3. 查看 GitHub Actions 日志以获取详细错误信息
4. 运行 `check_env.py` 脚本验证环境变量设置