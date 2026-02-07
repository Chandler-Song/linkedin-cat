# LinkedIn Cat - LinkedIn 自动化与抓取工具

LinkedIn Cat 是一个基于 Python 的自动化工具包，旨在通过 Selenium 和 API 两种方式简化 LinkedIn 的操作。它支持自动搜索、个性化好友申请、私信发送以及详尽的个人档案抓取。

## 1. 项目结构

本项目由多个核心模块组成，每个模块负责特定的 LinkedIn 交互逻辑：

- **`base.py`**: 核心基础类 `LinkedinBase`，负责 Selenium 驱动初始化、基于 Cookie 的登录状态维持及基础页面操作（滚动、随机等待）。
- **`search.py`**: 提供 `LinkedinSearch` 类，支持关键词搜索、结果解析以及批量个人档案处理。
- **`message.py`**: 核心交互类 `LinkedinMessage`，实现自动发送好友申请（支持变量替换）、检查好友状态及发送私信。
- **`profile.py`**: 详尽的档案提取逻辑，支持抓取简介、关于、工作经历、教育背景、技能、荣誉等 10+ 个维度的数据。
- **`api.py`**: 提供了一套基于 REST API 的交互方案，绕过浏览器界面直接获取网络、消息及档案数据。
- **`helper.py`**: 包含 Selenium 辅助函数（元素定位、文本提取、JSON 保存）及 URL 解码工具。

## 2. 详细部署教程

### 环境要求
- **Python**: 3.7+
- **Chrome 浏览器**: 建议最新版
- **ChromeDriver**: 需与浏览器版本匹配
- **依赖项**: `selenium`, `pandas`, `requests`, `colorama`, `pydash`, `beautifulsoup4`

### 安装步骤
1. 克隆或下载本项目到本地。
2. 安装必要的 Python 库：
   ```bash
   pip install selenium pandas requests colorama pydash beautifulsoup4
   ```

### 准备认证信息
由于 LinkedIn 的高强度反爬机制，本项目采用 Cookie 认证：
1. 在浏览器中手动登录 LinkedIn。
2. 使用插件（如 "EditThisCookie"）导出 LinkedIn 的 Cookies。
3. 将 Cookies 保存为项目根目录下的 `linkedin_cookies.json`。

### 使用示例

#### 示例 1：搜索并抓取个人档案
```python
from linkedin_cat.search import LinkedinSearch

# 初始化（需提供 cookies 文件路径）
searcher = LinkedinSearch(linkedin_cookies_json="linkedin_cookies.json", headless=False)

# 执行关键词搜索
results = searcher.search_keywords("Python Developer")

# 抓取特定档案并保存为 JSON
for profile in results:
    searcher.search_linkedin_profile(profile['linkedin_url'], save_folder='./profiles')
```

#### 示例 2：发送个性化好友申请
```python
from linkedin_cat.message import LinkedinMessage

messenger = LinkedinMessage(linkedin_cookies_json="linkedin_cookies.json", button_class="your_button_class")

# [FIRSTNAME] 和 [FULLNAME] 将自动替换为对方的姓名
msg_template = "Hi [FIRSTNAME], I'd like to connect with you!"
messenger.send_single_request("https://www.linkedin.com/in/someone/", msg_template)
```

## 3. 典型错误及现象

### 3.1 认证失败
- **现象**: 终端显示 `No cookies file found, please login first`。
- **原因**: 根目录下缺少 `linkedin_cookies.json` 文件或路径配置错误。
- **报错原文示例**: `Fore.RED + "No cookies file found..."`

### 3.2 元素定位失败 (XPath 失效)
- **现象**: `Error: Message: no such element: Unable to locate element...`。
- **原因**: LinkedIn 经常更新其网页结构或 class 名称（如 `message_button_class`），导致预设的 XPath 失效。

### 3.3 消息长度受限
- **现象**: 程序抛出 `BaseException: Message too long (X characters). Max size is 300 characters`。
- **原因**: LinkedIn 好友申请的消息限制为 300 字符。

## 4. 注意事项

- **原理说明**: 
    - 本项目通过 `base.py` 中的 `driver.add_cookie()` 方法注入登录凭证，规避了直接处理登录页面的复杂逻辑（如验证码）。
    - 脚本内内置了 `short_wait`, `medium_wait`, `long_wait` 等随机等待机制，模拟人类行为以降低被封禁风险。
- **规避方案**:
    - **速率限制**: 建议在批量操作之间增加额外的 `time.sleep()`，避免在短时间内发送过快。
    - **无头模式**: 若需在服务器运行，可在初始化时设置 `headless=True`。
- **贡献指南**: 欢迎提交 Pull Request 以更新最新的元素选择器或增加新功能。
- **许可证**: 请参考项目授权说明（默认为 MIT 或同等开源协议）。
