"""
练习 5.3：并行执行节点
问题描述：设计一个支持并行执行的 execution_node，可以同时执行多个独立的任务。

学习目标：
- 实现并行任务执行
- 使用多线程/多进程
- 合并并行结果
"""

from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import StateGraph, END
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


# ============================================
# 1. 定义状态
# ============================================

def merge_results(left: List, right: List) -> List:
    """合并结果列表"""
    return left + right


class ParallelState(TypedDict):
    """并行执行状态"""
    tasks: List[str]                      # 任务列表
    results: Annotated[List[dict], merge_results]  # 执行结果
    max_workers: int                      # 最大并行数


# ============================================
# 2. 并行执行节点
# ============================================

def execute_single_task(task: str) -> dict:
    """执行单个任务"""
    print(f"    开始执行: {task}")
    start_time = time.time()
    
    # 模拟任务执行
    time.sleep(1)  # 模拟耗时操作
    
    elapsed = time.time() - start_time
    print(f"    完成: {task} (耗时 {elapsed:.1f}s)")
    
    return {
        "task": task,
        "status": "success",
        "elapsed": elapsed,
        "result": f"{task} 的结果"
    }


def parallel_execution_node(state: ParallelState) -> dict:
    """
    并行执行节点
    
    使用线程池并行执行多个任务
    """
    tasks = state["tasks"]
    max_workers = state.get("max_workers", 3)
    
    print(f"  并行执行 {len(tasks)} 个任务 (最大并行数: {max_workers})")
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_task = {
            executor.submit(execute_single_task, task): task
            for task in tasks
        }
        
        # 收集结果
        for future in as_completed(future_to_task):
            result = future.result()
            results.append(result)
    
    return {"results": results}


# ============================================
# 3. 带依赖的并行执行
# ============================================

class Task(TypedDict):
    """任务定义"""
    id: str
    action: str
    dependencies: List[str]  # 依赖的任务ID


def execute_with_dependencies(tasks: List[Task], max_workers: int = 3) -> List[dict]:
    """
    带依赖关系的并行执行
    
    拓扑排序后并行执行
    """
    from collections import defaultdict, deque
    
    # 构建依赖图
    in_degree = defaultdict(int)
    dependents = defaultdict(list)
    task_map = {t["id"]: t for t in tasks}
    
    for task in tasks:
        for dep in task.get("dependencies", []):
            dependents[dep].append(task["id"])
            in_degree[task["id"]] += 1
    
    # 找到没有依赖的任务
    queue = deque([t["id"] for t in tasks if in_degree[t["id"]] == 0])
    
    results = []
    completed = set()
    
    while queue:
        # 当前批次可并行执行的任务
        batch = []
        while queue and len(batch) < max_workers:
            batch.append(queue.popleft())
        
        # 并行执行
        with ThreadPoolExecutor(max_workers=len(batch)) as executor:
            futures = {
                executor.submit(execute_single_task, task_map[tid]["action"]): tid
                for tid in batch
            }
            
            for future in as_completed(futures):
                tid = futures[future]
                result = future.result()
                result["task_id"] = tid
                results.append(result)
                completed.add(tid)
                
                # 更新依赖
                for dependent in dependents[tid]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
    
    return results


# ============================================
# 4. 构建图
# ============================================

def build_graph():
    """构建图"""
    builder = StateGraph(ParallelState)
    
    builder.add_node("parallel_execute", parallel_execution_node)
    builder.set_entry_point("parallel_execute")
    builder.add_edge("parallel_execute", END)
    
    return builder.compile()


# ============================================
# 5. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 5.3：并行执行节点")
    print("=" * 60)
    
    graph = build_graph()
    
    # 测试并行执行
    print("\n测试1：并行执行多个独立任务")
    print("-" * 60)
    
    start_time = time.time()
    
    result = graph.invoke({
        "tasks": ["任务A", "任务B", "任务C", "任务D", "任务E"],
        "results": [],
        "max_workers": 3
    })
    
    total_time = time.time() - start_time
    
    print(f"\n结果:")
    print(f"  完成任务数: {len(result['results'])}")
    print(f"  总耗时: {total_time:.1f}s")
    
    # 测试带依赖的并行执行
    print("\n" + "=" * 60)
    print("测试2：带依赖关系的并行执行")
    print("-" * 60)
    
    tasks_with_deps = [
        Task(id="A", action="初始化", dependencies=[]),
        Task(id="B", action="加载数据", dependencies=["A"]),
        Task(id="C", action="加载配置", dependencies=["A"]),
        Task(id="D", action="处理数据", dependencies=["B", "C"]),
        Task(id="E", action="输出结果", dependencies=["D"]),
    ]
    
    print("\n任务依赖关系:")
    print("  A → B → D → E")
    print("  A → C ↗")
    
    print("\n执行过程:")
    start_time = time.time()
    results = execute_with_dependencies(tasks_with_deps, max_workers=2)
    total_time = time.time() - start_time
    
    print(f"\n结果:")
    for r in results:
        print(f"  {r['task_id']}: {r['task']}")
    print(f"  总耗时: {total_time:.1f}s")
    
    print("\n" + "=" * 60)
    print("并行执行要点：")
    print("-" * 60)
    print("1. 使用ThreadPoolExecutor并行执行")
    print("2. 控制最大并行数避免资源耗尽")
    print("3. 处理依赖关系需要拓扑排序")
    print("4. 合并结果时注意顺序")
    print("=" * 60)


if __name__ == "__main__":
    main()
