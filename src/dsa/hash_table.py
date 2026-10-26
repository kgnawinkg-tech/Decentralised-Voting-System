"""
DSA Module 1: Custom Hash Table with Collision Handling (Separate Chaining)

Complexity:
- Average Time: Insert O(1), Search O(1), Delete O(1)
- Worst Case Time: O(N) when all keys hash to the same bucket
- Space Complexity: O(N + M) where N is number of key-value pairs, M is bucket capacity

Integration:
- Used for fast in-memory voter lookups, duplicate-authorization checks, and local caching.
"""

from typing import Any, List, Optional, Tuple


class HashNode:
    """Represents a key-value node in a separate-chaining bucket."""

    def __init__(self, key: str, value: Any):
        self.key: str = key
        self.value: Any = value
        self.next: Optional["HashNode"] = None


class HashTable:
    """
    Separate-chaining hash table with dynamic resizing.
    Maintains a load factor threshold (default 0.75) to ensure O(1) average lookup.
    """

    def __init__(self, initial_capacity: int = 16, load_factor_threshold: float = 0.75):
        if initial_capacity < 1:
            raise ValueError("Capacity must be at least 1")
        self.capacity: int = initial_capacity
        self.load_factor_threshold: float = load_factor_threshold
        self.size: int = 0
        self.buckets: List[Optional[HashNode]] = [None] * self.capacity

    def _hash(self, key: str) -> int:
        """Deterministic polynomial rolling hash for strings mapped to bucket capacity."""
        h = 0
        p = 31
        m = 10**9 + 7
        for char in str(key):
            h = (h * p + ord(char)) % m
        return h % self.capacity

    def insert(self, key: str, value: Any) -> None:
        """Insert or update a key-value pair. Resizes if load factor exceeded."""
        key_str = str(key)
        index = self._hash(key_str)
        head = self.buckets[index]

        # Check if key exists; if so, update
        current = head
        while current is not None:
            if current.key == key_str:
                current.value = value
                return
            current = current.next

        # Insert new node at head of chain
        new_node = HashNode(key_str, value)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.size += 1

        # Check load factor
        if (self.size / self.capacity) > self.load_factor_threshold:
            self._resize(self.capacity * 2)

    def search(self, key: str) -> Optional[Any]:
        """Search for a key. Returns value or None if not found."""
        key_str = str(key)
        index = self._hash(key_str)
        current = self.buckets[index]
        while current is not None:
            if current.key == key_str:
                return current.value
            current = current.next
        return None

    def contains(self, key: str) -> bool:
        """Check if key exists in hash table."""
        return self.search(key) is not None

    def delete(self, key: str) -> bool:
        """Delete a key. Returns True if deleted, False if not found."""
        key_str = str(key)
        index = self._hash(key_str)
        current = self.buckets[index]
        prev = None

        while current is not None:
            if current.key == key_str:
                if prev is None:
                    self.buckets[index] = current.next
                else:
                    prev.next = current.next
                self.size -= 1
                return True
            prev = current
            current = current.next
        return False

    def _resize(self, new_capacity: int) -> None:
        """Resize bucket array and rehash all entries."""
        old_buckets = self.buckets
        self.capacity = new_capacity
        self.buckets = [None] * self.capacity
        self.size = 0

        for head in old_buckets:
            current = head
            while current is not None:
                self.insert(current.key, current.value)
                current = current.next

    def keys(self) -> List[str]:
        """Return list of all keys."""
        res = []
        for head in self.buckets:
            curr = head
            while curr is not None:
                res.append(curr.key)
                curr = curr.next
        return res

    def items(self) -> List[Tuple[str, Any]]:
        """Return list of (key, value) pairs."""
        res = []
        for head in self.buckets:
            curr = head
            while curr is not None:
                res.append((curr.key, curr.value))
                curr = curr.next
        return res

    def __len__(self) -> int:
        return self.size
