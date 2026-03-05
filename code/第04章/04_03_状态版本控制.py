"""
练习 4.3：状态版本控制
问题描述：设计一个支持状态版本控制的系统，能够回滚到之前的状态。

学习目标：
- 实现状态快照机制
- 掌握版本回滚逻辑
- 理解状态持久化
"""

from typing import TypedDict, List, Any, Optional
from datetime import datetime
import copy


# ============================================
# 1. 版本控制状态定义
# ============================================

class VersionInfo(TypedDict):
    """版本信息"""
    version: int
    timestamp: datetime
    description: str
    state_snapshot: dict


class VersionedState(TypedDict):
    """带版本控制的状态"""
    current: dict           # 当前状态
    versions: List[VersionInfo]  # 版本历史
    max_versions: int       # 最大版本数


# ============================================
# 2. 版本控制器
# ============================================

class StateVersionController:
    """状态版本控制器"""
    
    def __init__(self, max_versions: int = 10):
        self.max_versions = max_versions
        self.versions: List[VersionInfo] = []
        self.current_version = 0
    
    def save_version(self, state: dict, description: str = "") -> int:
        """
        保存当前状态为新版本
        
        Args:
            state: 当前状态
            description: 版本描述
        
        Returns:
            版本号
        """
        self.current_version += 1
        
        version_info = VersionInfo(
            version=self.current_version,
            timestamp=datetime.now(),
            description=description,
            state_snapshot=copy.deepcopy(state)
        )
        
        self.versions.append(version_info)
        
        # 限制版本数量
        if len(self.versions) > self.max_versions:
            self.versions.pop(0)
        
        return self.current_version
    
    def get_version(self, version: int) -> Optional[dict]:
        """
        获取指定版本的状态
        
        Args:
            version: 版本号
        
        Returns:
            状态快照，如果不存在返回None
        """
        for v in self.versions:
            if v["version"] == version:
                return copy.deepcopy(v["state_snapshot"])
        return None
    
    def rollback(self, version: int) -> Optional[dict]:
        """
        回滚到指定版本
        
        Args:
            version: 目标版本号
        
        Returns:
            回滚后的状态
        """
        state = self.get_version(version)
        if state:
            # 保存回滚操作
            self.save_version(state, f"回滚到版本 {version}")
        return state
    
    def list_versions(self) -> List[dict]:
        """列出所有版本"""
        return [
            {
                "version": v["version"],
                "timestamp": v["timestamp"].isoformat(),
                "description": v["description"]
            }
            for v in self.versions
        ]
    
    def get_latest(self) -> Optional[dict]:
        """获取最新版本"""
        if self.versions:
            return copy.deepcopy(self.versions[-1]["state_snapshot"])
        return None


# ============================================
# 3. 在LangGraph中使用
# ============================================

from langgraph.graph import StateGraph, END


class AppState(TypedDict):
    """应用状态"""
    data: dict
    version_controller: StateVersionController


def node_with_version_save(controller: StateVersionController):
    """创建带版本保存的节点装饰器"""
    def decorator(func):
        def wrapper(state: dict) -> dict:
            # 执行节点逻辑
            result = func(state)
            
            # 保存版本
            new_state = {**state, **result}
            controller.save_version(
                new_state,
                f"执行节点: {func.__name__}"
            )
            
            return result
        return wrapper
    return decorator


# ============================================
# 4. 示例使用
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 4.3：状态版本控制")
    print("=" * 60)
    
    # 创建版本控制器
    controller = StateVersionController(max_versions=5)
    
    # 初始状态
    state = {"count": 0, "data": []}
    controller.save_version(state, "初始状态")
    
    print("\n版本1: 初始状态")
    print(f"  state: {state}")
    
    # 修改状态
    state["count"] = 1
    state["data"].append("item1")
    controller.save_version(state, "添加item1")
    
    print("\n版本2: 添加item1")
    print(f"  state: {state}")
    
    # 继续修改
    state["count"] = 2
    state["data"].append("item2")
    controller.save_version(state, "添加item2")
    
    print("\n版本3: 添加item2")
    print(f"  state: {state}")
    
    # 列出所有版本
    print("\n" + "-" * 60)
    print("版本历史：")
    for v in controller.list_versions():
        print(f"  版本{v['version']}: {v['description']} ({v['timestamp']})")
    
    # 回滚到版本2
    print("\n" + "-" * 60)
    print("回滚到版本2...")
    rolled_back = controller.rollback(2)
    print(f"  回滚后状态: {rolled_back}")
    
    # 再次列出版本
    print("\n回滚后的版本历史：")
    for v in controller.list_versions():
        print(f"  版本{v['version']}: {v['description']}")
    
    print("\n" + "=" * 60)
    print("版本控制要点：")
    print("-" * 60)
    print("1. 使用深拷贝保存状态快照")
    print("2. 限制版本数量避免内存溢出")
    print("3. 记录版本描述便于追溯")
    print("4. 回滚操作也保存为新版本")
    print("=" * 60)


if __name__ == "__main__":
    main()
