"""
练习 10.3：动态加入智能体
问题描述：设计一个支持"动态加入"的多智能体系统。

学习目标：
- 实现动态智能体注册
- 运行时添加新能力
- 灵活扩展系统
"""

from typing import TypedDict, Annotated, List, Dict, Callable
from langgraph.graph import StateGraph, END
from operator import add


# ============================================
# 1. 定义状态
# ============================================

class AgentInfo(TypedDict):
    """智能体信息"""
    name: str
    capability: str
    handler: str  # 处理函数名


class DynamicState(TypedDict):
    """动态系统状态"""
    task: str
    registered_agents: Dict[str, AgentInfo]
    results: Annotated[List[str], add]
    current_agent: str


# ============================================
# 2. 智能体注册表
# ============================================

class AgentRegistry:
    """智能体注册表"""
    
    def __init__(self):
        self.agents: Dict[str, Callable] = {}
    
    def register(self, name: str, handler: Callable):
        """注册智能体"""
        self.agents[name] = handler
        print(f"  [Registry] 注册智能体: {name}")
    
    def unregister(self, name: str):
        """注销智能体"""
        if name in self.agents:
            del self.agents[name]
            print(f"  [Registry] 注销智能体: {name}")
    
    def get_handler(self, name: str) -> Callable:
        """获取处理函数"""
        return self.agents.get(name)
    
    def list_agents(self) -> List[str]:
        """列出所有智能体"""
        return list(self.agents.keys())


# 全局注册表
registry = AgentRegistry()


# ============================================
# 3. 定义智能体处理函数
# ============================================

def order_handler(state: DynamicState) -> dict:
    """订单处理智能体"""
    print("  [OrderAgent] 处理订单")
    return {"results": ["订单处理完成"]}


def product_handler(state: DynamicState) -> dict:
    """产品处理智能体"""
    print("  [ProductAgent] 处理产品")
    return {"results": ["产品查询完成"]}


def support_handler(state: DynamicState) -> dict:
    """客服处理智能体"""
    print("  [SupportAgent] 处理客服")
    return {"results": ["客服响应完成"]}


# 注册初始智能体
registry.register("order", order_handler)
registry.register("product", product_handler)


# ============================================
# 4. 动态调度节点
# ============================================

def dispatcher(state: DynamicState) -> dict:
    """调度节点"""
    task = state["task"]
    
    # 根据任务选择智能体
    agent_name = None
    
    if "订单" in task:
        agent_name = "order"
    elif "产品" in task:
        agent_name = "product"
    elif "客服" in task or "投诉" in task:
        agent_name = "support"
    
    if agent_name and agent_name in registry.list_agents():
        print(f"  [Dispatcher] 分配给: {agent_name}")
        return {"current_agent": agent_name}
    else:
        print("  [Dispatcher] 无可用智能体")
        return {"current_agent": ""}


def agent_executor(state: DynamicState) -> dict:
    """智能体执行器"""
    agent_name = state["current_agent"]
    
    if not agent_name:
        return {"results": ["无法处理"]}
    
    handler = registry.get_handler(agent_name)
    if handler:
        return handler(state)
    
    return {"results": [f"智能体 {agent_name} 不存在"]}


# ============================================
# 5. 构建图
# ============================================

def build_graph():
    """构建动态图"""
    builder = StateGraph(DynamicState)
    
    builder.add_node("dispatcher", dispatcher)
    builder.add_node("executor", agent_executor)
    
    builder.set_entry_point("dispatcher")
    builder.add_edge("dispatcher", "executor")
    builder.add_edge("executor", END)
    
    return builder.compile()


# ============================================
# 6. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 10.3：动态加入智能体")
    print("=" * 60)
    
    graph = build_graph()
    
    # 测试1：使用已注册的智能体
    print("\n测试1：处理订单（已注册）")
    print("-" * 40)
    result = graph.invoke({
        "task": "查询订单状态",
        "registered_agents": {},
        "results": [],
        "current_agent": ""
    })
    print(f"结果: {result['results']}")
    
    # 测试2：处理客服（未注册）
    print("\n测试2：处理客服（未注册）")
    print("-" * 40)
    result = graph.invoke({
        "task": "转人工客服",
        "registered_agents": {},
        "results": [],
        "current_agent": ""
    })
    print(f"结果: {result['results']}")
    
    # 动态注册新智能体
    print("\n" + "=" * 60)
    print("动态注册客服智能体...")
    print("-" * 40)
    registry.register("support", support_handler)
    
    # 测试3：再次处理客服
    print("\n测试3：处理客服（已注册）")
    print("-" * 40)
    result = graph.invoke({
        "task": "转人工客服",
        "registered_agents": {},
        "results": [],
        "current_agent": ""
    })
    print(f"结果: {result['results']}")
    
    print("\n" + "=" * 60)
    print("当前注册的智能体：")
    for name in registry.list_agents():
        print(f"  - {name}")
    
    print("\n" + "=" * 60)
    print("动态注册要点：")
    print("-" * 60)
    print("1. 使用注册表管理智能体")
    print("2. 运行时注册/注销")
    print("3. 调度器动态选择")
    print("4. 支持热插拔")
    print("=" * 60)


if __name__ == "__main__":
    main()
