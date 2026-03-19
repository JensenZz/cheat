# 项目说明

## 项目目标
构建一个使用 **YOLO + 行为树 + UI 界面 + 可配置策略系统** 的本地自动化平台，用于识别页面后自动操作鼠标键盘。

第一阶段聚焦：
- Windows 环境
- 浏览器 / 桌面软件页面自动化
- 单场景真实流程跑通

后续阶段扩展：
- 多目标优先级决策
- 多场景切换
- 游戏窗口支持
- OCR / 模板匹配融合
- 更强的调试与策略编辑能力

## 当前确认范围
- 技术栈：Python
- 平台：先 Windows，接口预留跨平台
- 推进方式：先固定流程 MVP，再逐步增强为动态优先级决策
- 第一版场景：浏览器 / 桌面软件按钮点击流程
- 第一版范围：单场景可运行，但配置结构按多场景设计

## 当前方向调整
- 当前项目不再以“只读 preview 收口”作为最终目标，而是转为“可研究 YOLO 与自动化的全流程项目”。
- 执行链路按 `preview / dry_run / live` 三种模式推进：默认安全启动为 `preview`，逐步扩展到 `dry_run` 与 `live`。
- `executor`、`ocr`、模拟器与底层驱动能力采用“可选后端 + Windows-only 插件化”设计，避免一次性把高风险能力塞进主链路。
- 继续坚持 clean-room 实现：只参考结构与思路，不复制外部仓库代码或资源。

## 架构原则
- 采用“单体 MVP + 模块化分层”方案。
- 检测、状态建模、优先级决策、行为树调度、执行器、UI 必须分层。
- 策略尽量配置化，不把规则直接写死在业务代码里。
- 第一版优先保证：可运行、可观察、可调试、可扩展。
- 不为了未来假设过度设计；先跑通 MVP，再按阶段增强。

## 计划中的核心模块
- `src/auto_ops/capture`：截图与窗口绑定
- `src/auto_ops/detector`：YOLO 推理与识别结果标准化
- `src/auto_ops/state`：页面状态建模
- `src/auto_ops/priority`：候选目标过滤、打分与排序
- `src/auto_ops/behavior_tree`：流程与节点调度
- `src/auto_ops/executor`：鼠标键盘执行与安全保护
- `src/auto_ops/ui`：运行控制、画面预览、参数编辑、日志展示
- `strategies/scenes`：场景配置

## 当前实施顺序
1. 阶段 0：范围重置与模式定义（`preview / dry_run / live`、后端字段、默认安全启动）
2. 阶段 1：单窗口真实链路 MVP（真实截图 + YOLO/FakeDetector + 标准 Windows 执行后端）
3. 阶段 2：OCR 服务层与批量识别
4. 阶段 3：多窗口调度
5. 阶段 4：模拟器后端
6. 阶段 5：底层输入驱动 / 拦截实验后端

## 第一版必须有
- 窗口绑定
- 截图采集
- YOLO 识别
- 单场景配置
- 基础点击 / 输入执行
- 简单 UI
- 日志输出

## 第一版不要提前做
- 复杂可视化行为树编辑器
- 完整跨平台支持
- 自学习策略
- 双进程或分布式架构
- 过早适配大量场景

## 工作约定
- 所有新增设计与计划文档优先使用中文。
- 优先使用 TDD，先写失败测试，再写最小实现。
- 每完成一个阶段，都更新 `task_plan.md`、`findings.md`、`progress.md`。
- 如果当前目录还不是 Git 仓库，不主动初始化；是否启用版本控制由用户决定。
- 后续实施以 `docs/plans/2026-03-18-yolo-behavior-tree-ui-implementation.md` 为主执行依据。

## Mac 开发约束
- 允许在 Mac 上继续开发纯 Python 逻辑、配置加载、状态建模、优先级决策、行为树、伪检测器、UI 非 Windows 绑定部分、单元测试与文档。
- Mac 上新增代码必须优先依赖抽象接口，不得把窗口绑定、真实截图、真实鼠标键盘执行直接写死到跨平台公共模块中。
- Windows 专属实现必须收敛在 `capture/windows.py`、`executor/windows.py`、后续 `detector` 或平台适配层中，避免影响 Mac 上的开发与测试。
- 在 Mac 上默认只做 `dry_run`、伪检测器、纯逻辑集成与 UI 状态流验证；真实窗口绑定、真实输入执行、Windows API 联调统一放回 Windows 环境完成。
- 新增依赖时优先保证跨平台；若依赖仅支持 Windows，必须使用平台条件依赖或延迟导入，确保仓库在 Mac 上仍可安装、导入并运行非 Windows 测试。
- 默认开发安装以纯逻辑依赖为主；真实 UI、YOLO、自动化执行依赖放入可选依赖组，由需要的平台显式安装。

## 关键文档
- 设计文档：`docs/plans/2026-03-18-yolo-behavior-tree-ui-design.md`
- 实施计划：`docs/plans/2026-03-18-yolo-behavior-tree-ui-implementation.md`
- 工作记忆：`task_plan.md`、`findings.md`、`progress.md`
