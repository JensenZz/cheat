from auto_ops.config.loader import load_scene


def test_load_scene_returns_parsed_models(tmp_path):
    config = tmp_path / "scene.yaml"
    config.write_text(
        """
scene:
  id: browser-demo
  name: Browser Demo
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
    assert scene.targets[0].class_name == "primary_button"
