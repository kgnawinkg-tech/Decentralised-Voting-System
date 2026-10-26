"""
DSA Module 9: Trie (Prefix Tree)

Complexity:
- Time: Insert O(L), Exact Search O(L), Prefix Search O(L + K) where L is string length,
  K is total characters of matching descendants.
- Space Complexity: O(ALPHABET_SIZE * L * N)

Integration:
- Indexes candidate names, party affiliations, and non-sensitive voter registration identifiers
  for instant autocomplete and prefix search in the dashboard.
"""

from typing import Any, Dict, List, Optional, Tuple


class TrieNode:
    """Node in a Trie."""

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end_of_word: bool = False
        self.data: Any = None


class Trie:
    """Trie (Prefix Tree) supporting insertion, exact search, prefix matching, and autocompletion."""

    def __init__(self):
        self.root: TrieNode = TrieNode()
        self._count: int = 0

    def insert(self, word: str, data: Any = None) -> None:
        """Insert a word and optional associated payload into the trie."""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        if not node.is_end_of_word:
            self._count += 1
            node.is_end_of_word = True
        node.data = data

    def search_exact(self, word: str) -> Optional[Any]:
        """Search for exact word match. Returns data or None."""
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        if node.is_end_of_word:
            return node.data if node.data is not None else True
        return None

    def starts_with(self, prefix: str) -> bool:
        """Check if any word in the trie starts with prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return False
            node = node.children[char]
        return True

    def get_words_with_prefix(self, prefix: str) -> List[Tuple[str, Any]]:
        """Return all (word, data) pairs starting with given prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        results: List[Tuple[str, Any]] = []
        self._collect_words(node, list(prefix), results)
        return results

    def _collect_words(self, node: TrieNode, current_prefix: List[str], results: List[Tuple[str, Any]]) -> None:
        if node.is_end_of_word:
            results.append(("".join(current_prefix), node.data))
        for char, child_node in sorted(node.children.items()):
            current_prefix.append(char)
            self._collect_words(child_node, current_prefix, results)
            current_prefix.pop()

    def size(self) -> int:
        return self._count

    def __len__(self) -> int:
        return self._count
