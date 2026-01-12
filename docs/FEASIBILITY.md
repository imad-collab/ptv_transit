# PTV Multi-Modal Journey Planner - Feasibility Analysis

## Executive Summary

**Feasibility: ✅ HIGHLY FEASIBLE**

Building a multi-modal journey planner for Melbourne's public transport using PTV's GTFS datasets is entirely feasible and technically sound. All required data sources are available, well-documented, and supported by mature Python libraries.

**Key Findings**:
- ✅ Complete data coverage (trains, trams, buses, V/Line)
- ✅ Both static schedules and realtime updates available
- ✅ Mature algorithms and libraries exist
- ✅ Reasonable development timeline (4-16 weeks depending on scope)
- ✅ Free data access with Creative Commons licensing

---

## Requirements Analysis

### User Requirements

**Core Functionality**:
1. Input: Starting station name + ending station name
2. Find: All transport options (train, tram, bus)
3. Explore: All possible route combinations
4. Optimize: For total travel time
5. Output: Best route suggestion + alternatives

**Implied Requirements**:
- Handle multi-modal journeys (e.g., train → tram)
- Account for transfer times and walking
- Consider real-time delays and disruptions
- Present results in user-friendly format
- Time-aware routing (different schedules throughout day)

### Technical Requirements

**Data Requirements**:
- ✅ Station/stop locations and names
- ✅ Route information (all modes)
- ✅ Scheduled timetables
- ✅ Transfer points and walking times
- ✅ Real-time service updates
- ✅ Service alerts and disruptions

**Algorithm Requirements**:
- Multi-modal graph traversal
- Time-dependent routing (schedules change by time of day)
- Transfer validation (minimum connection times)
- Multi-criteria optimization (time, transfers, walking)
- Real-time data integration

---

## Data Availability Assessment

### 1. Static GTFS Schedule Dataset

**Source**: Transport Victoria Open Data Portal
**URL**: https://opendata.transport.vic.gov.au/dataset/gtfs-schedule
**Size**: 242 MB (ZIP)
**Update Frequency**: Weekly or as-needed
**License**: Creative Commons Attribution 4.0 ✅ Free to use

**Coverage**:
- ✅ Metro trains (all lines)
- ✅ Trams (all routes)
- ✅ Metro & regional buses
- ✅ V/Line regional trains

**Available Files**:

| File | Purpose | Critical? |
|------|---------|-----------|
| `stops.txt` | Station/stop locations, names, coordinates | ✅ YES |
| `routes.txt` | Route definitions (lines, route names) | ✅ YES |
| `trips.txt` | Individual service trips | ✅ YES |
| `stop_times.txt` | Scheduled arrival/departure times | ✅ YES |
| `calendar.txt` | Service days (weekday/weekend schedules) | ✅ YES |
| `calendar_dates.txt` | Service exceptions (holidays, special events) | ✅ YES |
| `transfers.txt` | Pre-defined transfer points and times | ✅ YES |
| `pathways.txt` | Walking paths within stations | ⚠️ Nice-to-have |
| `levels.txt` | Multi-level station navigation | ⚠️ Nice-to-have |

**Data Quality**:
- ✅ Standardized GTFS format (industry standard)
- ✅ Includes wheelchair accessibility data
- ✅ Platform numbers for metro train stations
- ✅ Parent station grouping (multi-platform stops)
- ✅ Rolling 30-day window (always current)

**Assessment**: **EXCELLENT** - All critical data available

---

### 2. GTFS Realtime Feeds

**Source**: Transport Victoria Open Data Portal
**URL**: https://opendata.transport.vic.gov.au/dataset/gtfs-realtime
**Format**: Protocol Buffers (binary)
**Authentication**: API Key (header: `KeyID`)
**Rate Limit**: 24 requests / 60 seconds per service type
**Update Frequency**: 30-60 seconds (varies by mode)
**License**: Creative Commons Attribution 4.0

**Available Feeds**:

| Transport Mode | Trip Updates | Vehicle Positions | Service Alerts |
|----------------|--------------|-------------------|----------------|
| Metro Train | ✅ | ✅ | ✅ |
| Trams | ✅ | ✅ | ✅ |
| Metro/Regional Bus | ✅ | ✅ | ❌ |
| V/Line Train | ✅ | ✅ | ❌ |

**Feed Data**:
- **Trip Updates**: Arrival/departure predictions, delays, cancellations
- **Vehicle Positions**: Real-time vehicle locations
- **Service Alerts**: Planned/unplanned disruptions, route diversions

**Rate Limit Analysis**:
```
24 requests/min per service type
= 1 request every 2.5 seconds

For 10 total feeds (4 modes × ~2.5 feeds avg):
- Conservative: Poll each feed every 30s → 20 req/min ✅ Safe
- Aggressive: Poll each feed every 10s → 60 req/min ❌ Too fast
```

**Caching Strategy**:
- Server-side caching: 30 seconds
- Client should cache: 30 seconds minimum
- No point polling faster than 30s

**Assessment**: **GOOD** - Requires careful rate limit management

---

### 3. API Key Access

**Obtained**: ✅ YES
**Stored**: `.env` file (secure)
**Validated**: ✅ Successfully tested with metro train trip updates

**Authentication Method**:
```http
Header: KeyID
Value: <api-key>
```

**Assessment**: **COMPLETE** - Authentication working

---

## Technical Feasibility

### 1. Algorithm Selection

#### Problem Classification
This is a **Multi-Modal Time-Dependent Shortest Path Problem**:
- **Multi-modal**: Different transport modes (train, tram, bus)
- **Time-dependent**: Schedules vary by time of day
- **Shortest path**: Minimize travel time

#### Recommended Algorithm: **Connection Scan Algorithm (CSA)**

**Why CSA?**:
1. ✅ Specifically designed for timetable-based routing
2. ✅ Handles time-dependency natively
3. ✅ Simple to implement (~200 lines of Python)
4. ✅ Fast: O(n) where n = number of connections
5. ✅ Finds optimal solutions
6. ✅ Naturally handles transfers

**Alternative: RAPTOR (Round-based Public Transit Router)**
- More complex but faster for dense networks
- Better for finding multiple alternatives
- Harder to implement (~500 lines)

**Assessment**: **PROVEN** - Well-established algorithms exist

---

### 2. Library Ecosystem

#### GTFS Parsing

**Option 1: gtfs-kit** (Recommended)
```python
import gtfs_kit as gk
feed = gk.read_feed('gtfs.zip', dist_units='km')
```
- ✅ Well-maintained (last update: 2024)
- ✅ Fast pandas-based parsing
- ✅ Built-in validation
- ✅ Spatial operations support

**Option 2: partridge**
- ✅ Lightweight, minimal dependencies
- ⚠️ Less feature-rich

**Option 3: gtfspy**
- ✅ Academic-grade, includes routing
- ⚠️ Heavier dependency tree

**Assessment**: **MATURE** - Multiple production-ready options

---

#### Graph Algorithms

**NetworkX** (Recommended)
```python
import networkx as nx
G = nx.MultiDiGraph()  # Directed graph with multiple edges
```
- ✅ Industry standard
- ✅ Extensive algorithm library
- ✅ Excellent documentation
- ⚠️ Performance: Good for <100k nodes (Melbourne has ~22k stops)

**Alternative: igraph**
- Faster for very large graphs
- Less Pythonic API

**Assessment**: **EXCELLENT** - NetworkX sufficient for Melbourne network

---

#### Spatial Operations

**GeoPandas + Shapely**
```python
import geopandas as gpd
from shapely.geometry import Point

# Find stops within 500m
nearby_stops = stops_gdf[stops_gdf.distance(origin_point) < 500]
```

**Use Cases**:
- Calculate walking distances
- Find transfer options
- Spatial clustering of stops

**Assessment**: **STANDARD** - Mature geospatial stack

---

#### Fuzzy String Matching

**FuzzyWuzzy**
```python
from fuzzywuzzy import process

# Handle "Flinders St" vs "Flinders Street Station"
match = process.extractOne("Flinders St", all_station_names)
# Returns: ("Flinders Street Station", 95)
```

**Critical for**:
- User input handling
- Station name variations
- Typo tolerance

**Assessment**: **ESSENTIAL** - Well-proven library

---

### 3. Performance Analysis

#### Dataset Size
- **Static GTFS**: 242 MB compressed → ~600 MB uncompressed
- **Stops**: ~22,444 stops (metro bus alone)
- **Routes**: ~500-1000 routes (estimated)
- **Daily trips**: ~50,000-100,000 (estimated)

#### Memory Requirements

**Option A: In-Memory (Fast)**
```
GTFS data:        600 MB
Indexes:          200 MB
Graph:            300 MB
Realtime cache:    50 MB
------------------------
Total:          ~1.2 GB
```
✅ Fits comfortably in modern systems

**Option B: SQLite (Smaller footprint)**
```
Database file:    400 MB
Active memory:    200 MB
------------------------
Total:          ~600 MB
```
✅ Good for resource-constrained environments

**Option C: PostgreSQL + PostGIS (Production)**
```
Database:       Separate server
Active memory:  ~300 MB per worker
```
✅ Best for high-traffic production

**Assessment**: **FEASIBLE** - Moderate resource requirements

---

#### Query Performance Estimates

**Graph Build Time** (one-time startup):
- Load GTFS: 5-10 seconds
- Build indexes: 3-5 seconds
- Construct graph: 10-20 seconds
- **Total**: ~30 seconds startup

**Query Time** (per journey request):
- Name lookup: <1ms
- Routing (CSA): 50-200ms (depends on time window)
- Realtime fetch: 50-100ms (cached) or 200-500ms (API call)
- **Total**: 100-500ms per query

**Target**: <500ms average, <1000ms p95

**Assessment**: **ACCEPTABLE** - Sub-second response times achievable

---

### 4. Development Effort

#### Skill Requirements
- ✅ Python (moderate level)
- ✅ Graph algorithms (can use libraries)
- ✅ API integration (straightforward)
- ⚠️ Geospatial operations (learning curve)
- ⚠️ GTFS specification (well-documented)

#### Complexity Assessment

**Low Complexity** (1-2 weeks):
- GTFS parsing and indexing
- Basic graph construction
- Single-mode routing (train only)
- CLI interface

**Medium Complexity** (3-4 weeks):
- Multi-modal routing
- Transfer handling
- Realtime integration
- Web API (FastAPI)

**High Complexity** (6-8+ weeks):
- Advanced optimization (Pareto-optimal)
- Wheelchair routing
- Fare calculation
- Real-time disruption handling
- Production deployment

**Assessment**: **MANAGEABLE** - Clear path from MVP to production

---

## Risk Analysis

### High Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Rate limit exceeded | Service degradation | Implement caching (30s TTL), rate limiter, queue |
| GTFS data quality issues | Incorrect routes | Validation layer, fallback to older data |
| Realtime API downtime | No live updates | Graceful degradation to static schedules |

### Medium Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Station name ambiguity | Wrong stops matched | Fuzzy matching + confirmation prompt |
| Complex transfers not modeled | Suboptimal routes | Use `transfers.txt` + spatial proximity |
| Peak memory usage | System crashes | Database option, pagination, lazy loading |

### Low Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| GTFS format changes | Parser breaks | Use maintained libraries (gtfs-kit) |
| API key expiration | Auth failure | Rotation process, monitoring |

**Overall Risk**: **LOW-MEDIUM** - Standard engineering challenges

---

## Comparison: Build vs Use PTV API

### PTV Timetable API (Alternative)

PTV offers an official Timetable API:
- **URL**: `https://timetableapi.ptv.vic.gov.au/`
- **Features**: Directions, departures, stops, routes
- **Authentication**: HMAC signature required
- **Rate Limits**: Likely more generous

**Pros of PTV API**:
- ✅ Already built and maintained
- ✅ Guaranteed accuracy
- ✅ No hosting costs
- ✅ Officially supported

**Cons of PTV API**:
- ❌ Less control over optimization
- ❌ Limited customization
- ❌ Dependent on external service
- ❌ Potential rate limits for high usage
- ❌ No offline capability

### Recommendation

**For Production Use**: Consider PTV API first (less maintenance)
**For Learning/Research**: Build custom solution (valuable learning)
**For Specialized Use Cases**: Custom build (e.g., academic research, custom optimization)

---

## Feasibility Score

| Category | Score | Notes |
|----------|-------|-------|
| **Data Availability** | 10/10 | Complete GTFS static + realtime coverage |
| **Data Quality** | 9/10 | Standard format, well-maintained, minor edge cases |
| **Algorithm Maturity** | 10/10 | CSA/RAPTOR proven, libraries available |
| **Library Support** | 9/10 | Excellent Python ecosystem |
| **Development Effort** | 7/10 | Moderate complexity, clear path |
| **Performance** | 8/10 | Acceptable latency, moderate resources |
| **Risk Level** | 8/10 | Low-medium risks, all mitigatable |
| **Documentation** | 9/10 | GTFS spec excellent, PTV docs good |

**Overall Feasibility**: **9.0/10** - **HIGHLY FEASIBLE**

---

## Constraints & Limitations

### Known Limitations

1. **No Real-time Bus Alerts**
   - Only trip updates and positions available
   - Workaround: Use trip updates to infer disruptions

2. **30-Second Data Freshness**
   - Server-side caching means data can be 30s stale
   - Acceptable for journey planning use case

3. **Rate Limits**
   - 24 requests/minute per service type
   - Limits scalability for high-traffic applications
   - Mitigation: Aggressive caching, request batching

4. **No Fare Data**
   - GTFS feeds don't include fare information
   - Requires separate PTV API or manual fare rules

5. **Platform Changes**
   - Real-time platform changes not always available
   - May show wrong platform occasionally

6. **Transfer Time Assumptions**
   - `transfers.txt` may not cover all transfer scenarios
   - Need heuristic for unlisted transfers (e.g., 5 min minimum)

### Technical Constraints

1. **Memory**: ~1-2 GB for in-memory operation
2. **Startup Time**: ~30 seconds to load and index GTFS
3. **Query Latency**: 100-500ms typical, up to 1s for complex routes
4. **Data Updates**: Must re-load GTFS weekly (automated job needed)

---

## Success Criteria

### MVP (Minimum Viable Product)

**Timeline**: 4-6 weeks

**Features**:
- ✅ Load and parse static GTFS
- ✅ Find routes between two stations (train only)
- ✅ Basic CLI interface
- ✅ Optimize for travel time
- ✅ Show top 3 alternatives

**Success Metrics**:
- Finds correct route for 95% of test cases
- Query latency <1 second
- No crashes on valid inputs

### V1 (Production-Ready)

**Timeline**: 8-12 weeks

**Features**:
- ✅ Multi-modal routing (train + tram + bus)
- ✅ Real-time delay integration
- ✅ Transfer handling
- ✅ Web API (FastAPI)
- ✅ Fuzzy station name matching
- ✅ Service alert display

**Success Metrics**:
- Multi-modal routes correct for 90% of test cases
- Query latency <500ms (p50), <1s (p95)
- 99.9% uptime
- Matches PTV API results for 85%+ of queries

### V2 (Advanced)

**Timeline**: 16+ weeks

**Features**:
- ✅ Multiple optimization modes (time, transfers, walking)
- ✅ Wheelchair-accessible routing
- ✅ Time-window optimization (best departure time finder)
- ✅ Historical reliability data
- ✅ Fare estimation
- ✅ Live departure boards

---

## Conclusion

**Final Assessment**: **GO - HIGHLY FEASIBLE**

Building a multi-modal journey planner for Melbourne's public transport is:

1. ✅ **Technically Feasible**: All required data available, proven algorithms exist
2. ✅ **Economically Feasible**: Free data, moderate development costs
3. ✅ **Practically Feasible**: Clear development path, manageable complexity
4. ✅ **Legally Feasible**: CC BY 4.0 license permits commercial use

**Recommendation**:

- **Start with MVP** (single-mode, static data) → 4-6 weeks
- **Iterate to V1** (multi-modal, realtime) → 8-12 weeks total
- **Consider PTV API** for comparison/validation

**Key Success Factors**:
1. Proper GTFS data modeling
2. Efficient graph construction
3. Smart realtime feed caching
4. Robust error handling
5. Comprehensive testing against known routes

This project is an excellent learning opportunity and entirely achievable with the available resources.

---

## References

- GTFS Specification: https://gtfs.org/
- GTFS Realtime: https://gtfs.org/realtime/
- PTV Open Data Portal: https://opendata.transport.vic.gov.au/
- CSA Algorithm: https://arxiv.org/abs/1703.05997
- RAPTOR Algorithm: https://www.microsoft.com/en-us/research/publication/round-based-public-transit-routing/
