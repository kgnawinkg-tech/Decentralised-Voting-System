"""
DSA Module 24: Hash Set for Duplicate Detection

Complexity:
- Time: Add O(1) avg, Contains O(1) avg, Remove O(1) avg
- Space: O(N)

Integration:
- Fast in-memory duplicate vote rejection, token reuse detection, and transaction deduplication.
  Combined with persistent SQLite UNIQUE constraints for atomic database integrity.
"""

from typing import Any, Iterator, List
from src.dsa.hash_table import HashTable


class HashSet:
    """
    Custom Hash Set implementation backed by the custom separate-chaining HashTable.
    Provides O(1) average-time set membership and duplicate detection.
    """

    def __init__(self, initial_capacity: int = 16):
        self._table = HashTable(initial_capacity=initial_capacity)

    def add(self, item: Any) -> bool:
        """
        Add item to set.
        Returns True if item was new and added, False if item was already present (duplicate detected!).
        """
        key_str = str(item)
        if self._table.contains(key_str):
            return False  # Duplicate detected
        self._table.insert(key_str, True)
        return True

    def contains(self, item: Any) -> bool:
        """Check if item exists in set in O(1) average time."""
        return self._table.contains(str(item))

    def remove(self, item: Any) -> bool:
        """Remove item from set. Returns True if removed, False if not present."""
        return self._table.delete(str(item))

    def to_list(self) -> List[str]:
        """Return all elements in set."""
        return self._table.keys()

    def size(self) -> int:
        return len(self._table)

    def __contains__(self, item: Any) -> bool:
        return self.contains(item)

    def __len__(self) -> int:
        return len(self._table)

    def __iter__(self) -> Iterator[str]:
        return iter(self._table.keys())
