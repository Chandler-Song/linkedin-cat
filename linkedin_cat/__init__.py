"""
LinkedIn Cat - LinkedIn 自动化工具
====================================

企业级 LinkedIn 自动化解决方案，支持消息发送、搜索、档案抓取等功能。

基础用法::

    from linkedin_cat import LinkedInClient, ContactCache, LinkedinCatConfig
    
    # 使用 wrapper 发送消息
    with LinkedInClient(cookies_path="cookies.json") as client:
        result = client.send("https://linkedin.com/in/someone", "Hello!")
        print(result.status)
    
    # 使用缓存管理联系人状态
    cache = ContactCache("./cache")
    status = cache.check("https://linkedin.com/in/someone")
    if status["can_send"]:
        # 执行发送操作
        pass

CLI 用法::

    # 初始化工作目录
    linkedincat init
    
    # 批量发送消息
    linkedincat send cookies.json message/default.txt urls/demo.txt
    
    # 查看状态
    linkedincat status

模块结构::

    linkedin_cat/
    ├── core/          # 核心 Selenium 引擎
    ├── cli/           # Typer CLI 界面
    ├── wrapper/       # 安全包装器
    ├── cache/         # 缓存管理
    ├── config/        # 配置系统
    └── utils/         # 工具函数

"""

__version__ = "1.0.0"
__author__ = "LinkedIn Cat Team"

# ============================================
# Core Engine - Selenium 自动化
# ============================================
from linkedin_cat.core import (
    LinkedinBase,
    LinkedinMessage,
    LinkedinSearch,
    LinkedIn,
    extract_profile,
    extract_profile_thread_pool,
)

# ============================================
# Wrapper - 安全包装器
# ============================================
from linkedin_cat.wrapper import LinkedInClient, SendResult

# ============================================
# Cache - 状态管理
# ============================================
from linkedin_cat.cache import ContactCache

# ============================================
# Config - 配置系统
# ============================================
from linkedin_cat.config import (
    LinkedinCatConfig,
    RetryConfig,
    DelayConfig,
    SafetyConfig,
    BrowserConfig,
)

# ============================================
# Utils - 工具函数
# ============================================
from linkedin_cat.utils import replace_template_variables, normalize_url

# ============================================
# CLI - 命令行接口
# ============================================
from linkedin_cat.cli import app as cli_app


__all__ = [
    # Version
    "__version__",
    
    # Core
    "LinkedinBase",
    "LinkedinMessage",
    "LinkedinSearch",
    "LinkedIn",
    "extract_profile",
    "extract_profile_thread_pool",
    
    # Wrapper
    "LinkedInClient",
    "SendResult",
    
    # Cache
    "ContactCache",
    
    # Config
    "LinkedinCatConfig",
    "RetryConfig",
    "DelayConfig",
    "SafetyConfig",
    "BrowserConfig",
    
    # Utils
    "replace_template_variables",
    "normalize_url",
    
    # CLI
    "cli_app",
]


def run_cli():
    """运行 CLI 入口"""
    from linkedin_cat.cli.app import run
    run()
