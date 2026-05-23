"""
graph.py — Graph BFS renderer for Textual.
"""

from __future__ import annotations

import ast

from rich.text import Text
from textual.widget import Widget
from textual.app import RenderResult

from neonodes.theme import SURFACE, TEXT, DIM, YELLOW, TEAL, GREEN, RED

COLOR_CURRENT  = "#F7768E"
COLOR_IN_QUEUE = "#E0AF68"
COLOR_VISITED  = "#9ECE6A"
BG_CURRENT     = "#321820"
BG_IN_QUEUE    = "#2D2010"
BG_VISITED     = "#253320"
BG_NODE        = "#2D3250"


class GraphWidget(Widget):
    DEFAULT_CSS = f"""
    GraphWidget {{
        background: {SURFACE};
        padding: 1 2;
        height: auto;
        min-height: 10;
    }}
    """

    def __init__(self, input_data, **kwargs) -> None:
        super().__init__(**kwargs)
        self._input_data = input_data
        self._states: dict = {}

    def update_graph(self, input_data, states: dict) -> None:
        self._input_data = input_data
        self._states = states
        self.refresh()

    def render(self) -> RenderResult:
        graph, start = self._input_data
        states = self._states
        visited: set[int] = states.get("visited", set())
        queue: list[int] = states.get("queue", [])
        current: int | None = states.get("current")

        result = Text()

        # Two-column layout
        col_w = 24

        # Headers
        result.append("  Adjacency List".ljust(col_w), style=f"bold {DIM}")
        result.append("  Traversal State\n", style=f"bold {DIM}")
        result.append("  " + "─" * (col_w - 2), style=DIM)
        result.append("  " + "─" * 20 + "\n", style=DIM)

        # Build right panel lines
        right_lines = [
            ("Queue:  ", str(queue) if queue else "[]", COLOR_IN_QUEUE),
            ("Visited:", str(sorted(visited)) if visited else "{}",  COLOR_VISITED),
            ("Current:", str(current) if current is not None else "—", COLOR_CURRENT),
        ]

        # Left panel: adjacency list rows
        nodes_sorted = sorted(graph.keys())
        for row_idx, node in enumerate(nodes_sorted):
            neighbors = graph[node]
            node_style = self._node_style(node, visited, queue, current)
            # left column
            result.append("  ")
            result.append(f"{node}", style=node_style)
            result.append(" → [", style=DIM)
            for ni, nb in enumerate(neighbors):
                nb_style = self._node_style(nb, visited, queue, current)
                result.append(str(nb), style=nb_style)
                if ni < len(neighbors) - 1:
                    result.append(", ", style=DIM)
            result.append("]", style=DIM)
            # pad to col_w
            used = 2 + 1 + 4 + len(str(neighbors))
            pad = max(1, col_w - used)
            result.append(" " * pad)

            # right column
            if row_idx < len(right_lines):
                label, val, color = right_lines[row_idx]
                result.append(f"  {label} ", style=DIM)
                result.append(val, style=f"bold {color}")
            result.append("\n")

        # Any remaining right-panel lines
        for row_idx in range(len(nodes_sorted), len(right_lines)):
            result.append(" " * col_w)
            label, val, color = right_lines[row_idx]
            result.append(f"  {label} ", style=DIM)
            result.append(val, style=f"bold {color}")
            result.append("\n")

        return result

    def _node_style(self, node: int, visited: set, queue: list, current) -> str:
        if node == current:
            return f"bold {COLOR_CURRENT} on {BG_CURRENT}"
        if node in queue:
            return f"bold {COLOR_IN_QUEUE} on {BG_IN_QUEUE}"
        if node in visited:
            return f"{COLOR_VISITED} on {BG_VISITED}"
        return f"{TEXT} on {BG_NODE}"


# ---------------------------------------------------------------------------
# GraphRenderer
# ---------------------------------------------------------------------------


class GraphRenderer:

    def make_widget(self, input_data) -> GraphWidget:
        return GraphWidget(input_data=input_data, id="graph-widget")

    def update_widget(self, widget: GraphWidget, input_data, frame_states: dict) -> None:
        widget.update_graph(input_data, frame_states)

    def compute_states(self, frames: list[dict], up_to: int) -> dict:
        visited: set[int] = set()
        queue: list[int] = []
        current: int | None = None

        for frame in frames[:up_to + 1]:
            ft = frame.get("type")
            if ft == "enqueue":
                node = frame.get("node")
                if node not in queue:
                    queue.append(node)
            elif ft == "dequeue":
                node = frame.get("node")
                current = node
                if node in queue:
                    queue.remove(node)
            elif ft == "node_visit":
                node = frame.get("node")
                visited.add(node)

        return {"visited": visited, "queue": queue, "current": current}

    def filter_frames(self, frames: list[dict]) -> list[dict]:
        keep_types = {"node_visit", "enqueue", "dequeue"}
        return [f for f in frames if f.get("type") in keep_types]

    def explain_frame(self, frame: dict, step: int, total: int) -> str:
        ft = frame.get("type")
        prefix = f"  [{step + 1}/{total}]  "
        if ft == "enqueue":
            return f"{prefix}Enqueue node {frame.get('node')} — discovered unvisited neighbor"
        if ft == "dequeue":
            return f"{prefix}Dequeue node {frame.get('node')} — processing next in queue"
        if ft == "node_visit":
            return f"{prefix}Visit node {frame.get('node')} — exploring its neighbors"
        return f"{prefix}—"

    def apply_frame_extras(self, screen, frame: dict) -> None:
        pass

    def legend_entries(self) -> list[tuple[str, str, str]]:
        return [
            (COLOR_CURRENT,  "■", "currently processing"),
            (COLOR_IN_QUEUE, "■", "in queue"),
            (COLOR_VISITED,  "■", "visited"),
            (TEXT,           "■", "unvisited"),
        ]

    def variable_entries(self, frame: dict) -> list[tuple[str, str, str]]:
        node = frame.get("node", "—")
        queue = frame.get("queue", [])
        visited = frame.get("visited", set())
        return [
            ("node",    str(node),           f"bold {COLOR_CURRENT}"),
            ("queue",   str(queue),          COLOR_IN_QUEUE),
            ("visited", str(sorted(visited)), COLOR_VISITED),
        ]

    def parse_input(self, raw: str) -> tuple:
        raw = raw.strip()
        # Format: "{0:[1,2], 1:[0,3]}, 0"
        try:
            brace_end = raw.rindex("}")
            graph_part = raw[:brace_end + 1]
            rest = raw[brace_end + 1:].strip().lstrip(",").strip()
            graph = ast.literal_eval(graph_part)
            start = int(rest)
            if not isinstance(graph, dict):
                raise ValueError("expected dict")
            # Normalize keys/values to int
            graph = {int(k): [int(v) for v in vs] for k, vs in graph.items()}
            return (graph, start)
        except Exception as e:
            raise ValueError(f"Expected '{{0:[1,2], ...}}, start': {e}")

    def serialize_input(self, data: tuple) -> str:
        graph, start = data
        return f"{graph}, {start}"
