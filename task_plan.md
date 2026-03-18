# 任务计划

## 目标
构建一个基于 Python 的本地自动化系统：使用 YOLO 做页面目标识别，使用优先级规则 + 行为树做决策，使用桌面 UI 做配置与调试；第一阶段先支持 Windows 下的浏览器/桌面软件按钮流程，后续再扩展到游戏窗口和多场景。

## 当前状态
- 项目目录已完成初始文档与计划落地，并已初始化为本地 Git 仓库。
- 已完成：需求澄清、总体架构设计、设计文档、实施计划、项目级 `CLAUDE.md`。
- 正在进行：阶段 0 的工程骨架实现（Task 4 准备中）。
- Task 1 已完成：Python 3.11 与项目 `.venv` 已可用，已补做 TDD 红测与绿测验证。
- Task 2 已完成：共享配置模型、YAML 加载器、示例场景配置与基础加载测试已落地。
- Task 3 已完成：应用启动入口与结构化日志基线已落地，并完成日志测试。

## 阶段追踪
| 阶段 | 内容 | 状态 | 说明 |
|---|---|---|---|
| 0 | 项目上下文确认 | complete | 已确认当前目录为空，暂无现成代码可复用 |
| 1 | 需求澄清 | complete | 已确认平台、技术栈、MVP 范围与首个真实场景 |
| 2 | 架构设计 | complete | 已确认单体 MVP + 模块化分层方案 |
| 3 | 设计文档写入 | complete | 设计文档将写入 `docs/plans/2026-03-18-yolo-behavior-tree-ui-design.md` |
| 4 | 实施计划写入 | complete | 实施计划将写入 `docs/plans/2026-03-18-yolo-behavior-tree-ui-implementation.md` |
| 5 | 项目说明写入 | complete | 项目级 `CLAUDE.md` 已写入目标、边界与实施顺序 |
| 6 | 进入实现阶段 | in_progress | 已选择子代理开发流程，当前执行 Task 1，但被本机 Python 环境阻塞 |

## 已确认的关键决策
- 技术栈：Python。
- 平台策略：先 Windows 落地，接口预留跨平台。
- 业务推进：先固定流程 MVP，再逐步升级到多目标优先级决策。
- 场景策略：第一版只跑一个真实场景，但配置结构按多场景设计。
- 首个真实场景：浏览器 / 桌面软件按钮点击流程。
- 架构路线：单体 MVP 起步，但内部按 `capture / detector / state / priority / behavior_tree / executor / ui` 分层。

## 风险与注意事项
- 当前目录已初始化为 Git 仓库，并绑定远端 `https://github.com/JensenZz/cheat.git`；但在用户明确要求前，不执行 push。
- 当前最大阻塞是本机缺少可用的 Python 3.11 / pytest，导致无法严格完成 TDD 验证与后续测试驱动实施。
- YOLO 模型训练数据、类别定义、浏览器/桌面窗口适配方案尚未落地，实现阶段需要先固定一个最小样本场景。
- 游戏窗口支持明确属于后续阶段，不纳入第一版 MVP 交付范围。
- Windows 自动化必须加安全保护，例如 dry-run、cooldown、窗口校验与停机按钮。

## 下一步
1. 由用户提供可用的 Python 3.11 解释器或项目虚拟环境。
2. 补做 Task 1 的红测与绿测验证。
3. 处理 Task 1 代码评审中提出的基线问题后，再继续 Task 2。
4. 每完成一个阶段，回写 `findings.md` 与 `progress.md`。

## 错误记录
| 日期 | 错误 | 尝试 | 处理 |
|---|---|---|---|
| 2026-03-18 | `session-catchup.py` 在当前 bash 环境下返回 exit code 49 | 1 | 不重复重试，直接手工建立 `task_plan.md`、`findings.md`、`progress.md` 作为本次会话的持久工作记忆 |
