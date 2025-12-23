# Cluster wide configuration like zookeeper


#List of all the nodes in the cluster, Any node can talk to any other node via REST
NODES = [
    "http://node1:8000",
    "http://node2:8000",
    "http://node3:8000",
    "http://node4:8000",
    "http://node5:8000",
]

REPLICATION_FACTOR = 3
WRITE_QUORUM = 2
READ_QUORUM = 2
NODE_ID = "node1"