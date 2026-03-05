"""
练习 14.1：多层缓存LLM调用
问题描述：实现一个带多层缓存的LLM调用封装。

学习目标：
- 实现多层缓存
- 提高调用效率
- 减少API调用
"""

from typing import Dict, Any, Optional
import time
import hashlib


# ============================================
# 1. 缓存层定义
# ============================================

class MemoryCache:
    """内存缓存"""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, Any] = {}
        self._max_size = max_size
    
    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any):
        if len(self._cache) >= self._max_size:
            # 简单LRU：删除第一个
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = value
    
    def contains(self, key: str) -> bool:
        return key in self._cache


class RedisCache:
    """Redis缓存（模拟）"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
    
    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        self._cache[key] = value
        # 实际应设置TTL
    
    def contains(self, key: str) -> bool:
        return key in self._cache


# ============================================
# 2. 多层缓存LLM封装
# ============================================

class CachedLLM:
    """带缓存的LLM"""
    
    def __init__(self):
        self.memory_cache = MemoryCache()
        self.redis_cache = RedisCache()
        self.hit_stats = {"memory": 0, "redis": 0, "miss": 0}
    
    def _generate_key(self, prompt: str) -> str:
        """生成缓存键"""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def invoke(self, prompt: str) -> str:
        """调用LLM（带缓存）"""
        key = self._generate_key(prompt)
        
        # 1. 检查内存缓存
        if self.memory_cache.contains(key):
            self.hit_stats["memory"] += 1
            print("  [缓存命中] 内存缓存")
            return self.memory_cache.get(key)
        
        # 2. 检查Redis缓存
        if self.redis_cache.contains(key):
            self.hit_stats["redis"] += 1
            print("  [缓存命中] Redis缓存")
            result = self.redis_cache.get(key)
            # 回填内存缓存
            self.memory_cache.set(key, result)
            return result
        
        # 3. 调用LLM
        self.hit_stats["miss"] += 1
        print("  [缓存未命中] 调用LLM")
        result = self._call_llm(prompt)
        
        # 存入缓存
        self.memory_cache.set(key, result)
        self.redis_cache.set(key, result)
        
        return result
    
    def _call_llm(self, prompt: str) -> str:
        """实际调用LLM（模拟）"""
        time.sleep(0.1)  # 模拟延迟
        return f"Response for: {prompt[:20]}..."
    
    def get_stats(self) -> Dict:
        """获取统计"""
        total = sum(self.hit_stats.values())
        if total == 0:
            return self.hit_stats
        
        return {
            **self.hit_stats,
            "hit_rate": (self.hit_stats["memory"] + self.hit_stats["redis"]) / total
        }


def main():
    print("=" * 60)
    print("练习 14.1：多层缓存LLM调用")
    print("=" * 60)
    
    llm = CachedLLM()
    
    prompts = [
        "什么是Python?",
        "什么是LangGraph?",
        "什么是Python?",  # 重复
        "什么是AI?",
        "什么是Python?",  # 再次重复
    ]
    
    print("\n执行调用：")
    print("-" * 40)
    
    for prompt in prompts:
        print(f"\nPrompt: {prompt}")
        result = llm.invoke(prompt)
        print(f"Result: {result}")
    
    print("\n" + "=" * 60)
    print("缓存统计：")
    print("-" * 40)
    stats = llm.get_stats()
    print(f"  内存命中: {stats['memory']}")
    print(f"  Redis命中: {stats['redis']}")
    print(f"  未命中: {stats['miss']}")
    print(f"  命中率: {stats['hit_rate']:.1%}")
    print("=" * 60)


if __name__ == "__main__":
    main()
