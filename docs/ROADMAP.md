# PTV Multi-Modal Journey Planner - Implementation Roadmap

## Overview

This document provides a phased implementation plan for building a multi-modal journey planner using PTV's GTFS data.

**Development Philosophy**: Incremental delivery with testable milestones

---

## Phase 0: Foundation (Week 1)

**Goal**: Set up development environment and validate data access

### Tasks

#### 0.1 Environment Setup
- [x] Create Python virtual environment
- [x] Install base dependencies
  ```bash
  pip install requests gtfs-realtime-bindings python-dotenv
  ```
- [x] Set up `.env` file with PTV API key
- [x] Create project structure

#### 0.2 Data Access Validation
- [x] Test realtime API access (trip updates)
- [x] Validate authentication (KeyID header)
- [x] Create basic feed fetcher script
- [ ] Download static GTFS dataset (242 MB)
- [ ] Extract and validate GTFS files

#### 0.3 Project Setup
- [x] Create `CLAUDE.md` with project guidance
- [ ] Set up Git repository
- [ ] Create `.gitignore` (exclude `.env`, `venv/`, `data/`)
- [ ] Initial documentation structure

### Deliverables
- ✅ Working development environment
- ✅ Validated API access
- ✅ Basic realtime feed reader (`read_gtfs_feed.py`)
- ⏳ Static GTFS dataset downloaded

**Status**: **85% Complete** (needs static GTFS download)

---

## Phase 1: Data Layer (Week 2)

**Goal**: Parse and index static GTFS data

### Tasks

#### 1.1 GTFS Parser
```python
# src/data/gtfs_parser.py

from dataclasses import dataclass
import pandas as pd
import zipfile

@dataclass
class GTFSData:
    stops: pd.DataFrame
    routes: pd.DataFrame
    trips: pd.DataFrame
    stop_times: pd.DataFrame
    calendar: pd.DataFrame
    transfers: pd.DataFrame

def load_gtfs(zip_path: str) -> GTFSData:
    """Load GTFS files from ZIP into pandas DataFrames"""
    pass
```

**Subtasks**:
- [ ] Create `GTFSData` class
- [ ] Parse all required GTFS files
- [ ] Add data validation (check required columns)
- [ ] Handle missing/optional files gracefully
- [ ] Add unit tests

#### 1.2 Stop Index
```python
# src/data/stop_index.py

class StopIndex:
    def __init__(self, stops_df: pd.DataFrame):
        self._build_indexes()

    def find_by_name(self, name: str, fuzzy: bool = True) -> List[Stop]:
        """Find stops by name (exact or fuzzy match)"""
        pass

    def find_nearby(self, lat: float, lon: float, radius_m: float) -> List[Stop]:
        """Find stops within radius of coordinates"""
        pass

    def get_parent_station(self, stop_id: str) -> Optional[str]:
        """Get parent station for multi-platform stops"""
        pass
```

**Subtasks**:
- [ ] Implement exact name lookup (dictionary)
- [ ] Add fuzzy matching (fuzzywuzzy)
- [ ] Build spatial index (GeoDataFrame)
- [ ] Handle parent stations
- [ ] Add unit tests with known stations

#### 1.3 Schedule Index
```python
# src/data/schedule_index.py

class ScheduleIndex:
    def get_trips_at_stop(
        self,
        stop_id: str,
        time_start: int,
        time_end: int,
        date: str
    ) -> List[TripAtStop]:
        """Get all trips passing through stop in time window"""
        pass

    def get_trip_stops(self, trip_id: str) -> List[StopTime]:
        """Get all stops for a trip in sequence"""
        pass
```

**Subtasks**:
- [ ] Index stop_times by stop_id
- [ ] Index stop_times by trip_id
- [ ] Handle service calendar (weekday/weekend)
- [ ] Handle exceptions (calendar_dates)
- [ ] Add unit tests

### Deliverables
- [ ] GTFS parser with validation
- [ ] Stop name search (exact + fuzzy)
- [ ] Schedule querying by stop and time
- [ ] Test coverage >80%

**Estimated Time**: 5-7 days

---

## Phase 2: Graph Construction (Week 3)

**Goal**: Build transit network graph

### Tasks

#### 2.1 Graph Builder
```python
# src/graph/builder.py

import networkx as nx

class TransitGraphBuilder:
    def __init__(self, gtfs_data: GTFSData):
        self.gtfs = gtfs_data
        self.graph = nx.MultiDiGraph()

    def build(self) -> nx.MultiDiGraph:
        """Build complete transit graph"""
        self._add_transit_edges()
        self._add_transfer_edges()
        self._add_walking_edges()
        return self.graph
```

**Subtasks**:
- [ ] Create nodes for all stops
- [ ] Add transit edges (from stop_times)
- [ ] Add transfer edges (from transfers.txt)
- [ ] Add walking edges (spatial proximity)
- [ ] Store edge attributes (time, distance, mode)

#### 2.2 Transfer Logic
```python
# src/graph/transfers.py

def calculate_transfer_time(
    from_stop: Stop,
    to_stop: Stop,
    transfers_df: pd.DataFrame
) -> int:
    """
    Calculate transfer time between stops
    1. Check transfers.txt for defined transfer
    2. If parent_station same, use min transfer time (2 min)
    3. Else calculate walking time from distance
    """
    pass
```

**Subtasks**:
- [ ] Parse transfers.txt
- [ ] Detect same-station transfers
- [ ] Calculate walking time (distance / 1.4 m/s)
- [ ] Set reasonable min/max transfer times

#### 2.3 Graph Validation
- [ ] Verify connectivity (all stops reachable)
- [ ] Check for isolated components
- [ ] Validate edge weights (no negatives)
- [ ] Test with known routes

### Deliverables
- [ ] Complete transit graph for Melbourne network
- [ ] Transfer time calculator
- [ ] Graph statistics (nodes, edges, connectivity)
- [ ] Validation tests

**Estimated Time**: 4-6 days

---

## Phase 3: Single-Mode Routing (Week 4)

**Goal**: Implement basic routing for trains only

### Tasks

#### 3.1 Connection Scan Algorithm (CSA)
```python
# src/routing/csa.py

def connection_scan(
    connections: List[Connection],
    origin_stop: str,
    destination_stop: str,
    departure_time: int
) -> Optional[Journey]:
    """
    Connection Scan Algorithm for earliest arrival time

    Args:
        connections: Sorted list of all connections (edges)
        origin_stop: Starting stop ID
        destination_stop: Target stop ID
        departure_time: Departure time in seconds since midnight

    Returns:
        Journey object or None if no route found
    """
    # Initialize earliest arrival times
    earliest = {stop: float('inf') for stop in all_stops}
    earliest[origin_stop] = departure_time

    # Scan all connections in chronological order
    for conn in connections:
        if conn.departure_time >= earliest[conn.from_stop]:
            if conn.arrival_time < earliest[conn.to_stop]:
                earliest[conn.to_stop] = conn.arrival_time
                # Track connection for path reconstruction

    # Reconstruct path
    if earliest[destination_stop] < float('inf'):
        return reconstruct_journey(...)
    return None
```

**Subtasks**:
- [ ] Define Connection and Journey data classes
- [ ] Implement CSA algorithm
- [ ] Add path reconstruction (backtracking)
- [ ] Filter by mode (train only for now)
- [ ] Test with known routes

#### 3.2 Journey Representation
```python
# src/routing/journey.py

@dataclass
class Journey:
    origin: Stop
    destination: Stop
    departure_time: datetime
    arrival_time: datetime
    legs: List[Leg]
    total_duration_min: int
    num_transfers: int

    def __str__(self) -> str:
        """Pretty print journey"""
        pass

@dataclass
class Leg:
    type: str  # 'transit' | 'transfer'
    mode: str  # 'train' | 'tram' | 'bus' | 'walk'
    from_stop: Stop
    to_stop: Stop
    departure_time: datetime
    arrival_time: datetime
    route_name: str
    trip_id: str
```

**Subtasks**:
- [ ] Define data classes
- [ ] Add validation
- [ ] Implement string formatting
- [ ] Add JSON serialization

#### 3.3 CLI Interface
```python
# src/cli/planner_cli.py

def main():
    parser = argparse.ArgumentParser(
        description='PTV Multi-Modal Journey Planner'
    )
    parser.add_argument('origin', help='Starting station name')
    parser.add_argument('destination', help='Destination station name')
    parser.add_argument('--time', help='Departure time (HH:MM)', default='now')
    parser.add_argument('--date', help='Date (YYYY-MM-DD)', default='today')
    parser.add_argument('--mode', choices=['train', 'tram', 'bus', 'all'], default='train')

    args = parser.parse_args()

    # Find journey
    journey = planner.plan(args.origin, args.destination, args.time)
    print(journey)
```

**Subtasks**:
- [ ] Create CLI argument parser
- [ ] Integrate with routing engine
- [ ] Format output nicely
- [ ] Handle errors gracefully

### Deliverables
- [ ] Working CSA implementation
- [ ] Single-mode (train) routing
- [ ] CLI interface
- [ ] Test with 10+ known train routes

**Estimated Time**: 5-7 days

---

## Phase 4: Multi-Modal Routing (Week 5-6)

**Goal**: Support train + tram + bus routing

### Tasks

#### 4.1 Multi-Modal CSA
```python
# src/routing/multimodal_csa.py

def multimodal_connection_scan(
    connections: List[Connection],
    origin_stop: str,
    destination_stop: str,
    departure_time: int,
    allowed_modes: Set[str] = {'train', 'tram', 'bus'}
) -> List[Journey]:
    """
    Multi-modal CSA with mode filtering
    Returns multiple Pareto-optimal journeys
    """
    pass
```

**Subtasks**:
- [ ] Extend CSA to handle multiple modes
- [ ] Add mode transition validation
- [ ] Find multiple alternatives (Pareto-optimal)
- [ ] Test mode combinations

#### 4.2 Transfer Validation
```python
# src/routing/transfer_validator.py

def is_transfer_valid(
    arriving_leg: Leg,
    departing_leg: Leg,
    min_transfer_time: int = 120  # 2 minutes default
) -> bool:
    """
    Check if transfer is physically possible

    Rules:
    - Minimum transfer time between arrival and departure
    - Same station or nearby stops
    - Account for walking time
    """
    time_available = (departing_leg.departure_time -
                     arriving_leg.arrival_time).total_seconds()

    if arriving_leg.to_stop.parent_station == departing_leg.from_stop.parent_station:
        # Same station - use min transfer time
        return time_available >= min_transfer_time
    else:
        # Different stations - calculate walking time
        walking_time = calculate_walking_time(
            arriving_leg.to_stop,
            departing_leg.from_stop
        )
        return time_available >= walking_time
```

**Subtasks**:
- [ ] Implement transfer validation
- [ ] Add walking time calculation
- [ ] Handle edge cases (cross-platform, cross-station)
- [ ] Test with known transfer scenarios

#### 4.3 Journey Ranking
```python
# src/routing/ranker.py

def rank_journeys(
    journeys: List[Journey],
    criteria: str = 'time'
) -> List[Journey]:
    """
    Rank journeys by optimization criteria

    Criteria:
    - 'time': Minimize total travel time
    - 'transfers': Minimize number of transfers
    - 'walking': Minimize walking distance
    - 'balanced': Weighted combination
    """
    if criteria == 'time':
        return sorted(journeys, key=lambda j: j.total_duration_min)
    elif criteria == 'transfers':
        return sorted(journeys, key=lambda j: (j.num_transfers, j.total_duration_min))
    # ... other criteria
```

**Subtasks**:
- [ ] Implement ranking functions
- [ ] Add multi-criteria scoring
- [ ] Filter dominated journeys
- [ ] Test ranking logic

### Deliverables
- [ ] Multi-modal routing (train + tram + bus)
- [ ] Transfer validation
- [ ] Journey ranking by multiple criteria
- [ ] Test with 20+ multi-modal routes

**Estimated Time**: 7-10 days

---

## Phase 5: Realtime Integration (Week 7)

**Goal**: Incorporate realtime delays and alerts

### Tasks

#### 5.1 Realtime Feed Manager
```python
# src/realtime/feed_manager.py

class RealtimeFeedManager:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cache = {}
        self.cache_ttl = 30  # seconds

    def fetch_trip_updates(self, mode: str) -> Dict[str, TripUpdate]:
        """Fetch and cache trip updates for mode"""
        cache_key = f'trip_updates_{mode}'
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]

        # Fetch from API
        url = self._get_feed_url(mode, 'trip-updates')
        feed = fetch_gtfs_feed(url, self.api_key)

        # Parse and cache
        updates = self._parse_trip_updates(feed)
        self.cache[cache_key] = (updates, time.time())
        return updates

    def get_trip_delay(self, trip_id: str) -> int:
        """Get delay in seconds for trip"""
        pass

    def is_trip_cancelled(self, trip_id: str) -> bool:
        """Check if trip is cancelled"""
        pass
```

**Subtasks**:
- [ ] Implement feed fetcher for all modes
- [ ] Add caching with TTL
- [ ] Parse trip updates, vehicle positions, alerts
- [ ] Handle API errors gracefully

#### 5.2 Journey Adjuster
```python
# src/realtime/adjuster.py

def apply_realtime_updates(
    journey: Journey,
    feed_manager: RealtimeFeedManager
) -> Journey:
    """
    Adjust journey with realtime data

    Updates:
    - Apply delays to scheduled times
    - Mark cancelled trips
    - Invalidate if transfer becomes impossible
    """
    for leg in journey.legs:
        if leg.type == 'transit':
            # Get realtime update for this trip
            delay = feed_manager.get_trip_delay(leg.trip_id)
            leg.departure_time += timedelta(seconds=delay)
            leg.arrival_time += timedelta(seconds=delay)

            # Check cancellation
            if feed_manager.is_trip_cancelled(leg.trip_id):
                journey.mark_invalid()
                journey.alerts.append(f"Service {leg.route_name} cancelled")

    # Validate transfers still work
    for i in range(len(journey.legs) - 1):
        if not is_transfer_valid(journey.legs[i], journey.legs[i+1]):
            journey.mark_invalid()
            journey.alerts.append("Transfer no longer feasible due to delays")

    return journey
```

**Subtasks**:
- [ ] Apply delays to journey legs
- [ ] Detect cancelled trips
- [ ] Re-validate transfers
- [ ] Add service alerts to results

#### 5.3 Rate Limiter
```python
# src/realtime/rate_limiter.py

from collections import deque
import time

class RateLimiter:
    def __init__(self, max_calls: int = 24, period: int = 60):
        self.max_calls = max_calls
        self.period = period
        self.calls = deque()

    def wait_if_needed(self):
        """Block if rate limit would be exceeded"""
        now = time.time()

        # Remove calls outside the window
        while self.calls and self.calls[0] < now - self.period:
            self.calls.popleft()

        # Wait if at limit
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            time.sleep(sleep_time)

        self.calls.append(time.time())
```

**Subtasks**:
- [ ] Implement rate limiter
- [ ] Integrate with feed fetcher
- [ ] Add monitoring/logging
- [ ] Test rate limit compliance

### Deliverables
- [ ] Realtime feed integration
- [ ] Delay-aware journey planning
- [ ] Cancellation detection
- [ ] Service alerts display
- [ ] Rate limiting

**Estimated Time**: 4-5 days

---

## Phase 6: API & Polish (Week 8)

**Goal**: Create web API and improve UX

### Tasks

#### 6.1 FastAPI Web Service
```python
# src/api/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="PTV Journey Planner API")

class JourneyRequest(BaseModel):
    origin: str
    destination: str
    departure_time: Optional[str] = None
    modes: List[str] = ['train', 'tram', 'bus']
    max_transfers: int = 3

class JourneyResponse(BaseModel):
    best_journey: Journey
    alternatives: List[Journey]
    metadata: dict

@app.post("/plan", response_model=JourneyResponse)
def plan_journey(request: JourneyRequest):
    """Plan a journey between two locations"""
    try:
        result = planner.plan(
            origin=request.origin,
            destination=request.destination,
            time=request.departure_time,
            modes=request.modes
        )
        return result
    except NoRouteFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**Subtasks**:
- [ ] Create FastAPI application
- [ ] Define request/response models
- [ ] Add input validation
- [ ] Add error handling
- [ ] Add API documentation (Swagger)

#### 6.2 Improvements
- [ ] Better error messages
- [ ] Progress indicators for CLI
- [ ] Journey visualization (ASCII art or web)
- [ ] Configuration file support
- [ ] Logging

### Deliverables
- [ ] REST API with FastAPI
- [ ] API documentation
- [ ] Improved CLI UX
- [ ] Configuration management

**Estimated Time**: 3-4 days

---

## Phase 7: Testing & Validation (Week 9)

**Goal**: Comprehensive testing and validation

### Tasks

#### 7.1 Test Suite
- [ ] Unit tests for all components (>80% coverage)
- [ ] Integration tests (end-to-end journeys)
- [ ] Performance tests (query latency)
- [ ] Load tests (concurrent requests)

#### 7.2 Validation
- [ ] Compare results with PTV official API
- [ ] Test against known routes (create test set)
- [ ] Edge case testing:
  - Midnight crossings
  - Service exceptions (holidays)
  - Very long routes (>2 hours)
  - No route available
  - Stations with same names

#### 7.3 Documentation
- [ ] API documentation
- [ ] User guide
- [ ] Developer guide
- [ ] Deployment guide

### Deliverables
- [ ] Comprehensive test suite
- [ ] Validation report
- [ ] Complete documentation

**Estimated Time**: 5-7 days

---

## Phase 8: Optimization (Week 10+)

**Goal**: Performance optimization and advanced features

### Tasks

#### 8.1 Performance
- [ ] Profile and optimize hot paths
- [ ] Database backend (PostgreSQL + PostGIS)
- [ ] Caching strategy optimization
- [ ] Parallel processing for alternatives

#### 8.2 Advanced Features
- [ ] Wheelchair-accessible routing
- [ ] Time window optimization (find best departure time)
- [ ] Fare calculation
- [ ] Historical reliability data
- [ ] Live departure boards

#### 8.3 Production Readiness
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Monitoring and alerting
- [ ] Auto-update GTFS data (weekly job)

---

## Milestones Summary

| Phase | Duration | Deliverable | Status |
|-------|----------|-------------|--------|
| **0. Foundation** | Week 1 | Dev env, API validation | 85% ✅ |
| **1. Data Layer** | Week 2 | GTFS parser, indexes | ⏳ Not started |
| **2. Graph** | Week 3 | Transit network graph | ⏳ Not started |
| **3. Single-Mode** | Week 4 | Train routing + CLI | ⏳ Not started |
| **4. Multi-Modal** | Week 5-6 | All modes routing | ⏳ Not started |
| **5. Realtime** | Week 7 | Live updates integration | ⏳ Not started |
| **6. API** | Week 8 | Web API + UX | ⏳ Not started |
| **7. Testing** | Week 9 | Test suite + validation | ⏳ Not started |
| **8. Optimization** | Week 10+ | Performance + advanced | ⏳ Not started |

---

## MVP Definition (Weeks 1-4)

**Minimum Viable Product Scope**:
- ✅ Static GTFS parsing
- ✅ Single-mode routing (train only)
- ✅ Basic CLI interface
- ✅ Find best route by travel time
- ❌ No realtime (static schedules only)
- ❌ No web API (CLI only)
- ❌ No multi-modal (trains only)

**MVP Success Criteria**:
- Correctly finds train routes between any two metro stations
- Query time <1 second
- Shows top 3 alternatives
- Handles common errors gracefully

**MVP Timeline**: 4 weeks

---

## V1 Definition (Weeks 1-8)

**V1 Scope** (Production-ready):
- ✅ Multi-modal routing (train + tram + bus)
- ✅ Realtime updates integration
- ✅ Web API (FastAPI)
- ✅ Fuzzy station matching
- ✅ Service alerts
- ✅ Multiple alternatives

**V1 Success Criteria**:
- Multi-modal routes correct for 90%+ of test cases
- Query time <500ms average
- API uptime 99%+
- Matches PTV results for 80%+ of queries

**V1 Timeline**: 8 weeks

---

## Resource Requirements

### Development
- **Time**: 8-10 weeks for V1 (1 developer, part-time)
- **Skills**: Python, algorithms, APIs, GTFS
- **Tools**: VSCode, Git, Python 3.9+

### Infrastructure (Production)
- **Server**: 2-4 GB RAM, 20 GB storage
- **Database**: PostgreSQL (optional for V1)
- **Hosting**: Cloud VM (AWS, GCP, Azure) or VPS

### Ongoing
- **Data updates**: Automated weekly GTFS refresh
- **Monitoring**: Error tracking, performance metrics
- **Maintenance**: ~2-4 hours/month

---

## Next Steps (Immediate)

1. **Complete Phase 0**:
   - [ ] Download static GTFS (242 MB)
   - [ ] Extract and validate files
   - [ ] Set up Git repository

2. **Start Phase 1**:
   - [ ] Install data processing libraries:
     ```bash
     pip install pandas geopandas gtfs-kit fuzzywuzzy
     ```
   - [ ] Create project structure:
     ```
     src/
       data/
       graph/
       routing/
       api/
       cli/
     tests/
     docs/
     data/
     ```
   - [ ] Begin GTFS parser implementation

3. **Documentation**:
   - [x] Architecture document
   - [x] Feasibility analysis
   - [x] This roadmap
   - [ ] API specification

---

## Risk Mitigation

### Top Risks & Mitigations

1. **GTFS data quality issues**
   - Mitigation: Validate data on load, fallback to previous version
   - Test: Create validation test suite

2. **CSA algorithm complexity**
   - Mitigation: Use reference implementation first, optimize later
   - Test: Unit tests with known routes

3. **Realtime API rate limits**
   - Mitigation: Aggressive caching, rate limiter
   - Test: Load testing with concurrent requests

4. **Performance (query latency)**
   - Mitigation: Start with in-memory, optimize later
   - Test: Benchmark against target (<500ms)

---

## Success Metrics

### Development Metrics
- Code coverage: >80%
- Build time: <30 seconds
- Test execution: <5 minutes

### Product Metrics
- Query latency: <500ms (p50), <1s (p95)
- Accuracy: 90%+ match with PTV API
- Availability: 99%+ uptime

### Usage Metrics (if deployed)
- Daily active users
- Average queries per user
- Error rate <1%

---

## Appendix: Code Structure

```
PTV_GTFS/
├── .env                      # API keys (gitignored)
├── .gitignore
├── requirements.txt
├── README.md
├── CLAUDE.md                 # Project guidance
├── setup.py
│
├── src/
│   ├── __init__.py
│   │
│   ├── data/                 # Data layer
│   │   ├── gtfs_parser.py    # Parse GTFS files
│   │   ├── stop_index.py     # Stop lookup
│   │   ├── schedule_index.py # Timetable queries
│   │   └── models.py         # Data classes
│   │
│   ├── graph/                # Graph layer
│   │   ├── builder.py        # Graph construction
│   │   ├── transfers.py      # Transfer logic
│   │   └── validator.py      # Graph validation
│   │
│   ├── routing/              # Routing layer
│   │   ├── csa.py            # Connection Scan Algorithm
│   │   ├── multimodal.py     # Multi-modal routing
│   │   ├── journey.py        # Journey models
│   │   └── ranker.py         # Journey ranking
│   │
│   ├── realtime/             # Realtime layer
│   │   ├── feed_manager.py   # Fetch realtime feeds
│   │   ├── adjuster.py       # Apply updates
│   │   └── rate_limiter.py   # Rate limiting
│   │
│   ├── api/                  # API layer
│   │   ├── main.py           # FastAPI app
│   │   ├── models.py         # Request/response models
│   │   └── routes.py         # API endpoints
│   │
│   └── cli/                  # CLI interface
│       └── planner_cli.py    # Command-line tool
│
├── tests/
│   ├── test_data/
│   ├── test_graph/
│   ├── test_routing/
│   └── test_integration/
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── FEASIBILITY.md
│   ├── ROADMAP.md (this file)
│   ├── DATA_SOURCES.md
│   └── CHECKPOINT.md
│
├── data/                     # Data files (gitignored)
│   ├── gtfs.zip
│   └── gtfs/
│       ├── stops.txt
│       ├── routes.txt
│       └── ...
│
└── scripts/
    ├── download_gtfs.py      # Download latest GTFS
    └── update_data.sh        # Weekly update job
```
