# Project Context - Resume Point

**Date**: 2026-01-13
**Repository**: https://github.com/imad-collab/ptv_transit
**Branch**: main
**Last Commit**: `7ed43a6` - "Update project documentation with Phase 1 completion status"

---

## Current State Summary

You are building a **PTV Transit Assistant** - a journey planner for Melbourne's public transport network. The project follows a phased approach with comprehensive test coverage.

### What's Complete ✅

1. **Phase 0: Foundation** (100% complete, 21 tests, 100% coverage)
   - Real-time GTFS feed fetcher
   - Protobuf parsing
   - PTV API integration

2. **Phase 1: Data Layer** (100% complete, 62 tests, 97% coverage)
   - GTFS static data parser
   - Type-safe data models
   - Stop index with fuzzy search
   - Successfully answered: "Tarneit to Waurn Ponds - what trips are available?" (1,989 trips found)

### What's Next ⏳

**Phase 2: Graph Construction** - Build transit network graph using NetworkX
- Create nodes for stops
- Create edges for connections with travel times
- Handle transfers
- Target: 95%+ test coverage

---

## Key Project Information

### Repository Structure
```
PTV_Assistant-main/
├── src/
│   ├── data/           ✅ Complete - GTFS parser, models, stop index
│   ├── realtime/       ✅ Complete - Feed fetcher
│   ├── graph/          ⏳ Empty - Next phase
│   ├── routing/        ⏳ Empty - Future phase
│   ├── api/            ⏳ Empty - Future phase
│   └── cli/            ⏳ Empty - Future phase
├── tests/
│   ├── test_data/      ✅ 62 tests
│   └── test_realtime/  ✅ 21 tests
├── data/
│   └── gtfs/           ✅ V/Line data extracted (497 stops, 13 routes, 8,096 trips)
└── docs/               ✅ Documentation files
```

### Important Files

**Source Code:**
- `src/data/models.py` - GTFS dataclasses (Stop, Route, Trip, StopTime, etc.)
- `src/data/gtfs_parser.py` - CSV parser for GTFS files
- `src/data/stop_index.py` - Fast stop lookup with fuzzy matching
- `src/realtime/feed_fetcher.py` - Real-time feed fetcher

**Tests:**
- `tests/test_data/` - 62 tests for Phase 1
- `tests/test_realtime/` - 21 tests for Phase 0
- `tests/test_data/fixtures/` - Sample GTFS CSV files

**Documentation:**
- `README.md` - Project overview and roadmap
- `DEVELOPMENT_STATUS.md` - Detailed progress report
- `CLAUDE.md` - Instructions for Claude Code
- `docs/` - Architecture, feasibility, data sources

**Data:**
- `data/gtfs/` - Extracted V/Line GTFS data

---

## Test Coverage Status

| Component | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| Phase 0: Realtime | 21 | 100% | ✅ Complete |
| Phase 1: Data Layer | 62 | 97% | ✅ Complete |
| **Total** | **83** | **98%** | **2/8 phases done** |

Run tests:
```bash
pytest                                    # All tests
pytest tests/test_data/                   # Phase 1 only
pytest --cov=src --cov-report=term-missing  # With coverage
```

---

## Key Technical Decisions

### GTFS Data Extraction
- **What**: Extracted only V/Line regional train data (route_type=1)
- **Why**: Full extraction with all modes (metro, tram, bus) had performance issues on 17M rows
- **Result**: 497 stops, 13 routes, 8,096 trips - sufficient for development
- **Future**: May need to extract all modes for full Melbourne network

### Test Fixtures
- **Location**: `tests/test_data/fixtures/`
- **Files**: 8 CSV files (stops.txt, routes.txt, trips.txt, etc.)
- **Encoding**: UTF-8 with BOM (matches real GTFS files)
- **Size**: 2-4 sample records per file for fast testing

### Fuzzy Matching
- **Library**: fuzzywuzzy with python-Levenshtein
- **Scorer**: `token_sort_ratio` (handles word order)
- **Default threshold**: 60% similarity
- **Example**: "Waurn Pond" → "Waurn Ponds Station" (95% match)

---

## Important Data

### Sample Stations (for testing queries)
- **Tarneit Station**: stop_id `47648`, lat `-37.832`, lon `144.694`
- **Waurn Ponds Station**: stop_id `47641`, lat `-38.216`, lon `144.306`
- **Example route**: Geelong - Melbourne Via Geelong line
- **Example trip**: Departs Tarneit 14:57, arrives Waurn Ponds 15:48 (51 min)

### GTFS Data Stats
- 497 stops
- 13 routes
- 8,096 trips
- 1,989 trips serve both Tarneit and Waurn Ponds

---

## Git Status

### Recent Commits
```
7ed43a6 Update project documentation with Phase 1 completion status
f17c4b0 Phase 1: Data Layer Complete ✅
873891e Add comprehensive test report for Phase 0
0f78d7e Phase 0: Foundation Complete ✅
```

### Remote Repository
- **URL**: https://github.com/imad-collab/ptv_transit.git
- **Status**: All commits pushed
- **Branch**: main (tracking origin/main)

### Working Directory
- **Status**: Clean (no uncommitted changes)
- **Untracked files**: `scripts/extract_all_gtfs.py` (extraction script, not committed)

---

## Environment Setup

### Python Environment
```bash
# Virtual environment location
source venv/bin/activate  # or: source .venv/bin/activate

# Check Python version
python --version  # Should be 3.9+
```

### Dependencies
```bash
# Production
requests>=2.31.0
protobuf>=4.23.0
gtfs-realtime-bindings>=1.0.0
pandas>=2.1.0
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.20.0

# Development
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1
requests-mock>=1.11.0

# Install
pip install -r requirements.txt
```

### PTV API Key
- **Required**: For real-time feed fetcher
- **Get from**: https://opendata.transport.vic.gov.au/
- **Set via**: `export PTV_API_KEY='your-key-here'` or `.env` file

---

## How to Resume Work

### Quick Context Refresh
1. **Read this file** (CONTEXT.md) - You're doing it now! ✅
2. **Check git status**: `git status` and `git log --oneline -5`
3. **Run tests**: `pytest` to verify everything works
4. **Review**: `DEVELOPMENT_STATUS.md` for detailed progress

### Next Steps - Phase 2: Graph Construction

**Goal**: Build a transit network graph representing how stops connect

**Tasks**:
1. Install NetworkX: `pip install networkx`
2. Create `src/graph/transit_graph.py`
3. Implement `TransitGraph` class:
   - Build graph from GTFS parser data
   - Nodes: Stops (with metadata)
   - Edges: Connections between stops with travel times
   - Add transfer edges
4. Write tests in `tests/test_graph/test_transit_graph.py`
5. Target: 95%+ test coverage
6. Commit and push to GitHub

**Success Criteria**:
- Can build graph from 497 V/Line stops
- Can query: "What stops connect to Tarneit?"
- Can retrieve: "Travel time from Tarneit to next stop?"
- All tests passing

### Common Commands

```bash
# Testing
pytest                                      # Run all tests
pytest tests/test_data/ -v                  # Run Phase 1 tests verbosely
pytest --cov=src --cov-report=term-missing  # Coverage report

# Git
git status                                  # Check status
git log --oneline -5                        # Recent commits
git add <files>                             # Stage changes
git commit -m "message"                     # Commit
git push                                    # Push to GitHub

# GTFS Data
ls data/gtfs/                              # View extracted files
head -5 data/gtfs/stops.txt                # Preview stops data

# Python
python read_gtfs_feed.py                   # Run real-time feed viewer
```

---

## Known Issues & Technical Debt

1. **Limited to V/Line data**: Need to extract metro, tram, bus for full network
2. **No service calendar filtering**: All trips loaded regardless of which days they run
3. **No direction filtering**: Trips in both directions included in results
4. **Missing optional files**: Calendar and transfers files may not exist in all feeds

These are intentional simplifications for Phase 1. Will be addressed in future phases.

---

## Key Questions You Asked

1. **"Explain what you mean by a trip?"**
   - A trip = one vehicle's complete journey on a route at a specific time
   - Example: The 8:00 AM train from Geelong to Melbourne is one trip
   - The same route may have 100+ trips per day at different times

2. **"Is Phase 1 done?"**
   - Yes! ✅ 62 tests, 97% coverage, committed to Git

3. **"Is Phase 2 done?"**
   - No, not started yet. Phase 2 is next.

4. **"Did my progress commit on GitHub repository?"**
   - Yes! ✅ All pushed to https://github.com/imad-collab/ptv_transit

---

## Important Concepts

### GTFS (General Transit Feed Specification)
- **Static GTFS**: CSV files with schedules (stops.txt, routes.txt, trips.txt, etc.)
- **Realtime GTFS**: Protobuf API with live delays and positions
- **Our data**: 242 MB ZIP from PTV Open Data Portal

### Data Models
- **Stop**: A station/stop with location (lat/lon)
- **Route**: A transit line (e.g., "Geelong - Melbourne")
- **Trip**: One vehicle journey on a route with specific times
- **StopTime**: Arrival/departure time at a specific stop for a trip

### Testing Philosophy
- **Target**: 95%+ coverage on all new code
- **Approach**: Test-driven development, write tests first
- **Fixtures**: Use minimal sample data for fast tests
- **Real data**: Separate fixtures for integration testing

---

## Project Vision

### End Goal
A journey planner that answers queries like:
- "How do I get from Tarneit to Waurn Ponds leaving at 2 PM?"
- "What's the fastest route from Flinders Street to Geelong?"
- "Show me all trains from Southern Cross in the next hour"

### Current Capability
- ✅ Can parse GTFS data
- ✅ Can find stations by name
- ✅ Can list all trips between two stations
- ❌ Cannot find optimal routes yet (Phase 3)
- ❌ Cannot apply real-time delays yet (Phase 5)

---

## Contact & Resources

- **Repository**: https://github.com/imad-collab/ptv_transit
- **PTV Data**: https://opendata.transport.vic.gov.au/
- **GTFS Spec**: https://gtfs.org/
- **GTFS Realtime**: https://developers.google.com/transit/gtfs-realtime

---

## Quick Checklist for Next Session

- [ ] Read this CONTEXT.md file
- [ ] Check git status and recent commits
- [ ] Run `pytest` to verify tests pass
- [ ] Review DEVELOPMENT_STATUS.md
- [ ] Decide: Continue with Phase 2 or work on something else?
- [ ] If Phase 2: Install NetworkX and create transit_graph.py
- [ ] Commit and push all work before ending session

---

**This file captures everything you need to resume work. Read it at the start of your next session!**

**Last Updated**: 2026-01-13
**Next Phase**: Phase 2 - Graph Construction
**Status**: Ready to continue! 🚀
