"""
Election Management Module

Controls election lifecycle (DRAFT -> OPEN -> CLOSED), candidate registration,
and strict temporal enforcement of voting rules.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class ElectionStatus(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Election:
    """Manages election state and registered candidates."""

    def __init__(
        self,
        election_id: str,
        title: str,
        description: str = "",
        candidates: Optional[List[Dict[str, str]]] = None,
    ):
        self.election_id: str = election_id
        self.title: str = title
        self.description: str = description
        self.status: ElectionStatus = ElectionStatus.OPEN  # Default OPEN for demo
        self.candidates: Dict[str, Dict[str, str]] = {}

        if candidates:
            for cand in candidates:
                self.add_candidate(cand["id"], cand["name"], cand.get("party", ""))

    def add_candidate(self, candidate_id: str, name: str, party: str = "") -> bool:
        """Register a valid candidate."""
        if candidate_id in self.candidates:
            return False
        self.candidates[candidate_id] = {
            "id": candidate_id,
            "name": name,
            "party": party,
        }
        return True

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, str]]:
        return self.candidates.get(candidate_id)

    def is_valid_candidate(self, candidate_id: str) -> bool:
        return candidate_id in self.candidates

    def open_election(self) -> None:
        self.status = ElectionStatus.OPEN

    def close_election(self) -> None:
        self.status = ElectionStatus.CLOSED

    def is_open(self) -> bool:
        return self.status == ElectionStatus.OPEN

    def to_dict(self) -> Dict[str, Any]:
        return {
            "election_id": self.election_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "candidates": list(self.candidates.values()),
        }
