"""
DSA Module 5: Queue (FIFO)

Complexity:
- Time: Enqueue O(1), Dequeue O(1) amortized, Peek O(1)
- Space Complexity: O(N)

Integration:
- Used as the Mempool to order pending voting transactions strictly in first-in, first-out order.
"""

from typing import Any, List, Optional


class QueueUnderflowError(Exception):
    """Raised when attempting to dequeue or peek from an empty queue."""
    pass


class Queue:
    """FIFO Queue using two stacks for O(1) amortized operations."""

    def __init__(self):
        self._in_stack: List[Any] = []
        self._out_stack: List[Any] = []

    def enqueue(self, item: Any) -> None:
        """Enqueue item at the back: O(1)."""
        self._in_stack.append(item)

    def _shift(self) -> None:
        if not self._out_stack:
            while self._in_stack:
                self._out_stack.append(self._in_stack.pop())

    def dequeue(self) -> Any:
        """Dequeue item from the front: O(1) amortized."""
        self._shift()
        if not self._out_stack:
            raise QueueUnderflowError("Cannot dequeue from an empty queue")
        return self._out_stack.pop()

    def peek(self) -> Any:
        """Peek at front item: O(1) amortized."""
        self._shift()
        if not self._out_stack:
            raise QueueUnderflowError("Cannot peek into an empty queue")
        return self._out_stack[-1]

    def is_empty(self) -> bool:
        return len(self._in_stack) == 0 and len(self._out_stack) == 0

    def size(self) -> int:
        return len(self._in_stack) + len(self._out_stack)

    def to_list(self) -> List[Any]:
        """Return items in FIFO order without consuming the queue."""
        return list(reversed(self._out_stack)) + list(self._in_stack)

    def __len__(self) -> int:
        return self.size()
