# PTV Multi-Modal Journey Planner - Architecture

## System Overview

A Python-based multi-modal journey planning system for Melbourne's public transport network (trains, trams, buses) using PTV's GTFS static and realtime datasets.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Journey Planner                        │
│              (CLI / Web API / Library)                   │
└─────────────────────────────────────────────────────────┘
                          │
          ┌───────────────┴───────────────┐
          │                               │
┌─────────▼────────┐          ┌──────────▼──────────┐
│  Static GTFS     │          │  Realtime GTFS      │
│  (Schedule Data) │          │  (Live Updates)     │
│  - 242 MB ZIP    │          │  - Trip Updates     │
│  - Weekly Update │          │  - Vehicle Pos      │
└──────────────────┘          │  - Service Alerts   │
          │                   └─────────────────────┘
          │                               │
    ┌─────▼──────┐              ┌────────▼────────┐
    │ GTFS       │              │ Realtime        │
    │ Parser     │              │ Feed Manager    │
    │            │              │                 │
    │ - stops    │              │ - Delay calc    │
    │ - routes   │              │ - Cancellations │
    │ - trips    │              │ - Alerts        │
    │ - times    │              │ - Caching (30s) │
    └─────┬──────┘              └────────┬────────┘
          │                               │
          └───────────┬───────────────────┘
                      │
              ┌───────▼────────┐
              │  Graph Builder │
              │                │
              │ - Transit Graph│
              │ - Transfers    │
              │ - Walkways     │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │ Routing Engine │
              │                │
              │ - CSA/RAPTOR   │
              │ - Multi-modal  │
              │ - Time-aware   │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │  Optimization  │
              │                │
              │ - Travel time  │
              │ - Transfers    │
              │ - Walking dist │
              └───────┬────────┘
                      │
              ┌───────▼────────┐
              │   Results      │
              │ - Best route   │
              │ - Alternatives │
              │ - Metadata     │
              └────────────────┘
```

## Component Architecture

### 1. Data Layer

#### 1.1 Static GTFS Manager
**Responsibility**: Load, parse, and index static schedule data

**Key Files**:
- `stops.txt` - Station/stop locations (lat/lon, name, platform info)
- `routes.txt` - Route definitions (train lines, tram routes, bus routes)
- `trips.txt` - Individual service trips with route associations
- `stop_times.txt` - Scheduled arrival/departure at each stop
- `transfers.txt` - Pre-defined transfer points and minimum transfer times
- `calendar.txt` / `calendar_dates.txt` - Service days and exceptions
- `pathways.txt` - Walking paths between platforms
- `levels.txt` - Multi-level station navigation

**Operations**:
- Load GTFS ZIP into memory or database
- Build indexes for fast lookups:
  - Stop name → Stop ID (fuzzy matching)
  - Route ID → Trips
  - Trip ID → Stop times
- Handle parent stations (multi-platform stops)

**Data Structure**:
```python
class GTFSStaticData:
    stops: Dict[str, Stop]              # stop_id → Stop
    routes: Dict[str, Route]            # route_id → Route
    trips: Dict[str, Trip]              # trip_id → Trip
    stop_times: Dict[str, List[StopTime]]  # trip_id → [StopTime]
    transfers: List[Transfer]

    # Indexes
    stop_name_index: Dict[str, List[str]]  # name → [stop_ids]
    stop_spatial_index: RTree              # Spatial queries
```

#### 1.2 Realtime Feed Manager
**Responsibility**: Fetch and cache realtime updates

**Feed Types**:
- Trip Updates (delays, schedule changes)
- Vehicle Positions (current location tracking)
- Service Alerts (disruptions, planned works)

**Operations**:
- Poll realtime feeds respecting rate limits (24 req/min)
- Cache responses with 30s TTL
- Parse protobuf messages
- Apply updates to static schedules

**Data Structure**:
```python
class RealtimeManager:
    trip_updates: Dict[str, TripUpdate]      # trip_id → update
    vehicle_positions: Dict[str, VehiclePos] # vehicle_id → position
    service_alerts: List[Alert]

    cache_timestamp: datetime
    cache_ttl: int = 30  # seconds

    def fetch_updates(self) -> None
    def get_trip_delay(self, trip_id: str) -> int
    def is_trip_cancelled(self, trip_id: str) -> bool
```

### 2. Graph Layer

#### 2.1 Transit Network Graph
**Responsibility**: Build traversable network graph

**Graph Structure**:
- **Nodes**: Stops (stations, tram stops, bus stops)
- **Edges**:
  - Transit connections (trip segments between consecutive stops)
  - Walking transfers (between nearby stops or platforms)
  - Pathway connections (within stations)

**Implementation**:
```python
import networkx as nx

class TransitGraph:
    graph: nx.MultiDiGraph

    def add_transit_edge(
        self,
        from_stop: str,
        to_stop: str,
        trip_id: str,
        departure_time: int,
        arrival_time: int,
        route_id: str
    )

    def add_transfer_edge(
        self,
        from_stop: str,
        to_stop: str,
        transfer_time: int,
        distance_m: float
    )
```

**Edge Attributes**:
```python
{
    'type': 'transit' | 'transfer' | 'pathway',
    'trip_id': str,
    'route_id': str,
    'mode': 'train' | 'tram' | 'bus',
    'departure_time': int,  # seconds since midnight
    'arrival_time': int,
    'duration': int,
    'distance': float,
    'stops_count': int,
    'platform': str
}
```

### 3. Routing Layer

#### 3.1 Routing Algorithms

**Primary: Connection Scan Algorithm (CSA)**
- Optimized for timetable-based routing
- Linear scan through all connections
- Handles time-dependent networks efficiently
- Finds Pareto-optimal journeys

**Alternative: RAPTOR (Round-based Public Transit Optimized Router)**
- Round-based approach (each round = one more transfer)
- Better for multi-criteria optimization
- Faster for dense networks

**Implementation Considerations**:
```python
class RoutingEngine:
    def __init__(self, static_data: GTFSStaticData, realtime: RealtimeManager):
        self.static = static_data
        self.realtime = realtime
        self.graph = self._build_graph()

    def find_journeys(
        self,
        origin: str,
        destination: str,
        departure_time: datetime,
        max_transfers: int = 3,
        modes: List[str] = ['train', 'tram', 'bus']
    ) -> List[Journey]:
        """
        Find all feasible journeys using CSA/RAPTOR
        Returns list of Journey objects sorted by criteria
        """
        pass
```

#### 3.2 Multi-Modal Routing

**Challenges**:
1. Mode transitions (train → tram requires walking transfer)
2. Transfer time validation (minimum connection time)
3. Platform changes at same station
4. Different service frequencies per mode

**Strategy**:
```python
class MultiModalRouter:
    def route(
        self,
        origin: str,
        destination: str,
        time: datetime,
        allowed_modes: Set[str]
    ) -> List[Journey]:
        """
        1. For each allowed mode, find direct connections
        2. Build transfer graph between modes
        3. Use CSA with mode-aware edge weights
        4. Filter invalid transfers (insufficient time)
        5. Rank by optimization criteria
        """
        pass
```

### 4. Optimization Layer

#### 4.1 Journey Ranking

**Primary Criterion**: Total Travel Time
```python
total_time = arrival_time - departure_time
```

**Secondary Criteria**:
- Number of transfers (fewer is better)
- Total walking distance (minimize)
- Service reliability (prefer frequent services)
- Wheelchair accessibility (if required)

**Scoring Function**:
```python
def score_journey(journey: Journey, weights: Dict[str, float]) -> float:
    """
    Weighted multi-criteria scoring

    score = w1 * total_time +
            w2 * num_transfers * 10 +  # 10 min penalty per transfer
            w3 * walking_distance / 100 +  # 1 min per 100m
            w4 * reliability_penalty
    """
    return (
        weights['time'] * journey.total_minutes +
        weights['transfers'] * journey.num_transfers * 10 +
        weights['walking'] * journey.total_walking_m / 100 +
        weights['reliability'] * journey.delay_risk_score
    )
```

#### 4.2 Realtime Adjustments

**Apply Delays**:
```python
def apply_realtime_updates(journey: Journey) -> Journey:
    """
    Adjust scheduled times with realtime data
    Invalidate if transfer becomes impossible
    """
    for leg in journey.legs:
        if leg.type == 'transit':
            delay = realtime.get_trip_delay(leg.trip_id)
            leg.arrival_time += delay
            leg.departure_time += delay

            # Check cancellation
            if realtime.is_trip_cancelled(leg.trip_id):
                journey.mark_invalid()
                return journey

    # Validate transfers still feasible
    for i in range(len(journey.legs) - 1):
        if not is_transfer_valid(journey.legs[i], journey.legs[i+1]):
            journey.mark_invalid()

    return journey
```

### 5. API Layer

#### 5.1 Core API

```python
class JourneyPlanner:
    def __init__(self):
        self.static_data = GTFSStaticData.load('gtfs.zip')
        self.realtime = RealtimeManager(api_key=os.getenv('PTV_API_KEY'))
        self.router = RoutingEngine(self.static_data, self.realtime)

    def plan_journey(
        self,
        origin_name: str,
        destination_name: str,
        departure_time: datetime,
        preferences: Dict = None
    ) -> JourneyResult:
        """
        Main API endpoint

        Args:
            origin_name: Station/stop name (fuzzy matched)
            destination_name: Station/stop name (fuzzy matched)
            departure_time: Desired departure time
            preferences: {
                'modes': ['train', 'tram', 'bus'],
                'max_transfers': 3,
                'max_walking_m': 1000,
                'wheelchair': False,
                'optimize_for': 'time' | 'transfers' | 'walking'
            }

        Returns:
            JourneyResult with best route and alternatives
        """
        # 1. Resolve station names
        origin_stops = self._fuzzy_match_stops(origin_name)
        dest_stops = self._fuzzy_match_stops(destination_name)

        # 2. Find all journeys
        all_journeys = []
        for origin in origin_stops:
            for dest in dest_stops:
                journeys = self.router.find_journeys(
                    origin, dest, departure_time,
                    max_transfers=preferences.get('max_transfers', 3),
                    modes=preferences.get('modes', ['train', 'tram', 'bus'])
                )
                all_journeys.extend(journeys)

        # 3. Apply realtime updates
        for journey in all_journeys:
            apply_realtime_updates(journey)

        # 4. Filter valid journeys
        valid = [j for j in all_journeys if j.is_valid]

        # 5. Rank by optimization criteria
        ranked = self._rank_journeys(valid, preferences.get('optimize_for', 'time'))

        return JourneyResult(
            best=ranked[0] if ranked else None,
            alternatives=ranked[1:6],  # Top 5 alternatives
            metadata={
                'total_found': len(all_journeys),
                'valid_count': len(valid),
                'realtime_applied': True,
                'query_time_ms': ...
            }
        )
```

## Data Models

### Journey Structure
```python
@dataclass
class Journey:
    origin: Stop
    destination: Stop
    departure_time: datetime
    arrival_time: datetime
    legs: List[Leg]
    total_duration_min: int
    total_distance_km: float
    num_transfers: int
    total_walking_m: float
    is_valid: bool
    alerts: List[str]

    @property
    def modes_used(self) -> List[str]:
        return list(set(leg.mode for leg in self.legs if leg.type == 'transit'))

@dataclass
class Leg:
    type: str  # 'transit' | 'transfer' | 'walk'
    mode: str  # 'train' | 'tram' | 'bus' | 'walk'
    route_id: str
    route_name: str
    trip_id: str
    from_stop: Stop
    to_stop: Stop
    departure_time: datetime
    arrival_time: datetime
    duration_min: int
    distance_m: float
    stops_count: int
    platform: str
    realtime_delay_sec: int

@dataclass
class Stop:
    stop_id: str
    name: str
    lat: float
    lon: float
    platform_code: str
    wheelchair_accessible: bool
    parent_station: str
```

## Technology Stack

### Core Libraries
```
gtfs-kit==6.1.0              # GTFS parsing
networkx==3.2.1              # Graph algorithms
pandas==2.1.4                # Data manipulation
geopandas==0.14.1            # Spatial operations
shapely==2.0.2               # Geometry
requests==2.31.0             # HTTP
gtfs-realtime-bindings       # Protobuf parsing
python-dotenv==1.0.0         # Config
```

### Routing Algorithms
```
# Option 1: Use existing library
gtfs-functions==1.0.0        # Built-in routing

# Option 2: Implement CSA/RAPTOR from scratch
```

### Database (Optional)
```
sqlalchemy==2.0.23           # ORM
psycopg2==2.9.9             # PostgreSQL
postgis                      # Spatial indexing
```

### Fuzzy Matching
```
fuzzywuzzy==0.18.0          # Station name matching
python-Levenshtein==0.23.0   # Speed up
```

### API Layer
```
fastapi==0.108.0            # REST API
uvicorn==0.25.0             # ASGI server
pydantic==2.5.0             # Data validation
```

## Performance Considerations

### 1. Data Loading
- **Static GTFS**: 242 MB ZIP
  - Option A: Load into memory (~500 MB RAM)
  - Option B: SQLite database (slower but smaller footprint)
  - Option C: PostgreSQL with PostGIS (production-ready)

### 2. Indexing Strategy
```python
# Essential indexes
stops_by_name: Dict[str, List[str]]           # O(1) name lookup
stops_spatial: RTree                          # O(log n) spatial queries
trips_by_route: Dict[str, List[str]]         # O(1) route lookup
stop_times_by_trip: Dict[str, List[StopTime]] # O(1) trip lookup

# Build at initialization
def build_indexes(gtfs_data) -> Indexes:
    # ~5-10 seconds for full Melbourne network
    pass
```

### 3. Caching
```python
# Realtime feed cache (30s TTL)
@lru_cache(maxsize=128)
def get_realtime_feed(feed_type: str) -> FeedMessage:
    if cache_expired():
        fetch_from_api()
    return cached_feed

# Journey cache (5 min TTL)
@lru_cache(maxsize=1000)
def find_journeys_cached(origin, dest, time_bucket) -> List[Journey]:
    # Round time to 5-minute buckets for cache hits
    pass
```

### 4. Query Optimization
- Limit search space with bounding box (don't search nationwide for city trips)
- Early termination if dominant solution found
- Limit max journey duration (e.g., 3 hours)
- Prune dominated journeys during search

## Scalability

### Horizontal Scaling
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ API     │     │ API     │     │ API     │
│ Server 1│     │ Server 2│     │ Server 3│
└────┬────┘     └────┬────┘     └────┬────┘
     └────────┬──────┴─────┬──────────┘
              │            │
        ┌─────▼────┐  ┌────▼─────┐
        │ Shared   │  │ Shared   │
        │ Cache    │  │ GTFS DB  │
        │ (Redis)  │  │ (Postgres│
        └──────────┘  └──────────┘
```

### Rate Limit Management
```python
# Distributed rate limiter (Redis)
from redis import Redis
from ratelimit import limits, sleep_and_retry

redis = Redis()

@sleep_and_retry
@limits(calls=24, period=60)
def fetch_realtime_feed(feed_url: str):
    # Ensures 24 req/min limit across all API servers
    pass
```

## Error Handling

### Failure Modes
1. **Static GTFS unavailable**: Graceful degradation (use cached version)
2. **Realtime API down**: Fall back to static schedules only
3. **No route found**: Suggest nearest alternatives
4. **Rate limit hit**: Queue request or return cached results

```python
class JourneyPlannerError(Exception):
    pass

class NoRouteFoundError(JourneyPlannerError):
    def __init__(self, origin, destination, suggestions):
        self.suggestions = suggestions  # Nearby stops with routes

class RealtimeUnavailableError(JourneyPlannerError):
    pass  # Non-fatal, use static schedules
```

## Security Considerations

1. **API Key Protection**:
   - Store in `.env` file (not in code)
   - Use environment variables in production
   - Rotate keys periodically

2. **Input Validation**:
   - Sanitize station names (prevent injection)
   - Validate time ranges (reasonable departure times)
   - Rate limit user requests

3. **Data Privacy**:
   - Don't log user queries
   - Anonymize analytics if collected

## Testing Strategy

### Unit Tests
- GTFS parser correctness
- Graph construction accuracy
- Routing algorithm validation
- Realtime update application

### Integration Tests
- End-to-end journey planning
- Multi-modal transfers
- Realtime feed integration

### Performance Tests
- Query latency benchmarks (target: <500ms)
- Memory usage monitoring
- Concurrent request handling

### Validation Tests
- Compare results with PTV's official API
- Validate against known good journeys
- Test edge cases (midnight crossings, service exceptions)

## Monitoring & Observability

```python
# Metrics to track
journey_query_duration_ms
journey_results_count
realtime_api_latency_ms
realtime_cache_hit_rate
invalid_journey_rate
api_error_rate
```

## Future Enhancements

1. **Fare calculation** (requires fare data)
2. **Real-time crowding** (requires vehicle capacity data)
3. **Bike-share integration** (multi-modal with bikes)
4. **Historical delay analysis** (predict reliability)
5. **Preference learning** (personalized suggestions)
6. **Live departure boards** (station-specific views)
