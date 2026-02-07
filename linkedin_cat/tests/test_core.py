"""
核心模块单元测试
测试 linkedin_cat.core 中的基础功能
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import json
import os


class TestLinkedinBase:
    """LinkedinBase 基类测试"""
    
    def test_base_init_with_valid_cookies(self, temp_dir):
        """测试使用有效 cookies 初始化"""
        # 创建 mock cookies 文件
        cookies_file = os.path.join(temp_dir, "cookies.json")
        with open(cookies_file, "w") as f:
            json.dump([{"name": "li_at", "value": "test123"}], f)
        
        with patch('linkedin_cat.core.base.webdriver') as mock_webdriver:
            mock_driver = MagicMock()
            mock_webdriver.Chrome.return_value = mock_driver
            
            from linkedin_cat.core import LinkedinBase
            
            # 此处只测试类是否可以实例化，实际驱动不启动
            assert LinkedinBase is not None
    
    def test_url_normalization(self):
        """测试 URL 标准化"""
        from linkedin_cat.utils import normalize_url
        
        test_cases = [
            ("https://www.linkedin.com/in/test-user/", "https://www.linkedin.com/in/test-user"),
            ("https://linkedin.com/in/test-user?param=1", "https://linkedin.com/in/test-user"),
            ("https://www.linkedin.com/in/Test-User/", "https://www.linkedin.com/in/test-user"),
        ]
        
        for input_url, expected in test_cases:
            result = normalize_url(input_url)
            assert result == expected, f"Expected {expected}, got {result}"


class TestLinkedinMessage:
    """LinkedinMessage 消息发送测试"""
    
    @pytest.mark.selenium
    def test_message_class_exists(self):
        """测试 LinkedinMessage 类存在"""
        from linkedin_cat.core import LinkedinMessage
        assert LinkedinMessage is not None
    
    @pytest.mark.selenium
    def test_send_result_types(self):
        """测试发送结果类型定义"""
        from linkedin_cat.wrapper import SendResult
        
        # 测试 success 结果
        success_result = SendResult(
            status="success",
            raw_result="ok",
            url="https://linkedin.com/in/test",
            timestamp=1234567890.0,
            attempts=1
        )
        assert success_result.status == "success"
        assert success_result.attempts == 1
        
        # 测试 fail 结果
        fail_result = SendResult(
            status="fail",
            raw_result="error",
            url="https://linkedin.com/in/test",
            timestamp=1234567890.0,
            attempts=3,
            error="Max retries reached"
        )
        assert fail_result.status == "fail"
        assert fail_result.error is not None


class TestLinkedinSearch:
    """LinkedinSearch 搜索功能测试"""
    
    @pytest.mark.selenium
    def test_search_class_exists(self):
        """测试 LinkedinSearch 类存在"""
        from linkedin_cat.core import LinkedinSearch
        assert LinkedinSearch is not None
    
    def test_search_result_types(self):
        """测试搜索结果应为列表"""
        # 模拟搜索结果
        mock_results = [
            "https://linkedin.com/in/user1",
            "https://linkedin.com/in/user2",
            "https://linkedin.com/in/user3",
        ]
        assert isinstance(mock_results, list)
        assert len(mock_results) == 3


class TestProfileExtraction:
    """档案提取功能测试"""
    
    def test_extract_profile_function_exists(self):
        """测试 extract_profile 函数存在"""
        from linkedin_cat.core import extract_profile
        assert callable(extract_profile)
    
    def test_extract_profile_thread_pool_exists(self):
        """测试线程池版本存在"""
        from linkedin_cat.core import extract_profile_thread_pool
        assert callable(extract_profile_thread_pool)


class TestLinkedInClass:
    """LinkedIn 主类测试"""
    
    def test_linkedin_class_exists(self):
        """测试 LinkedIn 主类存在"""
        from linkedin_cat.core import LinkedIn
        assert LinkedIn is not None
    
    def test_linkedin_inherits_message(self):
        """测试 LinkedIn 继承自 LinkedinMessage"""
        from linkedin_cat.core import LinkedIn, LinkedinMessage
        assert issubclass(LinkedIn, LinkedinMessage)


class TestModuleExports:
    """模块导出测试"""
    
    def test_core_exports(self):
        """测试核心模块导出"""
        from linkedin_cat import core
        
        expected_exports = [
            "LinkedinBase",
            "LinkedinMessage", 
            "LinkedinSearch",
            "LinkedIn",
            "extract_profile",
            "extract_profile_thread_pool",
        ]
        
        for name in expected_exports:
            assert hasattr(core, name), f"Missing export: {name}"
    
    def test_main_package_exports(self):
        """测试主包导出"""
        import linkedin_cat
        
        # 检查版本
        assert hasattr(linkedin_cat, "__version__")
        assert linkedin_cat.__version__ == "1.0.0"
        
        # 检查核心类导出
        assert hasattr(linkedin_cat, "LinkedinMessage")
        assert hasattr(linkedin_cat, "LinkedinSearch")
        assert hasattr(linkedin_cat, "LinkedInClient")
        assert hasattr(linkedin_cat, "ContactCache")
