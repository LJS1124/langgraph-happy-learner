"""
练习 18.1：多级审批系统
问题描述：实现一个完整的多级审批系统，支持动态配置审批级别。

学习目标：
- 实现审批工作流
- 支持多级审批
- 动态配置审批链
"""

from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass
class ApprovalLevel:
    level: int
    approver: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    comment: str = ""


class MultiLevelApproval:
    """多级审批系统"""
    
    def __init__(self):
        self.approval_chains: Dict[str, List[str]] = {}
        self.pending_approvals: Dict[str, Dict] = {}
    
    def configure_chain(self, chain_name: str, approvers: List[str]):
        """配置审批链"""
        self.approval_chains[chain_name] = approvers
        print(f"  [配置] 审批链 '{chain_name}': {' -> '.join(approvers)}")
    
    def submit(self, request_id: str, chain_name: str, content: str) -> bool:
        """提交审批请求"""
        if chain_name not in self.approval_chains:
            print(f"  [错误] 未找到审批链: {chain_name}")
            return False
        
        approvers = self.approval_chains[chain_name]
        
        self.pending_approvals[request_id] = {
            "content": content,
            "chain_name": chain_name,
            "levels": [
                ApprovalLevel(level=i+1, approver=a)
                for i, a in enumerate(approvers)
            ],
            "current_level": 0
        }
        
        print(f"  [提交] 请求 {request_id} 进入审批流程")
        return True
    
    def approve(self, request_id: str, approver: str, comment: str = "") -> str:
        """审批"""
        if request_id not in self.pending_approvals:
            return "请求不存在"
        
        request = self.pending_approvals[request_id]
        current_level = request["current_level"]
        
        if current_level >= len(request["levels"]):
            return "审批已完成"
        
        level = request["levels"][current_level]
        
        if level.approver != approver:
            return f"当前审批人应为: {level.approver}"
        
        level.status = ApprovalStatus.APPROVED
        level.comment = comment
        
        print(f"  [批准] {approver} 批准了请求")
        
        request["current_level"] += 1
        
        if request["current_level"] >= len(request["levels"]):
            return "审批通过！"
        
        next_approver = request["levels"][request["current_level"]].approver
        return f"等待 {next_approver} 审批"
    
    def reject(self, request_id: str, approver: str, reason: str) -> str:
        """拒绝"""
        if request_id not in self.pending_approvals:
            return "请求不存在"
        
        request = self.pending_approvals[request_id]
        current_level = request["current_level"]
        level = request["levels"][current_level]
        
        level.status = ApprovalStatus.REJECTED
        level.comment = reason
        
        print(f"  [拒绝] {approver} 拒绝了请求: {reason}")
        
        return "审批被拒绝"


def main():
    print("=" * 60)
    print("练习 18.1：多级审批系统")
    print("=" * 60)
    
    system = MultiLevelApproval()
    
    # 配置审批链
    print("\n配置审批链：")
    print("-" * 40)
    system.configure_chain("expense", ["组长", "经理", "财务"])
    system.configure_chain("leave", ["组长", "HR"])
    
    # 提交审批
    print("\n提交审批：")
    print("-" * 40)
    system.submit("REQ001", "expense", "报销1000元")
    
    # 审批流程
    print("\n审批流程：")
    print("-" * 40)
    
    result = system.approve("REQ001", "组长", "同意")
    print(f"  结果: {result}")
    
    result = system.approve("REQ001", "经理", "同意")
    print(f"  结果: {result}")
    
    result = system.approve("REQ001", "财务", "已核实，同意")
    print(f"  结果: {result}")
    
    print("\n" + "=" * 60)
    print("多级审批要点：")
    print("-" * 60)
    print("1. 配置灵活的审批链")
    print("2. 按顺序逐级审批")
    print("3. 支持批准/拒绝")
    print("4. 记录审批意见")
    print("=" * 60)


if __name__ == "__main__":
    main()
