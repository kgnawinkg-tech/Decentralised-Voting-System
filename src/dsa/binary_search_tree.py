"""
DSA Module 7: Binary Search Tree (BST)

Complexity:
- Average Time: Insert O(log N), Search O(log N), Delete O(log N)
- Worst Case Time: O(N) when tree degenerates into a linear chain (unbalanced)
- Space Complexity: O(N)

Integration:
- Indexes block indices, timestamps, and ordered transaction metadata.
"""

from typing import Any, List, Optional, Tuple


class BSTNode:
    """Node in a Binary Search Tree."""

    def __init__(self, key: Any, value: Any):
        self.key: Any = key
        self.value: Any = value
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class BinarySearchTree:
    """Binary Search Tree implementation supporting insert, search, delete, and traversals."""

    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._size: int = 0

    def insert(self, key: Any, value: Any) -> None:
        """Insert or update key-value pair."""
        self.root = self._insert_node(self.root, key, value)

    def _insert_node(self, node: Optional[BSTNode], key: Any, value: Any) -> BSTNode:
        if node is None:
            self._size += 1
            return BSTNode(key, value)
        if key == node.key:
            node.value = value
        elif key < node.key:
            node.left = self._insert_node(node.left, key, value)
        else:
            node.right = self._insert_node(node.right, key, value)
        return node

    def search(self, key: Any) -> Optional[Any]:
        """Search for a key. Returns value or None."""
        node = self.root
        while node is not None:
            if key == node.key:
                return node.value
            elif key < node.key:
                node = node.left
            else:
                node = node.right
        return None

    def contains(self, key: Any) -> bool:
        return self.search(key) is not None

    def delete(self, key: Any) -> bool:
        """Delete key from BST. Returns True if deleted, False if not found."""
        if not self.contains(key):
            return False
        self.root = self._delete_node(self.root, key)
        self._size -= 1
        return True

    def _delete_node(self, node: Optional[BSTNode], key: Any) -> Optional[BSTNode]:
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete_node(node.left, key)
        elif key > node.key:
            node.right = self._delete_node(node.right, key)
        else:
            # Case 1 & 2: 0 or 1 child
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            # Case 3: 2 children - find in-order successor (min of right subtree)
            successor = self._min_node(node.right)
            node.key = successor.key
            node.value = successor.value
            node.right = self._delete_node(node.right, successor.key)
        return node

    def _min_node(self, node: BSTNode) -> BSTNode:
        current = node
        while current.left is not None:
            current = current.left
        return current

    def in_order(self) -> List[Tuple[Any, Any]]:
        """Return (key, value) pairs in ascending order: O(N)."""
        result = []
        self._in_order_traversal(self.root, result)
        return result

    def _in_order_traversal(self, node: Optional[BSTNode], result: List[Tuple[Any, Any]]) -> None:
        if node is not None:
            self._in_order_traversal(node.left, result)
            result.append((node.key, node.value))
            self._in_order_traversal(node.right, result)

    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return self._size
