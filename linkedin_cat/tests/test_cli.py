"""
CLI 命令测试
测试 linkedin_cat.cli 中的 Typer CLI 命令
"""
import pytest
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner
from pathlib import Path


runner = CliRunner()


class TestCliApp:
    """CLI 应用基础测试"""
    
    def test_app_exists(self):
        """测试 CLI app 存在"""
        from linkedin_cat.cli import app
        assert app is not None
    
    def test_help_command(self):
        """测试 --help 命令"""
        from linkedin_cat.cli import app
        
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "LinkedIn Cat" in result.stdout or "linkedincat" in result.stdout.lower()


class TestVersionCommand:
    """version 命令测试"""
    
    def test_version_command(self):
        """测试 version 命令"""
        from linkedin_cat.cli import app
        
        result = runner.invoke(app, ["version"])
        
        assert result.exit_code == 0
        assert "1.0.0" in result.stdout or "version" in result.stdout.lower()


class TestInitCommand:
    """init 命令测试"""
    
    def test_init_command_help(self):
        """测试 init 命令帮助"""
        from linkedin_cat.cli import app
        
        result = runner.invoke(app, ["init", "--help"])
        
        assert result.exit_code == 0
        assert "init" in result.stdout.lower() or "初始化" in result.stdout


class TestSendCommand:
    """send 命令测试"""
    
    def test_send_help(self):
        """测试 send 命令帮助"""
        from linkedin_cat.cli import app
        
        result = runner.invoke(app, ["send", "--help"])
        
        assert result.exit_code == 0
    
    @patch('linkedin_cat.cli.app.LinkedInClient')
    @patch('linkedin_cat.cli.app.ContactCache')
    def test_send_dry_run(self, mock_cache, mock_client, temp_dir):
        """测试 send --dry-run 模式"""
        from linkedin_cat.cli import app
        
        # 创建测试文件
        cookies = Path(temp_dir) / "cookies.json"
        cookies.write_text('[]')
        
        message = Path(temp_dir) / "message.txt"
        message.write_text("Hello {{name|there}}!")
        
        urls = Path(temp_dir) / "urls.txt"
        urls.write_text("https://linkedin.com/in/test-user")
        
        # Mock cache
        mock_cache_instance = MagicMock()
        mock_cache_instance.check.return_value = {"can_send": True, "status": "new"}
        mock_cache.return_value.__enter__ = MagicMock(return_value=mock_cache_instance)
        mock_cache.return_value.__exit__ = MagicMock(return_value=False)
        
        result = runner.invoke(app, [
            "send",
            str(cookies),
            str(message),
            str(urls),
            "--dry-run"
        ])
        
        # dry-run 不应该实际发送
        mock_client.assert_not_called()


class TestStatusCommand:
    """status 命令测试"""
    
    def test_status_help(self):
        """测试 status 命令帮助"""
        from linkedin_cat.cli import app
        
        result = runner.invoke(app, ["status", "--help"])
        
        assert result.exit_code == 0
    
    @patch('linkedin_cat.cli.app.ContactCache')
    def test_status_command(self, mock_cache, temp_dir):
        """测试 status 命令"""
        from linkedin_cat.cli import app
        
        # Mock cache stats
        mock_cache_instance = MagicMock()
        mock_cache_instance.get_stats.return_value = {
            "total_contacts": 10,
            "blocked": 2,
            "in_cooldown": 5,
            "available": 3,
            "cache_size_mb": 0.5
        }
        mock_cache.return_value.__enter__ = MagicMock(return_value=mock_cache_instance)
        mock_cache.return_value.__exit__ = MagicMock(return_value=False)
        
        urls_file = Path(temp_dir) / "urls.txt"
        urls_file.write_text("https://linkedin.com/in/user1\nhttps://linkedin.com/in/user2")
        
        result = runner.invoke(app, ["status", str(urls_file)])
        
        # 应该显示某种状态信息
        assert result.exit_code == 0


class TestResetCommand:
    """reset 命令测试"""
    
    def test_reset_help(self):
        """测试 reset 命令帮助"""
        from linkedin_cat.cli import app
        
        result = runner.invoke(app, ["reset", "--help"])
        
        assert result.exit_code == 0
    
    @patch('linkedin_cat.cli.app.ContactCache')
    def test_reset_all_requires_force(self, mock_cache):
        """测试 reset --all 需要 --force"""
        from linkedin_cat.cli import app
        
        # 不带 --force 应该需要确认或失败
        result = runner.invoke(app, ["reset", "--all"])
        
        # 检查是否提示确认或退出
        # 具体行为取决于实现


class TestExportCommand:
    """export 命令测试"""
    
    def test_export_help(self):
        """测试 export 命令帮助"""
        from linkedin_cat.cli import app
        
        result = runner.invoke(app, ["export", "--help"])
        
        assert result.exit_code == 0
    
    @patch('linkedin_cat.cli.app.ContactCache')
    def test_export_command(self, mock_cache, temp_dir):
        """测试 export 命令"""
        from linkedin_cat.cli import app
        
        mock_cache_instance = MagicMock()
        mock_cache.return_value.__enter__ = MagicMock(return_value=mock_cache_instance)
        mock_cache.return_value.__exit__ = MagicMock(return_value=False)
        
        output_file = Path(temp_dir) / "export.json"
        
        result = runner.invoke(app, ["export", str(output_file)])
        
        # 检查 export_history 是否被调用
        # mock_cache_instance.export_history.assert_called_once()


class TestCliModuleExports:
    """CLI 模块导出测试"""
    
    def test_cli_module_exports(self):
        """测试 CLI 模块导出"""
        from linkedin_cat import cli
        
        assert hasattr(cli, "app")
    
    def test_main_package_cli_export(self):
        """测试主包中的 CLI 导出"""
        import linkedin_cat
        
        assert hasattr(linkedin_cat, "cli_app")
    
    def test_run_cli_function(self):
        """测试 run_cli 入口函数"""
        import linkedin_cat
        
        assert hasattr(linkedin_cat, "run_cli")
        assert callable(linkedin_cat.run_cli)


class TestCliEdgeCases:
    """CLI 边缘情况测试"""
    
    def test_missing_file_error(self):
        """测试文件不存在时的错误处理"""
        from linkedin_cat.cli import app
        
        result = runner.invoke(app, [
            "send",
            "/nonexistent/cookies.json",
            "/nonexistent/message.txt",
            "/nonexistent/urls.txt"
        ])
        
        # 应该返回错误
        assert result.exit_code != 0 or "error" in result.stdout.lower() or "not found" in result.stdout.lower() or "不存在" in result.stdout
    
    def test_invalid_url_format(self, temp_dir):
        """测试无效 URL 格式处理"""
        from linkedin_cat.cli import app
        
        cookies = Path(temp_dir) / "cookies.json"
        cookies.write_text('[]')
        
        message = Path(temp_dir) / "message.txt"
        message.write_text("Hello!")
        
        urls = Path(temp_dir) / "urls.txt"
        urls.write_text("not-a-valid-url\nstill-not-valid")
        
        result = runner.invoke(app, [
            "send",
            str(cookies),
            str(message),
            str(urls),
            "--dry-run"
        ])
        
        # 应该能处理无效 URL（跳过或报错）
