"""
DSA Module 12: Circular Queue (Ring Buffer)

Complexity:
- Time: Enqueue O(1), Dequeue O(1), Peek O(1)
- Space Complexity: O(K) where K is the fixed capacity

Integration:
- Buffers incoming requests and synchronization messages with strict upper memory bounds,
  preventing unbounded resource exhaustion and memory flooding.
"""

from typing import Any, List, Optional


class CircularQueueOverflowError(Exception):
    """Raised when enqueuing into a full circular queue."""
    pass


class CircularQueueUnderflowError(Exception):
    """Raised when dequeuing or peeking from an empty circular queue."""
    pass


class CircularQueue:
    """Fixed-capacity circular queue using ring buffer wraparound."""

    def __init__(self, capacity: int):
        if capacity < 1:
            raise ValueError("Capacity must be at least 1")
        self.capacity: int = capacity
        self._buffer: List[Optional[Any]] = [None] * capacity
        self._head: int = 0
        self._tail: int = 0
        self._size: int = 0

    def enqueue(self, item: Any) -> bool:
        """
        Enqueue item into circular buffer.
        Raises CircularQueueOverflowError if full.
        """
        if self.is_full():
            raise CircularQueueOverflowError(f"Circular queue of capacity {self.capacity} is full")
        self._buffer[self._tail] = item
        self._tail = (self._tail + 1) % self.capacity
        self._size += 1
        return True

    def try_enqueue(self, item: Any) -> bool:
        """Enqueue item if not full; returns False if full without raising exception."""
        if self.is_full():
            return False
        return self.enqueue(item)

    def dequeue(self) -> Any:
        """
        Dequeue oldest item from buffer.
        Raises CircularQueueUnderflowError if empty.
        """
        if self.is_empty():
            raise CircularQueueUnderflowError("Cannot dequeue from empty circular queue")
        item = self._buffer[self._head]
        self._buffer[self._head] = None  # Prevent memory retention
        self._head = (self._head + 1) % self.capacity
        self._size -= 1
        return item

    def peek(self) -> Any:
        """Return oldest item without removing it."""
        if self.is_empty():
            raise CircularQueueUnderflowError("Cannot peek into empty circular queue")
        return self._buffer[self._head]

    def is_empty(self) -> bool:
        return self._size == 0

    def is_full(self) -> bool:
        return self._size == self.capacity

    def size(self) -> int:
        return self._size

    def to_list(self) -> List[Any]:
        """Return contents in FIFO order."""
        items = []
        for i in range(self._size):
            idx = (self._head + i) % self.capacity
            items.append(self._buffer[idx])
        return items

    def __len__(self) -> int:
        return self._size
