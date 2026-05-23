"""
recorder.py — sys.settrace-based frame recorder for algorithm visualization.

Records execution frames by intercepting special marker function calls
(_viz_visit, _viz_mark) and line events during algorithm execution.
"""

from __future__ import annotations

import copy
import sys


_MARKER_FNS = {"_viz_visit", "_viz_mark", "_viz_count"}


class Recorder:
    """Collects execution frames from an instrumented function."""

    def __init__(self) -> None:
        self.frames: list[dict] = []
        self._dfs_depth: int = 0
        self._recording: bool = False
        self._target_fn_names: set[str] = set()

    def record(self, fn_name: str, func, *args, **kwargs) -> list[dict]:
        """Run func(*args, **kwargs) under sys.settrace, return collected frames."""
        self.frames = []
        self._dfs_depth = 0
        self._recording = False
        self._target_fn_names = {fn_name, "dfs"}

        old_trace = sys.gettrace()
        sys.settrace(self._global_trace)
        try:
            func(*args, **kwargs)
        finally:
            sys.settrace(old_trace)

        return self.frames

    # ------------------------------------------------------------------
    # Trace callbacks
    # ------------------------------------------------------------------

    def _global_trace(self, frame, event: str, arg):
        fn_name = frame.f_code.co_name

        if event == "call":
            if fn_name in _MARKER_FNS:
                # Global trace receives "call" with args already in f_locals
                self._handle_marker(fn_name, frame)
                return None  # no local trace needed for marker stubs
            if fn_name == "dfs":
                self._dfs_depth += 1
            if fn_name in self._target_fn_names:
                return self._local_trace

        return None

    def _local_trace(self, frame, event: str, arg):
        fn_name = frame.f_code.co_name

        if event == "call":
            return self._local_trace

        if event == "return":
            if fn_name == "dfs":
                self._dfs_depth = max(0, self._dfs_depth - 1)
                self.frames.append({
                    "type": "dfs_return",
                    "dfs_depth": self._dfs_depth,
                    "locals": self._safe_deepcopy(dict(frame.f_locals)),
                })
            return self._local_trace

        if event == "line":
            if fn_name in _MARKER_FNS:
                return self._local_trace
            if fn_name in self._target_fn_names:
                self._emit_line_frame(frame)
            return self._local_trace

        return self._local_trace

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _emit_line_frame(self, frame) -> None:
        try:
            locals_snap = self._safe_deepcopy(dict(frame.f_locals))
        except Exception:
            locals_snap = {}
        self.frames.append({
            "type": "line",
            "lineno": frame.f_lineno,
            "fn": frame.f_code.co_name,
            "locals": locals_snap,
            "dfs_depth": self._dfs_depth,
        })

    def _handle_marker(self, fn_name: str, frame) -> None:
        """Intercept _viz_* marker calls and emit structured events."""
        locs = dict(frame.f_locals)
        if fn_name == "_viz_visit":
            r = locs.get("r")
            c = locs.get("c")
            if r is not None and c is not None:
                self.frames.append({
                    "type": "cell_visit",
                    "r": r,
                    "c": c,
                    "color": "current",
                    "dfs_depth": self._dfs_depth,
                })
        elif fn_name == "_viz_mark":
            r = locs.get("r")
            c = locs.get("c")
            if r is not None and c is not None:
                self.frames.append({
                    "type": "cell_mark",
                    "r": r,
                    "c": c,
                    "color": "visited",
                    "dfs_depth": self._dfs_depth,
                })
        elif fn_name == "_viz_count":
            count = locs.get("count")
            if count is not None:
                self.frames.append({
                    "type": "count_update",
                    "count": count,
                    "dfs_depth": self._dfs_depth,
                })

    @staticmethod
    def _safe_deepcopy(obj: dict) -> dict:
        result = {}
        for k, v in obj.items():
            if k.startswith("_"):
                continue
            try:
                result[k] = copy.deepcopy(v)
            except Exception:
                result[k] = repr(v)
        return result
