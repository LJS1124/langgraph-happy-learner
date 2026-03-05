"""
练习 12.1：优先级消息队列
问题描述：实现一个支持优先级的消息队列，高优先级消息优先处理。

学习目标：
- 实现优先级队列
- 处理消息排序
- 支持紧急消息
"""

import heapq
from typing import Any, Dict, List
from datetime import datetime
from enum import IntEnum


# ============================================
# 1. 定义优先级
# ============================================

class Priority(IntEnum):
    """消息优先级"""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    URGENT = 0


# ============================================
# 2. 消息定义
# ============================================

class Message:
    """消息"""
    
    def __init__(self, content: Any, priority: Priority = Priority.NORMAL):
        self.content = content
        self.priority = priority
        self.timestamp = datetime.now()
        self.id = id(self)
    
    def __lt__(self, other):
        # 优先级小的先处理，相同优先级按时间
        if self.priority == other.priority:
            return self.timestamp < other.timestamp
        return self.priority < other.priority
    
    def __repr__(self):
        return f"Message(priority={self.priority.name}, content={self.content})"


# ============================================
# 3. 优先级消息队列
# ============================================

class PriorityMessageQueue:
    """优先级消息队列"""
    
    def __init__(self):
        self._queue: List[Message] = []
        self._counter = 0
    
    def push(self, content: Any, priority: Priority = Priority.NORMAL):
        """添加消息"""
        message = Message(content, priority)
        heapq.heappush(self._queue, message)
        print(f"  [入队] {message}")
    
    def pop(self) -> Message:
        """取出消息"""
        if self._queue:
            message = heapq.heappop(self._queue)
            print(f"  [出队] {message}")
            return message
        return None
    
    def peek(self) -> Message:
        """查看队首消息"""
        if self._queue:
            return self._queue[0]
        return None
    
    def size(self) -> int:
        """队列大小"""
        return len(self._queue)
    
    def is_empty(self) -> bool:
        """是否为空"""
        return len(self._queue) == 0
    
    def get_all(self) -> List[Message]:
        """获取所有消息（按优先级排序）"""
        return sorted(self._queue)


# ============================================
# 4. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 12.1：优先级消息队列")
    print("=" * 60)
    
    queue = PriorityMessageQueue()
    
    # 添加不同优先级的消息
    print("\n添加消息：")
    print("-" * 40)
    queue.push("普通消息1", Priority.NORMAL)
    queue.push("紧急消息", Priority.URGENT)
    queue.push("普通消息2", Priority.NORMAL)
    queue.push("高优先级消息", Priority.HIGH)
    queue.push("低优先级消息", Priority.LOW)
    
    # 查看队列
    print(f"\n队列大小: {queue.size()}")
    
    # 按优先级处理
    print("\n按优先级处理消息：")
    print("-" * 40)
    
    while not queue.is_empty():
        msg = queue.pop()
        # 模拟处理
        print(f"    处理: {msg.content}")
    
    print("\n" + "=" * 60)
    print("优先级队列要点：")
    print("-" * 60)
    print("1. 使用堆实现优先级队列")
    print("2. 定义清晰的优先级级别")
    print("3. 相同优先级按时间排序")
    print("4. 紧急消息立即处理")
    print("=" * 60)


if __name__ == "__main__":
    main()
