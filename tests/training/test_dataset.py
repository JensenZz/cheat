from pathlib import Path

import pytest

from auto_ops.training.dataset import build_dataset_descriptor, validate_dataset_layout
from auto_ops.training.models import DatasetConfig, DatasetDescriptor, DatasetYaml



def make_dataset(root: Path) -> None:
    for relative in [
        "images/train",
        "images/val",
        "labels/train",
        "labels/val",
    ]:
        (root / relative).mkdir(parents=True, exist_ok=True)

    (root / "images/train/sample1.png").write_bytes(b"png")
    (root / "images/val/sample2.png").write_bytes(b"png")
    (root / "labels/train/sample1.txt").write_text("0 0.5 0.5 0.2 0.2\n", encoding="utf-8")
    (root / "labels/val/sample2.txt").write_text("1 0.5 0.5 0.2 0.2\n", encoding="utf-8")



def test_validate_dataset_layout_accepts_expected_yolo_structure(tmp_path):
    root = tmp_path / "dataset"
    make_dataset(root)
    config = DatasetConfig(root_dir=root, train_split="train", val_split="val")

    descriptor = validate_dataset_layout(config=config, classes=["primary_button", "popup_close"])

    assert isinstance(descriptor, DatasetDescriptor)
    assert descriptor.dataset_yaml.names == {0: "primary_button", 1: "popup_close"}
    assert descriptor.train_images_dir == root / "images/train"
    assert descriptor.val_labels_dir == root / "labels/val"



def test_validate_dataset_layout_rejects_missing_label_file(tmp_path):
    root = tmp_path / "dataset"
    make_dataset(root)
    (root / "labels/val/sample2.txt").unlink()
    config = DatasetConfig(root_dir=root, train_split="train", val_split="val")

    with pytest.raises(ValueError, match="sample2.txt"):
        validate_dataset_layout(config=config, classes=["primary_button", "popup_close"])



def test_validate_dataset_layout_rejects_class_index_out_of_range(tmp_path):
    root = tmp_path / "dataset"
    make_dataset(root)
    (root / "labels/val/sample2.txt").write_text("2 0.5 0.5 0.2 0.2\n", encoding="utf-8")
    config = DatasetConfig(root_dir=root, train_split="train", val_split="val")

    with pytest.raises(ValueError, match="class index"):
        validate_dataset_layout(config=config, classes=["primary_button", "popup_close"])



def test_build_dataset_descriptor_returns_dataset_yaml_model(tmp_path):
    root = tmp_path / "dataset"
    make_dataset(root)
    config = DatasetConfig(root_dir=root, train_split="train", val_split="val")

    descriptor = build_dataset_descriptor(config=config, classes=["primary_button"])

    assert isinstance(descriptor.dataset_yaml, DatasetYaml)
    assert descriptor.dataset_yaml.path == root
    assert descriptor.dataset_yaml.train == Path("images/train")
    assert descriptor.dataset_yaml.val == Path("images/val")
    assert descriptor.dataset_yaml.nc == 1



def test_dataset_config_rejects_unsafe_split_names(tmp_path):
    root = tmp_path / "dataset"

    with pytest.raises(ValueError, match="split"):
        DatasetConfig(root_dir=root, train_split="../train", val_split="val")
