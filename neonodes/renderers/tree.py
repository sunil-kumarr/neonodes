"""
tree.py — ASCII binary tree renderer for Textual.
"""

from __future__ import annotations

import ast

from rich.text import Text
from textual.widget import Widget
from textual.app import RenderResult

from neonodes.theme import SURFACE, TEXT, DIM, YELLOW, TEAL

COLOR_CURRENT  = "#F7768E"
COLOR_VISITED  = "#9ECE6A"
BG_CURRENT     = "#321820"
BG_VISITED     = "#253320"
BG_NODE        = "#2D3250"


# ---------------------------------------------------------------------------
# TreeWidget
# ---------------------------------------------------------------------------


class TreeWidget(Widget):
    DEFAULT_CSS = f"""
    TreeWidget {{
        background: {SURFACE};
        padding: 1 2;
        height: auto;
        min-height: 10;
    }}
    """

    def __init__(self, input_data: list, **kwargs) -> None:
        super().__init__(**kwargs)
        self._input_data = input_data
        self._states: dict = {}

    def update_tree(self, input_data: list, states: dict) -> None:
        self._input_data = input_data
        self._states = states
        self.refresh()

    def render(self) -> RenderResult:
        arr = self._input_data
        if not arr:
            return Text("  (empty tree)", style="dim")

        visited: set[int] = self._states.get("visited", set())
        current: int | None = self._states.get("current")

        nodes: dict[int, int] = {}  # node_id (1-based) -> val
        for i, v in enumerate(arr):
            if v is not None:
                nodes[i + 1] = v

        if not nodes:
            return Text("  (empty tree)", style="dim")

        max_depth = max((nid.bit_length() - 1) for nid in nodes)
        total_slots = 2 ** max_depth
        slot_w = 4  # chars per slot at deepest level

        result = Text()

        for depth in range(max_depth + 1):
            first_id = 2 ** depth
            slots = 2 ** depth
            gap = total_slots // slots  # leaf-level slots per node at this depth

            row = Text()
            for pos in range(slots):
                nid = first_id + pos
                slot_pixels = gap * slot_w
                center = pos * slot_pixels + slot_pixels // 2

                if nid in nodes:
                    val = nodes[nid]
                    label = f"[{val}]"
                    pad = max(0, center - len(label) // 2 - len(row.plain))
                    row.append(" " * pad)
                    if nid == current:
                        row.append(label, style=f"bold {COLOR_CURRENT} on {BG_CURRENT}")
                    elif nid in visited:
                        row.append(label, style=f"bold {COLOR_VISITED} on {BG_VISITED}")
                    else:
                        row.append(label, style=f"bold {TEXT} on {BG_NODE}")

            result.append_text(row)
            result.append("\n")

            if depth < max_depth:
                conn = Text()
                for pos in range(slots):
                    nid = first_id + pos
                    slot_pixels = gap * slot_w
                    center = pos * slot_pixels + slot_pixels // 2

                    left_child = 2 * nid
                    right_child = 2 * nid + 1
                    quarter = slot_pixels // 4

                    if left_child in nodes:
                        slash_pos = center - quarter
                        pad = max(0, slash_pos - len(conn.plain))
                        conn.append(" " * pad)
                        conn.append("/", style=DIM)
                    if right_child in nodes:
                        backslash_pos = center + quarter
                        pad = max(0, backslash_pos - len(conn.plain))
                        conn.append(" " * pad)
                        conn.append("\\", style=DIM)

                result.append_text(conn)
                result.append("\n")

        result_list = self._states.get("result", [])
        if result_list:
            result.append("\n  result:  ", style=DIM)
            result.append(" → ".join(str(v) for v in result_list), style=f"bold {YELLOW}")
            result.append("\n")

        return result


# ---------------------------------------------------------------------------
# TreeRenderer
# ---------------------------------------------------------------------------


class TreeRenderer:

    def make_widget(self, input_data: list) -> TreeWidget:
        return TreeWidget(input_data=input_data, id="tree-widget")

    def update_widget(self, widget: TreeWidget, input_data: list, frame_states: dict) -> None:
        widget.update_tree(input_data, frame_states)

    def compute_states(self, frames: list[dict], up_to: int) -> dict:
        visited: set[int] = set()
        current: int | None = None
        result: list[int] = []

        for frame in frames[:up_to + 1]:
            ft = frame.get("type")
            if ft == "node_visit":
                if current is not None:
                    visited.add(current)
                current = frame["node_id"]
            elif ft == "append_result":
                result.append(frame["val"])

        return {"visited": visited, "current": current, "result": result}

    def filter_frames(self, frames: list[dict]) -> list[dict]:
        keep_types = {"node_visit", "append_result"}
        result = []
        seen: set[tuple] = set()

        for f in frames:
            ft = f["type"]
            if ft in keep_types:
                result.append(f)
                continue
            if ft == "line":
                key = ("line", f.get("fn", ""), f.get("dfs_depth", 0), f.get("lineno"))
                if key not in seen:
                    seen.add(key)
                    result.append(f)

        return result

    def explain_frame(self, frame: dict, step: int, total: int) -> str:
        ft = frame.get("type")
        prefix = f"  [{step + 1}/{total}]  "
        if ft == "node_visit":
            return f"{prefix}Visiting node {frame['val']} — process left subtree first (inorder)"
        if ft == "append_result":
            return f"{prefix}Appended {frame['val']} to result"
        if ft == "line":
            depth = frame.get("dfs_depth", 0)
            return f"{prefix}traverse() at recursion depth {depth}"
        return f"{prefix}—"

    def apply_frame_extras(self, screen, frame: dict) -> None:
        pass

    def legend_entries(self) -> list[tuple[str, str, str]]:
        return [
            (COLOR_CURRENT, "■", "currently visiting"),
            (COLOR_VISITED, "■", "visited"),
            (TEXT,          "■", "unvisited"),
        ]

    def variable_entries(self, frame: dict) -> list[tuple[str, str, str]]:
        ft = frame.get("type")
        if ft == "node_visit":
            return [
                ("node",  str(frame.get("val", "—")),              f"bold {COLOR_CURRENT}"),
                ("id",    str(frame.get("node_id", "—")),           TEAL),
                ("depth", str(frame.get("depth", frame.get("dfs_depth", "—"))), DIM),
            ]
        if ft == "append_result":
            return [
                ("appended", str(frame.get("val", "—")), f"bold {YELLOW}"),
            ]
        locs = frame.get("locals", {})
        return [("depth", str(frame.get("dfs_depth", "—")), DIM)]

    def parse_input(self, raw: str) -> list:
        parsed = ast.literal_eval(raw.strip())
        if not isinstance(parsed, list):
            raise ValueError("Must be a list (level-order)")
        if len(parsed) > 15:
            raise ValueError("Max 15 nodes")
        for v in parsed:
            if v is not None and not isinstance(v, int):
                raise ValueError("Values must be integers or None")
        return parsed

    def serialize_input(self, data: list) -> str:
        return str(data)
