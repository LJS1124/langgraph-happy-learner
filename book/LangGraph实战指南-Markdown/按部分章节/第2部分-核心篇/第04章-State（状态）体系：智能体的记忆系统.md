# **第 4 章 State（状态）体系：智能体的记忆系统**

**📋 业务背景说明\**
在智能体系统中，State就像是智能体的"记忆"。想象一个客服机器人的工作场景：\
【场景】用户与客服机器人对话\
• 用户："我想查订单" → 机器人需要记住"查订单"这个意图\
• 用户："订单号是12345" → 机器人需要把订单号和之前的意图关联起来\
• 用户："什么时候能到？" → 机器人需要知道用户问的是订单12345的配送时间\
如果没有状态管理，机器人每次都像失忆一样，无法进行连贯对话。\
State解决的核心问题：\
• 让智能体能够"记住"对话上下文\
• 实现连贯的多轮交互体验\
• 支持复杂业务流程的状态追踪\
**🔄 业务逻辑流程\**
【输入】用户消息 + 当前状态\
【处理】状态读取 → 智能体决策 → 状态更新\
【输出】新状态 + 智能体响应\
【业务价值】实现连贯的多轮对话体验\
流程示意：\
用户消息 → 状态读取 → 智能体处理 → 状态更新 → 响应用户\
↑ ↓\
└───────────── 下一轮对话 ←─────────────────┘\
**📍 在整体系统中的位置\**
State是智能体的"大脑记忆区"：\
• 上游依赖：用户输入、工具返回结果\
• 当前模块：存储和更新状态数据\
• 下游影响：智能体决策、检查点持久化\
**💡 关键设计决策\**
【决策1】为什么用TypedDict而不是普通字典？\
• 业务原因：明确的状态结构让团队协作更清晰\
• 技术原因：类型检查可以在开发阶段发现错误\
【决策2】为什么需要Reducer函数？\
• 业务原因：不同场景下状态更新逻辑不同\
• 技术原因：确保状态更新的可预测性\
**⚠️ 边界情况处理\**
• 状态过大：设置大小限制，超出时进行摘要压缩\
• 状态冲突：使用乐观锁机制，检测冲突后重试\
• 敏感信息：敏感字段加密存储，日志脱敏

<img src="LangGraph实战指南_assets/media/image1.png" style="width:2.60069in;height:9.8625in" />

状态是LangGraph智能体系统的核心。如果把智能体比作一个人，状态就是它的记忆——记录了对话历史、任务进度、上下文信息等所有需要记住的内容。本章将深入探讨状态的设计原则、类型定义、Reducer机制以及最佳实践。

## **4.1 为什么状态设计如此重要**

### **4.1.1 状态的本质**

在传统的程序中，数据通常存储在数据库或变量中，处理逻辑通过函数调用来组织。但在智能体系统中，情况有所不同：

- 智能体的执行是不确定的：LLM的输出不可预测，同样的输入可能产生不同的输出。这意味着我们需要一种机制来追踪"发生了什么"。

- 智能体需要上下文：多轮对话、任务分解、错误恢复等场景都需要访问之前的信息。状态就是这些信息的载体。

- 智能体可能被中断：人工审批、等待外部事件等情况需要暂停执行。状态需要能够被保存和恢复。

LangGraph的状态设计正是为了解决这些问题。状态不仅存储数据，还定义了数据如何被更新、如何被追踪、如何被恢复。

### **4.1.2 状态设计的影响**

状态设计的好坏直接影响系统的可维护性和可扩展性：

好的状态设计：字段命名清晰，类型明确，更新逻辑简单。当需求变化时，只需要添加或修改少量字段。调试时可以清楚地看到状态变化。

差的状态设计：字段命名模糊，类型混乱，更新逻辑复杂。当需求变化时，需要大量重构。调试时难以追踪问题。

让我们通过一个具体的例子来说明这个问题。假设我们要构建一个客服智能体：

> *// python*
>
> \# 差的状态设计
>
> class BadState(TypedDict):
>
> data: dict \# 什么都往这里放，类型不明确
>
> temp: str \# 临时变量，不知道干什么用
>
> flag: bool \# 标志位，不知道代表什么
>
> \# 问题：
>
> \# 1. data 字段太宽泛，什么都可以放，类型不安全
>
> \# 2. temp 字段命名不清晰，不知道用途
>
> \# 3. flag 字段含义不明，难以理解
>
> \# 4. 缺少必要的字段，如对话历史、用户信息等
>
> \# 好的状态设计
>
> class GoodState(TypedDict):
>
> \# 对话相关
>
> messages: Annotated\[list\[BaseMessage\], add_messages\] \# 对话历史
>
> current_intent: str \| None \# 当前意图
>
> \# 用户相关
>
> user_id: str \# 用户ID
>
> user_info: dict \# 用户信息
>
> \# 任务相关
>
> task_type: str \| None \# 任务类型
>
> task_status: str \# 任务状态：pending, processing, completed, failed
>
> \# 上下文
>
> context: dict \# 上下文信息
>
> metadata: dict \# 元数据
>
> \# 优点：
>
> \# 1. 每个字段都有明确的用途
>
> \# 2. 类型清晰，IDE可以提供代码补全
>
> \# 3. 结构完整，覆盖了客服场景的主要需求
>
> \# 4. 命名规范，易于理解

## **4.2 状态类型定义：TypedDict vs Pydantic vs Dataclass**

LangGraph支持多种方式定义状态类型，每种方式都有其优缺点。选择合适的方式对于项目的可维护性很重要。

### **4.2.1 TypedDict**

TypedDict是Python内置的类型提示工具，LangGraph官方推荐使用。它的优点是轻量、与LangGraph的Reducer机制完美配合。

> *// python*
>
> \# TypedDict 示例
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
> 使用 TypedDict 定义状态类型。
>
> 优点：轻量、与 LangGraph 完美配合
>
> 缺点：运行时不做类型检查
>
> """
>
> \# 对话历史
>
> messages: Annotated\[list\[BaseMessage\], add_messages\]
>
> \# 当前意图
>
> intent: str \| None
>
> \# 置信度
>
> confidence: float
>
> \# 是否需要人工介入
>
> need_human: bool
>
> \# 元数据
>
> metadata: dict
>
> \# 使用示例
>
> state: ConversationState = {
>
> "messages": \[\],
>
> "intent": None,
>
> "confidence": 0.0,
>
> "need_human": False,
>
> "metadata": {}
>
> }
>
> \# 类型提示会在 IDE 中显示，但运行时不检查
>
> \# 这意味着以下代码不会报错（但 IDE 会警告）
>
> wrong_state: ConversationState = {
>
> "messages": "not a list", \# 类型错误，但运行时不报错
>
> "intent": 123, \# 类型错误，但运行时不报错
>
> }

### **4.2.2 Pydantic**

Pydantic提供了运行时类型验证，适合需要严格数据验证的场景。

> *// python*
>
> \# Pydantic 示例
>
> from pydantic import BaseModel, Field
>
> from typing import Optional
>
> from langchain_core.messages import BaseMessage
>
> class ConversationStatePydantic(BaseModel):
>
> """
>
> 使用 Pydantic 定义状态
>
> 优点：运行时类型验证、丰富的验证器
>
> 缺点：与 LangGraph Reducer 配合需要额外处理
>
> """
>
> \# 对话历史
>
> messages: list\[BaseMessage\] = Field(default_factory=list)
>
> \# 当前意图
>
> intent: Optional\[str\] = Field(default=None)
>
> \# 置信度（带验证）
>
> confidence: float = Field(
>
> default=0.0,
>
> ge=0.0, \# 大于等于 0
>
> le=1.0, \# 小于等于 1
>
> description="意图识别的置信度"
>
> )
>
> \# 是否需要人工介入
>
> need_human: bool = Field(default=False)
>
> \# 元数据
>
> metadata: dict = Field(default_factory=dict)
>
> class Config:
>
> \# 允许任意类型（如 BaseMessage）
>
> arbitrary_types_allowed = True
>
> \# 使用示例
>
> state = ConversationStatePydantic(
>
> messages=\[\],
>
> intent="search",
>
> confidence=0.95
>
> )
>
> \# 运行时验证
>
> try:
>
> invalid_state = ConversationStatePydantic(
>
> confidence=1.5 \# 超出范围，会抛出验证错误
>
> )
>
> except ValueError as e:
>
> print(f"验证错误: {e}")

### **4.2.3 如何选择**

> **💡 推荐做法**
>
> 对于大多数LangGraph项目，推荐使用TypedDict。如果需要运行时验证，可以在边界层（如API入口）使用Pydantic，内部使用TypedDict。

## **4.3 Reducer 机制：状态更新的核心**

Reducer定义了如何将节点返回的状态更新合并到当前状态中。理解Reducer机制是掌握LangGraph状态管理的关键。

### **4.3.1 默认行为：覆盖**

默认情况下，节点返回的字段会直接覆盖状态中的对应字段。这是最简单、最常见的行为。

> *// python*
>
> \# 默认覆盖行为
>
> class SimpleState(TypedDict):
>
> count: int
>
> message: str
>
> def increment_node(state: SimpleState) -\> SimpleState:
>
> \# 返回的状态更新会直接覆盖
>
> return {"count": state\["count"\] + 1}
>
> def set_message_node(state: SimpleState) -\> SimpleState:
>
> \# 返回的状态更新会直接覆盖
>
> return {"message": "Hello"}
>
> \# 执行过程：
>
> \# 初始状态: {"count": 0, "message": ""}
>
> \# increment_node 返回: {"count": 1}
>
> \# 新状态: {"count": 1, "message": ""} \# count 被覆盖，message 不变
>
> \# set_message_node 返回: {"message": "Hello"}
>
> \# 新状态: {"count": 1, "message": "Hello"} \# message 被覆盖，count 不变

### **4.3.2 add_messages Reducer**

add_messages是LangGraph内置的Reducer，专门用于处理消息列表。它支持追加、更新和删除消息。

> *// python*
>
> \# add_messages Reducer
>
> from typing import Annotated
>
> from langgraph.graph import add_messages
>
> from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
>
> class ChatState(TypedDict):
>
> \# 使用 add_messages reducer
>
> messages: Annotated\[list\[BaseMessage\], add_messages\]
>
> def chat_node(state: ChatState) -\> ChatState:
>
> \# 返回新消息，会自动追加到 messages 列表
>
> return {
>
> "messages": \[AIMessage(content="你好！有什么可以帮助你的？")\]
>
> }
>
> \# add_messages 的行为：
>
> \# 1. 如果消息有 id 且已存在，则更新该消息
>
> \# 2. 如果消息有 id 且不存在，则追加该消息
>
> \# 3. 如果消息没有 id，则追加该消息
>
> \# 4. 如果返回的消息包含 REMOVE 字段，则删除该消息
>
> \# 示例：追加消息
>
> state1 = {"messages": \[HumanMessage(content="你好")\]}
>
> \# 节点返回 {"messages": \[AIMessage(content="你好！")\]}
>
> \# 结果: {"messages": \[HumanMessage(...), AIMessage(...)\]}
>
> \# 示例：更新消息
>
> from langchain_core.messages import RemoveMessage
>
> state2 = {"messages": \[
>
> HumanMessage(content="你好", id="msg1"),
>
> AIMessage(content="旧的回复", id="msg2")
>
> \]}
>
> \# 节点返回 {"messages": \[AIMessage(content="新的回复", id="msg2")\]}
>
> \# 结果: {"messages": \[
>
> \# HumanMessage(content="你好", id="msg1"),
>
> \# AIMessage(content="新的回复", id="msg2") \# 被更新
>
> \# \]}
>
> \# 示例：删除消息
>
> \# 节点返回 {"messages": \[RemoveMessage(id="msg2")\]}
>
> \# 结果: {"messages": \[HumanMessage(content="你好", id="msg1")\]}

### **4.3.3 自定义 Reducer**

你可以定义自己的Reducer来实现复杂的合并逻辑。

> *// python*
>
> \# 自定义 Reducer
>
> from typing import Annotated
>
> def merge_dicts(left: dict, right: dict) -\> dict:
>
> """
>
> 合并两个字典
>
> 规则：
>
> 1\. 如果 key 只在 right 中，添加到 left
>
> 2\. 如果 key 在两者中都存在，right 的值覆盖 left
>
> 3\. 如果值是字典，递归合并
>
> """
>
> result = left.copy()
>
> for key, value in right.items():
>
> if key in result and isinstance(result\[key\], dict) and isinstance(value, dict):
>
> result\[key\] = merge_dicts(result\[key\], value)
>
> else:
>
> result\[key\] = value
>
> return result
>
> def append_unique(left: list, right: list) -\> list:
>
> """
>
> 追加唯一元素
>
> 规则：只追加 left 中不存在的元素
>
> """
>
> result = left.copy()
>
> for item in right:
>
> if item not in result:
>
> result.append(item)
>
> return result
>
> \# 使用自定义 Reducer
>
> class CustomState(TypedDict):
>
> \# 字典合并
>
> config: Annotated\[dict, merge_dicts\]
>
> \# 列表去重追加
>
> tags: Annotated\[list\[str\], append_unique\]
>
> def update_config_node(state: CustomState) -\> CustomState:
>
> return {
>
> "config": {"theme": "dark", "language": "zh"},
>
> "tags": \["important", "urgent"\]
>
> }
>
> \# 执行过程：
>
> \# 初始状态: {"config": {"theme": "light"}, "tags": \["important"\]}
>
> \# 节点返回: {"config": {"theme": "dark", "language": "zh"}, "tags": \["important", "urgent"\]}
>
> \# 结果: {"config": {"theme": "dark", "language": "zh"}, "tags": \["important", "urgent"\]}
>
> \# 注意：tags 中的 "important" 不会重复

## **4.4 状态设计最佳实践**

### **4.4.1 字段命名规范**

良好的命名是代码可读性的基础。以下是一些命名建议：

- 使用描述性名称：intent 比 i 好，confidence 比 c 好。

- 保持一致性：如果用 user_id 表示用户ID，就不要在其他地方用 userId 或 uid。

- 避免缩写：除非是广泛认可的缩写（如 id、url），否则使用完整单词。

- 使用复数表示列表：messages 表示消息列表，message 表示单条消息。

### **4.4.2 状态膨胀问题**

状态膨胀是指状态变得过大，影响性能和可维护性。常见原因和解决方案：

> *// python*
>
> \# 状态膨胀问题示例
>
> \# 问题 1：消息历史无限增长
>
> class BadChatState(TypedDict):
>
> messages: list\[BaseMessage\] \# 可能包含数百条消息
>
> \# 解决方案：消息裁剪
>
> def trim_messages(messages: list, max_count: int = 20) -\> list:
>
> """保留最近的消息"""
>
> if len(messages) \<= max_count:
>
> return messages
>
> \# 保留系统消息和最近的 N 条消息
>
> system_messages = \[m for m in messages if m.type == "system"\]
>
> recent_messages = messages\[-max_count:\]
>
> return system_messages + recent_messages
>
> \# 问题 2：存储大量临时数据
>
> class BadTaskState(TypedDict):
>
> all_intermediate_results: list\[dict\] \# 可能很大
>
> \# 解决方案：只保留必要数据
>
> class GoodTaskState(TypedDict):
>
> final_result: dict \# 只保留最终结果
>
> summary: str \# 摘要代替完整数据
>
> \# 问题 3：嵌套过深
>
> class BadNestedState(TypedDict):
>
> data: dict \# 嵌套很深的字典
>
> \# 解决方案：扁平化设计
>
> class FlatState(TypedDict):
>
> user_name: str
>
> user_email: str
>
> order_id: str
>
> order_status: str

### **4.4.3 可选字段处理**

状态中的可选字段需要特别处理，避免空值错误。

> *// python*
>
> \# 可选字段处理
>
> from typing import TypedDict
>
> class OptionalState(TypedDict):
>
> required_field: str \# 必填字段
>
> optional_field: str \| None \# 可选字段
>
> def safe_access_node(state: OptionalState) -\> OptionalState:
>
> \# 错误方式：直接访问可能为 None 的字段
>
> \# value = state\["optional_field"\].upper() \# 可能报错
>
> \# 正确方式 1：使用 get 方法提供默认值
>
> value = state.get("optional_field", "default").upper()
>
> \# 正确方式 2：先检查是否为 None
>
> if state.get("optional_field") is not None:
>
> value = state\["optional_field"\].upper()
>
> \# 正确方式 3：使用 or 运算符
>
> value = (state.get("optional_field") or "default").upper()
>
> return {"required_field": value}

## **4.5 本章交付物：设计一个完整的对话状态**

本章的交付物是设计一个完整的对话智能体状态，包含以下能力：

- 多轮对话：支持对话历史的累积和管理。

- 意图识别：记录当前意图和置信度。

- 用户信息：存储用户基本信息。

- 任务管理：跟踪任务状态和进度。

- 上下文保持：维护对话上下文。

> *// python*
>
> \# 完整的对话状态设计
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
> 完整的对话智能体状态
>
> 设计原则：
>
> 1\. 字段命名清晰
>
> 2\. 类型明确
>
> 3\. 支持多轮对话
>
> 4\. 便于调试和追踪
>
> """
>
> \# ========== 对话相关 ==========
>
> \# 对话历史（使用 add_messages reducer 自动管理）
>
> messages: Annotated\[list\[BaseMessage\], add_messages\]
>
> \# 当前意图
>
> current_intent: str \| None
>
> \# 意图置信度（0.0 - 1.0）
>
> intent_confidence: float
>
> \# ========== 用户相关 ==========
>
> \# 用户ID
>
> user_id: str
>
> \# 用户信息
>
> user_info: dict
>
> \# 用户偏好
>
> user_preferences: dict
>
> \# ========== 任务相关 ==========
>
> \# 任务类型
>
> task_type: str \| None
>
> \# 任务状态：pending, processing, completed, failed
>
> task_status: str
>
> \# 任务进度（0-100）
>
> task_progress: int
>
> \# 任务结果
>
> task_result: dict \| None
>
> \# ========== 上下文 ==========
>
> \# 对话上下文（实体、话题等）
>
> context: dict
>
> \# 上一次活动时间
>
> last_activity_time: float
>
> \# ========== 控制 ==========
>
> \# 是否需要人工介入
>
> need_human_intervention: bool
>
> \# 人工介入原因
>
> intervention_reason: str \| None
>
> \# ========== 元数据 ==========
>
> \# 会话ID
>
> session_id: str
>
> \# 其他元数据
>
> metadata: dict
>
> \# 使用示例
>
> initial_state: ConversationState = {
>
> "messages": \[\],
>
> "current_intent": None,
>
> "intent_confidence": 0.0,
>
> "user_id": "",
>
> "user_info": {},
>
> "user_preferences": {},
>
> "task_type": None,
>
> "task_status": "pending",
>
> "task_progress": 0,
>
> "task_result": None,
>
> "context": {},
>
> "last_activity_time": 0.0,
>
> "need_human_intervention": False,
>
> "intervention_reason": None,
>
> "session_id": "",
>
> "metadata": {}
>
> }

## **4.6 本章小结**

本章深入探讨了LangGraph的状态体系。关键要点包括：

- 状态是智能体的记忆，设计好坏直接影响系统可维护性。

- 推荐使用TypedDict定义状态，与LangGraph完美配合。

- Reducer机制定义了状态更新的方式，默认是覆盖，add_messages用于消息列表。

- 注意状态膨胀问题，定期裁剪不必要的数据。

- 可选字段需要安全处理，避免空值错误。

下一章将讨论节点设计，节点是状态的处理者。

## **4.7 课后练习**

练习 4.1（基础）：定义一个电商订单查询智能体的状态，包含订单信息、用户信息、查询历史。

练习 4.2（进阶）：实现一个自定义Reducer，用于合并两个列表并去重。

练习 4.3（挑战）：设计一个支持状态版本控制的系统，能够回滚到之前的状态。
