"""
练习 6.3：人工介入迭代改进
问题描述：设计一个支持"人工介入"的迭代改进图。

学习目标：
- 实现人机协作模式
- 使用interrupt机制
- 处理人工反馈
"""

from typing import TypedDict, Literal, Optional
from langgraph.graph import StateGraph, END


# ============================================
# 1. 定义状态
# ============================================

class ImprovementState(TypedDict):
    """改进状态"""
    content: str              # 原始内容
    current_version: str      # 当前版本
    quality_score: float      # 质量分数
    iteration: int            # 迭代次数
    max_iterations: int       # 最大迭代次数
    human_feedback: Optional[str]  # 人工反馈
    needs_human: bool         # 是否需要人工介入
    final_content: str        # 最终内容


# ============================================
# 2. 定义节点
# ============================================

def auto_improve(state: ImprovementState) -> dict:
    """自动改进节点"""
    content = state["current_version"]
    iteration = state["iteration"] + 1
    
    print(f"  自动改进 (迭代 {iteration})")
    
    # 模拟改进（每次提高0.1分）
    improved = f"[改进v{iteration}] {content}"
    new_score = min(state["quality_score"] + 0.1, 0.85)  # 最高0.85
    
    return {
        "current_version": improved,
        "quality_score": new_score,
        "iteration": iteration
    }


def evaluate_quality(state: ImprovementState) -> dict:
    """评估质量节点"""
    score = state["quality_score"]
    iteration = state["iteration"]
    
    print(f"  评估质量: {score:.2f}")
    
    # 判断是否需要人工介入
    # 条件：迭代3次后质量仍低于0.8
    needs_human = iteration >= 3 and score < 0.8
    
    return {"needs_human": needs_human}


def human_review(state: ImprovementState) -> dict:
    """人工审核节点（模拟）"""
    print("  等待人工审核...")
    
    # 模拟人工反馈
    feedback = state.get("human_feedback")
    if not feedback:
        feedback = "请增加更多细节"
    
    print(f"  人工反馈: {feedback}")
    
    # 根据反馈改进
    improved = f"{state['current_version']} [人工修改: {feedback}]"
    
    return {
        "current_version": improved,
        "quality_score": 0.9,  # 人工修改后质量提升
        "human_feedback": None
    }


def finalize(state: ImprovementState) -> dict:
    """最终处理节点"""
    print("  生成最终版本")
    return {"final_content": state["current_version"]}


# ============================================
# 3. 路由函数
# ============================================

def should_continue(state: ImprovementState) -> Literal["auto", "human", "done"]:
    """
    决定下一步：
    - auto: 继续自动改进
    - human: 需要人工介入
    - done: 完成
    """
    score = state["quality_score"]
    iteration = state["iteration"]
    max_iter = state["max_iterations"]
    
    # 质量达标，完成
    if score >= 0.8:
        print(f"  路由: 质量达标 ({score:.2f} >= 0.8) → 完成")
        return "done"
    
    # 需要人工介入
    if state["needs_human"]:
        print(f"  路由: 需要人工介入 → 人工审核")
        return "human"
    
    # 超过最大迭代次数
    if iteration >= max_iter:
        print(f"  路由: 超过最大迭代次数 → 完成")
        return "done"
    
    # 继续自动改进
    print(f"  路由: 继续自动改进")
    return "auto"


# ============================================
# 4. 构建图
# ============================================

def build_graph():
    """
    构建人工介入迭代改进图
    
    结构：
    START → auto_improve → evaluate → (条件边)
                                      ├→ auto_improve (回环)
                                      ├→ human_review → auto_improve
                                      └→ finalize → END
    """
    builder = StateGraph(ImprovementState)
    
    # 添加节点
    builder.add_node("auto_improve", auto_improve)
    builder.add_node("evaluate", evaluate_quality)
    builder.add_node("human_review", human_review)
    builder.add_node("finalize", finalize)
    
    # 设置入口
    builder.set_entry_point("auto_improve")
    
    # 添加边
    builder.add_edge("auto_improve", "evaluate")
    
    # 条件边
    builder.add_conditional_edges(
        "evaluate",
        should_continue,
        {
            "auto": "auto_improve",
            "human": "human_review",
            "done": "finalize"
        }
    )
    
    builder.add_edge("human_review", "auto_improve")
    builder.add_edge("finalize", END)
    
    return builder.compile()


# ============================================
# 5. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 6.3：人工介入迭代改进")
    print("=" * 60)
    
    graph = build_graph()
    
    # 初始状态（质量较低，需要迭代改进）
    initial_state = {
        "content": "原始内容",
        "current_version": "原始内容",
        "quality_score": 0.5,
        "iteration": 0,
        "max_iterations": 5,
        "human_feedback": None,
        "needs_human": False,
        "final_content": ""
    }
    
    print("\n开始迭代改进：")
    print("-" * 60)
    
    result = graph.invoke(initial_state)
    
    print("-" * 60)
    print("\n最终结果：")
    print(f"  迭代次数: {result['iteration']}")
    print(f"  最终质量: {result['quality_score']:.2f}")
    print(f"  最终内容: {result['final_content'][:50]}...")
    
    print("\n" + "=" * 60)
    print("人工介入要点：")
    print("-" * 60)
    print("1. 设置质量阈值触发人工介入")
    print("2. 使用needs_human标志")
    print("3. 人工反馈后继续自动流程")
    print("4. 设置最大迭代次数防止无限循环")
    print("=" * 60)


if __name__ == "__main__":
    main()
