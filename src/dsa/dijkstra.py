"""
DSA Module 19: Dijkstra's Shortest Path Algorithm

Complexity:
- Time: O((V + E) log V) using priority queue
- Space: O(V) for distance table, visited set, and priority queue

Integration:
- Determines optimal low-latency communication paths across weighted peer networks.
- Strictly kept separate from blockchain consensus: optimal routing delivers packets,
  while consensus determines block and transaction validity.
"""

from typing import Dict, List, Optional, Tuple
from src.dsa.graph import Graph
from src.dsa.priority_queue import PriorityQueue


def dijkstra_shortest_path(
    graph: Graph, start: str, target: Optional[str] = None
) -> Tuple[Dict[str, float], Dict[str, Optional[str]]]:
    """
    Compute shortest path from start vertex to all other vertices (or specific target).
    
    Validates:
    - Rejects negative edge weights with ValueError.
    - Handles disconnected/unreachable nodes with infinity (float('inf')).

    Returns:
    - distances: Dict[vertex, minimum_cost]
    - predecessors: Dict[vertex, previous_vertex_in_path]
    """
    if start not in graph.adj:
        raise ValueError(f"Start vertex '{start}' does not exist in graph")

    # Check for negative weights
    for u in graph.adj:
        for v, w in graph.adj[u]:
            if w < 0:
                raise ValueError(f"Negative weight detected on edge ({u}, {v}, {w}). Dijkstra requires non-negative weights.")

    distances: Dict[str, float] = {v: float("inf") for v in graph.get_vertices()}
    predecessors: Dict[str, Optional[str]] = {v: None for v in graph.get_vertices()}
    distances[start] = 0.0

    pq = PriorityQueue()
    pq.push(start, 0.0)
    visited = set()

    while not pq.is_empty():
        curr_dist = pq.peek_priority()
        u = pq.pop()

        if u in visited:
            continue
        visited.add(u)

        if target is not None and u == target:
            break

        for v, weight in graph.get_neighbors(u):
            if v in visited:
                continue
            new_dist = curr_dist + weight
            if new_dist < distances.get(v, float("inf")):
                distances[v] = new_dist
                predecessors[v] = u
                pq.push(v, new_dist)

    return distances, predecessors


def reconstruct_dijkstra_path(predecessors: Dict[str, Optional[str]], start: str, target: str) -> Optional[List[str]]:
    """Reconstruct path from start to target using predecessor map."""
    if target not in predecessors:
        return None
    if predecessors[target] is None and target != start:
        return None  # Unreachable

    path = []
    curr: Optional[str] = target
    while curr is not None:
        path.append(curr)
        curr = predecessors[curr]

    path.reverse()
    return path if path and path[0] == start else None
