"""Fake detector for tests and dry runs."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from auto_ops.shared.models import Detection


class FakeDetector:
    def __init__(self, seeded: list[dict[str, Any]]):
        self._seeded = deepcopy(seeded)

    def detect(self, image: Any) -> list[Detection]:
        return [Detection(**item) for item in self._seeded]
