# Distributed Key-Value Store

A fault-tolerant, distributed key-value store implementation inspired by Amazon's Dynamo. This project demonstrates core concepts of distributed systems including consistent hashing, quorum-based replication, and eventual consistency.

## 📋 Overview

The Distributed KV Store is a educational project that implements a scalable, distributed storage system with the following capabilities:

- **Consistent Hashing**: Efficient key distribution across cluster nodes using a hash ring
- **Quorum-Based Replication**: Read and write quorum protocols for data consistency
- **Fault Tolerance**: Automatic replica selection and failover
- **Write-Ahead Logging (WAL)**: Crash recovery and durability guarantees
- **Eventual Consistency**: Multi-version data with timestamp-based conflict resolution
- **HTTP-Based Communication**: RESTful APIs for inter-node communication
- **Docker Support**: Easy deployment and scaling with Docker Compose

## 🛠️ Technology Stack

- **Language**: Python 3.11
- **Web Framework**: FastAPI with Uvicorn
- **Async Runtime**: AsyncIO for concurrent operations
- **HTTP Client**: HTTPX for async HTTP communication
- **Containerization**: Docker & Docker Compose
- **Deployment**: 3-node cluster configuration

## 📁 Project Structure

```
distributed-kvstore/
├── distributed-kv/
│   ├── app/
│   │   ├── main.py               # FastAPI application & REST endpoints
│   │   ├── config.py             # Cluster-wide configuration
│   │   ├── ring.py               # Consistent hashing implementation
│   │   ├── store.py              # Local storage engine with WAL
│   │   └── coordinator.py        # Quorum protocol coordinator
│   ├── data/                     # Persistent storage for each node
│   │   ├── node1/
│   │   ├── node2/
│   │   └── node3/
│   ├── Dockerfile                # Container image definition
│   ├── docker-compose.yml        # Multi-node cluster orchestration
│   └── requirements.txt          # Python dependencies
└── LICENSE                       # GPL v3.0 License
```

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                     Client Applications                      │
└────────────┬────────────────────────────────────┬────────────┘
             │                                    │
        HTTP │ REST API                      HTTP │ REST API
             │                                    │
    ┌────────▼──────────┐            ┌───────────▼────────┐
    │  Coordinator Node │            │  Any Other Node    │
    │  (Hash Ring)      │            │  (Hash Ring)       │
    │  Quorum Protocol  │            │  Quorum Protocol   │
    └────────┬──────────┘            └────────┬───────────┘
             │                                │
        ┌────▼────────────────────────────────▼────┐
        │    Consistent Hash Ring                  │
        │    (Maps keys to replica nodes)          │
        └──────────────────────────────────────────┘
             │                │                │
    ┌────────▼─────┐  ┌──────▼──────┐  ┌────▼──────────┐
    │    Node 1    │  │    Node 2   │  │    Node 3    │
    │    Port 8001 │  │   Port 8002 │  │   Port 8003  │
    │              │  │             │  │              │
    │ KV Store:    │  │ KV Store:   │  │ KV Store:   │
    │  - Memory    │  │  - Memory   │  │  - Memory   │
    │  - WAL Log   │  │  - WAL Log  │  │  - WAL Log  │
    │  - Recovery  │  │  - Recovery │  │  - Recovery │
    └──────────────┘  └─────────────┘  └──────────────┘
```

### Core Components

#### 1. **Consistent Hashing (ring.py)**
- Implements a hash ring with virtual nodes for load balancing
- Uses SHA-1 hashing for key distribution
- 100 virtual nodes per physical node by default
- Enables efficient replica selection with `bisect` for O(log n) lookup

```python
# Example: Finding replicas for a key
replicas = ring.get_replicas("user_id_123", replication_factor=3)
# Returns: ["http://node2:8000", "http://node3:8000", "http://node1:8000"]
```

#### 2. **Key-Value Store (store.py)**
- In-memory storage with async access using locks
- Write-Ahead Logging (WAL) for crash recovery
- Versioned records with timestamps
- Soft deletes with deletion flag
- Automatic recovery from WAL on startup

**Storage Record Structure**:
```python
{
    "value": <any_data>,
    "timestamp": <unix_timestamp>,
    "deleted": <boolean>
}
```

#### 3. **Quorum Coordinator (coordinator.py)**
- Implements Dynamo-style quorum protocol
- **Quorum Write**: Write succeeds if W (write quorum) replicas acknowledge
- **Quorum Read**: Read returns latest version from R (read quorum) replicas
- Timestamp-based conflict resolution for concurrent writes
- Configurable W and R parameters for consistency tuning

#### 4. **FastAPI Application (main.py)**
Two categories of endpoints:

**Internal Replica APIs** (used by coordinator):
- `PUT /replica/{key}` - Write to local replica
- `GET /replica/{key}` - Read from local replica
- `DELETE /replica/{key}` - Delete from local replica

**Client-Facing APIs**:
- `PUT /kv/{key}` - Write key-value with quorum
- `GET /kv/{key}` - Read key-value with quorum
- `DELETE /kv/{key}` - Delete key-value with quorum

#### 5. **Configuration (config.py)**
```python
NODES = [...]              # Cluster nodes
REPLICATION_FACTOR = 3     # Total replicas per key
WRITE_QUORUM = 2          # Minimum writes for success
READ_QUORUM = 2           # Minimum reads for consistency
```

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- 15+ MB disk space (for container images)

### Quick Start with Docker Compose

1. **Clone the repository**:
   ```bash
   git clone https://github.com/idhanwal/distributed-kvstore.git
   cd distributed-kvstore/distributed-kv
   ```

2. **Start the cluster**:
   ```bash
   docker-compose up -d
   ```

   This starts 3 nodes:
   - Node 1: `http://localhost:8001`
   - Node 2: `http://localhost:8002`
   - Node 3: `http://localhost:8003`

3. **Verify cluster is running**:
   ```bash
   curl http://localhost:8001/docs
   ```

   Opens interactive API documentation (Swagger UI)

### Manual Setup (Local Development)

1. **Install dependencies**:
   ```bash
   cd distributed-kv
   pip install -r requirements.txt
   ```

2. **Create data directory**:
   ```bash
   mkdir -p data/node1
   ```

3. **Configure environment**:
   ```bash
   export NODE_ID=node1
   export PYTHONUNBUFFERED=1
   ```

4. **Run the node**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## 📚 API Usage

### Writing Data

```bash
# Put a key-value pair
curl -X PUT http://localhost:8001/kv/user_id_123 \
  -H "Content-Type: application/json" \
  -d '{"value": {"name": "John", "age": 30}}'

# Response
{"success": true}
```

### Reading Data

```bash
# Get a key-value pair
curl -X GET http://localhost:8001/kv/user_id_123

# Response (on successful write)
{
  "value": {"name": "John", "age": 30},
  "timestamp": 1703000000.123,
  "deleted": false
}
```

### Deleting Data

```bash
# Delete a key
curl -X DELETE http://localhost:8001/kv/user_id_123

# Response
{"deleted": true}
```

## ⚙️ Configuration Guide

### Tuning Consistency

Edit `app/config.py`:

```python
# Strong Consistency (W + R > N)
REPLICATION_FACTOR = 3
WRITE_QUORUM = 3  # All replicas must ack
READ_QUORUM = 1   # Read from any

# High Availability (W + R ≤ N)
REPLICATION_FACTOR = 5
WRITE_QUORUM = 2  # Majority ack
READ_QUORUM = 3   # Majority confirms
```

### Adding More Nodes

1. Update `app/config.py`:
   ```python
   NODES = [
       "http://node1:8000",
       "http://node2:8000",
       "http://node3:8000",
       "http://node4:8000",  # New node
       "http://node5:8000",  # New node
   ]
   ```

2. Update `docker-compose.yml`:
   ```yaml
   node4:
     build: .
     container_name: node4
     ports:
       - "8004:8000"
     environment:
       - NODE_ID=node4
     volumes:
       - ./data/node4:/app/data
   ```

3. Recreate cluster:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## 🔄 How It Works

### Write Operation Flow

```
Client → PUT /kv/mykey
    ↓
Coordinator identifies replicas [node2, node3, node1]
    ↓
Send write to all replicas in parallel
    ↓
node2: ✓ Written to memory & WAL
node3: ✓ Written to memory & WAL
node1: ✗ Timeout
    ↓
Check: 2 responses ≥ WRITE_QUORUM (2) → SUCCESS
    ↓
Response to Client: {"success": true}
```

### Read Operation Flow

```
Client → GET /kv/mykey
    ↓
Coordinator identifies replicas [node2, node3, node1]
    ↓
Send read to all replicas in parallel
    ↓
node2: {value: "xyz", timestamp: 1000, deleted: false}
node3: {value: "xyz", timestamp: 1000, deleted: false}
node1: ✗ Timeout
    ↓
Check: 2 responses ≥ READ_QUORUM (2) → SUCCESS
    ↓
Compare timestamps, return latest version
    ↓
Response to Client: {value: "xyz", timestamp: 1000, deleted: false}
```

## 💾 Durability & Recovery

### Write-Ahead Logging (WAL)

Each node maintains `data/wal.log`:

```json
["key1", {"value": "data1", "timestamp": 1000, "deleted": false}]
["key2", {"value": "data2", "timestamp": 1001, "deleted": false}]
["key1", {"value": null, "timestamp": 1002, "deleted": true}]
```

### Crash Recovery

On node restart:
1. Read `data/wal.log` sequentially
2. Rebuild in-memory data store
3. Resume normal operations
4. Eventual consistency syncs any missed updates

## 🔒 Fault Tolerance

### Node Failure Scenarios

| Scenario | Behavior | Recovery |
|----------|----------|----------|
| 1 node down | Write/Read succeed (quorum met) | Node recovers from WAL |
| 2 nodes down | Write fails, Read may fail | Rebuild failed nodes |
| Network partition | Partial availability | Split-brain prevention needed |

### Consistency Guarantees

- **Strong Consistency**: W + R > N (all replicas confirmation)
- **Eventual Consistency**: W + R ≤ N (faster, may have stale reads)
- **Read Repair**: Latest timestamp during read operations

## 📊 Performance Characteristics

| Operation | Complexity | Time |
|-----------|-----------|------|
| Write | O(log n) hash lookup + O(r) network calls | ~50-100ms |
| Read | O(log n) hash lookup + O(r) network calls | ~50-100ms |
| Recovery | O(n) log lines | Depends on WAL size |

*r = replication factor, n = cluster size*

## 🧪 Testing

### Manual Testing

1. **Write test**:
   ```bash
   curl -X PUT http://localhost:8001/kv/test_key \
     -d '{"value": "test_value"}'
   ```

2. **Read test**:
   ```bash
   curl http://localhost:8001/kv/test_key
   ```

3. **Failover test**:
   ```bash
   docker-compose stop node1
   curl http://localhost:8002/kv/test_key  # Should still work
   ```

4. **Recovery test**:
   ```bash
   docker-compose start node1
   # Check node1 WAL recovery from logs
   docker-compose logs node1
   ```

### Stress Testing

```python
import httpx
import asyncio

async def stress_test():
    async with httpx.AsyncClient() as client:
        for i in range(1000):
            await client.put(
                "http://localhost:8001/kv/key_" + str(i),
                json={"value": f"value_{i}"}
            )

asyncio.run(stress_test())
```

## 📈 Monitoring

### View logs
```bash
docker-compose logs -f node1
docker-compose logs -f node2
docker-compose logs -f node3
```

### Check node health
```bash
curl http://localhost:8001/docs  # Swagger UI
curl http://localhost:8001/openapi.json  # OpenAPI spec
```

### Inspect storage
```bash
cat distributed-kv/data/node1/wal.log
```

## 🔍 Key Concepts Explained

### Consistent Hashing
- Maps keys to nodes deterministically
- Minimizes data migration when nodes join/leave
- Virtual nodes improve load distribution

### Quorum Protocol
- Write Quorum (W): Minimum replicas that must acknowledge a write
- Read Quorum (R): Minimum replicas that must be consulted for a read
- Invariant: W + R > N ensures strong consistency

### Vector Clocks Alternative
- Uses simple timestamps for version tracking
- Sufficient for read-write workloads
- Could extend with vector clocks for complex conflicts

### Eventual Consistency
- Different replicas may have different values temporarily
- Converges to same value over time
- Sufficient for many applications (user profiles, product catalogs)

## 🚧 Known Limitations

1. **No Dynamic Cluster Resize**: Nodes must be configured upfront
2. **No Distributed Transactions**: Single-key operations only
3. **Basic Failure Detection**: Simple timeout-based (no heartbeat)
4. **No Compression**: WAL files grow unbounded
5. **In-Memory Only**: Reboot data loss without WAL
6. **No Security**: No authentication or encryption

## 🎯 Future Enhancements

- [ ] Distributed consensus (Raft/Paxos)
- [ ] Dynamic cluster membership
- [ ] Multi-version concurrency control
- [ ] Backup and replication
- [ ] Monitoring and metrics
- [ ] Compression and compaction
- [ ] TLS/SSL support
- [ ] Authentication and authorization

## 📖 Learning Resources

- **Dynamo Paper**: Amazon's paper on distributed key-value stores
- **Consistent Hashing**: Tom White's explanation
- **Quorum Protocols**: Byzantine Generals Problem
- **WAL Pattern**: Database durability techniques

## 📝 License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## 👤 Author

Created by [idhanwal](https://github.com/idhanwal)

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

1. Performance optimizations
2. Better failure detection
3. Cluster management
4. Comprehensive testing
5. Documentation improvements

To contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support & Issues

- Open a [GitHub Issue](https://github.com/idhanwal/distributed-kvstore/issues)
- Check FastAPI docs at `http://localhost:8001/docs`
- Review source code comments for implementation details

## 🔗 Links

- [GitHub Repository](https://github.com/idhanwal/distributed-kvstore)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Consistent Hashing Explained](https://www.akamai.com/us/en/multimedia/documents/technical-publication/consistent-hashing-and-random-trees-distributed-caching-protocols-for-relieving-hot-spots-on-the-world-wide-web-technical-publication.pdf)
- [Amazon Dynamo Paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)

---

**Last Updated**: December 2025
**Status**: Educational/Reference Implementation