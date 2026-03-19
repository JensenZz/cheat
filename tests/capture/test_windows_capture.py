import sys
import types

import pytest

from auto_ops.capture.windows import WindowsCapture



def install_fake_win32gui(monkeypatch, windows):
    module = types.SimpleNamespace()

    def enum_windows(callback, extra):
        for handle, title, rect, visible in windows:
            extra[handle] = {"title": title, "rect": rect, "visible": visible}
            callback(handle, extra)

    module.EnumWindows = enum_windows
    module.GetWindowText = lambda handle: windows[handle][1] if isinstance(windows, dict) else None
    module.GetWindowRect = lambda handle: windows[handle][2] if isinstance(windows, dict) else None
    module.IsWindowVisible = lambda handle: windows[handle][3] if isinstance(windows, dict) else None
    monkeypatch.setitem(sys.modules, "win32gui", module)
    return module



def install_fake_mss(monkeypatch, grabbed_images):
    class FakeShot:
        size = (1, 1)
        bgra = bytes([1, 2, 3, 255])

    class FakeMSS:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def grab(self, monitor):
            grabbed_images.append(monitor)
            return FakeShot()

    module = types.SimpleNamespace(mss=lambda: FakeMSS())
    monkeypatch.setitem(sys.modules, "mss", module)
    return module



def test_windows_capture_locates_window_by_title_contains(monkeypatch):
    windows = {
        1: (1, "Other App", (1, 2, 3, 4), True),
        2: (2, "Browser Demo - Edge", (10, 20, 210, 120), True),
    }
    win32gui = types.SimpleNamespace(
        EnumWindows=lambda callback, extra: [callback(handle, extra) for handle in windows],
        GetWindowText=lambda handle: windows[handle][1],
        GetWindowRect=lambda handle: windows[handle][2],
        IsWindowVisible=lambda handle: windows[handle][3],
    )
    monkeypatch.setitem(sys.modules, "win32gui", win32gui)

    capture = WindowsCapture(window_match=types.SimpleNamespace(title_contains=["Demo"] ))

    located = capture.locate()

    assert located.title == "Browser Demo - Edge"
    assert located.region == (10, 20, 210, 120)



def test_windows_capture_grab_returns_window_snapshot(monkeypatch):
    windows = {
        2: (2, "Browser Demo - Edge", (10, 20, 210, 120), True),
    }
    win32gui = types.SimpleNamespace(
        EnumWindows=lambda callback, extra: [callback(handle, extra) for handle in windows],
        GetWindowText=lambda handle: windows[handle][1],
        GetWindowRect=lambda handle: windows[handle][2],
        IsWindowVisible=lambda handle: windows[handle][3],
    )
    monkeypatch.setitem(sys.modules, "win32gui", win32gui)
    grabbed_images = []
    install_fake_mss(monkeypatch, grabbed_images)

    capture = WindowsCapture(window_match=types.SimpleNamespace(title_contains=["Demo"]))

    snapshot = capture.grab()

    assert snapshot.title == "Browser Demo - Edge"
    assert snapshot.region == (10, 20, 210, 120)
    assert snapshot.image is not None
    assert grabbed_images == [{"left": 10, "top": 20, "width": 200, "height": 100}]



def test_windows_capture_raises_clear_error_when_window_not_found(monkeypatch):
    win32gui = types.SimpleNamespace(
        EnumWindows=lambda callback, extra: None,
        GetWindowText=lambda handle: "",
        GetWindowRect=lambda handle: (0, 0, 0, 0),
        IsWindowVisible=lambda handle: True,
    )
    monkeypatch.setitem(sys.modules, "win32gui", win32gui)

    capture = WindowsCapture(window_match=types.SimpleNamespace(title_contains=["Demo"]))

    with pytest.raises(RuntimeError, match="Demo"):
        capture.locate()



def test_windows_capture_rejects_empty_title_keywords(monkeypatch):
    win32gui = types.SimpleNamespace(
        EnumWindows=lambda callback, extra: None,
        GetWindowText=lambda handle: "Demo",
        GetWindowRect=lambda handle: (0, 0, 100, 100),
        IsWindowVisible=lambda handle: True,
    )
    monkeypatch.setitem(sys.modules, "win32gui", win32gui)

    capture = WindowsCapture(window_match=types.SimpleNamespace(title_contains=[]))

    with pytest.raises(RuntimeError, match="title_contains"):
        capture.locate()



def test_windows_capture_grab_uses_window_rect_as_snapshot_region(monkeypatch):
    windows = {
        3: (3, "Demo App", (100, 200, 500, 700), True),
    }
    win32gui = types.SimpleNamespace(
        EnumWindows=lambda callback, extra: [callback(handle, extra) for handle in windows],
        GetWindowText=lambda handle: windows[handle][1],
        GetWindowRect=lambda handle: windows[handle][2],
        IsWindowVisible=lambda handle: windows[handle][3],
    )
    monkeypatch.setitem(sys.modules, "win32gui", win32gui)
    install_fake_mss(monkeypatch, [])

    capture = WindowsCapture(window_match=types.SimpleNamespace(title_contains=["Demo"]))

    snapshot = capture.grab()

    assert snapshot.region == (100, 200, 500, 700)
    assert snapshot.image is not None



def test_windows_capture_grab_normalizes_mss_frame_to_rgb_array(monkeypatch):
    windows = {
        4: (4, "Demo App", (10, 20, 12, 21), True),
    }
    win32gui = types.SimpleNamespace(
        EnumWindows=lambda callback, extra: [callback(handle, extra) for handle in windows],
        GetWindowText=lambda handle: windows[handle][1],
        GetWindowRect=lambda handle: windows[handle][2],
        IsWindowVisible=lambda handle: windows[handle][3],
    )
    monkeypatch.setitem(sys.modules, "win32gui", win32gui)

    class FakeShot:
        size = (2, 1)
        bgra = bytes([1, 2, 3, 255, 10, 20, 30, 255])

    class FakeMSS:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def grab(self, monitor):
            return FakeShot()

    monkeypatch.setitem(sys.modules, "mss", types.SimpleNamespace(mss=lambda: FakeMSS()))

    capture = WindowsCapture(window_match=types.SimpleNamespace(title_contains=["Demo"]))

    snapshot = capture.grab()

    assert snapshot.image.tolist() == [[[3, 2, 1], [30, 20, 10]]]
