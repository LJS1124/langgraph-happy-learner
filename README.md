<div align="center">

# LangGraph 从入门到精通实战指南

一套面向工程实践的中文 LangGraph 学习资料  
从基础概念到生产级智能体系统落地

[![Chapters](https://img.shields.io/badge/Chapters-26-1f6feb)](./book/LangGraph实战指南-Markdown/按部分章节/目录.md)
[![Markdown Files](https://img.shields.io/badge/Markdown%20Files-28-2ea043)](./book/LangGraph实战指南-Markdown/按部分章节/目录.md)
[![Code Examples](https://img.shields.io/badge/Code%20Examples-41-f0883e)](./code)
[![Last Commit](https://img.shields.io/github/last-commit/LJS1124/langgraph-happy-learner)](https://github.com/LJS1124/langgraph-happy-learner/commits/main)

</div>

## 快速入口

| 资源 | 说明 | 链接 |
|---|---|---|
| PDF 原版 | 适合连续阅读的完整书稿 | [LangGraph实战指南.pdf](./LangGraph实战指南.pdf) |
| Markdown 完整版 | 便于检索、引用与二次编辑 | [LangGraph实战指南-完整.md](./book/LangGraph实战指南-Markdown/LangGraph实战指南-完整.md) |
| 按章节拆分版 | 已按前言 + 六大部分拆分 | [章节目录](./book/LangGraph实战指南-Markdown/按部分章节/目录.md) |
| 配套代码 | 按章节整理的练习与案例 | [code/](./code) |

## 仓库结构

```text
.
├── LangGraph实战指南.pdf
├── book/
│   └── LangGraph实战指南-Markdown/
│       ├── LangGraph实战指南-完整.md
│       ├── LangGraph实战指南_assets/
│       │   └── media/                  # 图片资源（与 Markdown 相对路径匹配）
│       └── 按部分章节/
│           ├── 目录.md
│           ├── 第0部分-前言/
│           ├── 第1部分-基础篇/
│           ├── 第2部分-核心篇/
│           ├── 第3部分-实战案例/
│           ├── 第4部分-难点专题/
│           ├── 第5部分-高级特性/
│           └── 第6部分-综合项目/
└── code/
    └── 第XX章/*.py
```

## 学习路线图

```mermaid
flowchart LR
    A["第1部分 基础篇"] --> B["第2部分 核心篇"]
    B --> C["第3部分 实战案例"]
    C --> D["第4部分 难点专题"]
    D --> E["第5部分 高级特性"]
    E --> F["第6部分 综合项目"]
```

## 六大部分一览

| 部分 | 章节 | 重点内容 | 产出导向 |
|---|---|---|---|
| 第1部分 基础篇 | 1-3 | 环境搭建、核心概念、学习目标 | 建立 LangGraph 心智模型 |
| 第2部分 核心篇 | 4-7 | State / Node / Edge / Graph | 能独立构建可维护图流程 |
| 第3部分 实战案例 | 8-10 | MVP 对话、工具调用、多智能体 | 从 Demo 走向可用系统 |
| 第4部分 难点专题 | 11-16 | 状态隔离、通信、死锁、调试 | 解决复杂流程中的稳定性问题 |
| 第5部分 高级特性 | 17-22 | 检查点、HIL、评估、安全、运维 | 面向生产环境的能力完善 |
| 第6部分 综合项目 | 23-26 | 需求到部署全流程 | 完成端到端项目落地 |

## 配套代码覆盖

- 共 `41` 个 Python 示例文件
- 覆盖 `20` 个章节目录
- 代码入口：[`code/README.md`](./code/README.md)

<details>
<summary>展开查看已覆盖章节</summary>

`第01章`、`第03章`、`第04章`、`第05章`、`第06章`、`第07章`、`第08章`、`第09章`、`第10章`、`第11章`、`第12章`、`第13章`、`第14章`、`第15章`、`第17章`、`第18章`、`第20章`、`第21章`、`第22章`、`第25章`

</details>

## 推荐阅读方式

1. 先读 [PDF](./LangGraph实战指南.pdf) 建立全局认知。  
2. 再用 [章节拆分版](./book/LangGraph实战指南-Markdown/按部分章节/目录.md) 按主题精读。  
3. 最后对应 [code/](./code) 逐章运行与改造示例。  

## 运行示例的最小环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U langgraph langchain langchain-openai python-dotenv
```

> 说明：不同章节可能依赖不同模型或中间件（如 Redis / FastAPI），请以章节代码和注释为准。

## 反馈与共建

- 欢迎通过 [Issues](https://github.com/LJS1124/langgraph-happy-learner/issues) 提出勘误、补充案例和优化建议。
- 如果这个仓库对你有帮助，欢迎 Star 支持。
