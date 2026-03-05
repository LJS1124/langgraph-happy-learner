"""
练习 11.2：状态版本控制系统
问题描述：设计一个状态版本控制系统，支持冲突检测和合并。

学习目标：
- 实现版本控制
- 检测冲突
- 合并变更
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import copy


# ============================================
# 1. 版本定义
# ============================================

class Version:
    """版本"""
    
    def __init__(self, version_id: int, state: Dict, author: str, message: str):
        self.version_id = version_id
        self.state = copy.deepcopy(state)
        self.author = author
        self.message = message
        self.timestamp = datetime.now()
        self.parent_id: Optional[int] = None


# ============================================
# 2. 版本控制系统
# ============================================

class StateVersionControl:
    """状态版本控制系统"""
    
    def __init__(self):
        self.versions: Dict[int, Version] = {}
        self.current_version_id = 0
        self.branches: Dict[str, int] = {"main": 0}
        self.current_branch = "main"
    
    def commit(self, state: Dict, author: str, message: str) -> int:
        """提交新版本"""
        self.current_version_id += 1
        
        version = Version(
            version_id=self.current_version_id,
            state=state,
            author=author,
            message=message
        )
        version.parent_id = self.branches[self.current_branch]
        
        self.versions[self.current_version_id] = version
        self.branches[self.current_branch] = self.current_version_id
        
        print(f"  [Commit] v{self.current_version_id}: {message}")
        return self.current_version_id
    
    def checkout(self, version_id: int) -> Optional[Dict]:
        """检出指定版本"""
        if version_id in self.versions:
            version = self.versions[version_id]
            print(f"  [Checkout] v{version_id}")
            return copy.deepcopy(version.state)
        return None
    
    def diff(self, version_id1: int, version_id2: int) -> Dict:
        """比较两个版本"""
        v1 = self.versions.get(version_id1)
        v2 = self.versions.get(version_id2)
        
        if not v1 or not v2:
            return {}
        
        diff_result = {}
        all_keys = set(v1.state.keys()) | set(v2.state.keys())
        
        for key in all_keys:
            val1 = v1.state.get(key)
            val2 = v2.state.get(key)
            
            if val1 != val2:
                diff_result[key] = {"old": val1, "new": val2}
        
        return diff_result
    
    def detect_conflict(self, version_id1: int, version_id2: int, base_id: int) -> List[str]:
        """检测冲突"""
        base = self.versions.get(base_id)
        v1 = self.versions.get(version_id1)
        v2 = self.versions.get(version_id2)
        
        if not base or not v1 or not v2:
            return []
        
        conflicts = []
        
        for key in set(v1.state.keys()) & set(v2.state.keys()):
            # 两个版本都修改了同一个字段
            if (v1.state.get(key) != base.state.get(key) and 
                v2.state.get(key) != base.state.get(key) and
                v1.state.get(key) != v2.state.get(key)):
                conflicts.append(key)
        
        return conflicts
    
    def merge(self, version_id1: int, version_id2: int, base_id: int, 
              author: str, strategy: str = "latest") -> int:
        """合并两个版本"""
        conflicts = self.detect_conflict(version_id1, version_id2, base_id)
        
        if conflicts:
            print(f"  [冲突] 检测到冲突字段: {conflicts}")
            if strategy == "latest":
                print("  [策略] 使用最新版本")
        
        v1 = self.versions[version_id1]
        v2 = self.versions[version_id2]
        
        merged_state = copy.deepcopy(v1.state)
        
        for key, value in v2.state.items():
            if key not in merged_state:
                merged_state[key] = value
            elif key in conflicts:
                if strategy == "latest":
                    # 使用版本号较大的
                    if version_id2 > version_id1:
                        merged_state[key] = value
        
        return self.commit(merged_state, author, f"Merge v{version_id1} and v{version_id2}")
    
    def log(self) -> List[Dict]:
        """查看版本历史"""
        history = []
        for vid in sorted(self.versions.keys(), reverse=True):
            v = self.versions[vid]
            history.append({
                "version": vid,
                "author": v.author,
                "message": v.message,
                "timestamp": v.timestamp.isoformat()
            })
        return history


# ============================================
# 3. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 11.2：状态版本控制系统")
    print("=" * 60)
    
    vcs = StateVersionControl()
    
    # 初始提交
    print("\n初始提交：")
    print("-" * 40)
    vcs.commit({"count": 0, "data": []}, "user1", "初始状态")
    
    # 修改并提交
    print("\n修改提交：")
    print("-" * 40)
    vcs.commit({"count": 1, "data": ["a"]}, "user1", "添加数据a")
    vcs.commit({"count": 2, "data": ["a", "b"]}, "user2", "添加数据b")
    
    # 查看历史
    print("\n版本历史：")
    print("-" * 40)
    for entry in vcs.log():
        print(f"  v{entry['version']}: {entry['message']} (by {entry['author']})")
    
    # 检出
    print("\n检出v2：")
    print("-" * 40)
    state = vcs.checkout(2)
    print(f"  状态: {state}")
    
    # 差异
    print("\n比较v1和v3：")
    print("-" * 40)
    diff = vcs.diff(1, 3)
    for key, change in diff.items():
        print(f"  {key}: {change['old']} -> {change['new']}")
    
    print("\n" + "=" * 60)
    print("版本控制要点：")
    print("-" * 60)
    print("1. 记录每次变更")
    print("2. 支持版本回退")
    print("3. 检测合并冲突")
    print("4. 提供合并策略")
    print("=" * 60)


if __name__ == "__main__":
    main()
