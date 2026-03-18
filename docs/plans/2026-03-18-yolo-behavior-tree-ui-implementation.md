# YOLO + 行为树 + UI 自动化系统 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建一个以 Windows 为首发平台的 Python MVP：能够绑定浏览器/桌面软件窗口，执行截图、YOLO 检测、多目标优先级选择、行为树流程调度、安全鼠标键盘操作，并通过 PySide6 UI 做配置与调试。

**Architecture:** 项目先采用单进程单体结构，但内部严格按 `capture / detector / state / priority / behavior_tree / executor / ui / config` 分层。所有自动化流程都遵循“截图 → 检测 → 状态建模 → 优先级选择 → 行为树决策 → 执行动作 → 日志反馈”的闭环，并优先以 YAML 配置驱动，避免把策略硬编码到业务流程中。

**Tech Stack:** Python 3.11、pytest、PyYAML、pydantic、ultralytics、mss、pywin32、pyautogui、PySide6、numpy

---

## 实施前提
- 当前目录还不是 Git 仓库。执行本计划时：
  - **如果用户先初始化 Git**，按每个任务的提交步骤创建新提交。
  - **如果用户不初始化 Git**，每个任务完成后把检查点写入 `progress.md`。
- 先实现浏览器 / 桌面软件单场景 MVP。
- 游戏窗口适配、OCR、模板匹配、复杂行为树编辑器都放到 MVP 之后。
- 所有实现先写失败测试，再写最小实现，再跑测试。

## 目标目录结构
```text
I:/work/cheat/
├─ CLAUDE.md
├─ task_plan.md
├─ findings.md
├─ progress.md
├─ pyproject.toml
├─ src/
│  └─ auto_ops/
│     ├─ __init__.py
│     ├─ app.py
│     ├─ logging.py
│     ├─ shared/
│     │  ├─ models.py
│     │  └─ enums.py
│     ├─ config/
│     │  ├─ models.py
│     │  └─ loader.py
│     ├─ capture/
│     │  ├─ base.py
│     │  └─ windows.py
│     ├─ detector/
│     │  ├─ base.py
│     │  ├─ fake.py
│     │  └─ yolo.py
│     ├─ state/
│     │  └─ builder.py
│     ├─ priority/
│     │  └─ scorer.py
│     ├─ behavior_tree/
│     │  ├─ nodes.py
│     │  └─ runner.py
│     ├─ executor/
│     │  ├─ base.py
│     │  └─ windows.py
│     ├─ orchestrator/
│     │  └─ engine.py
│     └─ ui/
│        ├─ app.py
│        ├─ main_window.py
│        └─ view_model.py
├─ strategies/
│  └─ scenes/
│     └─ browser_demo.yaml
└─ tests/
   ├─ conftest.py
   ├─ config/
   ├─ capture/
   ├─ detector/
   ├─ state/
   ├─ priority/
   ├─ behavior_tree/
   ├─ executor/
   ├─ orchestrator/
   └─ ui/
```

---

### Task 1: 初始化 Python 工程与测试基线

**Files:**
- Create: `pyproject.toml`
- Create: `src/auto_ops/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_import_app.py`

**Step 1: Write the failing test**

```python
from importlib import import_module


def test_package_imports():
    module = import_module("auto_ops")
    assert module.__package__ == "auto_ops"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_import_app.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'auto_ops'`

**Step 3: Write minimal implementation**

`pyproject.toml`
```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "auto-ops"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "PyYAML>=6.0.1",
  "pydantic>=2.11.0",
  "mss>=9.0.1",
  "numpy>=2.0.0",
  "ultralytics>=8.3.0",
  "pywin32>=308",
  "pyautogui>=0.9.54",
  "PySide6>=6.8.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.3.0", "pytest-qt>=4.4.0"]

[tool.pytest.ini_options]
pythonpath = ["src"]
```

`src/auto_ops/__init__.py`
```python
__all__ = ["__version__"]
__version__ = "0.1.0"
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_import_app.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add pyproject.toml src/auto_ops/__init__.py tests/test_import_app.py tests/conftest.py
git commit -m "chore: bootstrap auto ops package"
```
Otherwise: append `Task 1 complete` to `progress.md`.

---

### Task 2: 建立共享数据模型与配置加载器

**Files:**
- Create: `src/auto_ops/shared/enums.py`
- Create: `src/auto_ops/shared/models.py`
- Create: `src/auto_ops/config/models.py`
- Create: `src/auto_ops/config/loader.py`
- Create: `strategies/scenes/browser_demo.yaml`
- Create: `tests/config/test_loader.py`

**Step 1: Write the failing test**

```python
from auto_ops.config.loader import load_scene


def test_load_scene_returns_parsed_models(tmp_path):
    config = tmp_path / "scene.yaml"
    config.write_text(
        """
scene:
  id: browser-demo
  name: Browser Demo
  window_match:
    title_contains: ["Demo"]
  capture_config:
    fps: 2
  targets:
    - class_name: primary_button
      min_confidence: 0.6
      weight: 80
      cooldown_ms: 1000
""".strip(),
        encoding="utf-8",
    )

    scene = load_scene(config)

    assert scene.scene.id == "browser-demo"
    assert scene.targets[0].class_name == "primary_button"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/config/test_loader.py -v`
Expected: FAIL with `ModuleNotFoundError` or `ImportError`

**Step 3: Write minimal implementation**

`src/auto_ops/shared/enums.py`
```python
from enum import StrEnum


class ActionType(StrEnum):
    CLICK = "click"
    INPUT_TEXT = "input_text"
    WAIT = "wait"
    FOCUS_WINDOW = "focus_window"
```

`src/auto_ops/config/models.py`
```python
from pydantic import BaseModel, Field


class WindowMatch(BaseModel):
    title_contains: list[str] = Field(default_factory=list)


class CaptureConfig(BaseModel):
    fps: int = 2


class TargetRule(BaseModel):
    class_name: str
    min_confidence: float
    weight: int
    cooldown_ms: int = 0


class SceneConfig(BaseModel):
    id: str
    name: str
    window_match: WindowMatch
    capture_config: CaptureConfig


class SceneBundle(BaseModel):
    scene: SceneConfig
    targets: list[TargetRule]
```

`src/auto_ops/config/loader.py`
```python
from pathlib import Path
import yaml
from auto_ops.config.models import SceneBundle


def load_scene(path: Path) -> SceneBundle:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return SceneBundle(scene=data["scene"], targets=data.get("targets", []))
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/config/test_loader.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/shared/enums.py src/auto_ops/shared/models.py src/auto_ops/config/models.py src/auto_ops/config/loader.py strategies/scenes/browser_demo.yaml tests/config/test_loader.py
git commit -m "feat: add scene config loader"
```
Otherwise: append `Task 2 complete` to `progress.md`.

---

### Task 3: 建立应用设置与结构化日志

**Files:**
- Create: `src/auto_ops/logging.py`
- Create: `src/auto_ops/app.py`
- Create: `tests/test_logging_setup.py`

**Step 1: Write the failing test**

```python
from auto_ops.logging import build_logger


def test_build_logger_writes_named_logger(caplog):
    logger = build_logger("auto_ops.test")
    logger.info("hello")
    assert any(record.name == "auto_ops.test" for record in caplog.records)
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_logging_setup.py -v`
Expected: FAIL because `build_logger` does not exist

**Step 3: Write minimal implementation**

`src/auto_ops/logging.py`
```python
import logging


def build_logger(name: str) -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
    return logging.getLogger(name)
```

`src/auto_ops/app.py`
```python
from auto_ops.logging import build_logger


def main() -> int:
    build_logger("auto_ops").info("app boot")
    return 0
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_logging_setup.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/logging.py src/auto_ops/app.py tests/test_logging_setup.py
git commit -m "feat: add app logging bootstrap"
```
Otherwise: append `Task 3 complete` to `progress.md`.

---

### Task 4: 建立检测结果与伪检测器接口

**Files:**
- Create: `src/auto_ops/shared/models.py`
- Create: `src/auto_ops/detector/base.py`
- Create: `src/auto_ops/detector/fake.py`
- Create: `tests/detector/test_fake_detector.py`

**Step 1: Write the failing test**

```python
from auto_ops.detector.fake import FakeDetector


def test_fake_detector_returns_seeded_detections():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": [10, 10, 50, 30]}
    ])

    detections = detector.detect(image=None)

    assert len(detections) == 1
    assert detections[0].class_name == "primary_button"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/detector/test_fake_detector.py -v`
Expected: FAIL because detector module does not exist

**Step 3: Write minimal implementation**

`src/auto_ops/shared/models.py`
```python
from dataclasses import dataclass

from pydantic import BaseModel


@dataclass(slots=True)
class WindowSnapshot:
    title: str
    region: tuple[int, int, int, int]
    image: object


class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]

    @property
    def center(self) -> tuple[int, int]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)
```

`src/auto_ops/detector/base.py`
```python
from typing import Protocol
from auto_ops.shared.models import Detection


class Detector(Protocol):
    def detect(self, image) -> list[Detection]: ...
```

`src/auto_ops/detector/fake.py`
```python
from auto_ops.shared.models import Detection


class FakeDetector:
    def __init__(self, seeded: list[dict]):
        self._seeded = seeded

    def detect(self, image) -> list[Detection]:
        return [Detection(**item) for item in self._seeded]
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/detector/test_fake_detector.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/shared/models.py src/auto_ops/detector/base.py src/auto_ops/detector/fake.py tests/detector/test_fake_detector.py
git commit -m "feat: add detector abstractions"
```
Otherwise: append `Task 4 complete` to `progress.md`.

---

### Task 5: 建立窗口匹配与截图采集接口

**Files:**
- Create: `src/auto_ops/capture/base.py`
- Create: `src/auto_ops/capture/windows.py`
- Create: `tests/capture/test_window_capture.py`

**Step 1: Write the failing test**

```python
from auto_ops.capture.windows import WindowSnapshot


def test_window_snapshot_exposes_region():
    snapshot = WindowSnapshot(title="Demo", region=(0, 0, 800, 600), image=None)
    assert snapshot.region == (0, 0, 800, 600)
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/capture/test_window_capture.py -v`
Expected: FAIL because capture module does not exist

**Step 3: Write minimal implementation**

`src/auto_ops/capture/base.py`
```python
from typing import Protocol
from auto_ops.shared.models import WindowSnapshot


class CaptureBackend(Protocol):
    def locate(self): ...
    def grab(self) -> WindowSnapshot: ...
```

`src/auto_ops/capture/windows.py`
```python
from dataclasses import dataclass


@dataclass(slots=True)
class WindowSnapshot:
    title: str
    region: tuple[int, int, int, int]
    image: object
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/capture/test_window_capture.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/capture/base.py src/auto_ops/capture/windows.py tests/capture/test_window_capture.py
git commit -m "feat: add capture interfaces"
```
Otherwise: append `Task 5 complete` to `progress.md`.

---

### Task 6: 把检测结果转换为页面状态

**Files:**
- Create: `src/auto_ops/state/builder.py`
- Create: `tests/state/test_builder.py`

**Step 1: Write the failing test**

```python
from auto_ops.shared.models import Detection
from auto_ops.state.builder import build_state


def test_build_state_marks_blocking_popup():
    detections = [
        Detection(class_name="popup_close", confidence=0.95, bbox=(10, 10, 40, 40)),
        Detection(class_name="primary_button", confidence=0.91, bbox=(50, 50, 120, 90)),
    ]

    state = build_state(detections)

    assert state.has_blocking_target is True
    assert len(state.visible_targets) == 2
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/state/test_builder.py -v`
Expected: FAIL because `build_state` does not exist

**Step 3: Write minimal implementation**

`src/auto_ops/state/builder.py`
```python
from pydantic import BaseModel, Field
from auto_ops.shared.models import Detection


class RuntimeState(BaseModel):
    visible_targets: list[Detection] = Field(default_factory=list)
    has_blocking_target: bool = False
    last_action: str | None = None
    failure_count: int = 0


def build_state(detections: list[Detection]) -> RuntimeState:
    blocking = any(item.class_name.startswith("popup") for item in detections)
    return RuntimeState(visible_targets=detections, has_blocking_target=blocking)
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/state/test_builder.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/state/builder.py tests/state/test_builder.py
git commit -m "feat: add runtime state builder"
```
Otherwise: append `Task 6 complete` to `progress.md`.

---

### Task 7: 实现优先级打分与候选目标选择

**Files:**
- Create: `src/auto_ops/priority/scorer.py`
- Create: `tests/priority/test_scorer.py`

**Step 1: Write the failing test**

```python
from auto_ops.shared.models import Detection
from auto_ops.priority.scorer import pick_best_target


def test_pick_best_target_prefers_blocking_popup():
    detections = [
        Detection(class_name="primary_button", confidence=0.92, bbox=(50, 50, 120, 90)),
        Detection(class_name="popup_close", confidence=0.88, bbox=(10, 10, 40, 40)),
    ]
    weights = {"primary_button": 80, "popup_close": 100}

    best = pick_best_target(detections, weights)

    assert best.class_name == "popup_close"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/priority/test_scorer.py -v`
Expected: FAIL because scorer module does not exist

**Step 3: Write minimal implementation**

`src/auto_ops/priority/scorer.py`
```python
from auto_ops.shared.models import Detection


def score_target(target: Detection, weights: dict[str, int]) -> float:
    return weights.get(target.class_name, 0) + target.confidence


def pick_best_target(targets: list[Detection], weights: dict[str, int]) -> Detection | None:
    if not targets:
        return None
    return max(targets, key=lambda item: score_target(item, weights))
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/priority/test_scorer.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/priority/scorer.py tests/priority/test_scorer.py
git commit -m "feat: add target priority scoring"
```
Otherwise: append `Task 7 complete` to `progress.md`.

---

### Task 8: 实现最小行为树运行时

**Files:**
- Create: `src/auto_ops/behavior_tree/nodes.py`
- Create: `src/auto_ops/behavior_tree/runner.py`
- Create: `tests/behavior_tree/test_runner.py`

**Step 1: Write the failing test**

```python
from auto_ops.behavior_tree.nodes import ActionNode, ConditionNode, SequenceNode


def test_sequence_stops_on_failed_condition():
    calls = []
    tree = SequenceNode([
        ConditionNode(lambda state: False),
        ActionNode(lambda state: calls.append("clicked") or True),
    ])

    result = tree.tick({})

    assert result is False
    assert calls == []
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/behavior_tree/test_runner.py -v`
Expected: FAIL because node classes do not exist

**Step 3: Write minimal implementation**

`src/auto_ops/behavior_tree/nodes.py`
```python
class ConditionNode:
    def __init__(self, predicate):
        self.predicate = predicate

    def tick(self, state):
        return bool(self.predicate(state))


class ActionNode:
    def __init__(self, fn):
        self.fn = fn

    def tick(self, state):
        return bool(self.fn(state))


class SequenceNode:
    def __init__(self, children):
        self.children = children

    def tick(self, state):
        for child in self.children:
            if not child.tick(state):
                return False
        return True
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/behavior_tree/test_runner.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/behavior_tree/nodes.py src/auto_ops/behavior_tree/runner.py tests/behavior_tree/test_runner.py
git commit -m "feat: add minimal behavior tree runtime"
```
Otherwise: append `Task 8 complete` to `progress.md`.

---

### Task 9: 实现安全执行器与 dry-run 模式

**Files:**
- Create: `src/auto_ops/executor/base.py`
- Create: `src/auto_ops/executor/windows.py`
- Create: `tests/executor/test_windows_executor.py`

**Step 1: Write the failing test**

```python
from auto_ops.executor.windows import WindowsExecutor


def test_windows_executor_records_dry_run_click():
    executor = WindowsExecutor(dry_run=True)

    result = executor.click((100, 200))

    assert result.ok is True
    assert result.performed is False
    assert result.action == "click"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/executor/test_windows_executor.py -v`
Expected: FAIL because executor does not exist

**Step 3: Write minimal implementation**

`src/auto_ops/executor/base.py`
```python
from pydantic import BaseModel


class ExecutionResult(BaseModel):
    action: str
    ok: bool
    performed: bool
    detail: str = ""
```

`src/auto_ops/executor/windows.py`
```python
from auto_ops.executor.base import ExecutionResult


class WindowsExecutor:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def click(self, point: tuple[int, int]) -> ExecutionResult:
        if self.dry_run:
            return ExecutionResult(action="click", ok=True, performed=False, detail=str(point))
        import pyautogui
        pyautogui.click(*point)
        return ExecutionResult(action="click", ok=True, performed=True, detail=str(point))
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/executor/test_windows_executor.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/executor/base.py src/auto_ops/executor/windows.py tests/executor/test_windows_executor.py
git commit -m "feat: add safe windows executor"
```
Otherwise: append `Task 9 complete` to `progress.md`.

---

### Task 10: 串起主循环编排引擎

**Files:**
- Create: `src/auto_ops/orchestrator/engine.py`
- Create: `tests/orchestrator/test_engine.py`

**Step 1: Write the failing test**

```python
from auto_ops.capture.windows import WindowSnapshot
from auto_ops.detector.fake import FakeDetector
from auto_ops.orchestrator.engine import run_cycle
from auto_ops.executor.windows import WindowsExecutor


class FakeCapture:
    def grab(self):
        return WindowSnapshot(title="Demo", region=(0, 0, 800, 600), image=None)


def test_run_cycle_selects_and_clicks_best_target():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": (10, 10, 50, 30)},
    ])
    executor = WindowsExecutor(dry_run=True)

    result = run_cycle(FakeCapture(), detector, executor, {"primary_button": 80})

    assert result.selected_target.class_name == "primary_button"
    assert result.execution.action == "click"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/orchestrator/test_engine.py -v`
Expected: FAIL because `run_cycle` does not exist

**Step 3: Write minimal implementation**

`src/auto_ops/orchestrator/engine.py`
```python
from pydantic import BaseModel
from auto_ops.state.builder import build_state
from auto_ops.priority.scorer import pick_best_target


class CycleResult(BaseModel):
    selected_target: object | None
    execution: object | None


def run_cycle(capture, detector, executor, weights: dict[str, int]) -> CycleResult:
    snapshot = capture.grab()
    detections = detector.detect(snapshot.image)
    state = build_state(detections)
    target = pick_best_target(state.visible_targets, weights)
    execution = executor.click(target.center) if target else None
    return CycleResult(selected_target=target, execution=execution)
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/orchestrator/test_engine.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/orchestrator/engine.py tests/orchestrator/test_engine.py
git commit -m "feat: add orchestrator loop"
```
Otherwise: append `Task 10 complete` to `progress.md`.

---

### Task 11: 加入真实 YOLO 适配器与检测结果标准化

**Files:**
- Create: `src/auto_ops/detector/yolo.py`
- Create: `tests/detector/test_yolo_adapter.py`

**Step 1: Write the failing test**

```python
from auto_ops.detector.yolo import normalize_box


def test_normalize_box_returns_int_tuple():
    assert normalize_box([10.2, 11.8, 40.0, 42.9]) == (10, 11, 40, 42)
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/detector/test_yolo_adapter.py -v`
Expected: FAIL because adapter does not exist

**Step 3: Write minimal implementation**

`src/auto_ops/detector/yolo.py`
```python
from auto_ops.shared.models import Detection


def normalize_box(box) -> tuple[int, int, int, int]:
    return tuple(int(value) for value in box)


class YoloDetector:
    def __init__(self, model):
        self.model = model

    def detect(self, image) -> list[Detection]:
        result = self.model(image)[0]
        detections = []
        for box, conf, cls_id in zip(result.boxes.xyxy, result.boxes.conf, result.boxes.cls):
            class_name = result.names[int(cls_id)]
            detections.append(
                Detection(class_name=str(class_name), confidence=float(conf), bbox=normalize_box(box.tolist()))
            )
        return detections
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/detector/test_yolo_adapter.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/detector/yolo.py tests/detector/test_yolo_adapter.py
git commit -m "feat: add yolo detector adapter"
```
Otherwise: append `Task 11 complete` to `progress.md`.

---

### Task 12: 建立 PySide6 MVP 控制台

**Files:**
- Create: `src/auto_ops/ui/view_model.py`
- Create: `src/auto_ops/ui/main_window.py`
- Create: `src/auto_ops/ui/app.py`
- Create: `tests/ui/test_view_model.py`

**Step 1: Write the failing test**

```python
from auto_ops.ui.view_model import UiState


def test_ui_state_tracks_selected_scene():
    state = UiState(selected_scene="browser-demo", running=False)
    assert state.selected_scene == "browser-demo"
    assert state.running is False
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/ui/test_view_model.py -v`
Expected: FAIL because UI state model does not exist

**Step 3: Write minimal implementation**

`src/auto_ops/ui/view_model.py`
```python
from pydantic import BaseModel


class UiState(BaseModel):
    selected_scene: str
    running: bool = False
    last_action: str | None = None
```

`src/auto_ops/ui/main_window.py`
```python
from PySide6.QtWidgets import QLabel, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Ops")
        self._label = QLabel("Ready")
        self.setCentralWidget(self._label)
```

`src/auto_ops/ui/app.py`
```python
from PySide6.QtWidgets import QApplication
from auto_ops.ui.main_window import MainWindow


def build_ui() -> MainWindow:
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    window.show()
    return window
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/ui/test_view_model.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/ui/view_model.py src/auto_ops/ui/main_window.py src/auto_ops/ui/app.py tests/ui/test_view_model.py
git commit -m "feat: add PySide6 MVP console"
```
Otherwise: append `Task 12 complete` to `progress.md`.

---

### Task 13: 接通真实场景配置、只识别模式与手工验证脚本

**Files:**
- Modify: `strategies/scenes/browser_demo.yaml`
- Modify: `src/auto_ops/orchestrator/engine.py`
- Modify: `src/auto_ops/ui/view_model.py`
- Create: `tests/orchestrator/test_dry_run_cycle.py`

**Step 1: Write the failing test**

```python
from auto_ops.executor.windows import WindowsExecutor


def test_dry_run_executor_never_performs_real_action():
    executor = WindowsExecutor(dry_run=True)
    result = executor.click((10, 10))
    assert result.performed is False
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/orchestrator/test_dry_run_cycle.py -v`
Expected: FAIL because dry-run wiring is not guaranteed at orchestrator/UI layer

**Step 3: Write minimal implementation**

Add a `mode: dry_run` field to `browser_demo.yaml`, pass that flag through the UI state and engine bootstrap, and ensure the engine uses `WindowsExecutor(dry_run=True)` when the mode is enabled.

Illustrative code in `src/auto_ops/ui/view_model.py`:
```python
class UiState(BaseModel):
    selected_scene: str
    running: bool = False
    dry_run: bool = True
    last_action: str | None = None
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/orchestrator/test_dry_run_cycle.py -v`
Expected: PASS

**Step 5: Commit**

If Git exists:
```bash
git add strategies/scenes/browser_demo.yaml src/auto_ops/orchestrator/engine.py src/auto_ops/ui/view_model.py tests/orchestrator/test_dry_run_cycle.py
git commit -m "feat: wire dry-run scene execution"
```
Otherwise: append `Task 13 complete` to `progress.md`.

---

### Task 14: 完成 MVP 验证与回归测试命令

**Files:**
- Modify: `progress.md`
- Modify: `findings.md`
- Create: `tests/orchestrator/test_priority_and_state_integration.py`

**Step 1: Write the failing test**

```python
from auto_ops.shared.models import Detection
from auto_ops.state.builder import build_state
from auto_ops.priority.scorer import pick_best_target


def test_popup_is_chosen_before_primary_button():
    detections = [
        Detection(class_name="primary_button", confidence=0.99, bbox=(40, 40, 80, 80)),
        Detection(class_name="popup_close", confidence=0.70, bbox=(10, 10, 20, 20)),
    ]
    state = build_state(detections)
    best = pick_best_target(state.visible_targets, {"primary_button": 80, "popup_close": 100})
    assert state.has_blocking_target is True
    assert best.class_name == "popup_close"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/orchestrator/test_priority_and_state_integration.py -v`
Expected: FAIL if state builder and scorer still operate independently without the intended priority weighting

**Step 3: Write minimal implementation**

Adjust `src/auto_ops/priority/scorer.py` so blocking targets receive an explicit bonus, and log the chosen target plus score into the structured logger.

Illustrative code:
```python
def score_target(target: Detection, weights: dict[str, int]) -> float:
    bonus = 100 if target.class_name.startswith("popup") else 0
    return weights.get(target.class_name, 0) + bonus + target.confidence
```

**Step 4: Run test to verify it passes**

Run all MVP tests:

`python -m pytest tests/config tests/capture tests/detector tests/state tests/priority tests/behavior_tree tests/executor tests/orchestrator tests/ui -v`

Expected: PASS across the MVP test suite.

Then do one manual smoke test:
1. Install deps: `python -m pip install -e ".[dev]"`
2. Launch UI shell from Python REPL or a small launcher.
3. Load `strategies/scenes/browser_demo.yaml`.
4. Enable `dry_run` and confirm the UI shows detection, score, selected target, and simulated action.

**Step 5: Commit**

If Git exists:
```bash
git add src/auto_ops/priority/scorer.py tests/orchestrator/test_priority_and_state_integration.py progress.md findings.md
git commit -m "test: verify MVP priority integration"
```
Otherwise: append `Task 14 complete` to `progress.md`.

---

## MVP 完成定义
满足以下条件才算当前计划完成：
- 能加载 `browser_demo.yaml`
- 能绑定一个 Windows 浏览器 / 桌面软件窗口
- 能抓取窗口图像
- 能通过假检测器或真实 YOLO 适配器产出标准化检测结果
- 能建立页面状态
- 能按优先级选出候选目标
- 能通过最小行为树决定是否执行
- 能在 dry-run 模式下展示动作而不真实点击
- 能通过 PySide6 UI 查看当前画面、当前目标、最近动作与运行状态
- 单元测试与集成测试全部通过

## MVP 之后的顺序优化清单
以下内容不纳入当前实施任务，但按顺序排进后续计划：
1. `cooldown`、`action_history`、`failure_counter` 真正接入状态模型
2. 窗口守卫、失焦暂停、panic stop 热键
3. ROI、最小置信度、类别权重在 UI 中可编辑
4. 标注预览图层与关键帧保存
5. OCR 适配器：`src/auto_ops/detector/ocr.py`
6. 模板匹配适配器：`src/auto_ops/detector/template.py`
7. 多场景加载：`strategies/scenes/*.yaml`
8. 游戏执行器：`src/auto_ops/executor/game_windows.py`
9. 更完整的行为树节点：`SelectorNode`、`RepeatNode`、`CooldownGuardNode`
10. 回放与复盘面板

## 执行注意事项
- 每完成 1 个任务就更新 `task_plan.md`、`findings.md`、`progress.md`。
- 如果出现同一个错误连续 2 次，不要重复同样的修复方式，先记录错误，再换方法。
- 在真实点击前，先保持 `dry_run=True`，直到用户确认目标检测和优先级都正确。
- 所有鼠标键盘动作必须先校验当前窗口仍然匹配配置中的目标窗口。
- 允许在 Mac 上继续实现纯逻辑模块与非平台绑定测试，但 Windows API、真实窗口绑定、真实输入执行的实现与验收必须保留在 Windows 环境。
- 后续涉及平台专属能力时，优先采用抽象接口 + 平台实现分离，避免 Mac 上的开发改动破坏 Windows 功能。
- Windows 专属依赖必须使用平台条件依赖、可选安装或模块内延迟导入，确保 Mac 上可以完成安装、导入和非 Windows 测试。
- 默认先安装基础依赖；真实 UI、YOLO、自动化执行依赖通过可选依赖组单独安装，例如需要完整 MVP 联调时再安装 `.[app,dev]`。
