"""
模板变量替换工具
支持 {{var|default}} 语法
"""

import re
from typing import Dict, Any


def replace_template_variables(template: str, variables: Dict[str, Any]) -> str:
    """
    简单的模板变量替换，支持 {{var|default}} 语法
    
    Args:
        template: 模板字符串
        variables: 变量字典
        
    Returns:
        替换后的字符串
        
    Examples:
        >>> replace_template_variables("Hi {{name|there}}", {"name": "John"})
        'Hi John'
        >>> replace_template_variables("Hi {{name|there}}", {})
        'Hi there'
    """
    def replacer(match):
        content = match.group(1).strip()
        if '|' in content:
            var_name, default_val = content.split('|', 1)
            var_name = var_name.strip()
            default_val = default_val.strip()
            return str(variables.get(var_name, default_val))
        else:
            return str(variables.get(content, match.group(0)))

    # 处理 {{var}} 或 {{var|default}}
    pattern = r"\{\{(.*?)\}\}"
    return re.sub(pattern, replacer, template)


def normalize_url(url: str) -> str:
    """
    标准化 LinkedIn URL
    
    Args:
        url: 原始 URL
        
    Returns:
        标准化后的 URL
    """
    return url.split('?')[0].rstrip('/').lower()


def extract_username_from_url(url: str) -> str:
    """
    从 LinkedIn URL 中提取用户名
    
    Args:
        url: LinkedIn 个人主页 URL
        
    Returns:
        用户名
    """
    from urllib.parse import unquote
    url = url.rstrip('/')
    username_encoded = url.split('/')[-1]
    return unquote(username_encoded)


def format_duration(seconds: float) -> str:
    """
    格式化时间长度
    
    Args:
        seconds: 秒数
        
    Returns:
        格式化后的字符串
    """
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分钟"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}小时"
    else:
        days = seconds / 86400
        return f"{days:.1f}天"


def read_url_file(filepath: str) -> list:
    """
    读取 URL 列表文件
    
    Args:
        filepath: 文件路径
        
    Returns:
        URL 列表（过滤空行和注释）
    """
    from pathlib import Path
    p = Path(filepath)
    if not p.exists():
        return []
    
    lines = p.read_text(encoding='utf-8').splitlines()
    return [
        line.strip() for line in lines
        if line.strip() and not line.strip().startswith('#')
    ]


def read_message_template(filepath: str) -> str:
    """
    读取消息模板文件
    
    Args:
        filepath: 文件路径
        
    Returns:
        模板内容
    """
    from pathlib import Path
    return Path(filepath).read_text(encoding='utf-8')
