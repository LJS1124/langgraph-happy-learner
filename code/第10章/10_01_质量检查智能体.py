"""
练习 10.1：质量检查智能体
问题描述：为研究助手系统添加一个新的智能体，负责"质量检查"。

学习目标：
- 扩展多智能体系统
- 实现质量检查逻辑
- 集成到工作流
"""

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from operator import add


# ============================================
# 1. 定义状态
# ============================================

class ResearchState(TypedDict):
    """研究状态"""
    query: str
    search_results: Annotated[List[str], add]
    analysis: str
    report: str
    quality_score: float
    quality_feedback: str
    final_report: str


# ============================================
# 2. 定义智能体节点
# ============================================

def search_agent(state: ResearchState) -> dict:
    """搜索智能体"""
    query = state["query"]
    print(f"  [SearchAgent] 搜索: {query}")
    
    results = [
        f"搜索结果1: 关于{query}的信息",
        f"搜索结果2: {query}的最新进展",
    ]
    
    return {"search_results": results}


def analysis_agent(state: ResearchState) -> dict:
    """分析智能体"""
    results = state["search_results"]
    print(f"  [AnalysisAgent] 分析 {len(results)} 条结果")
    
    analysis = f"分析结果: 从{len(results)}条信息中提取关键点..."
    
    return {"analysis": analysis}


def writer_agent(state: ResearchState) -> dict:
    """写作智能体"""
    analysis = state["analysis"]
    print(f"  [WriterAgent] 生成报告")
    
    report = f"研究报告\n{analysis}\n\n详细内容..."
    
    return {"report": report}


def quality_checker_agent(state: ResearchState) -> dict:
    """
    质量检查智能体（新增）
    
    检查报告质量，给出评分和反馈
    """
    report = state["report"]
    print(f"  [QualityChecker] 检查报告质量")
    
    # 质量检查逻辑
    score = 0.0
    feedback_items = []
    
    # 检查长度
    if len(report) > 100:
        score += 0.3
    else:
        feedback_items.append("报告内容过短")
    
    # 检查结构
    if "报告" in report:
        score += 0.2
    else:
        feedback_items.append("缺少报告标题")
    
    # 检查内容
    if "分析" in report:
        score += 0.3
    else:
        feedback_items.append("缺少分析内容")
    
    # 检查详细程度
    if "详细" in report:
        score += 0.2
    else:
        feedback_items.append("内容不够详细")
    
    feedback = "; ".join(feedback_items) if feedback_items else "质量良好"
    
    print(f"    质量分数: {score:.1f}")
    print(f"    反馈: {feedback}")
    
    return {
        "quality_score": score,
        "quality_feedback": feedback
    }


def finalize_report(state: ResearchState) -> dict:
    """最终报告"""
    report = state["report"]
    score = state["quality_score"]
    feedback = state["quality_feedback"]
    
    final = f"{report}\n\n---\n质量评分: {score:.1f}\n反馈: {feedback}"
    
    return {"final_report": final}


# ============================================
# 3. 构建图
# ============================================

def build_graph():
    """构建多智能体图"""
    builder = StateGraph(ResearchState)
    
    # 添加所有智能体节点
    builder.add_node("search", search_agent)
    builder.add_node("analysis", analysis_agent)
    builder.add_node("writer", writer_agent)
    builder.add_node("quality_checker", quality_checker_agent)  # 新增
    builder.add_node("finalize", finalize_report)
    
    # 设置执行顺序
    builder.set_entry_point("search")
    builder.add_edge("search", "analysis")
    builder.add_edge("analysis", "writer")
    builder.add_edge("writer", "quality_checker")  # 新增
    builder.add_edge("quality_checker", "finalize")
    builder.add_edge("finalize", END)
    
    return builder.compile()


# ============================================
# 4. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 10.1：质量检查智能体")
    print("=" * 60)
    
    graph = build_graph()
    
    result = graph.invoke({
        "query": "AI发展趋势",
        "search_results": [],
        "analysis": "",
        "report": "",
        "quality_score": 0.0,
        "quality_feedback": "",
        "final_report": ""
    })
    
    print("\n" + "=" * 60)
    print("最终报告：")
    print("-" * 60)
    print(result["final_report"])
    
    print("\n" + "=" * 60)
    print("质量检查要点：")
    print("-" * 60)
    print("1. 定义质量评估标准")
    print("2. 给出量化评分")
    print("3. 提供改进反馈")
    print("4. 可迭代改进")
    print("=" * 60)


if __name__ == "__main__":
    main()
