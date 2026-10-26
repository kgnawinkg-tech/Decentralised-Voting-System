"""
DSA Module 14: Depth-First Search (DFS)

Complexity:
- Time: O(V + E) where V is vertices, E is edges
- Space: O(V) for recursion stack and visited set

Integration:
- Deep traversal of network topology, finding path connectivity, and discovering connected components
  across physical or simulated peer networks.
"""

from typing import Dict, List, Set
from src.dsa.graph import Graph


def dfs_traversal(graph: Graph, start_vertex: str) -> List[str]:
    """
    Traverse graph using Depth-First Search starting from start_vertex.
    Returns list of vertices in the exact order visited.
    """
    if start_vertex not in graph.adj:
        return []

    visited: Set[str] = set()
    order: List[str] = []

    def _dfs(u: str) -> None:
        visited.add(u)
        order.append(u)
        for v, _ in graph.get_neighbors(u):
            if v not in visited:
                _dfs(v)

    _dfs(start_vertex)
    return order


def dfs_connected_components(graph: Graph) -> List[List[str]]:
    """
    Find all connected components in an undirected graph using DFS.
    Returns list of components, each containing a list of vertex IDs.
    """
    visited: Set[str] = set()
    components: List[List[str]] = []

    for vertex in graph.get_vertices():
        if vertex not in visited:
            comp: List[str] = []
            stack = [vertex]
            visited.add(vertex)

            while stack:
                u = stack.pop()
                comp.append(u)
                for v, _ in graph.get_neighbors(u):
                    if v not in visited:
                        visited.add(v)
                        stack.append(v)

            components.append(sorted(comp))

    return components
