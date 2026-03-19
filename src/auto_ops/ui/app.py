from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from auto_ops.ui.main_window import MainWindow


_APP = None
_WINDOW = None


def build_ui(state=None) -> "MainWindow":
    global _APP, _WINDOW

    from PySide6.QtWidgets import QApplication

    from auto_ops.ui.main_window import MainWindow

    _APP = QApplication.instance() or QApplication([])
    _WINDOW = MainWindow(state)
    _WINDOW.show()
    return _WINDOW



def run_ui(state=None) -> int:
    build_ui(state)
    return _APP.exec()
