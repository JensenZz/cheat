from auto_ops.shared.models import Detection
from auto_ops.priority.scorer import pick_best_target, score_target


def test_pick_best_target_prefers_blocking_popup():
    detections = [
        Detection(class_name="primary_button", confidence=0.92, bbox=(50, 50, 120, 90)),
        Detection(class_name="popup_close", confidence=0.88, bbox=(10, 10, 40, 40)),
    ]
    weights = {"primary_button": 80, "popup_close": 100}

    best = pick_best_target(detections, weights)

    assert best.class_name == "popup_close"


def test_pick_best_target_uses_confidence_when_weights_match():
    detections = [
        Detection(class_name="primary_button", confidence=0.92, bbox=(50, 50, 120, 90)),
        Detection(class_name="primary_button", confidence=0.88, bbox=(10, 10, 40, 40)),
    ]

    best = pick_best_target(detections, {"primary_button": 80})

    assert best.confidence == 0.92


def test_pick_best_target_returns_none_for_empty_targets():
    assert pick_best_target([], {"primary_button": 80}) is None


def test_score_target_uses_zero_weight_for_unknown_class():
    target = Detection(class_name="secondary_button", confidence=0.75, bbox=(10, 10, 40, 40))

    assert score_target(target, {"primary_button": 80}) == 0.75
