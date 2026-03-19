import importlib
import sys
import types


class FakeApplication:
    _instance = None

    def __init__(self, args):
        self.args = args
        self.executed = False
        FakeApplication._instance = self

    @classmethod
    def instance(cls):
        return cls._instance

    def exec(self):
        self.executed = True
        return 0


class FakeWindow:
    def __init__(self, state=None):
        self.state = state
        self.shown = False

    def show(self):
        self.shown = True



def test_importing_ui_app_module_does_not_require_pyside6(monkeypatch):
    monkeypatch.setitem(sys.modules, "PySide6", None)
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", None)
    sys.modules.pop("auto_ops.ui.app", None)
    sys.modules.pop("auto_ops.ui.main_window", None)

    ui_app = importlib.import_module("auto_ops.ui.app")

    assert callable(ui_app.build_ui)



def test_build_ui_keeps_application_reference(monkeypatch):
    fake_widgets = types.SimpleNamespace(QApplication=FakeApplication)
    monkeypatch.setitem(sys.modules, "PySide6", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", fake_widgets)
    monkeypatch.setitem(sys.modules, "auto_ops.ui.main_window", types.SimpleNamespace(MainWindow=FakeWindow))
    sys.modules.pop("auto_ops.ui.app", None)

    ui_app = importlib.import_module("auto_ops.ui.app")

    window = ui_app.build_ui()

    assert isinstance(window, FakeWindow)
    assert window.shown is True
    assert getattr(ui_app, "_APP", None) is FakeApplication.instance()



def test_build_ui_passes_state_to_window(monkeypatch):
    fake_widgets = types.SimpleNamespace(QApplication=FakeApplication)
    monkeypatch.setitem(sys.modules, "PySide6", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", fake_widgets)
    monkeypatch.setitem(sys.modules, "auto_ops.ui.main_window", types.SimpleNamespace(MainWindow=FakeWindow))
    sys.modules.pop("auto_ops.ui.app", None)

    ui_app = importlib.import_module("auto_ops.ui.app")
    state = object()

    window = ui_app.build_ui(state)

    assert window.state is state



def test_run_ui_enters_application_event_loop(monkeypatch):
    fake_widgets = types.SimpleNamespace(QApplication=FakeApplication)
    monkeypatch.setitem(sys.modules, "PySide6", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", fake_widgets)
    monkeypatch.setitem(sys.modules, "auto_ops.ui.main_window", types.SimpleNamespace(MainWindow=FakeWindow))
    sys.modules.pop("auto_ops.ui.app", None)

    ui_app = importlib.import_module("auto_ops.ui.app")

    exit_code = ui_app.run_ui(object())

    assert exit_code == 0
    assert ui_app._APP.executed is True



def test_run_ui_keeps_window_reference(monkeypatch):
    fake_widgets = types.SimpleNamespace(QApplication=FakeApplication)
    monkeypatch.setitem(sys.modules, "PySide6", types.SimpleNamespace())
    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", fake_widgets)
    monkeypatch.setitem(sys.modules, "auto_ops.ui.main_window", types.SimpleNamespace(MainWindow=FakeWindow))
    sys.modules.pop("auto_ops.ui.app", None)

    ui_app = importlib.import_module("auto_ops.ui.app")

    ui_app.run_ui(object())

    assert getattr(ui_app, "_WINDOW", None) is not None
    assert isinstance(ui_app._WINDOW, FakeWindow)
    assert ui_app._WINDOW.shown is True
