"""
练习 8.1：天气查询意图
问题描述：添加一个新的意图类型"weather"，用于处理天气查询请求。

学习目标：
- 扩展意图识别
- 实现天气查询功能
- 集成外部API
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
    entities: dict
    response: str


# ============================================
# 2. 意图识别节点
# ============================================

def intent_recognition(state: ChatState) -> dict:
    """意图识别"""
    last_message = state["messages"][-1] if state["messages"] else ""
    
    entities = {}
    
    # 意图识别（简化版）
    if "天气" in last_message:
        intent = "weather"
        # 提取城市
        for city in ["北京", "上海", "广州", "深圳", "杭州"]:
            if city in last_message:
                entities["city"] = city
                break
    elif "订单" in last_message:
        intent = "order"
    elif "产品" in last_message:
        intent = "product"
    else:
        intent = "general"
    
    print(f"  意图: {intent}, 实体: {entities}")
    return {"intent": intent, "entities": entities}


# ============================================
# 3. 天气查询节点
# ============================================

def weather_node(state: ChatState) -> dict:
    """天气查询节点"""
    city = state["entities"].get("city", "北京")
    
    # 模拟天气API调用
    weather_data = {
        "北京": {"temp": "25°C", "weather": "晴"},
        "上海": {"temp": "28°C", "weather": "多云"},
        "广州": {"temp": "32°C", "weather": "晴"},
        "深圳": {"temp": "30°C", "weather": "雷阵雨"},
        "杭州": {"temp": "27°C", "weather": "阴"},
    }
    
    data = weather_data.get(city, {"temp": "未知", "weather": "未知"})
    
    response = f"{city}今天天气{data['weather']}，气温{data['temp']}"
    
    print(f"  天气查询结果: {response}")
    
    return {
        "response": response,
        "messages": [f"助手: {response}"]
    }


def order_node(state: ChatState) -> dict:
    """订单查询节点"""
    response = "您的订单正在处理中"
    return {"response": response, "messages": [f"助手: {response}"]}


def product_node(state: ChatState) -> dict:
    """产品查询节点"""
    response = "我们有多种产品可供选择"
    return {"response": response, "messages": [f"助手: {response}"]}

def general_node(state: ChatState) -> dict:
    """通用回复节点"""
    response = "我可以帮您查询天气、订单和产品信息"
    return {"response": response, "messages": [f"助手: {response}"]}


# ============================================
# 4. 路由函数
# ============================================

def route_by_intent(state: ChatState) -> Literal["weather", "order", "product", "general"]:
    return state["intent"]


# ============================================
# 5. 构建图
# ============================================

def build_graph():
    """构建对话图"""
    builder = StateGraph(ChatState)
    
    builder.add_node("intent", intent_recognition)
    builder.add_node("weather", weather_node)
    builder.add_node("order", order_node)
    builder.add_node("product", product_node)
    builder.add_node("general", general_node)
    
    builder.set_entry_point("intent")
    
    builder.add_conditional_edges(
        "intent",
        route_by_intent,
        {
            "weather": "weather",
            "order": "order",
            "product": "product",
            "general": "general"
        }
    )
    
    for node in ["weather", "order", "product", "general"]:
        builder.add_edge(node, END)
    
    return builder.compile()


# ============================================
# 6. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 8.1：天气查询意图")
    print("=" * 60)
    
    graph = build_graph()
    
    test_cases = [
        "北京今天天气怎么样",
        "上海天气如何",
        "广州的天气",
        "我的订单状态",
        "你好"
    ]
    
    for msg in test_cases:
        print(f"\n用户: {msg}")
        print("-" * 40)
        
        result = graph.invoke({
            "messages": [f"用户: {msg}"],
            "intent": "",
            "entities": {},
            "response": ""
        })
        
        print(f"响应: {result['response']}")
    
    print("\n" + "=" * 60)
    print("天气查询要点：")
    print("-" * 60)
    print("1. 识别天气相关意图")
    print("2. 提取城市等实体")
    print("3. 调用天气API获取数据")
    print("4. 格式化响应返回用户")
    print("=" * 60)


if __name__ == "__main__":
    main()
