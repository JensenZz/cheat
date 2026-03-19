from auto_ops.behavior_tree.nodes import ActionNode, ConditionNode, SequenceNode
from auto_ops.behavior_tree.runner import run_tree


def test_sequence_stops_on_failed_condition():
    calls = []
    tree = SequenceNode([
        ConditionNode(lambda state: False),
        ActionNode(lambda state: calls.append("clicked") or True),
    ])

    result = tree.tick({})

    assert result is False
    assert calls == []


def test_run_tree_executes_root_node():
    tree = SequenceNode([
        ConditionNode(lambda state: state["enabled"]),
        ActionNode(lambda state: state.update({"ran": True}) or True),
    ])
    state = {"enabled": True, "ran": False}

    result = run_tree(tree, state)

    assert result is True
    assert state["ran"] is True
