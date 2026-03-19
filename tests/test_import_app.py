from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
import types


class FakeWindow:
    def __init__(self, state):
        self.state = state
        self.shown = True


class FakeCapture:
    def grab(self):
        from auto_ops.capture.windows import WindowSnapshot

        return WindowSnapshot(title="Demo", region=(0, 0, 800, 600), image=None)



def test_package_imports():
    module = import_module("auto_ops")
    assert module.__package__ == "auto_ops"



def test_main_builds_preview_ui_state(monkeypatch):
    app_module = import_module("auto_ops.app")

    monkeypatch.setattr(app_module, "load_scene", lambda path: type(
        "SceneBundleStub",
        (),
        {
            "scene": type(
                "SceneStub",
                (),
                {
                    "id": "browser-demo",
                    "mode": "preview",
                    "capture_backend": "preview",
                    "detector_backend": "fake",
                    "detector_model": None,
                    "executor_backend": "standard",
                    "window_match": type("WindowMatchStub", (), {"title_contains": ["Demo"]})(),
                },
            )(),
            "targets": [type("TargetStub", (), {"class_name": "primary_button", "weight": 80})()],
        },
    )(), raising=False)
    monkeypatch.setattr(app_module, "preview_cycle", lambda capture, detector, weights: type(
        "PreviewStub",
        (),
        {
            "planned_action": "click",
            "planned_point": (30, 20),
            "has_blocking_target": False,
        },
    )(), raising=False)
    captured = {}

    def fake_run_ui(state):
        captured["state"] = state
        return 0

    monkeypatch.setattr(app_module, "run_ui", fake_run_ui, raising=False)
    monkeypatch.setattr(app_module, "_build_capture", lambda scene: captured.setdefault("capture_backend", scene.capture_backend) or FakeCapture(), raising=False)
    monkeypatch.setattr(app_module, "_build_detector", lambda scene: captured.setdefault("detector_backend", scene.detector_backend) or object(), raising=False)

    result = app_module.main(Path("strategies/scenes/browser_demo.yaml"))

    assert result == 0
    assert captured["capture_backend"] == "preview"
    assert captured["detector_backend"] == "fake"
    assert captured["state"].selected_scene == "browser-demo"
    assert captured["state"].mode == "preview"
    assert captured["state"].executor_backend == "standard"
    assert captured["state"].preview_action == "click"



def test_main_uses_demo_preview_by_default(monkeypatch):
    app_module = import_module("auto_ops.app")
    captured = {}

    def fake_run_ui(state):
        captured["state"] = state
        return 0

    monkeypatch.setattr(app_module, "preview_cycle", lambda capture, detector, weights: type(
        "PreviewStub",
        (),
        {
            "planned_action": "click",
            "planned_point": (30, 20),
            "has_blocking_target": False,
        },
    )(), raising=False)
    monkeypatch.setattr(app_module, "run_ui", fake_run_ui, raising=False)
    monkeypatch.setattr(app_module, "_build_capture", lambda scene: FakeCapture(), raising=False)
    monkeypatch.setattr(app_module, "_build_detector", lambda scene: object(), raising=False)

    result = app_module.main()

    assert result == 0
    assert captured["state"].selected_scene == "browser-demo"
    assert captured["state"].mode == "preview"
    assert captured["state"].executor_backend == "standard"
    assert captured["state"].preview_action == "click"
    assert captured["state"].preview_point == (30, 20)



def test_main_uses_run_cycle_with_dry_run_executor(monkeypatch):
    app_module = import_module("auto_ops.app")
    captured = {}

    monkeypatch.setattr(app_module, "load_scene", lambda path: type(
        "SceneBundleStub",
        (),
        {
            "scene": type(
                "SceneStub",
                (),
                {
                    "id": "browser-demo",
                    "mode": "dry_run",
                    "capture_backend": "windows",
                    "detector_backend": "fake",
                    "detector_model": None,
                    "executor_backend": "standard",
                    "window_match": type("WindowMatchStub", (), {"title_contains": ["Demo"]})(),
                },
            )(),
            "targets": [type("TargetStub", (), {"class_name": "primary_button", "weight": 80})()],
        },
    )(), raising=False)

    def fake_run_cycle(capture, detector, executor, weights, mode):
        captured["mode"] = mode
        captured["dry_run"] = executor.dry_run
        return type(
            "CycleStub",
            (),
            {
                "selected_target": type("TargetStub", (), {"center": (30, 20)})(),
                "execution": type("ExecutionStub", (), {"action": "click"})(),
                "planned_action": "click",
                "planned_point": (30, 20),
                "has_blocking_target": False,
            },
        )()

    monkeypatch.setattr(app_module, "run_cycle", fake_run_cycle, raising=False)
    monkeypatch.setattr(app_module, "preview_cycle", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("preview_cycle should not run in dry_run mode")), raising=False)
    monkeypatch.setattr(app_module, "run_ui", lambda state: 0, raising=False)
    monkeypatch.setattr(app_module, "_build_capture", lambda scene: captured.setdefault("capture_backend", scene.capture_backend) or FakeCapture(), raising=False)
    monkeypatch.setattr(app_module, "_build_detector", lambda scene: captured.setdefault("detector_backend", scene.detector_backend) or object(), raising=False)

    result = app_module.main(Path("strategies/scenes/browser_demo.yaml"))

    assert result == 0
    assert captured["capture_backend"] == "windows"
    assert captured["detector_backend"] == "fake"
    assert captured["mode"] == "dry_run"
    assert captured["dry_run"] is True



def test_main_uses_run_cycle_with_live_executor(monkeypatch):
    app_module = import_module("auto_ops.app")
    captured = {}

    monkeypatch.setattr(app_module, "load_scene", lambda path: type(
        "SceneBundleStub",
        (),
        {
            "scene": type(
                "SceneStub",
                (),
                {
                    "id": "browser-demo",
                    "mode": "live",
                    "capture_backend": "windows",
                    "detector_backend": "fake",
                    "detector_model": None,
                    "executor_backend": "standard",
                    "window_match": type("WindowMatchStub", (), {"title_contains": ["Demo"]})(),
                },
            )(),
            "targets": [type("TargetStub", (), {"class_name": "primary_button", "weight": 80})()],
        },
    )(), raising=False)

    def fake_run_cycle(capture, detector, executor, weights, mode):
        captured["mode"] = mode
        captured["dry_run"] = executor.dry_run
        return type(
            "CycleStub",
            (),
            {
                "selected_target": type("TargetStub", (), {"center": (30, 20)})(),
                "execution": type("ExecutionStub", (), {"action": "click"})(),
                "planned_action": "click",
                "planned_point": (30, 20),
                "has_blocking_target": False,
            },
        )()

    monkeypatch.setattr(app_module, "run_cycle", fake_run_cycle, raising=False)
    monkeypatch.setattr(app_module, "preview_cycle", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("preview_cycle should not run in live mode")), raising=False)
    monkeypatch.setattr(app_module, "run_ui", lambda state: 0, raising=False)
    monkeypatch.setattr(app_module, "_build_capture", lambda scene: captured.setdefault("capture_backend", scene.capture_backend) or FakeCapture(), raising=False)
    monkeypatch.setattr(app_module, "_build_detector", lambda scene: captured.setdefault("detector_backend", scene.detector_backend) or object(), raising=False)

    result = app_module.main(Path("strategies/scenes/browser_demo.yaml"))

    assert result == 0
    assert captured["capture_backend"] == "windows"
    assert captured["detector_backend"] == "fake"
    assert captured["mode"] == "live"
    assert captured["dry_run"] is False



def test_main_uses_yolo_detector_backend_when_selected(monkeypatch):
    app_module = import_module("auto_ops.app")
    captured = {}

    monkeypatch.setattr(app_module, "load_scene", lambda path: type(
        "SceneBundleStub",
        (),
        {
            "scene": type(
                "SceneStub",
                (),
                {
                    "id": "browser-demo",
                    "mode": "preview",
                    "capture_backend": "windows",
                    "detector_backend": "yolo",
                    "detector_model": "models/browser.pt",
                    "executor_backend": "standard",
                    "window_match": type("WindowMatchStub", (), {"title_contains": ["Demo"]})(),
                },
            )(),
            "targets": [type("TargetStub", (), {"class_name": "primary_button", "weight": 80})()],
        },
    )(), raising=False)

    monkeypatch.setattr(app_module, "preview_cycle", lambda capture, detector, weights: type(
        "PreviewStub",
        (),
        {
            "planned_action": "click",
            "planned_point": (30, 20),
            "has_blocking_target": False,
        },
    )(), raising=False)
    monkeypatch.setattr(app_module, "run_ui", lambda state: 0, raising=False)
    monkeypatch.setattr(app_module, "_build_capture", lambda scene: FakeCapture(), raising=False)

    def fake_build_detector(scene):
        captured["detector_backend"] = scene.detector_backend
        captured["detector_model"] = scene.detector_model
        return object()

    monkeypatch.setattr(app_module, "_build_detector", fake_build_detector, raising=False)

    result = app_module.main(Path("strategies/scenes/browser_demo.yaml"))

    assert result == 0
    assert captured == {"detector_backend": "yolo", "detector_model": "models/browser.pt"}



def test_main_loads_default_scene_from_package_resource(monkeypatch):
    app_module = import_module("auto_ops.app")
    captured = {}
    resource_path = Path("virtual/browser_demo.yaml")
    resource = types.SimpleNamespace(joinpath=lambda name: resource_path)

    class FakeAsFile:
        def __init__(self, path):
            self.path = path

        def __enter__(self):
            return self.path

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_load_scene(path):
        captured["scene_path"] = path
        return type(
            "SceneBundleStub",
            (),
            {
                "scene": type(
                    "SceneStub",
                    (),
                    {
                        "id": "browser-demo",
                        "mode": "preview",
                        "capture_backend": "preview",
                        "detector_backend": "fake",
                        "detector_model": None,
                        "executor_backend": "standard",
                        "window_match": type("WindowMatchStub", (), {"title_contains": ["Demo"]})(),
                    },
                )(),
                "targets": [type("TargetStub", (), {"class_name": "primary_button", "weight": 80})()],
            },
        )()

    def fake_preview_cycle(capture, detector, weights):
        return type(
            "PreviewStub",
            (),
            {
                "planned_action": "click",
                "planned_point": (30, 20),
                "has_blocking_target": False,
            },
        )()

    def fake_run_ui(state):
        captured["state"] = state
        return 0

    monkeypatch.setattr(app_module, "load_scene", fake_load_scene, raising=False)
    monkeypatch.setattr(app_module, "preview_cycle", fake_preview_cycle, raising=False)
    monkeypatch.setattr(app_module, "run_ui", fake_run_ui, raising=False)
    monkeypatch.setattr(app_module, "_build_capture", lambda scene: FakeCapture(), raising=False)
    monkeypatch.setattr(app_module, "_build_detector", lambda scene: object(), raising=False)
    monkeypatch.setattr(app_module, "files", lambda package: resource, raising=False)
    monkeypatch.setattr(app_module, "as_file", lambda path: FakeAsFile(path), raising=False)

    result = app_module.main()

    assert result == 0
    assert captured["scene_path"] == resource_path
    assert captured["state"].selected_scene == "browser-demo"
    assert captured["state"].mode == "preview"
    assert captured["state"].executor_backend == "standard"



def test_importing_app_does_not_require_ultralytics(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "ultralytics":
            raise AssertionError("ultralytics should not be imported during auto_ops.app import")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    module = import_module("auto_ops.app")

    assert module.__name__ == "auto_ops.app"



def test_build_capture_returns_preview_capture_for_preview_backend():
    app_module = import_module("auto_ops.app")

    capture = app_module._build_capture(SimpleNamespace(capture_backend="preview", window_match=None))

    assert isinstance(capture, app_module.PreviewCapture)



def test_build_detector_returns_fake_detector_for_fake_backend():
    app_module = import_module("auto_ops.app")

    detector = app_module._build_detector(SimpleNamespace(detector_backend="fake", detector_model=None))

    assert detector.__class__.__name__ == "FakeDetector"



def test_build_detector_builds_yolo_detector_lazily(monkeypatch):
    app_module = import_module("auto_ops.app")
    captured = {}

    class FakeYOLO:
        def __init__(self, model_path):
            captured["model_path"] = model_path

    monkeypatch.setattr(app_module, "YOLO", FakeYOLO, raising=False)

    detector = app_module._build_detector(SimpleNamespace(detector_backend="yolo", detector_model="models/browser.pt"))

    assert detector.__class__.__name__ == "YoloDetector"
    assert captured["model_path"] == "models/browser.pt"
