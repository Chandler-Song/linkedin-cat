"""
配置模块测试
测试 linkedin_cat.config 中的 Pydantic 配置系统
"""
import pytest
import os
import yaml
from pathlib import Path


class TestRetryConfig:
    """RetryConfig 测试"""
    
    def test_default_values(self):
        """测试默认值"""
        from linkedin_cat.config import RetryConfig
        
        config = RetryConfig()
        
        assert config.max_retries == 2
        assert config.delays == [3, 7, 15]
    
    def test_custom_values(self):
        """测试自定义值"""
        from linkedin_cat.config import RetryConfig
        
        config = RetryConfig(max_retries=5, delays=[1, 2, 4, 8])
        
        assert config.max_retries == 5
        assert config.delays == [1, 2, 4, 8]


class TestDelayConfig:
    """DelayConfig 测试"""
    
    def test_default_values(self):
        """测试默认值"""
        from linkedin_cat.config import DelayConfig
        
        config = DelayConfig()
        
        assert config.min_seconds == 3.0
        assert config.max_seconds == 8.0
        assert config.after_fail == 10.0
    
    def test_custom_delay(self):
        """测试自定义延迟"""
        from linkedin_cat.config import DelayConfig
        
        config = DelayConfig(min_seconds=1.0, max_seconds=5.0, after_fail=15.0)
        
        assert config.min_seconds == 1.0
        assert config.max_seconds == 5.0
        assert config.after_fail == 15.0


class TestSafetyConfig:
    """SafetyConfig 测试"""
    
    def test_default_values(self):
        """测试默认安全配置"""
        from linkedin_cat.config import SafetyConfig
        
        config = SafetyConfig()
        
        assert config.cooldown_days == 28
        assert config.max_daily == 50
        assert config.auto_stop_on_limit is True
    
    def test_custom_safety(self):
        """测试自定义安全配置"""
        from linkedin_cat.config import SafetyConfig
        
        config = SafetyConfig(cooldown_days=14, max_daily=100)
        
        assert config.cooldown_days == 14
        assert config.max_daily == 100


class TestBrowserConfig:
    """BrowserConfig 测试"""
    
    def test_default_values(self):
        """测试默认浏览器配置"""
        from linkedin_cat.config import BrowserConfig
        
        config = BrowserConfig()
        
        assert config.headless is False
        assert config.timeout == 30
        assert config.window_size == (1920, 1080)
    
    def test_headless_mode(self):
        """测试无头模式配置"""
        from linkedin_cat.config import BrowserConfig
        
        config = BrowserConfig(headless=True)
        
        assert config.headless is True


class TestLinkedinCatConfig:
    """LinkedinCatConfig 主配置测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        from linkedin_cat.config import LinkedinCatConfig
        
        config = LinkedinCatConfig()
        
        assert config.project_name == "LinkedinCat"
        assert config.version == "1.0.0"
        assert config.cache_dir == "./cache"
        assert config.log_dir == "./logs"
    
    def test_nested_configs(self):
        """测试嵌套配置"""
        from linkedin_cat.config import LinkedinCatConfig
        
        config = LinkedinCatConfig()
        
        assert config.safety.cooldown_days == 28
        assert config.retry.max_retries == 2
        assert config.delay.min_seconds == 3.0
        assert config.browser.headless is False
    
    def test_from_dict(self, sample_config_dict):
        """测试从字典创建配置"""
        from linkedin_cat.config import LinkedinCatConfig
        
        config = LinkedinCatConfig(**sample_config_dict)
        
        assert config.project_name == "TestProject"
        assert config.safety.cooldown_days == 14
        assert config.retry.max_retries == 3
    
    def test_save_and_load_yaml(self, temp_dir):
        """测试保存和加载 YAML"""
        from linkedin_cat.config import LinkedinCatConfig
        
        yaml_path = Path(temp_dir) / "config.yaml"
        
        # 创建并保存配置
        config = LinkedinCatConfig(project_name="SaveTest")
        config.save(str(yaml_path))
        
        assert yaml_path.exists()
        
        # 加载配置
        loaded = LinkedinCatConfig.from_yaml(str(yaml_path))
        
        assert loaded.project_name == "SaveTest"
    
    def test_from_yaml_creates_default(self, temp_dir):
        """测试 from_yaml 在文件不存在时创建默认配置"""
        from linkedin_cat.config import LinkedinCatConfig
        
        yaml_path = Path(temp_dir) / "new_config.yaml"
        
        config = LinkedinCatConfig.from_yaml(str(yaml_path))
        
        assert yaml_path.exists()
        assert config.project_name == "LinkedinCat"
    
    def test_template_variables(self):
        """测试模板变量"""
        from linkedin_cat.config import LinkedinCatConfig
        
        config = LinkedinCatConfig(
            template_variables={
                "name": "John",
                "company": "Tech Corp"
            }
        )
        
        assert config.template_variables["name"] == "John"
        assert config.template_variables["company"] == "Tech Corp"


class TestConfigPathHelpers:
    """配置路径辅助方法测试"""
    
    def test_get_cache_path(self, temp_dir):
        """测试获取缓存路径"""
        from linkedin_cat.config import LinkedinCatConfig
        
        cache_dir = str(Path(temp_dir) / "test_cache")
        config = LinkedinCatConfig(cache_dir=cache_dir)
        
        path = config.get_cache_path()
        
        assert path.exists()
        assert str(path) == cache_dir
    
    def test_get_log_path(self, temp_dir):
        """测试获取日志路径"""
        from linkedin_cat.config import LinkedinCatConfig
        
        log_dir = str(Path(temp_dir) / "test_logs")
        config = LinkedinCatConfig(log_dir=log_dir)
        
        path = config.get_log_path()
        
        assert path.exists()
    
    def test_get_message_path(self, temp_dir):
        """测试获取消息模板路径"""
        from linkedin_cat.config import LinkedinCatConfig
        
        msg_dir = str(Path(temp_dir) / "test_messages")
        config = LinkedinCatConfig(message_dir=msg_dir)
        
        path = config.get_message_path()
        
        assert path.exists()


class TestEnvOverrides:
    """环境变量覆盖测试"""
    
    def test_env_headless_override(self, temp_dir, monkeypatch):
        """测试环境变量覆盖 headless"""
        from linkedin_cat.config import LinkedinCatConfig
        
        monkeypatch.setenv("LINKEDINCAT_HEADLESS", "true")
        
        yaml_path = Path(temp_dir) / "env_test.yaml"
        config = LinkedinCatConfig()
        config.save(str(yaml_path))
        
        loaded = LinkedinCatConfig.from_yaml(str(yaml_path))
        
        assert loaded.browser.headless is True
    
    def test_env_max_daily_override(self, temp_dir, monkeypatch):
        """测试环境变量覆盖 max_daily"""
        from linkedin_cat.config import LinkedinCatConfig
        
        monkeypatch.setenv("LINKEDINCAT_MAX_DAILY", "200")
        
        yaml_path = Path(temp_dir) / "env_test2.yaml"
        config = LinkedinCatConfig()
        config.save(str(yaml_path))
        
        loaded = LinkedinCatConfig.from_yaml(str(yaml_path))
        
        assert loaded.safety.max_daily == 200


class TestConfigExports:
    """配置模块导出测试"""
    
    def test_config_module_exports(self):
        """测试 config 模块导出"""
        from linkedin_cat import config
        
        assert hasattr(config, "LinkedinCatConfig")
        assert hasattr(config, "RetryConfig")
        assert hasattr(config, "DelayConfig")
        assert hasattr(config, "SafetyConfig")
        assert hasattr(config, "BrowserConfig")
    
    def test_main_package_config_exports(self):
        """测试主包中的配置导出"""
        import linkedin_cat
        
        assert hasattr(linkedin_cat, "LinkedinCatConfig")
        assert hasattr(linkedin_cat, "RetryConfig")
        assert hasattr(linkedin_cat, "SafetyConfig")
