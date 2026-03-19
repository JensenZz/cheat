from typing import Literal

from auto_ops.executor.base import ExecutionResult
from auto_ops.priority.scorer import pick_best_target
from auto_ops.shared.models import Detection
from auto_ops.state.builder import build_state

from pydantic import BaseModel


class CycleResult(BaseModel):
    selected_target: Detection | None
    execution: ExecutionResult | None

    @property
    def planned_action(self) -> str | None:
        if self.execution is not None:
            return self.execution.action
        if self.selected_target is not None:
            return "click"
        return None

    @property
    def planned_point(self) -> tuple[int, int] | None:
        if self.selected_target is None:
            return None
        return (int(self.selected_target.center[0]), int(self.selected_target.center[1]))

    @property
    def has_blocking_target(self) -> bool:
        return bool(self.selected_target and self.selected_target.class_name.startswith("popup"))


class PreviewCycleResult(BaseModel):
    selected_target: Detection | None
    has_blocking_target: bool
    planned_action: str | None
    planned_point: tuple[int, int] | None



def preview_cycle(capture, detector, weights: dict[str, int]) -> PreviewCycleResult:
    snapshot = capture.grab()
    detections = detector.detect(snapshot.image)
    state = build_state(detections)
    target = pick_best_target(state.visible_targets, weights)
    if not target:
        return PreviewCycleResult(
            selected_target=None,
            has_blocking_target=state.has_blocking_target,
            planned_action=None,
            planned_point=None,
        )

    point = (int(target.center[0]), int(target.center[1]))
    return PreviewCycleResult(
        selected_target=target,
        has_blocking_target=state.has_blocking_target,
        planned_action="click",
        planned_point=point,
    )



def run_cycle(
    capture,
    detector,
    executor,
    weights: dict[str, int],
    mode: Literal["preview", "dry_run", "live"] = "live",
) -> CycleResult:
    snapshot = capture.grab()
    detections = detector.detect(snapshot.image)
    state = build_state(detections)
    target = pick_best_target(state.visible_targets, weights)
    execution = None
    if target and mode != "preview":
        point = (int(target.center[0]), int(target.center[1]))
        execution = executor.click(point)
    return CycleResult(selected_target=target, execution=execution)
