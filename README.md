# PTV Assistant

A Python-based multi-modal journey planner for Melbourne's public transport network (trains, trams, and buses) using Public Transport Victoria's (PTV) GTFS datasets.

## 🚀 Project Status

**Current Phase**: Foundation (85% Complete)  
**Next Milestone**: Data Layer Implementation  
**Target**: MVP in 4 weeks, V1 in 8 weeks

## 📋 Overview

PTV Assistant finds optimal routes between stations using real-time and scheduled data from PTV's GTFS feeds. The system supports:

- 🚆 Metro trains
- 🚊 Trams
- 🚌 Metro & regional buses
- 🚂 V/Line regional trains

## 🎯 Current Capabilities

- ✅ Fetch real-time trip updates from PTV GTFS feeds
- ✅ Parse protocol buffer data
- ✅ Display arrival/departure predictions with delays
- ✅ Support for metro trains (initial implementation)

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

## 🗺️ Roadmap

| Phase | Timeline | Status |
|-------|----------|--------|
| Foundation | Week 1 | 85% ✅ |
| Data Layer | Week 2 | ⏳ |
| Single-Mode | Week 4 | ⏳ MVP |
| Multi-Modal | Week 6 | ⏳ |
| V1 Release | Week 8 | ⏳ |

## 📝 License

MIT License - Data from PTV under CC BY 4.0

## 🔗 Resources

- [PTV Open Data Portal](https://opendata.transport.vic.gov.au/)
- [GTFS Specification](https://gtfs.org/)

---

**Last Updated**: 2026-01-12
