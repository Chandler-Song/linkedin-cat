# LinkedIn Cat 故障排除指南

本指南帮助解决使用 LinkedIn Cat 时遇到的常见问题。

## 目录

- [安装问题](#安装问题)
- [Cookies 相关](#cookies-相关)
- [发送失败](#发送失败)
- [Selenium/浏览器问题](#selenium浏览器问题)
- [缓存问题](#缓存问题)
- [性能问题](#性能问题)
- [常见错误代码](#常见错误代码)

---

## 安装问题

### 问题：ModuleNotFoundError

**症状:**
```
ModuleNotFoundError: No module named 'selenium'
```

**解决方案:**
```bash
# 确保在虚拟环境中
source .venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt

# 或单独安装缺失的包
pip install selenium colorama pydash beautifulsoup4 pandas diskcache pydantic pyyaml typer rich
```

---

### 问题：ChromeDriver 版本不匹配

**症状:**
```
selenium.common.exceptions.SessionNotCreatedException: 
Message: session not created: This version of ChromeDriver only supports Chrome version XX
```

**解决方案:**

1. 检查 Chrome 版本：`chrome://version/`
2. 下载对应版本的 ChromeDriver：https://chromedriver.chromium.org/downloads
3. 或使用 webdriver-manager 自动管理：

```bash
pip install webdriver-manager
```

```python
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(ChromeDriverManager().install())
```

---

## Cookies 相关

### 问题：Cookies 过期

**症状:**
- 登录后立即被重定向到登录页
- 发送全部失败

**解决方案:**

1. 重新登录 LinkedIn 获取新 cookies
2. 确保导出的 cookies 包含 `li_at` cookie
3. 使用浏览器扩展正确导出

**验证 cookies:**
```python
import json

with open("cookies.json") as f:
    cookies = json.load(f)

# 检查关键 cookie
li_at = next((c for c in cookies if c["name"] == "li_at"), None)
if li_at:
    print(f"li_at cookie 存在，长度: {len(li_at['value'])}")
else:
    print("警告: 缺少 li_at cookie!")
```

---

### 问题：Cookies 格式错误

**症状:**
```
json.decoder.JSONDecodeError: Expecting value
```

**解决方案:**

确保 cookies.json 格式正确：

```json
[
  {
    "name": "li_at",
    "value": "AQE...",
    "domain": ".linkedin.com",
    "path": "/",
    "secure": true,
    "httpOnly": true
  }
]
```

---

## 发送失败

### 问题：所有发送都返回 "fail"

**可能原因及解决方案:**

1. **Cookies 失效**
   - 重新获取 cookies

2. **LinkedIn 界面更新**
   - 检查按钮 CSS 类名是否改变
   - 使用 `button_class` 参数指定新的类名

3. **账号被限制**
   - 暂停发送 24-48 小时
   - 减少每日发送量

4. **网络问题**
   - 检查网络连接
   - 尝试增加超时时间

**调试方法:**
```python
# 关闭无头模式观察行为
with LinkedInClient(cookies_path="cookies.json", headless=False) as client:
    result = client.send(url, message)
    # 观察浏览器行为
```

---

### 问题："Connect" 按钮找不到

**症状:**
- 页面加载正常但无法点击按钮

**解决方案:**

1. LinkedIn 可能更新了按钮类名
2. 检查页面手动确认按钮位置
3. 更新 `button_class` 参数

```python
# 尝试不同的按钮类名
client = LinkedInClient(
    cookies_path="cookies.json",
    button_class="artdeco-button--primary"  # 或其他类名
)
```

---

### 问题：消息发送成功但没有效果

**可能原因:**

1. 对方已经是联系人
2. 对方设置了消息限制
3. 已达到周请求限制

**检查方法:**
```python
# 检查缓存确认状态
cache = ContactCache("./cache")
status = cache.check(url)
print(f"状态: {status}")
```

---

## Selenium/浏览器问题

### 问题：浏览器无法启动

**症状:**
```
selenium.common.exceptions.WebDriverException: 
Message: unknown error: cannot find Chrome binary
```

**解决方案:**

1. 确保已安装 Chrome 浏览器
2. 检查 Chrome 安装路径
3. 使用环境变量指定路径

```python
from selenium.webdriver.chrome.options import Options

options = Options()
options.binary_location = "/usr/bin/google-chrome"  # Linux
# options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # Mac
```

---

### 问题：无头模式不工作

**症状:**
- 在服务器上无法运行
- 报错提示缺少显示

**解决方案:**

```python
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
```

---

### 问题：页面加载超时

**症状:**
```
selenium.common.exceptions.TimeoutException: Message: timeout
```

**解决方案:**

1. 增加超时时间
```python
client = LinkedInClient(cookies_path="cookies.json", timeout=60)
```

2. 检查网络连接

3. LinkedIn 可能限制了访问速度，增加延迟

---

## 缓存问题

### 问题：缓存损坏

**症状:**
- 无法读取缓存
- 状态不正确

**解决方案:**

```python
# 导出现有数据
cache = ContactCache("./cache")
cache.export_history("backup.json")

# 清除缓存
cache.reset_all()

# 重新导入
cache.import_history("backup.json")
```

或直接删除缓存目录：
```bash
rm -rf ./cache/contacts/
```

---

### 问题：冷却期计算错误

**可能原因:**
- 时区问题
- 系统时间不正确

**解决方案:**
```python
import time
print(f"当前时间戳: {time.time()}")

# 手动重置特定联系人
cache = ContactCache("./cache")
cache.reset("https://linkedin.com/in/user")
```

---

## 性能问题

### 问题：运行速度慢

**优化建议:**

1. **使用无头模式**
```python
client = LinkedInClient(headless=True)
```

2. **减少等待时间**
```python
# 仅在必要时等待
client.send(url, message, wait=False)
```

3. **批量处理时使用适当延迟**
```python
import random
time.sleep(random.uniform(2, 5))  # 而不是 5-10 秒
```

---

### 问题：内存使用过高

**解决方案:**

1. 确保正确关闭浏览器
```python
# 使用上下文管理器
with LinkedInClient(...) as client:
    # 操作
pass  # 自动关闭
```

2. 定期重启会话
```python
# 每 50 条重启一次
for i, url in enumerate(urls):
    if i % 50 == 0 and i > 0:
        # 重新初始化客户端
        pass
```

---

## 常见错误代码

### SendResult.status 含义

| 状态 | 说明 | 处理方式 |
|------|------|----------|
| `success` | 发送成功 | 记录到缓存 |
| `fail` | 发送失败 | 检查原因，可能需要重试 |
| `blocked` | 被 LinkedIn 阻止 | 暂停发送，等待限制解除 |
| `timeout` | 操作超时 | 增加超时时间，检查网络 |
| `retry_exhausted` | 重试耗尽 | 检查 cookies 和网络 |

---

### 错误日志分析

查看日志文件获取详细信息：

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='debug.log'
)
```

常见日志关键词：
- `timeout` - 超时问题
- `element not found` - 页面元素问题
- `cookie` - 认证问题
- `rate limit` - 速率限制

---

## 获取帮助

如果以上方法都无法解决问题：

1. **检查项目 Issues**
   - 搜索是否有类似问题

2. **收集信息**
   - Python 版本
   - 操作系统
   - Chrome 版本
   - 完整错误日志

3. **提交 Issue**
   - 描述问题
   - 提供复现步骤
   - 附加相关日志（注意脱敏）

---

## 预防措施

### 定期维护

```bash
# 每周更新依赖
pip install --upgrade -r requirements.txt

# 定期备份缓存
linkedincat export backup_$(date +%Y%m%d).json

# 检查 cookies 有效性
python -c "from linkedin_cat import LinkedInClient; print('OK')"
```

### 监控建议

```python
# 添加成功率监控
stats = client.get_stats()
success_rate = stats["sent"] / (stats["sent"] + stats["failed"]) * 100
if success_rate < 50:
    logging.warning(f"成功率过低: {success_rate:.1f}%")
```
