"""
DSA Module 20: Topological Sort (Kahn's Algorithm with In-Degrees)

Complexity:
- Time: O(V + E) where V is tasks/nodes, E is dependency constraints
- Space: O(V) for in-degree map and FIFO queue

Integration:
- Orders dependent processing stages:
  1. Voter Credential Authentication
  2. Eligibility Check & Blinded Authorization Token Issuance
  3. Ballot Signature & Submission
  4. Shard Routing via Consistent Hashing Ring
  5. Transaction Validation & Mempool Enqueuing
  6. Block Proposal & Merkle Tree Assembly
  7. Quorum Consensus Verification & Chain Commit
  8. Ballot Receipt Generation & Local Audit Log Update
- Detects cyclical dependency deadlocks and rejects invalid processing pipelines.
"""

from collections import deque
from typing import Dict, List, Set
from src.dsa.graph import Graph


class CycleDependencyError(ValueError):
    """Raised when a cyclical dependency prevents topological ordering."""
    pass


def topological_sort(graph: Graph) -> List[str]:
    """
    Compute topological ordering of a directed acyclic graph (DAG) using Kahn's algorithm.
    Raises CycleDependencyError if the graph contains a directed cycle.
    """
    if not graph.directed:
        raise ValueError("Topological sort is only defined for directed graphs")

    # Compute in-degrees of all vertices
    in_degree: Dict[str, int] = {v: 0 for v in graph.get_vertices()}
    for u in graph.adj:
        for v, _ in graph.adj[u]:
            in_degree[v] = in_degree.get(v, 0) + 1

    # Queue all vertices with in-degree 0
    queue = deque([v for v, deg in in_degree.items() if deg == 0])
    result: List[str] = []

    while queue:
        u = queue.popleft()
        result.append(u)

        for v, _ in graph.get_neighbors(u):
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    if len(result) != graph.vertex_count():
        remaining = [v for v, deg in in_degree.items() if deg > 0]
        raise CycleDependencyError(f"Graph contains a directed cycle involving vertices: {remaining}")

    return result
