#!/usr/bin/env python3
"""
基本消息发送示例
展示如何使用 LinkedInClient 发送消息或连接请求
"""

from linkedin_cat import LinkedInClient, ContactCache, replace_template_variables
import time
import random


def example_single_send():
    """
    示例 1: 发送单条消息
    """
    print("=" * 50)
    print("示例 1: 发送单条消息")
    print("=" * 50)
    
    # 准备消息模板
    message_template = """
Hi {{name|there}},

I came across your profile and was impressed by your work at {{company|your company}}.
I'd love to connect and exchange ideas about {{topic|the industry}}.

Best regards!
    """.strip()
    
    # 替换变量
    variables = {
        "name": "John",
        "company": "Google",
        "topic": "AI/ML trends"
    }
    message = replace_template_variables(message_template, variables)
    
    print(f"消息内容:\n{message}\n")
    
    # 使用上下文管理器发送（安全资源管理）
    with LinkedInClient(
        cookies_path="./cookies.json",
        headless=False,  # 设置为 True 可无头运行
        max_retries=2
    ) as client:
        result = client.send(
            url="https://www.linkedin.com/in/example-user/",
            message=message
        )
        
        print(f"发送结果: {result.status}")
        print(f"尝试次数: {result.attempts}")
        if result.error:
            print(f"错误信息: {result.error}")


def example_with_cache():
    """
    示例 2: 使用缓存避免重复发送
    """
    print("\n" + "=" * 50)
    print("示例 2: 使用缓存避免重复发送")
    print("=" * 50)
    
    urls = [
        "https://www.linkedin.com/in/user-1/",
        "https://www.linkedin.com/in/user-2/",
        "https://www.linkedin.com/in/user-3/",
    ]
    
    message = "Hi! I'd love to connect with you."
    
    # 使用缓存管理联系人状态
    with ContactCache("./cache/contacts", cooldown_days=28) as cache:
        with LinkedInClient(cookies_path="./cookies.json") as client:
            for url in urls:
                # 检查是否可以发送
                status = cache.check(url)
                
                if not status["can_send"]:
                    print(f"跳过 {url}: {status['status']}")
                    if status["status"] == "cooldown":
                        remaining_days = status["cooldown_remaining"] / 86400
                        print(f"  冷却期剩余: {remaining_days:.1f} 天")
                    continue
                
                # 发送消息
                result = client.send(url, message)
                
                # 记录发送状态
                if result.status == "success":
                    cache.mark_sent(url, success=True)
                    print(f"✓ 发送成功: {url}")
                else:
                    print(f"✗ 发送失败: {url} - {result.error}")
                
                # 随机延迟，避免被检测
                delay = random.uniform(3, 8)
                print(f"  等待 {delay:.1f} 秒...")
                time.sleep(delay)


def example_retry_callback():
    """
    示例 3: 使用重试回调监控发送状态
    """
    print("\n" + "=" * 50)
    print("示例 3: 使用重试回调")
    print("=" * 50)
    
    def on_retry(attempt: int):
        """重试回调函数"""
        print(f"  [重试] 第 {attempt} 次尝试失败，正在重试...")
    
    with LinkedInClient(
        cookies_path="./cookies.json",
        max_retries=3,
        retry_delays=(2, 5, 10)  # 自定义重试延迟
    ) as client:
        result = client.send(
            url="https://www.linkedin.com/in/example-user/",
            message="Hello!",
            on_retry=on_retry  # 传入回调函数
        )
        
        print(f"最终结果: {result.status}")
        print(f"总尝试次数: {result.attempts}")


def example_session_stats():
    """
    示例 4: 获取会话统计信息
    """
    print("\n" + "=" * 50)
    print("示例 4: 获取会话统计")
    print("=" * 50)
    
    urls = [
        "https://www.linkedin.com/in/user-a/",
        "https://www.linkedin.com/in/user-b/",
        "https://www.linkedin.com/in/user-c/",
    ]
    
    with LinkedInClient(cookies_path="./cookies.json") as client:
        for url in urls:
            result = client.send(url, "Hi! Let's connect.")
            print(f"{url}: {result.status}")
            time.sleep(2)
        
        # 获取本次会话统计
        stats = client.get_stats()
        print(f"\n会话统计:")
        print(f"  发送成功: {stats['sent']}")
        print(f"  发送失败: {stats['failed']}")
        print(f"  重试次数: {stats['retried']}")


def example_access_raw_bot():
    """
    示例 5: 访问底层 bot 实例（高级用法）
    """
    print("\n" + "=" * 50)
    print("示例 5: 访问底层 bot 实例")
    print("=" * 50)
    
    with LinkedInClient(cookies_path="./cookies.json") as client:
        # 获取底层 LinkedinMessage 实例
        bot = client.bot
        
        if bot:
            print(f"底层 bot 类型: {type(bot).__name__}")
            # 可以直接调用 linkedin_cat 的原始方法
            # bot.send_single_request(...)
            # bot.driver.get(...)


if __name__ == "__main__":
    print("LinkedIn Cat - 基本消息发送示例")
    print("注意: 这些示例需要有效的 cookies.json 文件才能运行\n")
    
    # 运行示例（取消注释以运行）
    # example_single_send()
    # example_with_cache()
    # example_retry_callback()
    # example_session_stats()
    # example_access_raw_bot()
    
    print("\n提示: 取消注释相应函数调用以运行示例")
