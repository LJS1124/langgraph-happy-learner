"""
练习 1.2：条件边实现
问题描述：添加一个条件边：如果count大于2，直接结束；否则继续执行greet节点。

学习目标：
- 理解条件边的概念
- 掌握路由函数的编写
- 学会基于状态做决策
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


# ============================================
# 1. 定义状态
# ============================================

class State(TypedDict):
    """对话状态"""
    messages: list[str]
    count: int


# ============================================
# 2. 定义节点函数
# ============================================

def greet_node(state: State) -> dict:
    """问候节点"""
    print(f"  执行 greet_node, count={state['count']}")
    return {
        "messages": state["messages"] + [f"Greeting #{state['count'] + 1}"],
        "count": state["count"] + 1
    }


def echo_node(state: State) -> dict:
    """回显节点"""
    print(f"  执行 echo_node, count={state['count']}")
    last_message = state["messages"][-1] if state["messages"] else ""
    return {
        "messages": state["messages"] + [f"Echo: {last_message}"],
        "count": state["count"] + 1
    }


# ============================================
# 3. 定义路由函数（条件边）
# ============================================

def should_continue(state: State) -> Literal["continue", "end"]:
    """
    路由函数：决定是否继续执行
    
    如果 count > 2，结束；否则继续
    
    Returns:
        "continue": 继续执行 greet 节点
        "end": 结束执行
    """
    if state["count"] > 2:
        print(f"  路由决策: count={state['count']} > 2, 结束")
        return "end"
    else:
        print(f"  路由决策: count={state['count']} <= 2, 继续")
        return "continue"


# ============================================
# 4. 构建图
# ============================================

def build_graph():
    """构建带条件边的图"""
    builder = StateGraph(State)
    
    # 添加节点
    builder.add_node("greet", greet_node)
    builder.add_node("echo", echo_node)
    
    # 设置入口点
    builder.set_entry_point("greet")
    
    # 添加普通边
    builder.add_edge("greet", "echo")
    
    # 添加条件边（关键！）
    # 从 echo 节点出发，根据 should_continue 的返回值决定下一步
    builder.add_conditional_edges(
        "echo",
        should_continue,
        {
            "continue": "greet",  # 返回 "continue" 时，跳转到 greet
            "end": END            # 返回 "end" 时，结束
        }
    )
    
    return builder.compile()


# ============================================
# 5. 运行示例
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 1.2：条件边实现")
    print("=" * 60)
    
    graph = build_graph()
    
    print("\n开始执行：")
    print("-" * 60)
    
    initial_state = {"messages": [], "count": 0}
    result = graph.invoke(initial_state)
    
    print("-" * 60)
    print("\n最终结果：")
    for i, msg in enumerate(result["messages"], 1):
        print(f"  {i}. {msg}")
    print(f"\n总执行次数: {result['count']}")


if __name__ == "__main__":
    main()


# ============================================
# 示例输出
# ============================================
"""
开始执行：
------------------------------------------------------------
  执行 greet_node, count=0
  执行 echo_node, count=1
  路由决策: count=1 <= 2, 继续
  执行 greet_node, count=1
  执行 echo_node, count=2
  路由决策: count=2 <= 2, 继续
  执行 greet_node, count=2
  执行 echo_node, count=3
  路由决策: count=3 > 2, 结束
------------------------------------------------------------

最终结果：
  1. Greeting #1
  2. Echo: Greeting #1
  3. Greeting #2
  4. Echo: Greeting #2
  5. Greeting #3
  6. Echo: Greeting #3

总执行次数: 3
"""
