"""
练习 10.2：消息传递多智能体
问题描述：实现一个基于消息传递的多智能体系统。

学习目标：
- 实现智能体间消息传递
- 设计消息格式
- 处理异步通信
"""

from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from operator import add
from datetime import datetime


# ============================================
# 1. 定义消息格式
# ============================================

class Message(TypedDict):
    """消息结构"""
    sender: str
    receiver: str
    content: str
    timestamp: str
    msg_type: str  # "request", "response", "notification"


def create_message(sender: str, receiver: str, content: str, msg_type: str = "request") -> Message:
    """创建消息"""
    return Message(
        sender=sender,
        receiver=receiver,
        content=content,
        timestamp=datetime.now().isoformat(),
        msg_type=msg_type
    )


# ============================================
# 2. 定义状态
# ============================================

class MessagingState(TypedDict):
    """消息传递状态"""
    messages: Annotated[List[Message], add]
    pending_requests: List[Message]
    processed: List[str]


# ============================================
# 3. 定义智能体
# ============================================

def coordinator_agent(state: MessagingState) -> dict:
    """协调智能体"""
    print("  [Coordinator] 检查消息")
    
    # 处理待处理请求
    pending = state.get("pending_requests", [])
    new_messages = []
    
    if not pending:
        # 发起新任务
        msg = create_message(
            "coordinator",
            "worker_a",
            "请处理任务A",
            "request"
        )
        new_messages.append(msg)
        print(f"    发送消息给 WorkerA: {msg['content']}")
    
    return {"messages": new_messages}


def worker_a_agent(state: MessagingState) -> dict:
    """工作智能体A"""
    messages = state["messages"]
    new_messages = []
    
    for msg in messages:
        if msg["receiver"] == "worker_a" and msg["msg_type"] == "request":
            print(f"  [WorkerA] 收到请求: {msg['content']}")
            
            # 处理并发送响应
            response = create_message(
                "worker_a",
                "coordinator",
                "任务A已完成",
                "response"
            )
            new_messages.append(response)
            print(f"    发送响应: {response['content']}")
    
    return {"messages": new_messages}


def worker_b_agent(state: MessagingState) -> dict:
    """工作智能体B"""
    messages = state["messages"]
    new_messages = []
    
    for msg in messages:
        if msg["receiver"] == "worker_b" and msg["msg_type"] == "request":
            print(f"  [WorkerB] 收到请求: {msg['content']}")
            
            response = create_message(
                "worker_b",
                "coordinator",
                "任务B已完成",
                "response"
            )
            new_messages.append(response)
    
    return {"messages": new_messages}


def message_processor(state: MessagingState) -> dict:
    """消息处理器"""
    messages = state["messages"]
    processed = []
    
    for msg in messages:
        if msg["msg_type"] == "response":
            processed.append(f"{msg['sender']}: {msg['content']}")
            print(f"  [Processor] 处理响应: {msg['sender']} -> {msg['content']}")
    
    return {"processed": processed}


# ============================================
# 4. 构建图
# ============================================

def build_graph():
    """构建消息传递图"""
    builder = StateGraph(MessagingState)
    
    builder.add_node("coordinator", coordinator_agent)
    builder.add_node("worker_a", worker_a_agent)
    builder.add_node("worker_b", worker_b_agent)
    builder.add_node("processor", message_processor)
    
    builder.set_entry_point("coordinator")
    
    # 简单的串行流程
    builder.add_edge("coordinator", "worker_a")
    builder.add_edge("worker_a", "worker_b")
    builder.add_edge("worker_b", "processor")
    builder.add_edge("processor", END)
    
    return builder.compile()


# ============================================
# 5. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 10.2：消息传递多智能体")
    print("=" * 60)
    
    graph = build_graph()
    
    result = graph.invoke({
        "messages": [],
        "pending_requests": [],
        "processed": []
    })
    
    print("\n" + "=" * 60)
    print("处理结果：")
    for p in result["processed"]:
        print(f"  - {p}")
    
    print("\n" + "=" * 60)
    print("消息传递要点：")
    print("-" * 60)
    print("1. 定义统一的消息格式")
    print("2. 消息包含发送者、接收者、内容")
    print("3. 支持请求-响应模式")
    print("4. 记录消息历史")
    print("=" * 60)


if __name__ == "__main__":
    main()
