"""
Peer Network & Topology Manager

Maintains the peer network topology using the custom Graph (Concept 10).
Analyzes connectivity using BFS (Concept 13), DFS (Concept 14), Union-Find (Concept 11),
Dijkstra shortest-latency routing (Concept 19), and Cycle Detection (Concept 25).
"""

import time
from typing import Any, Dict, List, Optional, Set, Tuple
import requests
from src.dsa.graph import Graph
from src.dsa.bfs import bfs_traversal, bfs_shortest_path
from src.dsa.dfs import dfs_traversal, dfs_connected_components
from src.dsa.union_find import UnionFind
from src.dsa.dijkstra import dijkstra_shortest_path, reconstruct_dijkstra_path
from src.dsa.cycle_detection import detect_cycle_undirected


class PeerManager:
    """Manages peer endpoints and network topology graph."""

    def __init__(self, local_node_id: str, local_endpoint: str, peer_endpoints: Optional[List[str]] = None):
        self.local_node_id: str = local_node_id
        self.local_endpoint: str = local_endpoint
        self.peer_endpoints: Set[str] = set(peer_endpoints or [])
        self.peer_status: Dict[str, Dict[str, Any]] = {}
        self.topology_graph: Graph = Graph(directed=False)
        self.latencies: Dict[Tuple[str, str], float] = {}

        # Add self to topology
        self.topology_graph.add_vertex(self.local_node_id)

    def add_peer(self, endpoint: str) -> None:
        """Add peer endpoint URL."""
        if endpoint and endpoint != self.local_endpoint:
            self.peer_endpoints.add(endpoint)

    def ping_peer(self, endpoint: str, timeout: float = 2.0) -> Tuple[bool, Optional[Dict[str, Any]], float]:
        """Ping a peer's /api/health endpoint and measure round-trip latency."""
        url = f"{endpoint.rstrip('/')}/api/health"
        start = time.time()
        try:
            resp = requests.get(url, timeout=timeout)
            latency = (time.time() - start) * 1000.0  # ms
            if resp.status_code == 200:
                data = resp.json()
                peer_id = data.get("node_id", endpoint)
                self.peer_status[endpoint] = {
                    "online": True,
                    "node_id": peer_id,
                    "latency_ms": round(latency, 2),
                    "last_seen": time.time(),
                    "block_height": data.get("block_height", 0),
                }
                # Update topology graph with measured latency weight
                self.topology_graph.add_edge(self.local_node_id, peer_id, weight=round(latency, 2))
                return True, data, latency
        except Exception:
            pass

        self.peer_status[endpoint] = {
            "online": False,
            "node_id": "unknown",
            "latency_ms": float("inf"),
            "last_seen": 0,
            "block_height": 0,
        }
        return False, None, float("inf")

    def ping_all_peers(self) -> Dict[str, Dict[str, Any]]:
        """Ping all registered peers to refresh network status."""
        for endpoint in list(self.peer_endpoints):
            self.ping_peer(endpoint)
        return self.peer_status

    def get_online_peers(self) -> List[str]:
        """Return list of endpoints of currently online peers."""
        return [ep for ep, s in self.peer_status.items() if s.get("online", False)]

    def analyze_network_connectivity(self) -> Dict[str, Any]:
        """
        Comprehensive network analysis integrating multiple DSA concepts:
        - Graph (Concept 10)
        - Union-Find (Concept 11) for partition analysis
        - BFS (Concept 13) for hop-layer reachability
        - DFS (Concept 14) for component enumeration
        - Dijkstra (Concept 19) for lowest-latency routing
        - Cycle Detection (Concept 25) for ring topology validation
        """
        vertices = self.topology_graph.get_vertices()
        uf = UnionFind(vertices)

        # Union edges into Union-Find
        for u, v, _ in self.topology_graph.get_edges():
            uf.union(u, v)

        bfs_order = bfs_traversal(self.topology_graph, self.local_node_id)
        dfs_components = dfs_connected_components(self.topology_graph)
        has_cycle, cycle_path = detect_cycle_undirected(self.topology_graph)

        # Calculate Dijkstra distances from local node
        try:
            distances, predecessors = dijkstra_shortest_path(self.topology_graph, self.local_node_id)
        except ValueError:
            distances, predecessors = {}, {}

        return {
            "local_node": self.local_node_id,
            "total_nodes": len(vertices),
            "connected_components_count": uf.count(),
            "bfs_traversal_order": bfs_order,
            "dfs_components": dfs_components,
            "topology_has_cycle": has_cycle,
            "cycle_path": cycle_path,
            "dijkstra_distances_ms": distances,
            "edges": self.topology_graph.get_edges(),
        }
