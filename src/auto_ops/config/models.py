from typing import Literal

from pydantic import BaseModel, Field, model_validator

SceneMode = Literal["preview", "dry_run", "live"]
ExecutorBackend = Literal["standard", "emulator", "interception"]
OcrBackend = Literal["none", "tesseract"]
WindowPolicy = Literal["focused", "match_first", "all"]


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
    mode: SceneMode = "preview"
    executor_backend: ExecutorBackend = "standard"
    ocr_backend: OcrBackend = "none"
    window_policy: WindowPolicy = "focused"
    multi_window: bool = False
    emulator_type: str | None = None
    window_match: WindowMatch
    capture_config: CaptureConfig

    @model_validator(mode="after")
    def validate_backend_requirements(self) -> "SceneConfig":
        if self.executor_backend == "emulator" and not self.emulator_type:
            raise ValueError("emulator backend requires emulator_type")
        return self


class SceneBundle(BaseModel):
    scene: SceneConfig
    targets: list[TargetRule] = Field(default_factory=list)
