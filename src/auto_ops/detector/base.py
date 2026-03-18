"""Detector abstractions."""

from __future__ import annotations

from typing import Any, Protocol

from auto_ops.shared.models import Detection


class Detector(Protocol):
    def detect(self, image: Any) -> list[Detection]:
        """Return detections for the provided image."""
