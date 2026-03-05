"""
练习 7.2：检查点对话智能体
问题描述：实现一个带检查点的对话智能体，支持多轮对话和会话恢复。

学习目标：
- 使用MemorySaver
- 实现会话持久化
- 支持会话恢复
"""

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from operator import add


# ============================================
# 1. 定义状态
# ============================================

class ConversationState(TypedDict):
    """对话状态"""
    messages: Annotated[List[str], add]
    session_id: str


# ============================================
# 2. 定义节点
# ============================================

def chat_node(state: ConversationState) -> dict:
    """聊天节点"""
    messages = state["messages"]
    last_message = messages[-1] if messages else ""
    
    # 模拟LLM响应
    if "你好" in last_message:
        response = "你好！有什么我可以帮助你的吗？"
    elif "再见" in last_message:
        response = "再见！期待下次聊天。"
    else:
        response = f"我收到了你的消息：{last_message}"
    
    return {"messages": [f"助手: {response}"]}


# ============================================
# 3. 构建带检查点的图
# ============================================

def build_graph_with_checkpoint():
    """构建带检查点的图"""
    builder = StateGraph(ConversationState)
    
    builder.add_node("chat", chat_node)
    builder.set_entry_point("chat")
    builder.add_edge("chat", END)
    
    # 创建检查点存储
    checkpointer = MemorySaver()
    
    return builder.compile(checkpointer=checkpointer)


# ============================================
# 4. 会话管理
# ============================================

class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.graph = build_graph_with_checkpoint()
    
    def chat(self, session_id: str, user_message: str) -> str:
        """发送消息并获取响应"""
        # 创建配置
        config = {"configurable": {"thread_id": session_id}}
        
        # 发送消息
        result = self.graph.invoke(
            {"messages": [f"用户: {user_message}"], "session_id": session_id},
            config=config
        )
        
        # 获取最后一条助手消息
        for msg in reversed(result["messages"]):
            if msg.startswith("助手:"):
                return msg[3:].strip()
        
        return ""
    
    def get_history(self, session_id: str) -> List[str]:
        """获取会话历史"""
        config = {"configurable": {"thread_id": session_id}}
        state = self.graph.get_state(config)
        
        if state and state.values:
            return state.values.get("messages", [])
        return []
    
    def clear_session(self, session_id: str):
        """清除会话"""
        # MemorySaver不支持直接清除，这里用新状态覆盖
        config = {"configurable": {"thread_id": session_id}}
        self.graph.update_state(config, {"messages": [], "session_id": session_id})


# ============================================
# 5. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 7.2：检查点对话智能体")
    print("=" * 60)
    
    manager = SessionManager()
    session_id = "session_001"
    
    # 多轮对话
    print("\n多轮对话测试：")
    print("-" * 60)
    
    messages = ["你好", "今天天气怎么样", "再见"]
    
    for msg in messages:
        print(f"\n用户: {msg}")
        response = manager.chat(session_id, msg)
        print(f"助手: {response}")
    
    # 查看历史
    print("\n" + "-" * 60)
    print("会话历史：")
    history = manager.get_history(session_id)
    for i, msg in enumerate(history, 1):
        print(f"  {i}. {msg}")
    
    # 恢复会话
    print("\n" + "-" * 60)
    print("恢复会话测试：")
    response = manager.chat(session_id, "我们之前聊了什么？")
    print(f"用户: 我们之前聊了什么？")
    print(f"助手: {response}")
    
    print("\n" + "=" * 60)
    print("检查点要点：")
    print("-" * 60)
    print("1. 使用MemorySaver保存状态")
    print("2. 通过thread_id区分会话")
    print("3. 支持会话恢复和历史查询")
    print("4. 生产环境使用数据库存储")
    print("=" * 60)


if __name__ == "__main__":
    main()
