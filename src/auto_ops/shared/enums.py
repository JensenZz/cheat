from enum import StrEnum


class ActionType(StrEnum):
    CLICK = "click"
    INPUT_TEXT = "input_text"
    WAIT = "wait"
    FOCUS_WINDOW = "focus_window"
