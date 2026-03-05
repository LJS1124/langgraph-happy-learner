"""
练习 12.2：黑板系统
问题描述：设计一个黑板系统，支持订阅机制。

学习目标：
- 实现黑板模式
- 支持订阅/通知
- 解耦智能体通信
"""

from typing import Dict, Any, List, Callable, Set
from dataclasses import dataclass


# ============================================
# 1. 订阅者定义
# ============================================

@dataclass
class Subscriber:
    """订阅者"""
    name: str
    callback: Callable[[str, Any], None]
    subscribed_keys: Set[str]


# ============================================
# 2. 黑板系统
# ============================================

class Blackboard:
    """黑板系统"""
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._subscribers: Dict[str, List[Subscriber]] = {}
        self._history: List[Dict] = []
    
    def subscribe(self, key: str, subscriber_name: str, callback: Callable):
        """订阅数据变更"""
        if key not in self._subscribers:
            self._subscribers[key] = []
        
        subscriber = Subscriber(
            name=subscriber_name,
            callback=callback,
            subscribed_keys={key}
        )
        
        self._subscribers[key].append(subscriber)
        print(f"  [订阅] {subscriber_name} 订阅了 {key}")
    
    def unsubscribe(self, key: str, subscriber_name: str):
        """取消订阅"""
        if key in self._subscribers:
            self._subscribers[key] = [
                s for s in self._subscribers[key] 
                if s.name != subscriber_name
            ]
            print(f"  [取消订阅] {subscriber_name} 取消订阅 {key}")
    
    def write(self, key: str, value: Any, author: str = "unknown"):
        """写入数据"""
        old_value = self._data.get(key)
        self._data[key] = value
        
        # 记录历史
        self._history.append({
            "key": key,
            "old_value": old_value,
            "new_value": value,
            "author": author
        })
        
        print(f"  [写入] {key} = {value} (by {author})")
        
        # 通知订阅者
        self._notify(key, value)
    
    def read(self, key: str) -> Any:
        """读取数据"""
        value = self._data.get(key)
        print(f"  [读取] {key} = {value}")
        return value
    
    def _notify(self, key: str, value: Any):
        """通知订阅者"""
        subscribers = self._subscribers.get(key, [])
        
        for subscriber in subscribers:
            try:
                subscriber.callback(key, value)
                print(f"    [通知] {subscriber.name}")
            except Exception as e:
                print(f"    [通知失败] {subscriber.name}: {e}")
    
    def get_history(self, key: str = None) -> List[Dict]:
        """获取历史记录"""
        if key:
            return [h for h in self._history if h["key"] == key]
        return self._history


# ============================================
# 3. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 12.2：黑板系统")
    print("=" * 60)
    
    blackboard = Blackboard()
    
    # 定义订阅者回调
    def order_agent_callback(key, value):
        print(f"      OrderAgent收到: {key} 更新为 {value}")
    
    def product_agent_callback(key, value):
        print(f"      ProductAgent收到: {key} 更新为 {value}")
    
    def log_agent_callback(key, value):
        print(f"      LogAgent记录: {key} = {value}")
    
    # 订阅
    print("\n订阅数据：")
    print("-" * 40)
    blackboard.subscribe("order_status", "OrderAgent", order_agent_callback)
    blackboard.subscribe("product_info", "ProductAgent", product_agent_callback)
    blackboard.subscribe("order_status", "LogAgent", log_agent_callback)
    blackboard.subscribe("product_info", "LogAgent", log_agent_callback)
    
    # 写入数据
    print("\n写入数据：")
    print("-" * 40)
    blackboard.write("order_status", "shipped", "System")
    blackboard.write("product_info", {"name": "iPhone", "price": 9999}, "Admin")
    blackboard.write("order_status", "delivered", "System")
    
    # 查看历史
    print("\n历史记录：")
    print("-" * 40)
    for h in blackboard.get_history():
        print(f"  {h['key']}: {h['old_value']} -> {h['new_value']}")
    
    print("\n" + "=" * 60)
    print("黑板系统要点：")
    print("-" * 60)
    print("1. 集中存储共享数据")
    print("2. 支持订阅/通知机制")
    print("3. 解耦智能体间依赖")
    print("4. 记录数据变更历史")
    print("=" * 60)


if __name__ == "__main__":
    main()
