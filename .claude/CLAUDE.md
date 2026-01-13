# PTV Transit Assistant - Claude Code Context

This file provides guidance to Claude Code when working with this repository.

---

## 🔄 HANDOFF PROTOCOL (CRITICAL - READ FIRST)

This project uses **12-hour rotating shifts** between two developers across timezones.

### Team Configuration
| Developer | Subscription | Timezone | GitHub |
|-----------|--------------|----------|--------|
| **Gaurav** | Claude Pro Max | Melbourne (AEST/AEDT) | @gauravcaprihan |
| **Imad** | Claude Pro | [Timezone TBD] | @imad-collab |

### Mandatory Workflow

**START OF EVERY SESSION:**
```
1. git pull origin main
2. Run: /catchup
3. Run: /status (optional - quick check)
4. Continue work from handoff context
```

**END OF EVERY SESSION:**
```
1. Run: /handoff
2. Review generated handoff document
3. git add . && git commit -m "Handoff: [date] [your-name]"
4. git push origin main
```

### Handoff Files Location
- **Current handoff**: `.claude/handoffs/CURRENT-HANDOFF.md`
- **Archive**: `.claude/handoffs/archive/` (auto-archived by /handoff)

---

## Project Overview

A Python-based multi-modal journey planner for Melbourne's public transport network using PTV's GTFS datasets.

**Repository**: https://github.com/imad-collab/ptv_transit
**Branch**: main

### Current Status (Update after each phase)
- **Phase 0**: ✅ Foundation Complete (21 tests, 100% coverage)
- **Phase 1**: ✅ Data Layer Complete (62 tests, 97% coverage)
- **Phase 2**: ⏳ Graph Construction (NOT STARTED)
- **Total Tests**: 83 | **Overall Coverage**: 98%

---

## Environment Setup

### Virtual Environment
```bash
source venv/bin/activate
# or
source .venv/bin/activate
```

### Python Version
- Required: Python 3.9+
- Current: Python 3.13.5

### Key Dependencies
```bash
# Production
pip install requests protobuf gtfs-realtime-bindings pandas fuzzywuzzy python-Levenshtein

# Development
pip install pytest pytest-cov pytest-mock requests-mock
```

### PTV API Key
- **Required for**: Real-time feed fetcher
- **Get from**: https://opendata.transport.vic.gov.au/
- **Set via**: `export PTV_API_KEY='your-key-here'` or `.env` file

---

## Common Commands

### Testing
```bash
pytest                                      # Run all tests
pytest tests/test_data/ -v                  # Phase 1 tests
pytest tests/test_realtime/ -v              # Phase 0 tests
pytest --cov=src --cov-report=term-missing  # With coverage
```

### Git Operations
```bash
git status
git log --oneline -5
git add .
git commit -m "message"
git push origin main
git pull origin main
```

### Running the Application
```bash
python read_gtfs_feed.py                    # Real-time feed viewer
python read_gtfs_feed.py --max-display 10   # Show 10 updates
```

---

## Project Structure

```
ptv_transit/
├── src/
│   ├── data/           ✅ Complete - GTFS parser, models, stop index
│   ├── realtime/       ✅ Complete - Feed fetcher
│   ├── graph/          ⏳ Phase 2 - Transit network graph
│   ├── routing/        ⏳ Phase 3 - Routing algorithms
│   ├── api/            ⏳ Phase 6 - Web API
│   └── cli/            ⏳ Phase 6 - CLI interface
├── tests/
│   ├── test_data/      ✅ 62 tests
│   └── test_realtime/  ✅ 21 tests
├── data/
│   └── gtfs/           ✅ V/Line data (497 stops, 13 routes, 8,096 trips)
├── docs/               ✅ Documentation
└── .claude/
    ├── CLAUDE.md       # This file
    ├── commands/       # Custom slash commands
    └── handoffs/       # Shift handoff documents
```

---

## Key Files Reference

### Source Code
| File | Purpose |
|------|---------|
| `src/data/models.py` | GTFS dataclasses (Stop, Route, Trip, StopTime) |
| `src/data/gtfs_parser.py` | CSV parser for GTFS files |
| `src/data/stop_index.py` | Fast stop lookup with fuzzy matching |
| `src/realtime/feed_fetcher.py` | Real-time GTFS feed fetcher |

### Documentation
| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `DEVELOPMENT_STATUS.md` | Detailed progress report |
| `CONTEXT.md` | Resume context (legacy - use handoffs instead) |

### Test Fixtures
- Location: `tests/test_data/fixtures/`
- Files: 8 sample GTFS CSV files
- Encoding: UTF-8 with BOM

---

## Architecture Decisions

### GTFS Data Extraction
- **Current**: V/Line regional trains only (route_type=1)
- **Reason**: Full extraction (metro, tram, bus) had 17M rows - performance issues
- **Data**: 497 stops, 13 routes, 8,096 trips
- **Future**: Extract all modes for full Melbourne network

### Test Philosophy
- **Target**: 95%+ coverage on all new code
- **Approach**: Test-driven development
- **Fixtures**: Minimal sample data for fast tests

### Fuzzy Matching
- **Library**: fuzzywuzzy with python-Levenshtein
- **Scorer**: `token_sort_ratio` (handles word order)
- **Threshold**: 60% similarity default

---

## Sample Data for Testing

### Stations
| Station | stop_id | Coordinates |
|---------|---------|-------------|
| Tarneit Station | 47648 | -37.832, 144.694 |
| Waurn Ponds Station | 47641 | -38.216, 144.306 |

### Example Query Result
- "Tarneit to Waurn Ponds" → 1,989 trips found
- Sample trip: Departs 14:57, arrives 15:48 (51 min)

---

## Code Style Guidelines

- **PEP 8**: Follow Python style guide
- **Type Hints**: Use throughout data models
- **Docstrings**: Comprehensive documentation
- **Error Handling**: Defensive programming with clear messages
- **Commits**: Use conventional commit messages

---

## Phase 2 Implementation Notes (NEXT)

**Goal**: Build transit network graph using NetworkX

**Tasks**:
1. Install: `pip install networkx`
2. Create: `src/graph/transit_graph.py`
3. Implement `TransitGraph` class:
   - Nodes: Stops with metadata
   - Edges: Stop-to-stop connections with travel times
   - Handle transfers from transfers.txt
4. Tests: `tests/test_graph/test_transit_graph.py`
5. Target: 95%+ test coverage

**Success Criteria**:
- Graph built from 497 V/Line stops
- Query: "What stops connect to Tarneit?"
- Retrieve: "Travel time from Tarneit to next stop?"

---

## Important Reminders

1. **Always read handoff first**: `/catchup` at session start
2. **Always create handoff last**: `/handoff` at session end
3. **Commit frequently**: Small, atomic commits with clear messages
4. **Push before shift end**: Don't leave uncommitted work
5. **Test coverage**: Maintain 95%+ on new code
6. **Documentation**: Update DEVELOPMENT_STATUS.md after major changes

---

*Last Updated: 2026-01-14*
*Next Phase: Phase 2 - Graph Construction*
