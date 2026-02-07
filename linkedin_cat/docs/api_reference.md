# LinkedIn Cat API 参考文档

本文档详细介绍 linkedin_cat 包的所有公共 API。

## 目录

- [核心模块 (core)](#核心模块-core)
- [包装器模块 (wrapper)](#包装器模块-wrapper)
- [缓存模块 (cache)](#缓存模块-cache)
- [配置模块 (config)](#配置模块-config)
- [工具模块 (utils)](#工具模块-utils)
- [CLI 模块 (cli)](#cli-模块-cli)

---

## 核心模块 (core)

### LinkedinBase

基础类，提供 Selenium WebDriver 初始化和 cookie 管理。

```python
from linkedin_cat.core import LinkedinBase

base = LinkedinBase(
    linkedin_cookies_json="cookies.json",  # cookies 文件路径
    headless=False,                        # 是否无头模式
    wait=True                              # 是否等待页面加载
)
```

**属性:**
- `driver` - Selenium WebDriver 实例
- `wait` - WebDriverWait 实例

**方法:**
- `close_driver()` - 关闭浏览器驱动

---

### LinkedinMessage

消息发送类，继承自 LinkedinBase。

```python
from linkedin_cat.core import LinkedinMessage

msg = LinkedinMessage(
    linkedin_cookies_json="cookies.json",
    headless=False,
    button_class=None  # 可选：Connect 按钮的 CSS 类名
)
```

**方法:**

#### send_single_request(url, message, wait=True)

发送单条消息或连接请求。

```python
result = msg.send_single_request(
    "https://www.linkedin.com/in/user/",
    "Hi! Let's connect."
)
# 返回值: "success" | "fail" | 其他状态字符串
```

**参数:**
- `url` (str) - 目标用户的 LinkedIn 主页 URL
- `message` (str) - 消息内容
- `wait` (bool) - 是否等待页面加载完成

**返回:** str - 发送结果状态

---

### LinkedinSearch

搜索和档案抓取类。

```python
from linkedin_cat.core import LinkedinSearch

search = LinkedinSearch(
    linkedin_cookies_json="cookies.json",
    headless=False
)
```

**方法:**

#### search_keywords(keywords, wait=True)

按关键词搜索用户。

```python
results = search.search_keywords("software engineer")
# 返回: List[str] - 搜索到的用户 URL 列表
```

#### search_linkedin_profile(url, save_folder="./linkedin")

抓取单个用户档案。

```python
profile = search.search_linkedin_profile(
    "https://www.linkedin.com/in/user/",
    save_folder="./data"
)
# 返回: Dict - 用户档案数据
```

#### search_linkedin_profile_list(url_list, save_folder="./linkedin")

批量抓取用户档案。

```python
profiles = search.search_linkedin_profile_list(
    ["https://linkedin.com/in/user1", "https://linkedin.com/in/user2"],
    save_folder="./data"
)
```

---

### LinkedIn

主类，继承自 LinkedinMessage，包含所有功能。

```python
from linkedin_cat.core import LinkedIn

bot = LinkedIn(linkedin_cookies_json="cookies.json")
```

---

### extract_profile(url, cookies_json, save_folder)

函数：提取单个档案。

```python
from linkedin_cat.core import extract_profile

profile = extract_profile(
    "https://linkedin.com/in/user",
    "cookies.json",
    "./data"
)
```

### extract_profile_thread_pool(urls, cookies_json, save_folder, max_workers=4)

函数：使用线程池批量提取档案。

```python
from linkedin_cat.core import extract_profile_thread_pool

results = extract_profile_thread_pool(
    ["url1", "url2", "url3"],
    "cookies.json",
    "./data",
    max_workers=4
)
```

---

## 包装器模块 (wrapper)

### LinkedInClient

安全的消息发送客户端，提供上下文管理、自动重试等功能。

```python
from linkedin_cat import LinkedInClient

with LinkedInClient(
    cookies_path="cookies.json",
    headless=False,
    button_class=None,
    max_retries=2,
    retry_delays=(3, 7, 15),
    timeout=30
) as client:
    result = client.send("https://linkedin.com/in/user", "Hello!")
```

**初始化参数:**
- `cookies_path` (str) - cookies 文件路径
- `headless` (bool) - 无头模式，默认 False
- `button_class` (str, optional) - Connect 按钮 CSS 类名
- `max_retries` (int) - 最大重试次数，默认 2
- `retry_delays` (tuple) - 重试延迟（秒），默认 (3, 7, 15)
- `timeout` (int) - 超时时间（秒），默认 30

**方法:**

#### send(url, message, on_retry=None, wait=True) -> SendResult

发送消息。

```python
def on_retry(attempt):
    print(f"重试第 {attempt} 次")

result = client.send(
    "https://linkedin.com/in/user",
    "Hello!",
    on_retry=on_retry
)
```

#### get_stats() -> Dict[str, int]

获取会话统计。

```python
stats = client.get_stats()
# {"sent": 10, "failed": 2, "retried": 3}
```

**属性:**
- `bot` - 底层 LinkedinMessage 实例

---

### SendResult

发送结果数据类。

```python
from linkedin_cat import SendResult

# 属性
result.status       # "success" | "fail" | "blocked" | "timeout" | "retry_exhausted"
result.raw_result   # 原始返回值
result.url          # 目标 URL
result.timestamp    # 时间戳
result.attempts     # 尝试次数
result.screenshot   # 截图路径 (可选)
result.error        # 错误信息 (可选)
```

---

## 缓存模块 (cache)

### ContactCache

联系人状态缓存管理器。

```python
from linkedin_cat import ContactCache

with ContactCache(
    cache_dir="./cache/contacts",
    cooldown_days=28
) as cache:
    status = cache.check("https://linkedin.com/in/user")
```

**初始化参数:**
- `cache_dir` (str) - 缓存目录，默认 "./cache/contacts"
- `cooldown_days` (int) - 冷却期天数，默认 28

**方法:**

#### check(url) -> Dict

检查联系人状态。

```python
status = cache.check("https://linkedin.com/in/user")
# 返回:
# {
#     "can_send": True/False,
#     "status": "new" | "cooldown" | "blocked" | "available",
#     "last_sent": timestamp | None,
#     "cooldown_remaining": seconds | None,
#     "record": dict | None
# }
```

#### mark_sent(url, success=True, metadata=None)

标记已发送。

```python
cache.mark_sent(
    "https://linkedin.com/in/user",
    success=True,
    metadata={"template": "intro_v1"}
)
```

#### block(url, reason="")

永久阻止联系人。

```python
cache.block("https://linkedin.com/in/user", reason="用户拒绝")
```

#### unblock(url)

取消阻止。

#### reset(url)

重置单个联系人状态。

#### reset_all()

重置所有缓存。

#### get_stats() -> Dict

获取缓存统计。

```python
stats = cache.get_stats()
# {
#     "total_contacts": 100,
#     "blocked": 5,
#     "in_cooldown": 30,
#     "available": 65,
#     "cache_size_mb": 0.5
# }
```

#### export_history(filepath)

导出历史记录为 JSON。

#### import_history(filepath)

从 JSON 导入历史记录。

#### get_all_urls() -> List[str]

获取所有跟踪的 URL。

---

## 配置模块 (config)

### LinkedinCatConfig

主配置类。

```python
from linkedin_cat import LinkedinCatConfig

# 从 YAML 加载
config = LinkedinCatConfig.from_yaml("config.yaml")

# 直接创建
config = LinkedinCatConfig(
    project_name="MyProject",
    safety=SafetyConfig(cooldown_days=14),
    browser=BrowserConfig(headless=True)
)

# 保存配置
config.save("config.yaml")
```

**属性:**
- `project_name` (str) - 项目名称
- `version` (str) - 版本号
- `safety` (SafetyConfig) - 安全配置
- `retry` (RetryConfig) - 重试配置
- `delay` (DelayConfig) - 延迟配置
- `browser` (BrowserConfig) - 浏览器配置
- `cache_dir` (str) - 缓存目录
- `log_dir` (str) - 日志目录
- `message_dir` (str) - 消息模板目录
- `urls_dir` (str) - URL 列表目录
- `template_variables` (Dict) - 模板变量

**方法:**
- `from_yaml(path)` - 从 YAML 加载
- `save(path)` - 保存到 YAML
- `get_cache_path()` - 获取缓存路径
- `get_log_path()` - 获取日志路径
- `get_message_path()` - 获取消息路径
- `get_urls_path()` - 获取 URL 路径

---

### SafetyConfig

```python
from linkedin_cat import SafetyConfig

safety = SafetyConfig(
    cooldown_days=28,      # 冷却期
    max_daily=50,          # 每日最大发送
    auto_stop_on_limit=True  # 达到限制时自动停止
)
```

### RetryConfig

```python
from linkedin_cat import RetryConfig

retry = RetryConfig(
    max_retries=2,
    delays=[3, 7, 15]
)
```

### DelayConfig

```python
from linkedin_cat import DelayConfig

delay = DelayConfig(
    min_seconds=3.0,
    max_seconds=8.0,
    after_fail=10.0
)
```

### BrowserConfig

```python
from linkedin_cat import BrowserConfig

browser = BrowserConfig(
    headless=False,
    timeout=30,
    window_size=(1920, 1080)
)
```

---

## 工具模块 (utils)

### replace_template_variables(template, variables)

替换模板中的变量。

```python
from linkedin_cat import replace_template_variables

message = replace_template_variables(
    "Hi {{name|there}}! I work at {{company}}.",
    {"name": "John", "company": "Google"}
)
# "Hi John! I work at Google."
```

**变量语法:**
- `{{name}}` - 必需变量
- `{{name|default}}` - 带默认值的变量

---

### normalize_url(url)

标准化 LinkedIn URL。

```python
from linkedin_cat import normalize_url

normalized = normalize_url("https://www.LinkedIn.com/in/User/?ref=123")
# "https://www.linkedin.com/in/user"
```

---

## CLI 模块 (cli)

### 命令行使用

```bash
# 查看帮助
linkedincat --help

# 初始化工作目录
linkedincat init

# 发送消息
linkedincat send cookies.json message.txt urls.txt

# 查看状态
linkedincat status urls.txt

# 重置缓存
linkedincat reset --url https://linkedin.com/in/user
linkedincat reset --all --force

# 导出历史
linkedincat export output.json

# 查看版本
linkedincat version
```

### 编程方式调用

```python
from linkedin_cat import cli_app, run_cli

# 获取 Typer app 实例
app = cli_app

# 运行 CLI
run_cli()
```
