from __future__ import annotations

from pathlib import Path

import yaml

from auto_ops.training.models import TrainingSpec



def load_training_spec(path: Path) -> TrainingSpec:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return TrainingSpec.model_validate(data)
