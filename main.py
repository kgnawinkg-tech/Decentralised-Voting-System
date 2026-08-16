import hashlib
import json
import time
from collections import deque

class Vote:
    """
    Represents an individual voting transaction.
    """
    def __init__(self, voter_id, candidate_id):
        self.voter_id = voter_id
        self.candidate_id = candidate_id
        self.timestamp = time.time()
        
    def to_dict(self):
        """Converts the vote to a dictionary for hashing."""
        return {
            "voter_id": self.voter_id,
            "candidate_id": self.candidate_id,
            "timestamp": self.timestamp
        }

class Block:
    """
    Represents a single block in the blockchain.
    Acts as a node in a Doubly Linked List.
    """
    def __init__(self, index, votes_list, previous_hash=""):
        self.index = index
        self.timestamp = time.time()
        self.votes_list = votes_list
        self.previous_hash = previous_hash
        
        
        self.prev_node = None
        self.next_node = None
        
        
        self.current_hash = self.calculate_hash()
        
    def calculate_hash(self):
        """
        Calculates the SHA-256 hash of the block's contents.
        """
        
        votes_data = [vote.to_dict() for vote in self.votes_list]
        
        
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "votes": votes_data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        
        return hashlib.sha256(block_string).hexdigest()
        
    def __repr__(self):
        return (f"Block(index={self.index}, "
                f"hash={self.current_hash[:8]}..., "
                f"prev_hash={self.previous_hash[:8]}..., "
                f"votes={len(self.votes_list)})")

class Blockchain:
    """
    Manages the chain of blocks, pending votes (mempool), and voter registry.
    """
    def __init__(self):
        
        self.head = self.create_genesis_block()
        self.tail = self.head
        
        
        self.voter_registry = {}
        
        
        self.mempool = deque()
        
        
        self.candidate_registry = {}
        
        self.chain_size = 1

    def create_genesis_block(self):
        """Creates the initial block in the chain."""
        return Block(0, [], "0")
        
    def register_candidate(self, candidate_name):
        """Registers a valid candidate."""
        if candidate_name not in self.candidate_registry:
            self.candidate_registry[candidate_name] = True
            print(f"[*] Candidate '{candidate_name}' registered successfully.")
        else:
            print(f"[!] Candidate '{candidate_name}' is already registered.")

    def register_voter(self, voter_id):
        """
        Registers a voter in the O(1) Hash Table.
        """
        if voter_id not in self.voter_registry:
            self.voter_registry[voter_id] = False
            print(f"[*] Voter '{voter_id}' registered successfully.")
        else:
            print(f"[!] Voter '{voter_id}' is already registered.")

    def cast_vote(self, voter_id, candidate_id):
        """
        Casts a vote. Checks the Hash Table to prevent double-voting,
        then pushes the vote to the FIFO Mempool Queue.
        """
        
        if voter_id not in self.voter_registry:
            print(f"[!] Vote failed: Voter '{voter_id}' is NOT registered.")
            return False
            
        
        if self.voter_registry[voter_id] == True:
            print(f"[!] Vote failed: Voter '{voter_id}' has already voted! (Double-Voting Attempt Rejected)")
            return False
            
        
        if candidate_id not in self.candidate_registry:
            print(f"[!] Vote failed: '{candidate_id}' is NOT a registered candidate.")
            return False
            
        
        new_vote = Vote(voter_id, candidate_id)
        self.mempool.append(new_vote) # Enqueue (FIFO)
        
        
        self.voter_registry[voter_id] = True
        print(f"[+] Vote cast by '{voter_id}' for '{candidate_id}' added to Mempool.")
        return True
        
    def add_block(self):
        """
        Pops all pending votes from the Mempool Queue, packages them into
        a new Block, and appends it to the Doubly Linked List.
        """
        if not self.mempool:
            print("[-] No pending votes in the Mempool to add.")
            return None
            
        
        pending_votes = []
        while self.mempool:
            pending_votes.append(self.mempool.popleft())
            
        
        new_block = Block(self.chain_size, pending_votes, self.tail.current_hash)
        
        
        self.tail.next_node = new_block
        new_block.prev_node = self.tail
        self.tail = new_block
        
        self.chain_size += 1
        print(f"[*] Block {new_block.index} added to the Blockchain containing {len(pending_votes)} votes!")
        return new_block
        
    def verify_chain(self):
        """
        Traverses the Doubly Linked List to verify that each block's
        `previous_hash` perfectly matches the preceding block's hash.
        """
        current = self.head.next_node 
        
        is_valid = True
        while current:
            
            if current.current_hash != current.calculate_hash():
                print(f"[!] Block {current.index} data has been tampered with!")
                is_valid = False
                
            
            if current.previous_hash != current.prev_node.current_hash:
                print(f"[!] Chain broken! Block {current.index}'s prev_hash doesn't match Block {current.prev_node.index}'s actual hash!")
                is_valid = False
                
            
            current = current.next_node
            
        if is_valid:
            print("[*] Blockchain integrity verified. All blocks and links are valid.")
        else:
            print("[!] Blockchain integrity check FAILED.")
            
        return is_valid

if __name__ == "__main__":
    voting_chain = Blockchain()
    
   
    voting_chain.register_candidate("Maddy")
    voting_chain.register_candidate("VK")
    
    
    print("\n--- Pre-registering Voters ---")
    voting_chain.register_voter("Nawin")
    voting_chain.register_voter("AK")
    voting_chain.register_voter("Nakul")

    while True:
        print("\n--- Decentralized Voting System ---")
        print("1. Cast Vote")
        print("2. Mine Block (Process Mempool)")
        print("3. View Blockchain & Verify")
        print("4. Exit")
        
        choice = input("Select an option: ")
        
        if choice == '1':
            voter_id = input("Enter your Voter ID: ")
            print("Available Candidates:", list(voting_chain.candidate_registry.keys()))
            candidate_id = input("Enter Candidate Name: ")
            voting_chain.cast_vote(voter_id, candidate_id)
        elif choice == '2':
            voting_chain.add_block()
        elif choice == '3':
            current_block = voting_chain.head
            while current_block:
                print(f" -> {current_block}")
                current_block = current_block.next_node
            print("\nVerifying Chain:")
            voting_chain.verify_chain()
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")
