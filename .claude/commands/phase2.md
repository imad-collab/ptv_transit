---
description: Bootstrap Phase 2 (Graph Construction) development
allowed-tools: Bash(pip:*), Bash(mkdir:*), Read, Write
---

# Phase 2: Graph Construction Bootstrap

Set up everything needed for Phase 2 development.

## Step 1: Verify Prerequisites

Check that Phase 1 is complete:
```bash
pytest tests/test_data/ --tb=no -q
```

Expected: All 62 tests passing.

## Step 2: Install NetworkX

```bash
pip install networkx
```

Verify installation:
```bash
python -c "import networkx as nx; print(f'NetworkX {nx.__version__} installed')"
```

## Step 3: Create Directory Structure

```bash
mkdir -p src/graph
mkdir -p tests/test_graph
touch src/graph/__init__.py
touch tests/test_graph/__init__.py
```

## Step 4: Create TransitGraph Skeleton

Create `src/graph/transit_graph.py` with this structure:

```python
"""
Transit Graph Module
Builds a NetworkX graph representing the transit network.
"""

import networkx as nx
from typing import Dict, List, Optional, Set
from dataclasses import dataclass

from src.data.models import Stop, StopTime, Trip
from src.data.gtfs_parser import GTFSParser


@dataclass
class Connection:
    """Represents a connection between two stops."""
    from_stop_id: str
    to_stop_id: str
    travel_time_seconds: int
    trip_id: str
    route_id: str


class TransitGraph:
    """
    Transit network graph built from GTFS data.
    
    Nodes: Stops (stations)
    Edges: Connections between stops with travel times
    """
    
    def __init__(self):
        """Initialize empty transit graph."""
        self.graph = nx.DiGraph()
        self._stops: Dict[str, Stop] = {}
    
    def build_from_gtfs(self, parser: GTFSParser) -> None:
        """
        Build graph from GTFS parser data.
        
        Args:
            parser: GTFSParser with loaded GTFS data
        """
        # TODO: Implement
        # 1. Add all stops as nodes
        # 2. Add edges from stop_times (consecutive stops on same trip)
        # 3. Add transfer edges from transfers.txt
        raise NotImplementedError("Phase 2 implementation needed")
    
    def add_stop(self, stop: Stop) -> None:
        """Add a stop as a node in the graph."""
        self.graph.add_node(
            stop.stop_id,
            name=stop.name,
            lat=stop.lat,
            lon=stop.lon,
            platform=stop.platform_code
        )
        self._stops[stop.stop_id] = stop
    
    def add_connection(self, connection: Connection) -> None:
        """Add a connection (edge) between two stops."""
        self.graph.add_edge(
            connection.from_stop_id,
            connection.to_stop_id,
            travel_time=connection.travel_time_seconds,
            trip_id=connection.trip_id,
            route_id=connection.route_id
        )
    
    def get_neighbors(self, stop_id: str) -> List[str]:
        """Get all stops directly reachable from a given stop."""
        if stop_id not in self.graph:
            return []
        return list(self.graph.successors(stop_id))
    
    def get_travel_time(self, from_stop: str, to_stop: str) -> Optional[int]:
        """Get travel time between two adjacent stops in seconds."""
        if self.graph.has_edge(from_stop, to_stop):
            return self.graph[from_stop][to_stop]['travel_time']
        return None
    
    @property
    def num_stops(self) -> int:
        """Number of stops (nodes) in the graph."""
        return self.graph.number_of_nodes()
    
    @property
    def num_connections(self) -> int:
        """Number of connections (edges) in the graph."""
        return self.graph.number_of_edges()
```

## Step 5: Create Test Skeleton

Create `tests/test_graph/test_transit_graph.py`:

```python
"""
Tests for Transit Graph Module
Target: 95%+ coverage
"""

import pytest
from src.graph.transit_graph import TransitGraph, Connection
from src.data.models import Stop


class TestTransitGraphInit:
    """Test TransitGraph initialization."""
    
    def test_init_creates_empty_graph(self):
        """Graph should start empty."""
        graph = TransitGraph()
        assert graph.num_stops == 0
        assert graph.num_connections == 0


class TestAddStop:
    """Test adding stops to graph."""
    
    def test_add_single_stop(self):
        """Should add stop as node with metadata."""
        graph = TransitGraph()
        stop = Stop(
            stop_id="47648",
            name="Tarneit Station",
            lat=-37.832,
            lon=144.694,
            platform_code="1"
        )
        graph.add_stop(stop)
        assert graph.num_stops == 1


class TestAddConnection:
    """Test adding connections between stops."""
    
    def test_add_connection(self):
        """Should add edge with travel time."""
        graph = TransitGraph()
        # Add stops first
        stop1 = Stop("A", "Stop A", 0, 0, "")
        stop2 = Stop("B", "Stop B", 0, 0, "")
        graph.add_stop(stop1)
        graph.add_stop(stop2)
        
        # Add connection
        conn = Connection(
            from_stop_id="A",
            to_stop_id="B",
            travel_time_seconds=300,
            trip_id="trip1",
            route_id="route1"
        )
        graph.add_connection(conn)
        
        assert graph.num_connections == 1
        assert graph.get_travel_time("A", "B") == 300


class TestGetNeighbors:
    """Test neighbor retrieval."""
    
    def test_get_neighbors_returns_connected_stops(self):
        """Should return all directly connected stops."""
        # TODO: Implement test
        pass


class TestBuildFromGTFS:
    """Test building graph from GTFS data."""
    
    def test_build_from_gtfs_creates_nodes(self):
        """Should create node for each stop."""
        # TODO: Implement test
        pass
    
    def test_build_from_gtfs_creates_edges(self):
        """Should create edges from stop_times."""
        # TODO: Implement test
        pass
```

## Step 6: Update Requirements

Add to `requirements.txt`:
```
networkx>=3.0
```

## Step 7: Run Initial Tests

```bash
pytest tests/test_graph/ -v
```

## Summary

After running this command, you will have:
- ✅ NetworkX installed
- ✅ `src/graph/transit_graph.py` skeleton
- ✅ `tests/test_graph/test_transit_graph.py` skeleton
- ✅ Ready to implement `build_from_gtfs()`

### Next Steps
1. Implement `build_from_gtfs()` method
2. Add edges from stop_times (consecutive stops)
3. Add transfer edges
4. Complete test suite
5. Target 95%+ coverage
