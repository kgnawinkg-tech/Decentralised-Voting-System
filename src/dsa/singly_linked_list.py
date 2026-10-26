"""
DSA Module 2: Singly Linked List

Complexity:
- Time: Append O(1) with tail pointer or O(N), Prepend O(1), Search O(N), Delete O(N)
- Space Complexity: O(N)

Integration:
- Demonstrates sequential block linkage. Unlike cryptographic hash-links where block N contains
  hash(block N-1), linked list pointers reside purely in memory addresses.
"""

from typing import Any, Iterator, List, Optional


class SListNode:
    """Node in a singly linked list."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional["SListNode"] = None


class SinglyLinkedList:
    """Singly linked list with head and tail tracking."""

    def __init__(self):
        self.head: Optional[SListNode] = None
        self.tail: Optional[SListNode] = None
        self.size: int = 0

    def append(self, data: Any) -> SListNode:
        """Append node to the end of the list: O(1)."""
        node = SListNode(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            assert self.tail is not None
            self.tail.next = node
            self.tail = node
        self.size += 1
        return node

    def prepend(self, data: Any) -> SListNode:
        """Prepend node to the head of the list: O(1)."""
        node = SListNode(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head = node
        self.size += 1
        return node

    def delete(self, data: Any) -> bool:
        """Delete first node matching data: O(N). Returns True if deleted."""
        current = self.head
        prev = None
        while current is not None:
            if current.data == data:
                if prev is None:
                    self.head = current.next
                    if self.head is None:
                        self.tail = None
                else:
                    prev.next = current.next
                    if current == self.tail:
                        self.tail = prev
                self.size -= 1
                return True
            prev = current
            current = current.next
        return False

    def find(self, data: Any) -> Optional[SListNode]:
        """Search for node with data: O(N)."""
        curr = self.head
        while curr is not None:
            if curr.data == data:
                return curr
            curr = curr.next
        return None

    def to_list(self) -> List[Any]:
        """Convert list to Python array."""
        res = []
        curr = self.head
        while curr is not None:
            res.append(curr.data)
            curr = curr.next
        return res

    def __iter__(self) -> Iterator[Any]:
        curr = self.head
        while curr is not None:
            yield curr.data
            curr = curr.next

    def __len__(self) -> int:
        return self.size
