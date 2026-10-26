"""
DSA Module 3: Doubly Linked List

Complexity:
- Time: Append O(1), Prepend O(1), Delete O(1) given node reference or O(N) by value,
  Forward/Backward Traversal O(N)
- Space Complexity: O(N)

Integration:
- Used for bidirectional traversal of transaction history, audit trails, and block viewer navigation.
"""

from typing import Any, Iterator, List, Optional


class DListNode:
    """Node in a doubly linked list."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.prev: Optional["DListNode"] = None
        self.next: Optional["DListNode"] = None


class DoublyLinkedList:
    """Doubly linked list supporting forward and backward traversal."""

    def __init__(self):
        self.head: Optional[DListNode] = None
        self.tail: Optional[DListNode] = None
        self.size: int = 0

    def append(self, data: Any) -> DListNode:
        """Append node to tail: O(1)."""
        node = DListNode(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            assert self.tail is not None
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self.size += 1
        return node

    def prepend(self, data: Any) -> DListNode:
        """Prepend node to head: O(1)."""
        node = DListNode(data)
        if self.head is None:
            self.head = node
            self.tail = node
        else:
            node.next = self.head
            self.head.prev = node
            self.head = node
        self.size += 1
        return node

    def delete_node(self, node: DListNode) -> None:
        """Remove a specific node reference: O(1)."""
        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        self.size -= 1

    def delete(self, data: Any) -> bool:
        """Delete first node containing data: O(N). Returns True if found & deleted."""
        curr = self.head
        while curr is not None:
            if curr.data == data:
                self.delete_node(curr)
                return True
            curr = curr.next
        return False

    def forward_traversal(self) -> List[Any]:
        """Traverse from head to tail."""
        res = []
        curr = self.head
        while curr is not None:
            res.append(curr.data)
            curr = curr.next
        return res

    def backward_traversal(self) -> List[Any]:
        """Traverse from tail to head."""
        res = []
        curr = self.tail
        while curr is not None:
            res.append(curr.data)
            curr = curr.prev
        return res

    def __len__(self) -> int:
        return self.size
