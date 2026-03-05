"""
练习 8.2：上下文记忆
问题描述：实现一个上下文管理功能，记住用户在对话中提到的关键信息。

学习目标：
- 实现上下文记忆
- 提取和存储关键信息
- 在后续对话中使用
"""

from typing import TypedDict, Annotated, List, Optional
from langgraph.graph import StateGraph, END
from operator import add
import re


# ============================================
# 1. 定义状态
# ============================================

class ContextState(TypedDict):
    """带上下文的状态"""
    messages: Annotated[List[str], add]
    # 记忆的关键信息
    user_name: Optional[str]
    user_preference: dict
    mentioned_topics: Annotated[List[str], add]
    response: str


# ============================================
# 2. 信息提取节点
# ============================================

def extract_info(state: ContextState) -> dict:
    """提取关键信息节点"""
    last_message = state["messages"][-1] if state["messages"] else ""
    
    updates = {}
    
    # 提取姓名
    name_patterns = [
        r"我叫(.{2,4})",
        r"我是(.{2,4})",
        r"我的名字是(.{2,4})"
    ]
    for pattern in name_patterns:
        match = re.search(pattern, last_message)
        if match:
            updates["user_name"] = match.group(1)
            print(f"  记住用户姓名: {updates['user_name']}")
            break
    
    # 提取偏好
    if "喜欢" in last_message:
        if "preference" not in state:
            updates["user_preference"] = {}
        # 简单提取
        if "Python" in last_message:
            updates["user_preference"]["language"] = "Python"
            print("  记住用户偏好: Python")
    
    # 提取话题
    topics = []
    for topic in ["AI", "Python", "LangGraph", "机器学习", "深度学习"]:
        if topic in last_message:
            topics.append(topic)
    
    if topics:
        updates["mentioned_topics"] = topics
        print(f"  记住话题: {topics}")
    
    return updates


# ============================================
# 3. 对话节点
# ============================================

def chat_node(state: ContextState) -> dict:
    """对话节点"""
    last_message = state["messages"][-1] if state["messages"] else ""
    name = state.get("user_name")
    preference = state.get("user_preference", {})
    topics = state.get("mentioned_topics", [])
    
    # 根据上下文生成响应
    if name and ("你好" in last_message or "您好" in last_message):
        response = f"你好{name}！很高兴再次见到你！"
    elif "我叫" in last_message or "我是" in last_message:
        if name:
            response = f"好的，我记住了你的名字是{name}！"
        else:
            response = "好的，请问你叫什么名字？"
    elif "我喜欢" in last_message:
        response = f"我记住了你的偏好！你喜欢{preference.get('language', '编程')}"
    elif "我之前说了什么" in last_message or "记得我吗" in last_message:
        context_info = []
        if name:
            context_info.append(f"你叫{name}")
        if preference:
            context_info.append(f"你喜欢{preference}")
        if topics:
            context_info.append(f"我们聊过{', '.join(topics)}")
        
        if context_info:
            response = "我记得：" + "，".join(context_info)
        else:
            response = "我还没有记住你的信息"
    else:
        response = f"收到你的消息：{last_message}"
    
    print(f"  响应: {response}")
    
    return {
        "response": response,
        "messages": [f"助手: {response}"]
    }


# ============================================
# 4. 构建图
# ============================================

def build_graph():
    """构建带上下文记忆的图"""
    builder = StateGraph(ContextState)
    
    builder.add_node("extract", extract_info)
    builder.add_node("chat", chat_node)
    
    builder.set_entry_point("extract")
    builder.add_edge("extract", "chat")
    builder.add_edge("chat", END)
    
    return builder.compile()


# ============================================
# 5. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 8.2：上下文记忆")
    print("=" * 60)
    
    graph = build_graph()
    
    # 模拟多轮对话
    conversation = [
        "你好",
        "我叫小明",
        "我喜欢Python",
        "我们聊聊AI吧",
        "我之前说了什么"
    ]
    
    state = {
        "messages": [],
        "user_name": None,
        "user_preference": {},
        "mentioned_topics": [],
        "response": ""
    }
    
    for msg in conversation:
        print(f"\n用户: {msg}")
        print("-" * 40)
        
        state["messages"].append(f"用户: {msg}")
        state = graph.invoke(state)
    
    print("\n" + "=" * 60)
    print("最终记忆状态：")
    print("-" * 60)
    print(f"  用户姓名: {state.get('user_name')}")
    print(f"  用户偏好: {state.get('user_preference')}")
    print(f"  提到话题: {state.get('mentioned_topics')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
