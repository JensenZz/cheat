from __future__ import annotations

from pathlib import Path
import re

from pydantic import BaseModel, field_validator, model_validator

_SAFE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")



def validate_safe_name(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must not be empty")
    if not _SAFE_NAME_PATTERN.fullmatch(normalized):
        raise ValueError(f"{field_name} must contain only letters, numbers, hyphen, or underscore")
    return normalized


class DatasetConfig(BaseModel):
    root_dir: Path
    train_split: str = "train"
    val_split: str = "val"

    @field_validator("train_split", "val_split")
    @classmethod
    def validate_split_name(cls, value: str) -> str:
        return validate_safe_name(value, field_name="dataset split")

    @model_validator(mode="after")
    def validate_distinct_splits(self) -> "DatasetConfig":
        if self.train_split == self.val_split:
            raise ValueError("train_split and val_split must be different")
        return self


class TrainingSpec(BaseModel):
    scene_id: str
    classes: list[str]
    output_dir: Path
    base_model: Path
    dataset: DatasetConfig

    @field_validator("scene_id")
    @classmethod
    def validate_scene_id(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("scene_id must not be empty")
        return normalized

    @field_validator("classes")
    @classmethod
    def validate_classes(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value if item and item.strip()]
        if not normalized:
            raise ValueError("classes must contain at least one class name")
        return normalized


class DatasetYaml(BaseModel):
    path: Path
    train: Path
    val: Path
    nc: int
    names: dict[int, str]


class DatasetDescriptor(BaseModel):
    root_dir: Path
    train_images_dir: Path
    val_images_dir: Path
    train_labels_dir: Path
    val_labels_dir: Path
    dataset_yaml: DatasetYaml


class SampleRecord(BaseModel):
    scene_id: str
    split: str
    sample_name: str
    window_title: str
    region: tuple[int, int, int, int]
    image_path: Path
    metadata_path: Path
