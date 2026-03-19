from auto_ops.executor.base import ExecutionResult


class WindowsExecutor:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run

    def click(self, point: tuple[int, int]) -> ExecutionResult:
        if self.dry_run:
            return ExecutionResult(action="click", ok=True, performed=False, detail=str(point))

        import pyautogui

        pyautogui.click(*point)
        return ExecutionResult(action="click", ok=True, performed=True, detail=str(point))
