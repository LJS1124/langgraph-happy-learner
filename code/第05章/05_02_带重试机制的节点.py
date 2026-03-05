"""
练习 5.2：带重试机制的节点
问题描述：实现一个带重试机制的 execution_node，当某个任务失败时自动重试最多 3 次。

学习目标：
- 实现自动重试机制
- 处理不同类型的错误
- 控制重试次数和间隔
"""

from typing import TypedDict, Optional, Callable, Any
from langgraph.graph import StateGraph, END
import time
import random


# ============================================
# 1. 定义状态
# ============================================

class ExecutionState(TypedDict):
    """执行状态"""
    task: str                    # 任务描述
    result: Optional[str]        # 执行结果
    error: Optional[str]         # 错误信息
    retry_count: int             # 重试次数
    max_retries: int             # 最大重试次数
    success: bool                # 是否成功


# ============================================
# 2. 重试装饰器
# ============================================

def with_retry(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟（秒）
        backoff: 延迟增长因子
        exceptions: 需要重试的异常类型
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(state) -> dict:
            retry_count = state.get("retry_count", 0)
            current_delay = delay * (backoff ** retry_count)
            
            while retry_count <= max_retries:
                try:
                    # 尝试执行
                    result = func(state)
                    return {**result, "success": True, "retry_count": retry_count}
                
                except exceptions as e:
                    retry_count += 1
                    
                    if retry_count > max_retries:
                        # 重试次数用尽
                        return {
                            "error": f"重试{max_retries}次后仍失败: {str(e)}",
                            "success": False,
                            "retry_count": retry_count - 1
                        }
                    
                    # 等待后重试
                    print(f"    第{retry_count}次重试，等待{current_delay:.1f}秒...")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            return {"error": "未知错误", "success": False}
        
        return wrapper
    return decorator


# ============================================
# 3. 模拟任务执行
# ============================================

@with_retry(max_retries=3, delay=0.5, backoff=2.0)
def execution_node(state: ExecutionState) -> dict:
    """
    执行节点：执行任务（模拟可能失败）
    """
    task = state["task"]
    print(f"  执行任务: {task}")
    
    # 模拟随机失败（70%概率失败）
    if random.random() < 0.7:
        raise ConnectionError("网络连接失败")
    
    # 成功
    return {"result": f"任务 '{task}' 执行成功"}


# ============================================
# 4. 简化版重试节点（不使用装饰器）
# ============================================

def execution_node_with_retry(state: ExecutionState) -> dict:
    """
    带重试的执行节点（简化版）
    """
    task = state["task"]
    max_retries = state.get("max_retries", 3)
    retry_count = state.get("retry_count", 0)
    
    while retry_count <= max_retries:
        try:
            print(f"  执行任务: {task} (尝试 {retry_count + 1}/{max_retries + 1})")
            
            # 模拟执行
            if random.random() < 0.5:  # 50%概率失败
                raise ValueError("模拟执行失败")
            
            # 成功
            return {
                "result": f"任务 '{task}' 执行成功",
                "success": True,
                "retry_count": retry_count
            }
        
        except Exception as e:
            retry_count += 1
            
            if retry_count > max_retries:
                return {
                    "error": f"重试{max_retries}次后失败: {e}",
                    "success": False,
                    "retry_count": retry_count - 1
                }
            
            # 等待
            time.sleep(0.5)
    
    return {"error": "未知错误", "success": False}


# ============================================
# 5. 构建图
# ============================================

def build_graph():
    """构建图"""
    builder = StateGraph(ExecutionState)
    
    builder.add_node("execute", execution_node_with_retry)
    builder.set_entry_point("execute")
    builder.add_edge("execute", END)
    
    return builder.compile()


# ============================================
# 6. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 5.2：带重试机制的节点")
    print("=" * 60)
    
    graph = build_graph()
    
    # 执行多次测试
    for i in range(3):
        print(f"\n测试 {i + 1}:")
        print("-" * 60)
        
        result = graph.invoke({
            "task": f"任务{i + 1}",
            "result": None,
            "error": None,
            "retry_count": 0,
            "max_retries": 3,
            "success": False
        })
        
        print(f"\n结果:")
        print(f"  成功: {result['success']}")
        print(f"  重试次数: {result['retry_count']}")
        if result['success']:
            print(f"  结果: {result['result']}")
        else:
            print(f"  错误: {result['error']}")
    
    print("\n" + "=" * 60)
    print("重试机制要点：")
    print("-" * 60)
    print("1. 设置最大重试次数")
    print("2. 使用指数退避增加延迟")
    print("3. 只对可恢复错误重试")
    print("4. 记录重试次数和结果")
    print("=" * 60)


if __name__ == "__main__":
    main()
