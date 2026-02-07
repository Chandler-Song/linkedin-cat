"""
Pydantic 配置模型
支持 config.yaml + 环境变量 + 命令行覆盖
"""

from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
import yaml
import os


class RetryConfig(BaseModel):
    """重试配置"""
    max_retries: int = 2
    delays: List[int] = [3, 7, 15]  # 指数退避


class DelayConfig(BaseModel):
    """延迟配置"""
    min_seconds: float = 3.0
    max_seconds: float = 8.0
    after_fail: float = 10.0  # 失败后额外等待


class SafetyConfig(BaseModel):
    """安全配置"""
    cooldown_days: int = 28
    max_daily: int = 50
    auto_stop_on_limit: bool = True


class BrowserConfig(BaseModel):
    """浏览器配置"""
    headless: bool = False
    timeout: int = 30
    window_size: Tuple[int, int] = (1920, 1080)


class LinkedinCatConfig(BaseModel):
    """配置根模型"""
    
    project_name: str = "LinkedinCat"
    version: str = "1.0.0"
    
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    delay: DelayConfig = Field(default_factory=DelayConfig)
    browser: BrowserConfig = Field(default_factory=BrowserConfig)
    
    # 路径配置
    cache_dir: str = "./cache"
    log_dir: str = "./logs"
    message_dir: str = "./message"
    urls_dir: str = "./urls"
    
    # 模板变量（可在配置中预设）
    template_variables: Dict[str, str] = Field(default_factory=dict)
    
    @classmethod
    def from_yaml(cls, path: str = "config.yaml") -> "LinkedinCatConfig":
        """从 YAML 加载，不存在则创建默认配置"""
        p = Path(path)
        if not p.exists():
            config = cls()
            config.save(path)
            return config
        
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        # 支持环境变量覆盖
        data = cls._apply_env_overrides(data)
        
        return cls(**data)
    
    @classmethod
    def _apply_env_overrides(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖"""
        env_mappings = {
            "LINKEDINCAT_HEADLESS": ("browser", "headless", lambda x: x.lower() == "true"),
            "LINKEDINCAT_COOLDOWN_DAYS": ("safety", "cooldown_days", int),
            "LINKEDINCAT_MAX_DAILY": ("safety", "max_daily", int),
            "LINKEDINCAT_CACHE_DIR": ("cache_dir", None, str),
            "LINKEDINCAT_LOG_DIR": ("log_dir", None, str),
        }
        
        for env_key, (first_key, second_key, converter) in env_mappings.items():
            env_value = os.environ.get(env_key)
            if env_value is not None:
                try:
                    value = converter(env_value)
                    if second_key:
                        if first_key not in data:
                            data[first_key] = {}
                        data[first_key][second_key] = value
                    else:
                        data[first_key] = value
                except (ValueError, TypeError):
                    pass
        
        return data
    
    def save(self, path: str = "config.yaml"):
        """保存配置到 YAML 文件"""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, allow_unicode=True)
    
    def get_cache_path(self) -> Path:
        """获取缓存目录路径"""
        p = Path(self.cache_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p
    
    def get_log_path(self) -> Path:
        """获取日志目录路径"""
        p = Path(self.log_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p
    
    def get_message_path(self) -> Path:
        """获取消息模板目录路径"""
        p = Path(self.message_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p
    
    def get_urls_path(self) -> Path:
        """获取 URL 列表目录路径"""
        p = Path(self.urls_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p
