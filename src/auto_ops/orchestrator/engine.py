from auto_ops.executor.base import ExecutionResult
from auto_ops.priority.scorer import pick_best_target
from auto_ops.shared.models import Detection
from auto_ops.state.builder import build_state

from pydantic import BaseModel


class CycleResult(BaseModel):
    selected_target: Detection | None
    execution: ExecutionResult | None


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



def run_cycle(capture, detector, executor, weights: dict[str, int], observe_only: bool = False) -> CycleResult:
    snapshot = capture.grab()
    detections = detector.detect(snapshot.image)
    state = build_state(detections)
    target = pick_best_target(state.visible_targets, weights)
    execution = None
    if target and not observe_only:
        point = (int(target.center[0]), int(target.center[1]))
        execution = executor.click(point)
    return CycleResult(selected_target=target, execution=execution)
