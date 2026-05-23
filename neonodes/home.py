"""
home.py — Home screen for neonodes: topic/difficulty filters + problem list.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.message import Message
from textual.screen import Screen
from textual.widget import Widget
from rich.text import Text

from neonodes.problems.registry import TOPICS, DIFFICULTIES, PROBLEMS

# ---------------------------------------------------------------------------
# Color palette
# ---------------------------------------------------------------------------

BG      = "#252836"
SURFACE = "#1E2230"
BORDER  = "#3D4566"
TEXT    = "#C0CAE4"
DIM     = "#565F89"
BLUE    = "#7AA2F7"
GREEN   = "#9ECE6A"
YELLOW  = "#E0AF68"
RED     = "#F7768E"
TEAL    = "#73DACA"
SEL_BG  = "#2D3250"

DIFF_COLORS = {
    "easy":   GREEN,
    "medium": YELLOW,
    "hard":   RED,
}


# ---------------------------------------------------------------------------
# HomeWidget
# ---------------------------------------------------------------------------


class HomeWidget(Widget):
    """Full-screen home widget with topic/difficulty filters and problem list."""

    can_focus = True

    VISIBLE_ROWS = 8  # max rows before scrolling

    class ProblemSelected(Message):
        """Emitted when the user presses Enter on an available problem."""

        def __init__(self, problem_id: str) -> None:
            super().__init__()
            self.problem_id = problem_id

    DEFAULT_CSS = f"""
    HomeWidget {{
        background: {BG};
        width: 100%;
        height: 100%;
        padding: 0;
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._topic: str = "all"
        self._difficulty: str = "all"
        self._selected: int = 0
        self._scroll_offset: int = 0

    def on_mount(self) -> None:
        self.focus()

    def _filtered(self) -> list[dict]:
        result = []
        for p in PROBLEMS:
            if self._topic != "all" and p["topic"] != self._topic:
                continue
            if self._difficulty != "all" and p["difficulty"] != self._difficulty:
                continue
            result.append(p)
        return result

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def render(self) -> Text:
        result = Text()
        width = self.size.width or 80

        # Column widths
        TW = 38   # title col inner width
        CW = 10   # topic col inner width
        DW = 10   # difficulty col inner width
        # total table width = 1 + TW + 1 + 1 + CW + 1 + 1 + DW + 1 = TW+CW+DW+7
        table_w = TW + CW + DW + 7

        # indent to center the table
        pad = max(0, (width - table_w) // 2)
        P = " " * pad

        # ── Header ──────────────────────────────────────────────────────
        result.append("\n\n")
        result.append("neonodes".center(width) + "\n", style=f"bold {BLUE}")
        result.append("algorithm visualizer".center(width) + "\n", style=DIM)
        result.append("\n")

        # ── Filters as dropdowns ────────────────────────────────────────
        topic_val = f" {self._topic} ▾ "
        diff_val  = f" {self._difficulty} ▾ "

        result.append(P + "  topic  ", style=DIM)
        result.append(f"┌{'─' * (len(topic_val))}┐", style=BORDER)
        result.append("      difficulty  ", style=DIM)
        result.append(f"┌{'─' * (len(diff_val))}┐", style=BORDER)
        result.append("\n")

        result.append(P + "         ", style=DIM)
        result.append("│", style=BORDER)
        result.append(topic_val, style=f"bold {BLUE} on {SEL_BG}")
        result.append("│", style=BORDER)
        result.append("                  ", style=DIM)
        result.append("│", style=BORDER)
        diff_color = DIFF_COLORS.get(self._difficulty, BLUE)
        result.append(diff_val, style=f"bold {diff_color} on {SEL_BG}")
        result.append("│", style=BORDER)
        result.append("\n")

        result.append(P + "         ", style=DIM)
        result.append(f"└{'─' * (len(topic_val))}┘", style=BORDER)
        result.append("                  ", style=DIM)
        result.append(f"└{'─' * (len(diff_val))}┘", style=BORDER)
        result.append("\n\n")

        # ── Table ───────────────────────────────────────────────────────
        def row_sep(left: str, mid1: str, mid2: str, right: str) -> None:
            result.append(P + left + "─" * (TW + 2) + mid1 +
                          "─" * (CW + 2) + mid2 +
                          "─" * (DW + 2) + right + "\n", style=BORDER)

        def cell(text: str, w: int, style: str) -> None:
            result.append(" " + text[:w].ljust(w) + " ", style=style)

        # Top border
        row_sep("┌", "┬", "┬", "┐")

        # Header row
        result.append(P + "│", style=BORDER)
        cell("problem", TW, f"bold {DIM}")
        result.append("│", style=BORDER)
        cell("topic", CW, f"bold {DIM}")
        result.append("│", style=BORDER)
        cell("difficulty", DW, f"bold {DIM}")
        result.append("│\n", style=BORDER)

        # Header separator
        row_sep("├", "┼", "┼", "┤")

        # Problem rows
        filtered = self._filtered()
        if not filtered:
            result.append(P + "│", style=BORDER)
            msg = " no problems match filters"
            result.append((" " + msg).ljust(TW + CW + DW + 6), style=DIM)
            result.append("│\n", style=BORDER)
        else:
            sel = max(0, min(self._selected, len(filtered) - 1))
            visible_rows = self.VISIBLE_ROWS
            scroll = self._scroll_offset
            if sel < scroll:
                scroll = sel
            if sel >= scroll + visible_rows:
                scroll = sel - visible_rows + 1
            self._scroll_offset = scroll

            visible = filtered[scroll: scroll + visible_rows]

            for idx_rel, problem in enumerate(visible):
                idx_abs = idx_rel + scroll
                is_sel  = (idx_abs == sel)
                avail   = problem.get("available", False)
                bg      = SEL_BG if is_sel else ""

                diff       = problem["difficulty"]
                diff_color = DIFF_COLORS.get(diff, TEXT)

                # title cell
                if is_sel:
                    prefix = "▶ "
                    t_style = f"bold {TEXT}"
                else:
                    prefix = "  "
                    t_style = TEXT if avail else DIM

                title_raw = prefix + problem["title"]
                if not avail:
                    title_raw += "  · · ·"

                result.append(P + "│", style=BORDER)
                val = title_raw[:TW].ljust(TW)
                s = f"{t_style} on {bg}" if bg else t_style
                result.append(" " + val + " ", style=s)

                result.append("│", style=BORDER)
                topic_s = f"{TEAL} on {bg}" if bg else TEAL
                cell(problem["topic"], CW, topic_s)

                result.append("│", style=BORDER)
                diff_s = f"{diff_color} on {bg}" if bg else diff_color
                cell(diff, DW, diff_s)

                result.append("│\n", style=BORDER)

                # row separator between rows (not after last)
                if idx_rel < len(visible) - 1:
                    row_sep("├", "┼", "┼", "┤")

        # Bottom border
        row_sep("└", "┴", "┴", "┘")
        result.append("\n")

        # ── Key hints ───────────────────────────────────────────────────
        hints = [("[↑↓]","navigate"), ("[t]","topic"), ("[d]","difficulty"),
                 ("[enter]","launch"), ("[q]","quit")]
        result.append(P)
        for key, label in hints:
            result.append(key, style=f"bold {BLUE}")
            result.append(f" {label}   ", style=DIM)
        result.append("\n")

        return result

    # ------------------------------------------------------------------
    # Key handling
    # ------------------------------------------------------------------

    def on_key(self, event) -> None:
        filtered = self._filtered()
        total = len(filtered)

        if event.key == "up":
            if total > 0:
                self._selected = max(0, self._selected - 1)
            self.refresh()

        elif event.key == "down":
            if total > 0:
                self._selected = min(total - 1, self._selected + 1)
            self.refresh()

        elif event.key == "t":
            cur_idx = TOPICS.index(self._topic)
            self._topic = TOPICS[(cur_idx + 1) % len(TOPICS)]
            self._selected = 0
            self._scroll_offset = 0
            self.refresh()

        elif event.key == "d":
            cur_idx = DIFFICULTIES.index(self._difficulty)
            self._difficulty = DIFFICULTIES[(cur_idx + 1) % len(DIFFICULTIES)]
            self._selected = 0
            self._scroll_offset = 0
            self.refresh()

        elif event.key == "enter":
            if total > 0:
                sel = max(0, min(self._selected, total - 1))
                problem = filtered[sel]
                if problem.get("available", False):
                    self.post_message(HomeWidget.ProblemSelected(problem["id"]))
                else:
                    # Coming soon — stay, just refresh (no navigation)
                    self.refresh()


# ---------------------------------------------------------------------------
# HomeScreen
# ---------------------------------------------------------------------------


class HomeScreen(Screen):
    """Home screen with problem browser."""

    CSS = f"Screen {{ background: {BG}; }}"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield HomeWidget(id="home-widget")

    def on_home_widget_problem_selected(self, event: HomeWidget.ProblemSelected) -> None:
        self.app.launch_problem(event.problem_id)

    def action_quit(self) -> None:
        self.app.exit()
