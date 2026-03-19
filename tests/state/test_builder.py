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
    assert state.visible_targets == detections


def test_build_state_keeps_non_popup_targets_non_blocking():
    detections = [
        Detection(class_name="primary_button", confidence=0.91, bbox=(50, 50, 120, 90)),
    ]

    state = build_state(detections)

    assert state.has_blocking_target is False
    assert state.visible_targets == detections


def test_build_state_copies_input_list_into_state_snapshot():
    detections = [
        Detection(class_name="primary_button", confidence=0.91, bbox=(50, 50, 120, 90)),
    ]

    state = build_state(detections)
    detections.append(Detection(class_name="popup_close", confidence=0.95, bbox=(10, 10, 40, 40)))

    assert len(state.visible_targets) == 1
