"""
练习 3.2：自定义Reducer
问题描述：实现一个自定义Reducer，用于合并两个列表并去重。

学习目标：
- 理解Reducer的作用
- 掌握Annotated类型注解
- 学会自定义合并逻辑
"""

from typing import TypedDict, Annotated, List, Any
from operator import add


# ============================================
# 1. 理解默认Reducer
# ============================================

def demonstrate_default_reducer():
    """演示默认的add reducer"""
    print("=" * 60)
    print("默认Reducer演示")
    print("=" * 60)
    
    # 默认的add操作：直接拼接
    list1 = [1, 2, 3]
    list2 = [3, 4, 5]
    result = add(list1, list2)
    
    print(f"\nlist1: {list1}")
    print(f"list2: {list2}")
    print(f"add(list1, list2): {result}")
    print(f"注意: 3出现了两次，没有去重")


# ============================================
# 2. 定义自定义Reducer
# ============================================

def merge_unique(left: List[Any], right: List[Any]) -> List[Any]:
    """
    自定义Reducer：合并两个列表并去重
    
    Args:
        left: 左侧列表（当前状态）
        right: 右侧列表（新值）
    
    Returns:
        合并后的去重列表
    
    注意：
    - 保持元素顺序（先左后右）
    - 只保留第一次出现的元素
    """
    # 合并列表
    combined = left + right
    
    # 去重（保持顺序）
    seen = set()
    result = []
    
    for item in combined:
        # 对于不可哈希的类型，转换为字符串比较
        key = str(item) if not isinstance(item, (int, float, str, bool, tuple)) else item
        
        if key not in seen:
            seen.add(key)
            result.append(item)
    
    return result


def merge_unique_dicts(left: List[dict], right: List[dict]) -> List[dict]:
    """
    专门用于字典列表的去重合并
    
    根据字典的某个键（如'id'）去重
    """
    combined = left + right
    seen_ids = set()
    result = []
    
    for item in combined:
        item_id = item.get('id')
        if item_id and item_id not in seen_ids:
            seen_ids.add(item_id)
            result.append(item)
    
    return result


# ============================================
# 3. 在状态中使用自定义Reducer
# ============================================

class StateWithUniqueList(TypedDict):
    """使用自定义Reducer的状态"""
    
    # 使用Annotated注解指定Reducer
    # Annotated[类型, reducer函数]
    unique_items: Annotated[List[int], merge_unique]
    
    # 普通列表（使用默认add）
    normal_items: Annotated[List[int], add]


# ============================================
# 4. 演示效果对比
# ============================================

def demonstrate_custom_reducer():
    """演示自定义Reducer效果"""
    print("\n" + "=" * 60)
    print("自定义Reducer演示")
    print("=" * 60)
    
    # 测试数据
    left = [1, 2, 3]
    right = [3, 4, 5]
    
    print(f"\n输入数据：")
    print(f"  left: {left}")
    print(f"  right: {right}")
    
    # 默认add
    add_result = add(left, right)
    print(f"\n默认add结果: {add_result}")
    
    # 自定义merge_unique
    unique_result = merge_unique(left, right)
    print(f"自定义merge_unique结果: {unique_result}")
    
    # 测试字典列表
    print("\n" + "-" * 60)
    print("字典列表去重测试：")
    
    dict_left = [
        {'id': 1, 'name': 'Alice'},
        {'id': 2, 'name': 'Bob'}
    ]
    dict_right = [
        {'id': 2, 'name': 'Bob'},  # 重复
        {'id': 3, 'name': 'Charlie'}
    ]
    
    dict_result = merge_unique_dicts(dict_left, dict_right)
    print(f"\n合并结果：")
    for item in dict_result:
        print(f"  {item}")


# ============================================
# 5. 在LangGraph中使用
# ============================================

from langgraph.graph import StateGraph, END


def node_add_items(state: StateWithUniqueList) -> dict:
    """节点：添加新项目"""
    new_items = [3, 4, 5]  # 注意：3已存在
    
    return {
        "unique_items": new_items,  # 会使用merge_unique
        "normal_items": new_items   # 会使用add
    }


def build_graph():
    """构建图"""
    builder = StateGraph(StateWithUniqueList)
    
    builder.add_node("add_items", node_add_items)
    builder.set_entry_point("add_items")
    builder.add_edge("add_items", END)
    
    return builder.compile()


def demonstrate_in_graph():
    """在图中演示"""
    print("\n" + "=" * 60)
    print("在LangGraph中使用自定义Reducer")
    print("=" * 60)
    
    graph = build_graph()
    
    # 初始状态
    initial_state = {
        "unique_items": [1, 2, 3],
        "normal_items": [1, 2, 3]
    }
    
    print(f"\n初始状态：")
    print(f"  unique_items: {initial_state['unique_items']}")
    print(f"  normal_items: {initial_state['normal_items']}")
    
    # 执行
    result = graph.invoke(initial_state)
    
    print(f"\n执行后状态：")
    print(f"  unique_items: {result['unique_items']} (去重)")
    print(f"  normal_items: {result['normal_items']} (未去重)")


# ============================================
# 主函数
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 3.2：自定义Reducer")
    print("=" * 60)
    
    # 演示默认Reducer
    demonstrate_default_reducer()
    
    # 演示自定义Reducer
    demonstrate_custom_reducer()
    
    # 在LangGraph中使用
    demonstrate_in_graph()
    
    print("\n" + "=" * 60)
    print("总结：")
    print("-" * 60)
    print("1. 默认Reducer(add)：直接拼接列表")
    print("2. 自定义Reducer：可以实现任意合并逻辑")
    print("3. 使用Annotated[类型, reducer]指定Reducer")
    print("4. 常见场景：去重、合并、覆盖等")
    print("=" * 60)


if __name__ == "__main__":
    main()


# ============================================
# 示例输出
# ============================================
"""
============================================================
练习 3.2：自定义Reducer
============================================================

默认Reducer演示
------------------------------------------------------------

list1: [1, 2, 3]
list2: [3, 4, 5]
add(list1, list2): [1, 2, 3, 3, 4, 5]
注意: 3出现了两次，没有去重

============================================================
自定义Reducer演示
============================================================

输入数据：
  left: [1, 2, 3]
  right: [3, 4, 5]

默认add结果: [1, 2, 3, 3, 4, 5]
自定义merge_unique结果: [1, 2, 3, 4, 5]

------------------------------------------------------------
字典列表去重测试：

合并结果：
  {'id': 1, 'name': 'Alice'}
  {'id': 2, 'name': 'Bob'}
  {'id': 3, 'name': 'Charlie'}

============================================================
在LangGraph中使用自定义Reducer
============================================================

初始状态：
  unique_items: [1, 2, 3]
  normal_items: [1, 2, 3]

执行后状态：
  unique_items: [1, 2, 3, 4, 5] (去重)
  normal_items: [1, 2, 3, 3, 4, 5] (未去重)

============================================================
总结：
------------------------------------------------------------
1. 默认Reducer(add)：直接拼接列表
2. 自定义Reducer：可以实现任意合并逻辑
3. 使用Annotated[类型, reducer]指定Reducer
4. 常见场景：去重、合并、覆盖等
============================================================
"""
