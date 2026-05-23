"""Binary Tree Inorder Traversal — stub, not yet available."""

from __future__ import annotations
from typing import Any

TITLE       = "Binary Tree Inorder Traversal"
CATEGORY    = "tree"
DIFFICULTY  = "easy"
RENDERER    = "tree"
DESCRIPTION = "Given the root of a binary tree, return the inorder traversal of its nodes' values."

DEFAULT_INPUT: Any = None

CODE_LINES = [
    "def inorder(root):",
    "    result = []",
    "",
    "    def traverse(node):",
    "        if not node:",
    "            return",
    "        traverse(node.left)",
    "        result.append(node.val)",
    "        traverse(node.right)",
    "",
    "    traverse(root)",
    "    return result",
]


def run(input_data: Any) -> list[dict]:
    return []
