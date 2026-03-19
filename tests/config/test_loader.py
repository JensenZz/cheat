import pytest
from pydantic import ValidationError

from auto_ops.config.loader import load_scene


def test_load_scene_returns_parsed_models(tmp_path):
    config = tmp_path / "scene.yaml"
    config.write_text(
        """
scene:
  id: browser-demo
  name: Browser Demo
  mode: dry_run
  executor_backend: standard
  ocr_backend: none
  window_policy: focused
  multi_window: false
  window_match:
    title_contains: ["Demo"]
  capture_config:
    fps: 2
  targets:
    - class_name: primary_button
      min_confidence: 0.6
      weight: 80
      cooldown_ms: 1000
""".strip(),
        encoding="utf-8",
    )

    scene = load_scene(config)

    assert scene.scene.id == "browser-demo"
    assert scene.scene.mode == "dry_run"
    assert scene.scene.executor_backend == "standard"
    assert scene.scene.ocr_backend == "none"
    assert scene.scene.window_policy == "focused"
    assert scene.scene.multi_window is False
    assert scene.targets[0].class_name == "primary_button"



def test_load_scene_rejects_unknown_mode(tmp_path):
    config = tmp_path / "scene.yaml"
    config.write_text(
        """
scene:
  id: browser-demo
  name: Browser Demo
  mode: auto
  window_match:
    title_contains: ["Demo"]
  capture_config:
    fps: 2
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="preview|dry_run|live"):
        load_scene(config)



def test_load_scene_rejects_emulator_backend_without_emulator_type(tmp_path):
    config = tmp_path / "scene.yaml"
    config.write_text(
        """
scene:
  id: browser-demo
  name: Browser Demo
  mode: dry_run
  executor_backend: emulator
  window_match:
    title_contains: ["Demo"]
  capture_config:
    fps: 2
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="emulator"):
        load_scene(config)
