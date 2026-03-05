# **第 3 章 LangGraph 基础概念**

本章将系统介绍LangGraph的核心概念，包括状态、节点、边、图。这些概念是理解和使用LangGraph的基础，务必确保完全理解后再继续学习。

## **3.1 核心概念总览**

LangGraph的核心可以概括为四个概念：State（状态）、Node（节点）、Edge（边）、Graph（图）。它们之间的关系可以用以下类比来理解：

- State（状态）：就像工厂的流水线上的产品，它承载着所有需要处理的数据。每个工位（节点）都可以查看和修改产品。

- Node（节点）：就像工厂的工位，每个工位负责一个特定的加工任务。工位接收产品，进行加工，然后传递给下一个工位。

- Edge（边）：就像流水线的传送带，它决定了产品从一个工位传到哪个工位。传送带可以是固定的（普通边），也可以根据产品的状态选择方向（条件边）。

- Graph（图）：就像整个工厂的布局，它定义了有哪些工位、传送带如何连接、从哪里开始、到哪里结束。

## **3.2 State（状态）：智能体的记忆**

### **3.2.1 什么是状态**

状态是智能体在执行过程中维护的所有数据的集合。它就像智能体的记忆，记录了对话历史、任务进度、中间结果等信息。在LangGraph中，状态有以下几个关键特点：

- 类型安全：状态使用TypedDict定义，每个字段都有明确的类型。这使得IDE可以提供代码补全，也便于在编译时发现类型错误。

- 不可变更新：节点不直接修改状态，而是返回状态的更新。LangGraph会自动将更新合并到当前状态中。这种不可变设计避免了意外的副作用。

- 可序列化：状态应该能够被序列化为JSON，这样才能保存到检查点中。这意味着状态中不应该包含不可序列化的对象，如文件句柄、数据库连接等。

### **3.2.2 状态定义示例**

> *// python*
>
> \# 状态定义示例
>
> from typing import TypedDict, Annotated
>
> from langgraph.graph import add_messages
>
> from langchain_core.messages import BaseMessage
>
> class ConversationState(TypedDict):
>
> """
>
> 对话状态
>
> 这个状态定义了一个对话智能体需要的所有数据。
>
> 每个字段都有明确的类型和用途。
>
> """
>
> \# 对话历史
>
> \# 使用 add_messages reducer，新消息会自动追加到列表中
>
> messages: Annotated\[list\[BaseMessage\], add_messages\]
>
> \# 当前意图
>
> intent: str \| None
>
> \# 意图置信度
>
> confidence: float
>
> \# 上下文信息
>
> context: dict
>
> \# 是否需要人工介入
>
> need_human: bool
>
> \# 元数据
>
> metadata: dict
>
> \# 状态字段的类型说明：
>
> \# - list\[BaseMessage\]: 消息列表，包含用户和助手的对话
>
> \# - str \| None: 可选字符串，可能为 None
>
> \# - float: 浮点数，通常用于表示概率或分数
>
> \# - dict: 字典，用于存储结构化的键值对
>
> \# - bool: 布尔值，用于表示是/否状态

### **3.2.3 Reducer 机制**

Reducer定义了如何将节点返回的状态更新合并到当前状态中。LangGraph提供了几种内置的Reducer：

- 默认覆盖：新值直接替换旧值。这是最常见的行为。

- add_messages：专门用于消息列表，支持追加、更新和删除消息。

- 自定义Reducer：你可以定义自己的Reducer函数，实现复杂的合并逻辑。

> *// python*
>
> \# Reducer 示例
>
> from typing import TypedDict, Annotated
>
> \# 默认覆盖行为
>
> class StateV1(TypedDict):
>
> count: int \# 新值直接替换旧值
>
> \# 使用 add_messages reducer
>
> class StateV2(TypedDict):
>
> messages: Annotated\[list, add_messages\] \# 新消息追加到列表
>
> \# 自定义 reducer
>
> def merge_dicts(old: dict, new: dict) -\> dict:
>
> """合并字典，新值覆盖旧值"""
>
> result = old.copy()
>
> result.update(new)
>
> return result
>
> class StateV3(TypedDict):
>
> data: Annotated\[dict, merge_dicts\] \# 使用自定义合并逻辑

## **3.3 Node（节点）：智能体的处理单元**

### **3.3.1 节点的本质**

节点是一个函数，它接收当前状态，执行某些操作，然后返回状态更新。节点的本质是：

- 单一职责：每个节点应该只负责一个明确的任务。

- 纯函数倾向：相同的输入应该产生相同的输出，避免副作用。

- 可测试性：节点应该能够独立测试，不需要模拟整个图。

### **3.3.2 节点类型**

根据功能不同，节点可以分为以下类型：

### **3.3.3 节点实现示例**

> *// python*
>
> \# 节点实现示例
>
> from typing import TypedDict
>
> from langchain_openai import ChatOpenAI
>
> from langchain_core.messages import AIMessage
>
> class MyState(TypedDict):
>
> messages: list
>
> response: str
>
> \# LLM 节点
>
> def llm_node(state: MyState) -\> MyState:
>
> """
>
> LLM 节点：调用大语言模型生成回复
>
> 输入：state 包含 messages（对话历史）
>
> 输出：返回包含 response 的状态更新
>
> """
>
> llm = ChatOpenAI(model="gpt-4o")
>
> \# 调用 LLM
>
> response = llm.invoke(state\["messages"\])
>
> \# 返回状态更新（不是完整状态）
>
> return {
>
> "response": response.content,
>
> "messages": \[AIMessage(content=response.content)\]
>
> }
>
> \# 路由节点
>
> def router_node(state: MyState) -\> MyState:
>
> """
>
> 路由节点：分析消息，决定下一步
>
> 这个节点不修改状态，只是为后续的路由决策提供信息。
>
> """
>
> last_message = state\["messages"\]\[-1\].content
>
> \# 简单的意图识别
>
> if "搜索" in last_message:
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
> \# 错误处理节点
>
> def error_handler_node(state: MyState) -\> MyState:
>
> """
>
> 错误处理节点：处理之前节点的错误
>
> 这个节点检查是否有错误，并决定如何处理。
>
> """
>
> error = state.get("error")
>
> if not error:
>
> return {}
>
> \# 根据错误类型决定处理方式
>
> if error.get("type") == "timeout":
>
> return {"action": "retry"}
>
> elif error.get("type") == "validation":
>
> return {"action": "abort", "message": "输入无效"}
>
> else:
>
> return {"action": "fallback"}

## **3.4 Edge（边）：智能体的控制流**

### **3.4.1 边的类型**

LangGraph支持两种类型的边：

- 普通边：表示固定的连接关系，从源节点执行完后一定执行目标节点。

- 条件边：根据路由函数的返回值选择下一个节点，支持分支逻辑。

### **3.4.2 普通边示例**

> *// python*
>
> \# 普通边示例
>
> from langgraph.graph import StateGraph, END
>
> builder = StateGraph(MyState)
>
> \# 添加节点
>
> builder.add_node("step1", step1_node)
>
> builder.add_node("step2", step2_node)
>
> builder.add_node("step3", step3_node)
>
> \# 设置入口点
>
> builder.set_entry_point("step1")
>
> \# 添加普通边：固定流程
>
> builder.add_edge("step1", "step2") \# step1 -\> step2
>
> builder.add_edge("step2", "step3") \# step2 -\> step3
>
> builder.add_edge("step3", END) \# step3 -\> END
>
> \# 执行流程：step1 -\> step2 -\> step3 -\> END
>
> \# 无论状态如何，流程都是固定的

### **3.4.3 条件边示例**

> *// python*
>
> \# 条件边示例
>
> from typing import Literal
>
> def route_by_intent(state: MyState) -\> Literal\["search", "calculate", "chat"\]:
>
> """
>
> 路由函数：根据意图选择下一个节点
>
> 返回值必须是 Literal 类型，明确列出所有可能的返回值。
>
> """
>
> intent = state.get("intent", "chat")
>
> \# 意图映射
>
> intent_map = {
>
> "search": "search",
>
> "calculate": "calculate",
>
> "chat": "chat"
>
> }
>
> return intent_map.get(intent, "chat")
>
> \# 添加条件边
>
> builder.add_conditional_edges(
>
> "router", \# 源节点
>
> route_by_intent, \# 路由函数
>
> {
>
> "search": "search_node", \# 返回 "search" -\> 执行 search_node
>
> "calculate": "calc_node", \# 返回 "calculate" -\> 执行 calc_node
>
> "chat": "chat_node" \# 返回 "chat" -\> 执行 chat_node
>
> }
>
> )

## **3.5 Graph（图）：智能体的完整架构**

### **3.5.1 图的构建流程**

构建一个完整的图需要以下步骤：

- 第一步：定义状态。使用TypedDict定义状态结构。

- 第二步：创建构建器。使用StateGraph创建构建器，传入状态类型。

- 第三步：添加节点。使用add_node添加节点，指定节点名称和函数。

- 第四步：设置入口点。使用set_entry_point指定第一个执行的节点。

- 第五步：添加边。使用add_edge或add_conditional_edges添加边。

- 第六步：编译图。使用compile编译图，生成可执行的图。

### **3.5.2 完整示例**

> *// python*
>
> \# 完整图构建示例
>
> from typing import TypedDict, Literal
>
> from langgraph.graph import StateGraph, END
>
> \# 第一步：定义状态
>
> class ConversationState(TypedDict):
>
> messages: list
>
> intent: str \| None
>
> response: str \| None
>
> \# 第二步：定义节点
>
> def intent_node(state: ConversationState) -\> ConversationState:
>
> """意图识别节点"""
>
> last_message = state\["messages"\]\[-1\].content
>
> if "搜索" in last_message:
>
> return {"intent": "search"}
>
> elif "计算" in last_message:
>
> return {"intent": "calculate"}
>
> else:
>
> return {"intent": "chat"}
>
> def search_node(state: ConversationState) -\> ConversationState:
>
> """搜索节点"""
>
> return {"response": "搜索结果..."}
>
> def calculate_node(state: ConversationState) -\> ConversationState:
>
> """计算节点"""
>
> return {"response": "计算结果..."}
>
> def chat_node(state: ConversationState) -\> ConversationState:
>
> """聊天节点"""
>
> return {"response": "聊天回复..."}
>
> \# 第三步：定义路由函数
>
> def route(state: ConversationState) -\> Literal\["search", "calculate", "chat"\]:
>
> return state.get("intent", "chat")
>
> \# 第四步：构建图
>
> def build_graph():
>
> builder = StateGraph(ConversationState)
>
> \# 添加节点
>
> builder.add_node("intent", intent_node)
>
> builder.add_node("search", search_node)
>
> builder.add_node("calculate", calculate_node)
>
> builder.add_node("chat", chat_node)
>
> \# 设置入口点
>
> builder.set_entry_point("intent")
>
> \# 添加条件边
>
> builder.add_conditional_edges(
>
> "intent",
>
> route,
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
> \# 添加终止边
>
> builder.add_edge("search", END)
>
> builder.add_edge("calculate", END)
>
> builder.add_edge("chat", END)
>
> \# 编译图
>
> return builder.compile()
>
> \# 第五步：执行图
>
> graph = build_graph()
>
> result = graph.invoke({
>
> "messages": \[{"role": "user", "content": "搜索 Python 教程"}\],
>
> "intent": None,
>
> "response": None
>
> })
>
> print(result)
>
> \# 输出：{'messages': \[...\], 'intent': 'search', 'response': '搜索结果...'}

## **3.6 本章小结**

本章介绍了LangGraph的四个核心概念：State（状态）、Node（节点）、Edge（边）、Graph（图）。这些概念是理解和使用LangGraph的基础。

关键要点：

- State是智能体的记忆，使用TypedDict定义，支持Reducer机制。

- Node是智能体的处理单元，遵循单一职责原则。

- Edge定义控制流，包括普通边和条件边。

- Graph将所有组件组合成完整的智能体系统。

下一章将深入探讨状态设计，这是构建智能体系统的第一步。

## **3.7 课后练习**

练习 3.1（基础）：定义一个包含至少5个字段的状态，每个字段有不同的类型。

练习 3.2（进阶）：实现一个自定义Reducer，用于合并两个列表（去重）。

练习 3.3（挑战）：构建一个包含条件边和回环边的图，实现迭代推理。

<table>
<colgroup>
<col style="width: 20%" />
<col style="width: 5%" />
<col style="width: 8%" />
<col style="width: 6%" />
<col style="width: 10%" />
<col style="width: 10%" />
<col style="width: 6%" />
<col style="width: 8%" />
<col style="width: 5%" />
<col style="width: 20%" />
</colgroup>
<tbody>
<tr>
<td>特性</td>
<td colspan="3">LangGraph</td>
<td colspan="2">LangChain Chain</td>
<td colspan="3">AutoGPT</td>
<td>CrewAI</td>
</tr>
<tr>
<td>控制流</td>
<td colspan="3">显式图结构</td>
<td colspan="2">链式结构</td>
<td colspan="3">隐式循环</td>
<td>角色协作</td>
</tr>
<tr>
<td>状态管理</td>
<td colspan="3">显式状态</td>
<td colspan="2">隐式传递</td>
<td colspan="3">全局状态</td>
<td>任务状态</td>
</tr>
<tr>
<td>可观测性</td>
<td colspan="3">内置追踪</td>
<td colspan="2">有限</td>
<td colspan="3">有限</td>
<td>有限</td>
</tr>
<tr>
<td>可恢复性</td>
<td colspan="3">检查点机制</td>
<td colspan="2">不支持</td>
<td colspan="3">不支持</td>
<td>不支持</td>
</tr>
<tr>
<td>学习曲线</td>
<td colspan="3">中等</td>
<td colspan="2">简单</td>
<td colspan="3">复杂</td>
<td>中等</td>
</tr>
<tr>
<td colspan="3">能力等级</td>
<td colspan="4">描述</td>
<td colspan="3">典型表现</td>
</tr>
<tr>
<td colspan="3">初级</td>
<td colspan="4">能够运行和修改示例代码</td>
<td colspan="3">理解基本概念，能完成课后基础练习</td>
</tr>
<tr>
<td colspan="3">中级</td>
<td colspan="4">能够独立构建简单智能体</td>
<td colspan="3">能完成课后进阶练习，能解决常见问题</td>
</tr>
<tr>
<td colspan="3">高级</td>
<td colspan="4">能够构建生产级智能体系统</td>
<td colspan="3">能完成课后挑战练习，能处理复杂场景</td>
</tr>
<tr>
<td colspan="2">学习模式</td>
<td colspan="3">每日时间</td>
<td colspan="3">预计周期</td>
<td colspan="2">适合人群</td>
</tr>
<tr>
<td colspan="2">快速模式</td>
<td colspan="3">4-6小时</td>
<td colspan="3">1-2周</td>
<td colspan="2">全职学习者、有Python基础</td>
</tr>
<tr>
<td colspan="2">标准模式</td>
<td colspan="3">2-3小时</td>
<td colspan="3">3-4周</td>
<td colspan="2">在职学习者、有一定编程基础</td>
</tr>
<tr>
<td colspan="2">慢速模式</td>
<td colspan="3">1小时</td>
<td colspan="3">6-8周</td>
<td colspan="2">业余学习者、编程基础较弱</td>
</tr>
<tr>
<td colspan="3">节点类型</td>
<td colspan="4">功能</td>
<td colspan="3">示例</td>
</tr>
<tr>
<td colspan="3">LLM节点</td>
<td colspan="4">调用大语言模型</td>
<td colspan="3">生成回复、分析文本</td>
</tr>
<tr>
<td colspan="3">工具节点</td>
<td colspan="4">调用外部工具</td>
<td colspan="3">搜索、计算、查询数据库</td>
</tr>
<tr>
<td colspan="3">路由节点</td>
<td colspan="4">决定下一步</td>
<td colspan="3">意图识别、条件判断</td>
</tr>
<tr>
<td colspan="3">聚合节点</td>
<td colspan="4">合并多个结果</td>
<td colspan="3">整合并行执行的结果</td>
</tr>
<tr>
<td colspan="3">纠错节点</td>
<td colspan="4">处理错误</td>
<td colspan="3">重试、降级、升级</td>
</tr>
</tbody>
</table>
