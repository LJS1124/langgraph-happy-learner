"""
练习 4.2：列表合并去重Reducer
问题描述：实现一个自定义Reducer，用于合并两个列表并去重。

学习目标：
- 深入理解Reducer机制
- 实现复杂的合并逻辑
- 处理不同类型数据的去重
"""

from typing import TypedDict, Annotated, List, Any, Callable


# ============================================
# 1. 基础去重Reducer
# ============================================

def unique_merge(left: List, right: List) -> List:
    """
    基础去重合并
    
    特点：
    - 保持顺序
    - 只保留首次出现的元素
    """
    result = list(left)  # 复制左侧列表
    seen = set(left)     # 已见元素集合
    
    for item in right:
        if item not in seen:
            result.append(item)
            seen.add(item)
    
    return result


# ============================================
# 2. 高级去重Reducer
# ============================================

def unique_by_key(key: str) -> Callable:
    """
    工厂函数：创建基于键的去重Reducer
    
    Args:
        key: 用于判断重复的键名
    
    Returns:
        Reducer函数
    """
    def reducer(left: List[dict], right: List[dict]) -> List[dict]:
        result = list(left)
        seen_keys = {item[key] for item in left if key in item}
        
        for item in right:
            if key in item and item[key] not in seen_keys:
                result.append(item)
                seen_keys.add(item[key])
        
        return result
    
    return reducer


# ============================================
# 3. 条件去重Reducer
# ============================================

def conditional_unique(
    condition: Callable[[Any], bool]
) -> Callable:
    """
    工厂函数：创建条件去重Reducer
    
    Args:
        condition: 判断是否需要去重的条件函数
    
    Returns:
        Reducer函数
    """
    def reducer(left: List, right: List) -> List:
        result = list(left)
        
        for item in right:
            if condition(item):
                # 需要去重的元素，检查是否已存在
                if item not in result:
                    result.append(item)
            else:
                # 不需要去重的元素，直接添加
                result.append(item)
        
        return result
    
    return reducer


# ============================================
# 4. 使用示例
# ============================================

from langgraph.graph import StateGraph, END


class State(TypedDict):
    """示例状态"""
    # 基础去重
    tags: Annotated[List[str], unique_merge]
    
    # 基于键去重
    users: Annotated[List[dict], unique_by_key("id")]
    
    # 条件去重
    messages: Annotated[List[str], conditional_unique(lambda x: x.startswith("system:"))]


def add_tags(state: State) -> dict:
    """添加标签"""
    return {"tags": ["python", "ai", "python"]}  # python重复


def add_users(state: State) -> dict:
    """添加用户"""
    return {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"},
            {"id": 1, "name": "Alice"},  # 重复
        ]
    }


def add_messages(state: State) -> dict:
    """添加消息"""
    return {
        "messages": [
            "system: initialized",
            "user: hello",
            "system: initialized",  # system消息去重
            "user: hi",             # user消息不去重
        ]
    }


def build_graph():
    """构建图"""
    builder = StateGraph(State)
    
    builder.add_node("add_tags", add_tags)
    builder.add_node("add_users", add_users)
    builder.add_node("add_messages", add_messages)
    
    builder.set_entry_point("add_tags")
    builder.add_edge("add_tags", "add_users")
    builder.add_edge("add_users", "add_messages")
    builder.add_edge("add_messages", END)
    
    return builder.compile()


def main():
    """主函数"""
    print("=" * 60)
    print("练习 4.2：列表合并去重Reducer")
    print("=" * 60)
    
    graph = build_graph()
    
    initial_state = {
        "tags": ["langgraph"],
        "users": [],
        "messages": []
    }
    
    print("\n初始状态：")
    print(f"  tags: {initial_state['tags']}")
    print(f"  users: {initial_state['users']}")
    print(f"  messages: {initial_state['messages']}")
    
    result = graph.invoke(initial_state)
    
    print("\n执行后状态：")
    print(f"  tags: {result['tags']}")  # 去重
    print(f"  users: {result['users']}")  # 按id去重
    print(f"  messages: {result['messages']}")  # system消息去重
    
    print("\n" + "=" * 60)
    print("Reducer类型总结：")
    print("-" * 60)
    print("1. 基础去重：unique_merge")
    print("2. 基于键去重：unique_by_key('id')")
    print("3. 条件去重：conditional_unique(condition)")
    print("=" * 60)


if __name__ == "__main__":
    main()
