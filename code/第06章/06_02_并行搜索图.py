"""
练习 6.2：并行搜索图
问题描述：实现一个并行搜索图，同时从多个数据源搜索，然后合并结果。

学习目标：
- 实现并行节点执行
- 合并多个数据源结果
- 处理并行结果聚合
"""

from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
import asyncio
import time


# ============================================
# 1. 定义状态
# ============================================

def merge_search_results(left: List, right: List) -> List:
    """合并搜索结果"""
    return left + right


class SearchState(TypedDict):
    """搜索状态"""
    query: str
    results: Annotated[List[dict], merge_search_results]
    search_time: float


# ============================================
# 2. 模拟搜索函数
# ============================================

async def search_source(source_name: str, query: str, delay: float) -> dict:
    """模拟搜索单个数据源"""
    await asyncio.sleep(delay)  # 模拟网络延迟
    return {
        "source": source_name,
        "query": query,
        "results": [
            {"title": f"{source_name}结果1", "score": 0.9},
            {"title": f"{source_name}结果2", "score": 0.8},
        ]
    }


# ============================================
# 3. 并行搜索节点
# ============================================

async def parallel_search_node(state: SearchState) -> dict:
    """并行搜索节点"""
    query = state["query"]
    
    print(f"  开始并行搜索: {query}")
    start_time = time.time()
    
    # 并行搜索多个数据源
    tasks = [
        search_source("Google", query, 0.5),
        search_source("Bing", query, 0.7),
        search_source("Baidu", query, 0.6),
    ]
    
    results = await asyncio.gather(*tasks)
    
    elapsed = time.time() - start_time
    print(f"  搜索完成，耗时: {elapsed:.2f}s")
    
    # 合并结果
    all_results = []
    for r in results:
        all_results.extend(r["results"])
    
    return {
        "results": all_results,
        "search_time": elapsed
    }


# ============================================
# 4. 使用LangGraph的并行执行
# ============================================

def google_search(state: SearchState) -> dict:
    """Google搜索节点"""
    print("  搜索 Google...")
    time.sleep(0.5)
    return {
        "results": [
            {"source": "Google", "title": "Google结果1", "score": 0.95}
        ]
    }


def bing_search(state: SearchState) -> dict:
    """Bing搜索节点"""
    print("  搜索 Bing...")
    time.sleep(0.7)
    return {
        "results": [
            {"source": "Bing", "title": "Bing结果1", "score": 0.90}
        ]
    }


def baidu_search(state: SearchState) -> dict:
    """百度搜索节点"""
    print("  搜索 Baidu...")
    time.sleep(0.6)
    return {
        "results": [
            {"source": "Baidu", "title": "百度结果1", "score": 0.85}
        ]
    }


def merge_results_node(state: SearchState) -> dict:
    """合并结果节点"""
    print("  合并搜索结果...")
    results = state["results"]
    
    # 按分数排序
    sorted_results = sorted(results, key=lambda x: x["score"], reverse=True)
    
    return {"results": sorted_results}


# ============================================
# 5. 构建图
# ============================================

def build_parallel_search_graph():
    """
    构建并行搜索图
    
    结构：
           ┌→ google_search ─┐
    START ─┼→ bing_search  ──┼→ merge → END
           └→ baidu_search ─┘
    """
    builder = StateGraph(SearchState)
    
    # 添加搜索节点
    builder.add_node("google", google_search)
    builder.add_node("bing", bing_search)
    builder.add_node("baidu", baidu_search)
    builder.add_node("merge", merge_results_node)
    
    # 设置入口（使用虚拟入口点实现并行）
    # 注意：LangGraph不直接支持并行执行
    # 这里使用串行模拟
    
    builder.set_entry_point("google")
    builder.add_edge("google", "bing")
    builder.add_edge("bing", "baidu")
    builder.add_edge("baidu", "merge")
    builder.add_edge("merge", END)
    
    return builder.compile()


# ============================================
# 6. 测试
# ============================================

def main():
    """主函数"""
    print("=" * 60)
    print("练习 6.2：并行搜索图")
    print("=" * 60)
    
    # 测试异步并行搜索
    print("\n测试1：异步并行搜索")
    print("-" * 60)
    
    async def test_async():
        state = {"query": "LangGraph", "results": [], "search_time": 0}
        result = await parallel_search_node(state)
        print(f"\n结果数: {len(result['results'])}")
        print(f"耗时: {result['search_time']:.2f}s")
    
    asyncio.run(test_async())
    
    # 测试图执行
    print("\n测试2：图执行（串行模拟）")
    print("-" * 60)
    
    graph = build_parallel_search_graph()
    result = graph.invoke({
        "query": "Python教程",
        "results": [],
        "search_time": 0
    })
    
    print(f"\n结果:")
    for r in result["results"]:
        print(f"  [{r['source']}] {r['title']} (score: {r['score']})")
    
    print("\n" + "=" * 60)
    print("并行搜索要点：")
    print("-" * 60)
    print("1. 使用asyncio.gather实现并行")
    print("2. 使用Annotated合并结果")
    print("3. 注意结果去重和排序")
    print("4. 处理超时和错误")
    print("=" * 60)


if __name__ == "__main__":
    main()
