"""
练习 17.1：Redis检查点存储
问题描述：实现一个自定义的检查点存储后端，使用Redis作为存储。

学习目标：
- 自定义检查点存储
- 使用Redis持久化
- 支持会话恢复
"""

from typing import Dict, Any, Optional
import json


class RedisCheckpointStorage:
    """Redis检查点存储（模拟）"""
    
    def __init__(self):
        # 模拟Redis存储
        self._store: Dict[str, str] = {}
    
    def _get_key(self, thread_id: str, checkpoint_id: str = None) -> str:
        """生成存储键"""
        if checkpoint_id:
            return f"checkpoint:{thread_id}:{checkpoint_id}"
        return f"checkpoint:{thread_id}:latest"
    
    def save(self, thread_id: str, checkpoint: Dict) -> str:
        """保存检查点"""
        import uuid
        checkpoint_id = str(uuid.uuid4())[:8]
        
        checkpoint["id"] = checkpoint_id
        checkpoint["timestamp"] = str(uuid.uuid1().time)
        
        key = self._get_key(thread_id, checkpoint_id)
        latest_key = self._get_key(thread_id)
        
        # 保存检查点
        self._store[key] = json.dumps(checkpoint)
        # 更新最新指针
        self._store[latest_key] = checkpoint_id
        
        print(f"  [保存] 检查点 {checkpoint_id}")
        return checkpoint_id
    
    def load(self, thread_id: str, checkpoint_id: str = None) -> Optional[Dict]:
        """加载检查点"""
        if checkpoint_id is None:
            # 获取最新检查点ID
            latest_key = self._get_key(thread_id)
            checkpoint_id = self._store.get(latest_key)
        
        if not checkpoint_id:
            return None
        
        key = self._get_key(thread_id, checkpoint_id)
        data = self._store.get(key)
        
        if data:
            checkpoint = json.loads(data)
            print(f"  [加载] 检查点 {checkpoint_id}")
            return checkpoint
        
        return None
    
    def list_checkpoints(self, thread_id: str) -> list:
        """列出所有检查点"""
        prefix = f"checkpoint:{thread_id}:"
        checkpoints = []
        
        for key in self._store:
            if key.startswith(prefix) and "latest" not in key:
                checkpoint_id = key.split(":")[-1]
                checkpoints.append(checkpoint_id)
        
        return checkpoints


def main():
    print("=" * 60)
    print("练习 17.1：Redis检查点存储")
    print("=" * 60)
    
    storage = RedisCheckpointStorage()
    
    # 保存检查点
    print("\n保存检查点：")
    print("-" * 40)
    
    cp1 = storage.save("session_001", {"state": {"count": 1}, "step": "A"})
    cp2 = storage.save("session_001", {"state": {"count": 2}, "step": "B"})
    cp3 = storage.save("session_001", {"state": {"count": 3}, "step": "C"})
    
    # 列出检查点
    print(f"\n检查点列表: {storage.list_checkpoints('session_001')}")
    
    # 加载最新
    print("\n加载最新检查点：")
    print("-" * 40)
    latest = storage.load("session_001")
    print(f"  状态: {latest}")
    
    # 加载指定检查点
    print(f"\n加载检查点 {cp1}：")
    print("-" * 40)
    old = storage.load("session_001", cp1)
    print(f"  状态: {old}")
    
    print("\n" + "=" * 60)
    print("检查点存储要点：")
    print("-" * 60)
    print("1. 使用唯一ID标识检查点")
    print("2. 维护最新检查点指针")
    print("3. 支持按ID加载")
    print("4. 生产环境使用真实Redis")
    print("=" * 60)


if __name__ == "__main__":
    main()
