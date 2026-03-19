from __future__ import annotations

from pathlib import Path
import struct
import zlib

import numpy as np
import yaml

from auto_ops.training.models import SampleRecord, validate_safe_name

_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class SampleCollector:
    def __init__(self, output_dir: Path, scene_id: str, capture):
        self.output_dir = Path(output_dir)
        self.scene_id = scene_id
        self.capture = capture

    def collect(self, split: str, sample_name: str) -> SampleRecord:
        safe_split = validate_safe_name(split, field_name="split")
        safe_sample_name = validate_safe_name(sample_name, field_name="sample_name")
        snapshot = self.capture.grab()
        image_path = self.output_dir / "images" / safe_split / f"{safe_sample_name}.png"
        metadata_path = self.output_dir / "records" / safe_split / f"{safe_sample_name}.yaml"
        image_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        image_path.write_bytes(_image_to_bytes(snapshot.image))

        metadata = {
            "scene_id": self.scene_id,
            "split": safe_split,
            "sample_name": safe_sample_name,
            "window_title": snapshot.title,
            "region": list(snapshot.region),
            "image_path": image_path.as_posix(),
        }
        metadata_path.write_text(yaml.safe_dump(metadata, sort_keys=False, allow_unicode=True), encoding="utf-8")

        return SampleRecord(
            scene_id=self.scene_id,
            split=safe_split,
            sample_name=safe_sample_name,
            window_title=snapshot.title,
            region=snapshot.region,
            image_path=image_path,
            metadata_path=metadata_path,
        )



def _image_to_bytes(image) -> bytes:
    if isinstance(image, np.ndarray):
        return _encode_png(image)
    if isinstance(image, bytes):
        return _validate_png_bytes(image)
    if isinstance(image, bytearray):
        return _validate_png_bytes(bytes(image))
    raise TypeError("snapshot image must be a numpy array or encoded PNG bytes")



def _validate_png_bytes(payload: bytes) -> bytes:
    if not payload.startswith(_PNG_SIGNATURE):
        raise ValueError("encoded snapshot image must be PNG bytes")
    return payload



def _encode_png(image: np.ndarray) -> bytes:
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("numpy snapshot image must have shape (height, width, 3)")
    if image.dtype != np.uint8:
        raise ValueError("numpy snapshot image must use uint8 dtype")

    height, width, _channels = image.shape
    raw_rows = b"".join(b"\x00" + image[row_index].tobytes() for row_index in range(height))
    compressed = zlib.compress(raw_rows)
    header = struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0)
    return b"".join(
        [
            _PNG_SIGNATURE,
            _png_chunk(b"IHDR", header),
            _png_chunk(b"IDAT", compressed),
            _png_chunk(b"IEND", b""),
        ]
    )



def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    payload = chunk_type + data
    checksum = zlib.crc32(payload) & 0xFFFFFFFF
    return struct.pack("!I", len(data)) + payload + struct.pack("!I", checksum)
