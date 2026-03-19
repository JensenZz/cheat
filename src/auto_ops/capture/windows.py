"""Windows capture helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from auto_ops.capture.base import CaptureBackend
from auto_ops.shared.models import WindowSnapshot


@dataclass(frozen=True)
class WindowLocation:
    title: str
    region: tuple[int, int, int, int]


def _normalize_image(frame) -> np.ndarray:
    width, height = frame.size
    bgra = np.frombuffer(frame.bgra, dtype=np.uint8)
    expected_size = width * height * 4
    if bgra.size != expected_size:
        raise RuntimeError("Captured frame size did not match BGRA buffer length")
    pixels = bgra.reshape((height, width, 4))
    return pixels[:, :, [2, 1, 0]].copy()


class WindowsCapture(CaptureBackend):
    def __init__(self, window_match):
        self.window_match = window_match

    def locate(self) -> WindowLocation:
        import win32gui

        matched: WindowLocation | None = None
        keywords = [keyword for keyword in self.window_match.title_contains if keyword]

        def visit(handle, _extra):
            nonlocal matched
            if matched is not None or not win32gui.IsWindowVisible(handle):
                return

            title = win32gui.GetWindowText(handle)
            if not title:
                return
            if keywords and not any(keyword in title for keyword in keywords):
                return

            matched = WindowLocation(
                title=title,
                region=tuple(int(value) for value in win32gui.GetWindowRect(handle)),
            )

        win32gui.EnumWindows(visit, None)

        if matched is None:
            joined = ", ".join(keywords) or "<empty>"
            raise RuntimeError(f"No visible window matched title_contains: {joined}")

        return matched

    def grab(self) -> WindowSnapshot:
        import mss

        located = self.locate()
        left, top, right, bottom = located.region
        monitor = {
            "left": left,
            "top": top,
            "width": right - left,
            "height": bottom - top,
        }
        with mss.mss() as sct:
            image = _normalize_image(sct.grab(monitor))
        return WindowSnapshot(title=located.title, region=located.region, image=image)


__all__ = ["WindowLocation", "WindowsCapture", "WindowSnapshot"]
