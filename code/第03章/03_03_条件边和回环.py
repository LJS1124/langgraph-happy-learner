"""
练习 3.3：条件边和回环
问题描述：构建一个包含条件边和回环边的图，实现迭代推理。

学习目标：
- 理解条件边的概念
- 掌握回环（循环）的实现
- 学会迭代推理模式
"""

from typing import TypedDict, Literal, Annotated
from langgraph.graph import StateGraph, END
from operator import add


# ============================================
# 1. 定义状态
# ============================================

class ReasoningState(TypedDict):
    """推理状态"""
    question: str           # 原始问题
    thoughts: Annotated[list[str], add]  # 思考过程
    answer: str             # 最终答案
    iteration: int          # 迭代次数
    is_complete: bool       # 是否完成


# ============================================
# 2. 定义节点函数
# ============================================

def think_node(state: ReasoningState) -> dict:
    """
    思考节点：分析问题，生成思考
    
    在实际应用中，这里会调用LLM
    """
    iteration = state["iteration"] + 1
    
    # 模拟思考过程（实际应调用LLM）
    if iteration == 1:
        thought = f"第{iteration}次思考：分析问题 '{state['question']}'"
    elif iteration == 2:
        thought = f"第{iteration}次思考：深入分析关键点"
    elif iteration == 3:
        thought = f"第{iteration}次思考：综合分析得出结论"
    else:
        thought = f"第{iteration}次思考：验证和完善答案"
    
    print(f"  [think_node] {thought}")
    
    return {
        "thoughts": [thought],
        "iteration": iteration
    }


def answer_node(state: ReasoningState) -> dict:
    """
    回答节点：生成最终答案
    """
    # 模拟生成答案
    answer = f"基于{state['iteration']}次思考，答案是：..."
    
    print(f"  [answer_node] 生成答案")
    
    return {
        "answer": answer,
        "is_complete": True
    }


# ============================================
# 3. 定义路由函数（条件边）
# ============================================

def should_continue(state: ReasoningState) -> Literal["continue", "answer"]:
    """
    路由函数：决定继续思考还是生成答案
    
    条件：
    - 迭代次数 < 3：继续思考
    - 迭代次数 >= 3：生成答案
    """
    if state["iteration"] < 3:
        print(f"  [路由] 迭代{state['iteration']} < 3，继续思考")
        return "continue"
    else:
        print(f"  [路由] 迭代{state['iteration']} >= 3，生成答案")
        return "answer"


# ============================================
# 4. 构建图（包含回环）
# ============================================

def build_reasoning_graph():
    """
    构建推理图
    
    结构：
    START -> think -> (条件边) -> think (回环)
                       |
                       v
                     answer -> END
    """
    builder = StateGraph(ReasoningState)
    
    # 添加节点
    builder.add_node("think", think_node)
    builder.add_node("answer", answer_node)
    
    # 设置入口点
    builder.set_entry_point("think")
    
    # 添加条件边（关键：实现回环）
    builder.add_conditional_edges(
        "think",
        should_continue,
        {
            "continue": "think",  # 回环：继续执行think节点
            "answer": "answer"    # 前进：执行answer节点
        }
    )
    
    # 添加普通边
    builder.add_edge("answer", END)
    
    return builder.compile()


# ============================================
# 5. 运行示例
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 3.3：条件边和回环")
    print("=" * 60)
    
    # 构建图
    graph = build_reasoning_graph()
    
    # 初始状态
    initial_state = {
        "question": "什么是LangGraph？",
        "thoughts": [],
        "answer": "",
        "iteration": 0,
        "is_complete": False
    }
    
    print("\n开始迭代推理：")
    print("-" * 60)
    
    # 执行图
    result = graph.invoke(initial_state)
    
    print("-" * 60)
    print("\n最终结果：")
    print(f"  问题: {result['question']}")
    print(f"  迭代次数: {result['iteration']}")
    print(f"  思考过程:")
    for i, thought in enumerate(result['thoughts'], 1):
        print(f"    {i}. {thought}")
    print(f"  答案: {result['answer']}")


# ============================================
# 6. 可视化图结构
# ============================================

def print_graph_structure():
    """打印图结构"""
    print("\n" + "=" * 60)
    print("图结构说明")
    print("=" * 60)
    
    print("""
    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   START ──→ think ──┬──→ think (回环)              │
    │              │      │         ↑                    │
    │              │      └─────────┘                    │
    │              │                                     │
    │              └──→ answer ──→ END                   │
    │                                                     │
    │   条件边逻辑：                                      │
    │   - iteration < 3 → 继续 think                     │
    │   - iteration >= 3 → 执行 answer                   │
    │                                                     │
    └─────────────────────────────────────────────────────┘
    """)


if __name__ == "__main__":
    main()
    print_graph_structure()


# ============================================
# 示例输出
# ============================================
"""
============================================================
练习 3.3：条件边和回环
============================================================

开始迭代推理：
------------------------------------------------------------
  [think_node] 第1次思考：分析问题 '什么是LangGraph？'
  [路由] 迭代1 < 3，继续思考
  [think_node] 第2次思考：深入分析关键点
  [路由] 迭代2 < 3，继续思考
  [think_node] 第3次思考：综合分析得出结论
  [路由] 迭代3 >= 3，生成答案
  [answer_node] 生成答案
------------------------------------------------------------

最终结果：
  问题: 什么是LangGraph？
  迭代次数: 3
  思考过程:
    1. 第1次思考：分析问题 '什么是LangGraph？'
    2. 第2次思考：深入分析关键点
    3. 第3次思考：综合分析得出结论
  答案: 基于3次思考，答案是：...

============================================================
图结构说明
============================================================

    ┌─────────────────────────────────────────────────────┐
    │                                                     │
    │   START ──→ think ──┬──→ think (回环)              │
    │              │      │         ↑                    │
    │              │      └─────────┘                    │
    │              │                                     │
    │              └──→ answer ──→ END                   │
    │                                                     │
    │   条件边逻辑：                                      │
    │   - iteration < 3 → 继续 think                     │
    │   - iteration >= 3 → 执行 answer                   │
    │                                                     │
    └─────────────────────────────────────────────────────┘
"""
