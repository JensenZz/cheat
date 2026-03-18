from auto_ops.logging import build_logger


def test_build_logger_writes_named_logger(caplog):
    logger = build_logger("auto_ops.test")
    logger.info("hello")
    assert any(record.name == "auto_ops.test" for record in caplog.records)
