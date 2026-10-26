"""
DSA Module 4: Stack (LIFO)

Complexity:
- Time: Push O(1), Pop O(1), Peek O(1)
- Space Complexity: O(N)

Integration:
- Used for verification workflows, block back-tracing, and nested state evaluation.
- Strictly never used to erase or reverse accepted election ballots.
"""

from typing import Any, List, Optional


class StackUnderflowError(Exception):
    """Raised when attempting to pop or peek from an empty stack."""
    pass


class Stack:
    """LIFO Stack implementation."""

    def __init__(self):
        self._items: List[Any] = []

    def push(self, item: Any) -> None:
        """Push item onto stack: O(1)."""
        self._items.append(item)

    def pop(self) -> Any:
        """Pop and return top item: O(1). Raises StackUnderflowError if empty."""
        if self.is_empty():
            raise StackUnderflowError("Cannot pop from an empty stack")
        return self._items.pop()

    def peek(self) -> Any:
        """Return top item without removing it: O(1). Raises StackUnderflowError if empty."""
        if self.is_empty():
            raise StackUnderflowError("Cannot peek into an empty stack")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Return True if stack has no items."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return number of elements in stack."""
        return len(self._items)

    def to_list(self) -> List[Any]:
        """Return copy of items (bottom to top)."""
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)
