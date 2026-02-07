"""
工具函数测试
测试 linkedin_cat.utils 中的模板替换和其他工具函数
"""
import pytest


class TestReplaceTemplateVariables:
    """模板变量替换测试"""
    
    def test_simple_replacement(self):
        """测试简单变量替换"""
        from linkedin_cat.utils import replace_template_variables
        
        template = "Hello {{name}}!"
        variables = {"name": "John"}
        
        result = replace_template_variables(template, variables)
        
        assert result == "Hello John!"
    
    def test_multiple_replacements(self):
        """测试多个变量替换"""
        from linkedin_cat.utils import replace_template_variables
        
        template = "Hi {{name}}, I work at {{company}} as a {{role}}."
        variables = {
            "name": "Alice",
            "company": "Tech Corp",
            "role": "Engineer"
        }
        
        result = replace_template_variables(template, variables)
        
        assert result == "Hi Alice, I work at Tech Corp as a Engineer."
    
    def test_default_value(self):
        """测试使用默认值"""
        from linkedin_cat.utils import replace_template_variables
        
        template = "Hello {{name|there}}!"
        variables = {}  # name 未提供
        
        result = replace_template_variables(template, variables)
        
        assert result == "Hello there!"
    
    def test_default_value_not_used_when_provided(self):
        """测试提供值时不使用默认值"""
        from linkedin_cat.utils import replace_template_variables
        
        template = "Hello {{name|there}}!"
        variables = {"name": "John"}
        
        result = replace_template_variables(template, variables)
        
        assert result == "Hello John!"
    
    def test_missing_variable_without_default(self):
        """测试缺少变量且无默认值时保持原样"""
        from linkedin_cat.utils import replace_template_variables
        
        template = "Hello {{unknown}}!"
        variables = {}
        
        result = replace_template_variables(template, variables)
        
        # 保持原样或使用空字符串（取决于实现）
        assert "{{unknown}}" in result or result == "Hello !"
    
    def test_complex_template(self):
        """测试复杂模板"""
        from linkedin_cat.utils import replace_template_variables
        
        template = """
Hi {{name|Friend}},

I noticed you work at {{company|your company}} as a {{role|professional}}.
I'd love to connect!

Best,
{{sender|LinkedIn Cat}}
        """.strip()
        
        variables = {
            "name": "Alice",
            "company": "Google",
            "sender": "Bob"
        }
        
        result = replace_template_variables(template, variables)
        
        assert "Alice" in result
        assert "Google" in result
        assert "professional" in result  # role 使用默认值
        assert "Bob" in result
    
    def test_empty_template(self):
        """测试空模板"""
        from linkedin_cat.utils import replace_template_variables
        
        result = replace_template_variables("", {"name": "John"})
        
        assert result == ""
    
    def test_no_variables_in_template(self):
        """测试模板中没有变量"""
        from linkedin_cat.utils import replace_template_variables
        
        template = "Hello World!"
        
        result = replace_template_variables(template, {"name": "John"})
        
        assert result == "Hello World!"


class TestNormalizeUrl:
    """URL 标准化测试"""
    
    def test_remove_trailing_slash(self):
        """测试移除尾部斜杠"""
        from linkedin_cat.utils import normalize_url
        
        url = "https://www.linkedin.com/in/test-user/"
        
        result = normalize_url(url)
        
        assert not result.endswith("/")
    
    def test_remove_query_params(self):
        """测试移除查询参数"""
        from linkedin_cat.utils import normalize_url
        
        url = "https://www.linkedin.com/in/test-user?source=email&ref=123"
        
        result = normalize_url(url)
        
        assert "?" not in result
        assert "source" not in result
    
    def test_lowercase(self):
        """测试转换为小写"""
        from linkedin_cat.utils import normalize_url
        
        url = "https://www.LinkedIn.com/in/Test-User/"
        
        result = normalize_url(url)
        
        assert result == result.lower()
    
    def test_preserve_username(self):
        """测试保留用户名部分"""
        from linkedin_cat.utils import normalize_url
        
        url = "https://www.linkedin.com/in/john-doe-123456/"
        
        result = normalize_url(url)
        
        assert "john-doe-123456" in result
    
    def test_normalize_multiple_urls(self):
        """测试标准化多个不同形式的 URL 到相同结果"""
        from linkedin_cat.utils import normalize_url
        
        urls = [
            "https://www.linkedin.com/in/test-user/",
            "https://linkedin.com/in/test-user?ref=123",
            "https://www.linkedin.com/in/Test-User",
            "HTTPS://WWW.LINKEDIN.COM/IN/TEST-USER/",
        ]
        
        normalized = [normalize_url(u) for u in urls]
        
        # 所有变体应该标准化到相同的值
        assert len(set(normalized)) == 1


class TestUtilsExports:
    """工具模块导出测试"""
    
    def test_utils_module_exports(self):
        """测试 utils 模块导出"""
        from linkedin_cat import utils
        
        assert hasattr(utils, "replace_template_variables")
        assert hasattr(utils, "normalize_url")
    
    def test_main_package_utils_exports(self):
        """测试主包中的工具导出"""
        import linkedin_cat
        
        assert hasattr(linkedin_cat, "replace_template_variables")
        assert hasattr(linkedin_cat, "normalize_url")
    
    def test_functions_are_callable(self):
        """测试函数可调用"""
        from linkedin_cat.utils import replace_template_variables, normalize_url
        
        assert callable(replace_template_variables)
        assert callable(normalize_url)
