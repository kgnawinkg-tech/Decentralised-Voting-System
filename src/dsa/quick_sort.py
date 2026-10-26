"""
DSA Module 18: Quick Sort with Median-of-Three Pivot Selection

Complexity:
- Time:
  - Average: O(N log N)
  - Worst: O(N^2) mitigated by Median-of-Three pivot
- Space: O(log N) auxiliary recursion stack

Integration:
- Fast in-memory sorting of transaction mempools, candidate tallies, and peer latency rankings.
"""

from typing import Any, Callable, List, Optional


def quick_sort(
    arr: List[Any], key: Optional[Callable[[Any], Any]] = None, reverse: bool = False
) -> List[Any]:
    """
    Sort a list using Quick Sort with Median-of-Three pivot.
    Returns a new sorted list.
    """
    items = list(arr)
    if len(items) <= 1:
        return items

    _quick_sort_recursive(items, 0, len(items) - 1, key=key, reverse=reverse)
    return items


def _median_of_three(
    arr: List[Any], low: int, high: int, key: Optional[Callable[[Any], Any]]
) -> int:
    mid = (low + high) // 2
    a = key(arr[low]) if key else arr[low]
    b = key(arr[mid]) if key else arr[mid]
    c = key(arr[high]) if key else arr[high]

    if (a <= b <= c) or (c <= b <= a):
        return mid
    elif (b <= a <= c) or (c <= a <= b):
        return low
    else:
        return high


def _quick_sort_recursive(
    arr: List[Any],
    low: int,
    high: int,
    key: Optional[Callable[[Any], Any]],
    reverse: bool,
) -> None:
    if low < high:
        p_idx = _partition(arr, low, high, key, reverse)
        _quick_sort_recursive(arr, low, p_idx - 1, key, reverse)
        _quick_sort_recursive(arr, p_idx + 1, high, key, reverse)


def _partition(
    arr: List[Any],
    low: int,
    high: int,
    key: Optional[Callable[[Any], Any]],
    reverse: bool,
) -> int:
    # Median-of-three pivot selection
    pivot_idx = _median_of_three(arr, low, high, key)
    arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]

    pivot_val = key(arr[high]) if key else arr[high]
    i = low - 1

    for j in range(low, high):
        val_j = key(arr[j]) if key else arr[j]
        condition = (val_j >= pivot_val) if reverse else (val_j <= pivot_val)
        if condition:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1
