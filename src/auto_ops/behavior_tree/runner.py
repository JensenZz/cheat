from typing import Any

from auto_ops.behavior_tree.nodes import Node



def run_tree(root: Node, state: Any) -> bool:
    return root.tick(state)
