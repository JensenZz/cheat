from typing import Literal

from pydantic import BaseModel, Field


class WindowMatch(BaseModel):
    title_contains: list[str] = Field(default_factory=list)


class CaptureConfig(BaseModel):
    fps: int = 2


class TargetRule(BaseModel):
    class_name: str
    min_confidence: float
    weight: int
    cooldown_ms: int = 0


class SceneConfig(BaseModel):
    id: str
    name: str
    mode: Literal["observe_only"] = "observe_only"
    window_match: WindowMatch
    capture_config: CaptureConfig


class SceneBundle(BaseModel):
    scene: SceneConfig
    targets: list[TargetRule] = Field(default_factory=list)
