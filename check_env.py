import os

required_vars = [
    'TELEGRAM_BOT_TOKEN',
    'TARGET_GROUP_ID',
    'MONITOR_GROUP_ID',
    'RESPONSE_GROUP_ID',
    'ALLOWED_USER_ID'
]

optional_vars = [
    'KEYWORDS',
    'LOG_LEVEL',
    'KEYWORD_MATCH_MODE',
    'MESSAGE_FORMAT',
    'FORWARD_BOT_MESSAGES',
    'GITHUB_TOKEN'
]

print("环境变量检查:")
print("=" * 50)

all_required_set = True

# 检查必需变量
print("必需的环境变量:")
for var in required_vars:
    value = os.environ.get(var)
    if value:
        print(f"✓ {var}: 已设置")
    else:
        print(f"✗ {var}: 未设置")
        all_required_set = False

print("\n可选的环境变量:")
# 检查可选变量
for var in optional_vars:
    value = os.environ.get(var)
    if value:
        if var == 'FORWARD_BOT_MESSAGES':
            print(f"✓ {var}: {value} (将{'转发' if value.lower() == 'true' else '不转发'}其他机器人的消息)")
        else:
            print(f"✓ {var}: 已设置")
    else:
        if var == 'FORWARD_BOT_MESSAGES':
            print(f"○ {var}: 未设置 (使用默认值: true - 将转发其他机器人的消息)")
        else:
            print(f"○ {var}: 未设置 (使用默认值)")

print("\n" + "=" * 50)
if all_required_set:
    print("✓ 所有必需环境变量已正确设置!")
else:
    print("✗ 错误: 有些必需环境变量未设置，请检查 GitHub Secrets 配置")

# 显示当前关键词设置
keywords = os.environ.get('KEYWORDS', '')
if keywords:
    keyword_list = [k.strip() for k in keywords.split(',') if k.strip()]
    print(f"\n关键词列表: {keyword_list}")
else:
    print("\n关键词: 未设置 (关键词检测功能将禁用)")
