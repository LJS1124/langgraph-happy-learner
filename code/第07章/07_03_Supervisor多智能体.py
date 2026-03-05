"""
练习 7.3：Supervisor多智能体
问题描述：设计一个Supervisor模式的多智能体系统，包含至少三个工作节点。

学习目标：
- 实现Supervisor模式
- 协调多个工作节点
- 整合工作结果
"""

from typing import TypedDict, Literal, Annotated, List
from langgraph.graph import StateGraph, END
from operator import add


# ============================================
# 1. 定义状态
# ============================================

class WorkerResult(TypedDict):
    """工作节点结果"""
    worker: str
    task: str
    result: str


class SupervisorState(TypedDict):
    """Supervisor状态"""
    user_request: str
    tasks: List[str]
    current_task: str
    worker_results: Annotated[List[WorkerResult], add]
    final_response: str


# ============================================
# 2. Supervisor节点
# ============================================

def supervisor_node(state: SupervisorState) -> dict:
    """Supervisor节点：分解任务"""
    request = state["user_request"]
    
    print(f"  Supervisor: 分析请求 '{request}'")
    
    # 任务分解（实际应使用LLM）
    tasks = [
        "搜索相关信息",
        "分析数据",
        "生成报告"
    ]
    
    print(f"  Supervisor: 分解为 {len(tasks)} 个任务")
    
    return {"tasks": tasks}


def task_dispatcher(state: SupervisorState) -> dict:
    """任务分发节点"""
    tasks = state["tasks"]
    
    if tasks:
        current_task = tasks[0]
        remaining = tasks[1:]
        print(f"  分发任务: {current_task}")
        return {"current_task": current_task, "tasks": remaining}
    
    return {"current_task": ""}


# ============================================
# 3. 工作节点
# ============================================

def search_worker(state: SupervisorState) -> dict:
    """搜索工作节点"""
    task = state["current_task"]
    
    if "搜索" not in task:
        return {}
    
    print(f"    [SearchWorker] 执行: {task}")
    
    return {
        "worker_results": [{
            "worker": "search",
            "task": task,
            "result": "找到5条相关信息"
        }]
    }


def analysis_worker(state: SupervisorState) -> dict:
    """分析工作节点"""
    task = state["current_task"]
    
    if "分析" not in task:
        return {}
    
    print(f"    [AnalysisWorker] 执行: {task}")
    
    return {
        "worker_results": [{
            "worker": "analysis",
            "task": task,
            "result": "分析完成，发现3个关键点"
        }]
    }


def writer_worker(state: SupervisorState) -> dict:
    """写作工作节点"""
    task = state["current_task"]
    
    if "报告" not in task and "生成" not in task:
        return {}
    
    print(f"    [WriterWorker] 执行: {task}")
    
    return {
        "worker_results": [{
            "worker": "writer",
            "task": task,
            "result": "报告已生成"
        }]
    }


# ============================================
# 4. 路由函数
# ============================================

def route_to_worker(state: SupervisorState) -> Literal["search", "analysis", "writer", "aggregate"]:
    """路由到对应的工作节点"""
    task = state["current_task"]
    
    if not task:
        return "aggregate"
    
    if "搜索" in task:
        return "search"
    elif "分析" in task:
        return "analysis"
    elif "报告" in task or "生成" in task:
        return "writer"
    
    return "aggregate"


def should_continue(state: SupervisorState) -> Literal["dispatch", "aggregate"]:
    """判断是否还有任务"""
    if state["tasks"]:
        return "dispatch"
    return "aggregate"


# ============================================
# 5. 结果聚合节点
# ============================================

def aggregate_results(state: SupervisorState) -> dict:
    """聚合结果节点"""
    results = state["worker_results"]
    
    print("  聚合工作结果:")
    for r in results:
        print(f"    [{r['worker']}] {r['result']}")
    
    # 生成最终响应
    final = "\n".join([r["result"] for r in results])
    
    return {"final_response": f"完成！\n{final}"}


# ============================================
# 6. 构建图
# ============================================

def build_supervisor_graph():
    """
    构建Supervisor模式图
    
    结构：
    START → supervisor → dispatcher → (条件边)
                                     ├→ search_worker ─┐
                                     ├→ analysis_worker┼→ dispatcher (回环)
                                     └→ writer_worker ─┘
                                     ↓
                                   aggregate → END
    """
    builder = StateGraph(SupervisorState)
    
    # 添加节点
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("dispatcher", task_dispatcher)
    builder.add_node("search", search_worker)
    builder.add_node("analysis", analysis_worker)
    builder.add_node("writer", writer_worker)
    builder.add_node("aggregate", aggregate_results)
    
    # 设置入口
    builder.set_entry_point("supervisor")
    
    # 添加边
    builder.add_edge("supervisor", "dispatcher")
    
    # 条件路由到工作节点
    builder.add_conditional_edges(
        "dispatcher",
        route_to_worker,
        {
            "search": "search",
            "analysis": "analysis",
            "writer": "writer",
            "aggregate": "aggregate"
        }
    )
    
    # 工作节点完成后判断是否继续
    for worker in ["search", "analysis", "writer"]:
        builder.add_conditional_edges(
            worker,
            should_continue,
            {
                "dispatch": "dispatcher",
                "aggregate": "aggregate"
            }
        )
    
    builder.add_edge("aggregate", END)
    
    return builder.compile()


# ============================================
# 7. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 7.3：Supervisor多智能体")
    print("=" * 60)
    
    graph = build_supervisor_graph()
    
    print("\n执行请求：")
    print("-" * 60)
    
    result = graph.invoke({
        "user_request": "帮我研究一下AI发展趋势",
        "tasks": [],
        "current_task": "",
        "worker_results": [],
        "final_response": ""
    })
    
    print("-" * 60)
    print("\n最终响应：")
    print(result["final_response"])
    
    print("\n" + "=" * 60)
    print("Supervisor模式要点：")
    print("-" * 60)
    print("1. Supervisor负责任务分解和协调")
    print("2. 工作节点各司其职")
    print("3. 使用条件边路由任务")
    print("4. 最后聚合所有结果")
    print("=" * 60)


if __name__ == "__main__":
    main()
