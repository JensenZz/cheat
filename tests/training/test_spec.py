from pathlib import Path

import pytest
from pydantic import ValidationError

from auto_ops.training.loader import load_training_spec
from auto_ops.training.models import TrainingSpec



def test_load_training_spec_parses_yaml(tmp_path):
    config = tmp_path / "browser_demo_train.yaml"
    config.write_text(
        """
scene_id: browser-demo
classes:
  - primary_button
  - popup_close
output_dir: artifacts/models/browser_demo
base_model: models/yolo11n.pt
dataset:
  root_dir: artifacts/datasets/browser_demo
  train_split: train
  val_split: val
""".strip(),
        encoding="utf-8",
    )

    spec = load_training_spec(config)

    assert isinstance(spec, TrainingSpec)
    assert spec.scene_id == "browser-demo"
    assert spec.classes == ["primary_button", "popup_close"]
    assert spec.output_dir == Path("artifacts/models/browser_demo")
    assert spec.dataset.root_dir == Path("artifacts/datasets/browser_demo")



def test_load_training_spec_requires_scene_id(tmp_path):
    config = tmp_path / "browser_demo_train.yaml"
    config.write_text(
        """
classes:
  - primary_button
output_dir: artifacts/models/browser_demo
base_model: models/yolo11n.pt
dataset:
  root_dir: artifacts/datasets/browser_demo
  train_split: train
  val_split: val
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="scene_id"):
        load_training_spec(config)



def test_load_training_spec_requires_classes_and_output_dir(tmp_path):
    config = tmp_path / "browser_demo_train.yaml"
    config.write_text(
        """
scene_id: browser-demo
classes: []
dataset:
  root_dir: artifacts/datasets/browser_demo
  train_split: train
  val_split: val
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="classes|output_dir"):
        load_training_spec(config)



def test_training_models_stay_outside_scene_config_module():
    from auto_ops.config.models import SceneConfig

    assert not hasattr(SceneConfig, "classes")
    assert not hasattr(SceneConfig, "dataset")
    assert not hasattr(SceneConfig, "base_model")



def test_training_models_import_without_training_dependency(monkeypatch):
    import builtins
    import importlib
    import sys

    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "ultralytics":
            raise AssertionError("ultralytics should not be imported when loading training spec")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    sys.modules.pop("auto_ops.training.models", None)
    sys.modules.pop("auto_ops.training.loader", None)

    models = importlib.import_module("auto_ops.training.models")
    loader = importlib.import_module("auto_ops.training.loader")

    assert hasattr(models, "TrainingSpec")
    assert callable(loader.load_training_spec)



def test_load_training_spec_rejects_same_train_and_val_split(tmp_path):
    config = tmp_path / "browser_demo_train.yaml"
    config.write_text(
        """
scene_id: browser-demo
classes:
  - primary_button
output_dir: artifacts/models/browser_demo
base_model: models/yolo11n.pt
dataset:
  root_dir: artifacts/datasets/browser_demo
  train_split: train
  val_split: train
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValidationError, match="train_split|val_split"):
        load_training_spec(config)
