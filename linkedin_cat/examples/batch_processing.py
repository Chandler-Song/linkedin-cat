#!/usr/bin/env python3
"""
批量处理示例
展示如何处理大量 LinkedIn URL，包括错误处理、进度跟踪等
"""

from linkedin_cat import (
    LinkedInClient, 
    ContactCache, 
    LinkedinCatConfig,
    replace_template_variables
)
import time
import random
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_urls_from_file(filepath: str) -> List[str]:
    """
    从文件加载 URL 列表
    支持注释行（以 # 开头）和空行
    """
    urls = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                urls.append(line)
    return urls


def load_message_template(filepath: str) -> str:
    """加载消息模板"""
    with open(filepath, 'r') as f:
        return f.read().strip()


def example_basic_batch():
    """
    示例 1: 基本批量发送
    """
    print("=" * 60)
    print("示例 1: 基本批量发送")
    print("=" * 60)
    
    # 配置
    urls = [
        "https://www.linkedin.com/in/user-1/",
        "https://www.linkedin.com/in/user-2/",
        "https://www.linkedin.com/in/user-3/",
    ]
    message = "Hi! I'd love to connect with you."
    
    results = {"success": 0, "failed": 0, "skipped": 0}
    
    with ContactCache("./cache/contacts") as cache:
        with LinkedInClient(cookies_path="./cookies.json") as client:
            for i, url in enumerate(urls, 1):
                logger.info(f"[{i}/{len(urls)}] 处理: {url}")
                
                # 检查缓存
                status = cache.check(url)
                if not status["can_send"]:
                    logger.info(f"  跳过: {status['status']}")
                    results["skipped"] += 1
                    continue
                
                # 发送
                result = client.send(url, message)
                
                if result.status == "success":
                    cache.mark_sent(url)
                    results["success"] += 1
                    logger.info(f"  ✓ 发送成功")
                else:
                    results["failed"] += 1
                    logger.warning(f"  ✗ 发送失败: {result.error}")
                
                # 随机延迟
                if i < len(urls):
                    delay = random.uniform(3, 8)
                    logger.info(f"  等待 {delay:.1f} 秒...")
                    time.sleep(delay)
    
    # 打印统计
    print(f"\n批量处理完成:")
    print(f"  成功: {results['success']}")
    print(f"  失败: {results['failed']}")
    print(f"  跳过: {results['skipped']}")


def example_with_progress_tracking():
    """
    示例 2: 带进度跟踪和断点续传
    """
    print("\n" + "=" * 60)
    print("示例 2: 带进度跟踪和断点续传")
    print("=" * 60)
    
    progress_file = "./progress.json"
    urls_file = "./urls/targets.txt"
    
    # 加载或初始化进度
    if Path(progress_file).exists():
        with open(progress_file, 'r') as f:
            progress = json.load(f)
        logger.info(f"恢复进度: 已处理 {progress['processed']} 个")
    else:
        progress = {
            "processed": 0,
            "success": [],
            "failed": [],
            "skipped": [],
            "start_time": datetime.now().isoformat()
        }
    
    # 加载 URL
    all_urls = load_urls_from_file(urls_file)
    remaining_urls = all_urls[progress["processed"]:]
    
    logger.info(f"待处理: {len(remaining_urls)}/{len(all_urls)}")
    
    def save_progress():
        with open(progress_file, 'w') as f:
            json.dump(progress, f, indent=2, ensure_ascii=False)
    
    try:
        with ContactCache("./cache/contacts") as cache:
            with LinkedInClient(cookies_path="./cookies.json") as client:
                for url in remaining_urls:
                    # 检查和发送逻辑...
                    status = cache.check(url)
                    
                    if not status["can_send"]:
                        progress["skipped"].append(url)
                    else:
                        result = client.send(url, "Hello!")
                        if result.status == "success":
                            cache.mark_sent(url)
                            progress["success"].append(url)
                        else:
                            progress["failed"].append(url)
                    
                    progress["processed"] += 1
                    
                    # 每处理5个保存一次进度
                    if progress["processed"] % 5 == 0:
                        save_progress()
                        logger.info(f"进度已保存: {progress['processed']}/{len(all_urls)}")
                    
                    time.sleep(random.uniform(3, 8))
                    
    except KeyboardInterrupt:
        logger.info("用户中断，保存进度...")
    finally:
        progress["end_time"] = datetime.now().isoformat()
        save_progress()
        logger.info("进度已保存，下次可继续")


def example_with_config():
    """
    示例 3: 使用配置文件
    """
    print("\n" + "=" * 60)
    print("示例 3: 使用配置文件")
    print("=" * 60)
    
    # 加载配置
    config = LinkedinCatConfig.from_yaml("./config.yaml")
    
    logger.info(f"项目: {config.project_name}")
    logger.info(f"每日限制: {config.safety.max_daily}")
    logger.info(f"冷却期: {config.safety.cooldown_days} 天")
    
    urls = ["https://www.linkedin.com/in/test-user/"]
    message_template = load_message_template("./message/template.txt")
    
    # 替换配置中的模板变量
    message = replace_template_variables(message_template, config.template_variables)
    
    daily_count = 0
    
    with ContactCache(config.cache_dir, cooldown_days=config.safety.cooldown_days) as cache:
        with LinkedInClient(
            cookies_path="./cookies.json",
            headless=config.browser.headless,
            max_retries=config.retry.max_retries,
            retry_delays=tuple(config.retry.delays),
            timeout=config.browser.timeout
        ) as client:
            for url in urls:
                # 检查每日限制
                if config.safety.auto_stop_on_limit and daily_count >= config.safety.max_daily:
                    logger.warning(f"达到每日限制 ({config.safety.max_daily})，停止发送")
                    break
                
                # 发送逻辑...
                result = client.send(url, message)
                if result.status == "success":
                    daily_count += 1
                    cache.mark_sent(url)
                
                # 使用配置的延迟
                delay = random.uniform(config.delay.min_seconds, config.delay.max_seconds)
                time.sleep(delay)
    
    logger.info(f"今日发送: {daily_count}")


def example_error_recovery():
    """
    示例 4: 错误恢复和重试策略
    """
    print("\n" + "=" * 60)
    print("示例 4: 错误恢复和重试策略")
    print("=" * 60)
    
    urls = [
        "https://www.linkedin.com/in/user-1/",
        "https://www.linkedin.com/in/user-2/",
    ]
    
    failed_urls = []
    max_session_errors = 3  # 连续错误超过此数重启会话
    consecutive_errors = 0
    
    def process_batch(client, cache, urls_to_process):
        nonlocal consecutive_errors
        
        for url in urls_to_process:
            try:
                status = cache.check(url)
                if not status["can_send"]:
                    continue
                
                result = client.send(url, "Hello!")
                
                if result.status == "success":
                    cache.mark_sent(url)
                    consecutive_errors = 0  # 重置计数
                else:
                    failed_urls.append(url)
                    consecutive_errors += 1
                    
                    if consecutive_errors >= max_session_errors:
                        logger.warning(f"连续 {consecutive_errors} 次错误，需要重启会话")
                        return False  # 信号重启
                
                time.sleep(random.uniform(3, 8))
                
            except Exception as e:
                logger.error(f"异常: {e}")
                consecutive_errors += 1
                if consecutive_errors >= max_session_errors:
                    return False
        
        return True  # 正常完成
    
    # 首次尝试
    with ContactCache("./cache/contacts") as cache:
        with LinkedInClient(cookies_path="./cookies.json") as client:
            success = process_batch(client, cache, urls)
    
    # 如果有失败的，重试一次
    if failed_urls:
        logger.info(f"重试 {len(failed_urls)} 个失败的 URL...")
        time.sleep(30)  # 等待一段时间后重试
        
        retry_failed = []
        with ContactCache("./cache/contacts") as cache:
            with LinkedInClient(cookies_path="./cookies.json") as client:
                for url in failed_urls:
                    result = client.send(url, "Hello!")
                    if result.status != "success":
                        retry_failed.append(url)
                    time.sleep(random.uniform(5, 10))
        
        if retry_failed:
            logger.warning(f"仍然失败的 URL: {retry_failed}")
            # 可以保存到文件供后续处理


def example_multi_template():
    """
    示例 5: 使用多个消息模板（A/B 测试）
    """
    print("\n" + "=" * 60)
    print("示例 5: 多模板 A/B 测试")
    print("=" * 60)
    
    templates = {
        "A": "Hi {{name|there}}! I noticed your work in {{field|tech}}. Let's connect!",
        "B": "Hello {{name|there}}, I'd love to add you to my professional network.",
        "C": "{{name|Hi there}}! Your profile caught my attention. Would love to connect!"
    }
    
    urls = [
        "https://www.linkedin.com/in/user-1/",
        "https://www.linkedin.com/in/user-2/",
        "https://www.linkedin.com/in/user-3/",
    ]
    
    results_by_template = {k: {"sent": 0, "success": 0} for k in templates}
    
    with ContactCache("./cache/contacts") as cache:
        with LinkedInClient(cookies_path="./cookies.json") as client:
            for i, url in enumerate(urls):
                # 轮询选择模板
                template_key = list(templates.keys())[i % len(templates)]
                template = templates[template_key]
                
                message = replace_template_variables(template, {"name": "there"})
                
                status = cache.check(url)
                if not status["can_send"]:
                    continue
                
                result = client.send(url, message)
                results_by_template[template_key]["sent"] += 1
                
                if result.status == "success":
                    results_by_template[template_key]["success"] += 1
                    cache.mark_sent(url, metadata={"template": template_key})
                
                time.sleep(random.uniform(3, 8))
    
    # 输出统计
    print("\nA/B 测试结果:")
    for key, stats in results_by_template.items():
        rate = (stats["success"] / stats["sent"] * 100) if stats["sent"] > 0 else 0
        print(f"  模板 {key}: {stats['success']}/{stats['sent']} ({rate:.1f}%)")


if __name__ == "__main__":
    print("LinkedIn Cat - 批量处理示例")
    print("注意: 这些示例需要有效的 cookies.json 和配置文件才能运行\n")
    
    # 运行示例（取消注释以运行）
    # example_basic_batch()
    # example_with_progress_tracking()
    # example_with_config()
    # example_error_recovery()
    # example_multi_template()
    
    print("\n提示: 取消注释相应函数调用以运行示例")
