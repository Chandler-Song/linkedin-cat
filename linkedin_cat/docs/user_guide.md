# LinkedIn Cat 使用说明

## 简介

LinkedIn Cat 是一个企业级 LinkedIn 自动化工具，支持消息发送、搜索、档案抓取等功能。项目采用模块化架构，提供 Python API 和命令行两种使用方式。

## 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/your-repo/linkedin_cat.git
cd linkedin_cat

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 准备 Cookies

LinkedIn Cat 使用 cookies 进行身份验证。获取方式：

1. 在浏览器中登录 LinkedIn
2. 使用浏览器扩展（如 EditThisCookie）导出 cookies
3. 保存为 JSON 格式的 `cookies.json`

```json
[
  {
    "name": "li_at",
    "value": "your_linkedin_session_cookie",
    "domain": ".linkedin.com",
    "path": "/",
    "secure": true,
    "httpOnly": true
  }
]
```

### 3. 基本使用

#### Python API

```python
from linkedin_cat import LinkedInClient, ContactCache

# 发送消息
with LinkedInClient(cookies_path="cookies.json") as client:
    result = client.send(
        "https://www.linkedin.com/in/someone/",
        "Hi! I'd love to connect."
    )
    print(f"结果: {result.status}")
```

#### 命令行

```bash
# 初始化工作目录
linkedincat init

# 发送消息
linkedincat send cookies.json message.txt urls.txt
```

---

## 核心概念

### 联系人状态流转

```
新联系人 (new)
    ↓ 发送消息
已发送 (sent) → 冷却期 (cooldown, 28天)
    ↓                    ↓
手动阻止 (blocked)    冷却结束 (available)
    ↓                    ↓
永久跳过              可再次发送
```

### 消息模板

支持变量替换：

```
Hi {{name|there}},

I work at {{company}} and would love to connect!

{{signature|Best regards}}
```

- `{{name}}` - 必需变量，未提供则保留原样
- `{{name|default}}` - 带默认值，未提供则使用默认值

---

## 使用场景

### 场景 1: 批量发送连接请求

```python
from linkedin_cat import LinkedInClient, ContactCache, replace_template_variables
import time
import random

# 加载 URL 列表
with open("urls.txt") as f:
    urls = [line.strip() for line in f if line.strip()]

# 加载消息模板
with open("message.txt") as f:
    template = f.read()

# 发送
with ContactCache("./cache") as cache:
    with LinkedInClient(cookies_path="cookies.json") as client:
        for url in urls:
            # 检查是否可以发送
            status = cache.check(url)
            if not status["can_send"]:
                print(f"跳过 {url}: {status['status']}")
                continue
            
            # 发送
            message = replace_template_variables(template, {"name": "there"})
            result = client.send(url, message)
            
            # 记录状态
            if result.status == "success":
                cache.mark_sent(url)
                print(f"✓ {url}")
            else:
                print(f"✗ {url}: {result.error}")
            
            # 随机延迟
            time.sleep(random.uniform(3, 8))
```

### 场景 2: 搜索并筛选目标

```python
from linkedin_cat.wrapper.client import SearchClient
from linkedin_cat import ContactCache

# 搜索
with SearchClient(cookies_path="cookies.json") as client:
    results = client.search_keywords("software engineer san francisco")

# 筛选新联系人
with ContactCache("./cache") as cache:
    new_contacts = [url for url in results if cache.check(url)["can_send"]]

print(f"找到 {len(new_contacts)} 个新联系人")

# 保存到文件
with open("new_contacts.txt", "w") as f:
    f.write("\n".join(new_contacts))
```

### 场景 3: 使用配置文件

创建 `config.yaml`:

```yaml
project_name: "招聘外联"
safety:
  cooldown_days: 14
  max_daily: 30
browser:
  headless: true
template_variables:
  sender_name: "张三"
  company: "科技公司"
```

使用配置：

```python
from linkedin_cat import LinkedinCatConfig, LinkedInClient

config = LinkedinCatConfig.from_yaml("config.yaml")

with LinkedInClient(
    cookies_path="cookies.json",
    headless=config.browser.headless,
    max_retries=config.retry.max_retries
) as client:
    # 使用配置的模板变量
    message = f"Hi! I'm {config.template_variables['sender_name']} from {config.template_variables['company']}."
    result = client.send(url, message)
```

---

## 最佳实践

### 1. 安全发送

- **冷却期**: 默认 28 天，避免骚扰同一用户
- **每日限制**: 建议 30-50 条/天
- **随机延迟**: 每次操作间隔 3-8 秒

### 2. 消息个性化

```python
# 针对不同目标使用不同模板
templates = {
    "engineer": "I noticed your work in {{tech}}...",
    "manager": "Your leadership at {{company}} caught my attention...",
    "recruiter": "I'd love to discuss opportunities..."
}
```

### 3. 错误处理

```python
try:
    result = client.send(url, message)
    if result.status == "success":
        cache.mark_sent(url)
    elif result.status == "blocked":
        cache.block(url, reason="LinkedIn 限制")
except Exception as e:
    logging.error(f"发送失败: {e}")
```

### 4. 进度保存

```python
import json

# 保存进度
progress = {"sent": sent_urls, "failed": failed_urls}
with open("progress.json", "w") as f:
    json.dump(progress, f)

# 恢复进度
with open("progress.json") as f:
    progress = json.load(f)
```

---

## 文件目录结构

建议的工作目录结构：

```
project/
├── cookies.json          # LinkedIn cookies
├── config.yaml           # 配置文件
├── message/             
│   ├── intro.txt         # 介绍消息模板
│   └── follow_up.txt     # 跟进消息模板
├── urls/
│   ├── targets.txt       # 目标 URL 列表
│   └── sent.txt          # 已发送列表
├── cache/                # 缓存目录
│   └── contacts/         # 联系人状态缓存
├── logs/                 # 日志目录
└── output/               # 输出目录
```

---

## 常见问题

### Q: Cookies 多久过期？

A: LinkedIn cookies 通常有效期约 1 年，但如果在其他设备登录可能导致失效。建议定期更新。

### Q: 如何避免账号被限制？

A: 
1. 控制发送频率（每天 30-50 条）
2. 使用随机延迟
3. 避免重复发送给同一人
4. 使用个性化消息

### Q: 无头模式有什么好处？

A: 无头模式不显示浏览器窗口，适合服务器部署和自动化运行，但可能更容易被检测。

### Q: 如何调试发送失败？

A: 
1. 设置 `headless=False` 观察浏览器行为
2. 检查日志文件
3. 使用 `client.bot.driver` 访问底层驱动进行调试
