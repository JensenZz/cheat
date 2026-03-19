from __future__ import annotations

from importlib.resources import as_file, files
from pathlib import Path

from auto_ops.config.loader import load_scene
from auto_ops.detector.fake import FakeDetector
from auto_ops.executor.windows import WindowsExecutor
from auto_ops.logging import build_logger
from auto_ops.orchestrator.engine import preview_cycle, run_cycle
from auto_ops.ui.app import run_ui
from auto_ops.ui.view_model import build_ui_state


class PreviewCapture:
    def grab(self):
        from auto_ops.capture.windows import WindowSnapshot

        return WindowSnapshot(title="Preview", region=(0, 0, 800, 600), image=None)



def main(scene_path: Path | None = None) -> int:
    build_logger("auto_ops").info("app boot")

    if scene_path is None:
        resource = files("auto_ops").joinpath("resources/browser_demo.yaml")
        with as_file(resource) as bundled_scene_path:
            return _run_with_scene(bundled_scene_path)

    return _run_with_scene(scene_path)



def _run_with_scene(scene_path: Path) -> int:
    scene_bundle = load_scene(scene_path)
    weights = {target.class_name: target.weight for target in scene_bundle.targets}
    capture = PreviewCapture()
    detector = FakeDetector([
        {"class_name": "primary_button", "confidence": 0.9, "bbox": (10, 10, 50, 30)},
    ])

    if scene_bundle.scene.mode == "preview":
        preview = preview_cycle(capture, detector, weights)
    else:
        preview = run_cycle(
            capture,
            detector,
            WindowsExecutor(dry_run=scene_bundle.scene.mode == "dry_run"),
            weights,
            mode=scene_bundle.scene.mode,
        )

    state = build_ui_state(
        selected_scene=scene_bundle.scene.id,
        preview=preview,
        mode=scene_bundle.scene.mode,
        executor_backend=scene_bundle.scene.executor_backend,
    )
    return run_ui(state)
