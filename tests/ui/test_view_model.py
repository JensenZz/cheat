import pytest

from auto_ops.capture.windows import WindowSnapshot
from auto_ops.detector.fake import FakeDetector
from auto_ops.orchestrator.engine import preview_cycle
from auto_ops.ui.view_model import UiState, build_ui_state


class FakeCapture:
    def grab(self):
        return WindowSnapshot(title="Demo", region=(0, 0, 800, 600), image=None)



def test_ui_state_tracks_selected_scene():
    state = UiState(selected_scene="browser-demo", running=False)

    assert state.selected_scene == "browser-demo"
    assert state.running is False



def test_ui_state_defaults_to_observe_only():
    state = UiState(selected_scene="browser-demo")

    assert state.observe_only is True



def test_ui_state_tracks_preview_summary():
    state = UiState(
        selected_scene="browser-demo",
        preview_action="click",
        preview_point=(30, 20),
        has_blocking_target=True,
    )

    assert state.preview_action == "click"
    assert state.preview_point == (30, 20)
    assert state.has_blocking_target is True



def test_build_ui_state_maps_preview_cycle_result_to_ui_state():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": (10, 10, 50, 30)},
    ])
    preview = preview_cycle(FakeCapture(), detector, {"primary_button": 80})

    state = build_ui_state(selected_scene="browser-demo", preview=preview)

    assert state.selected_scene == "browser-demo"
    assert state.observe_only is True
    assert state.preview_action == "click"
    assert state.preview_point == (30, 20)
    assert state.has_blocking_target is False



def test_build_ui_state_defaults_when_preview_is_none():
    state = build_ui_state(selected_scene="browser-demo")

    assert state.selected_scene == "browser-demo"
    assert state.observe_only is True
    assert state.preview_action is None
    assert state.preview_point is None
    assert state.has_blocking_target is False



def test_build_ui_state_preserves_empty_preview_result():
    detector = FakeDetector([])
    preview = preview_cycle(FakeCapture(), detector, {"primary_button": 80})

    state = build_ui_state(selected_scene="browser-demo", preview=preview)

    assert state.preview_action is None
    assert state.preview_point is None
    assert state.has_blocking_target is False



def test_build_ui_state_rejects_wrong_preview_object():
    with pytest.raises(AttributeError):
        build_ui_state(selected_scene="browser-demo", preview=object())
