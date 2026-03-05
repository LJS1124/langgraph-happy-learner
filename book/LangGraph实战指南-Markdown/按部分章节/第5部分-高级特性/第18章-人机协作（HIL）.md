# **第 18 章 人机协作（HIL）**

**📋 业务背景说明\**
人机协作让AI知道"什么时候该问人"：\
【业务场景】\
客服系统中的典型场景：\
• 用户要退款 → 金额小：自动处理\
• 用户要退款 → 金额大：需要人工审批\
• 用户投诉 → 情绪激动：转人工安抚\
• 敏感操作 → 需要人工确认\
人机协作解决的核心问题：\
• AI能力边界识别\
• 关键决策人工把关\
• 提升用户信任度\
**🔄 业务逻辑流程\**
【人机协作流程】\
┌─────────────────────────────────────────┐\
│ 智能体执行 → 检测需要人工 → 发起中断 │\
│ ↓ │\
│ 等待人工输入 │\
│ ↓ │\
│ 人工处理完成 → 恢复执行 │\
└─────────────────────────────────────────┘\
【业务场景示例】退款处理\
用户："我要退款"\
→ 智能体：查询订单金额 = 5000元\
→ 判断：金额 \> 1000元，需要人工审批\
→ 中断：等待人工审批\
→ 人工：审批通过\
→ 恢复：继续执行退款流程\
**📍 在整体系统中的位置\**
人机协作层：\
┌─────────────────────────────────────────┐\
│ 智能体执行层 │\
│ • 正常执行 • 检测中断点 • 等待恢复 │\
└─────────────────┬───────────────────────┘\
↓\
┌─────────────────────────────────────────┐\
│ 人机协作层 │\
│ • 中断管理 • 状态保存 • 恢复机制 │\
└─────────────────────────────────────────┘\
**💡 关键设计决策\**
【决策1】哪些场景需要人工介入？\
• 高风险操作：大额退款、敏感数据\
• AI能力不足：复杂问题、新场景\
• 用户主动要求：投诉、特殊需求\
【决策2】如何设计等待体验？\
• 显示等待状态\
• 预估等待时间\
• 提供取消选项\
**⚠️ 边界情况处理\**
• 人工长时间不响应：超时提醒\
• 用户取消等待：恢复后引导其他方案\
• 中断状态丢失：从检查点恢复

<img src="LangGraph实战指南_assets/media/image16.png" style="width:2.86042in;height:7.525in" />

人机协作（Human-in-the-Loop, HIL）是智能体系统的重要特性，它允许在关键决策点暂停执行，等待人工介入。本章将详细介绍如何设计和实现HIL功能。

## **18.1 HIL 的典型场景**

HIL适用于以下场景：

- 高风险操作审批：如删除数据、转账、修改配置等，需要人工确认。

- 敏感内容审核：如发布内容、发送邮件等，需要人工审核。

- 质量把控：如重要输出、客户回复等，需要人工质检。

- 知识补充：当智能体知识不足时，请求人工提供信息。

- 异常处理：当遇到无法处理的情况时，升级人工处理。

## **18.2 interrupt 的使用方法**

### **18.2.1 基本用法**

> *// python*
>
> \# interrupt 基本用法
>
> from langgraph.types import interrupt
>
> from langgraph.graph import StateGraph, END
>
> class ApprovalState(TypedDict):
>
> request: str
>
> approved: bool \| None
>
> result: str \| None
>
> def approval_node(state: ApprovalState) -\> ApprovalState:
>
> """审批节点"""
>
> \# 发起中断，等待人工审批
>
> decision = interrupt({
>
> "type": "approval_required",
>
> "request": state\["request"\],
>
> "message": f"请审批以下请求: {state\['request'\]}"
>
> })
>
> \# 从中断恢复后，decision 包含人工提供的决策
>
> return {"approved": decision.get("approved", False)}
>
> def execute_node(state: ApprovalState) -\> ApprovalState:
>
> """执行节点"""
>
> if state\["approved"\]:
>
> result = execute_request(state\["request"\])
>
> return {"result": result}
>
> else:
>
> return {"result": "请求被拒绝"}
>
> \# 构建图
>
> builder = StateGraph(ApprovalState)
>
> builder.add_node("approval", approval_node)
>
> builder.add_node("execute", execute_node)
>
> builder.set_entry_point("approval")
>
> builder.add_edge("approval", "execute")
>
> builder.add_edge("execute", END)
>
> \# 编译图（需要检查点支持）
>
> from langgraph.checkpoint.memory import MemorySaver
>
> graph = builder.compile(checkpointer=MemorySaver())

### **18.2.2 处理中断**

> *// python*
>
> \# 处理中断
>
> \# 执行图，会触发中断
>
> config = {"configurable": {"thread_id": "approval-session"}}
>
> try:
>
> result = graph.invoke(
>
> {"request": "删除数据库表 users", "approved": None, "result": None},
>
> config=config
>
> )
>
> except:
>
> pass \# 图被中断
>
> \# 获取当前状态
>
> state = graph.get_state(config)
>
> print(f"当前状态: {state.values}")
>
> print(f"待处理任务: {state.tasks}")
>
> \# 查看中断信息
>
> for task in state.tasks:
>
> print(f"任务 ID: {task.id}")
>
> print(f"中断信息: {task.interrupts}")
>
> \# 提供审批决策
>
> \# 方式 1：更新状态
>
> graph.update_state(
>
> config,
>
> {"approved": True},
>
> as_node="approval"
>
> )
>
> \# 方式 2：使用 Command
>
> from langgraph.types import Command
>
> graph.invoke(
>
> Command(resume={"approved": True}),
>
> config=config
>
> )
>
> \# 恢复执行
>
> result = graph.invoke(None, config=config)
>
> print(f"最终结果: {result}")

## **18.3 审批流程设计**

### **18.3.1 多级审批**

> *// python*
>
> \# 多级审批
>
> from typing import Literal
>
> class MultiApprovalState(TypedDict):
>
> request: str
>
> amount: float
>
> approvals: list\[dict\]
>
> current_level: int
>
> final_decision: str \| None
>
> \# 审批级别配置
>
> APPROVAL_LEVELS = \[
>
> {"level": 1, "role": "manager", "max_amount": 1000},
>
> {"level": 2, "role": "director", "max_amount": 10000},
>
> {"level": 3, "role": "ceo", "max_amount": float("inf")}
>
> \]
>
> def get_required_level(amount: float) -\> int:
>
> """获取需要的审批级别"""
>
> for level_config in APPROVAL_LEVELS:
>
> if amount \<= level_config\["max_amount"\]:
>
> return level_config\["level"\]
>
> return len(APPROVAL_LEVELS)
>
> def approval_node(state: MultiApprovalState) -\> MultiApprovalState:
>
> """审批节点"""
>
> current_level = state.get("current_level", 1)
>
> required_level = get_required_level(state\["amount"\])
>
> \# 如果已达到所需级别，通过
>
> if current_level \> required_level:
>
> return {"final_decision": "approved"}
>
> \# 请求当前级别的审批
>
> level_config = APPROVAL_LEVELS\[current_level - 1\]
>
> decision = interrupt({
>
> "type": "approval_required",
>
> "level": current_level,
>
> "role": level_config\["role"\],
>
> "request": state\["request"\],
>
> "amount": state\["amount"\],
>
> "message": f"请 {level_config\['role'\]} 审批金额为 {state\['amount'\]} 的请求"
>
> })
>
> approval = {
>
> "level": current_level,
>
> "role": level_config\["role"\],
>
> "approved": decision.get("approved", False),
>
> "comment": decision.get("comment", ""),
>
> "timestamp": datetime.now().isoformat()
>
> }
>
> new_approvals = state.get("approvals", \[\]) + \[approval\]
>
> if not decision.get("approved", False):
>
> \# 被拒绝
>
> return {
>
> "approvals": new_approvals,
>
> "final_decision": "rejected"
>
> }
>
> \# 进入下一级别
>
> return {
>
> "approvals": new_approvals,
>
> "current_level": current_level + 1
>
> }
>
> def should_continue(state: MultiApprovalState) -\> Literal\["continue", "end"\]:
>
> """决定是否继续审批"""
>
> if state.get("final_decision"):
>
> return "end"
>
> return "continue"
>
> \# 构建图
>
> builder = StateGraph(MultiApprovalState)
>
> builder.add_node("approval", approval_node)
>
> builder.set_entry_point("approval")
>
> builder.add_conditional_edges("approval", should_continue, {
>
> "continue": "approval", \# 回环，继续下一级审批
>
> "end": END
>
> })

### **18.3.2 审批超时处理**

> *// python*
>
> \# 审批超时处理
>
> import asyncio
>
> from datetime import datetime, timedelta
>
> class TimeoutApprovalState(TypedDict):
>
> request: str
>
> approved: bool \| None
>
> created_at: str
>
> timeout_hours: int
>
> timed_out: bool
>
> def approval_with_timeout(state: TimeoutApprovalState) -\> TimeoutApprovalState:
>
> """带超时的审批节点"""
>
> created_at = datetime.fromisoformat(state\["created_at"\])
>
> timeout = timedelta(hours=state.get("timeout_hours", 24))
>
> \# 检查是否超时
>
> if datetime.now() - created_at \> timeout:
>
> return {"timed_out": True, "approved": False}
>
> \# 发起中断
>
> decision = interrupt({
>
> "type": "approval_required",
>
> "request": state\["request"\],
>
> "timeout": (created_at + timeout).isoformat()
>
> })
>
> return {"approved": decision.get("approved", False)}
>
> \# 超时监控任务
>
> async def monitor_timeouts(graph, config, timeout_callback):
>
> """监控审批超时"""
>
> while True:
>
> await asyncio.sleep(3600) \# 每小时检查一次
>
> state = graph.get_state(config)
>
> if state.values.get("approved") is None:
>
> created_at = datetime.fromisoformat(state.values\["created_at"\])
>
> timeout = timedelta(hours=state.values.get("timeout_hours", 24))
>
> if datetime.now() - created_at \> timeout:
>
> \# 触发超时回调
>
> await timeout_callback(state.values)
>
> \# 自动拒绝或升级
>
> graph.update_state(
>
> config,
>
> {"timed_out": True, "approved": False},
>
> as_node="approval"
>
> )

## **18.4 本章小结**

本章介绍了LangGraph的人机协作功能。关键要点包括：

- 使用interrupt在关键点暂停执行。

- 通过update_state或Command恢复执行。

- 可以设计多级审批流程。

- 需要处理审批超时情况。

## **18.5 课后练习**

练习 18.1：实现一个完整的多级审批系统，支持动态配置审批级别。

练习 18.2：设计一个审批工作流，支持会签（多人同时审批）和或签（任一人审批即可）。
