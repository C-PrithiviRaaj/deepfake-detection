import hashlib
import json
import time

class Block:
    def __init__(self, index, previous_hash, timestamp, data, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.hash = hash

class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # Create the first block (Genesis Block)
        genesis_block = self.calculate_block(0, "0", time.time(), "Genesis Block")
        self.chain.append(genesis_block)

    def calculate_hash(self, index, previous_hash, timestamp, data):
        value = str(index) + str(previous_hash) + str(timestamp) + json.dumps(data)
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def calculate_block(self, index, previous_hash, timestamp, data):
        hash_val = self.calculate_hash(index, previous_hash, timestamp, data)
        return Block(index, previous_hash, timestamp, data, hash_val)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        previous_block = self.get_latest_block()
        new_index = previous_block.index + 1
        new_timestamp = time.time()
        new_block = self.calculate_block(new_index, previous_block.hash, new_timestamp, data)
        self.chain.append(new_block)
        return new_block

# Initialize a global blockchain instance
deepfake_blockchain = Blockchain()
