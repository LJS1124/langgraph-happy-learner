"""
练习 9.2：带缓存的搜索工具
问题描述：实现一个带缓存的搜索工具，避免重复搜索相同的关键词。

学习目标：
- 实现工具结果缓存
- 提高工具调用效率
- 减少重复请求
"""

from typing import TypedDict, Annotated, List, Optional
from langchain_core.tools import tool
from functools import lru_cache
import time


# ============================================
# 1. 简单缓存装饰器
# ============================================

class SimpleCache:
    """简单缓存类"""
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl  # 缓存有效期（秒）
    
    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                print(f"  [缓存命中] {key}")
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: str):
        """设置缓存"""
        if len(self.cache) >= self.max_size:
            # 简单的LRU：删除最早的
            oldest = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest]
        
        self.cache[key] = (value, time.time())
        print(f"  [缓存存储] {key}")


# 全局缓存实例
_search_cache = SimpleCache()


# ============================================
# 2. 带缓存的搜索工具
# ============================================

@tool
def cached_search(query: str) -> str:
    """
    带缓存的搜索工具
    
    Args:
        query: 搜索关键词
    
    Returns:
        搜索结果
    """
    # 先查缓存
    cached = _search_cache.get(query)
    if cached:
        return cached
    
    # 模拟搜索（实际应调用搜索API）
    print(f"  [执行搜索] {query}")
    time.sleep(0.5)  # 模拟网络延迟
    
    result = f"搜索'{query}'的结果: 找到10条相关信息"
    
    # 存入缓存
    _search_cache.set(query, result)
    
    return result


# 使用Python内置的lru_cache
@lru_cache(maxsize=100)
@tool
def lru_cached_search(query: str) -> str:
    """
    使用LRU缓存的搜索工具
    
    Args:
        query: 搜索关键词
    
    Returns:
        搜索结果
    """
    print(f"  [执行搜索-lru] {query}")
    time.sleep(0.3)
    return f"搜索'{query}'的结果: 找到相关内容"


# ============================================
# 3. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 9.2：带缓存的搜索工具")
    print("=" * 60)
    
    print("\n测试1：自定义缓存")
    print("-" * 40)
    
    queries = ["Python", "LangGraph", "Python", "AI", "LangGraph"]
    
    for q in queries:
        print(f"\n搜索: {q}")
        result = cached_search.invoke(q)
        print(f"结果: {result[:30]}...")
    
    print("\n" + "=" * 60)
    print("测试2：LRU缓存")
    print("-" * 40)
    
    # 清除之前的缓存效果
    for q in ["Python", "LangGraph", "Python"]:
        print(f"\n搜索: {q}")
        result = lru_cached_search.invoke(q)
        print(f"结果: {result[:30]}...")
    
    print("\n" + "=" * 60)
    print("缓存要点：")
    print("-" * 60)
    print("1. 使用缓存避免重复请求")
    print("2. 设置缓存有效期(TTL)")
    print("3. 限制缓存大小")
    print("4. 可使用lru_cache简化实现")
    print("=" * 60)


if __name__ == "__main__":
    main()
