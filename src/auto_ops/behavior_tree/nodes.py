from __future__ import annotations

from typing import Any, Callable, Protocol


class Node(Protocol):
    def tick(self, state: Any) -> bool: ...


class ConditionNode:
    def __init__(self, predicate: Callable[[Any], bool]) -> None:
        self.predicate = predicate

    def tick(self, state: Any) -> bool:
        return bool(self.predicate(state))


class ActionNode:
    def __init__(self, fn: Callable[[Any], bool]) -> None:
        self.fn = fn

    def tick(self, state: Any) -> bool:
        return bool(self.fn(state))


class SequenceNode:
    def __init__(self, children: list[Node]) -> None:
        self.children = children

    def tick(self, state: Any) -> bool:
        for child in self.children:
            if not child.tick(state):
                return False
        return True
