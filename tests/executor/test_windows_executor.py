from auto_ops.executor.windows import WindowsExecutor


def test_windows_executor_records_dry_run_click():
    executor = WindowsExecutor(dry_run=True)

    result = executor.click((100, 200))

    assert result.ok is True
    assert result.performed is False
    assert result.action == "click"
