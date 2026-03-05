"""
练习 20.1：评估框架
问题描述：实现一个完整的评估框架，支持多种评估指标。

学习目标：
- 设计评估指标
- 自动化评估流程
- 生成评估报告
"""

from typing import List, Dict, Callable, Any
from dataclasses import dataclass


@dataclass
class EvaluationResult:
    metric_name: str
    score: float
    details: Dict


class EvaluationFramework:
    """评估框架"""
    
    def __init__(self):
        self.metrics: Dict[str, Callable] = {}
        self.results: List[EvaluationResult] = []
    
    def register_metric(self, name: str, metric_func: Callable):
        """注册评估指标"""
        self.metrics[name] = metric_func
        print(f"  [注册指标] {name}")
    
    def evaluate(self, predictions: List, ground_truth: List) -> Dict:
        """执行评估"""
        self.results = []
        
        for name, metric_func in self.metrics.items():
            score, details = metric_func(predictions, ground_truth)
            result = EvaluationResult(
                metric_name=name,
                score=score,
                details=details
            )
            self.results.append(result)
            print(f"  [{name}] 分数: {score:.2f}")
        
        return self.get_report()
    
    def get_report(self) -> Dict:
        """生成报告"""
        return {
            "metrics": {r.metric_name: r.score for r in self.results},
            "average": sum(r.score for r in self.results) / len(self.results) if self.results else 0,
            "details": {r.metric_name: r.details for r in self.results}
        }


# ============================================
# 预定义指标
# ============================================

def accuracy_metric(predictions: List, ground_truth: List) -> tuple:
    """准确率指标"""
    if not predictions:
        return 0.0, {"correct": 0, "total": 0}
    
    correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    total = len(predictions)
    score = correct / total if total > 0 else 0
    
    return score, {"correct": correct, "total": total}


def response_time_metric(predictions: List, ground_truth: List) -> tuple:
    """响应时间指标（模拟）"""
    import random
    avg_time = random.uniform(0.5, 2.0)
    # 时间越短分数越高
    score = max(0, 1 - avg_time / 3.0)
    
    return score, {"avg_time": f"{avg_time:.2f}s"}


def completeness_metric(predictions: List, ground_truth: List) -> tuple:
    """完整性指标"""
    if not predictions:
        return 0.0, {"empty": True}
    
    # 检查预测是否包含关键信息
    scores = []
    for pred in predictions:
        if isinstance(pred, str) and len(pred) > 10:
            scores.append(1.0)
        else:
            scores.append(0.5)
    
    avg_score = sum(scores) / len(scores)
    return avg_score, {"items": len(predictions)}


def main():
    print("=" * 60)
    print("练习 20.1：评估框架")
    print("=" * 60)
    
    framework = EvaluationFramework()
    
    # 注册指标
    print("\n注册评估指标：")
    print("-" * 40)
    framework.register_metric("accuracy", accuracy_metric)
    framework.register_metric("response_time", response_time_metric)
    framework.register_metric("completeness", completeness_metric)
    
    # 测试数据
    predictions = ["答案A", "答案B", "答案C", "答案D"]
    ground_truth = ["答案A", "答案B", "答案X", "答案D"]
    
    # 执行评估
    print("\n执行评估：")
    print("-" * 40)
    report = framework.evaluate(predictions, ground_truth)
    
    # 打印报告
    print("\n评估报告：")
    print("-" * 40)
    print(f"  各项指标: {report['metrics']}")
    print(f"  综合得分: {report['average']:.2f}")
    
    print("\n" + "=" * 60)
    print("评估框架要点：")
    print("-" * 60)
    print("1. 注册多种评估指标")
    print("2. 统一评估接口")
    print("3. 自动生成报告")
    print("4. 支持自定义指标")
    print("=" * 60)


if __name__ == "__main__":
    main()
