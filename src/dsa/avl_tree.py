"""
DSA Module 8: AVL Tree (Self-Balancing Binary Search Tree)

Complexity:
- Time: Insert O(log N), Search O(log N), Delete O(log N) - guaranteed worst-case!
- Space Complexity: O(N)

Integration:
- Indexes block heights and committed transactions with strict logarithmic lookup guarantees,
  preventing performance degradation from sorted or sequential block insertions.
"""

from typing import Any, List, Optional, Tuple


class AVLNode:
    """Node in an AVL Tree with height tracking."""

    def __init__(self, key: Any, value: Any):
        self.key: Any = key
        self.value: Any = value
        self.height: int = 1
        self.left: Optional["AVLNode"] = None
        self.right: Optional["AVLNode"] = None


class AVLTree:
    """
    Self-balancing BST that maintains height balance (|balance_factor| <= 1).
    Implements Left-Left (LL), Right-Right (RR), Left-Right (LR), and Right-Left (RL) rotations.
    """

    def __init__(self):
        self.root: Optional[AVLNode] = None
        self._size: int = 0

    def _get_height(self, node: Optional[AVLNode]) -> int:
        return node.height if node else 0

    def _get_balance(self, node: Optional[AVLNode]) -> int:
        if not node:
            return 0
        return self._get_height(node.left) - self._get_height(node.right)

    def _update_height(self, node: AVLNode) -> None:
        node.height = 1 + max(self._get_height(node.left), self._get_height(node.right))

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        r"""
        Right rotation (for Left-Left case):
            y             x
           / \           / \
          x   T3  ==>   T1  y
         / \               / \
        T1  T2            T2  T3
        """
        x = y.left
        assert x is not None
        t2 = x.right

        # Perform rotation
        x.right = y
        y.left = t2

        # Update heights
        self._update_height(y)
        self._update_height(x)

        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        r"""
        Left rotation (for Right-Right case):
          x                 y
         / \               / \
        T1  y     ==>     x   T3
           / \           / \
          T2  T3        T1  T2
        """
        y = x.right
        assert y is not None
        t2 = y.left

        # Perform rotation
        y.left = x
        x.right = t2

        # Update heights
        self._update_height(x)
        self._update_height(y)

        return y

    def insert(self, key: Any, value: Any) -> None:
        """Insert or update a key in the AVL tree with automatic balancing."""
        self.root = self._insert_node(self.root, key, value)

    def _insert_node(self, node: Optional[AVLNode], key: Any, value: Any) -> AVLNode:
        if not node:
            self._size += 1
            return AVLNode(key, value)

        if key == node.key:
            node.value = value
            return node
        elif key < node.key:
            node.left = self._insert_node(node.left, key, value)
        else:
            node.right = self._insert_node(node.right, key, value)

        self._update_height(node)
        balance = self._get_balance(node)

        # 4 Rotation Cases:
        # Case 1: Left-Left (LL)
        if balance > 1 and node.left and key < node.left.key:
            return self._rotate_right(node)

        # Case 2: Right-Right (RR)
        if balance < -1 and node.right and key > node.right.key:
            return self._rotate_left(node)

        # Case 3: Left-Right (LR)
        if balance > 1 and node.left and key > node.left.key:
            node.left = self._rotate_left(node.left)
            return self._rotate_right(node)

        # Case 4: Right-Left (RL)
        if balance < -1 and node.right and key < node.right.key:
            node.right = self._rotate_right(node.right)
            return self._rotate_left(node)

        return node

    def search(self, key: Any) -> Optional[Any]:
        """Search for a key in O(log N)."""
        curr = self.root
        while curr:
            if key == curr.key:
                return curr.value
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def contains(self, key: Any) -> bool:
        return self.search(key) is not None

    def delete(self, key: Any) -> bool:
        """Delete key and rebalance. Returns True if deleted."""
        if not self.contains(key):
            return False
        self.root = self._delete_node(self.root, key)
        self._size -= 1
        return True

    def _min_node(self, node: AVLNode) -> AVLNode:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def _delete_node(self, node: Optional[AVLNode], key: Any) -> Optional[AVLNode]:
        if not node:
            return None

        if key < node.key:
            node.left = self._delete_node(node.left, key)
        elif key > node.key:
            node.right = self._delete_node(node.right, key)
        else:
            if not node.left:
                return node.right
            elif not node.right:
                return node.left

            temp = self._min_node(node.right)
            node.key = temp.key
            node.value = temp.value
            node.right = self._delete_node(node.right, temp.key)

        if not node:
            return None

        self._update_height(node)
        balance = self._get_balance(node)

        # Balance after deletion
        if balance > 1:
            if self._get_balance(node.left) >= 0:
                return self._rotate_right(node)
            else:
                node.left = self._rotate_left(node.left)
                return self._rotate_right(node)

        if balance < -1:
            if self._get_balance(node.right) <= 0:
                return self._rotate_left(node)
            else:
                node.right = self._rotate_right(node.right)
                return self._rotate_left(node)

        return node

    def in_order(self) -> List[Tuple[Any, Any]]:
        """Return (key, value) pairs in ascending order."""
        res = []
        self._in_order(self.root, res)
        return res

    def _in_order(self, node: Optional[AVLNode], res: List[Tuple[Any, Any]]) -> None:
        if node:
            self._in_order(node.left, res)
            res.append((node.key, node.value))
            self._in_order(node.right, res)

    def size(self) -> int:
        return self._size

    def __len__(self) -> int:
        return self._size
