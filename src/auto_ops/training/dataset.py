from __future__ import annotations

from pathlib import Path

from auto_ops.training.models import DatasetConfig, DatasetDescriptor, DatasetYaml

_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp"}



def build_dataset_descriptor(config: DatasetConfig, classes: list[str]) -> DatasetDescriptor:
    names = {index: class_name for index, class_name in enumerate(classes)}
    return DatasetDescriptor(
        root_dir=config.root_dir,
        train_images_dir=config.root_dir / "images" / config.train_split,
        val_images_dir=config.root_dir / "images" / config.val_split,
        train_labels_dir=config.root_dir / "labels" / config.train_split,
        val_labels_dir=config.root_dir / "labels" / config.val_split,
        dataset_yaml=DatasetYaml(
            path=config.root_dir,
            train=Path("images") / config.train_split,
            val=Path("images") / config.val_split,
            nc=len(classes),
            names=names,
        ),
    )



def validate_dataset_layout(config: DatasetConfig, classes: list[str]) -> DatasetDescriptor:
    descriptor = build_dataset_descriptor(config=config, classes=classes)
    for directory in (
        descriptor.train_images_dir,
        descriptor.val_images_dir,
        descriptor.train_labels_dir,
        descriptor.val_labels_dir,
    ):
        if not directory.is_dir():
            raise ValueError(f"dataset directory is missing: {directory}")

    _validate_split(descriptor.train_images_dir, descriptor.train_labels_dir, len(classes))
    _validate_split(descriptor.val_images_dir, descriptor.val_labels_dir, len(classes))
    return descriptor



def _validate_split(images_dir: Path, labels_dir: Path, class_count: int) -> None:
    for image_path in sorted(path for path in images_dir.iterdir() if path.is_file() and path.suffix.lower() in _IMAGE_EXTENSIONS):
        label_path = labels_dir / f"{image_path.stem}.txt"
        if not label_path.is_file():
            raise ValueError(f"missing label file for {image_path.name}: expected {label_path.name}")
        _validate_label_file(label_path, class_count)



def _validate_label_file(label_path: Path, class_count: int) -> None:
    for line_number, raw_line in enumerate(label_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split()
        try:
            class_index = int(parts[0])
        except (ValueError, IndexError) as exc:
            raise ValueError(f"invalid class index in {label_path.name}:{line_number}") from exc
        if class_index < 0 or class_index >= class_count:
            raise ValueError(f"class index {class_index} out of range in {label_path.name}:{line_number}")
