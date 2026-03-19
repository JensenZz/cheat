from auto_ops.capture.windows import WindowSnapshot
from auto_ops.detector.fake import FakeDetector
from auto_ops.executor.base import ExecutionResult
from auto_ops.orchestrator.engine import preview_cycle, run_cycle


class FakeCapture:
    def grab(self):
        return WindowSnapshot(title="Demo", region=(0, 0, 800, 600), image=None)


class RecordingExecutor:
    def __init__(self):
        self.points = []

    def click(self, point):
        self.points.append(point)
        return ExecutionResult(action="click", ok=True, performed=False, detail=str(point))



def test_preview_cycle_selects_target_without_execution():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": (10, 10, 50, 30)},
    ])

    result = preview_cycle(FakeCapture(), detector, {"primary_button": 80})

    assert result.selected_target.class_name == "primary_button"
    assert result.planned_action == "click"
    assert result.planned_point == (30, 20)



def test_preview_cycle_returns_no_action_when_no_target_found():
    detector = FakeDetector([])

    result = preview_cycle(FakeCapture(), detector, {"primary_button": 80})

    assert result.selected_target is None
    assert result.has_blocking_target is False
    assert result.planned_action is None
    assert result.planned_point is None



def test_run_cycle_skips_execution_in_preview_mode():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": (10, 10, 50, 30)},
    ])
    executor = RecordingExecutor()

    result = run_cycle(FakeCapture(), detector, executor, {"primary_button": 80}, mode="preview")

    assert result.selected_target.class_name == "primary_button"
    assert result.execution is None
    assert executor.points == []



def test_run_cycle_executes_in_dry_run_mode():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": (10, 10, 50, 30)},
    ])
    executor = RecordingExecutor()

    result = run_cycle(FakeCapture(), detector, executor, {"primary_button": 80}, mode="dry_run")

    assert result.selected_target.class_name == "primary_button"
    assert result.execution.action == "click"
    assert executor.points == [(30, 20)]
