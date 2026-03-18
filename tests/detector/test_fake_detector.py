import pytest
from pydantic import ValidationError

from auto_ops.detector.fake import FakeDetector


def test_fake_detector_returns_seeded_detections():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": [10, 10, 50, 30]}
    ])

    detections = detector.detect(image=None)

    assert len(detections) == 1
    assert detections[0].class_name == "primary_button"
    assert detections[0].bbox == (10, 10, 50, 30)


def test_detection_center_uses_x1_y1_x2_y2_coordinates():
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": [10, 20, 50, 30]}
    ])

    detections = detector.detect(image=None)

    assert detections[0].center == (30.0, 25.0)


def test_fake_detector_copies_seeded_input():
    seeded = [
        {"class_name": "primary_button", "confidence": 0.9, "bbox": [10, 10, 50, 30]}
    ]
    detector = FakeDetector(seeded)

    seeded[0]["class_name"] = "secondary_button"
    seeded[0]["bbox"][0] = 999

    detections = detector.detect(image=None)

    assert detections[0].class_name == "primary_button"
    assert detections[0].bbox == (10, 10, 50, 30)


@pytest.mark.parametrize(
    ("bbox", "expected_message"),
    [
        ([20, 10, 10, 30], "x2 must be greater than or equal to x1"),
        ([10, 30, 20, 10], "y2 must be greater than or equal to y1"),
    ],
)
def test_fake_detector_rejects_invalid_bbox_coordinates(bbox, expected_message):
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": bbox}
    ])

    with pytest.raises(ValidationError, match=expected_message):
        detector.detect(image=None)


@pytest.mark.parametrize(
    ("confidence", "expected_message"),
    [
        (-0.1, "confidence must be between 0.0 and 1.0"),
        (1.1, "confidence must be between 0.0 and 1.0"),
    ],
)
def test_fake_detector_rejects_invalid_confidence(confidence, expected_message):
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": confidence, "bbox": [10, 10, 50, 30]}
    ])

    with pytest.raises(ValidationError, match=expected_message):
        detector.detect(image=None)
