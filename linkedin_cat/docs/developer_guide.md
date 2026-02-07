# LinkedIn Cat 开发者指南

本指南面向想要扩展或贡献 LinkedIn Cat 项目的开发者。

## 项目架构

```
linkedin_cat/
├── __init__.py          # 主入口，导出公共 API
├── requirements.txt     # 依赖清单
├── core/               # 核心 Selenium 引擎
│   ├── __init__.py
│   ├── base.py         # 基础类，WebDriver 管理
│   ├── message.py      # 消息发送逻辑
│   ├── search.py       # 搜索和抓取逻辑
│   └── profile.py      # 档案提取
├── wrapper/            # 安全包装器
│   ├── __init__.py
│   └── client.py       # LinkedInClient, SearchClient
├── cache/              # 缓存管理
│   ├── __init__.py
│   └── contact_cache.py # 基于 DiskCache 的状态管理
├── config/             # 配置系统
│   ├── __init__.py
│   └── settings.py     # Pydantic 配置模型
├── utils/              # 工具函数
│   ├── __init__.py
│   └── template.py     # 模板替换等
├── cli/                # 命令行界面
│   ├── __init__.py
│   └── app.py          # Typer CLI 应用
├── tests/              # 测试用例
├── examples/           # 示例代码
└── docs/               # 文档
```

---

## 设计原则

### 1. 分层架构

```
┌─────────────────────────────────────┐
│           CLI Layer                 │  ← 用户交互
├─────────────────────────────────────┤
│         Wrapper Layer               │  ← 安全封装、重试、资源管理
├─────────────────────────────────────┤
│          Core Layer                 │  ← Selenium 自动化
└─────────────────────────────────────┘
```

### 2. 依赖注入

```python
# 好的做法
class LinkedInClient:
    def __init__(self, bot_factory=None):
        self.bot_factory = bot_factory or LinkedinMessage

# 不好的做法
class LinkedInClient:
    def __init__(self):
        self.bot = LinkedinMessage()  # 硬编码依赖
```

### 3. 上下文管理

所有资源密集型操作都应支持上下文管理器：

```python
class ResourceClass:
    def __enter__(self):
        self._init_resources()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup_resources()
        return False  # 不吞异常
```

---

## 开发环境设置

### 1. 克隆和安装

```bash
# 克隆项目
git clone https://github.com/your-repo/linkedin_cat.git
cd linkedin_cat

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy
```

### 2. 代码风格

项目使用以下工具保持代码质量：

```bash
# 格式化
black linkedin_cat/

# 检查风格
flake8 linkedin_cat/

# 类型检查
mypy linkedin_cat/
```

### 3. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_cache.py

# 显示覆盖率
pytest --cov=linkedin_cat --cov-report=html

# 跳过需要 Selenium 的测试
pytest -m "not selenium"
```

---

## 扩展指南

### 添加新的核心功能

1. 在 `core/` 目录添加新模块
2. 在 `core/__init__.py` 导出
3. 添加测试用例

示例：添加群组搜索功能

```python
# linkedin_cat/core/groups.py
from linkedin_cat.core.base import LinkedinBase

class LinkedinGroups(LinkedinBase):
    """LinkedIn 群组搜索"""
    
    def search_groups(self, keyword: str) -> list:
        """搜索群组"""
        self.driver.get(f"https://www.linkedin.com/search/results/groups/?keywords={keyword}")
        # 实现搜索逻辑...
        return groups
    
    def join_group(self, group_url: str) -> bool:
        """加入群组"""
        # 实现加入逻辑...
        pass
```

```python
# linkedin_cat/core/__init__.py
from linkedin_cat.core.groups import LinkedinGroups

__all__ = [..., "LinkedinGroups"]
```

### 添加新的包装器

```python
# linkedin_cat/wrapper/groups_client.py
from linkedin_cat.core.groups import LinkedinGroups

class GroupsClient:
    """群组操作的安全包装器"""
    
    def __init__(self, cookies_path: str, **kwargs):
        self.cookies_path = cookies_path
        self.kwargs = kwargs
        self._client = None
    
    def __enter__(self):
        self._client = LinkedinGroups(
            linkedin_cookies_json=self.cookies_path,
            **self.kwargs
        )
        return self
    
    def __exit__(self, *args):
        if self._client:
            self._client.close_driver()
        return False
    
    def search(self, keyword: str) -> list:
        return self._client.search_groups(keyword)
```

### 添加新的 CLI 命令

```python
# linkedin_cat/cli/app.py
@app.command()
def groups(
    cookies: str = typer.Argument(..., help="Cookies 文件路径"),
    keyword: str = typer.Option(..., "--keyword", "-k", help="搜索关键词"),
):
    """搜索 LinkedIn 群组"""
    from linkedin_cat.wrapper.groups_client import GroupsClient
    
    with GroupsClient(cookies) as client:
        results = client.search(keyword)
        for group in results:
            typer.echo(f"- {group}")
```

### 添加新的配置项

```python
# linkedin_cat/config/settings.py
class GroupsConfig(BaseModel):
    """群组配置"""
    max_join_per_day: int = 5
    auto_join: bool = False

class LinkedinCatConfig(BaseModel):
    # ...现有配置...
    groups: GroupsConfig = Field(default_factory=GroupsConfig)
```

---

## 测试指南

### 测试结构

```
tests/
├── conftest.py           # 共享 fixtures
├── test_core.py          # 核心模块测试
├── test_wrapper.py       # 包装器测试
├── test_cache.py         # 缓存测试
├── test_config.py        # 配置测试
├── test_utils.py         # 工具函数测试
└── test_cli.py           # CLI 测试
```

### 编写测试

```python
import pytest
from unittest.mock import MagicMock, patch

class TestMyFeature:
    """我的功能测试"""
    
    def test_basic_case(self):
        """测试基本情况"""
        result = my_function()
        assert result == expected
    
    @pytest.mark.parametrize("input,expected", [
        ("a", "A"),
        ("b", "B"),
    ])
    def test_multiple_cases(self, input, expected):
        """参数化测试"""
        assert transform(input) == expected
    
    @patch('linkedin_cat.core.module.SomeClass')
    def test_with_mock(self, mock_class):
        """使用 Mock 的测试"""
        mock_instance = MagicMock()
        mock_class.return_value = mock_instance
        
        result = function_using_class()
        
        mock_class.assert_called_once()
```

### 标记测试

```python
@pytest.mark.selenium
def test_requires_selenium():
    """需要 Selenium 的测试"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """运行较慢的测试"""
    pass

@pytest.mark.integration
def test_full_flow():
    """集成测试"""
    pass
```

---

## API 设计指南

### 函数签名

```python
# 好的设计
def send_message(
    url: str,
    message: str,
    *,
    wait: bool = True,
    timeout: int = 30,
) -> SendResult:
    """发送消息"""
    pass

# 不好的设计
def send_message(url, msg, w=True, t=30):
    pass
```

### 返回值

```python
# 使用数据类表示复杂返回值
@dataclass
class SendResult:
    status: str
    error: Optional[str] = None

# 避免返回裸字典
def send() -> dict:  # 不好
    return {"status": "ok"}
```

### 异常处理

```python
# 定义特定异常
class LinkedInCatError(Exception):
    """基础异常"""
    pass

class CookiesExpiredError(LinkedInCatError):
    """Cookies 过期"""
    pass

class RateLimitError(LinkedInCatError):
    """速率限制"""
    pass

# 使用
def send_message():
    if not valid_cookies:
        raise CookiesExpiredError("请更新 cookies")
```

---

## 提交贡献

### Git 工作流

```bash
# 1. Fork 项目
# 2. 创建功能分支
git checkout -b feature/my-new-feature

# 3. 开发和测试
# 4. 提交更改
git add .
git commit -m "feat: add group search feature"

# 5. 推送到 Fork
git push origin feature/my-new-feature

# 6. 创建 Pull Request
```

### 提交消息格式

```
<type>: <description>

[optional body]

[optional footer]
```

类型：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `test`: 测试相关
- `refactor`: 重构
- `chore`: 构建/工具变更

### Pull Request 检查清单

- [ ] 代码通过所有测试
- [ ] 添加了新功能的测试
- [ ] 更新了相关文档
- [ ] 代码符合项目风格
- [ ] 提交消息清晰
