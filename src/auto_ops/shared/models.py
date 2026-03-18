"""共享数据模型。"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, field_validator


@dataclass(frozen=True)
class WindowSnapshot:
    title: str
    region: tuple[int, int, int, int]
    image: object


class Detection(BaseModel):
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]

    @field_validator("confidence")
    @classmethod
    def _validate_confidence(cls, value: float) -> float:
        if not 0.0 <= value <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        return value

    @field_validator("bbox")
    @classmethod
    def _validate_bbox(cls, value: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
        if len(value) != 4:
            raise ValueError("bbox must contain exactly 4 values")

        x1, y1, x2, y2 = value
        if x2 < x1:
            raise ValueError("x2 must be greater than or equal to x1")
        if y2 < y1:
            raise ValueError("y2 must be greater than or equal to y1")

        return value

    @property
    def center(self) -> tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)
