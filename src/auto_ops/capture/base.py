"""Capture backend abstractions."""

from __future__ import annotations

from typing import Protocol

from auto_ops.shared.models import WindowSnapshot


class CaptureBackend(Protocol):
    def locate(self):
        """Locate the target window or capture region."""

    def grab(self) -> WindowSnapshot:
        """Capture and return a window snapshot."""
