from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

SceneMode = Literal["preview", "dry_run", "live"]
CaptureBackend = Literal["preview", "windows"]
DetectorBackend = Literal["fake", "yolo"]
ExecutorBackend = Literal["standard", "emulator", "interception"]
OcrBackend = Literal["none", "tesseract"]
WindowPolicy = Literal["focused", "match_first", "all"]


class WindowMatch(BaseModel):
    title_contains: list[str] = Field(default_factory=list)

    @field_validator("title_contains")
    @classmethod
    def validate_title_contains(cls, value: list[str]) -> list[str]:
        keywords = [item.strip() for item in value if item and item.strip()]
        if not keywords:
            raise ValueError("title_contains must contain at least one non-empty keyword")
        return keywords


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
    capture_backend: CaptureBackend = "preview"
    detector_backend: DetectorBackend = "fake"
    detector_model: str | None = None
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
        if self.detector_backend == "yolo" and not self.detector_model:
            raise ValueError("yolo detector backend requires detector_model")
        if self.detector_backend == "yolo" and self.capture_backend != "windows":
            raise ValueError("yolo detector backend requires capture_backend='windows'")
        return self


class SceneBundle(BaseModel):
    scene: SceneConfig
    targets: list[TargetRule] = Field(default_factory=list)
