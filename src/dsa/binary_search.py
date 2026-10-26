"""
DSA Module 16: Binary Search

Complexity:
- Time: O(log N)
- Space: O(1) iterative

Integration:
- Fast logarithmic lookup in sorted block header lists, ordered audit timestamps,
  and sorted transaction indices.
"""

from typing import Any, Callable, List, Optional


def binary_search(
    arr: List[Any], target: Any, key: Optional[Callable[[Any], Any]] = None
) -> int:
    """
    Search for target in a sorted list using binary search.
    
    Parameters:
    - arr: Sorted list of items.
    - target: Value to find.
    - key: Optional extraction function (e.g., lambda x: x['index']).
    
    Returns:
    - Index of target if found, otherwise -1.
    """
    if not arr:
        return -1

    left = 0
    right = len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        val = key(arr[mid]) if key else arr[mid]

        if val == target:
            return mid
        elif val < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1


def binary_search_leftmost(
    arr: List[Any], target: Any, key: Optional[Callable[[Any], Any]] = None
) -> int:
    """
    Find index of first occurrence of target in sorted list with duplicates.
    Returns -1 if not found.
    """
    if not arr:
        return -1

    left = 0
    right = len(arr) - 1
    result = -1

    while left <= right:
        mid = (left + right) // 2
        val = key(arr[mid]) if key else arr[mid]

        if val == target:
            result = mid
            right = mid - 1  # Keep searching left
        elif val < target:
            left = mid + 1
        else:
            right = mid - 1

    return result
