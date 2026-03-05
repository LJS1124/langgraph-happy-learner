"""
练习 25.1：订单修改功能
问题描述：为订单智能体添加订单修改功能，支持修改收货地址。

学习目标：
- 扩展智能体功能
- 实现数据修改
- 验证修改权限
"""

from typing import TypedDict, Optional
from dataclasses import dataclass


@dataclass
class Order:
    order_id: str
    user_id: str
    address: str
    status: str


class OrderAgent:
    """订单智能体"""
    
    def __init__(self):
        self.orders: dict = {}
        self._init_sample_data()
    
    def _init_sample_data(self):
        """初始化示例数据"""
        self.orders = {
            "ORD001": Order("ORD001", "U001", "北京市朝阳区xxx", "shipped"),
            "ORD002": Order("ORD002", "U001", "上海市浦东xxx", "pending"),
        }
    
    def query_order(self, order_id: str, user_id: str) -> dict:
        """查询订单"""
        order = self.orders.get(order_id)
        
        if not order:
            return {"success": False, "message": "订单不存在"}
        
        if order.user_id != user_id:
            return {"success": False, "message": "无权查看此订单"}
        
        return {
            "success": True,
            "order": {
                "order_id": order.order_id,
                "address": order.address,
                "status": order.status
            }
        }
    
    def modify_address(self, order_id: str, user_id: str, new_address: str) -> dict:
        """修改收货地址"""
        order = self.orders.get(order_id)
        
        if not order:
            return {"success": False, "message": "订单不存在"}
        
        if order.user_id != user_id:
            return {"success": False, "message": "无权修改此订单"}
        
        # 检查订单状态
        if order.status in ["delivered", "cancelled"]:
            return {"success": False, "message": f"订单已{order.status}，无法修改"}
        
        # 执行修改
        old_address = order.address
        order.address = new_address
        
        print(f"  [修改] 订单{order_id}地址: {old_address} -> {new_address}")
        
        return {
            "success": True,
            "message": "地址修改成功",
            "old_address": old_address,
            "new_address": new_address
        }
    
    def process_request(self, user_input: str, user_id: str) -> str:
        """处理用户请求"""
        # 简单的意图识别
        if "修改地址" in user_input or "改地址" in user_input:
            # 提取订单号和新地址（简化）
            order_id = "ORD001"
            new_address = "新地址xxx"
            result = self.modify_address(order_id, user_id, new_address)
            return result["message"]
        
        elif "查订单" in user_input or "订单状态" in user_input:
            order_id = "ORD001"
            result = self.query_order(order_id, user_id)
            if result["success"]:
                return f"订单{order_id}状态: {result['order']['status']}, 地址: {result['order']['address']}"
            return result["message"]
        
        else:
            return "我可以帮您查询订单或修改收货地址"


def main():
    print("=" * 60)
    print("练习 25.1：订单修改功能")
    print("=" * 60)
    
    agent = OrderAgent()
    
    # 测试查询
    print("\n测试查询订单：")
    print("-" * 40)
    result = agent.query_order("ORD001", "U001")
    print(f"结果: {result}")
    
    # 测试修改
    print("\n测试修改地址：")
    print("-" * 40)
    result = agent.modify_address("ORD001", "U001", "北京市海淀区新地址")
    print(f"结果: {result}")
    
    # 测试权限
    print("\n测试权限检查：")
    print("-" * 40)
    result = agent.modify_address("ORD001", "U002", "新地址")
    print(f"结果: {result}")
    
    print("\n" + "=" * 60)
    print("订单修改要点：")
    print("-" * 60)
    print("1. 验证用户权限")
    print("2. 检查订单状态")
    print("3. 记录修改历史")
    print("4. 返回明确结果")
    print("=" * 60)


if __name__ == "__main__":
    main()
