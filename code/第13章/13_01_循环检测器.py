"""
练习 13.1：循环检测器
问题描述：实现一个智能的循环检测器，能够识别复杂的循环模式。

学习目标：
- 检测执行循环
- 识别重复状态
- 防止无限循环
"""

from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass


@dataclass
class ExecutionStep:
    """执行步骤"""
    node: str
    state_hash: str
    timestamp: int


class LoopDetector:
    """循环检测器"""
    
    def __init__(self, max_history: int = 100, threshold: int = 3):
        self.history: List[ExecutionStep] = []
        self.max_history = max_history
        self.threshold = threshold  # 重复次数阈值
    
    def record(self, node: str, state: Dict) -> bool:
        """记录执行步骤并检测循环"""
        state_hash = self._hash_state(state)
        step = ExecutionStep(node=node, state_hash=state_hash, timestamp=len(self.history))
        
        # 检测循环
        is_loop = self._detect_loop(step)
        
        # 记录
        self.history.append(step)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return is_loop
    
    def _hash_state(self, state: Dict) -> str:
        """生成状态哈希"""
        import json
        return json.dumps(state, sort_keys=True, default=str)
    
    def _detect_loop(self, current: ExecutionStep) -> bool:
        """检测循环"""
        # 统计相同状态出现的次数
        count = sum(1 for s in self.history if s.state_hash == current.state_hash)
        
        if count >= self.threshold:
            print(f"  [循环检测] 状态重复{count}次，可能存在循环！")
            return True
        
        # 检测节点循环模式
        if len(self.history) >= 4:
            pattern = [s.node for s in self.history[-4:]]
            if pattern[0] == pattern[2] and pattern[1] == pattern[3]:
                print(f"  [循环检测] 检测到节点循环模式: {pattern}")
                return True
        
        return False
    
    def get_loop_pattern(self) -> List[str]:
        """获取循环模式"""
        if len(self.history) < 2:
            return []
        
        # 找到最近的重复状态
        current = self.history[-1]
        for i, step in enumerate(reversed(self.history[:-1])):
            if step.state_hash == current.state_hash:
                return [s.node for s in self.history[-(i+1):]]
        
        return []


def main():
    print("=" * 60)
    print("练习 13.1：循环检测器")
    print("=" * 60)
    
    detector = LoopDetector(threshold=3)
    
    # 模拟执行
    print("\n模拟执行：")
    print("-" * 40)
    
    states = [
        {"node": "A", "state": {"count": 0}},
        {"node": "B", "state": {"count": 1}},
        {"node": "A", "state": {"count": 2}},
        {"node": "B", "state": {"count": 3}},
        {"node": "A", "state": {"count": 4}},
        {"node": "B", "state": {"count": 5}},
    ]
    
    for s in states:
        is_loop = detector.record(s["node"], s["state"])
        print(f"  执行 {s['node']}, 循环={is_loop}")
    
    print("\n" + "=" * 60)
    print("循环检测要点：")
    print("-" * 60)
    print("1. 记录执行历史")
    print("2. 检测状态重复")
    print("3. 识别节点循环模式")
    print("4. 设置阈值触发告警")
    print("=" * 60)


if __name__ == "__main__":
    main()
