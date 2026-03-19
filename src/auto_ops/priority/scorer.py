from auto_ops.shared.models import Detection


def score_target(target: Detection, weights: dict[str, int]) -> float:
    return weights.get(target.class_name, 0) + target.confidence



def pick_best_target(targets: list[Detection], weights: dict[str, int]) -> Detection | None:
    if not targets:
        return None
    return max(targets, key=lambda item: score_target(item, weights))
