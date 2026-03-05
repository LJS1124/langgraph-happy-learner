"""
练习 15.1：错误处理中间件
问题描述：实现一个完整的错误处理中间件。

学习目标：
- 错误分类处理
- 自动重试机制
- 降级策略
"""

from typing import Callable, Any, Dict
from enum import Enum
from dataclasses import dataclass
import time


class ErrorType(Enum):
    TRANSIENT = "transient"      # 瞬时错误（可重试）
    PERMANENT = "permanent"      # 永久错误（不可重试）
    TIMEOUT = "timeout"          # 超时错误
    RATE_LIMIT = "rate_limit"    # 限流错误


@dataclass
class ErrorContext:
    error_type: ErrorType
    message: str
    retry_count: int = 0
    should_retry: bool = True


class ErrorHandler:
    """错误处理中间件"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.error_handlers: Dict[ErrorType, Callable] = {}
        self.fallback_handler: Callable = None
    
    def classify_error(self, error: Exception) -> ErrorType:
        """分类错误"""
        error_str = str(error).lower()
        
        if "timeout" in error_str:
            return ErrorType.TIMEOUT
        elif "rate limit" in error_str or "429" in error_str:
            return ErrorType.RATE_LIMIT
        elif "connection" in error_str or "network" in error_str:
            return ErrorType.TRANSIENT
        else:
            return ErrorType.PERMANENT
    
    def register_handler(self, error_type: ErrorType, handler: Callable):
        """注册错误处理器"""
        self.error_handlers[error_type] = handler
    
    def set_fallback(self, handler: Callable):
        """设置降级处理器"""
        self.fallback_handler = handler
    
    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """执行函数（带错误处理）"""
        retry_count = 0
        
        while retry_count <= self.max_retries:
            try:
                return func(*args, **kwargs)
            
            except Exception as e:
                error_type = self.classify_error(e)
                print(f"  [错误] {error_type.value}: {e}")
                
                context = ErrorContext(
                    error_type=error_type,
                    message=str(e),
                    retry_count=retry_count
                )
                
                # 检查是否可重试
                if error_type in [ErrorType.TRANSIENT, ErrorType.TIMEOUT, ErrorType.RATE_LIMIT]:
                    if retry_count < self.max_retries:
                        retry_count += 1
                        wait_time = self._get_wait_time(error_type, retry_count)
                        print(f"  [重试] 第{retry_count}次，等待{wait_time}秒")
                        time.sleep(wait_time)
                        continue
                
                # 尝试降级
                if self.fallback_handler:
                    print("  [降级] 使用降级处理")
                    return self.fallback_handler(*args, **kwargs)
                
                raise
        
        return None
    
    def _get_wait_time(self, error_type: ErrorType, retry_count: int) -> float:
        """获取等待时间"""
        if error_type == ErrorType.RATE_LIMIT:
            return 2.0 ** retry_count  # 指数退避
        else:
            return 0.5 * retry_count


def main():
    print("=" * 60)
    print("练习 15.1：错误处理中间件")
    print("=" * 60)
    
    handler = ErrorHandler(max_retries=3)
    
    # 设置降级处理
    handler.set_fallback(lambda x: f"降级响应: {x}")
    
    # 模拟函数
    def risky_function(should_fail: bool):
        if should_fail:
            raise ConnectionError("网络连接失败")
        return "成功"
    
    print("\n测试1：成功执行")
    print("-" * 40)
    result = handler.execute(risky_function, False)
    print(f"结果: {result}")
    
    print("\n测试2：失败后降级")
    print("-" * 40)
    result = handler.execute(risky_function, True)
    print(f"结果: {result}")
    
    print("\n" + "=" * 60)
    print("错误处理要点：")
    print("-" * 60)
    print("1. 分类错误类型")
    print("2. 瞬时错误自动重试")
    print("3. 永久错误直接降级")
    print("4. 提供友好的降级响应")
    print("=" * 60)


if __name__ == "__main__":
    main()
