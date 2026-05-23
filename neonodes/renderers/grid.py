"""
grid.py — Textual Widget that renders a 2D grid with per-cell color states.

Cell states:
  'visited'  — teal  (#4ECDC4)
  'current'  — coral (#FF6B6B)
  'start'    — gold  (#FFE66D)
  default    — dark panel bg, value determines land/water styling
"""

from __future__ import annotations

from rich.text import Text

from textual.widget import Widget
from textual.app import RenderResult


# Colour palette
COLOR_VISITED = "#4ECDC4"
COLOR_CURRENT = "#FF6B6B"
COLOR_START = "#FFE66D"
COLOR_LAND = "#2A9D8F"
COLOR_WATER = "#1A1A2E"
COLOR_TEXT_LAND = "#E8F4F8"
COLOR_TEXT_WATER = "#4A4A6A"
COLOR_INDEX = "#666688"


class GridWidget(Widget):
    """Renders a 2D grid with optional per-cell highlight states."""

    DEFAULT_CSS = """
    GridWidget {
        border: solid #333355;
        background: #0D0D1A;
        padding: 1 2;
        height: auto;
        min-height: 10;
    }
    """

    def __init__(
        self,
        grid: list[list[int]],
        cell_states: dict[tuple[int, int], str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._grid = grid
        self._cell_states: dict[tuple[int, int], str] = cell_states or {}

    def update_grid(
        self,
        grid: list[list[int]],
        cell_states: dict[tuple[int, int], str],
    ) -> None:
        self._grid = grid
        self._cell_states = cell_states
        self.refresh()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self) -> RenderResult:
        if not self._grid or not self._grid[0]:
            return Text("  (empty grid)", style="dim")

        rows = len(self._grid)
        cols = len(self._grid[0])

        lines: list[Text] = []

        # Column index header
        header = Text("     ", style=COLOR_INDEX)
        for c in range(cols):
            header.append(f" {c:2} ", style=COLOR_INDEX)
        lines.append(header)

        # Separator
        sep_len = 5 + cols * 4
        lines.append(Text("─" * sep_len, style="#333355"))

        for r in range(rows):
            row_text = Text()
            # Row index
            row_text.append(f" {r:2} │", style=COLOR_INDEX)

            for c in range(cols):
                val = self._grid[r][c]
                state = self._cell_states.get((r, c))
                row_text.append(" ")
                row_text.append_text(self._render_cell(val, state))
                row_text.append(" ")

            lines.append(row_text)

        result = Text("\n").join(lines)
        return result

    def _render_cell(self, val: int, state: str | None) -> Text:
        label = str(val)

        if state == "current":
            return Text(f"[{label}]", style=f"bold {COLOR_CURRENT} on #3D1A1A")
        elif state == "visited":
            return Text(f"[{label}]", style=f"bold {COLOR_VISITED} on #0A2020")
        elif state == "start":
            return Text(f"[{label}]", style=f"bold {COLOR_START} on #2A2010")
        elif val == 1:
            return Text(f" {label} ", style=f"{COLOR_TEXT_LAND} on #1A3A35")
        else:
            return Text(f" {label} ", style=f"{COLOR_TEXT_WATER} on #111122")
