# 从零开始：Multi-Agent Dev Team with Persistent Learning Memory

## 三个月完整学习计划

---

## 总体说明

- **时间投入**：每天 4 小时，每周 6 天（周日休息 or 弹性补进度），总计约 288 小时
- **节奏**：每天 2 小时学习 + 2 小时写代码，理论和实践交替不脱节
- **每个里程碑结束**：产出可运行的代码 + 一篇笔记/博客草稿
- **最终产出**：GitHub 开源项目 + 一篇深度技术博客 + 一段 5 分钟 Demo 视频

---

## 第一阶段：基础设施（第 1-3 周）

> **目标**：能熟练调用 LLM API，理解 Agent 的基本原理，写出第一个能调工具的简陋 Agent

### 第 1 周：LLM API 与 Tool Calling 打通

**阅读材料：**

| 优先级 | 材料 | 预计时间 |
|--------|------|---------|
| 必读 | [Anthropic API 文档](https://docs.anthropic.com/en/docs) — Tool Use 章节 | 4h |
| 必读 | [OpenAI Function Calling 文档](https://platform.openai.com/docs/guides/function-calling) | 3h |
| 推荐 | [Anthropic 的 Building Effective Agents 博客](https://www.anthropic.com/engineering/building-effective-agents) | 1h |
| 推荐 | Lilian Weng 的 [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) | 2h |

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 搭建 Python 项目骨架，用 `uv` 或 `poetry` 管理依赖，配好 `.env`、`.gitignore`、`README.md` |
| 2 | 跑通 Claude API / OpenAI API 基础调用，理解 message 格式（system/user/assistant） |
| 3 | 实现第一个 Tool Calling：写一个 `get_current_time()` 工具，让 LLM 决定什么时候调用 |
| 4 | 实现多工具调用：加 `search_web()` 和 `calculate()`，看 LLM 如何自动选择+编排 |
| 5 | 实现基本的错误处理：工具调用失败时如何让 LLM 感知并重试 |
| 6 | 整合：做一个 "ask + tool" 循环，Agent 能连续调用多个工具直到完成任务 |

**验收标准**：终端里你问 "帮我查一下北京天气，然后把温度从摄氏度转成华氏度"，Agent 能连续调两个工具给出答案。

### 第 2 周：Agent 核心循环 & Prompt 工程

**阅读材料：**

| 优先级 | 材料 | 预计时间 |
|--------|------|---------|
| 必读 | [ReAct 论文](https://arxiv.org/abs/2210.03629) — Reasoning + Acting | 2h |
| 必读 | [Prompt Engineering Guide](https://www.promptingguide.ai/) — 重点看 Chain-of-Thought 和 Few-shot 章节 | 3h |
| 必读 | [Anthropic Prompt Library](https://docs.anthropic.com/en/prompt-library/library) | 1h |
| 推荐 | [Plan-and-Solve Prompting 论文](https://arxiv.org/abs/2305.04091) | 1h |

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 实现标准的 ReAct Loop：Thought → Action → Observation → Thought → ... → Final Answer |
| 2 | 给 Agent 添加终止条件：最大步数限制、循环检测、超时保护 |
| 3 | 写一个高质量的 system prompt 模板，让 Agent 遵循 ReAct 格式输出 |
| 4 | 实现 Plan-and-Execute 模式：先让 LLM 生成计划，再逐步执行 |
| 5 | 对比 ReAct vs Plan-Execute 在同一个任务上的表现，记录差异 |
| 6 | 封装 Agent 基类，把 ReAct 和 Plan-Execute 两种策略统一接口 |

**验收标准**：同一个复杂任务（"在这个目录里找到所有 Python 文件，统计总行数，把结果保存到 report.txt"），两种策略都能完成，你能说清楚各自优劣。

### 第 3 周：工具系统 & 代码执行沙箱

**阅读材料：**

| 优先级 | 材料 | 预计时间 |
|--------|------|---------|
| 必读 | [E2B Code Interpreter SDK 文档](https://e2b.dev/docs) | 3h |
| 必读 | [Anthropic Tool Use Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/tool-use/overview) | 1h |
| 推荐 | [Gorilla 论文](https://arxiv.org/abs/2305.15334) — LLM 如何学会用 API | 1h |

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 设计工具注册系统：用一个 decorator 把普通函数注册为 Agent 可用的工具 |
| 2 | 实现 Tool Schema 自动生成：从函数签名 + docstring 自动生成 JSON Schema |
| 3 | 给 Dev Agent 添加代码执行能力：集成 E2B sandbox 或本地 Docker |
| 4 | 实现代码执行安全策略：超时限制、网络隔离、输出长度限制 |
| 5 | 实现工具调用日志系统：记录每次工具调用的输入输出，便于调试 |
| 6 | 写 10 个以上工具给 Agent 用（文件读写、shell 执行、web 搜索、JSON 解析等） |

**验收标准**：Agent 能接受"在当前目录创建一个 Flask API 项目，包含一个 hello world 端点"，然后实际创建文件、写代码、跑起来验证。

**🔴 第一阶段里程碑（Week 3 结束）**：
> 一个能调用多种工具、支持 ReAct 和 Plan-Execute 两种策略、可以执行代码的单 Agent 系统。

---

## 第二阶段：记忆系统（第 4-6 周）

> **目标**：给单 Agent 加上完整的记忆系统，这是整个项目最核心的模块

### 第 4 周：短期记忆与上下文管理

**阅读材料：**

| 优先级 | 材料 | 预计时间 |
|--------|------|---------|
| 必读 | [MemGPT 论文](https://arxiv.org/abs/2310.08560) — LLM 操作系统的记忆管理 | 2h |
| 必读 | [Letta (MemGPT) 源码](https://github.com/letta-ai/letta) — 重点看 memory.py 模块 | 3h |
| 必读 | Anthropic 关于 [Context Window 管理](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching) 的文档 | 1h |
| 推荐 | [LangChain Memory 模块文档](https://python.langchain.com/docs/modules/memory/) — 理解现有方案局限 | 2h |

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 通读 Claude Code 的 memory 系统设计（目录结构和系统提示），画一张架构图 |
| 2 | 实现对话历史管理器：滑动窗口、token 计数、智能截断 |
| 3 | 实现对话摘要器：当对话过长时，调用 LLM 将历史对话压缩为摘要 |
| 4 | 实现对话分层存储：最近 N 轮保留原文，更早的保留摘要，最久远的丢弃 |
| 5 | 实现上下文组装器：每次发请求前自动组装 system_prompt + memories + recent_conversation |
| 6 | 测试：模拟 100 轮对话，确保 token 消耗稳定不爆炸，Agent 仍能记住关键信息 |

**验收标准**：Agent 在第 50 轮对话中能正确回忆起第 5 轮你告诉它的偏好。

### 第 5 周：长期记忆 — 分类存储与检索

**阅读材料：**

| 优先级 | 材料 | 预计时间 |
|--------|------|---------|
| 必读 | [ChromaDB 文档](https://docs.trychroma.com/) | 2h |
| 必读 | [RAG 综述](https://arxiv.org/abs/2312.10997) — Retrieval-Augmented Generation 最新进展 | 3h |
| 必读 | [Sentence Transformers 文档](https://www.sbert.net/) — embedding 模型选型 | 1h |
| 推荐 | [Anthropic Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) | 1h |

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 设计记忆数据模型：实现 `Memory` 基类和四种具体类型（`FeedbackMemory`, `ProjectMemory`, `ReferenceMemory`, `UserMemory`） |
| 2 | 实现向量存储：集成 ChromaDB，把记忆内容 embedding 后存入，实现相似度检索 |
| 3 | 实现记忆写入接口：Agent 在执行过程中自动判断"这个信息是否值得存为记忆" |
| 4 | 实现记忆检索接口：给定当前任务，自动检索最相关的记忆并注入 prompt |
| 5 | 实现分层索引：做一个轻量索引层（先查索引再深入），参考 Claude Code 的 MEMORY.md |
| 6 | 实现 `[[memory-link]]` 语法：记忆之间可以互相引用，形成记忆图谱 |

**验收标准**：Agent 完成一个任务后自动存下关键决策记忆，下次做类似任务时能检索并利用之前的经验。

### 第 6 周：记忆演化 — Consolidation, 冲突检测, 衰减

**阅读材料：**

| 优先级 | 材料 | 预计时间 |
|--------|------|---------|
| 必读 | [Generative Agents 论文](https://arxiv.org/abs/2304.03442) — 斯坦福 AI 小镇的记忆系统 | 3h |
| 必读 | Claude Code memory system prompt — 关于"记忆冲突处理"和"衰减"部分（本地文件可用） | 1h |
| 推荐 | [CrewAI 记忆模块源码](https://github.com/crewAIInc/crewAI) — 竞品分析 | 2h |

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 实现记忆 Consolidation：2 条以上相似短期记忆 → 自动合并为 1 条长期记忆 |
| 2 | 实现 Consolidation 的触发条件：时间触发 + 数量触发 + 相似度触发 |
| 3 | 实现冲突检测：新记忆 vs 旧记忆 vs 当前代码状态，三方不一致时标记 STALE |
| 4 | 实现冲突处理策略：自动选择最新信息来源，通知 Agent "你的某条记忆可能过期了" |
| 5 | 实现记忆衰减引擎：不同类型记忆有不同衰减曲线（project 衰减快，reference 衰减慢） |
| 6 | 实现记忆可视化：终端输出当前记忆状态（活跃数、衰减中数、过期数、冲突数） |

**验收标准**：模拟 20 个任务周期，能观察到短期记忆逐渐 consolidation 为长期记忆、过期记忆自动衰减、冲突被检测并标记。

**🔴 第二阶段里程碑（Week 6 结束）**：
> 一个具备完整记忆系统的单 Agent：短期管理、长期存储、分层检索、自动 consolidation、冲突检测、记忆衰减。这是项目最核心的模块，尽量打磨好。

---

## 第三阶段：多 Agent 协作（第 7-9 周）

> **目标**：引入多 Agent 架构，每个 Agent 有独立记忆，Agent 之间可以通信协作

### 第 7 周：多 Agent 架构设计

**阅读材料：**

| 优先级 | 材料 | 预计时间 |
|--------|------|---------|
| 必读 | [AutoGen 论文](https://arxiv.org/abs/2308.08155) — 微软的多 Agent 对话框架 | 2h |
| 必读 | [CrewAI 文档](https://docs.crewai.com/) — 角色化多 Agent 框架 | 2h |
| 必读 | [MetaGPT 论文](https://arxiv.org/abs/2308.00352) — 多 Agent 软件开发团队 | 3h |
| 推荐 | [ChatDev 论文](https://arxiv.org/abs/2307.07924) — 多 Agent 软件公司的组织架构 | 2h |

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 通读 MetaGPT 源码，理解它的 Agent 角色划分和通信机制，写一份分析笔记 |
| 2 | 设计你的 Agent 团队架构：Orchestrator + PM + Architect + Dev + QA 的角色定义 |
| 3 | 实现 Agent 基类重构：让之前的单 Agent 代码支持实例化多个不同角色的 Agent |
| 4 | 实现 Agent 角色系统：每个 Agent 有独立的 system prompt + 能力边界 + 可用工具 |
| 5 | 实现 Orchestrator：调度各 Agent 的工作流程，决定什么任务分配给谁 |
| 6 | 实现多 Agent 的简单串联：需求输入 → PM 写 spec → Dev 写代码 → QA 检查 |

**验收标准**：输入"做一个计算器 CLI"，4 个 Agent 依次协作，产出 spec.md + calculator.py + test_report.md。

### 第 8 周：Agent 间通信与共享记忆

**阅读材料：**

| 优先级 | 材料 | 预计时间 |
|--------|------|---------|
| 必读 | [OpenAI Swarm 源码](https://github.com/openai/swarm) — 轻量多 Agent 协作的实现 | 2h |
| 必读 | [LangGraph Multi-Agent 文档](https://langchain-ai.github.io/langgraph/concepts/multi_agent/) | 2h |
| 推荐 | [Multi-Agent RL 综述](https://arxiv.org/abs/1911.10635) — 了解多智能体理论基础 | 1h |

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 实现消息传递协议：Agent 之间的消息格式（task, review, fix_request, handoff 等） |
| 2 | 实现通信总线（MessageBus）：发布/订阅模式，Agent 可以广播或定向发送消息 |
| 3 | 实现共享记忆空间（TeamMemory）：团队级别的记忆，所有 Agent 都可读写 |
| 4 | 实现记忆隔离：每个 Agent 同时拥有私有记忆（只有自己能读）和共享记忆（团队都能读） |
| 5 | 实现跨 Agent 记忆引用：QA Agent 发现 bug → 写 memory → Dev Agent 下次自动收到提醒 |
| 6 | 实现团队级别的记忆检索：Orchestrator 在分配任务前检索团队历史，避免重复踩坑 |

**验收标准**：QA Agent 发现 Dev 写的代码有 SQL 注入，自动记录 feedback memory，下次 Dev Agent 写新代码时系统自动提醒"注意 SQL 注入"。

### 第 9 周：完整工作流与人工介入

**阅读材料：**

| 优先级 | 材料 | 预计时间 |
|--------|------|---------|
| 必读 | [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) 的 "Human-in-the-loop" 章节 | 1h |
| 必读 | [LangGraph Human-in-the-Loop 文档](https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/) | 2h |

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 设计完整的工作流状态机：INIT → PLANNING → CODING → REVIEWING → TESTING → DONE |
| 2 | 实现工作流引擎：支持并行任务（Architect 和 PM 可并行工作）、条件分支、重试 |
| 3 | 实现人工介入点：在关键决策点暂停等待人类确认（架构选择、代码合并等） |
| 4 | 实现工作流日志与回放：每一步的输入输出都被记录，可以回放整个流程 |
| 5 | 实现失败恢复：某个 Agent 失败后，Orchestrator 可以重试或降级处理 |
| 6 | 整合测试：跑通 5 个不同复杂度的需求，记录每个 Agent 的决策链路 |

**验收标准**：输入一个中等复杂度的需求（"做一个带 JWT 认证的 TODO API"），整个团队自动完成从需求到可运行代码 + 测试的完整流程，且有详细日志。

**🔴 第三阶段里程碑（Week 9 结束）**：
> 一个能协作的四 Agent 开发团队，每个 Agent 有独立记忆，Agent 间有共享记忆空间，支持人工介入，工作流可追溯。

---

## 第四阶段：打磨与面试准备（第 10-12 周）

> **目标**：加上 UI、写好文档、准备面试叙事

### 第 10 周：可视化与交互

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 用 Gradio 搭一个 Web UI：左侧输入需求，中间显示 Agent 工作流实时进度，右侧显示产出文件 |
| 2 | 实现工作流可视化：用流程图实时展示当前进度（哪个 Agent 在工作、状态是什么） |
| 3 | 实现记忆管理面板：查看每个 Agent 的当前记忆状态，手动编辑/删除/强化记忆 |
| 4 | 实现 "记忆对比视图"：选择两个时间点，对比 Agent 团队记忆的演化 |
| 5 | 实现流式输出：Agent 的输出逐 token 显示在 UI 上（体验感翻倍） |
| 6 | UI 美化 + 暗色模式 + 移动端适配 |

**验收标准**：录制一段 3 分钟的使用视频，展示完整的项目交互体验。

### 第 11 周：测试、文档与开源准备

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 写单元测试：记忆模块的 CRUD、检索准确率、consolidation 逻辑 |
| 2 | 写集成测试：完整工作流端到端测试，Mock LLM 调用验证流程正确性 |
| 3 | 写 Agent 评估脚本：同样的需求跑 10 次，统计成功率、步骤数、Bug 率 |
| 4 | 写 README.md：项目介绍、架构图、快速开始、核心特性、Demo GIF |
| 5 | 写一篇深度技术博客（3000-5000 字）："给 AI Agent 加上持久记忆——Multi-Agent Dev Team 的记忆系统设计" |
| 6 | 准备 GitHub：加 License、Contributing.md、Issue 模板、GitHub Actions CI |

### 第 12 周：面试准备与复盘

**每日任务：**

| 天 | 任务 |
|----|------|
| 1 | 录 5 分钟项目 Demo 视频，发布到 B 站/YouTube |
| 2 | 准备 30 秒电梯演讲 + 3 分钟项目介绍 + 15 分钟深度技术问答 |
| 3 | 整理面试必问题清单（见下方），每个问题写 200 字回答 |
| 4 | 找朋友模拟面试，根据反馈调整叙事节奏 |
| 5 | 复盘整个项目：写一份架构决策记录（ADR），记录关键设计选择及其原因 |
| 6 | 发布到技术社区（掘金/V2EX/Reddit/Twitter），收集反馈 |

**🔴 最终产出物清单：**

```
📂 GitHub 仓库
├── README.md            # 项目介绍 + 架构图 + Quick Start
├── docs/
│   ├── architecture.md  # 架构设计文档
│   ├── memory-system.md # 记忆系统设计详解
│   └── adr/             # 架构决策记录
├── src/
│   ├── agents/          # PM, Architect, Dev, QA Agent
│   ├── memory/          # 记忆系统核心模块
│   ├── orchestration/   # Orchestrator + 工作流引擎
│   ├── tools/           # 工具注册与管理
│   └── ui/              # Gradio Web UI
├── tests/
├── blog-post.md         # 技术博客源文件
└── demo.mp4             # 5 分钟 Demo 视频
```

---

## 面试必备问题清单（提前准备）

| # | 问题 | 你的回答要点 |
|---|------|-------------|
| 1 | 为什么不做 LangChain/CrewAI 的 wrapper？ | 为了深入理解 Agent 底层，决定手写核心逻辑；同时现有框架的记忆模块都很薄，我的记忆系统是差异化点 |
| 2 | Agent 的记忆和 RAG 有什么区别？ | RAG 是"查文档"，记忆是"从经验中学习"；记忆有时效性、可信度、演化能力 |
| 3 | 如何保证 Agent 产出的代码质量？ | 多层校验：QA Agent 的静态检查 + 代码执行验证 + 人工介入确认点 |
| 4 | 记忆系统如何避免上下文窗口爆炸？ | 分层索引 + 摘要压缩 + 热温冷分离 + token 预算控制 |
| 5 | 多 Agent 通信为什么选 Publish/Subscribe 模式？ | 解耦 Agent 之间的直接依赖，Orchestrator 统一调度但 Agent 之间也可以直接通信 |
| 6 | 如果 LLM 返回了错误的工具调用格式怎么办？ | 多层容错：JSON 解析重试 + Schema 校验 + 降级策略 |
| 7 | 如何评估记忆系统的效果？ | 设计了 A/B 对比实验：有记忆 vs 无记忆，同样任务集的完成质量和效率差异 |
| 8 | 这个项目最大的技术难点是什么？ | 记忆 Consolidation 的时机和准确度判断——合并太激进丢信息，太保守记忆膨胀 |
| 9 | 如果给这个项目加一个特性，会是什么？ | 记忆的可解释性——让用户理解 Agent 为什么回忆起某条记忆，以及该记忆如何影响当前决策 |
| 10 | 为什么选 Claude/OpenAI API 而不是本地模型？ | 聚焦在 Agent 架构而非模型训练；架构是模型无关的，本地模型可以随时切换 |

---

## 技术博客大纲（建议）

```
标题：给 Multi-Agent 系统装上"记忆"——一个 AI 开发团队的持久学习之路

1. 问题：为什么大多数 Agent 系统"失忆"
2. 灵感：从 Claude Code 的 Memory System 学到什么
3. 设计：四类记忆 × 三层索引 × 热温冷存储
4. 实现：记忆的写入、检索、Consolidation、冲突检测、衰减
5. 实验：有记忆 vs 无记忆的 Agent 团队对比
6. 反思：哪些设计是对的，哪些需要改进
```

---

## 每周时间分配参考

```
周一～周六：
  19:00-21:00  理论学习（读论文/文档/源码）
  21:00-23:00  编码实践（写当天的任务）

周日：
  弹性补进度 or 休息
  如果进度正常：花 1 小时回顾本周产出，写周记
```

---

## 风险提示

1. **API 费用**：三个月调用 LLM API 的费用预估 200-500 元（取决于调用频率和模型选择）。建议前期用 Claude Haiku / OpenAI GPT-4o-mini 等便宜模型调试，关键场景再切贵模型。
2. **遇到卡点不要死磕**：某个技术点卡住 2 天以上，先跳过，后面理解深了回来看往往豁然开朗。
3. **保持 GitHub 绿点**：从第一天起就每天 commit，三个月后 GitHub 贡献图本身就是简历亮点。
4. **写博客不要等到最后**：每阶段结束时写一篇阶段总结，最后整理成大文章比一次性写轻松得多。
