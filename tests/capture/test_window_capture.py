from dataclasses import FrozenInstanceError

import pytest

from auto_ops.capture.windows import WindowSnapshot


def test_window_snapshot_exposes_region():
    snapshot = WindowSnapshot(title="Demo", region=(0, 0, 800, 600), image=None)
    assert snapshot.region == (0, 0, 800, 600)


def test_window_snapshot_is_frozen():
    snapshot = WindowSnapshot(title="Demo", region=(0, 0, 800, 600), image=None)

    with pytest.raises(FrozenInstanceError):
        snapshot.region = (1, 1, 2, 2)
