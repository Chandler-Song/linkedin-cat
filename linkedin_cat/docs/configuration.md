# LinkedIn Cat 配置选项说明

## 配置文件格式

LinkedIn Cat 使用 YAML 格式的配置文件。默认文件名为 `config.yaml`。

## 完整配置示例

```yaml
# ================================================
# LinkedIn Cat 配置文件
# ================================================

# 项目基本信息
project_name: "LinkedinCat"
version: "1.0.0"

# ================================================
# 安全配置
# ================================================
safety:
  # 联系人冷却期（天）
  # 同一个联系人发送后，多少天内不再发送
  # 默认: 28
  cooldown_days: 28
  
  # 每日最大发送数量
  # 默认: 50
  max_daily: 50
  
  # 达到每日限制时是否自动停止
  # 默认: true
  auto_stop_on_limit: true

# ================================================
# 重试配置
# ================================================
retry:
  # 最大重试次数
  # 默认: 2
  max_retries: 2
  
  # 重试延迟时间（秒）
  # 使用指数退避策略
  # 默认: [3, 7, 15]
  delays:
    - 3
    - 7
    - 15

# ================================================
# 延迟配置
# ================================================
delay:
  # 每次操作之间的最小延迟（秒）
  # 默认: 3.0
  min_seconds: 3.0
  
  # 每次操作之间的最大延迟（秒）
  # 默认: 8.0
  max_seconds: 8.0
  
  # 发送失败后的额外等待时间（秒）
  # 默认: 10.0
  after_fail: 10.0

# ================================================
# 浏览器配置
# ================================================
browser:
  # 是否使用无头模式
  # true: 不显示浏览器窗口（适合服务器）
  # false: 显示浏览器窗口（适合调试）
  # 默认: false
  headless: false
  
  # 操作超时时间（秒）
  # 默认: 30
  timeout: 30
  
  # 浏览器窗口大小 [宽度, 高度]
  # 默认: [1920, 1080]
  window_size:
    - 1920
    - 1080

# ================================================
# 路径配置
# ================================================
# 缓存目录 - 存储联系人状态
cache_dir: "./cache"

# 日志目录
log_dir: "./logs"

# 消息模板目录
message_dir: "./message"

# URL 列表目录
urls_dir: "./urls"

# ================================================
# 模板变量
# ================================================
# 这些变量可以在消息模板中使用
# 使用方式: {{variable_name}} 或 {{variable_name|default}}
template_variables:
  sender_name: "Your Name"
  sender_title: "Your Title"
  company: "Your Company"
  signature: |
    Best regards,
    Your Name
```

---

## 配置项详解

### safety（安全配置）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `cooldown_days` | int | 28 | 同一联系人的冷却期天数 |
| `max_daily` | int | 50 | 每日最大发送数量 |
| `auto_stop_on_limit` | bool | true | 达到限制时是否自动停止 |

**建议值:**
- 保守: `cooldown_days: 30`, `max_daily: 30`
- 标准: `cooldown_days: 28`, `max_daily: 50`
- 激进: `cooldown_days: 14`, `max_daily: 100` （风险较高）

---

### retry（重试配置）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `max_retries` | int | 2 | 最大重试次数 |
| `delays` | list[int] | [3, 7, 15] | 每次重试的延迟（秒） |

**工作原理:**
```
第 1 次尝试 → 失败 → 等待 3 秒
第 2 次尝试 → 失败 → 等待 7 秒
第 3 次尝试 → 失败 → 返回失败结果
```

---

### delay（延迟配置）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `min_seconds` | float | 3.0 | 最小延迟时间（秒） |
| `max_seconds` | float | 8.0 | 最大延迟时间（秒） |
| `after_fail` | float | 10.0 | 失败后额外等待（秒） |

每次操作会在 `min_seconds` 和 `max_seconds` 之间随机选择一个延迟时间，模拟人工操作。

---

### browser（浏览器配置）

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `headless` | bool | false | 无头模式开关 |
| `timeout` | int | 30 | 操作超时（秒） |
| `window_size` | list[int] | [1920, 1080] | 窗口尺寸 |

**无头模式说明:**
- `true`: 浏览器在后台运行，不显示窗口，适合服务器部署
- `false`: 显示浏览器窗口，适合本地开发和调试

---

### 路径配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `cache_dir` | "./cache" | 缓存目录，存储联系人状态 |
| `log_dir` | "./logs" | 日志目录 |
| `message_dir` | "./message" | 消息模板目录 |
| `urls_dir` | "./urls" | URL 列表目录 |

---

### template_variables（模板变量）

在消息模板中可以使用的变量：

```yaml
template_variables:
  name: "张三"
  title: "技术经理"
  company: "科技公司"
```

在模板中使用：

```
Hi {{recipient_name|there}},

I'm {{name}} from {{company}}.
```

---

## 环境变量覆盖

支持通过环境变量覆盖配置：

| 环境变量 | 对应配置 |
|----------|----------|
| `LINKEDINCAT_HEADLESS` | `browser.headless` |
| `LINKEDINCAT_COOLDOWN_DAYS` | `safety.cooldown_days` |
| `LINKEDINCAT_MAX_DAILY` | `safety.max_daily` |
| `LINKEDINCAT_CACHE_DIR` | `cache_dir` |
| `LINKEDINCAT_LOG_DIR` | `log_dir` |

示例：

```bash
export LINKEDINCAT_HEADLESS=true
export LINKEDINCAT_MAX_DAILY=100
linkedincat send cookies.json message.txt urls.txt
```

---

## 配置加载优先级

1. 命令行参数（最高）
2. 环境变量
3. 配置文件
4. 默认值（最低）

---

## 多环境配置

可以为不同环境创建不同的配置文件：

```
config/
├── config.yaml          # 默认配置
├── config.dev.yaml      # 开发环境
├── config.prod.yaml     # 生产环境
└── config.test.yaml     # 测试环境
```

加载指定配置：

```python
from linkedin_cat import LinkedinCatConfig

config = LinkedinCatConfig.from_yaml("config/config.prod.yaml")
```
