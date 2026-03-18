# 发现记录

## 项目上下文
- 当前工作目录：`I:\work\cheat`
- 当前目录为空。
- 当前目录已初始化为 Git 仓库，并绑定远端 `https://github.com/JensenZz/cheat.git`。
- 远端仓库当前为空仓库。
- 已补齐项目说明、设计文档、实施计划与最基础的工程结构。

## 已确认需求
- 目标系统：YOLO + 行为树 + UI 界面 + 可配置策略系统。
- 功能目标：识别页面后自动执行鼠标键盘操作。
- 长期目标：多目标优先级决策，支持更复杂自动化流程。
- 场景范围：浏览器 / 桌面软件 + 游戏窗口都要支持。
- MVP 策略：先做浏览器 / 桌面软件按钮点击流程，后续再扩展到游戏窗口。

## 已确认技术路线
- 语言：Python。
- 平台：先 Windows，接口保留跨平台扩展点。
- 架构：单体 MVP + 模块化分层。
- 决策：优先级系统负责“多个目标先处理谁”，行为树负责“当前流程该做什么”。

## 推荐模块划分
- `capture`：截图与窗口绑定。
- `detector`：YOLO 推理与检测结果标准化。
- `state`：页面状态建模。
- `priority`：多目标候选过滤、打分与排序。
- `behavior_tree`：策略流程控制。
- `executor`：鼠标键盘与窗口相关操作。
- `ui`：配置、监控、调试、日志展示。

## UI / 调试结论
- 第一版 UI 不追求复杂编辑器，先做“可运行 + 可观察 + 可调参数”的控制台。
- 建议优先使用 `PySide6`。
- 从第一版开始保留日志、单步运行、只识别不执行、关键帧保存等调试能力。

## 当前文档产物
- 设计文档：`docs/plans/2026-03-18-yolo-behavior-tree-ui-design.md`
- 实施计划：`docs/plans/2026-03-18-yolo-behavior-tree-ui-implementation.md`
- 项目说明：`CLAUDE.md`

## 当前实现发现
- Task 1 已落地文件：`pyproject.toml`、`src/auto_ops/__init__.py`、`tests/conftest.py`、`tests/test_import_app.py`。
- 当前环境中的 `python` / `python3` 都指向 WindowsApps 占位入口，不是可用解释器。
- 进一步确认这两个入口实际都链接到 `AppInstallerPythonRedirector.exe`，说明系统当前只是安装了 Microsoft Store 的 Python 重定向器，并没有发现真实 Python 解释器。
- `py`、`pytest`、项目 `.venv` 解释器都未找到。
- 当前已安装可用 Python 3.11.9，`python` 与 `py` 都可正常使用。
- 项目虚拟环境已创建：`I:/work/cheat/.venv`，并已安装 `pytest`。
- Task 1 已通过补做 TDD 完成验证：临时移开 `src/auto_ops` 后红测得到 `ModuleNotFoundError`，恢复实现后绿测通过（`1 passed`）。
- `pyproject.toml` 已补齐更稳妥的 `src` 布局打包发现配置。
- Task 2 已新增配置建模基础：`ActionType`、`WindowMatch`、`CaptureConfig`、`TargetRule`、`SceneConfig`、`SceneBundle`。
- 已实现 `load_scene(path)`，当前兼容两种 targets 结构：顶层 `targets` 与 `scene.targets`。
- 已新增示例场景配置：`strategies/scenes/browser_demo.yaml`。
- Task 2 的最小测试 `tests/config/test_loader.py` 已完成红测与绿测，当前通过（`1 passed`）。
- Task 3 已新增 `build_logger(name)` 与应用入口 `main()`。
- 当前 `build_logger()` 使用 `logging.basicConfig(...)` 初始化基础日志格式，并显式设置 `logger.setLevel(logging.INFO)` 以兼容 pytest `caplog` 捕获。
- Task 3 的最小测试 `tests/test_logging_setup.py` 已完成红测与绿测，当前通过（`1 passed`）。
- Task 4 已新增检测结果基础模型与伪检测器接口：`src/auto_ops/shared/models.py`、`src/auto_ops/detector/base.py`、`src/auto_ops/detector/fake.py`、`tests/detector/test_fake_detector.py`。
- Task 4 首轮规格复核发现 3 个偏差：`Detection.bbox` 被实现为 `list`、`center` 按 `x/y/width/height` 语义计算、`Detector` 在 `shared/models.py` 中重复定义。
- Task 4 经 TDD 回修后，`Detection.bbox` 已收敛为 `tuple[int, int, int, int]`，`center` 已按 `x1/y1/x2/y2` 语义计算，`Detector` 仅保留在 `src/auto_ops/detector/base.py`。
- `FakeDetector` 当前会深拷贝 seeded 输入，避免外部修改污染检测结果；`Detection` 额外校验 `x2 >= x1` 与 `y2 >= y1`，非法 bbox 会抛出校验错误。
- Task 4 本地验证命令 `python3 -m pytest tests/detector/test_fake_detector.py -v` 当前结果为 `5 passed`，但运行解释器仍是系统 `Python 3.9.6`，后续建议在项目要求的 Python 3.11+ 环境补跑一次完整验证。
- Task 5 已新增采集接口骨架：`src/auto_ops/capture/base.py`、`src/auto_ops/capture/windows.py`、`tests/capture/test_window_capture.py`。
- 由于 `src/auto_ops/shared/models.py` 已存在 `WindowSnapshot`，`src/auto_ops/capture/windows.py` 当前采用重导出方案暴露 `WindowSnapshot`，满足 `from auto_ops.capture.windows import WindowSnapshot` 的计划接口要求，避免重复定义模型。
- Task 5 代码质量回修后，`WindowSnapshot` 已改为 `@dataclass(frozen=True)`，并将 `image` 字段从 `Any` 收窄为 `object`，使其更适合作为跨模块共享的不可变快照值对象。
- `Detection` 现已补充 `confidence` 范围校验，要求输入必须位于 `[0.0, 1.0]`；对应非法置信度测试已补齐。
- Task 5 相关独立验证命令 `python3 -m pytest tests/detector/test_fake_detector.py tests/capture/test_window_capture.py -v` 当前结果为 `9 passed`，可作为继续 Task 6 的最新证据。
