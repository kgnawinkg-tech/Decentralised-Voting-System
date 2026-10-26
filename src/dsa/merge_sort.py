"""
DSA Module 17: Merge Sort (Divide-and-Conquer Stable Sorting)

Complexity:
- Time: O(N log N) in all cases (Best, Average, Worst)
- Space: O(N) auxiliary space
- Stability: Stable (preserves relative order of equal keys)

Integration:
- Safely sorts audit trails, block timestamps, and election receipts without reordering
  concurrent transactions with identical timestamps.
"""

from typing import Any, Callable, List, Optional


def merge_sort(
    arr: List[Any], key: Optional[Callable[[Any], Any]] = None, reverse: bool = False
) -> List[Any]:
    """
    Sort a list using Divide-and-Conquer Merge Sort.
    Returns a new sorted list (does not mutate original list).
    """
    if len(arr) <= 1:
        return list(arr)

    mid = len(arr) // 2
    left_half = merge_sort(arr[:mid], key=key, reverse=reverse)
    right_half = merge_sort(arr[mid:], key=key, reverse=reverse)

    return _merge(left_half, right_half, key=key, reverse=reverse)


def _merge(
    left: List[Any],
    right: List[Any],
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False,
) -> List[Any]:
    merged: List[Any] = []
    i = j = 0

    while i < len(left) and j < len(right):
        val_left = key(left[i]) if key else left[i]
        val_right = key(right[j]) if key else right[j]

        condition = (val_left >= val_right) if reverse else (val_left <= val_right)
        if condition:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1

    while i < len(left):
        merged.append(left[i])
        i += 1

    while j < len(right):
        merged.append(right[j])
        j += 1

    return merged
