"""
练习 11.1：权限控制状态管理器
问题描述：实现一个带权限控制的状态管理器，支持读写权限分离。

学习目标：
- 实现状态访问控制
- 分离读写权限
- 保护敏感数据
"""

from typing import TypedDict, Dict, Set, Any, Optional
from enum import Enum


# ============================================
# 1. 定义权限枚举
# ============================================

class Permission(Enum):
    """权限类型"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


# ============================================
# 2. 权限控制状态管理器
# ============================================

class PermissionControlledState:
    """带权限控制的状态管理器"""
    
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._permissions: Dict[str, Set[Permission]] = {}
        self._field_permissions: Dict[str, Dict[str, Set[Permission]]] = {}
    
    def set_field_permission(self, field: str, agent: str, permissions: Set[Permission]):
        """设置字段权限"""
        if field not in self._field_permissions:
            self._field_permissions[field] = {}
        self._field_permissions[field][agent] = permissions
        print(f"  设置权限: {agent} -> {field}: {[p.value for p in permissions]}")
    
    def can_read(self, agent: str, field: str) -> bool:
        """检查读权限"""
        field_perms = self._field_permissions.get(field, {})
        agent_perms = field_perms.get(agent, set())
        return Permission.READ in agent_perms or Permission.ADMIN in agent_perms
    
    def can_write(self, agent: str, field: str) -> bool:
        """检查写权限"""
        field_perms = self._field_permissions.get(field, {})
        agent_perms = field_perms.get(agent, set())
        return Permission.WRITE in agent_perms or Permission.ADMIN in agent_perms
    
    def get(self, agent: str, field: str) -> Optional[Any]:
        """读取状态（带权限检查）"""
        if not self.can_read(agent, field):
            print(f"  [权限拒绝] {agent} 无法读取 {field}")
            return None
        
        value = self._state.get(field)
        print(f"  [读取成功] {agent} -> {field}: {value}")
        return value
    
    def set(self, agent: str, field: str, value: Any) -> bool:
        """写入状态（带权限检查）"""
        if not self.can_write(agent, field):
            print(f"  [权限拒绝] {agent} 无法写入 {field}")
            return False
        
        self._state[field] = value
        print(f"  [写入成功] {agent} -> {field}: {value}")
        return True
    
    def get_all_readable(self, agent: str) -> Dict[str, Any]:
        """获取所有可读字段"""
        result = {}
        for field in self._state:
            if self.can_read(agent, field):
                result[field] = self._state[field]
        return result


# ============================================
# 3. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 11.1：权限控制状态管理器")
    print("=" * 60)
    
    # 创建状态管理器
    state_manager = PermissionControlledState()
    
    # 设置权限
    print("\n设置权限：")
    print("-" * 40)
    state_manager.set_field_permission("user_info", "order_agent", {Permission.READ})
    state_manager.set_field_permission("user_info", "admin_agent", {Permission.READ, Permission.WRITE})
    state_manager.set_field_permission("order_data", "order_agent", {Permission.READ, Permission.WRITE})
    state_manager.set_field_permission("order_data", "product_agent", {Permission.READ})
    state_manager.set_field_permission("system_config", "admin_agent", {Permission.ADMIN})
    
    # 初始化数据
    state_manager._state = {
        "user_info": {"name": "张三", "phone": "138****8000"},
        "order_data": {"order_id": "001", "status": "shipped"},
        "system_config": {"debug": False}
    }
    
    # 测试权限
    print("\n测试权限：")
    print("-" * 40)
    
    # order_agent 读取 user_info（有权限）
    print("\n1. order_agent 读取 user_info:")
    state_manager.get("order_agent", "user_info")
    
    # order_agent 写入 user_info（无权限）
    print("\n2. order_agent 写入 user_info:")
    state_manager.set("order_agent", "user_info", {"name": "李四"})
    
    # admin_agent 写入 user_info（有权限）
    print("\n3. admin_agent 写入 user_info:")
    state_manager.set("admin_agent", "user_info", {"name": "李四"})
    
    # product_agent 读取 order_data（有权限）
    print("\n4. product_agent 读取 order_data:")
    state_manager.get("product_agent", "order_data")
    
    # product_agent 写入 order_data（无权限）
    print("\n5. product_agent 写入 order_data:")
    state_manager.set("product_agent", "order_data", {"status": "delivered"})
    
    print("\n" + "=" * 60)
    print("权限控制要点：")
    print("-" * 60)
    print("1. 定义权限类型（读/写/管理）")
    print("2. 每个字段设置独立权限")
    print("3. 访问前检查权限")
    print("4. 记录访问日志")
    print("=" * 60)


if __name__ == "__main__":
    main()
