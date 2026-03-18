from auto_ops.logging import build_logger


def main() -> int:
    build_logger("auto_ops").info("app boot")
    return 0
