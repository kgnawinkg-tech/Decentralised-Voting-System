"""
Leader-Quorum Consensus Protocol Module

Educational Consensus Design & Security Assumptions:
1. Leader Proposal: The designated leader (e.g., node_a or round-robin) gathers verified transactions
   from its Mempool, constructs a candidate Block, and broadcasts a signed proposal.
2. Independent Validation: Each receiving follower validates:
   - Block index == parent.index + 1
   - Block.previous_hash == parent.current_hash
   - Merkle root matches sha256 transaction tree
   - All transactions inside are valid and unspent
3. Quorum Endorsement: Each follower returning an endorsement signs an acceptance vote.
   A quorum (default: >= 2 out of 3 participating nodes) is required to commit.
4. Partition Safety: If fewer than quorum nodes are reachable, the proposal fails safely,
   transactions remain in the pending mempool, and no unvalidated block is unilaterally committed.
5. Crash-Failure Model: Assumes fail-stop node crashes and reliable network communication when nodes are online.
"""

from typing import Any, Dict, List, Optional, Tuple
import requests
from src.blockchain.block import Block
from src.blockchain.validation import validate_single_block
from src.security.digital_signatures import KeyPair, verify_signature


class ConsensusManager:
    """Manages block proposal, validation voting, and quorum commitment."""

    def __init__(
        self,
        local_node_id: str,
        keypair: KeyPair,
        quorum_size: int = 2,
        is_leader: bool = True,
    ):
        self.local_node_id: str = local_node_id
        self.keypair: KeyPair = keypair
        self.quorum_size: int = quorum_size
        self.is_leader: bool = is_leader

    def validate_proposal(
        self, block_dict: Dict[str, Any], chain_tip: Block
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Follower validates proposed block and returns (is_valid, reason, signature_if_valid).
        """
        try:
            candidate_block = Block.from_dict(block_dict)
            valid, reason = validate_single_block(candidate_block, previous_block=chain_tip)
            if not valid:
                return False, f"Follower rejection: {reason}", None

            # Endorse proposal by signing block hash
            endorsement_sig = self.keypair.sign(candidate_block.current_hash)
            return True, "Proposal endorsed", endorsement_sig
        except Exception as e:
            return False, f"Validation exception: {str(e)}", None

    def propose_and_reach_consensus(
        self,
        candidate_block: Block,
        peer_endpoints: List[str],
        timeout: float = 3.0,
    ) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        Leader broadcasts block proposal to peers and gathers votes.
        Returns (consensus_reached, status_message, list_of_endorsements).
        """
        # Leader casts its own vote
        leader_vote = {
            "node_id": self.local_node_id,
            "public_key": self.keypair.get_public_pem(),
            "signature": self.keypair.sign(candidate_block.current_hash),
        }
        endorsements = [leader_vote]

        block_data = candidate_block.to_dict()
        proposal_payload = {
            "proposer_id": self.local_node_id,
            "block": block_data,
        }

        # Broadcast proposal to active peers
        for endpoint in peer_endpoints:
            url = f"{endpoint.rstrip('/')}/api/propose_block"
            try:
                resp = requests.post(url, json=proposal_payload, timeout=timeout)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("endorsed"):
                        endorsements.append({
                            "node_id": data.get("node_id"),
                            "public_key": data.get("public_key"),
                            "signature": data.get("signature"),
                        })
                    else:
                        print(f"[CONSENSUS DEBUG] Peer {endpoint} rejected: {data.get('reason')}")
                else:
                    print(f"[CONSENSUS DEBUG] Peer {endpoint} returned status {resp.status_code}: {resp.text}")
            except Exception:
                # Node offline or unreachable
                continue

        # Check quorum threshold
        if len(endorsements) >= self.quorum_size:
            # Broadcast commit to all peers
            self._broadcast_commit(candidate_block, endorsements, peer_endpoints)
            return (
                True,
                f"Consensus achieved with {len(endorsements)}/{self.quorum_size} required votes",
                endorsements,
            )
        else:
            return (
                False,
                f"Consensus FAILED: received only {len(endorsements)}/{self.quorum_size} required votes. Block rejected.",
                endorsements,
            )

    def _broadcast_commit(
        self,
        block: Block,
        endorsements: List[Dict[str, Any]],
        peer_endpoints: List[str],
    ) -> None:
        """Broadcast commit command to all online peers."""
        commit_payload = {
            "block": block.to_dict(),
            "endorsements": endorsements,
        }
        for endpoint in peer_endpoints:
            url = f"{endpoint.rstrip('/')}/api/commit_block"
            try:
                requests.post(url, json=commit_payload, timeout=2.0)
            except Exception:
                pass
