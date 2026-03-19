from auto_ops.capture.windows import WindowSnapshot
from auto_ops.detector.fake import FakeDetector
from auto_ops.orchestrator.engine import preview_cycle


class FakeCapture:
    def grab(self):
        return WindowSnapshot(title="Demo", region=(0, 0, 800, 600), image=None)



def test_preview_cycle_marks_blocking_popup_and_selects_it_first():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.99, "bbox": (40, 40, 80, 80)},
        {"class_name": "popup_close", "confidence": 0.70, "bbox": (10, 10, 20, 20)},
    ])

    result = preview_cycle(FakeCapture(), detector, {"primary_button": 80, "popup_close": 100})

    assert result.has_blocking_target is True
    assert result.selected_target.class_name == "popup_close"
    assert result.planned_action == "click"
