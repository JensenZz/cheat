import pytest

from auto_ops.detector.yolo import YoloDetector, normalize_box


class FakeTensor:
    def __init__(self, values):
        self._values = values

    def tolist(self):
        return self._values


class FakeBoxes:
    def __init__(self, xyxy=None, conf=None, cls=None):
        self.xyxy = [FakeTensor([10.2, 11.8, 40.0, 42.9])] if xyxy is None else xyxy
        self.conf = [0.87] if conf is None else conf
        self.cls = [1] if cls is None else cls


class FakeResult:
    def __init__(self, boxes=None, names=None):
        self.boxes = FakeBoxes() if boxes is None else boxes
        self.names = {1: "primary_button"} if names is None else names


class FakeModel:
    def __init__(self, result=None):
        self.result = result or FakeResult()
        self.seen_images = []

    def __call__(self, image):
        self.seen_images.append(image)
        return [self.result]



def test_normalize_box_returns_int_tuple():
    assert normalize_box([10.2, 11.8, 40.0, 42.9]) == (10, 11, 40, 42)



def test_yolo_detector_converts_result_to_detection_models():
    model = FakeModel()
    detector = YoloDetector(model)

    detections = detector.detect(image="frame")

    assert model.seen_images == ["frame"]
    assert len(detections) == 1
    assert detections[0].class_name == "primary_button"
    assert detections[0].confidence == 0.87
    assert detections[0].bbox == (10, 11, 40, 42)



def test_normalize_box_rejects_non_four_value_boxes():
    with pytest.raises(ValueError, match="box must contain exactly 4 values"):
        normalize_box([10.2, 11.8, 40.0])



def test_yolo_detector_returns_empty_list_for_empty_results():
    detector = YoloDetector(FakeModel(FakeResult(boxes=FakeBoxes(xyxy=[], conf=[], cls=[]))))

    detections = detector.detect(image="frame")

    assert detections == []



def test_yolo_detector_rejects_misaligned_box_metadata_lengths():
    detector = YoloDetector(
        FakeModel(
            FakeResult(
                boxes=FakeBoxes(
                    xyxy=[FakeTensor([10.2, 11.8, 40.0, 42.9])],
                    conf=[0.87],
                    cls=[1, 2],
                )
            )
        )
    )

    with pytest.raises(ValueError, match="yolo box data lengths must match"):
        detector.detect(image="frame")
