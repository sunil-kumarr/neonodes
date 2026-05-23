"""
main.py — entry point for neonodes.

Usage:
    neonodes
    python -m neonodes
"""

from __future__ import annotations


def main() -> None:
    """Launch the neonodes TUI application."""
    from neonodes.problems import count_islands
    from neonodes.app import NeonodesApp

    app = NeonodesApp(problem_module=count_islands)
    app.run()


if __name__ == "__main__":
    main()
