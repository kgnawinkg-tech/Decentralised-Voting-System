"""
DSA Module 11: Disjoint Set Union (Union-Find with Path Compression and Union by Rank)

Complexity:
- Time: Nearly O(1) amortized - O(alpha(N)) per operation where alpha is the inverse Ackermann function
- Space Complexity: O(N)

Integration:
- Analyzes peer network connectivity and detects network partitions between physical/simulated nodes.
- Strictly kept separate from blockchain consensus mechanisms.
"""

from typing import Dict, List, Set


class UnionFind:
    """Disjoint Set Union (DSU) with path compression and union by rank."""

    def __init__(self, elements: List[str] = None):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}
        self.component_count: int = 0

        if elements:
            for elem in elements:
                self.add(elem)

    def add(self, x: str) -> None:
        """Add a new element as an isolated set."""
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
            self.component_count += 1

    def find(self, x: str) -> str:
        """Find root of set containing x with recursive path compression."""
        if x not in self.parent:
            self.add(x)
            return x

        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x: str, y: str) -> bool:
        """
        Merge sets containing x and y using union by rank.
        Returns True if sets were disjoint and merged, False if already in same set.
        """
        root_x = self.find(x)
        root_y = self.find(y)

        if root_x == root_y:
            return False  # Already in same set

        # Union by rank: attach smaller tree under root of larger tree
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        self.component_count -= 1
        return True

    def connected(self, x: str, y: str) -> bool:
        """Check if x and y belong to the same connected component."""
        return self.find(x) == self.find(y)

    def get_components(self) -> Dict[str, List[str]]:
        """Return mapping of component root -> list of member elements."""
        components: Dict[str, List[str]] = {}
        for elem in self.parent:
            root = self.find(elem)
            if root not in components:
                components[root] = []
            components[root].append(elem)
        return components

    def count(self) -> int:
        return self.component_count
