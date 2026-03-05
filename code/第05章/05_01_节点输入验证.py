"""
练习 5.1：节点输入验证
问题描述：为 planning_node 添加输入验证，确保 user_request 不为空。

学习目标：
- 实现节点输入验证
- 处理验证失败的情况
- 提供友好的错误信息
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END


# ============================================
# 1. 定义状态
# ============================================

class PlanningState(TypedDict):
    """规划状态"""
    user_request: Optional[str]  # 用户请求
    plan: Optional[str]          # 生成的计划
    error: Optional[str]         # 错误信息


# ============================================
# 2. 验证装饰器
# ============================================

def validate_input(**validators):
    """
    输入验证装饰器
    
    Args:
        validators: 字段名 -> 验证函数的映射
    
    Example:
        @validate_input(user_request=lambda x: x is not None and len(x) > 0)
        def my_node(state):
            ...
    """
    def decorator(func):
        def wrapper(state):
            # 执行验证
            for field, validator in validators.items():
                value = state.get(field)
                is_valid, error_msg = validator(value)
                
                if not is_valid:
                    # 验证失败，返回错误
                    return {"error": error_msg}
            
            # 验证通过，执行节点逻辑
            return func(state)
        
        return wrapper
    return decorator


# ============================================
# 3. 验证函数
# ============================================

def validate_not_empty(value) -> tuple[bool, str]:
    """验证非空"""
    if value is None:
        return False, "值不能为None"
    if isinstance(value, str) and len(value.strip()) == 0:
        return False, "字符串不能为空"
    return True, ""


def validate_min_length(min_len: int):
    """验证最小长度"""
    def validator(value) -> tuple[bool, str]:
        if value is None:
            return False, f"值不能为None，最小长度{min_len}"
        if len(str(value)) < min_len:
            return False, f"长度不能小于{min_len}"
        return True, ""
    return validator


def validate_pattern(pattern: str):
    """验证正则模式"""
    import re
    compiled = re.compile(pattern)
    
    def validator(value) -> tuple[bool, str]:
        if not value:
            return False, "值不能为空"
        if not compiled.match(str(value)):
            return False, f"格式不正确，需要匹配 {pattern}"
        return True, ""
    
    return validator


# ============================================
# 4. 带验证的节点
# ============================================

@validate_input(user_request=validate_not_empty)
def planning_node(state: PlanningState) -> dict:
    """
    规划节点：根据用户请求生成计划
    
    验证：user_request 不能为空
    """
    user_request = state["user_request"]
    
    # 生成计划（实际应调用LLM）
    plan = f"执行计划：\n1. 分析请求: {user_request}\n2. 制定方案\n3. 执行"
    
    return {"plan": plan, "error": None}


def error_handler_node(state: PlanningState) -> dict:
    """错误处理节点"""
    print(f"  错误: {state['error']}")
    return {}


# ============================================
# 5. 构建图
# ============================================

def build_graph():
    """构建带验证的图"""
    builder = StateGraph(PlanningState)
    
    builder.add_node("planning", planning_node)
    builder.add_node("error_handler", error_handler_node)
    
    builder.set_entry_point("planning")
    
    # 条件边：根据是否有错误决定下一步
    def route(state):
        if state.get("error"):
            return "error"
        return "success"
    
    builder.add_conditional_edges(
        "planning",
        route,
        {"error": "error_handler", "success": END}
    )
    builder.add_edge("error_handler", END)
    
    return builder.compile()


# ============================================
# 6. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 5.1：节点输入验证")
    print("=" * 60)
    
    graph = build_graph()
    
    # 测试1：正常输入
    print("\n测试1：正常输入")
    print("-" * 60)
    result = graph.invoke({"user_request": "帮我写一个Python脚本", "plan": None, "error": None})
    print(f"结果: {result}")
    
    # 测试2：空输入
    print("\n测试2：空输入")
    print("-" * 60)
    result = graph.invoke({"user_request": "", "plan": None, "error": None})
    print(f"结果: {result}")
    
    # 测试3：None输入
    print("\n测试3：None输入")
    print("-" * 60)
    result = graph.invoke({"user_request": None, "plan": None, "error": None})
    print(f"结果: {result}")
    
    print("\n" + "=" * 60)
    print("验证要点：")
    print("-" * 60)
    print("1. 使用装饰器分离验证逻辑")
    print("2. 验证失败返回错误信息")
    print("3. 提供友好的错误提示")
    print("=" * 60)


if __name__ == "__main__":
    main()
