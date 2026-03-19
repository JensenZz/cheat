# 任务计划

## 目标
构建一个基于 Python 的本地自动化系统：使用 YOLO 做页面目标识别，使用优先级规则 + 行为树做决策，使用桌面 UI 做配置与调试；第一阶段先支持 Windows 下的浏览器/桌面软件按钮流程，后续再扩展到游戏窗口和多场景。

## 当前状态
- 项目目录已完成初始文档与计划落地，并已初始化为本地 Git 仓库。
- 已完成：需求澄清、总体架构设计、设计文档、实施计划、项目级 `CLAUDE.md`。
- 当前安全版 MVP 已完成一轮实现与验证，并补齐 UI preview 展示、preview→UiState 组装、只读启动链路、默认演示 preview 收口，以及启动稳定性加固。
- Task 38 已完成：默认 demo 场景改为包内资源加载，UI 启动器持有主窗口引用，降低打包与启动生命周期风险。
- Task 37 已完成：默认启动会展示一条演示 preview 摘要，避免 UI 只停留在 Ready。
- Task 36 已完成：启动入口已接通只读 preview 链路，组装 `UiState` 后进入 UI 事件循环，不接真实输入执行。
- Task 34 已完成：`build_ui_state()` 已把 `PreviewCycleResult` 组装为 `UiState`，供 UI 层消费 preview 结果，不接真实输入执行。
- Task 33 已完成：UiState / MainWindow / build_ui 已接通 preview 展示，仅展示 observe_only / blocking / planned action，不接真实输入执行。
- Task 14 已完成安全版验证收口：补齐 preview 集成验证与当前 MVP 回归命令基线。
- Task 13 已完成安全替代版：已接通 observe_only 配置、UI 观察态与 preview 预览链路，不接通真实输入执行。
- Task 12 已完成：PySide6 UI MVP 骨架已落地，并补齐可选依赖延迟导入与启动保活验证。
- Task 11 已完成：YOLO 适配器与检测结果标准化已落地，并完成边界测试与当前阶段回归验证。
- Task 1 已完成：Python 3.11 与项目 `.venv` 已可用，已补做 TDD 红测与绿测验证。
- Task 2 已完成：共享配置模型、YAML 加载器、示例场景配置与基础加载测试已落地。
- Task 3 已完成：应用启动入口与结构化日志基线已落地，并完成日志测试。
- Task 4 已完成：检测结果模型、伪检测器接口与对应测试已落地。
- Task 5 已完成：窗口快照与采集接口骨架已落地。
- Task 6 已完成：页面状态建模与阻塞目标识别规则已落地，并完成相关测试。
- Task 7 已完成：优先级打分与候选目标选择已落地，并完成基础优先级测试。
- Task 8 已完成：最小行为树节点与顺序执行逻辑已落地，并完成基础行为树测试。
- Task 9 已完成：安全执行结果模型与 Windows dry-run 点击执行器已落地，并完成基础执行器测试。
- Task 10 已完成：主循环编排引擎已串联 capture、detector、state、priority 与 executor，并完成基础编排测试。

## 阶段追踪
| 阶段 | 内容 | 状态 | 说明 |
|---|---|---|---|
| 0 | 项目上下文确认 | complete | 已确认当前目录为空，暂无现成代码可复用 |
| 1 | 需求澄清 | complete | 已确认平台、技术栈、MVP 范围与首个真实场景 |
| 2 | 架构设计 | complete | 已确认单体 MVP + 模块化分层方案 |
| 3 | 设计文档写入 | complete | 设计文档将写入 `docs/plans/2026-03-18-yolo-behavior-tree-ui-design.md` |
| 4 | 实施计划写入 | complete | 实施计划将写入 `docs/plans/2026-03-18-yolo-behavior-tree-ui-implementation.md` |
| 5 | 项目说明写入 | complete | 项目级 `CLAUDE.md` 已写入目标、边界与实施顺序 |
| 6 | 进入实现阶段 | in_progress | 已选择子代理开发流程，当前已完成 Task 1~14 的安全版收口，可进入下一轮需求确认或整理提交 |

## 已确认的关键决策
- 技术栈：Python。
- 平台策略：先 Windows 落地，接口预留跨平台。
- 业务推进：先固定流程 MVP，再逐步升级到多目标优先级决策。
- 场景策略：第一版只跑一个真实场景，但配置结构按多场景设计。
- 首个真实场景：浏览器 / 桌面软件按钮点击流程。
- 架构路线：单体 MVP 起步，但内部按 `capture / detector / state / priority / behavior_tree / executor / ui` 分层。

## 风险与注意事项
- 当前目录已初始化为 Git 仓库，并绑定远端 `https://github.com/JensenZz/cheat.git`；当前已完成首次 push，后续提交仍需按用户指令执行。
- 当前测试应统一使用项目 `.venv` 解释器：`I:/work/cheat/.venv/Scripts/python.exe`，避免系统 Python 缺少依赖导致误判。
- YOLO 模型训练数据、类别定义、浏览器/桌面窗口适配方案尚未落地，实现阶段需要先固定一个最小样本场景。
- 游戏窗口支持明确属于后续阶段，不纳入第一版 MVP 交付范围。
- Windows 自动化必须加安全保护，例如 dry-run、cooldown、窗口校验与停机按钮。

## 下一步
1. 当前安全版 MVP 已完成一轮实现与验证，可根据需要整理提交或确认下一阶段范围。
2. 继续保持 TDD：先写失败测试，再做最小实现与回归验证。
3. 每完成一个阶段，回写 `findings.md` 与 `progress.md`。
4. 后续在 Mac 上继续开发时，优先推进纯逻辑模块与非平台绑定测试。

## 错误记录
| 日期 | 错误 | 尝试 | 处理 |
|---|---|---|---|
| 2026-03-18 | `session-catchup.py` 在当前 bash 环境下返回 exit code 49 | 1 | 不重复重试，直接手工建立 `task_plan.md`、`findings.md`、`progress.md` 作为本次会话的持久工作记忆 |
