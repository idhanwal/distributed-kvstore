import hashlib
import bisect

# Implements consistent hashing

class HashRing:
    def __init__(self, nodes, vnodes=100):
        self.ring = {}
        self.sorted_keys = []

        for node in nodes:
            for i in range(vnodes):
                key = self._hash(f"{node}:{i}")
                self.ring[key] = node
                self.sorted_keys.append(key)

        self.sorted_keys.sort()

    def _hash(self, key):
        return int(hashlib.sha1(key.encode()).hexdigest(), 16)

    def get_replicas(self, key, n):
        h = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, h)

        replicas = []
        for i in range(n):
            node_key = self.sorted_keys[(idx + i) % len(self.sorted_keys)]
            replicas.append(self.ring[node_key])
        return replicas