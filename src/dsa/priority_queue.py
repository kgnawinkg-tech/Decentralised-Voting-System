"""
DSA Module 6: Priority Queue / Binary Heap

Complexity:
- Time: Insert O(log N), Extract-Min O(log N), Peek O(1), Heapify O(N)
- Space Complexity: O(N)

Integration:
- Prioritizes operational tasks such as synchronization jobs and peer reconnect retries.
- Strictly never allows task priority to bypass or alter voting rules.
"""

from typing import Any, List, Optional, Tuple


class PriorityQueueUnderflowError(Exception):
    """Raised when extracting or peeking from an empty priority queue."""
    pass


class PriorityQueue:
    """
    Min-Heap based Priority Queue.
    Stores tuples of (priority, item), where lower numerical priority = higher precedence.
    """

    def __init__(self):
        # Heap array storing (priority, sequence_id, item)
        self._heap: List[Tuple[float, int, Any]] = []
        self._counter: int = 0  # Tie-breaker for stable FIFO extraction on equal priorities

    def push(self, item: Any, priority: float) -> None:
        """Insert an item with a given priority: O(log N)."""
        entry = (priority, self._counter, item)
        self._counter += 1
        self._heap.append(entry)
        self._sift_up(len(self._heap) - 1)

    def pop(self) -> Any:
        """Extract the item with minimum priority value: O(log N)."""
        if self.is_empty():
            raise PriorityQueueUnderflowError("Cannot pop from an empty priority queue")
        
        # Swap root with last element
        self._swap(0, len(self._heap) - 1)
        _, _, item = self._heap.pop()
        
        if not self.is_empty():
            self._sift_down(0)
            
        return item

    def peek(self) -> Any:
        """Inspect the highest-priority item without removal: O(1)."""
        if self.is_empty():
            raise PriorityQueueUnderflowError("Cannot peek into an empty priority queue")
        return self._heap[0][2]

    def peek_priority(self) -> float:
        """Inspect the minimum priority value: O(1)."""
        if self.is_empty():
            raise PriorityQueueUnderflowError("Cannot peek into an empty priority queue")
        return self._heap[0][0]

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def size(self) -> int:
        return len(self._heap)

    def _swap(self, i: int, j: int) -> None:
        self._heap[i], self._heap[j] = self._heap[j], self._heap[i]

    def _sift_up(self, idx: int) -> None:
        parent = (idx - 1) // 2
        while idx > 0 and self._heap[idx] < self._heap[parent]:
            self._swap(idx, parent)
            idx = parent
            parent = (idx - 1) // 2

    def _sift_down(self, idx: int) -> None:
        size = len(self._heap)
        while True:
            left = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx

            if left < size and self._heap[left] < self._heap[smallest]:
                smallest = left
            if right < size and self._heap[right] < self._heap[smallest]:
                smallest = right

            if smallest != idx:
                self._swap(idx, smallest)
                idx = smallest
            else:
                break

    def to_sorted_list(self) -> List[Any]:
        """Return items sorted by priority without mutating original queue."""
        clone = PriorityQueue()
        clone._heap = list(self._heap)
        clone._counter = self._counter
        items = []
        while not clone.is_empty():
            items.append(clone.pop())
        return items

    def __len__(self) -> int:
        return len(self._heap)
