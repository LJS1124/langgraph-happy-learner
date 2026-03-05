"""
练习 3.1：定义复杂状态
问题描述：定义一个包含至少5个字段的状态，每个字段有不同的类型。

学习目标：
- 掌握TypedDict定义状态
- 理解不同类型字段的使用场景
- 学会Optional、List等类型注解
"""

from typing import TypedDict, Optional, List, Annotated
from datetime import datetime
from enum import Enum


# ============================================
# 1. 定义枚举类型
# ============================================

class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# ============================================
# 2. 定义嵌套类型
# ============================================

class Message(TypedDict):
    """消息结构"""
    role: MessageRole
    content: str
    timestamp: datetime


class Task(TypedDict):
    """任务结构"""
    id: str
    description: str
    status: TaskStatus
    result: Optional[str]


# ============================================
# 3. 定义主状态（5个以上字段）
# ============================================

class AgentState(TypedDict):
    """
    智能体状态 - 包含多种类型的字段
    
    字段说明：
    - session_id: 会话唯一标识
    - messages: 对话消息列表
    - current_task: 当前执行的任务
    - tasks: 任务历史
    - user_preferences: 用户偏好设置
    - error_count: 错误计数
    - last_activity: 最后活动时间
    - metadata: 元数据
    """
    
    # 字段1: 字符串类型 - 会话ID
    session_id: str
    
    # 字段2: 列表类型 - 消息历史
    messages: List[Message]
    
    # 字段3: 可选类型 - 当前任务
    current_task: Optional[Task]
    
    # 字段4: 字典类型 - 任务历史
    tasks: dict[str, Task]
    
    # 字段5: 字典类型 - 用户偏好
    user_preferences: dict[str, str]
    
    # 字段6: 整数类型 - 错误计数
    error_count: int
    
    # 字段7: 日期时间类型 - 最后活动时间
    last_activity: Optional[datetime]
    
    # 字段8: 任意类型 - 元数据
    metadata: dict


# ============================================
# 4. 创建状态实例
# ============================================

def create_initial_state(session_id: str) -> AgentState:
    """创建初始状态"""
    return AgentState(
        session_id=session_id,
        messages=[],
        current_task=None,
        tasks={},
        user_preferences={"language": "zh", "tone": "friendly"},
        error_count=0,
        last_activity=datetime.now(),
        metadata={"created_at": datetime.now().isoformat()}
    )


def create_message(role: MessageRole, content: str) -> Message:
    """创建消息"""
    return Message(
        role=role,
        content=content,
        timestamp=datetime.now()
    )


def create_task(task_id: str, description: str) -> Task:
    """创建任务"""
    return Task(
        id=task_id,
        description=description,
        status=TaskStatus.PENDING,
        result=None
    )


# ============================================
# 5. 示例使用
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 3.1：定义复杂状态")
    print("=" * 60)
    
    # 创建初始状态
    state = create_initial_state("session_001")
    
    print("\n初始状态：")
    print("-" * 60)
    print(f"会话ID: {state['session_id']}")
    print(f"消息数: {len(state['messages'])}")
    print(f"用户偏好: {state['user_preferences']}")
    print(f"错误计数: {state['error_count']}")
    
    # 添加消息
    state["messages"].append(
        create_message(MessageRole.USER, "你好，请帮我查询订单")
    )
    state["messages"].append(
        create_message(MessageRole.ASSISTANT, "好的，请提供订单号")
    )
    
    # 添加任务
    task = create_task("task_001", "查询订单状态")
    state["current_task"] = task
    state["tasks"][task["id"]] = task
    
    print("\n更新后的状态：")
    print("-" * 60)
    print(f"消息数: {len(state['messages'])}")
    print(f"当前任务: {state['current_task']['description']}")
    print(f"任务状态: {state['current_task']['status'].value}")
    
    # 打印消息历史
    print("\n消息历史：")
    for i, msg in enumerate(state["messages"], 1):
        print(f"  {i}. [{msg['role'].value}]: {msg['content']}")
    
    print("\n" + "=" * 60)
    print("状态字段类型总结：")
    print("-" * 60)
    print("  1. session_id: str")
    print("  2. messages: List[Message]")
    print("  3. current_task: Optional[Task]")
    print("  4. tasks: dict[str, Task]")
    print("  5. user_preferences: dict[str, str]")
    print("  6. error_count: int")
    print("  7. last_activity: Optional[datetime]")
    print("  8. metadata: dict")
    print("=" * 60)


if __name__ == "__main__":
    main()


# ============================================
# 示例输出
# ============================================
"""
============================================================
练习 3.1：定义复杂状态
============================================================

初始状态：
------------------------------------------------------------
会话ID: session_001
消息数: 0
用户偏好: {'language': 'zh', 'tone': 'friendly'}
错误计数: 0

更新后的状态：
------------------------------------------------------------
消息数: 2
当前任务: 查询订单状态
任务状态: pending

消息历史：
  1. [user]: 你好，请帮我查询订单
  2. [assistant]: 好的，请提供订单号

============================================================
状态字段类型总结：
------------------------------------------------------------
  1. session_id: str
  2. messages: List[Message]
  3. current_task: Optional[Task]
  4. tasks: dict[str, Task]
  5. user_preferences: dict[str, str]
  6. error_count: int
  7. last_activity: Optional[datetime]
  8. metadata: dict
============================================================
"""
