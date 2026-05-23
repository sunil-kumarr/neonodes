"""Protocol defining the interface every problem module must satisfy."""

from __future__ import annotations
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ProblemModule(Protocol):
    TITLE: str
    CATEGORY: str
    DIFFICULTY: str
    DESCRIPTION: str
    DEFAULT_INPUT: Any   # grid, tree node, array, etc.
    CODE_LINES: list[str]
    RENDERER: str        # "grid" | "tree" | "array"

    def run(self, input_data: Any) -> list[dict]: ...
