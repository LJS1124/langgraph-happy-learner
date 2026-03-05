# **第 6 章 Edge（边）与路由：控制流的显式化**

**📋 业务背景说明\**
Edge（边）就像是"交通指挥员"，决定智能体下一步该走哪条路：\
【交通指挥类比】\
• 用户问订单 → 走"订单查询"路线\
• 用户问产品 → 走"产品咨询"路线\
• 用户要投诉 → 走"人工客服"路线\
Edge解决的核心问题：\
• 根据业务规则动态选择执行路径\
• 实现智能路由，提高处理效率\
**🔄 业务逻辑流程\**
【条件路由流程】\
输入：当前状态\
处理：评估路由条件\
输出：下一个目标节点\
【业务场景示例】客服路由\
状态：{ "intent": "查询订单", "confidence": 0.95 }\
条件判断：\
• intent == "查询订单" → 订单查询节点\
• intent == "产品咨询" → 产品咨询节点\
• intent == "投诉" → 人工客服节点\
**📍 在整体系统中的位置\**
Edge是智能体系统的"决策中枢"：\
• 上游依赖：State提供决策数据\
• 当前模块：条件判断和路径选择\
• 下游影响：决定下一个执行的Node\
**💡 关键设计决策\**
【决策1】为什么用条件边而不是硬编码？\
• 业务原因：业务规则会变化，条件边让修改更灵活\
• 技术原因：解耦路由逻辑和业务逻辑\
【决策2】如何处理路由冲突？\
• 设置优先级：更具体的条件优先匹配\
• 设置默认路由：没有匹配时走默认路径\
**⚠️ 边界情况处理\**
• 多个条件同时满足：按优先级顺序匹配\
• 所有条件都不满足：走默认路由\
• 决策数据缺失：跳转到数据收集节点

<img src="LangGraph实战指南_assets/media/image3.png" style="width:5in;height:9.1344in" />

边（Edge）是LangGraph中定义节点之间连接关系的核心组件，它决定了数据流动的方向和执行顺序。与传统的隐式控制流不同，LangGraph通过显式定义边，使得控制逻辑清晰可见、易于理解和维护。本章将深入探讨边的设计，包括普通边、条件边、回环边以及路由策略。

## **6.1 为什么"显式边"优于隐式 if-else**

### **6.1.1 传统控制流的问题**

在传统的代码中，控制流通常通过if-else语句、循环语句、函数调用等方式表达。这种方式虽然灵活，但在复杂系统中容易变得难以理解和维护。让我们看一个具体的例子：

> *// python*
>
> \# 传统 if-else 控制流
>
> def process_request_implicit(state: dict) -\> dict:
>
> """
>
> 隐式控制流：if-else 嵌套
>
> 问题：
>
> 1\. 控制逻辑分散在代码中
>
> 2\. 难以看清完整的执行流程
>
> 3\. 添加新分支需要修改多处
>
> 4\. 测试需要覆盖所有分支组合
>
> """
>
> \# 第一层判断
>
> if state\["intent"\] == "search":
>
> \# 第二层判断
>
> if state.get("has_permission"):
>
> result = search_tool.invoke(state\["query"\])
>
> \# 第三层判断
>
> if result:
>
> \# 第四层判断
>
> if len(result) \> 10:
>
> return {"response": summarize(result)}
>
> else:
>
> return {"response": format(result)}
>
> else:
>
> return {"response": "未找到结果"}
>
> else:
>
> return {"response": "无权限"}
>
> elif state\["intent"\] == "calculate":
>
> \# 另一套嵌套逻辑
>
> if state.get("expression"):
>
> try:
>
> result = eval(state\["expression"\])
>
> return {"response": f"结果: {result}"}
>
> except:
>
> return {"response": "计算错误"}
>
> else:
>
> return {"response": "请提供表达式"}
>
> else:
>
> \# 默认处理
>
> return {"response": "无法处理"}
>
> \# 问题分析：
>
> \# 1. 要理解完整的执行流程，需要阅读整个函数
>
> \# 2. 嵌套层次深，容易出错
>
> \# 3. 添加新的 intent 类型，需要修改这个函数
>
> \# 4. 测试需要覆盖所有分支组合，测试用例数量爆炸

### **6.1.2 显式边的优势**

LangGraph的显式边将控制逻辑从代码中提取出来，以图的形式表达。这种方式的优势包括：

- 可读性强：图结构一目了然，可以快速理解执行流程。

- 易于调试：执行轨迹清晰，可以准确定位问题。

- 易于扩展：添加新节点和边，不影响现有逻辑。

- 易于测试：每个节点和路由函数可以独立测试。

- 支持静态分析：可以在编译时检测潜在问题。

> *// python*
>
> \# 显式边示例
>
> from typing import Literal
>
> from langgraph.graph import StateGraph, END
>
> \# 路由函数：控制逻辑集中管理
>
> def route_by_intent(state: dict) -\> Literal\["search", "calculate", "fallback"\]:
>
> """根据意图路由"""
>
> return state.get("intent", "fallback")
>
> def route_by_permission(state: dict) -\> Literal\["do_search", "no_permission"\]:
>
> """根据权限路由"""
>
> if state.get("has_permission"):
>
> return "do_search"
>
> return "no_permission"
>
> def route_by_result(state: dict) -\> Literal\["summarize", "format", "no_result"\]:
>
> """根据结果路由"""
>
> result = state.get("search_result")
>
> if not result:
>
> return "no_result"
>
> if len(result) \> 10:
>
> return "summarize"
>
> return "format"
>
> \# 构建图：控制流显式化
>
> builder = StateGraph(State)
>
> \# 添加节点
>
> builder.add_node("intent_router", intent_router_node)
>
> builder.add_node("search_permission_check", search_permission_node)
>
> builder.add_node("search", search_node)
>
> builder.add_node("summarize", summarize_node)
>
> builder.add_node("format", format_node)
>
> builder.add_node("calculate", calculate_node)
>
> builder.add_node("fallback", fallback_node)
>
> \# 设置入口点
>
> builder.set_entry_point("intent_router")
>
> \# 添加条件边：控制流显式定义
>
> builder.add_conditional_edges(
>
> "intent_router",
>
> route_by_intent,
>
> {
>
> "search": "search_permission_check",
>
> "calculate": "calculate",
>
> "fallback": "fallback"
>
> }
>
> )
>
> builder.add_conditional_edges(
>
> "search_permission_check",
>
> route_by_permission,
>
> {
>
> "do_search": "search",
>
> "no_permission": "fallback"
>
> }
>
> )
>
> builder.add_conditional_edges(
>
> "search",
>
> route_by_result,
>
> {
>
> "summarize": "summarize",
>
> "format": "format",
>
> "no_result": "fallback"
>
> }
>
> )
>
> \# 添加终止边
>
> builder.add_edge("summarize", END)
>
> builder.add_edge("format", END)
>
> builder.add_edge("calculate", END)
>
> builder.add_edge("fallback", END)
>
> \# 优势：
>
> \# 1. 图结构一目了然
>
> \# 2. 每个路由函数职责单一
>
> \# 3. 添加新分支只需添加节点和边
>
> \# 4. 每个节点和路由函数可以独立测试

### **6.1.3 静态分析能力**

显式边的另一个重要优势是支持静态分析。在编译图时，LangGraph可以检测以下问题：

- 孤立节点：没有入边或出边的节点。

- 不可达节点：从入口点无法到达的节点。

- 缺失路由目标：条件边的路由函数返回了未定义的目标。

- 类型不匹配：路由函数的返回类型与目标映射不匹配。

> *// python*
>
> \# 静态分析示例
>
> from typing import Literal
>
> \# 问题 1：孤立节点
>
> builder.add_node("orphan", orphan_node)
>
> \# 这个节点没有入边，永远不会被执行
>
> \# 问题 2：不可达节点
>
> builder.add_node("unreachable", unreachable_node)
>
> \# 这个节点没有从入口点到它的路径
>
> \# 问题 3：缺失路由目标
>
> def bad_router(state: dict) -\> str:
>
> return "nonexistent_node" \# 返回了不存在的节点
>
> builder.add_conditional_edges(
>
> "some_node",
>
> bad_router,
>
> {
>
> "existing_node": "existing_node"
>
> \# 缺少 "nonexistent_node" 的映射
>
> }
>
> )
>
> \# 问题 4：类型不匹配
>
> def typed_router(state: dict) -\> Literal\["a", "b"\]:
>
> return "a"
>
> builder.add_conditional_edges(
>
> "some_node",
>
> typed_router,
>
> {
>
> "a": "node_a",
>
> "b": "node_b",
>
> "c": "node_c" \# "c" 不在返回类型中
>
> }
>
> )
>
> \# LangGraph 会在编译时检测这些问题并报错

## **6.2 普通边 vs 条件边**

### **6.2.1 普通边**

普通边表示固定的连接关系：从源节点执行完后，一定执行目标节点。普通边适用于确定性的流程，不需要根据状态做决策。

> *// python*
>
> \# 普通边示例
>
> from langgraph.graph import StateGraph, END
>
> builder = StateGraph(State)
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
>
> \# 普通边的典型应用场景：
>
> \# 1. 线性流程：步骤 A 完成后必须执行步骤 B
>
> \# 2. 后处理：主逻辑完成后执行清理或日志记录
>
> \# 3. 固定转换：数据格式转换、结果格式化等

### **6.2.2 条件边**

条件边表示动态的连接关系：根据路由函数的返回值选择下一个节点。条件边适用于需要根据状态做决策的场景。

> *// python*
>
> \# 条件边示例
>
> from typing import Literal
>
> \# 路由函数
>
> def route_by_intent(state: dict) -\> Literal\["search", "chat", "fallback"\]:
>
> """
>
> 路由函数：决定下一个执行的节点
>
> 要求：
>
> 1\. 输入：当前状态
>
> 2\. 输出：下一个节点的名称（必须是 Literal 类型）
>
> 3\. 纯函数：相同输入产生相同输出
>
> """
>
> intent = state.get("intent", "unknown")
>
> if intent == "search":
>
> return "search"
>
> elif intent == "chat":
>
> return "chat"
>
> else:
>
> return "fallback"
>
> \# 构建图
>
> builder = StateGraph(State)
>
> builder.add_node("intent_router", intent_router_node)
>
> builder.add_node("search", search_node)
>
> builder.add_node("chat", chat_node)
>
> builder.add_node("fallback", fallback_node)
>
> builder.set_entry_point("intent_router")
>
> \# 添加条件边
>
> builder.add_conditional_edges(
>
> "intent_router", \# 源节点
>
> route_by_intent, \# 路由函数
>
> {
>
> \# 路由函数返回值 -\> 目标节点
>
> "search": "search",
>
> "chat": "chat",
>
> "fallback": "fallback"
>
> }
>
> )
>
> \# 每个分支的后续流程
>
> builder.add_edge("search", END)
>
> builder.add_edge("chat", END)
>
> builder.add_edge("fallback", END)
>
> \# 条件边的典型应用场景：
>
> \# 1. 意图路由：根据用户意图分发到不同的处理模块
>
> \# 2. 错误处理：根据错误类型选择恢复策略
>
> \# 3. 质量检查：根据检查结果决定是否继续或重试

### **6.2.3 路由函数设计原则**

路由函数是条件边的核心，它的设计需要遵循以下原则：

- 返回类型必须是 Literal：明确列出所有可能的返回值。

- 必须是纯函数：相同输入产生相同输出，没有副作用。

- 逻辑要简单：复杂的决策逻辑应该放在节点中。

- 要有默认分支：处理未知或异常情况。

> *// python*
>
> \# 路由函数设计示例
>
> \# 好的设计：简单、明确、有默认分支
>
> def good_router(state: dict) -\> Literal\["a", "b", "c", "default"\]:
>
> value = state.get("key", "")
>
> if value == "x":
>
> return "a"
>
> elif value == "y":
>
> return "b"
>
> elif value == "z":
>
> return "c"
>
> else:
>
> return "default" \# 默认分支
>
> \# 不好的设计：复杂逻辑、无默认分支
>
> def bad_router(state: dict) -\> str: \# 返回类型不明确
>
> \# 复杂的决策逻辑（应该放在节点中）
>
> if state.get("a") and state.get("b"):
>
> if state.get("c") \> 10:
>
> return "node_x"
>
> else:
>
> return "node_y"
>
> elif state.get("d"):
>
> return "node_z"
>
> \# 没有默认分支，可能返回 None
>
> \# 使用枚举提高可读性
>
> from enum import Enum
>
> class RouteTarget(str, Enum):
>
> SEARCH = "search"
>
> CHAT = "chat"
>
> FALLBACK = "fallback"
>
> def enum_router(state: dict) -\> RouteTarget:
>
> intent = state.get("intent", "unknown")
>
> if intent == "search":
>
> return RouteTarget.SEARCH
>
> elif intent == "chat":
>
> return RouteTarget.CHAT
>
> else:
>
> return RouteTarget.FALLBACK

## **6.3 回环边：迭代推理与自我修正**

回环边是指将边指向之前的节点，形成循环。这是LangGraph的一个强大特性，支持迭代推理、自我修正等高级模式。

### **6.3.1 迭代推理模式**

迭代推理是指智能体通过多轮思考逐步解决问题的模式。每轮思考都会更新状态，直到达到终止条件。

> *// python*
>
> \# 迭代推理示例
>
> from typing import Literal
>
> class ReasoningState(TypedDict):
>
> question: str
>
> thoughts: list\[str\]
>
> answer: str \| None
>
> iterations: int
>
> done: bool
>
> def think_node(state: ReasoningState) -\> ReasoningState:
>
> """思考节点：生成下一步思考"""
>
> previous_thoughts = "\n".join(state\["thoughts"\])
>
> thought = llm.invoke(
>
> f"问题：{state\['question'\]}\n"
>
> f"之前的思考：{previous_thoughts}\n"
>
> f"请继续思考，逐步解决问题。"
>
> )
>
> return {
>
> "thoughts": state\["thoughts"\] + \[thought.content\],
>
> "iterations": state\["iterations"\] + 1
>
> }
>
> def answer_node(state: ReasoningState) -\> ReasoningState:
>
> """回答节点：生成最终答案"""
>
> all_thoughts = "\n".join(state\["thoughts"\])
>
> answer = llm.invoke(
>
> f"问题：{state\['question'\]}\n"
>
> f"思考过程：{all_thoughts}\n"
>
> f"请给出最终答案。"
>
> )
>
> return {
>
> "answer": answer.content,
>
> "done": True
>
> }
>
> def should_continue(state: ReasoningState) -\> Literal\["think", "answer"\]:
>
> """决定是否继续思考"""
>
> \# 如果已经有答案，结束
>
> if state.get("done"):
>
> return "answer"
>
> \# 如果迭代次数超过限制，生成答案
>
> if state\["iterations"\] \>= 5:
>
> return "answer"
>
> \# 如果最后一个思考包含"答案"，生成答案
>
> if state\["thoughts"\] and "答案" in state\["thoughts"\]\[-1\]:
>
> return "answer"
>
> \# 否则继续思考
>
> return "think"
>
> \# 构建图
>
> builder = StateGraph(ReasoningState)
>
> builder.add_node("think", think_node)
>
> builder.add_node("answer", answer_node)
>
> builder.set_entry_point("think")
>
> \# 回环边：think -\> think 或 think -\> answer
>
> builder.add_conditional_edges(
>
> "think",
>
> should_continue,
>
> {
>
> "think": "think", \# 回环
>
> "answer": "answer"
>
> }
>
> )
>
> builder.add_edge("answer", END)

### **6.3.2 自我修正模式**

自我修正是指智能体检查自己的输出，如果不满足要求则重新生成。这种模式可以提高输出质量。

> *// python*
>
> \# 自我修正示例
>
> class WritingState(TypedDict):
>
> topic: str
>
> draft: str \| None
>
> feedback: str \| None
>
> iterations: int
>
> approved: bool
>
> def write_node(state: WritingState) -\> WritingState:
>
> """写作节点：生成或修改草稿"""
>
> if state\["iterations"\] == 0:
>
> \# 第一次写作
>
> draft = llm.invoke(f"写一篇关于 {state\['topic'\]} 的文章")
>
> else:
>
> \# 根据反馈修改
>
> draft = llm.invoke(
>
> f"根据反馈修改文章：\n"
>
> f"原稿：{state\['draft'\]}\n"
>
> f"反馈：{state\['feedback'\]}"
>
> )
>
> return {"draft": draft.content}
>
> def review_node(state: WritingState) -\> WritingState:
>
> """审核节点：评估草稿质量"""
>
> feedback = llm.invoke(
>
> f"审核以下文章并提出修改建议：\n{state\['draft'\]}"
>
> )
>
> \# 检查是否通过
>
> approved = "无需修改" in feedback.content or "通过" in feedback.content
>
> return {
>
> "feedback": feedback.content,
>
> "approved": approved,
>
> "iterations": state\["iterations"\] + 1
>
> }
>
> def should_revise(state: WritingState) -\> Literal\["revise", "end"\]:
>
> """决定是否需要修改"""
>
> \# 如果已通过审核，结束
>
> if state.get("approved"):
>
> return "end"
>
> \# 如果迭代次数超过限制，结束
>
> if state\["iterations"\] \>= 3:
>
> return "end"
>
> \# 否则继续修改
>
> return "revise"
>
> \# 构建图
>
> builder = StateGraph(WritingState)
>
> builder.add_node("write", write_node)
>
> builder.add_node("review", review_node)
>
> builder.set_entry_point("write")
>
> builder.add_edge("write", "review")
>
> \# 回环边：review -\> write 或 review -\> END
>
> builder.add_conditional_edges(
>
> "review",
>
> should_revise,
>
> {
>
> "revise": "write", \# 回环到 write
>
> "end": END
>
> }
>
> )

### **6.3.3 避免无限循环**

> **⚠️ 终止条件设计**
>
> 回环边必须有明确的终止条件。常见的终止条件包括：迭代次数限制、质量达标、时间限制、状态不变检测。建议始终设置迭代次数限制作为最后的保障。
>
> *// python*
>
> \# 终止条件设计示例
>
> from typing import Literal
>
> import time
>
> class LoopState(TypedDict):
>
> iterations: int
>
> max_iterations: int
>
> start_time: float
>
> max_time: float \# 秒
>
> previous_state: dict
>
> converged: bool
>
> def should_continue(state: LoopState) -\> Literal\["continue", "end"\]:
>
> """综合终止条件"""
>
> \# 条件 1：迭代次数限制（必须）
>
> if state\["iterations"\] \>= state\["max_iterations"\]:
>
> return "end"
>
> \# 条件 2：时间限制
>
> elapsed = time.time() - state\["start_time"\]
>
> if elapsed \>= state\["max_time"\]:
>
> return "end"
>
> \# 条件 3：收敛检测（状态不再变化）
>
> if state.get("converged"):
>
> return "end"
>
> \# 条件 4：质量达标
>
> if state.get("quality_score", 0) \>= 0.9:
>
> return "end"
>
> return "continue"
>
> \# 使用示例
>
> initial_state: LoopState = {
>
> "iterations": 0,
>
> "max_iterations": 10, \# 最多迭代 10 次
>
> "start_time": time.time(),
>
> "max_time": 60.0, \# 最多执行 60 秒
>
> "previous_state": {},
>
> "converged": False
>
> }

## **6.4 本章交付物：一个带条件边和回环边的图**

本章的交付物是一个包含条件边和回环边的图，展示了迭代改进的模式。

> *// python*
>
> """
>
> chapter6_demo.py - 第 6 章示例：条件边 + 回环边
>
> 展示了迭代改进的模式
>
> """
>
> from typing import TypedDict, Literal
>
> from langgraph.graph import StateGraph, END
>
> \# ============================================
>
> \# 状态定义
>
> \# ============================================
>
> class ImprovementState(TypedDict):
>
> """迭代改进状态"""
>
> task: str \# 任务描述
>
> current_output: str \# 当前输出
>
> feedback: str \# 反馈
>
> iterations: int \# 迭代次数
>
> quality_score: float \# 质量分数
>
> done: bool \# 是否完成
>
> \# ============================================
>
> \# 节点定义
>
> \# ============================================
>
> def generate_node(state: ImprovementState) -\> ImprovementState:
>
> """生成节点：生成或改进输出"""
>
> if state\["iterations"\] == 0:
>
> \# 第一次生成
>
> output = f"初始输出: {state\['task'\]}"
>
> else:
>
> \# 根据反馈改进
>
> output = f"改进输出 (迭代 {state\['iterations'\]}): {state\['feedback'\]}"
>
> return {
>
> "current_output": output,
>
> "iterations": state\["iterations"\] + 1
>
> }
>
> def evaluate_node(state: ImprovementState) -\> ImprovementState:
>
> """评估节点：评估输出质量"""
>
> \# 模拟质量评估
>
> \# 实际应用中会使用 LLM 或其他评估方法
>
> quality_score = min(0.9, 0.3 + state\["iterations"\] \* 0.2)
>
> if quality_score \>= 0.8:
>
> feedback = "质量达标"
>
> else:
>
> feedback = f"需要改进 (当前分数: {quality_score:.1f})"
>
> return {
>
> "quality_score": quality_score,
>
> "feedback": feedback
>
> }
>
> \# ============================================
>
> \# 路由函数
>
> \# ============================================
>
> def should_continue(state: ImprovementState) -\> Literal\["improve", "end"\]:
>
> """
>
> 决定是否继续改进
>
> 终止条件：
>
> 1\. 质量分数 \>= 0.8
>
> 2\. 迭代次数 \>= 5
>
> """
>
> \# 质量达标
>
> if state\["quality_score"\] \>= 0.8:
>
> return "end"
>
> \# 迭代次数限制
>
> if state\["iterations"\] \>= 5:
>
> return "end"
>
> \# 继续改进
>
> return "improve"
>
> \# ============================================
>
> \# 图构建
>
> \# ============================================
>
> def build_improvement_graph():
>
> builder = StateGraph(ImprovementState)
>
> \# 添加节点
>
> builder.add_node("generate", generate_node)
>
> builder.add_node("evaluate", evaluate_node)
>
> \# 设置入口点
>
> builder.set_entry_point("generate")
>
> \# 添加普通边
>
> builder.add_edge("generate", "evaluate")
>
> \# 添加条件边（包含回环）
>
> builder.add_conditional_edges(
>
> "evaluate",
>
> should_continue,
>
> {
>
> "improve": "generate", \# 回环到 generate
>
> "end": END
>
> }
>
> )
>
> return builder
>
> \# ============================================
>
> \# 测试
>
> \# ============================================
>
> def test_improvement_graph():
>
> graph = build_improvement_graph().compile()
>
> result = graph.invoke({
>
> "task": "写一篇文章",
>
> "current_output": "",
>
> "feedback": "",
>
> "iterations": 0,
>
> "quality_score": 0.0,
>
> "done": False
>
> })
>
> print("=" \* 50)
>
> print("迭代改进结果")
>
> print("=" \* 50)
>
> print(f"最终输出: {result\['current_output'\]}")
>
> print(f"质量分数: {result\['quality_score'\]}")
>
> print(f"迭代次数: {result\['iterations'\]}")
>
> print(f"反馈: {result\['feedback'\]}")
>
> if \_\_name\_\_ == "\_\_main\_\_":
>
> test_improvement_graph()

## **6.5 本章小结**

本章深入探讨了LangGraph的边设计，包括普通边、条件边、回环边以及路由策略。关键要点包括：

- 显式边优于隐式 if-else：控制流清晰可见，易于理解和维护。

- 普通边用于固定流程，条件边用于动态决策。

- 路由函数要简单、纯函数、有默认分支。

- 回环边支持迭代推理和自我修正，但必须有终止条件。

下一章将讨论图的构建和执行，这是将所有组件组织起来的最后一步。

## **6.6 课后练习**

练习 6.1（基础）：修改示例代码，添加一个新的路由分支，当质量分数在 0.5-0.7 之间时，使用"轻度改进"策略。

练习 6.2（进阶）：实现一个并行搜索图，同时从多个数据源搜索，然后合并结果。

练习 6.3（挑战）：设计一个支持"人工介入"的迭代改进图，当自动改进无法达到质量标准时，请求人工提供反馈。
