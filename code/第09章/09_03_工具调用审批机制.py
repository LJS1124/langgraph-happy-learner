"""
练习 9.3：工具调用审批机制
问题描述：设计一个工具调用审批机制，高风险工具调用需要用户确认后才能执行。

学习目标：
- 实现工具风险评估
- 添加审批流程
- 处理用户确认
"""

from typing import TypedDict, Annotated, List, Literal
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from operator import add


# ============================================
# 1. 定义工具（带风险等级）
# ============================================

@tool
def get_user_info(user_id: str) -> str:
    """获取用户信息（低风险）"""
    return f"用户{user_id}的信息: 张三, VIP会员"

@tool  
def send_email(to: str, subject: str, body: str) -> str:
    """发送邮件（中风险）"""
    return f"邮件已发送至 {to}"

@tool
def delete_account(user_id: str) -> str:
    """删除账户（高风险）"""
    return f"账户 {user_id} 已删除"

@tool
def transfer_money(from_account: str, to_account: str, amount: float) -> str:
    """转账（高风险）"""
    return f"已从{from_account}转账{amount}元至{to_account}"


# 工具风险等级
TOOL_RISK_LEVELS = {
    "get_user_info": "low",
    "send_email": "medium",
    "delete_account": "high",
    "transfer_money": "high",
}


# ============================================
# 2. 定义状态
# ============================================

class ApprovalState(TypedDict):
    """审批状态"""
    messages: Annotated[List[str], add]
    tool_name: str
    tool_args: dict
    risk_level: str
    needs_approval: bool
    approved: bool
    result: str


# ============================================
# 3. 节点定义
# ============================================

def analyze_tool_call(state: ApprovalState) -> dict:
    """分析工具调用风险"""
    tool_name = state["tool_name"]
    
    risk = TOOL_RISK_LEVELS.get(tool_name, "medium")
    needs_approval = risk in ["medium", "high"]
    
    print(f"  工具: {tool_name}")
    print(f"  风险等级: {risk}")
    print(f"  需要审批: {needs_approval}")
    
    return {
        "risk_level": risk,
        "needs_approval": needs_approval
    }


def request_approval(state: ApprovalState) -> dict:
    """请求审批"""
    tool_name = state["tool_name"]
    args = state["tool_args"]
    
    message = f"⚠️ 需要确认: 执行 {tool_name}({args})？"
    print(f"\n{message}")
    
    # 模拟用户确认（实际应等待用户输入）
    # 这里自动批准
    approved = True
    print(f"  用户确认: {'批准' if approved else '拒绝'}")
    
    return {
        "approved": approved,
        "messages": [message, f"用户: {'批准' if approved else '拒绝'}"]
    }


def execute_tool(state: ApprovalState) -> dict:
    """执行工具"""
    tool_name = state["tool_name"]
    args = state["tool_args"]
    
    print(f"  执行工具: {tool_name}")
    
    # 执行对应工具
    tools = {
        "get_user_info": get_user_info,
        "send_email": send_email,
        "delete_account": delete_account,
        "transfer_money": transfer_money,
    }
    
    if tool_name in tools:
        result = tools[tool_name].invoke(args)
    else:
        result = f"未知工具: {tool_name}"
    
    print(f"  结果: {result}")
    
    return {"result": result}


def reject_tool(state: ApprovalState) -> dict:
    """拒绝执行"""
    return {"result": "操作被用户拒绝"}


# ============================================
# 4. 路由函数
# ============================================

def route_by_approval(state: ApprovalState) -> Literal["request", "execute", "reject"]:
    """根据审批需求路由"""
    if not state["needs_approval"]:
        return "execute"
    elif state.get("approved"):
        return "execute"
    else:
        return "reject"


# ============================================
# 5. 构建图
# ============================================

def build_graph():
    """构建审批流程图"""
    builder = StateGraph(ApprovalState)
    
    builder.add_node("analyze", analyze_tool_call)
    builder.add_node("request", request_approval)
    builder.add_node("execute", execute_tool)
    builder.add_node("reject", reject_tool)
    
    builder.set_entry_point("analyze")
    
    def after_analyze(state):
        if state["needs_approval"]:
            return "request"
        return "execute"
    
    builder.add_conditional_edges(
        "analyze",
        after_analyze,
        {"request": "request", "execute": "execute"}
    )
    
    builder.add_conditional_edges(
        "request",
        lambda s: "execute" if s["approved"] else "reject",
        {"execute": "execute", "reject": "reject"}
    )
    
    builder.add_edge("execute", END)
    builder.add_edge("reject", END)
    
    return builder.compile()


# ============================================
# 6. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 9.3：工具调用审批机制")
    print("=" * 60)
    
    graph = build_graph()
    
    test_cases = [
        ("get_user_info", {"user_id": "U001"}, "低风险-无需审批"),
        ("send_email", {"to": "test@example.com", "subject": "测试", "body": "内容"}, "中风险-需审批"),
        ("delete_account", {"user_id": "U001"}, "高风险-需审批"),
    ]
    
    for tool_name, args, desc in test_cases:
        print(f"\n测试: {desc}")
        print("-" * 40)
        
        result = graph.invoke({
            "messages": [],
            "tool_name": tool_name,
            "tool_args": args,
            "risk_level": "",
            "needs_approval": False,
            "approved": False,
            "result": ""
        })
        
        print(f"\n最终结果: {result['result']}")
    
    print("\n" + "=" * 60)
    print("审批机制要点：")
    print("-" * 60)
    print("1. 定义工具风险等级")
    print("2. 高风险工具需要审批")
    print("3. 等待用户确认")
    print("4. 记录审批日志")
    print("=" * 60)


if __name__ == "__main__":
    main()
