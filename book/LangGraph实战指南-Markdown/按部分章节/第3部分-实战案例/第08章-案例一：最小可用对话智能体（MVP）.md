# **第 8 章 案例一：最小可用对话智能体（MVP）**

**📋 业务背景说明\**
这是一个"最小可用产品（MVP）"对话智能体，展示了智能体系统的核心要素：\
【业务场景】\
一个简单的在线客服助手，需要能够：\
• 接收用户消息\
• 理解用户意图\
• 生成合理响应\
• 保持对话连贯\
【为什么从MVP开始？】\
• 快速验证技术可行性\
• 降低开发风险\
• 为后续扩展打基础\
**🔄 完整业务逻辑流程\**
用户输入 → 意图识别 → 业务处理 → 响应生成 → 返回用户\
【详细流程示例】\
用户："你好，我想查询我的订单状态"\
→ 系统将消息添加到对话历史\
→ 调用LLM分析对话历史\
→ LLM生成响应："您好！请提供您的订单号..."\
【业务价值】\
• 7x24小时自动响应\
• 减少人工客服压力\
• 提升用户满意度\
**📍 在整体系统中的位置\**
这是最基础的智能体架构，后续扩展方向：\
• MVP → 添加工具调用（第9章）\
• → 添加多智能体协作（第10章）\
• → 添加检查点持久化（第17章）\
**💡 关键设计决策\**
【决策1】状态设计为什么这样简单？\
• MVP只需要messages字段即可实现基本对话\
• 保持简单，便于理解和调试\
【决策2】为什么只有一个节点？\
• MVP阶段功能单一，不需要复杂编排\
**⚠️ 边界情况处理\**
• 对话历史太长：设置最大消息数限制\
• 敏感内容：内容审核过滤\
• LLM返回格式错误：解析失败时使用默认回复

<img src="LangGraph实战指南_assets/media/image4.png" style="width:3.03472in;height:10.26458in" />

本章将构建一个最小可用的对话智能体（Minimum Viable Product, MVP）。虽然功能简单，但它包含了构建复杂智能体系统所需的所有基本元素。通过这个案例，读者将学会如何将前面学到的状态、节点、边、图的知识整合起来，构建一个完整的智能体应用。

## **8.1 需求分析**

### **8.1.1 功能需求**

在开始编码之前，我们需要明确这个MVP智能体需要实现哪些功能。作为一个最小可用产品，它应该具备以下核心能力：

- 多轮对话能力：智能体能够进行多轮对话，记住之前的对话内容。这是对话智能体的基本能力，用户不需要每次都重复之前的信息。例如，用户说"我想订一张机票"，然后说"去北京"，智能体应该知道用户是要订去北京的机票。

- 上下文保持：智能体能够在对话过程中保持上下文，理解用户的指代和省略。例如，用户说"它多少钱？"，智能体需要知道"它"指的是之前提到的商品。

- 基本路由能力：智能体能够识别用户的意图，并根据意图选择不同的处理方式。例如，闲聊、问答、任务执行等不同类型的请求需要不同的处理逻辑。

- 会话管理：智能体能够区分不同的用户会话，每个会话有独立的状态。这为后续的多用户支持打下基础。

### **8.1.2 非功能需求**

- 响应时间：普通请求的响应时间应该在3秒以内。

- 可扩展性：架构设计应该便于添加新功能，如工具调用、知识检索等。

- 可测试性：核心组件应该可以独立测试。

- 可观测性：执行过程应该有清晰的日志，便于调试。

### **8.1.3 技术选型**

## **8.2 架构设计**

### **8.2.1 状态设计**

状态是智能体的核心数据结构，它决定了智能体能够记住什么信息。对于这个MVP，我们需要以下状态字段：

> *// python*
>
> \# 状态定义
>
> from typing import TypedDict, Annotated
>
> from langgraph.graph import add_messages
>
> from langchain_core.messages import BaseMessage
>
> class ChatState(TypedDict):
>
> """
>
> 对话智能体状态
>
> 设计原则：
>
> 1\. 使用 TypedDict 确保类型安全
>
> 2\. 使用 add_messages reducer 自动处理消息累积
>
> 3\. 包含足够的上下文信息支持多轮对话
>
> """
>
> \# 消息历史：使用 add_messages reducer 自动追加
>
> messages: Annotated\[list\[BaseMessage\], add_messages\]
>
> \# 当前意图：用于路由决策
>
> intent: str \| None
>
> \# 对话上下文：存储关键实体和信息
>
> context: dict
>
> \# 会话元数据
>
> metadata: dict
>
> \# 状态字段说明：
>
> \# - messages: 对话历史，包含所有用户和助手的消息
>
> \# - intent: 当前识别的意图，如 "chat", "qa", "task"
>
> \# - context: 对话上下文，如用户提到的实体、偏好等
>
> \# - metadata: 会话级别的元数据，如会话ID、开始时间等

状态设计的关键考量：messages字段使用add_messages reducer，这意味着每次节点返回新消息时，它们会自动追加到现有消息列表中，无需手动管理。intent字段存储当前识别的意图，用于路由决策。context字段存储对话中的关键信息，如用户提到的实体、偏好等。metadata字段存储会话级别的元数据，如会话ID、开始时间等。

### **8.2.2 节点划分**

节点是智能体的处理单元。根据单一职责原则，我们将智能体划分为以下节点：

### **8.2.3 图拓扑设计**

图拓扑定义了节点之间的连接关系。对于这个MVP，我们采用Router模式：

> <img src="LangGraph实战指南_assets/media/image5.png" style="width:5.5in;height:2.04564in" />
>
> \# 图拓扑示意
>
> """
>
> ┌─────────────────┐
>
> │ intent_router │
>
> └────────┬────────┘
>
> │
>
> ┌──────────────┼──────────────┐
>
> │ │ │
>
> ▼ ▼ ▼
>
> ┌─────────┐ ┌─────────┐ ┌─────────┐
>
> │ chat │ │ qa │ │ task │
>
> │ \_agent │ │ \_agent │ │ \_agent │
>
> └────┬────┘ └────┬────┘ └────┬────┘
>
> │ │ │
>
> └──────────────┼──────────────┘
>
> │
>
> ▼
>
> ┌─────────┐
>
> │ END │
>
> └─────────┘
>
> （还有 fallback_agent 分支）
>
> """

## **8.3 代码实现**

### **8.3.1 导入和配置**

> *// python*
>
> """
>
> mvp_chat_agent.py - 最小可用对话智能体
>
> 这是一个完整的对话智能体实现，包含：
>
> 1\. 状态定义
>
> 2\. 节点实现
>
> 3\. 图构建
>
> 4\. 执行入口
>
> """
>
> import os
>
> from typing import TypedDict, Annotated, Literal
>
> from dotenv import load_dotenv
>
> \# 加载环境变量
>
> load_dotenv()
>
> \# LangGraph 导入
>
> from langgraph.graph import StateGraph, END, add_messages
>
> from langgraph.checkpoint.memory import MemorySaver
>
> \# LangChain 导入
>
> from langchain_openai import ChatOpenAI
>
> from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
>
> from langchain_core.prompts import ChatPromptTemplate
>
> \# 初始化 LLM
>
> llm = ChatOpenAI(
>
> model="gpt-4o",
>
> temperature=0.7,
>
> api_key=os.getenv("OPENAI_API_KEY")
>
> )

### **8.3.2 意图识别节点**

> *// python*
>
> \# 意图识别节点
>
> def intent_router_node(state: ChatState) -\> ChatState:
>
> """
>
> 意图识别节点
>
> 职责：
>
> 1\. 分析用户输入
>
> 2\. 识别用户意图
>
> 3\. 更新状态中的 intent 字段
>
> 设计考量：
>
> \- 使用 LLM 进行意图识别，提高准确性
>
> \- 返回结构化结果，便于后续处理
>
> \- 有默认值处理未知情况
>
> """
>
> \# 获取最后一条用户消息
>
> last_message = state\["messages"\]\[-1\].content if state\["messages"\] else ""
>
> \# 构建意图识别提示词
>
> prompt = f"""分析以下用户输入的意图。
>
> 用户输入：{last_message}
>
> 意图类型：
>
> \- chat: 闲聊、打招呼、日常对话
>
> \- qa: 询问问题、寻求信息
>
> \- task: 请求执行某个任务
>
> \- unknown: 无法确定
>
> 请只返回意图类型，不要返回其他内容。
>
> """
>
> \# 调用 LLM 进行意图识别
>
> response = llm.invoke(prompt)
>
> intent = response.content.strip().lower()
>
> \# 验证意图类型
>
> valid_intents = \["chat", "qa", "task", "unknown"\]
>
> if intent not in valid_intents:
>
> intent = "unknown"
>
> return {"intent": intent}

意图识别节点是整个智能体的入口。它使用LLM分析用户输入，识别用户意图。使用LLM进行意图识别的好处是灵活性高，可以处理各种表达方式。验证意图类型是为了确保后续路由的正确性。

### **8.3.3 各专家节点实现**

> *// python*
>
> \# 闲聊节点
>
> def chat_agent_node(state: ChatState) -\> ChatState:
>
> """
>
> 闲聊处理节点
>
> 职责：
>
> 1\. 处理日常对话
>
> 2\. 保持友好的对话风格
>
> """
>
> \# 构建系统提示词
>
> system_prompt = """你是一个友好的对话助手。
>
> 请用自然、亲切的方式回应用户。
>
> 保持回答简洁，不要过于冗长。
>
> """
>
> \# 构建消息列表
>
> messages = \[
>
> SystemMessage(content=system_prompt),
>
> \*state\["messages"\]
>
> \]
>
> \# 调用 LLM
>
> response = llm.invoke(messages)
>
> return {"messages": \[response\]}
>
> \# 问答节点
>
> def qa_agent_node(state: ChatState) -\> ChatState:
>
> """
>
> 问答处理节点
>
> 职责：
>
> 1\. 回答用户问题
>
> 2\. 提供准确、有用的信息
>
> """
>
> system_prompt = """你是一个知识渊博的问答助手。
>
> 请准确回答用户的问题。
>
> 如果不确定答案，请诚实说明。
>
> 提供的信息要有条理，便于理解。
>
> """
>
> messages = \[
>
> SystemMessage(content=system_prompt),
>
> \*state\["messages"\]
>
> \]
>
> response = llm.invoke(messages)
>
> return {"messages": \[response\]}
>
> \# 任务节点
>
> def task_agent_node(state: ChatState) -\> ChatState:
>
> """
>
> 任务处理节点
>
> 职责：
>
> 1\. 理解用户的任务请求
>
> 2\. 提供任务执行指导或模拟执行
>
> """
>
> system_prompt = """你是一个任务执行助手。
>
> 帮助用户完成他们请求的任务。
>
> 如果任务需要具体操作，请提供清晰的步骤说明。
>
> 如果任务无法完成，请说明原因并提供替代方案。
>
> """
>
> messages = \[
>
> SystemMessage(content=system_prompt),
>
> \*state\["messages"\]
>
> \]
>
> response = llm.invoke(messages)
>
> return {"messages": \[response\]}
>
> \# 降级节点
>
> def fallback_agent_node(state: ChatState) -\> ChatState:
>
> """
>
> 降级处理节点
>
> 职责：
>
> 1\. 处理无法识别的意图
>
> 2\. 引导用户提供更多信息
>
> """
>
> response = AIMessage(
>
> content="抱歉，我不太理解您的意思。"
>
> "您可以尝试：\n"
>
> "1. 用不同的方式表达\n"
>
> "2. 提供更多上下文信息\n"
>
> "3. 询问具体的问题"
>
> )
>
> return {"messages": \[response\]}

### **8.3.4 路由函数**

> *// python*
>
> \# 路由函数
>
> def route_by_intent(state: ChatState) -\> Literal\["chat", "qa", "task", "fallback"\]:
>
> """
>
> 根据意图路由到对应的处理节点
>
> 设计考量：
>
> 1\. 使用 Literal 类型确保类型安全
>
> 2\. 有明确的默认分支
>
> 3\. 路由逻辑简单清晰
>
> """
>
> intent = state.get("intent", "unknown")
>
> \# 意图映射
>
> intent_map = {
>
> "chat": "chat",
>
> "qa": "qa",
>
> "task": "task",
>
> "unknown": "fallback"
>
> }
>
> return intent_map.get(intent, "fallback")

### **8.3.5 图构建**

> *// python*
>
> \# 图构建
>
> def build_chat_graph():
>
> """
>
> 构建对话智能体图
>
> 步骤：
>
> 1\. 创建构建器
>
> 2\. 添加节点
>
> 3\. 设置入口点
>
> 4\. 添加边
>
> 5\. 编译图
>
> """
>
> \# 创建构建器
>
> builder = StateGraph(ChatState)
>
> \# 添加节点
>
> builder.add_node("intent_router", intent_router_node)
>
> builder.add_node("chat_agent", chat_agent_node)
>
> builder.add_node("qa_agent", qa_agent_node)
>
> builder.add_node("task_agent", task_agent_node)
>
> builder.add_node("fallback_agent", fallback_agent_node)
>
> \# 设置入口点
>
> builder.set_entry_point("intent_router")
>
> \# 添加条件边
>
> builder.add_conditional_edges(
>
> "intent_router",
>
> route_by_intent,
>
> {
>
> "chat": "chat_agent",
>
> "qa": "qa_agent",
>
> "task": "task_agent",
>
> "fallback": "fallback_agent"
>
> }
>
> )
>
> \# 添加终止边
>
> builder.add_edge("chat_agent", END)
>
> builder.add_edge("qa_agent", END)
>
> builder.add_edge("task_agent", END)
>
> builder.add_edge("fallback_agent", END)
>
> return builder
>
> \# 编译图（带检查点）
>
> def create_chat_agent():
>
> """创建对话智能体实例"""
>
> builder = build_chat_graph()
>
> checkpointer = MemorySaver()
>
> return builder.compile(checkpointer=checkpointer)

### **8.3.6 执行入口**

> *// python*
>
> \# 执行入口
>
> def chat(user_input: str, thread_id: str = "default") -\> str:
>
> """
>
> 对话入口函数
>
> 参数：
>
> \- user_input: 用户输入
>
> \- thread_id: 会话 ID
>
> 返回：
>
> \- 智能体回复
>
> """
>
> \# 创建智能体
>
> graph = create_chat_agent()
>
> \# 配置
>
> config = {"configurable": {"thread_id": thread_id}}
>
> \# 执行
>
> result = graph.invoke(
>
> {
>
> "messages": \[HumanMessage(content=user_input)\],
>
> "intent": None,
>
> "context": {},
>
> "metadata": {"thread_id": thread_id}
>
> },
>
> config=config
>
> )
>
> \# 返回最后一条消息
>
> return result\["messages"\]\[-1\].content
>
> \# CLI 入口
>
> def main():
>
> """命令行交互入口"""
>
> print("=" \* 50)
>
> print("对话智能体 MVP")
>
> print("输入 'quit' 或 'exit' 退出")
>
> print("=" \* 50)
>
> thread_id = "cli-session"
>
> while True:
>
> user_input = input("\n用户: ").strip()
>
> if user_input.lower() in \["quit", "exit"\]:
>
> print("再见！")
>
> break
>
> if not user_input:
>
> continue
>
> response = chat(user_input, thread_id)
>
> print(f"助手: {response}")
>
> if \_\_name\_\_ == "\_\_main\_\_":
>
> main()

## **8.4 测试验证**

### **8.4.1 单元测试**

> *// python*
>
> \# 单元测试
>
> import pytest
>
> from unittest.mock import Mock, patch
>
> class TestIntentRouterNode:
>
> """意图识别节点测试"""
>
> @patch('mvp_chat_agent.llm')
>
> def test_chat_intent(self, mock_llm):
>
> """测试闲聊意图识别"""
>
> \# 模拟 LLM 返回
>
> mock_llm.invoke.return_value = Mock(content="chat")
>
> state = {
>
> "messages": \[HumanMessage(content="你好")\],
>
> "intent": None,
>
> "context": {},
>
> "metadata": {}
>
> }
>
> result = intent_router_node(state)
>
> assert result\["intent"\] == "chat"
>
> @patch('mvp_chat_agent.llm')
>
> def test_qa_intent(self, mock_llm):
>
> """测试问答意图识别"""
>
> mock_llm.invoke.return_value = Mock(content="qa")
>
> state = {
>
> "messages": \[HumanMessage(content="什么是 Python？")\],
>
> "intent": None,
>
> "context": {},
>
> "metadata": {}
>
> }
>
> result = intent_router_node(state)
>
> assert result\["intent"\] == "qa"
>
> class TestRouteByIntent:
>
> """路由函数测试"""
>
> def test_route_chat(self):
>
> """测试 chat 路由"""
>
> state = {"intent": "chat"}
>
> assert route_by_intent(state) == "chat"
>
> def test_route_qa(self):
>
> """测试 qa 路由"""
>
> state = {"intent": "qa"}
>
> assert route_by_intent(state) == "qa"
>
> def test_route_unknown(self):
>
> """测试未知意图路由"""
>
> state = {"intent": None}
>
> assert route_by_intent(state) == "fallback"

### **8.4.2 集成测试**

> *// python*
>
> \# 集成测试
>
> class TestChatGraph:
>
> """图集成测试"""
>
> def test_full_conversation(self):
>
> """测试完整对话流程"""
>
> from mvp_chat_agent import create_chat_agent
>
> graph = create_chat_agent()
>
> \# 测试闲聊
>
> result = graph.invoke({
>
> "messages": \[HumanMessage(content="你好")\],
>
> "intent": None,
>
> "context": {},
>
> "metadata": {}
>
> })
>
> assert len(result\["messages"\]) \> 0
>
> assert result\["intent"\] is not None
>
> def test_multi_turn_conversation(self):
>
> """测试多轮对话"""
>
> from mvp_chat_agent import create_chat_agent
>
> graph = create_chat_agent()
>
> config = {"configurable": {"thread_id": "test-multi-turn"}}
>
> \# 第一轮
>
> result1 = graph.invoke({
>
> "messages": \[HumanMessage(content="我叫张三")\],
>
> "intent": None,
>
> "context": {},
>
> "metadata": {}
>
> }, config=config)
>
> \# 第二轮（应该记住名字）
>
> result2 = graph.invoke({
>
> "messages": \[HumanMessage(content="我叫什么名字？")\],
>
> "intent": None,
>
> "context": {},
>
> "metadata": {}
>
> }, config=config)
>
> \# 验证消息历史
>
> assert len(result2\["messages"\]) \> 2

## **8.5 本章交付物**

本章的交付物是一个完整可运行的对话智能体，包含以下文件：

> *// bash*
>
> \# 项目结构
>
> mvp_chat_agent/
>
> ├── src/
>
> │ ├── \_\_init\_\_.py
>
> │ ├── state.py \# 状态定义
>
> │ ├── nodes/
>
> │ │ ├── \_\_init\_\_.py
>
> │ │ ├── intent.py \# 意图识别节点
>
> │ │ ├── chat.py \# 闲聊节点
>
> │ │ ├── qa.py \# 问答节点
>
> │ │ └── task.py \# 任务节点
>
> │ └── graph.py \# 图构建
>
> ├── tests/
>
> │ ├── \_\_init\_\_.py
>
> │ ├── test_nodes.py \# 节点测试
>
> │ └── test_graph.py \# 图测试
>
> ├── .env \# 环境变量
>
> ├── pyproject.toml \# 项目配置
>
> └── README.md \# 项目说明

## **8.6 本章小结**

本章构建了一个最小可用的对话智能体，展示了如何将状态、节点、边、图的知识整合起来。关键要点包括：

- 需求分析是第一步：明确功能需求和非功能需求。

- 状态设计要考虑上下文保持和多轮对话。

- 节点划分要遵循单一职责原则。

- 图拓扑采用Router模式，根据意图路由到不同的处理节点。

- 测试要覆盖单元测试和集成测试。

下一章将扩展这个MVP，添加工具调用能力，使智能体能够执行实际的操作。

## **8.7 课后练习**

练习 8.1：为对话智能体添加一个新的意图类型"weather"，用于处理天气查询请求。

练习 8.2：实现一个上下文管理功能，能够记住用户在对话中提到的关键信息（如姓名、偏好等）。

练习 8.3：为对话智能体添加一个"重置"功能，允许用户清除当前会话的历史记录。
