from pydantic import BaseModel, Field

from auto_ops.shared.models import Detection


class RuntimeState(BaseModel):
    visible_targets: list[Detection] = Field(default_factory=list)
    has_blocking_target: bool = False
    last_action: str | None = None
    failure_count: int = 0


def build_state(detections: list[Detection]) -> RuntimeState:
    blocking = any(item.class_name.startswith("popup") for item in detections)
    return RuntimeState(visible_targets=detections, has_blocking_target=blocking)
