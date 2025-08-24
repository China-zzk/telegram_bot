# Telegram 机器人项目

这是一个集成了消息转发和命令控制功能的 Telegram 机器人项目，部署在 GitHub Actions 上实现 24/7 运行。

## 项目功能

### 🤖 消息转发机器人
- 自动转发用户发送给机器人的所有消息到指定用户
- 支持文本、图片、文档等多种消息类型
- 每4小时发送健康状态报告
- 崩溃后自动重启机制

### 🎮 命令控制机器人
- 在指定群聊中接收管理命令
- `/run` - 触发 GitHub Actions 工作流重新部署
- `/status` - 检查机器人运行状态
- `/start` - 查看机器人介绍和可用命令
- 仅限群组管理员使用命令功能

## 项目结构

```
telegram-bots/
├── .github/
│   └── workflows/
│       └── telegram_bot.yml    # GitHub Actions 工作流
├── bots/
│   ├── __init__.py             # 包标识文件
│   ├── message_bot.py          # 消息转发机器人
│   └── command_bot.py          # 命令控制机器人
├── requirements.txt            # Python 依赖
├── run_bots.sh                # 启动脚本
└── README.md                  # 项目说明
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd telegram-bots

# 安装依赖
pip install -r requirements.txt
```

### 2. 设置环境变量

在运行前需要设置以下环境变量：

```bash
# 消息转发机器人
export MESSAGE_BOT_TOKEN="你的消息机器人token"
export YOUR_CHAT_ID="你的用户ID"

# 命令控制机器人  
export COMMAND_BOT_TOKEN="你的命令机器人token"
export GITHUB_TOKEN="你的GitHub PAT"
export GITHUB_REPO="username/repository"
```

### 3. 本地运行

```bash
# 方式1: 使用启动脚本（推荐）
chmod +x run_bots.sh
./run_bots.sh

# 方式2: 分别运行
cd bots
python message_bot.py &  # 后台运行消息机器人
python command_bot.py    # 前台运行命令机器人
```

## GitHub Actions 部署

### 1. 设置 Secrets

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加：

| Secret 名称 | 说明 |
|------------|------|
| `MESSAGE_BOT_TOKEN` | 消息转发机器人的 Token |
| `YOUR_CHAT_ID` | 接收消息的用户 ID |
| `COMMAND_BOT_TOKEN` | 命令控制机器人的 Token |
| `GITHUB_TOKEN` | GitHub Personal Access Token |

### 2. 触发部署

部署可以通过以下方式触发：

1. **代码推送**: 推送代码到 main 分支
2. **手动触发**: 在 GitHub Actions 页面手动运行
3. **命令触发**: 在群聊中发送 `/run` 命令

### 3. 群聊设置

1. 将命令机器人添加为群组管理员
2. 确保机器人有读取和发送消息的权限
3. 群聊ID: `-1003073658115`

## 环境变量说明

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `MESSAGE_BOT_TOKEN` | ✅ | 消息转发机器人的 Bot Token |
| `YOUR_CHAT_ID` | ✅ | 接收转发消息的用户 ID |
| `COMMAND_BOT_TOKEN` | ✅ | 命令控制机器人的 Bot Token |
| `GITHUB_TOKEN` | ✅ | GitHub Personal Access Token |
| `GITHUB_REPO` | ✅ | GitHub 仓库名称 (格式: username/repo) |

## 可用命令

在配置的群聊中，管理员可以使用以下命令：

- `/start` - 显示帮助信息
- `/run` - 触发重新部署
- `/status` - 检查机器人状态

## 故障排除

### 常见问题

1. **机器人不响应**
   - 检查 Token 是否正确
   - 确认机器人已添加到群组并设为管理员

2. **消息未转发**
   - 检查 `YOUR_CHAT_ID` 是否正确
   - 确认消息转发机器人隐私设置允许读取消息

3. **命令不工作**
   - 确认发送者是群组管理员
   - 检查 GitHub Token 权限

4. **工作流触发失败**
   - 检查 GitHub Token 是否有 repo 权限
   - 确认仓库名称格式正确

### 日志查看

```bash
# 查看 GitHub Actions 日志
# 在仓库的 Actions 标签页查看运行日志

# 本地运行时可查看控制台输出
```

## 技术支持

如果遇到问题：

1. 检查 GitHub Actions 运行日志
2. 确认所有环境变量已正确设置
3. 验证机器人权限设置
4. 检查网络连接是否正常

## 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

## 更新日志

### v1.0.0
- 初始版本发布
- 集成消息转发和命令控制功能
- 支持 GitHub Actions 自动部署
- 添加健康检查和自动重启机制

---

**注意**: 使用前请确保遵守 Telegram 和 GitHub 的使用条款，并尊重用户隐私。