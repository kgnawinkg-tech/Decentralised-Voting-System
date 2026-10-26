"""
DSA Module 13: Breadth-First Search (BFS)

Complexity:
- Time: O(V + E) where V is vertices, E is edges
- Space: O(V) for visited set and FIFO queue

Integration:
- Explores peer network in layers of increasing hop-distance.
- Finds shortest unweighted path between nodes and discovers reachable peer subsets.
"""

from collections import deque
from typing import Dict, List, Optional
from src.dsa.graph import Graph


def bfs_traversal(graph: Graph, start_vertex: str) -> List[str]:
    """
    Traverse graph using Breadth-First Search starting from start_vertex.
    Returns list of vertices in the exact order visited.
    """
    if start_vertex not in graph.adj:
        return []

    visited = {start_vertex}
    queue = deque([start_vertex])
    traversal_order = []

    while queue:
        u = queue.popleft()
        traversal_order.append(u)

        for v, _ in graph.get_neighbors(u):
            if v not in visited:
                visited.add(v)
                queue.append(v)

    return traversal_order


def bfs_shortest_path(graph: Graph, start: str, target: str) -> Optional[List[str]]:
    """
    Find shortest unweighted hop path from start to target using BFS.
    Returns list of vertices representing the path, or None if unreachable.
    """
    if start not in graph.adj or target not in graph.adj:
        return None

    if start == target:
        return [start]

    visited = {start}
    queue = deque([start])
    parent: Dict[str, Optional[str]] = {start: None}

    while queue:
        u = queue.popleft()
        if u == target:
            # Reconstruct path
            path = []
            curr = target
            while curr is not None:
                path.append(curr)
                curr = parent[curr]
            return list(reversed(path))

        for v, _ in graph.get_neighbors(u):
            if v not in visited:
                visited.add(v)
                parent[v] = u
                queue.append(v)

    return None
