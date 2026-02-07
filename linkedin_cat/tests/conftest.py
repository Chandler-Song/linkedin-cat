"""
pytest 配置和共享 fixtures
"""
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch


# ============================================
# 测试路径 fixtures
# ============================================

@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    tmpdir = tempfile.mkdtemp(prefix="linkedin_cat_test_")
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture
def temp_cache_dir(temp_dir):
    """创建临时缓存目录"""
    cache_dir = Path(temp_dir) / "cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return str(cache_dir)


@pytest.fixture
def sample_cookies_file(temp_dir):
    """创建示例 cookies 文件"""
    cookies_path = Path(temp_dir) / "cookies.json"
    cookies_path.write_text('[{"name": "li_at", "value": "test_value"}]')
    return str(cookies_path)


@pytest.fixture
def sample_message_file(temp_dir):
    """创建示例消息模板文件"""
    msg_path = Path(temp_dir) / "message.txt"
    msg_path.write_text("Hello {{name|there}}! I saw your profile and wanted to connect.")
    return str(msg_path)


@pytest.fixture
def sample_urls_file(temp_dir):
    """创建示例 URL 文件"""
    urls_path = Path(temp_dir) / "urls.txt"
    urls_path.write_text("""
# 测试 URL 列表
https://www.linkedin.com/in/test-user-1/
https://www.linkedin.com/in/test-user-2/
https://www.linkedin.com/in/test-user-3/
""".strip())
    return str(urls_path)


# ============================================
# Mock fixtures
# ============================================

@pytest.fixture
def mock_selenium_driver():
    """模拟 Selenium WebDriver"""
    driver = MagicMock()
    driver.get.return_value = None
    driver.find_element.return_value = MagicMock()
    driver.quit.return_value = None
    return driver


@pytest.fixture
def mock_linkedin_message():
    """模拟 LinkedinMessage 类"""
    with patch('linkedin_cat.core.message.LinkedinMessage') as mock:
        instance = MagicMock()
        instance.send_single_request.return_value = "success"
        instance.close_driver.return_value = None
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_linkedin_search():
    """模拟 LinkedinSearch 类"""
    with patch('linkedin_cat.core.search.LinkedinSearch') as mock:
        instance = MagicMock()
        instance.search_keywords.return_value = ["https://linkedin.com/in/user1"]
        instance.close_driver.return_value = None
        mock.return_value = instance
        yield mock


# ============================================
# 测试数据 fixtures
# ============================================

@pytest.fixture
def sample_linkedin_urls():
    """示例 LinkedIn URL 列表"""
    return [
        "https://www.linkedin.com/in/john-doe-123456/",
        "https://www.linkedin.com/in/jane-smith-789012/",
        "https://www.linkedin.com/in/bob-wilson-345678/",
    ]


@pytest.fixture
def sample_config_dict():
    """示例配置字典"""
    return {
        "project_name": "TestProject",
        "version": "1.0.0",
        "safety": {
            "cooldown_days": 14,
            "max_daily": 100,
            "auto_stop_on_limit": True
        },
        "retry": {
            "max_retries": 3,
            "delays": [1, 2, 4]
        },
        "delay": {
            "min_seconds": 1.0,
            "max_seconds": 3.0,
            "after_fail": 5.0
        },
        "browser": {
            "headless": True,
            "timeout": 15,
            "window_size": [1920, 1080]
        },
        "cache_dir": "./test_cache",
        "log_dir": "./test_logs"
    }


@pytest.fixture
def sample_template_variables():
    """示例模板变量"""
    return {
        "name": "Test User",
        "company": "Test Company",
        "role": "Software Engineer"
    }


# ============================================
# 集成测试标记
# ============================================

def pytest_configure(config):
    """注册自定义标记"""
    config.addinivalue_line(
        "markers", "integration: 集成测试，需要真实环境"
    )
    config.addinivalue_line(
        "markers", "slow: 运行较慢的测试"
    )
    config.addinivalue_line(
        "markers", "selenium: 需要 Selenium 的测试"
    )
