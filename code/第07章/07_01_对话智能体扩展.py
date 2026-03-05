"""
练习 7.1：对话智能体扩展
问题描述：添加一个新的意图类型和对应的处理节点。

学习目标：
- 扩展意图识别
- 添加新的处理节点
- 更新路由逻辑
"""

from typing import TypedDict, Literal, Annotated, List
from langgraph.graph import StateGraph, END
from operator import add


# ============================================
# 1. 定义状态
# ============================================

class ChatState(TypedDict):
    """对话状态"""
    messages: Annotated[List[str], add]
    intent: str
    response: str


# ============================================
# 2. 意图识别节点
# ============================================

def intent_recognition(state: ChatState) -> dict:
    """意图识别节点"""
    last_message = state["messages"][-1] if state["messages"] else ""
    
    # 简单的意图识别（实际应使用LLM）
    if "天气" in last_message:
        intent = "weather"
    elif "订单" in last_message:
        intent = "order"
    elif "产品" in last_message or "商品" in last_message:
        intent = "product"
    elif "帮助" in last_message or "help" in last_message.lower():
        intent = "help"  # 新增意图
    else:
        intent = "general"
    
    print(f"  识别意图: {intent}")
    return {"intent": intent}


# ============================================
# 3. 处理节点
# ============================================

def weather_node(state: ChatState) -> dict:
    """天气查询节点"""
    return {
        "response": "今天天气晴朗，温度25°C",
        "messages": ["助手: 今天天气晴朗，温度25°C"]
    }


def order_node(state: ChatState) -> dict:
    """订单查询节点"""
    return {
        "response": "您的订单正在配送中",
        "messages": ["助手: 您的订单正在配送中"]
    }


def product_node(state: ChatState) -> dict:
    """产品查询节点"""
    return {
        "response": "我们有多款产品可供选择",
        "messages": ["助手: 我们有多款产品可供选择"]
    }


def help_node(state: ChatState) -> dict:
    """帮助节点（新增）"""
    help_text = """
我可以帮您：
1. 查询天气 - 说"今天天气怎么样"
2. 查询订单 - 说"我的订单状态"
3. 查询产品 - 说"有什么产品"
4. 获取帮助 - 说"帮助"
"""
    return {
        "response": help_text,
        "messages": [f"助手:{help_text}"]
    }


def general_node(state: ChatState) -> dict:
    """通用回复节点"""
    return {
        "response": "我不太理解您的问题，请说'帮助'获取更多信息",
        "messages": ["助手: 我不太理解您的问题，请说'帮助'获取更多信息"]
    }


# ============================================
# 4. 路由函数
# ============================================

def route_by_intent(state: ChatState) -> Literal["weather", "order", "product", "help", "general"]:
    """根据意图路由"""
    return state["intent"]


# ============================================
# 5. 构建图
# ============================================

def build_chat_graph():
    """构建对话图"""
    builder = StateGraph(ChatState)
    
    # 添加节点
    builder.add_node("intent", intent_recognition)
    builder.add_node("weather", weather_node)
    builder.add_node("order", order_node)
    builder.add_node("product", product_node)
    builder.add_node("help", help_node)  # 新增
    builder.add_node("general", general_node)
    
    # 设置入口
    builder.set_entry_point("intent")
    
    # 条件路由
    builder.add_conditional_edges(
        "intent",
        route_by_intent,
        {
            "weather": "weather",
            "order": "order",
            "product": "product",
            "help": "help",  # 新增
            "general": "general"
        }
    )
    
    # 所有处理节点指向END
    for node in ["weather", "order", "product", "help", "general"]:
        builder.add_edge(node, END)
    
    return builder.compile()


# ============================================
# 6. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 7.1：对话智能体扩展")
    print("=" * 60)
    
    graph = build_chat_graph()
    
    # 测试不同意图
    test_messages = [
        "今天天气怎么样",
        "我的订单状态",
        "有什么产品",
        "帮助",  # 新增意图测试
        "随便说点什么"
    ]
    
    for msg in test_messages:
        print(f"\n用户: {msg}")
        print("-" * 60)
        
        result = graph.invoke({
            "messages": [f"用户: {msg}"],
            "intent": "",
            "response": ""
        })
        
        print(f"意图: {result['intent']}")
        print(f"响应: {result['response'][:50]}...")
    
    print("\n" + "=" * 60)
    print("扩展要点：")
    print("-" * 60)
    print("1. 添加新的意图识别规则")
    print("2. 创建新的处理节点")
    print("3. 更新路由映射")
    print("4. 测试新功能")
    print("=" * 60)


if __name__ == "__main__":
    main()
