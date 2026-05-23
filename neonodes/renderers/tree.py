"""Stub tree renderer — not yet implemented."""

from __future__ import annotations
from typing import Any


class TreeRenderer:
    def make_widget(self, input_data: Any): raise NotImplementedError
    def update_widget(self, widget, input_data, frame_states): pass
    def compute_states(self, frames, up_to): return {}
    def filter_frames(self, frames): return frames
    def explain_frame(self, frame, step, total): return ""
    def apply_frame_extras(self, screen, frame): pass
    def legend_entries(self): return []
    def variable_entries(self, frame): return []
    def parse_input(self, raw): raise NotImplementedError("tree input not yet supported")
    def serialize_input(self, data): return ""
