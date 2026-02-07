#!/usr/bin/env python3
"""
搜索功能使用示例
展示如何使用 SearchClient 进行 LinkedIn 搜索和档案抓取
"""

from linkedin_cat.wrapper.client import SearchClient
from linkedin_cat import ContactCache
import json
import os


def example_keyword_search():
    """
    示例 1: 关键词搜索
    """
    print("=" * 50)
    print("示例 1: 关键词搜索")
    print("=" * 50)
    
    with SearchClient(
        cookies_path="./cookies.json",
        headless=False
    ) as client:
        # 搜索关键词
        results = client.search_keywords("software engineer san francisco")
        
        print(f"找到 {len(results)} 个结果:")
        for i, url in enumerate(results[:10], 1):  # 只显示前10个
            print(f"  {i}. {url}")


def example_profile_scrape():
    """
    示例 2: 抓取单个用户档案
    """
    print("\n" + "=" * 50)
    print("示例 2: 抓取单个用户档案")
    print("=" * 50)
    
    with SearchClient(cookies_path="./cookies.json") as client:
        # 抓取单个档案
        profile_data = client.search_profile(
            url="https://www.linkedin.com/in/example-user/",
            save_folder="./linkedin_data"
        )
        
        if profile_data:
            print("档案数据:")
            print(json.dumps(profile_data, indent=2, ensure_ascii=False))


def example_batch_profile_scrape():
    """
    示例 3: 批量抓取用户档案
    """
    print("\n" + "=" * 50)
    print("示例 3: 批量抓取用户档案")
    print("=" * 50)
    
    urls = [
        "https://www.linkedin.com/in/user-1/",
        "https://www.linkedin.com/in/user-2/",
        "https://www.linkedin.com/in/user-3/",
    ]
    
    with SearchClient(cookies_path="./cookies.json") as client:
        # 批量抓取
        results = client.search_profile_list(
            url_list=urls,
            save_folder="./linkedin_data"
        )
        
        print(f"抓取完成: {len(results)} 个档案")
        for url, data in results.items() if isinstance(results, dict) else []:
            print(f"  - {url}: {'成功' if data else '失败'}")


def example_search_and_save():
    """
    示例 4: 搜索并保存结果到文件
    """
    print("\n" + "=" * 50)
    print("示例 4: 搜索并保存结果")
    print("=" * 50)
    
    search_queries = [
        "machine learning engineer",
        "data scientist startup",
        "product manager tech"
    ]
    
    all_results = []
    
    with SearchClient(cookies_path="./cookies.json") as client:
        for query in search_queries:
            print(f"搜索: {query}")
            results = client.search_keywords(query)
            print(f"  找到 {len(results)} 个结果")
            all_results.extend(results)
    
    # 去重
    unique_results = list(set(all_results))
    print(f"\n总计唯一结果: {len(unique_results)}")
    
    # 保存到文件
    os.makedirs("./urls", exist_ok=True)
    output_file = "./urls/search_results.txt"
    with open(output_file, "w") as f:
        f.write("\n".join(unique_results))
    
    print(f"结果已保存到: {output_file}")


def example_search_with_cache_filter():
    """
    示例 5: 搜索并过滤已联系的用户
    """
    print("\n" + "=" * 50)
    print("示例 5: 搜索并过滤已联系的用户")
    print("=" * 50)
    
    with SearchClient(cookies_path="./cookies.json") as client:
        # 搜索
        all_results = client.search_keywords("python developer")
        print(f"搜索到 {len(all_results)} 个结果")
        
        # 使用缓存过滤
        with ContactCache("./cache/contacts") as cache:
            new_contacts = []
            for url in all_results:
                status = cache.check(url)
                if status["can_send"]:
                    new_contacts.append(url)
            
            print(f"新联系人（未发送过）: {len(new_contacts)}")
            print(f"已联系/冷却中: {len(all_results) - len(new_contacts)}")
            
            # 保存新联系人列表
            if new_contacts:
                with open("./urls/new_contacts.txt", "w") as f:
                    f.write("\n".join(new_contacts))
                print("新联系人已保存到 ./urls/new_contacts.txt")


def example_access_raw_searcher():
    """
    示例 6: 访问底层搜索器（高级用法）
    """
    print("\n" + "=" * 50)
    print("示例 6: 访问底层搜索器")
    print("=" * 50)
    
    with SearchClient(cookies_path="./cookies.json") as client:
        # 获取底层 LinkedinSearch 实例
        searcher = client.searcher
        
        if searcher:
            print(f"底层搜索器类型: {type(searcher).__name__}")
            # 可以直接调用原始方法
            # searcher.search_keywords(...)
            # searcher.driver.get(...)


if __name__ == "__main__":
    print("LinkedIn Cat - 搜索功能示例")
    print("注意: 这些示例需要有效的 cookies.json 文件才能运行\n")
    
    # 运行示例（取消注释以运行）
    # example_keyword_search()
    # example_profile_scrape()
    # example_batch_profile_scrape()
    # example_search_and_save()
    # example_search_with_cache_filter()
    # example_access_raw_searcher()
    
    print("\n提示: 取消注释相应函数调用以运行示例")
