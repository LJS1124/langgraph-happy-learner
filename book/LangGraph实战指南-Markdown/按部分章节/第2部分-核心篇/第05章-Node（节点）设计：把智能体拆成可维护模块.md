# **第 5 章 Node（节点）设计：把智能体拆成可维护模块**

**📋 业务背景说明\**
Node（节点）就像是工厂里的"工位"，每个工位负责特定的任务：\
【工厂类比】\
• 工位A（接待节点）：接收请求，识别意图\
• 工位B（处理节点）：执行具体业务逻辑\
• 工位C（输出节点）：生成最终响应\
Node解决的核心问题：\
• 将复杂的智能体系统拆分成可管理的功能模块\
• 每个模块职责单一，便于开发和维护\
**🔄 业务逻辑流程\**
【节点处理流程】\
输入：当前状态（从State获取）\
处理：执行节点业务逻辑\
输出：状态更新指令（返回给State）\
【业务场景示例】订单查询节点\
输入状态：{ "user_id": "u123", "order_id": "o456" }\
处理逻辑：验证权限 → 调用API → 格式化结果\
输出更新：{ "order_status": "配送中", "eta": "明天" }\
**📍 在整体系统中的位置\**
Node是智能体系统的"功能执行单元"：\
• 上游依赖：State提供输入数据\
• 当前模块：执行特定业务逻辑\
• 下游影响：更新State，触发下一个Node\
**💡 关键设计决策\**
【决策1】为什么每个Node只做一件事？\
• 业务原因：职责清晰，出问题容易定位\
• 技术原因：便于单元测试，降低耦合度\
【决策2】Node之间如何通信？\
• 通过State共享数据，避免直接依赖\
**⚠️ 边界情况处理\**
• 执行超时：设置超时时间，超时后返回默认响应\
• 服务不可用：实现降级策略\
• 执行出错：捕获异常，根据错误类型决定重试或跳过

<img src="LangGraph实战指南_assets/media/image2.png" style="width:5in;height:9.0873in" />

节点是LangGraph图的基本处理单元，每个节点负责一个明确的任务。良好的节点设计是构建可维护、可测试、可扩展智能体系统的关键。本章将深入探讨节点设计的各个方面。

## **5.1 节点的职责边界：单一职责原则**

### **5.1.1 为什么单一职责很重要**

单一职责原则（Single Responsibility Principle, SRP）是软件设计的基本原则之一。在节点设计中，它意味着每个节点应该只负责一个明确的任务。这样做的好处是：

- 易于理解：每个节点的功能单一，代码量少，容易理解。

- 易于测试：只需要测试一个功能，测试用例简单。

- 易于复用：功能单一的节点更容易在不同场景中复用。

- 易于维护：修改一个功能不会影响其他功能。

### **5.1.2 违反单一职责的例子**

> *// python*
>
> \# 违反单一职责的节点
>
> def bad_node(state: dict) -\> dict:
>
> """
>
> 问题节点：做了太多事情
>
> 这个节点同时负责：
>
> 1\. 意图识别
>
> 2\. 工具调用
>
> 3\. 结果处理
>
> 4\. 错误处理
>
> 问题：
>
> \- 代码冗长，难以理解
>
> \- 难以测试，需要模拟多个依赖
>
> \- 难以复用，逻辑耦合在一起
>
> \- 修改一个功能可能影响其他功能
>
> """
>
> \# 意图识别
>
> intent = llm.invoke(f"识别意图: {state\['messages'\]\[-1\]}")
>
> \# 工具调用
>
> if "搜索" in intent:
>
> result = search_tool.invoke(state\['messages'\]\[-1\])
>
> elif "计算" in intent:
>
> result = calculator_tool.invoke(state\['messages'\]\[-1\])
>
> else:
>
> result = None
>
> \# 结果处理
>
> if result:
>
> response = llm.invoke(f"处理结果: {result}")
>
> else:
>
> response = llm.invoke(f"直接回答: {state\['messages'\]\[-1\]}")
>
> \# 错误处理
>
> try:
>
> \# 一些可能失败的操作
>
> pass
>
> except Exception as e:
>
> \# 错误处理逻辑
>
> pass
>
> return {
>
> "intent": intent,
>
> "tool_result": result,
>
> "response": response
>
> }

### **5.1.3 遵循单一职责的例子**

> *// python*
>
> \# 遵循单一职责的节点
>
> \# 节点 1：意图识别
>
> def intent_recognition_node(state: dict) -\> dict:
>
> """
>
> 意图识别节点
>
> 职责：只负责识别用户意图
>
> 输入：messages
>
> 输出：intent, confidence
>
> """
>
> last_message = state\["messages"\]\[-1\].content
>
> \# 调用 LLM 进行意图识别
>
> prompt = f"识别以下消息的意图（搜索/计算/聊天）: {last_message}"
>
> result = llm.invoke(prompt)
>
> \# 解析结果
>
> intent = parse_intent(result.content)
>
> confidence = calculate_confidence(result.content)
>
> return {
>
> "intent": intent,
>
> "confidence": confidence
>
> }
>
> \# 节点 2：工具调用
>
> def tool_calling_node(state: dict) -\> dict:
>
> """
>
> 工具调用节点
>
> 职责：只负责调用工具
>
> 输入：intent, messages
>
> 输出：tool_result
>
> """
>
> intent = state.get("intent", "")
>
> last_message = state\["messages"\]\[-1\].content
>
> if intent == "search":
>
> result = search_tool.invoke(last_message)
>
> elif intent == "calculate":
>
> result = calculator_tool.invoke(last_message)
>
> else:
>
> result = None
>
> return {"tool_result": result}
>
> \# 节点 3：响应生成
>
> def response_generation_node(state: dict) -\> dict:
>
> """
>
> 响应生成节点
>
> 职责：只负责生成最终响应
>
> 输入：messages, tool_result
>
> 输出：response
>
> """
>
> tool_result = state.get("tool_result")
>
> last_message = state\["messages"\]\[-1\].content
>
> if tool_result:
>
> prompt = f"根据搜索结果回答: {tool_result}"
>
> else:
>
> prompt = f"回答问题: {last_message}"
>
> response = llm.invoke(prompt)
>
> return {"response": response.content}
>
> \# 在图中组合这些节点
>
> builder = StateGraph(State)
>
> builder.add_node("intent", intent_recognition_node)
>
> builder.add_node("tool", tool_calling_node)
>
> builder.add_node("response", response_generation_node)
>
> builder.set_entry_point("intent")
>
> builder.add_edge("intent", "tool")
>
> builder.add_edge("tool", "response")
>
> builder.add_edge("response", END)

通过职责分离，每个节点都有明确的功能。当需要修改意图识别逻辑时，只需要修改 intent_recognition_node，不会影响其他节点。

## **5.2 节点类型详解**

### **5.2.1 LLM 节点**

LLM节点是最常见的节点类型，它调用大语言模型进行推理或生成。设计LLM节点时，需要考虑提示词管理、输出解析、错误处理等问题。

> *// python*
>
> \# LLM 节点模板
>
> from langchain_openai import ChatOpenAI
>
> from langchain_core.prompts import ChatPromptTemplate
>
> from langchain_core.messages import BaseMessage
>
> class LLMNode:
>
> """
>
> LLM 节点模板
>
> 特点：
>
> 1\. 提示词与代码分离
>
> 2\. 支持流式输出
>
> 3\. 错误处理
>
> 4\. 可配置的模型参数
>
> """
>
> def \_\_init\_\_(
>
> self,
>
> model: str = "gpt-4o",
>
> temperature: float = 0.7,
>
> system_prompt: str = "你是一个有帮助的助手。"
>
> ):
>
> self.llm = ChatOpenAI(model=model, temperature=temperature)
>
> self.system_prompt = system_prompt
>
> self.prompt = ChatPromptTemplate.from_messages(\[
>
> ("system", system_prompt),
>
> ("placeholder", "{messages}")
>
> \])
>
> self.chain = self.prompt \| self.llm
>
> def \_\_call\_\_(self, state: dict) -\> dict:
>
> """执行 LLM 调用"""
>
> try:
>
> \# 调用 LLM
>
> response = self.chain.invoke(state)
>
> \# 返回结果
>
> return {"messages": \[response\]}
>
> except Exception as e:
>
> \# 错误处理
>
> return {
>
> "error": str(e),
>
> "error_type": type(e).\_\_name\_\_
>
> }
>
> \# 使用示例
>
> chat_node = LLMNode(
>
> model="gpt-4o",
>
> temperature=0.7,
>
> system_prompt="你是一个专业的客服代表。请用简洁、友好的方式回答用户问题。"
>
> )
>
> \# 在图中使用
>
> builder.add_node("chat", chat_node)

### **5.2.2 工具节点**

工具节点负责调用外部工具或API。设计工具节点时，需要考虑输入验证、超时处理、结果解析等问题。

> *// python*
>
> \# 工具节点模板
>
> from langchain_core.tools import tool
>
> from typing import Any
>
> class ToolNode:
>
> """
>
> 工具节点模板
>
> 特点：
>
> 1\. 工具注册机制
>
> 2\. 输入验证
>
> 3\. 超时处理
>
> 4\. 错误处理
>
> """
>
> def \_\_init\_\_(self, tools: list, timeout: float = 30.0):
>
> self.tools = {t.name: t for t in tools}
>
> self.timeout = timeout
>
> def \_\_call\_\_(self, state: dict) -\> dict:
>
> """执行工具调用"""
>
> tool_calls = state.get("tool_calls", \[\])
>
> results = \[\]
>
> for call in tool_calls:
>
> tool_name = call\["name"\]
>
> tool_args = call\["args"\]
>
> call_id = call.get("id", "unknown")
>
> \# 检查工具是否存在
>
> if tool_name not in self.tools:
>
> results.append({
>
> "tool_call_id": call_id,
>
> "error": f"Unknown tool: {tool_name}"
>
> })
>
> continue
>
> \# 执行工具调用
>
> try:
>
> tool = self.tools\[tool_name\]
>
> result = tool.invoke(tool_args)
>
> results.append({
>
> "tool_call_id": call_id,
>
> "result": result,
>
> "success": True
>
> })
>
> except Exception as e:
>
> results.append({
>
> "tool_call_id": call_id,
>
> "error": str(e),
>
> "success": False
>
> })
>
> return {"tool_results": results}
>
> \# 定义工具
>
> @tool
>
> def search_web(query: str) -\> str:
>
> """搜索互联网获取信息"""
>
> \# 实际实现会调用搜索 API
>
> return f"搜索结果: {query}"
>
> @tool
>
> def calculate(expression: str) -\> str:
>
> """计算数学表达式"""
>
> try:
>
> result = eval(expression)
>
> return f"结果: {result}"
>
> except Exception as e:
>
> return f"计算错误: {str(e)}"
>
> \# 使用示例
>
> tool_node = ToolNode(tools=\[search_web, calculate\])

### **5.2.3 路由节点**

路由节点负责根据状态决定下一步执行哪个节点。路由节点通常不修改状态，只返回路由决策。

> *// python*
>
> \# 路由节点模板
>
> from typing import Literal
>
> def router_node(state: dict) -\> dict:
>
> """
>
> 路由节点：根据意图决定下一步
>
> 职责：
>
> 1\. 分析当前状态
>
> 2\. 决定下一个节点
>
> 3\. 不修改状态（只读取）
>
> 注意：路由节点本身不返回路由决策，
>
> 路由决策由路由函数返回。
>
> """
>
> \# 路由节点可以做一些预处理
>
> \# 但通常不需要修改状态
>
> return {}
>
> def route_by_intent(state: dict) -\> Literal\["search", "chat", "fallback"\]:
>
> """
>
> 路由函数：决定下一个节点
>
> 要求：
>
> 1\. 返回类型必须是 Literal
>
> 2\. 返回值必须与条件边的映射匹配
>
> 3\. 逻辑要简单，复杂决策应该放在节点中
>
> """
>
> intent = state.get("intent", "unknown")
>
> \# 意图映射
>
> intent_map = {
>
> "search": "search",
>
> "query": "search",
>
> "chat": "chat",
>
> "greeting": "chat"
>
> }
>
> return intent_map.get(intent, "fallback")
>
> \# 在图中使用
>
> builder.add_conditional_edges(
>
> "intent_router",
>
> route_by_intent,
>
> {
>
> "search": "search_agent",
>
> "chat": "chat_agent",
>
> "fallback": "fallback_agent"
>
> }
>
> )

## **5.3 节点设计最佳实践**

### **5.3.1 幂等性设计**

节点应该是幂等的，即多次执行同一节点，结果应该相同。这对于重试机制和错误恢复非常重要。

> *// python*
>
> \# 幂等性设计
>
> \# 不幂等的节点
>
> def non_idempotent_node(state: dict) -\> dict:
>
> """
>
> 不幂等的节点：每次调用都会产生不同的副作用
>
> """
>
> \# 问题：每次调用都会发送邮件
>
> send_email(state\["user_email"\], "通知")
>
> return {"notified": True}
>
> \# 幂等的节点
>
> def idempotent_node(state: dict) -\> dict:
>
> """
>
> 幂等的节点：多次调用结果相同
>
> """
>
> \# 检查是否已经通知过
>
> if state.get("notified"):
>
> return {} \# 已经通知过，跳过
>
> \# 发送通知
>
> send_email(state\["user_email"\], "通知")
>
> return {"notified": True}

### **5.3.2 错误处理**

节点应该有完善的错误处理机制，避免因为单个节点的错误导致整个系统崩溃。

> *// python*
>
> \# 错误处理
>
> def robust_node(state: dict) -\> dict:
>
> """
>
> 健壮的节点：包含完善的错误处理
>
> """
>
> try:
>
> \# 主要逻辑
>
> result = process(state)
>
> return {"result": result, "error": None}
>
> except ValidationError as e:
>
> \# 验证错误：不重试
>
> return {
>
> "error": str(e),
>
> "error_type": "validation",
>
> "retryable": False
>
> }
>
> except TimeoutError as e:
>
> \# 超时错误：可以重试
>
> return {
>
> "error": str(e),
>
> "error_type": "timeout",
>
> "retryable": True
>
> }
>
> except Exception as e:
>
> \# 未知错误：记录并降级
>
> logger.error(f"Unknown error: {e}")
>
> return {
>
> "error": str(e),
>
> "error_type": "unknown",
>
> "retryable": False
>
> }

## **5.4 本章交付物：实现"规划 → 执行 → 总结"三节点**

本章的交付物是一个包含三个节点的简单工作流：规划节点生成任务计划，执行节点执行计划，总结节点生成总结报告。

> *// python*
>
> \# 规划-执行-总结三节点
>
> from typing import TypedDict
>
> from langchain_openai import ChatOpenAI
>
> class WorkflowState(TypedDict):
>
> user_request: str
>
> plan: list\[str\]
>
> execution_results: list\[str\]
>
> summary: str
>
> \# 规划节点
>
> def planning_node(state: WorkflowState) -\> WorkflowState:
>
> """规划节点：生成任务计划"""
>
> llm = ChatOpenAI(model="gpt-4o")
>
> prompt = f"""
>
> 为以下请求制定执行计划，分解为具体步骤：
>
> {state\['user_request'\]}
>
> 返回 JSON 格式的任务列表。
>
> """
>
> response = llm.invoke(prompt)
>
> plan = parse_plan(response.content)
>
> return {"plan": plan}
>
> \# 执行节点
>
> def execution_node(state: WorkflowState) -\> WorkflowState:
>
> """执行节点：执行任务计划"""
>
> results = \[\]
>
> for task in state\["plan"\]:
>
> \# 执行每个任务
>
> result = execute_task(task)
>
> results.append(result)
>
> return {"execution_results": results}
>
> \# 总结节点
>
> def summary_node(state: WorkflowState) -\> WorkflowState:
>
> """总结节点：生成总结报告"""
>
> llm = ChatOpenAI(model="gpt-4o")
>
> prompt = f"""
>
> 根据以下执行结果生成总结报告：
>
> {state\['execution_results'\]}
>
> """
>
> response = llm.invoke(prompt)
>
> return {"summary": response.content}
>
> \# 构建图
>
> builder = StateGraph(WorkflowState)
>
> builder.add_node("planning", planning_node)
>
> builder.add_node("execution", execution_node)
>
> builder.add_node("summary", summary_node)
>
> builder.set_entry_point("planning")
>
> builder.add_edge("planning", "execution")
>
> builder.add_edge("execution", "summary")
>
> builder.add_edge("summary", END)

## **5.5 本章小结**

本章深入探讨了LangGraph的节点设计。关键要点包括：

- 遵循单一职责原则，每个节点只负责一个明确的任务。

- 理解不同类型节点的设计模式：LLM节点、工具节点、路由节点。

- 节点应该是幂等的，支持重试和错误恢复。

- 节点应该有完善的错误处理机制。

下一章将讨论边的设计，边定义了节点之间的连接关系。

## **5.6 课后练习**

练习 5.1（基础）：为 planning_node 添加输入验证，确保 user_request 不为空。

练习 5.2（进阶）：实现一个带重试机制的 execution_node，当某个任务失败时自动重试最多 3 次。

练习 5.3（挑战）：设计一个支持并行执行的 execution_node，可以同时执行多个独立的任务。

|                     |           |              |
|---------------------|-----------|--------------|
| 场景                | 推荐方案  | 理由         |
| 简单项目            | TypedDict | 轻量、简单   |
| 需要运行时验证      | Pydantic  | 自动验证     |
| 与LangGraph深度集成 | TypedDict | 官方推荐     |
| 复杂数据模型        | Pydantic  | 丰富的验证器 |
