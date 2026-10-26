"""
DSA Module 10: Graph Using Adjacency Lists

Complexity:
- Space Complexity: O(V + E) where V is vertices and E is edges
- Time Complexity:
  - Add Vertex: O(1)
  - Add Edge: O(1)
  - Remove Edge: O(degree(V))
  - Get Neighbors: O(1)

Integration:
- Represents peer-to-peer network topology, physical/virtual computer connections,
  and transaction dependency graphs.
"""

from typing import Dict, List, Optional, Set, Tuple


class Graph:
    """Adjacency list representation of directed and undirected weighted graphs."""

    def __init__(self, directed: bool = False):
        self.directed: bool = directed
        # Maps vertex -> list of (neighbor, weight)
        self.adj: Dict[str, List[Tuple[str, float]]] = {}

    def add_vertex(self, vertex: str) -> None:
        """Add vertex to graph if not present."""
        if vertex not in self.adj:
            self.adj[vertex] = []

    def add_edge(self, u: str, v: str, weight: float = 1.0) -> None:
        """Add directed or undirected edge (u, v) with optional weight."""
        self.add_vertex(u)
        self.add_vertex(v)

        # Check if edge already exists; update weight if so
        for i, (neighbor, _) in enumerate(self.adj[u]):
            if neighbor == v:
                self.adj[u][i] = (v, weight)
                if not self.directed:
                    for j, (rev_neighbor, _) in enumerate(self.adj[v]):
                        if rev_neighbor == u:
                            self.adj[v][j] = (u, weight)
                return

        self.adj[u].append((v, weight))
        if not self.directed and u != v:
            self.adj[v].append((u, weight))

    def remove_edge(self, u: str, v: str) -> bool:
        """Remove edge (u, v). Returns True if edge existed and was removed."""
        removed = False
        if u in self.adj:
            original_len = len(self.adj[u])
            self.adj[u] = [edge for edge in self.adj[u] if edge[0] != v]
            if len(self.adj[u]) < original_len:
                removed = True

        if not self.directed and v in self.adj:
            self.adj[v] = [edge for edge in self.adj[v] if edge[0] != u]

        return removed

    def get_neighbors(self, vertex: str) -> List[Tuple[str, float]]:
        """Return list of (neighbor, weight) tuples for a vertex."""
        return self.adj.get(vertex, [])

    def get_vertices(self) -> List[str]:
        """Return sorted list of all vertices."""
        return sorted(self.adj.keys())

    def get_edges(self) -> List[Tuple[str, str, float]]:
        """Return list of all edges as (u, v, weight)."""
        edges = []
        seen = set()
        for u, neighbors in self.adj.items():
            for v, w in neighbors:
                if not self.directed:
                    edge_id = tuple(sorted([u, v]))
                    if edge_id in seen:
                        continue
                    seen.add(edge_id)
                edges.append((u, v, w))
        return edges

    def vertex_count(self) -> int:
        return len(self.adj)

    def edge_count(self) -> int:
        count = sum(len(neighbors) for neighbors in self.adj.values())
        return count if self.directed else count // 2
