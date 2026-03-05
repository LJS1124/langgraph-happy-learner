"""
练习 1.1：添加新节点
问题描述：修改第一个程序，添加一个新的节点，在echo节点之后执行，将消息转换为大写。

学习目标：
- 理解节点的定义方式
- 掌握节点之间的连接
- 学会状态更新
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END


# ============================================
# 1. 定义状态
# ============================================

class State(TypedDict):
    """对话状态"""
    messages: list[str]  # 消息列表
    count: int           # 消息计数


# ============================================
# 2. 定义节点函数
# ============================================

def greet_node(state: State) -> dict:
    """问候节点：添加问候消息"""
    return {
        "messages": ["Hello from LangGraph!"],
        "count": state.get("count", 0) + 1
    }


def echo_node(state: State) -> dict:
    """回显节点：重复最后一条消息"""
    last_message = state["messages"][-1] if state["messages"] else ""
    return {
        "messages": state["messages"] + [f"Echo: {last_message}"],
        "count": state["count"] + 1
    }


def uppercase_node(state: State) -> dict:
    """
    大写转换节点：将最后一条消息转换为大写
    
    这是练习要求添加的新节点
    """
    last_message = state["messages"][-1] if state["messages"] else ""
    uppercase_message = last_message.upper()
    
    return {
        "messages": state["messages"] + [f"Uppercase: {uppercase_message}"],
        "count": state["count"] + 1
    }


# ============================================
# 3. 构建图
# ============================================

def build_graph():
    """构建并返回图"""
    # 创建图构建器
    builder = StateGraph(State)
    
    # 添加节点
    builder.add_node("greet", greet_node)
    builder.add_node("echo", echo_node)
    builder.add_node("uppercase", uppercase_node)  # 新增节点
    
    # 设置入口点
    builder.set_entry_point("greet")
    
    # 添加边（定义执行顺序）
    builder.add_edge("greet", "echo")
    builder.add_edge("echo", "uppercase")  # echo 后执行 uppercase
    builder.add_edge("uppercase", END)      # uppercase 后结束
    
    return builder.compile()


# ============================================
# 4. 运行示例
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 1.1：添加新节点")
    print("=" * 60)
    
    # 构建图
    graph = build_graph()
    
    # 运行图
    initial_state = {"messages": [], "count": 0}
    result = graph.invoke(initial_state)
    
    # 打印结果
    print("\n执行结果：")
    print("-" * 60)
    for i, msg in enumerate(result["messages"], 1):
        print(f"{i}. {msg}")
    print("-" * 60)
    print(f"总消息数: {result['count']}")


if __name__ == "__main__":
    main()


# ============================================
# 示例输出
# ============================================
"""
执行结果：
------------------------------------------------------------
1. Hello from LangGraph!
2. Echo: Hello from LangGraph!
3. Uppercase: ECHO: HELLO FROM LANGGRAPH!
------------------------------------------------------------
总消息数: 3
"""
