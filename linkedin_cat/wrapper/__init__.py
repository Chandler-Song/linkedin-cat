"""
LinkedIn Cat Wrapper
安全包装器层，提供重试、上下文管理等企业级功能
"""

from .client import LinkedInClient, SendResult

__all__ = ["LinkedInClient", "SendResult"]
