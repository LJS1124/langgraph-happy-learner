"""
练习 21.1：安全防护系统
问题描述：实现一个完整的安全防护系统。

学习目标：
- 输入净化
- 输出审核
- 权限控制
"""

from typing import List, Dict, Tuple
import re


class SecuritySystem:
    """安全防护系统"""
    
    def __init__(self):
        self.sensitive_patterns = [
            r"\b\d{11}\b",  # 手机号
            r"\b\d{18}\b",  # 身份证
            r"\b[\w.-]+@[\w.-]+\.\w+\b",  # 邮箱
        ]
        self.blocked_words = ["敏感词1", "敏感词2"]
    
    def sanitize_input(self, text: str) -> Tuple[str, List[str]]:
        """净化输入"""
        warnings = []
        sanitized = text
        
        # 检查敏感词
        for word in self.blocked_words:
            if word in text:
                sanitized = sanitized.replace(word, "***")
                warnings.append(f"包含敏感词: {word}")
        
        # 检查敏感信息
        for pattern in self.sensitive_patterns:
            matches = re.findall(pattern, text)
            if matches:
                warnings.append(f"检测到敏感信息: {len(matches)}处")
                sanitized = re.sub(pattern, "[已脱敏]", sanitized)
        
        return sanitized, warnings
    
    def audit_output(self, text: str) -> Tuple[bool, List[str]]:
        """审核输出"""
        issues = []
        
        # 检查是否包含敏感信息
        for pattern in self.sensitive_patterns:
            if re.search(pattern, text):
                issues.append("输出包含敏感信息")
        
        # 检查敏感词
        for word in self.blocked_words:
            if word in text:
                issues.append("输出包含敏感词")
        
        is_safe = len(issues) == 0
        return is_safe, issues
    
    def check_permission(self, user: str, action: str, resource: str) -> bool:
        """检查权限"""
        # 简单的权限模型
        permissions = {
            "admin": ["read", "write", "delete"],
            "user": ["read"],
            "guest": []
        }
        
        user_perms = permissions.get(user, [])
        has_permission = action in user_perms
        
        print(f"  [权限检查] {user} -> {action} -> {resource}: {'允许' if has_permission else '拒绝'}")
        
        return has_permission


def main():
    print("=" * 60)
    print("练习 21.1：安全防护系统")
    print("=" * 60)
    
    security = SecuritySystem()
    
    # 测试输入净化
    print("\n测试输入净化：")
    print("-" * 40)
    
    test_inputs = [
        "我的手机号是13800138000",
        "这是一条正常消息",
        "敏感词1不应该出现",
    ]
    
    for text in test_inputs:
        sanitized, warnings = security.sanitize_input(text)
        print(f"\n原文: {text}")
        print(f"净化: {sanitized}")
        if warnings:
            print(f"警告: {warnings}")
    
    # 测试输出审核
    print("\n测试输出审核：")
    print("-" * 40)
    
    test_outputs = [
        "这是一条安全的回复",
        "联系邮箱: test@example.com",
    ]
    
    for text in test_outputs:
        is_safe, issues = security.audit_output(text)
        print(f"\n输出: {text}")
        print(f"安全: {'是' if is_safe else '否'}")
        if issues:
            print(f"问题: {issues}")
    
    # 测试权限检查
    print("\n测试权限检查：")
    print("-" * 40)
    
    security.check_permission("admin", "delete", "resource1")
    security.check_permission("user", "write", "resource1")
    security.check_permission("user", "read", "resource1")
    
    print("\n" + "=" * 60)
    print("安全防护要点：")
    print("-" * 60)
    print("1. 输入净化防止注入")
    print("2. 输出审核防止泄露")
    print("3. 权限控制最小权限")
    print("4. 记录安全日志")
    print("=" * 60)


if __name__ == "__main__":
    main()
