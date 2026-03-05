"""
练习 22.1：CI/CD流水线
问题描述：实现一个完整的CI/CD流水线。

学习目标：
- 自动化测试
- 自动构建
- 自动部署
"""

from typing import List, Dict, Callable
from enum import Enum
from dataclasses import dataclass


class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class StageResult:
    name: str
    status: StageStatus
    message: str
    duration: float = 0


class Pipeline:
    """CI/CD流水线"""
    
    def __init__(self, name: str):
        self.name = name
        self.stages: List[Dict] = []
        self.results: List[StageResult] = []
    
    def add_stage(self, name: str, func: Callable):
        """添加阶段"""
        self.stages.append({"name": name, "func": func})
        print(f"  [添加阶段] {name}")
    
    def run(self) -> bool:
        """执行流水线"""
        print(f"\n{'='*50}")
        print(f"执行流水线: {self.name}")
        print(f"{'='*50}")
        
        self.results = []
        
        for stage in self.stages:
            result = self._run_stage(stage)
            self.results.append(result)
            
            if result.status == StageStatus.FAILED:
                print(f"\n流水线失败于阶段: {result.name}")
                return False
        
        print(f"\n流水线执行成功!")
        return True
    
    def _run_stage(self, stage: Dict) -> StageResult:
        """执行单个阶段"""
        import time
        
        name = stage["name"]
        func = stage["func"]
        
        print(f"\n[{name}] 开始执行...")
        
        start_time = time.time()
        
        try:
            success, message = func()
            duration = time.time() - start_time
            
            status = StageStatus.SUCCESS if success else StageStatus.FAILED
            
            print(f"[{name}] {status.value} ({duration:.2f}s)")
            print(f"  {message}")
            
            return StageResult(
                name=name,
                status=status,
                message=message,
                duration=duration
            )
        
        except Exception as e:
            duration = time.time() - start_time
            print(f"[{name}] failed: {e}")
            
            return StageResult(
                name=name,
                status=StageStatus.FAILED,
                message=str(e),
                duration=duration
            )
    
    def get_report(self) -> Dict:
        """获取报告"""
        return {
            "pipeline": self.name,
            "stages": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "message": r.message,
                    "duration": f"{r.duration:.2f}s"
                }
                for r in self.results
            ],
            "total_duration": sum(r.duration for r in self.results)
        }


# ============================================
# 预定义阶段函数
# ============================================

def run_tests():
    """运行测试"""
    import time
    time.sleep(0.5)  # 模拟测试
    return True, "所有测试通过 (10/10)"


def build_image():
    """构建镜像"""
    import time
    time.sleep(0.3)
    return True, "镜像构建成功: v1.0.0"


def deploy_staging():
    """部署到测试环境"""
    import time
    time.sleep(0.2)
    return True, "部署到staging成功"


def deploy_production():
    """部署到生产环境"""
    import time
    time.sleep(0.2)
    return True, "部署到production成功"


def main():
    print("=" * 60)
    print("练习 22.1：CI/CD流水线")
    print("=" * 60)
    
    # 创建流水线
    pipeline = Pipeline("智能体服务部署")
    
    # 添加阶段
    print("\n配置流水线：")
    print("-" * 40)
    pipeline.add_stage("测试", run_tests)
    pipeline.add_stage("构建", build_image)
    pipeline.add_stage("部署测试环境", deploy_staging)
    pipeline.add_stage("部署生产环境", deploy_production)
    
    # 执行流水线
    success = pipeline.run()
    
    # 获取报告
    print("\n流水线报告：")
    print("-" * 40)
    report = pipeline.get_report()
    for stage in report["stages"]:
        print(f"  {stage['name']}: {stage['status']} ({stage['duration']})")
    print(f"\n总耗时: {report['total_duration']:.2f}s")
    
    print("\n" + "=" * 60)
    print("CI/CD要点：")
    print("-" * 60)
    print("1. 分阶段执行")
    print("2. 失败立即停止")
    print("3. 记录执行结果")
    print("4. 生成详细报告")
    print("=" * 60)


if __name__ == "__main__":
    main()
