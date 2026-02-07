"""
linkedin_cat.core.LinkedinMessage 的安全包装器
添加上下文管理、自动重试、结果标准化
"""

import time
import random
import logging
from dataclasses import dataclass
from typing import Optional, Literal, Callable, Dict, Any
from pathlib import Path

from linkedin_cat.core.message import LinkedinMessage
from linkedin_cat.core.search import LinkedinSearch

logger = logging.getLogger(__name__)


@dataclass
class SendResult:
    """标准化的发送结果"""
    status: Literal["success", "fail", "blocked", "timeout", "retry_exhausted", "pending", "already_friend"]
    raw_result: str  # linkedin_cat 返回的原始结果
    url: str
    timestamp: float
    attempts: int = 1
    screenshot: Optional[Path] = None
    error: Optional[str] = None
    detail_status: Optional[str] = None  # 详细状态: sent/pending/already_friend/failed/error


class LinkedInClient:
    """
    linkedin_cat.LinkedInMessage 的企业级包装器
    
    增强功能:
    - 上下文管理器 (with 语句)
    - 指数退避重试
    - 自动截图
    - 结果标准化
    
    Usage:
        with LinkedInClient(cookies_path="cookies.json") as client:
            result = client.send("https://www.linkedin.com/in/someone/", "Hello!")
            print(f"Status: {result.status}")
    """
    
    def __init__(
        self,
        cookies_path: str,
        headless: bool = False,
        button_class: Optional[str] = None,
        max_retries: int = 2,
        retry_delays: tuple = (3, 7, 15),
        timeout: int = 30
    ):
        """
        初始化 LinkedIn 客户端
        
        Args:
            cookies_path: LinkedIn cookies JSON 文件路径
            headless: 是否使用无头模式
            button_class: Connect 按钮的 CSS class
            max_retries: 最大重试次数
            retry_delays: 重试延迟时间（秒）
            timeout: 操作超时时间
        """
        self.cookies_path = cookies_path
        self.headless = headless
        self.button_class = button_class
        self.max_retries = max_retries
        self.retry_delays = retry_delays
        self.timeout = timeout
        
        self._bot: Optional[LinkedinMessage] = None
        self._stats = {"sent": 0, "failed": 0, "retried": 0}
    
    def __enter__(self) -> "LinkedInClient":
        """初始化 linkedin_cat 实例"""
        logger.info(f"Initializing LinkedIn client (headless={self.headless})")
        self._bot = LinkedinMessage(
            linkedin_cookies_json=self.cookies_path,
            headless=self.headless,
            button_class=self.button_class
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        if self._bot:
            try:
                self._bot.close_driver()
            except Exception:
                pass
            logger.info(f"Session closed. Stats: {self._stats}")
        return False
    
    def send(
        self, 
        url: str, 
        message: str,
        on_retry: Optional[Callable[[int], None]] = None,
        wait: bool = True
    ) -> SendResult:
        """
        发送消息/好友申请，带重试机制
        
        Args:
            url: LinkedIn 个人主页 URL
            message: 消息内容
            on_retry: 重试回调函数 (attempt_number) -> None
            wait: 是否等待页面加载
            
        Returns:
            SendResult 标准化结果
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # linkedin_cat 的核心调用 - 现在返回 dict
                raw_result = self._bot.send_single_request(url, message, wait=wait)
                
                # 解析新的结构化返回结果
                if isinstance(raw_result, dict):
                    success = raw_result.get("success", False)
                    detail_status = raw_result.get("status", "unknown")
                    result_message = raw_result.get("message", "")
                    
                    if success:
                        # 成功状态
                        self._stats["sent"] += 1
                        
                        # 根据详细状态设置主状态
                        if detail_status == "pending":
                            main_status = "pending"
                        elif detail_status == "already_friend":
                            main_status = "already_friend"
                        else:
                            main_status = "success"
                        
                        return SendResult(
                            status=main_status,
                            raw_result=result_message,
                            url=url,
                            timestamp=time.time(),
                            attempts=attempt,
                            detail_status=detail_status
                        )
                    else:
                        # 失败，检查是否需要重试
                        if attempt < self.max_retries:
                            delay = self.retry_delays[min(attempt-1, len(self.retry_delays)-1)]
                            logger.warning(f"Attempt {attempt} failed for {url}: {result_message}, retrying in {delay}s...")
                            
                            if on_retry:
                                on_retry(attempt)
                            
                            time.sleep(delay + random.uniform(0, 2))
                            self._stats["retried"] += 1
                            continue
                        else:
                            self._stats["failed"] += 1
                            return SendResult(
                                status="fail",
                                raw_result=result_message,
                                url=url,
                                timestamp=time.time(),
                                attempts=attempt,
                                error=result_message,
                                detail_status=detail_status
                            )
                else:
                    # 兼容旧版返回值
                    if raw_result == 'fail' or raw_result is False:
                        if attempt < self.max_retries:
                            delay = self.retry_delays[min(attempt-1, len(self.retry_delays)-1)]
                            logger.warning(f"Attempt {attempt} failed for {url}, retrying in {delay}s...")
                            
                            if on_retry:
                                on_retry(attempt)
                            
                            time.sleep(delay + random.uniform(0, 2))
                            self._stats["retried"] += 1
                            continue
                        else:
                            self._stats["failed"] += 1
                            return SendResult(
                                status="fail",
                                raw_result=str(raw_result),
                                url=url,
                                timestamp=time.time(),
                                attempts=attempt,
                                error="Max retries reached, operation failed"
                            )
                    else:
                        # 成功
                        self._stats["sent"] += 1
                        return SendResult(
                            status="success",
                            raw_result=str(raw_result) if raw_result else "ok",
                            url=url,
                            timestamp=time.time(),
                            attempts=attempt
                        )
                    
            except Exception as e:
                last_error = str(e)
                logger.exception(f"Exception on attempt {attempt} for {url}")
                
                if attempt < self.max_retries:
                    delay = self.retry_delays[min(attempt-1, len(self.retry_delays)-1)]
                    if on_retry:
                        on_retry(attempt)
                    time.sleep(delay)
                else:
                    break
        
        # 所有重试耗尽
        self._stats["failed"] += 1
        return SendResult(
            status="retry_exhausted",
            raw_result="",
            url=url,
            timestamp=time.time(),
            attempts=self.max_retries,
            error=f"All retries failed. Last error: {last_error}"
        )
    
    def get_stats(self) -> Dict[str, int]:
        """获取会话统计"""
        return self._stats.copy()
    
    @property
    def bot(self) -> Optional[LinkedinMessage]:
        """获取底层 LinkedinMessage 实例，供高级用法"""
        return self._bot


class SearchClient:
    """
    linkedin_cat.LinkedinSearch 的包装器
    """
    
    def __init__(
        self,
        cookies_path: str,
        headless: bool = False,
        **kwargs
    ):
        self.cookies_path = cookies_path
        self.headless = headless
        self.kwargs = kwargs
        self._searcher: Optional[LinkedinSearch] = None
    
    def __enter__(self) -> "SearchClient":
        """初始化搜索客户端"""
        logger.info(f"Initializing LinkedIn search client")
        self._searcher = LinkedinSearch(
            linkedin_cookies_json=self.cookies_path,
            headless=self.headless,
            **self.kwargs
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """清理资源"""
        if self._searcher:
            try:
                self._searcher.close_driver()
            except Exception:
                pass
        return False
    
    def search_keywords(self, keywords: str, wait: bool = True):
        """搜索关键词"""
        return self._searcher.search_keywords(keywords, wait=wait)
    
    def search_profile(self, url: str, save_folder: str = "./linkedin"):
        """抓取用户档案"""
        return self._searcher.search_linkedin_profile(url, save_folder=save_folder)
    
    def search_profile_list(self, url_list: list, save_folder: str = "./linkedin"):
        """批量抓取用户档案"""
        return self._searcher.search_linkedin_profile_list(url_list, save_folder=save_folder)
    
    @property
    def searcher(self) -> Optional[LinkedinSearch]:
        """获取底层 LinkedinSearch 实例"""
        return self._searcher
