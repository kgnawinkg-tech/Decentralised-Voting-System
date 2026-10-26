"""
Election Tally & Audit Module

Calculates verifiable election results directly from immutable blockchain blocks.
Cross-references database records, Merkle roots, and duplicate rejection metrics.
"""

from typing import Any, Dict, List, Tuple
from src.blockchain.chain import Blockchain
from src.storage.database import Database
from src.voting.election import Election


class ElectionTally:
    """Tally calculator and integrity auditor."""

    def __init__(self, election: Election, blockchain: Blockchain, db: Database):
        self.election = election
        self.blockchain = blockchain
        self.db = db

    def calculate_results(self) -> Dict[str, Any]:
        """
        Calculate election results from committed blockchain blocks.
        """
        candidate_counts = {cid: 0 for cid in self.election.candidates}
        total_valid_ballots = 0
        seen_tokens = set()
        duplicate_attempts = 0

        # Traverse blockchain blocks
        for block in self.blockchain.blocks:
            for tx in block.transactions:
                token_hash = tx.get("token_hash")
                cid = tx.get("candidate_id")

                if token_hash in seen_tokens:
                    duplicate_attempts += 1
                    continue
                seen_tokens.add(token_hash)

                if cid in candidate_counts:
                    candidate_counts[cid] += 1
                    total_valid_ballots += 1

        # Format candidate results with details
        candidate_results = []
        for cid, cand_data in self.election.candidates.items():
            count = candidate_counts.get(cid, 0)
            pct = (count / total_valid_ballots * 100.0) if total_valid_ballots > 0 else 0.0
            candidate_results.append({
                "candidate_id": cid,
                "name": cand_data["name"],
                "party": cand_data.get("party", ""),
                "votes": count,
                "percentage": round(pct, 2),
            })

        # Sort candidate results by votes descending
        from src.dsa.merge_sort import merge_sort
        candidate_results = merge_sort(candidate_results, key=lambda c: c["votes"], reverse=True)

        # Audit verification
        is_chain_valid, chain_msg = self.blockchain.verify_integrity()

        return {
            "election_id": self.election.election_id,
            "title": self.election.title,
            "status": self.election.status.value,
            "total_accepted_ballots": total_valid_ballots,
            "total_ballots": total_valid_ballots,
            "candidate_tallies": candidate_counts,
            "candidate_results": candidate_results,
            "duplicate_attempts_rejected": duplicate_attempts,
            "blockchain_height": len(self.blockchain.blocks),
            "chain_integrity_verified": is_chain_valid,
            "integrity_message": chain_msg,
        }
