from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from auto_ops.config.models import ExecutorBackend, SceneMode

if TYPE_CHECKING:
    from auto_ops.orchestrator.engine import PreviewCycleResult


class UiState(BaseModel):
    selected_scene: str
    running: bool = False
    mode: SceneMode = "preview"
    can_execute: bool = False
    executor_backend: ExecutorBackend = "standard"
    preview_action: str | None = None
    preview_point: tuple[int, int] | None = None
    has_blocking_target: bool = False
    last_action: str | None = None



def build_ui_state(
    selected_scene: str,
    preview: "PreviewCycleResult | None" = None,
    mode: SceneMode = "preview",
    executor_backend: ExecutorBackend = "standard",
) -> UiState:
    preview_action = None
    preview_point = None
    has_blocking_target = False

    if preview is not None:
        preview_action = preview.planned_action
        preview_point = preview.planned_point
        has_blocking_target = preview.has_blocking_target

    return UiState(
        selected_scene=selected_scene,
        mode=mode,
        can_execute=mode != "preview",
        executor_backend=executor_backend,
        preview_action=preview_action,
        preview_point=preview_point,
        has_blocking_target=has_blocking_target,
    )
