import importlib
import sys
import types


class FakeLabel:
    def __init__(self, text):
        self.text = text

    def setText(self, text):
        self.text = text


class FakeMainWindowBase:
    def __init__(self):
        self.title = None
        self.central_widget = None

    def setWindowTitle(self, title):
        self.title = title

    def setCentralWidget(self, widget):
        self.central_widget = widget


class FakeUiState:
    def __init__(
        self,
        selected_scene="browser-demo",
        mode="preview",
        can_execute=False,
        executor_backend="standard",
        preview_action=None,
        preview_point=None,
        has_blocking_target=False,
    ):
        self.selected_scene = selected_scene
        self.mode = mode
        self.can_execute = can_execute
        self.executor_backend = executor_backend
        self.preview_action = preview_action
        self.preview_point = preview_point
        self.has_blocking_target = has_blocking_target



def test_importing_main_window_module_does_not_require_pyside6(monkeypatch):
    monkeypatch.setitem(sys.modules, "PySide6", None)
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", None)
    sys.modules.pop("auto_ops.ui.main_window", None)

    module = importlib.import_module("auto_ops.ui.main_window")

    assert callable(module.MainWindow)



def test_main_window_builds_ready_label(monkeypatch):
    fake_widgets = types.SimpleNamespace(QLabel=FakeLabel, QMainWindow=FakeMainWindowBase)
    monkeypatch.setitem(sys.modules, "PySide6", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", fake_widgets)
    sys.modules.pop("auto_ops.ui.main_window", None)

    module = importlib.import_module("auto_ops.ui.main_window")
    window = module.MainWindow()

    assert window.title == "Auto Ops"
    assert isinstance(window.central_widget, FakeLabel)
    assert window.central_widget.text == "Ready"



def test_main_window_renders_preview_summary(monkeypatch):
    fake_widgets = types.SimpleNamespace(QLabel=FakeLabel, QMainWindow=FakeMainWindowBase)
    monkeypatch.setitem(sys.modules, "PySide6", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", fake_widgets)
    monkeypatch.setitem(sys.modules, "auto_ops.ui.view_model", types.SimpleNamespace(UiState=FakeUiState))
    sys.modules.pop("auto_ops.ui.main_window", None)

    module = importlib.import_module("auto_ops.ui.main_window")
    window = module.MainWindow(
        FakeUiState(preview_action="click", preview_point=(30, 20), has_blocking_target=True)
    )

    assert window.central_widget.text == "Mode: preview | Backend: standard | Scene: browser-demo | Blocking: yes | Planned: click @(30, 20)"



def test_main_window_refreshes_preview_summary(monkeypatch):
    fake_widgets = types.SimpleNamespace(QLabel=FakeLabel, QMainWindow=FakeMainWindowBase)
    monkeypatch.setitem(sys.modules, "PySide6", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", fake_widgets)
    monkeypatch.setitem(sys.modules, "auto_ops.ui.view_model", types.SimpleNamespace(UiState=FakeUiState))
    sys.modules.pop("auto_ops.ui.main_window", None)

    module = importlib.import_module("auto_ops.ui.main_window")
    window = module.MainWindow()

    window.update_state(FakeUiState(preview_action="click", preview_point=(30, 20), has_blocking_target=True))

    assert window.central_widget.text == "Mode: preview | Backend: standard | Scene: browser-demo | Blocking: yes | Planned: click @(30, 20)"
