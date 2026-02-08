# LinkedIn Cat

> 一个LinkedIn 自动化工具包，支持消息发送、搜索、档案抓取等功能。

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [详细使用指南](#详细使用指南)
- [配置说明](#配置说明)
- [CLI 命令行工具](#cli-命令行工具)
- [API 参考](#api-参考)
- [常见问题](#常见问题)
- [开发者指南](#开发者指南)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

---

## 功能特性

- **消息发送** - 批量发送连接请求和私信，支持消息模板变量替换
- **用户搜索** - 按关键词搜索 LinkedIn 用户
- **档案抓取** - 提取用户详细资料（教育、工作经历、技能等）
- **智能缓存** - 避免重复发送，支持冷却期管理
- **CLI 工具** - 现代化命令行界面，开箱即用
- **安全机制** - 内置随机延迟、重试策略、发送限制

---

## 快速开始

### 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | 3.7+ | 推荐 3.9+ |
| Chrome | 最新版 | 需与 ChromeDriver 匹配 |
| ChromeDriver | 与 Chrome 版本匹配 | 或使用 webdriver-manager 自动管理 |

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/your-username/linkedin-cat.git
cd linkedin-cat

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 准备 Cookies

由于 LinkedIn 的反爬机制，本项目使用 Cookie 认证：

1. 在浏览器中登录 LinkedIn
2. 使用浏览器扩展（如 [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)）导出 Cookies
3. 保存为 `cookies.json` 文件

**Cookies 文件格式：**

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

> **重要提示：** 确保导出的 cookies 包含 `li_at` cookie，这是 LinkedIn 的会话凭证。

### 3. 第一次使用

**方式一：Python API**

```python
from linkedin_cat import LinkedInClient, ContactCache

# 发送连接请求
with LinkedInClient(cookies_path="cookies.json") as client:
    result = client.send(
        "https://www.linkedin.com/in/someone/",
        "Hi! I'd love to connect with you."
    )
    print(f"发送结果: {result.status}")
```

**方式二：命令行**

```bash
# 初始化工作目录
python -m linkedin_cat.cli.app init

# 发送消息
python -m linkedin_cat.cli.app send cookies.json message.txt urls.txt
```

---

## 项目结构

```
linkedin_cat/
├── __init__.py          # 主入口，导出公共 API
├── requirements.txt     # 依赖清单
├── core/                # 核心 Selenium 引擎
│   ├── base.py          # 基础类，WebDriver 管理
│   ├── message.py       # 消息发送逻辑
│   ├── search.py        # 搜索功能
│   ├── profile.py       # 档案提取
│   ├── api.py           # REST API 接口
│   └── helper.py        # 辅助函数
├── wrapper/             # 安全包装器
│   └── client.py        # LinkedInClient, SearchClient
├── cache/               # 缓存管理
│   └── contact_cache.py # 基于 DiskCache 的状态管理
├── config/              # 配置系统
│   └── settings.py      # Pydantic 配置模型
├── utils/               # 工具函数
│   └── template.py      # 模板变量替换
├── cli/                 # 命令行界面
│   └── app.py           # Typer CLI 应用
├── tests/               # 测试用例
├── examples/            # 示例代码
└── docs/                # 详细文档
```

---

## 详细使用指南

### 场景 1：批量发送连接请求

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
            
            # 替换模板变量
            message = replace_template_variables(template, {"name": "there"})
            result = client.send(url, message)
            
            # 记录状态
            if result.status == "success":
                cache.mark_sent(url)
                print(f"✓ 成功: {url}")
            else:
                print(f"✗ 失败: {url} - {result.error}")
            
            # 随机延迟 (重要!)
            time.sleep(random.uniform(3, 8))
```

### 场景 2：搜索用户

```python
from linkedin_cat.core import LinkedinSearch

search = LinkedinSearch(
    linkedin_cookies_json="cookies.json",
    headless=False  # 设为 True 可隐藏浏览器
)

# 按关键词搜索
results = search.search_keywords("Python Developer San Francisco")
print(f"找到 {len(results)} 个用户")

# 抓取档案详情
for url in results[:5]:
    profile = search.search_linkedin_profile(url, save_folder="./profiles")
    print(f"已保存: {profile.get('name', 'Unknown')}")

search.close_driver()
```

### 场景 3：使用消息模板

**模板语法：**

```
Hi {{name|there}},

I noticed your work at {{company|your company}}. 
I'd love to connect!

{{signature|Best regards}}
```

- `{{variable}}` - 必需变量
- `{{variable|default}}` - 带默认值的变量

**使用示例：**

```python
from linkedin_cat import replace_template_variables

template = "Hi {{name|there}}, I work at {{company}}."
message = replace_template_variables(template, {
    "name": "John",
    "company": "Google"
})
# 输出: "Hi John, I work at Google."
```

### 场景 4：使用配置文件

创建 `config.yaml`：

```yaml
project_name: "招聘外联"
safety:
  cooldown_days: 14
  max_daily: 30
browser:
  headless: true
  timeout: 30
template_variables:
  sender_name: "张三"
  company: "科技公司"
```

加载配置：

```python
from linkedin_cat import LinkedinCatConfig, LinkedInClient

config = LinkedinCatConfig.from_yaml("config.yaml")

with LinkedInClient(
    cookies_path="cookies.json",
    headless=config.browser.headless
) as client:
    pass
```

---

## 配置说明

### 完整配置选项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `safety.cooldown_days` | int | 28 | 同一联系人的冷却期天数 |
| `safety.max_daily` | int | 50 | 每日最大发送数量 |
| `retry.max_retries` | int | 2 | 最大重试次数 |
| `retry.delays` | list | [3,7,15] | 重试延迟（秒） |
| `delay.min_seconds` | float | 3.0 | 最小操作延迟 |
| `delay.max_seconds` | float | 8.0 | 最大操作延迟 |
| `browser.headless` | bool | false | 无头模式 |
| `browser.timeout` | int | 30 | 操作超时（秒） |

### 环境变量

```bash
export LINKEDINCAT_HEADLESS=true
export LINKEDINCAT_MAX_DAILY=100
export LINKEDINCAT_COOLDOWN_DAYS=14
```

---

## CLI 命令行工具

### 可用命令

| 命令 | 说明 |
|------|------|
| `init` | 初始化工作目录 |
| `send` | 发送消息/连接请求 |
| `status` | 查看联系人状态 |
| `reset` | 重置缓存状态 |
| `export` | 导出历史记录 |
| `version` | 显示版本信息 |

### 使用示例

```bash
# 初始化项目目录
python -m linkedin_cat.cli.app init --path ./my_project

# 发送消息（无头模式，限制 30 条）
python -m linkedin_cat.cli.app send cookies.json message.txt urls.txt --headless --max 30

# 干运行模式（不实际发送）
python -m linkedin_cat.cli.app send cookies.json message.txt urls.txt --dry-run

# 查看缓存统计
python -m linkedin_cat.cli.app status --stats

# 重置单个联系人
python -m linkedin_cat.cli.app reset --url "https://linkedin.com/in/user"

# 导出历史记录
python -m linkedin_cat.cli.app export history.json
```

### 文件格式

**urls.txt（URL 列表）：**

```text
# 这是注释
https://www.linkedin.com/in/user-1/
https://www.linkedin.com/in/user-2/
https://www.linkedin.com/in/user-3/
```

**message.txt（消息模板）：**

```text
Hi {{name|there}},

I noticed your experience at {{company|your company}}.
I'd love to connect!

Best regards
```

---

## API 参考

### LinkedInClient

安全的消息发送客户端，提供上下文管理、自动重试等功能。

```python
from linkedin_cat import LinkedInClient

with LinkedInClient(
    cookies_path="cookies.json",  # cookies 文件路径
    headless=False,                # 无头模式
    max_retries=2,                 # 最大重试次数
    retry_delays=(3, 7, 15),       # 重试延迟
    timeout=30                     # 超时时间
) as client:
    result = client.send(url, message)
```

**SendResult 返回值：**

| 属性 | 类型 | 说明 |
|------|------|------|
| `status` | str | "success" / "fail" / "blocked" / "timeout" |
| `url` | str | 目标 URL |
| `attempts` | int | 尝试次数 |
| `error` | str | 错误信息（如有） |

### ContactCache

联系人状态缓存管理器。

```python
from linkedin_cat import ContactCache

with ContactCache(cache_dir="./cache", cooldown_days=28) as cache:
    status = cache.check(url)  # 检查状态
    cache.mark_sent(url)       # 标记已发送
    cache.block(url)           # 阻止联系人
    stats = cache.get_stats()  # 获取统计
```

完整 API 文档请查看 [docs/api_reference.md](linkedin_cat/docs/api_reference.md)

---

## 常见问题

### Q: Cookies 多久过期？

**A:** LinkedIn cookies 通常有效期约 1 年，但在其他设备登录可能导致失效。建议定期更新。

### Q: 如何避免账号被限制？

**A:**
1. 控制发送频率（每天 30-50 条）
2. 使用随机延迟（3-8 秒）
3. 避免重复发送给同一人
4. 使用个性化消息

### Q: 发送全部失败怎么办？

**A:**
1. 检查 cookies 是否过期
2. 关闭无头模式观察浏览器：`headless=False`
3. 检查 LinkedIn 是否更新了界面

### Q: ChromeDriver 版本不匹配？

**A:** 安装 webdriver-manager 自动管理：`pip install webdriver-manager`

更多故障排除请查看 [docs/troubleshooting.md](linkedin_cat/docs/troubleshooting.md)

---

## 开发者指南

### 设置开发环境

```bash
git clone https://github.com/your-username/linkedin-cat.git
cd linkedin-cat
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

### 运行测试

```bash
pytest linkedin_cat/tests/                    # 运行所有测试
pytest --cov=linkedin_cat linkedin_cat/tests/ # 带覆盖率
pytest -m "not selenium"                      # 跳过 Selenium 测试
```

### 代码风格

```bash
black linkedin_cat/   # 格式化
flake8 linkedin_cat/  # 检查
```

详细开发指南请查看 [docs/developer_guide.md](linkedin_cat/docs/developer_guide.md)

---

## 贡献指南

1. **Fork** 项目
2. **创建分支**: `git checkout -b feature/your-feature`
3. **提交更改**: `git commit -m "feat: add new feature"`
4. **推送**: `git push origin feature/your-feature`
5. **创建 Pull Request**

### Commit 消息规范

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `test`: 测试相关
- `refactor`: 代码重构

详细贡献指南请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 最佳实践

1. **安全发送** - 冷却期 28 天，每日限制 30-50 条，随机延迟 3-8 秒
2. **消息个性化** - 使用模板变量，避免千篇一律
3. **错误处理** - 始终检查返回状态，记录失败 URL
4. **资源管理** - 使用 `with` 语句，定期保存进度

---

## 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 相关链接

- [API 参考文档](linkedin_cat/docs/api_reference.md)
- [使用说明](linkedin_cat/docs/user_guide.md)
- [配置选项](linkedin_cat/docs/configuration.md)
- [CLI 命令详解](linkedin_cat/docs/cli_commands.md)
- [故障排除](linkedin_cat/docs/troubleshooting.md)
- [开发者指南](linkedin_cat/docs/developer_guide.md)

---

**声明：** 本工具仅供学习和研究使用。请遵守 LinkedIn 的服务条款，合理使用自动化功能。
