"""
array.py — Array/string renderer shared by Two Sum and Valid Parentheses.
"""

from __future__ import annotations

import ast

from rich.text import Text
from textual.widget import Widget
from textual.app import RenderResult

from neonodes.theme import SURFACE, TEXT, DIM, BLUE, GREEN, YELLOW, TEAL, RED

COLOR_CURRENT = "#F7768E"
COLOR_COMPARE = "#7AA2F7"
COLOR_FOUND   = "#9ECE6A"
BG_CURRENT    = "#321820"
BG_COMPARE    = "#1E2A3D"
BG_FOUND      = "#253320"
BG_CELL       = "#2D3250"


class ArrayWidget(Widget):
    DEFAULT_CSS = f"""
    ArrayWidget {{
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

    def update_array(self, input_data, states: dict) -> None:
        self._input_data = input_data
        self._states = states
        self.refresh()

    def render(self) -> RenderResult:
        states = self._states
        problem = states.get("problem", "two_sum")

        if problem == "valid_parens":
            return self._render_parens()
        return self._render_two_sum()

    def _render_two_sum(self) -> RenderResult:
        data = self._input_data
        if isinstance(data, tuple):
            nums, target = data
        else:
            nums, target = data, None

        states = self._states
        i_idx = states.get("i")
        j_idx = states.get("j")
        state = states.get("state", "check")

        result = Text()
        CELL_W = 6
        SEP = "─" * CELL_W

        # Index header
        result.append("  ", style=DIM)
        for idx in range(len(nums)):
            result.append(f"  {idx:<4}", style=DIM)
        result.append("\n")

        # Top border
        result.append("  ┌", style=DIM)
        for idx in range(len(nums)):
            result.append(SEP, style=DIM)
            result.append("┬" if idx < len(nums) - 1 else "┐", style=DIM)
        result.append("\n")

        # Values row
        result.append("  │", style=DIM)
        for idx, val in enumerate(nums):
            label = f" {val:^4} "
            if state == "found" and idx in (i_idx, j_idx):
                result.append(label, style=f"bold {COLOR_FOUND} on {BG_FOUND}")
            elif idx == i_idx or idx == j_idx:
                result.append(label, style=f"bold {COLOR_COMPARE} on {BG_COMPARE}")
            else:
                result.append(label, style=f"{TEXT} on {BG_CELL}")
            result.append("│", style=DIM)
        result.append("\n")

        # Bottom border
        result.append("  └", style=DIM)
        for idx in range(len(nums)):
            result.append(SEP, style=DIM)
            result.append("┴" if idx < len(nums) - 1 else "┘", style=DIM)
        result.append("\n")

        # Pointer row
        result.append("  ", style=DIM)
        for idx in range(len(nums)):
            if idx == i_idx and idx == j_idx:
                result.append(f" {'↑ij':^4} ", style=f"bold {COLOR_COMPARE}")
            elif idx == i_idx:
                result.append(f" {'↑i':^4} ", style=f"bold {COLOR_COMPARE}")
            elif idx == j_idx:
                result.append(f" {'↑j':^4} ", style=f"bold {COLOR_COMPARE}")
            else:
                result.append(" " * CELL_W, style=DIM)
        result.append("\n")

        # Target + sum
        if i_idx is not None and j_idx is not None and i_idx < len(nums) and j_idx < len(nums):
            s = nums[i_idx] + nums[j_idx]
            result.append(f"\n  {nums[i_idx]} + {nums[j_idx]} = {s}", style=f"bold {TEAL}")
            if target is not None:
                eq = "==" if s == target else "!="
                result.append(f"  {eq}  target {target}", style=f"bold {COLOR_FOUND if s == target else DIM}")
            result.append("\n")

        return result

    def _render_parens(self) -> RenderResult:
        s = self._input_data
        if not isinstance(s, str):
            s = str(s)

        states = self._states
        current_idx: int | None = states.get("current_idx")
        stack: list[str] = states.get("stack", [])
        cell_states: dict[int, str] = states.get("cell_states", {})

        result = Text()
        CELL_W = 5

        # Index header
        result.append("  ", style=DIM)
        for idx in range(len(s)):
            result.append(f" {idx:<4}", style=DIM)
        result.append("\n")

        # Top border
        result.append("  ┌", style=DIM)
        for idx in range(len(s)):
            result.append("─" * CELL_W, style=DIM)
            result.append("┬" if idx < len(s) - 1 else "┐", style=DIM)
        result.append("\n")

        # Values
        result.append("  │", style=DIM)
        for idx, char in enumerate(s):
            label = f" {char:^3} "
            cs = cell_states.get(idx)
            if cs == "mismatch":
                result.append(label, style=f"bold {COLOR_CURRENT} on {BG_CURRENT}")
            elif cs == "matched":
                result.append(label, style=f"bold {COLOR_FOUND} on {BG_FOUND}")
            elif idx == current_idx:
                result.append(label, style=f"bold {COLOR_COMPARE} on {BG_COMPARE}")
            else:
                result.append(label, style=f"{TEXT} on {BG_CELL}")
            result.append("│", style=DIM)
        result.append("\n")

        # Bottom border
        result.append("  └", style=DIM)
        for idx in range(len(s)):
            result.append("─" * CELL_W, style=DIM)
            result.append("┴" if idx < len(s) - 1 else "┘", style=DIM)
        result.append("\n")

        # Pointer
        result.append("  ", style=DIM)
        for idx in range(len(s)):
            if idx == current_idx:
                result.append(f" {'↑':^3} ", style=f"bold {COLOR_COMPARE}")
            else:
                result.append(" " * (CELL_W + 1), style=DIM)
        result.append("\n")

        # Stack
        if stack:
            result.append(f"\n  stack:  ", style=DIM)
            result.append("[ " + "  ".join(stack) + " ]", style=f"bold {YELLOW}")
            result.append("\n")
        else:
            result.append(f"\n  stack:  [ ]", style=DIM)
            result.append("\n")

        return result


# ---------------------------------------------------------------------------
# ArrayRenderer
# ---------------------------------------------------------------------------


class ArrayRenderer:

    def make_widget(self, input_data) -> ArrayWidget:
        return ArrayWidget(input_data=input_data, id="array-widget")

    def update_widget(self, widget: ArrayWidget, input_data, frame_states: dict) -> None:
        widget.update_array(input_data, frame_states)

    def compute_states(self, frames: list[dict], up_to: int) -> dict:
        # Detect problem from frame types
        problem = "two_sum"
        for f in frames:
            if f.get("type") in ("push_char", "pop_char", "scan_char", "mismatch"):
                problem = "valid_parens"
                break

        if problem == "valid_parens":
            return self._compute_parens(frames, up_to)
        return self._compute_two_sum(frames, up_to)

    def _compute_two_sum(self, frames: list[dict], up_to: int) -> dict:
        i = j = None
        s = None
        target = None
        state = "check"
        for frame in frames[:up_to + 1]:
            ft = frame.get("type")
            if ft == "pair_check":
                i, j, s = frame.get("i"), frame.get("j"), frame.get("sum")
                target = frame.get("target")
                state = "check"
            elif ft == "pair_found":
                i, j = frame.get("i"), frame.get("j")
                target = frame.get("target")
                state = "found"
        return {"problem": "two_sum", "i": i, "j": j, "sum": s, "target": target, "state": state}

    def _compute_parens(self, frames: list[dict], up_to: int) -> dict:
        current_idx = None
        stack: list[str] = []
        cell_states: dict[int, str] = {}
        for frame in frames[:up_to + 1]:
            ft = frame.get("type")
            if ft == "scan_char":
                current_idx = frame.get("idx")
                stack = list(frame.get("stack", []))
            elif ft == "push_char":
                current_idx = frame.get("idx")
                stack = list(frame.get("stack", []))
            elif ft == "pop_char":
                idx = frame.get("idx")
                current_idx = idx
                stack = list(frame.get("stack", []))
                if idx is not None:
                    cell_states[idx] = "matched"
            elif ft == "mismatch":
                idx = frame.get("idx")
                current_idx = idx
                stack = list(frame.get("stack", []))
                if idx is not None:
                    cell_states[idx] = "mismatch"
        return {
            "problem": "valid_parens",
            "current_idx": current_idx,
            "stack": stack,
            "cell_states": cell_states,
        }

    def filter_frames(self, frames: list[dict]) -> list[dict]:
        keep_types = {"pair_check", "pair_found", "push_char", "pop_char", "scan_char", "mismatch"}
        result = []
        for f in frames:
            if f.get("type") in keep_types:
                result.append(f)
        return result

    def explain_frame(self, frame: dict, step: int, total: int) -> str:
        ft = frame.get("type")
        prefix = f"  [{step + 1}/{total}]  "
        if ft == "pair_check":
            i, j, s, t = frame.get("i"), frame.get("j"), frame.get("sum"), frame.get("target")
            return f"{prefix}Checking nums[{i}] + nums[{j}] = {s}  (target = {t})"
        if ft == "pair_found":
            i, j = frame.get("i"), frame.get("j")
            return f"{prefix}Found! indices [{i}, {j}] sum to target"
        if ft == "scan_char":
            return f"{prefix}Scanning char '{frame.get('char')}' at index {frame.get('idx')}"
        if ft == "push_char":
            return f"{prefix}Push '{frame.get('char')}' onto stack — open bracket"
        if ft == "pop_char":
            return f"{prefix}Pop — closing bracket '{frame.get('char')}' matched!"
        if ft == "mismatch":
            return f"{prefix}Mismatch at '{frame.get('char')}' — invalid!"
        return f"{prefix}—"

    def apply_frame_extras(self, screen, frame: dict) -> None:
        pass

    def legend_entries(self) -> list[tuple[str, str, str]]:
        return [
            (COLOR_CURRENT, "■", "mismatch / current error"),
            (COLOR_COMPARE, "■", "currently comparing"),
            (COLOR_FOUND,   "■", "matched / found"),
            (TEXT,          "■", "unvisited"),
        ]

    def variable_entries(self, frame: dict) -> list[tuple[str, str, str]]:
        ft = frame.get("type")
        if ft == "pair_check":
            return [
                ("i",      str(frame.get("i",      "—")), BLUE),
                ("j",      str(frame.get("j",      "—")), BLUE),
                ("sum",    str(frame.get("sum",    "—")), TEAL),
                ("target", str(frame.get("target", "—")), YELLOW),
            ]
        if ft == "pair_found":
            return [
                ("i",      str(frame.get("i",      "—")), f"bold {COLOR_FOUND}"),
                ("j",      str(frame.get("j",      "—")), f"bold {COLOR_FOUND}"),
                ("target", str(frame.get("target", "—")), YELLOW),
            ]
        if ft in ("push_char", "pop_char", "scan_char", "mismatch"):
            return [
                ("char",  str(frame.get("char",  "—")),             TEAL),
                ("idx",   str(frame.get("idx",   "—")),             BLUE),
                ("stack", str(frame.get("stack", [])),              YELLOW),
            ]
        return [("—", "—", DIM)]

    def parse_input(self, raw: str) -> object:
        raw = raw.strip()
        # valid_parens: single string of bracket chars
        bracket_chars = set("()[]{}")
        if all(c in bracket_chars for c in raw):
            return raw
        # two_sum: "[nums], target"
        try:
            bracket_end = raw.rindex("]")
            nums_part = raw[:bracket_end + 1]
            rest = raw[bracket_end + 1:].strip().lstrip(",").strip()
            nums = ast.literal_eval(nums_part)
            target = int(rest)
            if not isinstance(nums, list):
                raise ValueError("expected list")
            return (nums, target)
        except Exception:
            pass
        raise ValueError("Expected '[nums], target' or bracket string")

    def serialize_input(self, data) -> str:
        if isinstance(data, str):
            return data
        if isinstance(data, tuple):
            nums, target = data
            return f"{list(nums)}, {target}"
        return str(data)
