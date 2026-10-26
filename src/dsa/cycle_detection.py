"""
DSA Module 25: Graph Cycle Detection

Complexity:
- Time: O(V + E) for directed (3-color DFS) and undirected graphs
- Space: O(V) for color/visited tracking and recursion stack

Integration:
- Detects loops in network message relay topologies and task dependency graphs.
- Strictly maintained separate from blockchain previous-hash cryptographic chain verification.
"""

from typing import Dict, List, Optional, Set, Tuple
from src.dsa.graph import Graph


def detect_cycle_directed(graph: Graph) -> Tuple[bool, Optional[List[str]]]:
    """
    Detect directed cycles using 3-color DFS algorithm:
    - 0: WHITE (unvisited)
    - 1: GRAY (currently visiting in recursion stack - back-edge implies cycle)
    - 2: BLACK (fully visited)

    Returns (has_cycle, cycle_path_if_found).
    """
    if not graph.directed:
        raise ValueError("detect_cycle_directed requires a directed graph")

    WHITE, GRAY, BLACK = 0, 1, 2
    colors: Dict[str, int] = {v: WHITE for v in graph.get_vertices()}
    parent: Dict[str, Optional[str]] = {v: None for v in graph.get_vertices()}
    cycle_nodes: Optional[List[str]] = None

    def _dfs(u: str) -> bool:
        nonlocal cycle_nodes
        colors[u] = GRAY

        for v, _ in graph.get_neighbors(u):
            if colors.get(v, WHITE) == GRAY:
                # Cycle detected! Reconstruct cycle path from u back to v
                path = [v, u]
                curr = parent.get(u)
                while curr and curr != v:
                    path.append(curr)
                    curr = parent.get(curr)
                path.reverse()
                cycle_nodes = path
                return True
            elif colors.get(v, WHITE) == WHITE:
                parent[v] = u
                if _dfs(v):
                    return True

        colors[u] = BLACK
        return False

    for vertex in graph.get_vertices():
        if colors[vertex] == WHITE:
            if _dfs(vertex):
                return True, cycle_nodes

    return False, None


def detect_cycle_undirected(graph: Graph) -> Tuple[bool, Optional[List[str]]]:
    """
    Detect cycles in undirected graph using DFS with parent tracking.
    Returns (has_cycle, cycle_path_if_found).
    """
    if graph.directed:
        raise ValueError("detect_cycle_undirected requires an undirected graph")

    visited: Set[str] = set()
    parent: Dict[str, Optional[str]] = {}
    cycle_path: Optional[List[str]] = None

    def _dfs(u: str, p: Optional[str]) -> bool:
        nonlocal cycle_path
        visited.add(u)
        parent[u] = p

        for v, _ in graph.get_neighbors(u):
            if v == p:
                continue  # Don't backtrack to immediate parent in undirected graph
            if v in visited:
                # Found cycle
                path = [v, u]
                curr = p
                while curr and curr != v:
                    path.append(curr)
                    curr = parent.get(curr)
                path.reverse()
                cycle_path = path
                return True
            if _dfs(v, u):
                return True

        return False

    for vertex in graph.get_vertices():
        if vertex not in visited:
            if _dfs(vertex, None):
                return True, cycle_path

    return False, None
