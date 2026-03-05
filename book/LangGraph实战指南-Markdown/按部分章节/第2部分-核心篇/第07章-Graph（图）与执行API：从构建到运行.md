# **第 7 章 Graph（图）与执行 API：从构建到运行**

Graph（图）是LangGraph应用的顶层架构，它将状态、节点、边组合成一个完整的智能体系统。本章将深入探讨图的构建、编译、执行以及相关的API。理解这些内容是构建生产级智能体系统的最后一块拼图。

## **7.1 图的构建流程**

构建一个LangGraph图需要遵循固定的流程。理解这个流程是正确构建图的基础。

### **7.1.1 构建步骤详解**

- 第一步：创建构建器。使用StateGraph创建构建器，传入状态类型。

- 第二步：添加节点。使用add_node添加节点，指定节点名称和函数。

- 第三步：设置入口点。使用set_entry_point指定第一个执行的节点。

- 第四步：添加边。使用add_edge或add_conditional_edges添加边。

- 第五步：编译图。使用compile编译图，生成可执行的图。

> *// python*
>
> \# 图构建完整示例
>
> from typing import TypedDict, Literal
>
> from langgraph.graph import StateGraph, END
>
> \# 第一步：定义状态
>
> class MyState(TypedDict):
>
> messages: list
>
> result: str
>
> \# 第二步：定义节点
>
> def node_a(state: MyState) -\> MyState:
>
> return {"result": "processed by A"}
>
> def node_b(state: MyState) -\> MyState:
>
> return {"result": "processed by B"}
>
> \# 第三步：创建构建器
>
> builder = StateGraph(MyState)
>
> \# 第四步：添加节点
>
> builder.add_node("node_a", node_a)
>
> builder.add_node("node_b", node_b)
>
> \# 第五步：设置入口点
>
> builder.set_entry_point("node_a")
>
> \# 第六步：添加边
>
> builder.add_edge("node_a", "node_b")
>
> builder.add_edge("node_b", END)
>
> \# 第七步：编译图
>
> graph = builder.compile()
>
> \# 第八步：执行图
>
> result = graph.invoke({"messages": \[\], "result": ""})
>
> print(result) \# {'messages': \[\], 'result': 'processed by B'}

## **7.2 执行 API 详解**

### **7.2.1 invoke：同步执行**

invoke是最基本的执行方法，它会阻塞直到图执行完成，然后返回最终状态。

> *// python*
>
> \# invoke 示例
>
> from langgraph.graph import StateGraph, END
>
> \# 构建图
>
> graph = builder.compile()
>
> \# 基本执行
>
> result = graph.invoke({"messages": \[\], "value": 0})
>
> print(result) \# 最终状态
>
> \# 带配置的执行
>
> config = {"configurable": {"thread_id": "user-123"}}
>
> result = graph.invoke({"messages": \[\], "value": 0}, config=config)
>
> \# 带超时的执行
>
> result = graph.invoke({"messages": \[\], "value": 0}, timeout=30.0)
>
> \# invoke 的特点：
>
> \# 1. 同步阻塞，等待执行完成
>
> \# 2. 返回最终状态
>
> \# 3. 适用于简单的执行场景

### **7.2.2 stream：流式执行**

stream方法以流的形式返回执行过程，可以实时获取每个节点的输出。

> *// python*
>
> \# stream 示例
>
> \# 流式执行
>
> for event in graph.stream({"messages": \[\], "value": 0}):
>
> print(event)
>
> \# 输出类似: {"node_a": {"result": "processed by A"}}
>
> \# stream 的模式
>
> \# mode="values": 返回完整状态（默认）
>
> for event in graph.stream({"messages": \[\], "value": 0}, stream_mode="values"):
>
> print(event) \# 完整状态
>
> \# mode="updates": 返回节点更新
>
> for event in graph.stream({"messages": \[\], "value": 0}, stream_mode="updates"):
>
> print(event) \# {"node_a": {"result": "..."}}
>
> \# mode="debug": 返回调试信息
>
> for event in graph.stream({"messages": \[\], "value": 0}, stream_mode="debug"):
>
> print(event) \# 包含更多调试信息
>
> \# 流式执行的特点：
>
> \# 1. 可以实时获取执行进度
>
> \# 2. 适用于需要展示执行过程的场景
>
> \# 3. 可以提前终止执行

### **7.2.3 异步 API**

LangGraph提供了完整的异步API，适用于高并发场景。

> *// python*
>
> \# 异步 API 示例
>
> import asyncio
>
> async def main():
>
> \# 异步执行
>
> result = await graph.ainvoke({"messages": \[\], "value": 0})
>
> print(result)
>
> \# 异步流式执行
>
> async for event in graph.astream({"messages": \[\], "value": 0}):
>
> print(event)
>
> \# 异步批量执行
>
> inputs = \[{"value": i} for i in range(10)\]
>
> results = await graph.abatch(inputs)
>
> print(results)
>
> \# 运行异步函数
>
> asyncio.run(main())
>
> \# 在 FastAPI 中使用
>
> from fastapi import FastAPI
>
> app = FastAPI()
>
> @app.post("/process")
>
> async def process(request: dict):
>
> result = await graph.ainvoke(request)
>
> return result

## **7.3 图的可视化**

LangGraph支持将图导出为Mermaid格式，便于可视化和调试。

> *// python*
>
> \# 图的可视化
>
> from IPython.display import Image, display
>
> \# 获取 Mermaid 图
>
> mermaid_png = graph.get_graph().draw_mermaid_png()
>
> \# 在 Jupyter 中显示
>
> display(Image(mermaid_png))
>
> \# 获取 ASCII 图
>
> ascii_graph = graph.get_graph().draw_ascii()
>
> print(ascii_graph)
>
> \# 获取 Mermaid 代码
>
> mermaid_code = graph.get_graph().draw_mermaid()
>
> print(mermaid_code)
>
> \# 示例输出：
>
> \# graph
>
> \# \_\_start\_\_ --\> node_a
>
> \# node_a --\> node_b
>
> \# node_b --\> \_\_end\_\_
>
> \# 保存为文件
>
> with open("graph.png", "wb") as f:
>
> f.write(mermaid_png)

## **7.4 常见图模式**

### **7.4.1 Router 模式**

Router模式是最常见的模式，根据输入路由到不同的处理分支。

> *// python*
>
> \# Router 模式模板
>
> from typing import Literal
>
> class RouterState(TypedDict):
>
> input: str
>
> intent: str
>
> output: str
>
> def intent_node(state: RouterState) -\> RouterState:
>
> intent = recognize_intent(state\["input"\])
>
> return {"intent": intent}
>
> def router(state: RouterState) -\> Literal\["handler_a", "handler_b", "fallback"\]:
>
> intent_map = {
>
> "type_a": "handler_a",
>
> "type_b": "handler_b"
>
> }
>
> return intent_map.get(state\["intent"\], "fallback")
>
> def handler_a(state: RouterState) -\> RouterState:
>
> return {"output": f"处理 A: {state\['input'\]}"}
>
> def handler_b(state: RouterState) -\> RouterState:
>
> return {"output": f"处理 B: {state\['input'\]}"}
>
> def fallback(state: RouterState) -\> RouterState:
>
> return {"output": "无法处理"}
>
> \# 构建图
>
> builder = StateGraph(RouterState)
>
> builder.add_node("intent", intent_node)
>
> builder.add_node("handler_a", handler_a)
>
> builder.add_node("handler_b", handler_b)
>
> builder.add_node("fallback", fallback)
>
> builder.set_entry_point("intent")
>
> builder.add_conditional_edges("intent", router, {
>
> "handler_a": "handler_a",
>
> "handler_b": "handler_b",
>
> "fallback": "fallback"
>
> })
>
> builder.add_edge("handler_a", END)
>
> builder.add_edge("handler_b", END)
>
> builder.add_edge("fallback", END)
>
> router_graph = builder.compile()

### **7.4.2 ReAct 模式**

ReAct模式是一种迭代推理模式，智能体在思考和行动之间循环。

> *// python*
>
> \# ReAct 模式模板
>
> from typing import Literal
>
> class ReActState(TypedDict):
>
> question: str
>
> thoughts: list\[str\]
>
> actions: list\[dict\]
>
> answer: str \| None
>
> done: bool
>
> def think_node(state: ReActState) -\> ReActState:
>
> thought = llm.invoke(f"思考: {state\['question'\]}")
>
> return {"thoughts": state\["thoughts"\] + \[thought.content\]}
>
> def act_node(state: ReActState) -\> ReActState:
>
> action = decide_action(state\["thoughts"\]\[-1\])
>
> result = execute_action(action)
>
> return {"actions": state\["actions"\] + \[action, result\]}
>
> def should_continue(state: ReActState) -\> Literal\["think", "answer"\]:
>
> if state.get("done") or len(state\["thoughts"\]) \>= 10:
>
> return "answer"
>
> return "think"
>
> def answer_node(state: ReActState) -\> ReActState:
>
> answer = llm.invoke(f"回答: {state\['question'\]}, 思考: {state\['thoughts'\]}")
>
> return {"answer": answer.content, "done": True}
>
> \# 构建图
>
> builder = StateGraph(ReActState)
>
> builder.add_node("think", think_node)
>
> builder.add_node("act", act_node)
>
> builder.add_node("answer", answer_node)
>
> builder.set_entry_point("think")
>
> builder.add_edge("think", "act")
>
> builder.add_conditional_edges("act", should_continue, {
>
> "think": "think",
>
> "answer": "answer"
>
> })
>
> builder.add_edge("answer", END)
>
> react_graph = builder.compile()

## **7.5 本章交付物：一个完整的对话智能体图**

本章的交付物是一个完整的对话智能体图，综合运用了前面学到的所有知识。

> *// python*
>
> """
>
> chapter7_demo.py - 第 7 章示例：完整的对话智能体
>
> 综合运用状态、节点、边、图的知识
>
> """
>
> from typing import TypedDict, Annotated, Literal
>
> from langgraph.graph import StateGraph, END, add_messages
>
> from langgraph.checkpoint.memory import MemorySaver
>
> from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
>
> \# ============================================
>
> \# 状态定义
>
> \# ============================================
>
> class ChatState(TypedDict):
>
> """对话状态"""
>
> messages: Annotated\[list\[BaseMessage\], add_messages\]
>
> intent: str \| None
>
> done: bool
>
> \# ============================================
>
> \# 节点定义
>
> \# ============================================
>
> def intent_node(state: ChatState) -\> ChatState:
>
> """意图识别节点"""
>
> last_message = state\["messages"\]\[-1\].content
>
> if "搜索" in last_message or "查找" in last_message:
>
> intent = "search"
>
> elif "计算" in last_message:
>
> intent = "calculate"
>
> else:
>
> intent = "chat"
>
> return {"intent": intent}
>
> def search_node(state: ChatState) -\> ChatState:
>
> """搜索节点"""
>
> query = state\["messages"\]\[-1\].content
>
> result = f"搜索结果: {query}"
>
> return {
>
> "messages": \[AIMessage(content=result)\],
>
> "done": True
>
> }
>
> def calculate_node(state: ChatState) -\> ChatState:
>
> """计算节点"""
>
> expression = state\["messages"\]\[-1\].content
>
> try:
>
> result = eval(expression.replace("计算", "").strip())
>
> response = f"计算结果: {result}"
>
> except:
>
> response = "无法计算"
>
> return {
>
> "messages": \[AIMessage(content=response)\],
>
> "done": True
>
> }
>
> def chat_node(state: ChatState) -\> ChatState:
>
> """聊天节点"""
>
> response = f"收到您的消息: {state\['messages'\]\[-1\].content}"
>
> return {
>
> "messages": \[AIMessage(content=response)\],
>
> "done": True
>
> }
>
> \# ============================================
>
> \# 路由函数
>
> \# ============================================
>
> def route_by_intent(state: ChatState) -\> Literal\["search", "calculate", "chat"\]:
>
> """意图路由"""
>
> return state.get("intent", "chat")
>
> \# ============================================
>
> \# 图构建
>
> \# ============================================
>
> def build_chat_graph():
>
> builder = StateGraph(ChatState)
>
> builder.add_node("intent", intent_node)
>
> builder.add_node("search", search_node)
>
> builder.add_node("calculate", calculate_node)
>
> builder.add_node("chat", chat_node)
>
> builder.set_entry_point("intent")
>
> builder.add_conditional_edges(
>
> "intent",
>
> route_by_intent,
>
> {
>
> "search": "search",
>
> "calculate": "calculate",
>
> "chat": "chat"
>
> }
>
> )
>
> builder.add_edge("search", END)
>
> builder.add_edge("calculate", END)
>
> builder.add_edge("chat", END)
>
> return builder
>
> def create_chat_agent():
>
> builder = build_chat_graph()
>
> checkpointer = MemorySaver()
>
> return builder.compile(checkpointer=checkpointer)
>
> \# ============================================
>
> \# 测试
>
> \# ============================================
>
> def test_chat_agent():
>
> graph = create_chat_agent()
>
> test_cases = \[
>
> "你好",
>
> "搜索 Python 教程",
>
> "计算 2 + 3"
>
> \]
>
> for user_input in test_cases:
>
> print("=" \* 50)
>
> print(f"用户: {user_input}")
>
> config = {"configurable": {"thread_id": "test"}}
>
> result = graph.invoke(
>
> {"messages": \[HumanMessage(content=user_input)\], "intent": None, "done": False},
>
> config=config
>
> )
>
> print(f"助手: {result\['messages'\]\[-1\].content}")
>
> print(f"意图: {result\['intent'\]}")
>
> if \_\_name\_\_ == "\_\_main\_\_":
>
> test_chat_agent()

## **7.6 本章小结**

本章深入探讨了LangGraph的图构建和执行API。关键要点包括：

- 图的构建遵循固定流程：创建构建器、添加节点、设置入口点、添加边、编译。

- invoke用于同步执行，stream用于流式执行，异步API用于高并发场景。

- 图可以导出为Mermaid格式进行可视化。

- Router模式和ReAct模式是两种常见的图模式。

第二部分到此结束。通过学习状态、节点、边、图四个核心组件，读者已经具备了构建复杂智能体系统的基础能力。第三部分将通过三个递进式的实战案例，帮助读者将所学知识应用到实际项目中。

## **7.7 课后练习**

练习 7.1（基础）：修改对话智能体示例，添加一个新的意图类型和对应的处理节点。

练习 7.2（进阶）：实现一个带检查点的对话智能体，支持多轮对话和会话恢复。

练习 7.3（挑战）：设计一个Supervisor模式的多智能体系统，包含至少三个工作节点。

# **第三部分 实战案例（递进式）**

本部分通过三个递进式的实战案例，帮助读者将前面学到的知识应用到实际项目中。第一个案例是最小可用对话智能体，展示LangGraph的基本用法；第二个案例是工具调用智能体，展示如何集成外部工具；第三个案例是多智能体协作系统，展示如何构建复杂的多智能体架构。每个案例都包含完整的需求分析、架构设计、代码实现和测试验证。
