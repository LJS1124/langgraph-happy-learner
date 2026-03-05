"""
练习 6.1：路由分支扩展
问题描述：添加一个新的路由分支，当质量分数在 0.5-0.7 之间时，使用"轻度改进"策略。

学习目标：
- 扩展条件路由
- 实现多分支决策
- 理解路由优先级
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END


# ============================================
# 1. 定义状态
# ============================================

class QualityState(TypedDict):
    """质量评估状态"""
    content: str           # 内容
    quality_score: float   # 质量分数 (0-1)
    improved_content: str  # 改进后的内容
    improvement_type: str  # 改进类型


# ============================================
# 2. 定义节点
# ============================================

def assess_quality(state: QualityState) -> dict:
    """评估质量节点"""
    content = state["content"]
    # 模拟质量评估
    score = len(content) / 100  # 简单示例
    score = min(max(score, 0), 1)  # 限制在0-1之间
    
    print(f"  评估质量: {score:.2f}")
    return {"quality_score": score}


def major_improve(state: QualityState) -> dict:
    """重大改进节点（质量 < 0.5）"""
    print(f"  执行重大改进")
    return {
        "improved_content": f"[重大改进] {state['content']}",
        "improvement_type": "major"
    }


def minor_improve(state: QualityState) -> dict:
    """轻度改进节点（0.5 <= 质量 < 0.7）"""
    print(f"  执行轻度改进")
    return {
        "improved_content": f"[轻度改进] {state['content']}",
        "improvement_type": "minor"
    }


def fine_tune(state: QualityState) -> dict:
    """微调节点（质量 >= 0.7）"""
    print(f"  执行微调")
    return {
        "improved_content": f"[微调] {state['content']}",
        "improvement_type": "fine_tune"
    }


# ============================================
# 3. 路由函数
# ============================================

def route_by_quality(state: QualityState) -> Literal["major", "minor", "fine"]:
    """
    根据质量分数路由
    
    分支规则：
    - quality_score < 0.5: 重大改进
    - 0.5 <= quality_score < 0.7: 轻度改进（新增）
    - quality_score >= 0.7: 微调
    """
    score = state["quality_score"]
    
    if score < 0.5:
        print(f"  路由决策: {score:.2f} < 0.5 → 重大改进")
        return "major"
    elif score < 0.7:
        print(f"  路由决策: 0.5 <= {score:.2f} < 0.7 → 轻度改进")
        return "minor"
    else:
        print(f"  路由决策: {score:.2f} >= 0.7 → 微调")
        return "fine"


# ============================================
# 4. 构建图
# ============================================

def build_graph():
    """构建多分支路由图"""
    builder = StateGraph(QualityState)
    
    # 添加节点
    builder.add_node("assess", assess_quality)
    builder.add_node("major_improve", major_improve)
    builder.add_node("minor_improve", minor_improve)  # 新增
    builder.add_node("fine_tune", fine_tune)
    
    # 设置入口
    builder.set_entry_point("assess")
    
    # 添加条件边
    builder.add_conditional_edges(
        "assess",
        route_by_quality,
        {
            "major": "major_improve",
            "minor": "minor_improve",  # 新增分支
            "fine": "fine_tune"
        }
    )
    
    # 所有改进节点都指向END
    builder.add_edge("major_improve", END)
    builder.add_edge("minor_improve", END)
    builder.add_edge("fine_tune", END)
    
    return builder.compile()


# ============================================
# 5. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 6.1：路由分支扩展")
    print("=" * 60)
    
    graph = build_graph()
    
    # 测试不同质量分数
    test_cases = [
        ("短内容", "短"),           # 质量 < 0.5
        ("中等内容", "这是一段中等长度的内容"),  # 0.5 <= 质量 < 0.7
        ("长内容", "这是一段很长很长的内容" * 10),  # 质量 >= 0.7
    ]
    
    for name, content in test_cases:
        print(f"\n测试: {name}")
        print("-" * 60)
        
        result = graph.invoke({
            "content": content,
            "quality_score": 0,
            "improved_content": "",
            "improvement_type": ""
        })
        
        print(f"\n结果:")
        print(f"  质量分数: {result['quality_score']:.2f}")
        print(f"  改进类型: {result['improvement_type']}")
        print(f"  改进后: {result['improved_content'][:50]}...")
    
    print("\n" + "=" * 60)
    print("路由分支要点：")
    print("-" * 60)
    print("1. 条件边支持多分支")
    print("2. 路由函数返回分支标识")
    print("3. 分支标识映射到目标节点")
    print("4. 注意条件的优先级顺序")
    print("=" * 60)


if __name__ == "__main__":
    main()
