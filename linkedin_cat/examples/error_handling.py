#!/usr/bin/env python3
"""
错误处理示例
展示如何处理各种常见错误和异常情况
"""

from linkedin_cat import (
    LinkedInClient, 
    ContactCache, 
    LinkedinCatConfig,
    SendResult
)
from linkedin_cat.wrapper.client import SearchClient
import logging
import sys
from pathlib import Path
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_file_not_found():
    """
    示例 1: 处理文件不存在错误
    """
    print("=" * 60)
    print("示例 1: 处理文件不存在错误")
    print("=" * 60)
    
    cookies_path = "./nonexistent_cookies.json"
    
    try:
        # 检查文件是否存在
        if not Path(cookies_path).exists():
            raise FileNotFoundError(f"Cookies 文件不存在: {cookies_path}")
        
        with LinkedInClient(cookies_path=cookies_path) as client:
            pass
            
    except FileNotFoundError as e:
        logger.error(f"文件错误: {e}")
        logger.info("请确保 cookies.json 文件存在")
        logger.info("可以通过以下方式获取 cookies:")
        logger.info("  1. 登录 LinkedIn")
        logger.info("  2. 使用浏览器扩展导出 cookies")
        logger.info("  3. 保存为 JSON 格式")


def example_invalid_cookies():
    """
    示例 2: 处理无效 cookies
    """
    print("\n" + "=" * 60)
    print("示例 2: 处理无效 cookies")
    print("=" * 60)
    
    import json
    
    cookies_path = "./test_cookies.json"
    
    # 创建无效的 cookies 文件用于测试
    with open(cookies_path, 'w') as f:
        json.dump([{"name": "invalid", "value": "cookie"}], f)
    
    try:
        with LinkedInClient(cookies_path=cookies_path) as client:
            result = client.send(
                "https://www.linkedin.com/in/test/",
                "Hello!"
            )
            
            # 检查结果
            if result.status == "fail":
                logger.warning("发送失败，可能是 cookies 已过期")
                logger.info("建议重新获取 LinkedIn cookies")
                
    except Exception as e:
        logger.error(f"登录错误: {e}")
        logger.info("请检查 cookies 是否有效")
    finally:
        # 清理测试文件
        Path(cookies_path).unlink(missing_ok=True)


def example_network_timeout():
    """
    示例 3: 处理网络超时
    """
    print("\n" + "=" * 60)
    print("示例 3: 处理网络超时")
    print("=" * 60)
    
    def send_with_timeout_handling(
        client: LinkedInClient, 
        url: str, 
        message: str,
        max_attempts: int = 3
    ) -> Optional[SendResult]:
        """带超时处理的发送函数"""
        
        for attempt in range(1, max_attempts + 1):
            try:
                result = client.send(url, message)
                
                if result.status == "timeout":
                    logger.warning(f"尝试 {attempt}/{max_attempts}: 超时")
                    if attempt < max_attempts:
                        import time
                        wait_time = 30 * attempt  # 递增等待
                        logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        continue
                
                return result
                
            except TimeoutError as e:
                logger.error(f"网络超时: {e}")
                if attempt < max_attempts:
                    import time
                    time.sleep(30)
        
        return None
    
    # 使用示例
    logger.info("此函数展示如何处理超时，需要实际 cookies 运行")


def example_rate_limit():
    """
    示例 4: 处理速率限制
    """
    print("\n" + "=" * 60)
    print("示例 4: 处理速率限制")
    print("=" * 60)
    
    class RateLimitHandler:
        """速率限制处理器"""
        
        def __init__(self, max_per_hour: int = 25, max_per_day: int = 50):
            self.max_per_hour = max_per_hour
            self.max_per_day = max_per_day
            self.hourly_count = 0
            self.daily_count = 0
            self.last_hour_reset = None
            self.last_day_reset = None
        
        def can_send(self) -> bool:
            """检查是否可以发送"""
            from datetime import datetime
            
            now = datetime.now()
            
            # 检查小时重置
            if self.last_hour_reset is None or (now - self.last_hour_reset).seconds >= 3600:
                self.hourly_count = 0
                self.last_hour_reset = now
            
            # 检查天重置
            if self.last_day_reset is None or self.last_day_reset.date() < now.date():
                self.daily_count = 0
                self.last_day_reset = now
            
            return (self.hourly_count < self.max_per_hour and 
                    self.daily_count < self.max_per_day)
        
        def record_send(self):
            """记录一次发送"""
            self.hourly_count += 1
            self.daily_count += 1
        
        def get_wait_time(self) -> int:
            """获取需要等待的时间（秒）"""
            if self.hourly_count >= self.max_per_hour:
                return 3600  # 等待一小时
            if self.daily_count >= self.max_per_day:
                return 86400  # 等待一天
            return 0
    
    # 使用示例
    handler = RateLimitHandler(max_per_hour=25, max_per_day=50)
    
    if handler.can_send():
        logger.info("可以发送")
        handler.record_send()
    else:
        wait_time = handler.get_wait_time()
        logger.warning(f"达到速率限制，需等待 {wait_time // 60} 分钟")


def example_blocked_user():
    """
    示例 5: 处理被阻止的用户
    """
    print("\n" + "=" * 60)
    print("示例 5: 处理被阻止的用户")
    print("=" * 60)
    
    with ContactCache("./cache/contacts") as cache:
        url = "https://www.linkedin.com/in/blocked-user/"
        
        # 检查状态
        status = cache.check(url)
        
        if status["status"] == "blocked":
            logger.info(f"用户已被阻止: {url}")
            logger.info(f"原因: {status['record'].get('reason', '未知')}")
            logger.info("如需取消阻止，使用:")
            logger.info(f"  cache.unblock('{url}')")
        else:
            # 模拟发送失败后的阻止
            logger.info("模拟用户拒绝连接请求...")
            cache.block(url, reason="用户拒绝了连接请求")
            logger.info(f"已阻止: {url}")


def example_selenium_errors():
    """
    示例 6: 处理 Selenium 错误
    """
    print("\n" + "=" * 60)
    print("示例 6: 处理 Selenium 错误")
    print("=" * 60)
    
    common_errors = {
        "WebDriverException": "浏览器驱动问题，请检查 ChromeDriver 版本",
        "NoSuchElementException": "页面元素未找到，可能是 LinkedIn 更新了 UI",
        "TimeoutException": "页面加载超时，检查网络连接",
        "StaleElementReferenceException": "元素已过期，页面可能已刷新",
        "InvalidCookieDomainException": "Cookie 域无效，重新获取 cookies",
    }
    
    print("常见 Selenium 错误及处理方法:")
    for error, solution in common_errors.items():
        print(f"\n  {error}:")
        print(f"    → {solution}")


def example_graceful_shutdown():
    """
    示例 7: 优雅关闭和资源清理
    """
    print("\n" + "=" * 60)
    print("示例 7: 优雅关闭和资源清理")
    print("=" * 60)
    
    import signal
    import time
    
    shutdown_requested = False
    
    def signal_handler(signum, frame):
        nonlocal shutdown_requested
        logger.info("\n收到中断信号，准备优雅退出...")
        shutdown_requested = True
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("运行中... 按 Ctrl+C 测试优雅退出")
    logger.info("(这是一个演示，实际使用时会在批量处理循环中检查 shutdown_requested)")
    
    # 模拟工作循环
    try:
        for i in range(5):
            if shutdown_requested:
                logger.info("检测到关闭请求，保存状态...")
                break
            logger.info(f"处理中... {i+1}/5")
            time.sleep(1)
    finally:
        logger.info("清理完成")


def example_exception_logging():
    """
    示例 8: 完整的异常日志记录
    """
    print("\n" + "=" * 60)
    print("示例 8: 完整的异常日志记录")
    print("=" * 60)
    
    import traceback
    from datetime import datetime
    
    def log_exception(e: Exception, context: dict = None):
        """记录详细的异常信息"""
        error_log = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "traceback": traceback.format_exc(),
            "context": context or {}
        }
        
        # 保存到错误日志文件
        log_path = Path("./logs/errors.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_path, 'a') as f:
            f.write(f"\n{'='*60}\n")
            for key, value in error_log.items():
                f.write(f"{key}: {value}\n")
        
        logger.error(f"异常已记录到 {log_path}")
        return error_log
    
    # 使用示例
    try:
        raise ValueError("这是一个测试异常")
    except Exception as e:
        log_exception(e, context={"url": "https://example.com", "action": "send"})


if __name__ == "__main__":
    print("LinkedIn Cat - 错误处理示例")
    print("展示各种常见错误的处理方法\n")
    
    # 运行示例
    example_file_not_found()
    example_invalid_cookies()
    example_network_timeout()
    example_rate_limit()
    example_blocked_user()
    example_selenium_errors()
    # example_graceful_shutdown()  # 这个会等待用户输入
    example_exception_logging()
    
    print("\n所有错误处理示例完成")
