TOPICS = ["all", "grid", "tree", "graph", "array", "string", "dp"]
DIFFICULTIES = ["all", "easy", "medium", "hard"]

PROBLEMS = [
    {"id": "count_islands",     "title": "Count Islands",                 "topic": "grid",   "difficulty": "medium", "renderer": "grid",  "available": True},
    {"id": "number_of_islands", "title": "Number of Islands II",          "topic": "grid",   "difficulty": "hard",   "renderer": "grid",  "available": False},
    {"id": "bt_inorder",        "title": "Binary Tree Inorder Traversal", "topic": "tree",   "difficulty": "easy",   "renderer": "tree",  "available": False},
    {"id": "bt_level_order",    "title": "Binary Tree Level Order BFS",   "topic": "tree",   "difficulty": "medium", "renderer": "tree",  "available": False},
    {"id": "two_sum",           "title": "Two Sum",                       "topic": "array",  "difficulty": "easy",   "renderer": "array", "available": False},
    {"id": "merge_intervals",   "title": "Merge Intervals",               "topic": "array",  "difficulty": "medium", "renderer": "array", "available": False},
    {"id": "valid_parens",      "title": "Valid Parentheses",             "topic": "string", "difficulty": "easy",   "renderer": "array", "available": False},
    {"id": "dijkstra",          "title": "Dijkstra Shortest Path",        "topic": "graph",  "difficulty": "medium", "renderer": "graph", "available": False},
    {"id": "bfs_graph",         "title": "Graph BFS",                     "topic": "graph",  "difficulty": "easy",   "renderer": "graph", "available": False},
    {"id": "lcs",               "title": "Longest Common Subsequence",    "topic": "dp",     "difficulty": "medium", "renderer": "dp",    "available": False},
]

# Map renderer name → module path for dynamic loading
RENDERER_MAP = {
    "grid":  "neonodes.renderers.grid.GridRenderer",
    "tree":  "neonodes.renderers.tree.TreeRenderer",
    "array": "neonodes.renderers.tree.TreeRenderer",  # stub until array renderer exists
    "graph": "neonodes.renderers.tree.TreeRenderer",  # stub
    "dp":    "neonodes.renderers.tree.TreeRenderer",  # stub
}

# Map problem id → module path for dynamic loading
PROBLEM_MAP = {
    "count_islands": "neonodes.problems.count_islands",
    "bt_inorder":    "neonodes.problems.bt_inorder",
}
