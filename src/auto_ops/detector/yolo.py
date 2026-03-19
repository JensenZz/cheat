"""YOLO detector adapter."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from auto_ops.shared.models import Detection



def normalize_box(box: Sequence[float]) -> tuple[int, int, int, int]:
    if len(box) != 4:
        raise ValueError("box must contain exactly 4 values")

    x1, y1, x2, y2 = box
    return (int(x1), int(y1), int(x2), int(y2))


class YoloDetector:
    def __init__(self, model: Any):
        self.model = model

    def detect(self, image: Any) -> list[Detection]:
        result = self.model(image)[0]
        xyxy = result.boxes.xyxy
        conf = result.boxes.conf
        cls = result.boxes.cls

        if not (len(xyxy) == len(conf) == len(cls)):
            raise ValueError("yolo box data lengths must match")

        detections = []
        for box, score, cls_id in zip(xyxy, conf, cls):
            class_name = result.names[int(cls_id)]
            detections.append(
                Detection(
                    class_name=str(class_name),
                    confidence=float(score),
                    bbox=normalize_box(box.tolist()),
                )
            )
        return detections
