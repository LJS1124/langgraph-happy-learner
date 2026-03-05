"""
练习 25.2：产品推荐智能体
问题描述：实现一个产品推荐智能体，根据用户需求推荐合适的产品。

学习目标：
- 实现推荐逻辑
- 匹配用户需求
- 个性化推荐
"""

from typing import List, Dict
from dataclasses import dataclass


@dataclass
class Product:
    id: str
    name: str
    category: str
    price: float
    tags: List[str]


class ProductRecommendationAgent:
    """产品推荐智能体"""
    
    def __init__(self):
        self.products: List[Product] = []
        self._init_products()
    
    def _init_products(self):
        """初始化产品数据"""
        self.products = [
            Product("P001", "iPhone 15", "手机", 6999, ["苹果", "高端", "拍照"]),
            Product("P002", "小米14", "手机", 3999, ["安卓", "性价比", "游戏"]),
            Product("P003", "MacBook Pro", "电脑", 14999, ["苹果", "办公", "专业"]),
            Product("P004", "ThinkPad", "电脑", 8999, ["商务", "办公", "稳定"]),
            Product("P005", "AirPods", "耳机", 1299, ["苹果", "无线", "便携"]),
        ]
    
    def recommend(self, user_needs: Dict) -> List[Dict]:
        """根据需求推荐产品"""
        # 提取需求
        budget = user_needs.get("budget", float("inf"))
        category = user_needs.get("category")
        tags = user_needs.get("tags", [])
        
        # 筛选产品
        candidates = []
        
        for product in self.products:
            # 价格筛选
            if product.price > budget:
                continue
            
            # 类别筛选
            if category and product.category != category:
                continue
            
            # 计算匹配分数
            score = 0
            matched_tags = []
            
            for tag in tags:
                if tag in product.tags:
                    score += 1
                    matched_tags.append(tag)
            
            candidates.append({
                "product": product,
                "score": score,
                "matched_tags": matched_tags
            })
        
        # 按分数排序
        candidates.sort(key=lambda x: x["score"], reverse=True)
        
        return candidates[:3]  # 返回前3个
    
    def process_request(self, user_input: str) -> str:
        """处理用户请求"""
        # 简单的需求提取
        needs = {}
        
        if "手机" in user_input:
            needs["category"] = "手机"
        elif "电脑" in user_input:
            needs["category"] = "电脑"
        elif "耳机" in user_input:
            needs["category"] = "耳机"
        
        if "便宜" in user_input or "性价比" in user_input:
            needs["budget"] = 5000
            needs["tags"] = ["性价比"]
        elif "高端" in user_input or "苹果" in user_input:
            needs["tags"] = ["苹果", "高端"]
        
        # 推荐
        recommendations = self.recommend(needs)
        
        if not recommendations:
            return "抱歉，没有找到符合您需求的产品"
        
        # 格式化响应
        response = "为您推荐以下产品：\n"
        for i, rec in enumerate(recommendations, 1):
            p = rec["product"]
            response += f"\n{i}. {p.name} - ¥{p.price}\n"
            response += f"   匹配标签: {', '.join(rec['matched_tags'])}\n"
        
        return response


def main():
    print("=" * 60)
    print("练习 25.2：产品推荐智能体")
    print("=" * 60)
    
    agent = ProductRecommendationAgent()
    
    # 测试不同需求
    test_requests = [
        "我想买个手机，预算5000左右",
        "推荐一款苹果产品",
        "我需要一台办公电脑",
    ]
    
    for request in test_requests:
        print(f"\n用户: {request}")
        print("-" * 40)
        response = agent.process_request(request)
        print(response)
    
    print("\n" + "=" * 60)
    print("产品推荐要点：")
    print("-" * 60)
    print("1. 提取用户需求")
    print("2. 多维度匹配")
    print("3. 计算推荐分数")
    print("4. 返回个性化结果")
    print("=" * 60)


if __name__ == "__main__":
    main()
