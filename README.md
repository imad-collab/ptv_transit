# PTV Assistant

A Python-based multi-modal journey planner for Melbourne's public transport network (trains, trams, and buses) using Public Transport Victoria's (PTV) GTFS datasets.

## 🚀 Project Status

**Current Phase**: Phase 2 Complete ✅
**Next Milestone**: Phase 3 - Single-Mode Routing
**Progress**: 3/8 phases complete (38%)

## 📋 Overview

PTV Assistant finds optimal routes between stations using real-time and scheduled data from PTV's GTFS feeds. The system supports:

- 🚆 Metro trains
- 🚊 Trams
- 🚌 Metro & regional buses
- 🚂 V/Line regional trains

## 🎯 Current Capabilities

### Phase 0: Foundation ✅
- ✅ Fetch real-time trip updates from PTV GTFS feeds
- ✅ Parse protocol buffer data
- ✅ Display arrival/departure predictions with delays
- ✅ 21 tests, 100% test coverage

### Phase 1: Data Layer ✅
- ✅ Parse GTFS static data (stops, routes, trips, schedules)
- ✅ Type-safe data models for all GTFS entities
- ✅ Fast stop lookup with fuzzy name matching
- ✅ Extracted V/Line GTFS (497 stops, 13 routes, 8,096 trips)
- ✅ 62 tests, 97% test coverage
- ✅ Successfully query trips between stations (e.g., Tarneit to Waurn Ponds)

### Phase 2: Graph Construction ✅
- ✅ Build transit network graph with NetworkX
- ✅ Nodes for stops with metadata (name, coordinates)
- ✅ Edges for connections with travel times
- ✅ Support for trip connections and transfers
- ✅ Query methods (neighbors, travel times, routes, connections)
- ✅ 36 tests, 95% test coverage

## 🚦 Quick Start

### Prerequisites

- Python 3.9+
- PTV API key from [PTV Open Data Portal](https://opendata.transport.vic.gov.au/)

### Installation

1. Clone the repository
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file with your `PTV_API_KEY`

### Usage

```bash
# Show 5 trip updates
python read_gtfs_feed.py

# Show 10 trip updates
python read_gtfs_feed.py --max-display 10
```

## 📚 Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and components
- **[FEASIBILITY.md](docs/FEASIBILITY.md)** - Feasibility analysis (9/10 score)
- **[ROADMAP.md](docs/ROADMAP.md)** - Week-by-week implementation plan
- **[DATA_SOURCES.md](docs/DATA_SOURCES.md)** - Complete GTFS data reference
- **[CHECKPOINT.md](docs/CHECKPOINT.md)** - Current project status

## 🗺️ Development Roadmap

| Phase | Description | Status | Tests | Coverage |
|-------|-------------|--------|-------|----------|
| Phase 0 | Foundation - Realtime GTFS Feed | ✅ Complete | 21 | 100% |
| Phase 1 | Data Layer - GTFS Parser & Models | ✅ Complete | 62 | 97% |
| Phase 2 | Graph Construction - Transit Network | ✅ Complete | 36 | 95% |
| Phase 3 | Single-Mode Routing - CSA Algorithm | ⏳ Not Started | - | - |
| Phase 4 | Multi-Modal Routing | ⏳ Not Started | - | - |
| Phase 5 | Realtime Integration | ⏳ Not Started | - | - |
| Phase 6 | Web API & CLI | ⏳ Not Started | - | - |
| Phase 7 | Performance Optimization | ⏳ Not Started | - | - |

**Total**: 119 tests passing, 97% overall coverage

## 📝 License

MIT License - Data from PTV under CC BY 4.0

## 🔗 Resources

- [PTV Open Data Portal](https://opendata.transport.vic.gov.au/)
- [GTFS Specification](https://gtfs.org/)

---

**Last Updated**: 2026-01-13
**Repository**: https://github.com/imad-collab/ptv_transit
