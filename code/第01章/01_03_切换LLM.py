"""
练习 1.3：切换LLM
问题描述：使用不同的LLM替代OpenAI，观察行为差异。

学习目标：
- 理解LLM抽象接口
- 掌握不同LLM的调用方式
- 了解不同LLM的特点
"""

import os
from typing import TypedDict
from langgraph.graph import StateGraph, END

# ============================================
# LLM 配置 - 支持多种LLM切换
# ============================================

# 方式1：使用 OpenAI
try:
    from langchain_openai import ChatOpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# 方式2：使用 Anthropic Claude
try:
    from langchain_anthropic import ChatAnthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# 方式3：使用本地模型（如 Ollama）
try:
    from langchain_ollama import ChatOllama
    HAS_OLLAMA = True
except ImportError:
    HAS_OLLAMA = False


# ============================================
# 1. 定义状态
# ============================================

class State(TypedDict):
    """对话状态"""
    messages: list[str]
    response: str


# ============================================
# 2. LLM 工厂函数
# ============================================

def create_llm(provider: str = "openai", model: str = None):
    """
    创建LLM实例
    
    Args:
        provider: LLM提供商 ("openai", "anthropic", "ollama")
        model: 模型名称
    
    Returns:
        LLM实例
    """
    if provider == "openai":
        if not HAS_OPENAI:
            raise ImportError("请安装 langchain-openai: pip install langchain-openai")
        model = model or "gpt-4o-mini"
        return ChatOpenAI(model=model, temperature=0.7)
    
    elif provider == "anthropic":
        if not HAS_ANTHROPIC:
            raise ImportError("请安装 langchain-anthropic: pip install langchain-anthropic")
        model = model or "claude-3-haiku-20240307"
        return ChatAnthropic(model=model, temperature=0.7)
    
    elif provider == "ollama":
        if not HAS_OLLAMA:
            raise ImportError("请安装 langchain-ollama: pip install langchain-ollama")
        model = model or "llama3"
        return ChatOllama(model=model, temperature=0.7)
    
    else:
        raise ValueError(f"不支持的LLM提供商: {provider}")


# ============================================
# 3. 定义节点函数
# ============================================

def chat_node(state: State, llm) -> dict:
    """聊天节点：使用LLM生成响应"""
    # 构建提示
    prompt = "\n".join(state["messages"])
    
    # 调用LLM
    response = llm.invoke(prompt)
    
    return {
        "messages": state["messages"] + [f"Assistant: {response.content}"],
        "response": response.content
    }


# ============================================
# 4. 构建图
# ============================================

def build_graph(llm):
    """构建图"""
    builder = StateGraph(State)
    
    # 使用lambda绑定llm参数
    builder.add_node("chat", lambda state: chat_node(state, llm))
    
    builder.set_entry_point("chat")
    builder.add_edge("chat", END)
    
    return builder.compile()


# ============================================
# 5. 运行示例
# ============================================

def test_llm(provider: str, question: str):
    """测试单个LLM"""
    print(f"\n{'='*60}")
    print(f"测试 {provider.upper()} LLM")
    print(f"{'='*60}")
    
    try:
        llm = create_llm(provider)
        graph = build_graph(llm)
        
        initial_state = {
            "messages": [f"User: {question}"],
            "response": ""
        }
        
        result = graph.invoke(initial_state)
        
        print(f"\n问题: {question}")
        print(f"\n回答: {result['response']}")
        
    except Exception as e:
        print(f"\n错误: {e}")


def main():
    """主函数"""
    print("=" * 60)
    print("练习 1.3：切换LLM")
    print("=" * 60)
    
    question = "请用一句话解释什么是LangGraph"
    
    # 测试不同LLM
    providers = ["openai", "anthropic", "ollama"]
    
    for provider in providers:
        test_llm(provider, question)
    
    print("\n" + "=" * 60)
    print("对比说明：")
    print("-" * 60)
    print("1. OpenAI GPT-4: 响应快，质量高，但需要付费")
    print("2. Anthropic Claude: 响应细腻，安全意识强")
    print("3. Ollama本地模型: 免费，隐私好，但质量可能较低")
    print("=" * 60)


if __name__ == "__main__":
    main()


# ============================================
# 示例输出（实际输出会因LLM而异）
# ============================================
"""
============================================================
练习 1.3：切换LLM
============================================================

============================================================
测试 OPENAI LLM
============================================================

问题: 请用一句话解释什么是LangGraph

回答: LangGraph是一个用于构建有状态、多智能体AI应用的框架，它使用图结构来编排LLM的工作流程。

============================================================
测试 ANTHROPIC LLM
============================================================

问题: 请用一句话解释什么是LangGraph

回答: LangGraph是一个基于图结构的框架，用于构建复杂的AI智能体系统，支持状态管理和多智能体协作。

============================================================
测试 OLLAMA LLM
============================================================

问题: 请用一句话解释什么是LangGraph

回答: LangGraph是一个Python库，用于构建AI智能体工作流。
"""
