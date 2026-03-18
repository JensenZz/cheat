from pathlib import Path

import yaml

from auto_ops.config.models import SceneBundle


def load_scene(path: Path) -> SceneBundle:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    scene = data["scene"]
    targets = data.get("targets", scene.get("targets", []))
    return SceneBundle(scene=scene, targets=targets)
