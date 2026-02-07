"""
缓存模块测试
测试 linkedin_cat.cache.ContactCache 的所有功能
"""
import pytest
import time
import json
from pathlib import Path


class TestContactCacheInit:
    """ContactCache 初始化测试"""
    
    def test_init_creates_directory(self, temp_dir):
        """测试初始化时创建目录"""
        from linkedin_cat.cache import ContactCache
        
        cache_dir = Path(temp_dir) / "new_cache"
        cache = ContactCache(str(cache_dir))
        
        assert cache_dir.exists()
        cache.close()
    
    def test_init_with_custom_cooldown(self, temp_cache_dir):
        """测试自定义冷却期"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir, cooldown_days=14)
        
        assert cache.cooldown_seconds == 14 * 24 * 3600
        cache.close()
    
    def test_default_cooldown_is_28_days(self, temp_cache_dir):
        """测试默认冷却期为 28 天"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        
        assert cache.cooldown_seconds == 28 * 24 * 3600
        cache.close()


class TestContactCacheCheck:
    """ContactCache.check() 方法测试"""
    
    def test_check_new_contact(self, temp_cache_dir):
        """测试检查新联系人"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        url = "https://linkedin.com/in/new-user"
        
        result = cache.check(url)
        
        assert result["can_send"] is True
        assert result["status"] == "new"
        assert result["last_sent"] is None
        cache.close()
    
    def test_check_sent_contact_in_cooldown(self, temp_cache_dir):
        """测试处于冷却期的联系人"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir, cooldown_days=1)
        url = "https://linkedin.com/in/cooldown-user"
        
        # 先标记为已发送
        cache.mark_sent(url)
        
        result = cache.check(url)
        
        assert result["can_send"] is False
        assert result["status"] == "cooldown"
        assert result["cooldown_remaining"] > 0
        cache.close()
    
    def test_check_blocked_contact(self, temp_cache_dir):
        """测试被阻止的联系人"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        url = "https://linkedin.com/in/blocked-user"
        
        cache.block(url, reason="User declined")
        
        result = cache.check(url)
        
        assert result["can_send"] is False
        assert result["status"] == "blocked"
        cache.close()
    
    def test_url_normalization_in_check(self, temp_cache_dir):
        """测试 URL 标准化（去除参数和尾部斜杠）"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        url1 = "https://linkedin.com/in/test-user/"
        url2 = "https://linkedin.com/in/test-user?param=1"
        
        cache.mark_sent(url1)
        
        # 不同变体的 URL 应该指向同一条记录
        result1 = cache.check(url1)
        result2 = cache.check(url2)
        
        assert result1["status"] == result2["status"]
        cache.close()


class TestContactCacheMarkSent:
    """ContactCache.mark_sent() 方法测试"""
    
    def test_mark_sent_success(self, temp_cache_dir):
        """测试标记发送成功"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        url = "https://linkedin.com/in/sent-user"
        
        cache.mark_sent(url, success=True)
        
        result = cache.check(url)
        assert result["status"] in ["cooldown", "available"]
        assert result["record"]["success"] is True
        cache.close()
    
    def test_mark_sent_with_metadata(self, temp_cache_dir):
        """测试标记发送并附带元数据"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        url = "https://linkedin.com/in/metadata-user"
        metadata = {"message_template": "intro_v2", "campaign": "Q4_2024"}
        
        cache.mark_sent(url, metadata=metadata)
        
        result = cache.check(url)
        assert result["record"]["metadata"] == metadata
        cache.close()


class TestContactCacheBlockUnblock:
    """阻止和取消阻止测试"""
    
    def test_block_contact(self, temp_cache_dir):
        """测试阻止联系人"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        url = "https://linkedin.com/in/block-test"
        
        cache.block(url, reason="Declined connection")
        
        result = cache.check(url)
        assert result["can_send"] is False
        assert result["status"] == "blocked"
        assert result["record"]["reason"] == "Declined connection"
        cache.close()
    
    def test_unblock_contact(self, temp_cache_dir):
        """测试取消阻止联系人"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        url = "https://linkedin.com/in/unblock-test"
        
        cache.block(url)
        cache.unblock(url)
        
        result = cache.check(url)
        assert result["can_send"] is True
        assert result["status"] == "new"
        cache.close()


class TestContactCacheReset:
    """重置功能测试"""
    
    def test_reset_single_contact(self, temp_cache_dir):
        """测试重置单个联系人"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        url = "https://linkedin.com/in/reset-test"
        
        cache.mark_sent(url)
        cache.reset(url)
        
        result = cache.check(url)
        assert result["status"] == "new"
        cache.close()
    
    def test_reset_all(self, temp_cache_dir):
        """测试重置所有缓存"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        
        for i in range(5):
            cache.mark_sent(f"https://linkedin.com/in/user-{i}")
        
        cache.reset_all()
        
        stats = cache.get_stats()
        assert stats["total_contacts"] == 0
        cache.close()


class TestContactCacheStats:
    """统计功能测试"""
    
    def test_get_stats(self, temp_cache_dir):
        """测试获取统计信息"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir, cooldown_days=1)
        
        # 添加不同状态的联系人
        cache.mark_sent("https://linkedin.com/in/user-1")  # cooldown
        cache.block("https://linkedin.com/in/user-2")      # blocked
        
        stats = cache.get_stats()
        
        assert "total_contacts" in stats
        assert "blocked" in stats
        assert "in_cooldown" in stats
        assert "available" in stats
        assert "cache_size_mb" in stats
        cache.close()


class TestContactCacheExportImport:
    """导出导入功能测试"""
    
    def test_export_history(self, temp_cache_dir, temp_dir):
        """测试导出历史记录"""
        from linkedin_cat.cache import ContactCache
        
        cache = ContactCache(temp_cache_dir)
        
        cache.mark_sent("https://linkedin.com/in/export-1")
        cache.mark_sent("https://linkedin.com/in/export-2")
        
        export_path = Path(temp_dir) / "export.json"
        cache.export_history(str(export_path))
        
        assert export_path.exists()
        
        with open(export_path) as f:
            data = json.load(f)
        
        assert len(data) == 2
        cache.close()
    
    def test_import_history(self, temp_cache_dir, temp_dir):
        """测试导入历史记录"""
        from linkedin_cat.cache import ContactCache
        
        # 创建导入文件
        import_data = [
            {
                "timestamp": time.time() - 1000,
                "success": True,
                "url": "https://linkedin.com/in/import-1"
            },
            {
                "timestamp": time.time() - 2000,
                "success": True,
                "url": "https://linkedin.com/in/import-2"
            }
        ]
        import_path = Path(temp_dir) / "import.json"
        with open(import_path, "w") as f:
            json.dump(import_data, f)
        
        cache = ContactCache(temp_cache_dir)
        cache.import_history(str(import_path))
        
        stats = cache.get_stats()
        assert stats["total_contacts"] == 2
        cache.close()


class TestContactCacheContextManager:
    """上下文管理器测试"""
    
    def test_context_manager(self, temp_cache_dir):
        """测试使用 with 语句"""
        from linkedin_cat.cache import ContactCache
        
        with ContactCache(temp_cache_dir) as cache:
            cache.mark_sent("https://linkedin.com/in/ctx-test")
            result = cache.check("https://linkedin.com/in/ctx-test")
            assert result["status"] == "cooldown"
