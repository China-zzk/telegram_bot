Telegram 机器人 GitHub Actions 部署项目

```markdown
# Telegram 机器人 GitHub Actions 部署项目

## 项目简介

这是一个基于 GitHub Actions 的 Telegram 机器人项目，实现了消息转发、关键词检测和 GitHub Action 触发功能。所有代码和运行环境都部署在 GitHub Actions 上，无需额外服务器。

## 功能特性

- 🤖 **私聊消息转发**：用户私聊发送给机器人的消息自动转发到指定群组
- 🔍 **关键词检测**：在监控群组中检测预设关键词，触发消息转发（尚支持检测和转发其他机器人的消息）
- ⚡ **GitHub Action 触发**：授权用户通过 `/open` 命令触发 GitHub Action
- 📊 **完整日志**：提供详细的运行日志和错误报告
- 🔧 **灵活配置**：通过环境变量自定义所有行为
- 🤝 **跨机器人支持**：能够检测和转发其他机器人发送的消息

## 项目结构

```

telegram-bot-project/ ├──.github/ │├── workflows/ ││   └── telegram-bot.yml          # GitHub Actions 工作流配置 │└── ISSUE_TEMPLATE/ │└── bug_report.md             # 问题报告模板 ├──bot_handler.py                    # 主机器人处理脚本 ├──check_env.py                      # 环境变量检查脚本 ├──requirements.txt                  # Python 依赖包列表 └──README.md                         # 项目说明文档

```

## 快速开始

### 1. 创建 Telegram 机器人

1. 在 Telegram 中搜索 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot` 命令并按指示操作
3. 保存生成的 bot token

### 2. 获取聊天和用户 ID

1. **获取群组 ID**：
   - 将机器人添加到所有相关群组
   - 在群组中发送一条消息
   - 访问 `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - 查找聊天 ID (群组 ID 通常是负数，如 `-1001234567890`)

2. **获取用户 ID**：
   - 让用户在 Telegram 中发送消息给 [@userinfobot](https://t.me/userinfobot)
   - 该机器人会回复用户的 ID

### 3. 配置 GitHub Secrets

在 GitHub 仓库的 **Settings → Secrets and variables → Actions** 中添加以下 secrets：

#### 必需的环境变量
- `TELEGRAM_BOT_TOKEN`: 你的机器人 token
- `TARGET_GROUP_ID`: 用户消息转发目标群组的 ID
- `MONITOR_GROUP_ID`: 监控关键词的群组 ID
- `RESPONSE_GROUP_ID`: 响应 `/open` 命令的群组 ID
- `ALLOWED_USER_ID`: 允许触发 GitHub Action 的用户 ID

#### 可选的环境变量
- `KEYWORDS`: 逗号分隔的关键词列表 (例如: "urgent,important,alert")
- `LOG_LEVEL`: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `KEYWORD_MATCH_MODE`: 关键词匹配模式 (contains, exact, startswith, regex)
- `MESSAGE_FORMAT`: 转发消息的格式模板
- `GITHUB_TOKEN`: 用于触发 GitHub Action 的 token (默认使用 `secrets.GITHUB_TOKEN`)
- `FORWARD_BOT_MESSAGES`: 是否转发其他机器人的消息 (true/false，默认为 true)

### 4. 部署项目

1. 将本项目所有文件上传到 GitHub 仓库
2. GitHub Actions 将自动运行工作流
3. 机器人开始监听消息并执行相应功能

## 使用方法

### 私聊消息转发
1. 用户与机器人开始私聊对话
2. 发送任何消息给机器人
3. 消息将自动转发到配置的目标群组

### 关键词检测（支持其他机器人消息）（未解决）
1. 在监控群组中发送包含预设关键词的消息（包括其他机器人发送的消息）
2. 机器人检测到关键词后，将消息转发到响应群组
3. 默认情况下，机器人会检测和转发其他机器人发送的消息

### 触发 GitHub Action
1. 在响应群组中使用授权账户发送 `/open` 命令
2. 机器人将触发配置的 GitHub Action 工作流

## 环境变量详情

### 必需变量
| 变量名 | 描述 | 示例 |
|--------|------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram 机器人令牌 | `1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi` |
| `TARGET_GROUP_ID` | 用户消息转发目标群组 ID | `-1001234567890` |
| `MONITOR_GROUP_ID` | 监控关键词的群组 ID | `-1001234567891` |
| `RESPONSE_GROUP_ID` | 响应 `/open` 命令的群组 ID | `-1001234567892` |
| `ALLOWED_USER_ID` | 允许触发 GitHub Action 的用户 ID | `123456789` |

### 可选变量
| 变量名 | 描述 | 默认值 | 示例 |
|--------|------|--------|------|
| `KEYWORDS` | 触发转发的关键词列表 | 空 | `urgent,important,alert` |
| `LOG_LEVEL` | 日志详细程度 | `INFO` | `DEBUG` |
| `KEYWORD_MATCH_MODE` | 关键词匹配模式 | `contains` | `exact` |
| `MESSAGE_FORMAT` | 转发消息格式模板 | `来自用户 {user_name} 的消息: {message}` | `[{timestamp}] {user_name}: {message}` |
| `GITHUB_TOKEN` | GitHub API 令牌 | `secrets.GITHUB_TOKEN` | `ghp_xxxxxxxxxxxx` |
| `FORWARD_BOT_MESSAGES` | 是否转发其他机器人的消息 | `true` | `false` |

## 支持其他机器人消息的功能说明（尚未完成）

本机器人特别增强了处理其他机器人消息的能力：

1. **检测其他机器人的消息**：默认情况下，机器人会检测并处理其他机器人发送的消息
2. **转发其他机器人的消息**：当其他机器人发送的消息包含关键词时，也会被转发到目标群组
3. **配置选项**：通过 `FORWARD_BOT_MESSAGES` 环境变量可以控制是否处理其他机器人的消息

### 使用示例

假设您有一个监控群组，其中有多个机器人发送状态更新。您可以：

1. 设置关键词如 "error"、"warning"、"critical"
2. 当任何机器人发送包含这些关键词的消息时，您的机器人会自动将其转发到响应群组
3. 这样您就可以在一个地方集中监控所有重要通知

## 故障排除

### 常见问题

1. **机器人不响应消息**
   - 检查 `TELEGRAM_BOT_TOKEN` 是否正确
   - 确认机器人已添加到所有相关群组
   - 确保机器人在群组中有读取消息的权限

2. **消息未转发**
   - 检查群组 ID 是否正确（群组 ID 通常是负数）
   - 确认机器人有权限在群组中发送消息
   - 检查 `FORWARD_BOT_MESSAGES` 设置（如果需要处理其他机器人的消息）

3. **GitHub Action 未触发**
   - 检查 `ALLOWED_USER_ID` 是否正确
   - 确认用户有权限在响应群组中发送消息

4. **无法检测其他机器人的消息（正常情况）**
   - 确保机器人在群组中有管理员权限，或者群组设置允许机器人读取所有消息
   - 检查 `FORWARD_BOT_MESSAGES` 是否设置为 `true`

### 查看日志

1. 在 GitHub 仓库中转到 **Actions** 标签页
2. 选择最近的 **Telegram Bot Handler** 工作流运行
3. 查看详细日志以识别问题

### 环境变量检查

运行环境变量检查脚本：

```bash
python check_env.py
```

开发与贡献

本地开发

1. 克隆项目到本地
2. 安装依赖：pip install -r requirements.txt
3. 设置环境变量
4. 运行机器人：python bot_handler.py

报告问题

使用项目中的问题模板报告 bug 或提出功能建议。

许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

更新日志

v1.1.0 (2025-8-25)

· 新增支持检测和转发其他机器人的消息
· 添加 FORWARD_BOT_MESSAGES 配置选项
· 改进错误处理和日志记录

v1.0.0 (2025-8-24)

· 初始版本发布
· 实现私聊消息转发功能
· 添加关键词检测功能
· 支持 GitHub Action 触发
· 提供完整的环境变量配置

支持

如果您遇到问题或有疑问，请：

1. 查看本 README 中的故障排除部分
2. 检查 GitHub Actions 日志
3. 创建 issue 描述您的问题

免责声明

本项目仅用于教育和学习目的。使用者应遵守 Telegram 的使用条款和当地法律法规。开发者不对滥用此项目造成的任何后果负责。

```
