"""
练习 4.1：电商订单状态设计
问题描述：定义一个电商订单查询智能体的状态，包含订单信息、用户信息、查询历史。

学习目标：
- 设计复杂业务场景的状态结构
- 理解状态字段与业务需求的对应关系
- 掌握嵌套类型的定义
"""

from typing import TypedDict, Optional, List, Annotated
from datetime import datetime
from enum import Enum
from operator import add


# ============================================
# 枚举定义
# ============================================

class OrderStatus(str, Enum):
    """订单状态"""
    PENDING = "pending"           # 待支付
    PAID = "paid"                 # 已支付
    SHIPPED = "shipped"           # 已发货
    DELIVERED = "delivered"       # 已送达
    CANCELLED = "cancelled"       # 已取消
    REFUNDED = "refunded"         # 已退款


class QueryType(str, Enum):
    """查询类型"""
    ORDER_STATUS = "order_status"     # 查询订单状态
    ORDER_DETAIL = "order_detail"     # 查询订单详情
    LOGISTICS = "logistics"           # 查询物流
    REFUND = "refund"                 # 申请退款


# ============================================
# 嵌套类型定义
# ============================================

class OrderItem(TypedDict):
    """订单商品项"""
    product_id: str
    product_name: str
    quantity: int
    price: float
    sku: str


class OrderInfo(TypedDict):
    """订单信息"""
    order_id: str
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime]
    shipping_address: Optional[str]
    tracking_number: Optional[str]


class UserInfo(TypedDict):
    """用户信息"""
    user_id: str
    username: str
    phone: str
    email: Optional[str]
    vip_level: int  # 0=普通, 1=白银, 2=黄金, 3=钻石


class QueryRecord(TypedDict):
    """查询记录"""
    query_type: QueryType
    query_content: str
    timestamp: datetime
    result_summary: str


# ============================================
# 主状态定义
# ============================================

class OrderQueryState(TypedDict):
    """
    电商订单查询智能体状态
    
    业务场景：
    用户通过对话查询订单状态、物流信息等
    
    状态字段说明：
    - user: 当前用户信息
    - current_order: 当前查询的订单
    - query_history: 查询历史记录
    - messages: 对话消息
    - pending_action: 待执行的操作
    """
    
    # 用户信息
    user: Optional[UserInfo]
    
    # 当前订单信息
    current_order: Optional[OrderInfo]
    
    # 查询历史（使用add reducer自动追加）
    query_history: Annotated[List[QueryRecord], add]
    
    # 对话消息
    messages: Annotated[List[str], add]
    
    # 待执行操作
    pending_action: Optional[str]
    
    # 错误信息
    error: Optional[str]


# ============================================
# 辅助函数
# ============================================

def create_user(
    user_id: str,
    username: str,
    phone: str,
    vip_level: int = 0,
    email: str = None
) -> UserInfo:
    """创建用户信息"""
    return UserInfo(
        user_id=user_id,
        username=username,
        phone=phone,
        email=email,
        vip_level=vip_level
    )


def create_order(
    order_id: str,
    items: List[OrderItem],
    status: OrderStatus = OrderStatus.PENDING
) -> OrderInfo:
    """创建订单信息"""
    total = sum(item["price"] * item["quantity"] for item in items)
    return OrderInfo(
        order_id=order_id,
        items=items,
        total_amount=total,
        status=status,
        created_at=datetime.now(),
        updated_at=None,
        shipping_address=None,
        tracking_number=None
    )


def create_query_record(
    query_type: QueryType,
    content: str,
    result: str = ""
) -> QueryRecord:
    """创建查询记录"""
    return QueryRecord(
        query_type=query_type,
        query_content=content,
        timestamp=datetime.now(),
        result_summary=result
    )


# ============================================
# 示例使用
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 4.1：电商订单状态设计")
    print("=" * 60)
    
    # 创建用户
    user = create_user(
        user_id="U001",
        username="张三",
        phone="13800138000",
        vip_level=2,
        email="zhangsan@example.com"
    )
    
    # 创建订单商品
    items = [
        OrderItem(
            product_id="P001",
            product_name="iPhone 15 Pro",
            quantity=1,
            price=8999.0,
            sku="IP15PRO-256-BLK"
        ),
        OrderItem(
            product_id="P002",
            product_name="手机壳",
            quantity=2,
            price=99.0,
            sku="CASE-IP15-BLK"
        )
    ]
    
    # 创建订单
    order = create_order(
        order_id="ORD20240101001",
        items=items,
        status=OrderStatus.SHIPPED
    )
    
    # 创建初始状态
    state: OrderQueryState = {
        "user": user,
        "current_order": order,
        "query_history": [],
        "messages": [],
        "pending_action": None,
        "error": None
    }
    
    # 模拟查询操作
    state["query_history"].append(
        create_query_record(
            QueryType.ORDER_STATUS,
            "查询订单ORD20240101001状态",
            "订单已发货，正在配送中"
        )
    )
    
    state["messages"].append("用户: 帮我查一下订单状态")
    state["messages"].append("助手: 您的订单ORD20240101001已发货，正在配送中")
    
    # 打印状态
    print("\n用户信息：")
    print(f"  用户ID: {state['user']['user_id']}")
    print(f"  用户名: {state['user']['username']}")
    print(f"  VIP等级: {state['user']['vip_level']}")
    
    print("\n订单信息：")
    print(f"  订单号: {state['current_order']['order_id']}")
    print(f"  状态: {state['current_order']['status'].value}")
    print(f"  总金额: ¥{state['current_order']['total_amount']:.2f}")
    print(f"  商品数: {len(state['current_order']['items'])}")
    
    print("\n查询历史：")
    for i, record in enumerate(state['query_history'], 1):
        print(f"  {i}. [{record['query_type'].value}] {record['query_content']}")
        print(f"     结果: {record['result_summary']}")
    
    print("\n对话记录：")
    for msg in state['messages']:
        print(f"  {msg}")
    
    print("\n" + "=" * 60)
    print("状态设计要点：")
    print("-" * 60)
    print("1. 根据业务需求拆分状态字段")
    print("2. 使用枚举保证数据一致性")
    print("3. 使用Optional处理可能为空的字段")
    print("4. 使用Annotated指定Reducer")
    print("=" * 60)


if __name__ == "__main__":
    main()
