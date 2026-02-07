"""
包装器模块测试
测试 linkedin_cat.wrapper 中的 LinkedInClient 和 SearchClient
"""
import pytest
from unittest.mock import MagicMock, patch
import time


class TestSendResult:
    """SendResult 数据类测试"""
    
    def test_success_result(self):
        """测试成功结果创建"""
        from linkedin_cat.wrapper import SendResult
        
        result = SendResult(
            status="success",
            raw_result="ok",
            url="https://linkedin.com/in/test-user",
            timestamp=time.time(),
            attempts=1
        )
        
        assert result.status == "success"
        assert result.attempts == 1
        assert result.error is None
        assert result.screenshot is None
    
    def test_fail_result(self):
        """测试失败结果创建"""
        from linkedin_cat.wrapper import SendResult
        
        result = SendResult(
            status="fail",
            raw_result="error",
            url="https://linkedin.com/in/test-user",
            timestamp=time.time(),
            attempts=3,
            error="Connection timeout"
        )
        
        assert result.status == "fail"
        assert result.attempts == 3
        assert result.error == "Connection timeout"
    
    def test_all_status_types(self):
        """测试所有状态类型"""
        from linkedin_cat.wrapper import SendResult
        
        valid_statuses = ["success", "fail", "blocked", "timeout", "retry_exhausted"]
        
        for status in valid_statuses:
            result = SendResult(
                status=status,
                raw_result="test",
                url="https://linkedin.com/in/test",
                timestamp=time.time()
            )
            assert result.status == status


class TestLinkedInClient:
    """LinkedInClient 包装器测试"""
    
    def test_client_init(self, sample_cookies_file):
        """测试客户端初始化参数"""
        from linkedin_cat.wrapper.client import LinkedInClient
        
        client = LinkedInClient(
            cookies_path=sample_cookies_file,
            headless=True,
            max_retries=3,
            retry_delays=(1, 2, 4),
            timeout=15
        )
        
        assert client.cookies_path == sample_cookies_file
        assert client.headless is True
        assert client.max_retries == 3
        assert client.retry_delays == (1, 2, 4)
        assert client.timeout == 15
    
    def test_client_default_values(self, sample_cookies_file):
        """测试客户端默认值"""
        from linkedin_cat.wrapper.client import LinkedInClient
        
        client = LinkedInClient(cookies_path=sample_cookies_file)
        
        assert client.headless is False
        assert client.max_retries == 2
        assert client.retry_delays == (3, 7, 15)
        assert client.timeout == 30
    
    @patch('linkedin_cat.wrapper.client.LinkedinMessage')
    def test_client_context_manager_enter(self, mock_message, sample_cookies_file):
        """测试上下文管理器 __enter__"""
        from linkedin_cat.wrapper.client import LinkedInClient
        
        mock_instance = MagicMock()
        mock_message.return_value = mock_instance
        
        client = LinkedInClient(cookies_path=sample_cookies_file, headless=True)
        
        with client as c:
            assert c is client
            mock_message.assert_called_once_with(
                linkedin_cookies_json=sample_cookies_file,
                headless=True,
                button_class=None
            )
    
    @patch('linkedin_cat.wrapper.client.LinkedinMessage')
    def test_client_context_manager_exit(self, mock_message, sample_cookies_file):
        """测试上下文管理器 __exit__ 清理资源"""
        from linkedin_cat.wrapper.client import LinkedInClient
        
        mock_instance = MagicMock()
        mock_message.return_value = mock_instance
        
        with LinkedInClient(cookies_path=sample_cookies_file) as client:
            pass
        
        mock_instance.close_driver.assert_called_once()
    
    @patch('linkedin_cat.wrapper.client.LinkedinMessage')
    def test_send_success(self, mock_message, sample_cookies_file):
        """测试发送成功"""
        from linkedin_cat.wrapper.client import LinkedInClient
        
        mock_instance = MagicMock()
        mock_instance.send_single_request.return_value = "success"
        mock_message.return_value = mock_instance
        
        with LinkedInClient(cookies_path=sample_cookies_file) as client:
            result = client.send(
                "https://linkedin.com/in/test-user",
                "Hello!"
            )
            
            assert result.status == "success"
            assert result.attempts == 1
    
    @patch('linkedin_cat.wrapper.client.LinkedinMessage')
    @patch('linkedin_cat.wrapper.client.time')
    def test_send_retry_on_fail(self, mock_time, mock_message, sample_cookies_file):
        """测试失败后重试"""
        from linkedin_cat.wrapper.client import LinkedInClient
        
        mock_instance = MagicMock()
        # 前两次失败，第三次成功
        mock_instance.send_single_request.side_effect = ["fail", "fail", "success"]
        mock_message.return_value = mock_instance
        mock_time.time.return_value = time.time()
        mock_time.sleep.return_value = None
        
        with LinkedInClient(cookies_path=sample_cookies_file, max_retries=3) as client:
            result = client.send(
                "https://linkedin.com/in/test-user",
                "Hello!"
            )
            
            # 由于 max_retries=3, 应该成功
            assert mock_instance.send_single_request.call_count == 3
    
    @patch('linkedin_cat.wrapper.client.LinkedinMessage')
    def test_get_stats(self, mock_message, sample_cookies_file):
        """测试获取统计信息"""
        from linkedin_cat.wrapper.client import LinkedInClient
        
        mock_instance = MagicMock()
        mock_instance.send_single_request.return_value = "success"
        mock_message.return_value = mock_instance
        
        with LinkedInClient(cookies_path=sample_cookies_file) as client:
            client.send("https://linkedin.com/in/user1", "Hello")
            client.send("https://linkedin.com/in/user2", "Hello")
            
            stats = client.get_stats()
            
            assert stats["sent"] == 2
    
    @patch('linkedin_cat.wrapper.client.LinkedinMessage')
    def test_bot_property(self, mock_message, sample_cookies_file):
        """测试 bot 属性访问"""
        from linkedin_cat.wrapper.client import LinkedInClient
        
        mock_instance = MagicMock()
        mock_message.return_value = mock_instance
        
        with LinkedInClient(cookies_path=sample_cookies_file) as client:
            assert client.bot is mock_instance


class TestSearchClient:
    """SearchClient 包装器测试"""
    
    def test_search_client_init(self, sample_cookies_file):
        """测试搜索客户端初始化"""
        from linkedin_cat.wrapper.client import SearchClient
        
        client = SearchClient(
            cookies_path=sample_cookies_file,
            headless=True
        )
        
        assert client.cookies_path == sample_cookies_file
        assert client.headless is True
    
    @patch('linkedin_cat.wrapper.client.LinkedinSearch')
    def test_search_client_context_manager(self, mock_search, sample_cookies_file):
        """测试搜索客户端上下文管理器"""
        from linkedin_cat.wrapper.client import SearchClient
        
        mock_instance = MagicMock()
        mock_search.return_value = mock_instance
        
        with SearchClient(cookies_path=sample_cookies_file) as client:
            assert client.searcher is mock_instance
        
        mock_instance.close_driver.assert_called_once()
    
    @patch('linkedin_cat.wrapper.client.LinkedinSearch')
    def test_search_keywords(self, mock_search, sample_cookies_file):
        """测试关键词搜索"""
        from linkedin_cat.wrapper.client import SearchClient
        
        mock_instance = MagicMock()
        mock_instance.search_keywords.return_value = ["url1", "url2"]
        mock_search.return_value = mock_instance
        
        with SearchClient(cookies_path=sample_cookies_file) as client:
            results = client.search_keywords("software engineer")
            
            mock_instance.search_keywords.assert_called_once_with("software engineer", wait=True)
            assert results == ["url1", "url2"]
    
    @patch('linkedin_cat.wrapper.client.LinkedinSearch')
    def test_search_profile(self, mock_search, sample_cookies_file):
        """测试单个档案抓取"""
        from linkedin_cat.wrapper.client import SearchClient
        
        mock_instance = MagicMock()
        mock_instance.search_linkedin_profile.return_value = {"name": "Test"}
        mock_search.return_value = mock_instance
        
        with SearchClient(cookies_path=sample_cookies_file) as client:
            result = client.search_profile(
                "https://linkedin.com/in/test",
                save_folder="./data"
            )
            
            mock_instance.search_linkedin_profile.assert_called_once()


class TestWrapperExports:
    """包装器模块导出测试"""
    
    def test_wrapper_exports(self):
        """测试 wrapper 模块导出"""
        from linkedin_cat import wrapper
        
        assert hasattr(wrapper, "LinkedInClient")
        assert hasattr(wrapper, "SendResult")
    
    def test_main_package_wrapper_exports(self):
        """测试主包中的 wrapper 导出"""
        import linkedin_cat
        
        assert hasattr(linkedin_cat, "LinkedInClient")
        assert hasattr(linkedin_cat, "SendResult")
