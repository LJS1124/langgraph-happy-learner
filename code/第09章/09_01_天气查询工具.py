"""
练习 9.1：天气查询工具
问题描述：为工具调用智能体添加一个新的工具，用于查询天气信息。

学习目标：
- 定义自定义工具
- 实现工具调用逻辑
- 处理工具返回结果
"""

from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.tools import tool
from operator import add


# ============================================
# 1. 定义天气工具
# ============================================

@tool
def get_weather(city: str) -> str:
    """
    查询指定城市的天气信息
    
    Args:
        city: 城市名称，如"北京"、"上海"
    
    Returns:
        天气信息字符串
    """
    # 模拟天气数据
    weather_data = {
        "北京": "晴天，25°C，空气质量良好",
        "上海": "多云，28°C，有轻微雾霾",
        "广州": "雷阵雨，30°C，湿度较高",
        "深圳": "晴间多云，29°C",
        "杭州": "阴天，26°C",
    }
    
    result = weather_data.get(city, f"未找到城市 {city} 的天气信息")
    print(f"  [工具调用] get_weather(city='{city}')")
    print(f"  [工具返回] {result}")
    
    return result


@tool
def get_weather_forecast(city: str, days: int = 3) -> str:
    """
    查询未来几天的天气预报
    
    Args:
        city: 城市名称
        days: 预报天数，默认3天
    
    Returns:
        天气预报信息
    """
    forecast = []
    for i in range(1, days + 1):
        forecast.append(f"第{i}天: 晴转多云, 25-30°C")
    
    result = f"{city}未来{days}天预报: " + "; ".join(forecast)
    print(f"  [工具调用] get_weather_forecast(city='{city}', days={days})")
    return result


# ============================================
# 2. 定义状态
# ============================================

class ToolState(TypedDict):
    """工具调用状态"""
    messages: Annotated[List[str], add]
    tool_calls: List[dict]
    tool_results: Annotated[List[str], add]


# ============================================
# 3. 工具调用节点
# ============================================

def tool_router(state: ToolState) -> dict:
    """工具路由节点"""
    last_message = state["messages"][-1] if state["messages"] else ""
    
    tool_calls = []
    
    # 简单的工具匹配逻辑
    if "天气" in last_message:
        # 提取城市
        city = "北京"
        for c in ["北京", "上海", "广州", "深圳", "杭州"]:
            if c in last_message:
                city = c
                break
        
        if "预报" in last_message:
            tool_calls.append({"tool": "get_weather_forecast", "args": {"city": city, "days": 3}})
        else:
            tool_calls.append({"tool": "get_weather", "args": {"city": city}})
    
    print(f"  工具调用: {tool_calls}")
    return {"tool_calls": tool_calls}


def execute_tools(state: ToolState) -> dict:
    """执行工具节点"""
    results = []
    
    for call in state["tool_calls"]:
        tool_name = call["tool"]
        args = call["args"]
        
        if tool_name == "get_weather":
            result = get_weather.invoke(args)
        elif tool_name == "get_weather_forecast":
            result = get_weather_forecast.invoke(args)
        else:
            result = f"未知工具: {tool_name}"
        
        results.append(result)
    
    return {"tool_results": results, "tool_calls": []}


def generate_response(state: ToolState) -> dict:
    """生成响应节点"""
    results = state["tool_results"]
    
    if results:
        response = "\n".join(results)
    else:
        response = "我无法处理这个请求"
    
    return {
        "messages": [f"助手: {response}"],
        "tool_results": []
    }


# ============================================
# 4. 构建图
# ============================================

def build_graph():
    """构建工具调用图"""
    builder = StateGraph(ToolState)
    
    builder.add_node("router", tool_router)
    builder.add_node("execute", execute_tools)
    builder.add_node("respond", generate_response)
    
    builder.set_entry_point("router")
    
    def has_tool_calls(state):
        return "execute" if state["tool_calls"] else "respond"
    
    builder.add_conditional_edges(
        "router",
        has_tool_calls,
        {"execute": "execute", "respond": "respond"}
    )
    
    builder.add_edge("execute", "respond")
    builder.add_edge("respond", END)
    
    return builder.compile()


# ============================================
# 5. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 9.1：天气查询工具")
    print("=" * 60)
    
    graph = build_graph()
    
    test_cases = [
        "北京今天天气怎么样",
        "上海天气如何",
        "广州未来三天天气预报"
    ]
    
    for msg in test_cases:
        print(f"\n用户: {msg}")
        print("-" * 40)
        
        result = graph.invoke({
            "messages": [f"用户: {msg}"],
            "tool_calls": [],
            "tool_results": []
        })
        
        # 打印最后一条助手消息
        for m in reversed(result["messages"]):
            if m.startswith("助手:"):
                print(m)
                break
    
    print("\n" + "=" * 60)
    print("工具定义要点：")
    print("-" * 60)
    print("1. 使用@tool装饰器定义工具")
    print("2. 编写清晰的docstring")
    print("3. 定义参数类型")
    print("4. 返回字符串结果")
    print("=" * 60)


if __name__ == "__main__":
    main()
