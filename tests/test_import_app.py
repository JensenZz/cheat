from importlib import import_module
from pathlib import Path
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
            "scene": type("SceneStub", (), {"id": "browser-demo"})(),
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
    monkeypatch.setattr(app_module, "FakeDetector", lambda seeded: object(), raising=False)
    monkeypatch.setattr(app_module, "PreviewCapture", FakeCapture, raising=False)

    result = app_module.main(Path("strategies/scenes/browser_demo.yaml"))

    assert result == 0
    assert captured["state"].selected_scene == "browser-demo"
    assert captured["state"].preview_action == "click"



def test_main_uses_demo_preview_by_default(monkeypatch):
    app_module = import_module("auto_ops.app")
    captured = {}

    def fake_run_ui(state):
        captured["state"] = state
        return 0

    monkeypatch.setattr(app_module, "run_ui", fake_run_ui, raising=False)
    monkeypatch.setattr(app_module, "PreviewCapture", FakeCapture, raising=False)

    result = app_module.main()

    assert result == 0
    assert captured["state"].selected_scene == "browser-demo"
    assert captured["state"].preview_action == "click"
    assert captured["state"].preview_point == (30, 20)



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
                "scene": type("SceneStub", (), {"id": "browser-demo"})(),
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
    monkeypatch.setattr(app_module, "FakeDetector", lambda seeded: object(), raising=False)
    monkeypatch.setattr(app_module, "PreviewCapture", FakeCapture, raising=False)
    monkeypatch.setattr(app_module, "files", lambda package: resource, raising=False)
    monkeypatch.setattr(app_module, "as_file", lambda path: FakeAsFile(path), raising=False)

    result = app_module.main()

    assert result == 0
    assert captured["scene_path"] == resource_path
    assert captured["state"].selected_scene == "browser-demo"
