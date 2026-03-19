from __future__ import annotations



def _build_label_text(state) -> str:
    if not getattr(state, "preview_action", None):
        return "Ready"

    blocking = "yes" if state.has_blocking_target else "no"
    return (
        f"Mode: {state.mode} | "
        f"Backend: {state.executor_backend} | "
        f"Scene: {state.selected_scene} | "
        f"Blocking: {blocking} | "
        f"Planned: {state.preview_action} @{state.preview_point}"
    )


class MainWindow:
    def __new__(cls, state=None):
        from PySide6.QtWidgets import QLabel, QMainWindow

        if state is None:
            from auto_ops.ui.view_model import UiState

            state = UiState(selected_scene="browser-demo")

        class _MainWindow(QMainWindow):
            def __init__(self) -> None:
                super().__init__()
                self.setWindowTitle("Auto Ops")
                self._state = state
                self._label = QLabel(_build_label_text(self._state))
                self.setCentralWidget(self._label)

            def update_state(self, state) -> None:
                self._state = state
                self._label.setText(_build_label_text(self._state))

        return _MainWindow()
