from auto_ops.capture.windows import WindowSnapshot
from auto_ops.detector.fake import FakeDetector
from auto_ops.executor.base import ExecutionResult
from auto_ops.executor.windows import WindowsExecutor
from auto_ops.orchestrator.engine import run_cycle


class FakeCapture:
    def grab(self):
        return WindowSnapshot(title="Demo", region=(0, 0, 800, 600), image=None)


class RecordingExecutor:
    def __init__(self):
        self.points = []

    def click(self, point):
        self.points.append(point)
        return ExecutionResult(action="click", ok=True, performed=False, detail=str(point))



def test_run_cycle_selects_and_clicks_best_target():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": (10, 10, 50, 30)},
    ])
    executor = WindowsExecutor(dry_run=True)

    result = run_cycle(FakeCapture(), detector, executor, {"primary_button": 80})

    assert result.selected_target.class_name == "primary_button"
    assert result.execution.action == "click"



def test_run_cycle_returns_none_execution_when_no_target_found():
    detector = FakeDetector([])
    executor = WindowsExecutor(dry_run=True)

    result = run_cycle(FakeCapture(), detector, executor, {"primary_button": 80})

    assert result.selected_target is None
    assert result.execution is None



def test_run_cycle_normalizes_target_center_to_integer_point():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": (10, 10, 51, 31)},
    ])
    executor = RecordingExecutor()

    run_cycle(FakeCapture(), detector, executor, {"primary_button": 80})

    assert executor.points == [(30, 20)]
