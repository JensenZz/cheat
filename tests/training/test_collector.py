from pathlib import Path

import numpy as np
import pytest

from auto_ops.shared.models import WindowSnapshot
from auto_ops.training.collector import SampleCollector, _encode_png
from auto_ops.training.models import SampleRecord


class FakeCapture:
    def __init__(self, snapshot: WindowSnapshot):
        self.snapshot = snapshot
        self.calls = 0

    def grab(self) -> WindowSnapshot:
        self.calls += 1
        return self.snapshot



def test_sample_collector_only_uses_capture_abstraction(tmp_path):
    snapshot = WindowSnapshot(
        title="Browser Demo",
        region=(10, 20, 210, 120),
        image=_encode_png(np.array([[[255, 0, 0]]], dtype=np.uint8)),
    )
    collector = SampleCollector(output_dir=tmp_path, scene_id="browser-demo", capture=FakeCapture(snapshot))

    record = collector.collect(split="train", sample_name="sample-001")

    assert isinstance(record, SampleRecord)
    assert record.scene_id == "browser-demo"
    assert record.split == "train"
    assert record.window_title == "Browser Demo"
    assert record.region == (10, 20, 210, 120)



def test_sample_collector_persists_image_and_metadata(tmp_path):
    encoded_png = _encode_png(np.array([[[0, 255, 0]]], dtype=np.uint8))
    snapshot = WindowSnapshot(
        title="Browser Demo",
        region=(10, 20, 210, 120),
        image=encoded_png,
    )
    capture = FakeCapture(snapshot)
    collector = SampleCollector(output_dir=tmp_path, scene_id="browser-demo", capture=capture)

    record = collector.collect(split="val", sample_name="sample-002")

    assert capture.calls == 1
    assert record.image_path == tmp_path / "images/val/sample-002.png"
    assert record.image_path.read_bytes() == encoded_png
    assert record.metadata_path == tmp_path / "records/val/sample-002.yaml"
    assert "Browser Demo" in record.metadata_path.read_text(encoding="utf-8")
    assert "browser-demo" in record.metadata_path.read_text(encoding="utf-8")



def test_sample_collector_works_with_fake_capture_without_windows_api(tmp_path):
    snapshot = WindowSnapshot(
        title="Fake Window",
        region=(1, 2, 3, 4),
        image=_encode_png(np.array([[[0, 0, 255]]], dtype=np.uint8)),
    )
    collector = SampleCollector(output_dir=tmp_path, scene_id="browser-demo", capture=FakeCapture(snapshot))

    record = collector.collect(split="train", sample_name="sample-003")

    assert record.image_path.exists()
    assert record.metadata_path.exists()
    assert record.window_title == "Fake Window"



def test_sample_collector_rejects_unsafe_split_or_sample_name(tmp_path):
    snapshot = WindowSnapshot(
        title="Fake Window",
        region=(1, 2, 3, 4),
        image=_encode_png(np.array([[[0, 0, 255]]], dtype=np.uint8)),
    )
    collector = SampleCollector(output_dir=tmp_path, scene_id="browser-demo", capture=FakeCapture(snapshot))

    with pytest.raises(ValueError, match="split"):
        collector.collect(split="../train", sample_name="sample-004")

    with pytest.raises(ValueError, match="sample_name"):
        collector.collect(split="train", sample_name="../sample-004")



def test_sample_collector_encodes_numpy_image_as_png(tmp_path):
    snapshot = WindowSnapshot(
        title="Browser Demo",
        region=(10, 20, 11, 21),
        image=np.array([[[255, 0, 0]]], dtype=np.uint8),
    )
    collector = SampleCollector(output_dir=tmp_path, scene_id="browser-demo", capture=FakeCapture(snapshot))

    record = collector.collect(split="train", sample_name="sample-005")
    payload = record.image_path.read_bytes()

    assert payload.startswith(b"\x89PNG\r\n\x1a\n")
    assert b"IHDR" in payload
    assert payload.endswith(b"IEND\xaeB`\x82")



def test_sample_collector_rejects_non_png_encoded_bytes(tmp_path):
    snapshot = WindowSnapshot(
        title="Browser Demo",
        region=(10, 20, 11, 21),
        image=b"not-a-png",
    )
    collector = SampleCollector(output_dir=tmp_path, scene_id="browser-demo", capture=FakeCapture(snapshot))

    with pytest.raises(ValueError, match="PNG"):
        collector.collect(split="train", sample_name="sample-006")
