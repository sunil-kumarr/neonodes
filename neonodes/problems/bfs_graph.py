"""Graph BFS — breadth-first search with visualization."""

from __future__ import annotations

from neonodes.recorder import Recorder

TITLE      = "Graph BFS"
CATEGORY   = "graph"
DIFFICULTY = "easy"
RENDERER   = "graph"
DESCRIPTION = (
    "Given an undirected graph as an adjacency list and a start node, "
    "return the BFS traversal order."
)

DEFAULT_INPUT = ({0: [1, 2], 1: [0, 3], 2: [0], 3: [1]}, 0)

CODE_LINES = [
    "def bfs(graph, start):",
    "    visited = set()",
    "    queue = [start]",
    "    visited.add(start)",
    "    order = []",
    "    while queue:",
    "        node = queue.pop(0)",
    "        order.append(node)",
    "        for neighbor in graph[node]:",
    "            if neighbor not in visited:",
    "                visited.add(neighbor)",
    "                queue.append(neighbor)",
    "    return order",
]


def _viz_visit(node: int) -> None:  # noqa: ARG001
    pass


def _viz_enqueue(node: int) -> None:  # noqa: ARG001
    pass


def _viz_dequeue(node: int) -> None:  # noqa: ARG001
    pass


def _bfs_instrumented(graph: dict, start: int) -> list[int]:
    visited: set[int] = set()
    queue: list[int] = [start]
    visited.add(start)
    order: list[int] = []
    _viz_enqueue(start)
    while queue:
        node = queue.pop(0)
        _viz_dequeue(node)
        order.append(node)
        _viz_visit(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                _viz_enqueue(neighbor)
    return order


def run(input_data: tuple) -> list[dict]:
    graph, start = input_data
    queue_snapshot: list[int] = []
    visited_snapshot: set[int] = set()

    def handle_visit(locs: dict, depth: int) -> dict | None:
        node = locs.get("node")
        visited_snapshot.add(node)
        return {
            "type": "node_visit",
            "node": node,
            "queue": list(queue_snapshot),
            "visited": set(visited_snapshot),
        }

    def handle_enqueue(locs: dict, depth: int) -> dict | None:
        node = locs.get("node")
        queue_snapshot.append(node)
        return {
            "type": "enqueue",
            "node": node,
            "queue": list(queue_snapshot),
            "visited": set(visited_snapshot),
        }

    def handle_dequeue(locs: dict, depth: int) -> dict | None:
        node = locs.get("node")
        if node in queue_snapshot:
            queue_snapshot.remove(node)
        return {
            "type": "dequeue",
            "node": node,
            "queue": list(queue_snapshot),
            "visited": set(visited_snapshot),
        }

    recorder = Recorder()
    return recorder.record(
        "_bfs_instrumented",
        _bfs_instrumented,
        graph,
        start,
        marker_fns={"_viz_visit", "_viz_enqueue", "_viz_dequeue"},
        nested_fns=set(),
        marker_handlers={
            "_viz_visit":   handle_visit,
            "_viz_enqueue": handle_enqueue,
            "_viz_dequeue": handle_dequeue,
        },
    )
