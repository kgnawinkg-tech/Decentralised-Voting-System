"""
Election Lifecycle & Tally Tests
"""

import os
import tempfile
import pytest
from src.blockchain.chain import Blockchain
from src.storage.database import Database
from src.voting.election import Election, ElectionStatus
from src.voting.tally import ElectionTally


def test_election_status_transitions():
    elec = Election("el_1", "Test Election")
    assert elec.is_open() is True
    elec.close_election()
    assert elec.is_open() is False
    assert elec.status == ElectionStatus.CLOSED
    elec.open_election()
    assert elec.is_open() is True


def test_election_tally_calculation():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(os.path.join(tmpdir, "tally_test.db"))
        elec = Election("el_tally", "Tally Election", candidates=[
            {"id": "cand_1", "name": "Alice Johnson", "party": "Party A"},
            {"id": "cand_2", "name": "Bob Martinez", "party": "Party B"},
        ])
        chain = Blockchain("node_a")

        # Mine block 1 with 2 votes for cand_1 and 1 vote for cand_2
        txs = [
            {"transaction_id": "tx1", "candidate_id": "cand_1", "token_hash": "th_1"},
            {"transaction_id": "tx2", "candidate_id": "cand_1", "token_hash": "th_2"},
            {"transaction_id": "tx3", "candidate_id": "cand_2", "token_hash": "th_3"},
        ]
        chain.add_block(txs)

        tally_calculator = ElectionTally(elec, chain, db)
        res = tally_calculator.calculate_results()

        assert res["total_accepted_ballots"] == 3
        cand_map = {c["candidate_id"]: c["votes"] for c in res["candidate_results"]}
        assert cand_map["cand_1"] == 2
        assert cand_map["cand_2"] == 1
        assert res["chain_integrity_verified"] is True
