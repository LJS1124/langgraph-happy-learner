"""
练习 8.3：会话重置功能
问题描述：添加一个"重置"功能，允许用户清除当前会话的历史记录。

学习目标：
- 实现会话重置
- 清除状态数据
- 提供重新开始的能力
"""

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from operator import add


# ============================================
# 1. 定义状态
# ============================================

class SessionState(TypedDict):
    """会话状态"""
    messages: Annotated[List[str], add]
    session_active: bool
    message_count: int


# ============================================
# 2. 定义节点
# ============================================

def process_message(state: SessionState) -> dict:
    """处理消息节点"""
    last_message = state["messages"][-1] if state["messages"] else ""
    
    # 检查是否是重置命令
    if "重置" in last_message or "reset" in last_message.lower():
        print("  检测到重置命令")
        return {
            "messages": ["系统: 会话已重置"],
            "session_active": True,
            "message_count": 0
        }
    
    # 正常对话
    count = state.get("message_count", 0) + 1
    
    # 模拟响应
    if "你好" in last_message:
        response = "你好！有什么可以帮助你的？"
    elif "历史" in last_message:
        history = state["messages"][:-1]
        if history:
            response = f"历史消息({len(history)}条): " + " | ".join(history[-3:])
        else:
            response = "暂无历史消息"
    else:
        response = f"收到消息 #{count}"
    
    print(f"  响应: {response}")
    
    return {
        "messages": [f"助手: {response}"],
        "message_count": count
    }


# ============================================
# 3. 构建图
# ============================================

def build_graph():
    """构建图"""
    builder = StateGraph(SessionState)
    
    builder.add_node("process", process_message)
    builder.set_entry_point("process")
    builder.add_edge("process", END)
    
    # 添加检查点支持
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)


# ============================================
# 4. 会话管理器
# ============================================

class ChatSession:
    """聊天会话"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.graph = build_graph()
        self.config = {"configurable": {"thread_id": session_id}}
        
        # 初始化状态
        self.graph.invoke(
            {"messages": [], "session_active": True, "message_count": 0},
            self.config
        )
    
    def send(self, message: str) -> str:
        """发送消息"""
        result = self.graph.invoke(
            {"messages": [f"用户: {message}"]},
            self.config
        )
        
        # 获取最后一条助手消息
        for msg in reversed(result["messages"]):
            if msg.startswith("助手:") or msg.startswith("系统:"):
                return msg.split(":", 1)[1].strip()
        
        return ""
    
    def reset(self):
        """重置会话"""
        # 发送重置命令
        return self.send("重置")
    
    def get_history(self) -> List[str]:
        """获取历史"""
        state = self.graph.get_state(self.config)
        return state.values.get("messages", [])


# ============================================
# 5. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 8.3：会话重置功能")
    print("=" * 60)
    
    session = ChatSession("test_session")
    
    # 正常对话
    print("\n正常对话：")
    print("-" * 40)
    
    messages = ["你好", "今天天气怎么样", "查看历史"]
    for msg in messages:
        print(f"用户: {msg}")
        response = session.send(msg)
        print(f"响应: {response}")
        print()
    
    # 查看历史
    print("\n当前历史：")
    history = session.get_history()
    for msg in history:
        print(f"  {msg}")
    
    # 重置会话
    print("\n" + "=" * 60)
    print("重置会话...")
    print("-" * 40)
    response = session.reset()
    print(f"响应: {response}")
    
    # 查看重置后的历史
    print("\n重置后历史：")
    history = session.get_history()
    for msg in history:
        print(f"  {msg}")
    
    # 继续对话
    print("\n继续对话：")
    print("-" * 40)
    response = session.send("你好")
    print(f"用户: 你好")
    print(f"响应: {response}")
    
    print("\n" + "=" * 60)
    print("会话重置要点：")
    print("-" * 60)
    print("1. 检测重置命令")
    print("2. 清空消息历史")
    print("3. 重置计数器")
    print("4. 提供友好的提示")
    print("=" * 60)


if __name__ == "__main__":
    main()
