# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python script that reads and parses GTFS Realtime protobuf feeds from Transport Victoria (PTV) for Melbourne metro train services. The script fetches real-time trip updates including arrival/departure times, delays, and stop sequence information.

## Environment Setup

**Virtual Environment**: The project uses a Python virtual environment in `venv/`

Activate the environment:
```bash
source venv/bin/activate
```

**Dependencies**:
- `gtfs-realtime-bindings` - Parses GTFS Realtime protobuf data
- `requests` - HTTP requests
- `protobuf` - Protocol buffer support

Install new dependencies:
```bash
venv/bin/pip install <package-name>
```

## API Authentication

**Required**: PTV API subscription key from https://opendata.transport.vic.gov.au/

Set via environment variable (recommended):
```bash
export PTV_API_KEY='your-api-key-here'
```

Or use command line argument: `--api-key 'your-key'`

**Authentication method**: API key passed via `Ocp-Apim-Subscription-Key` header

## Running the Script

Basic execution (shows 5 trip updates):
```bash
venv/bin/python read_gtfs_feed.py
```

Show specific number of updates:
```bash
venv/bin/python read_gtfs_feed.py --max-display 10
```

Show all updates:
```bash
venv/bin/python read_gtfs_feed.py --max-display 0
```

Use different feed URL:
```bash
venv/bin/python read_gtfs_feed.py --url 'https://api.opendata.transport.vic.gov.au/...'
```

## Architecture

**Single-file script** (`read_gtfs_feed.py`) with three main components:

1. **fetch_gtfs_feed()**: Handles HTTP request with API authentication and protobuf parsing
   - Uses `requests` library with `Ocp-Apim-Subscription-Key` header
   - Parses response using `gtfs_realtime_pb2.FeedMessage()`
   - Returns parsed feed object

2. **display_feed_header()**: Shows feed metadata
   - GTFS Realtime version
   - Timestamp
   - Entity count

3. **display_trip_update()**: Iterates through entities and formats output
   - Trip metadata (ID, route, direction, schedule)
   - Stop time updates with arrival/departure info and delays

**Data flow**: API endpoint → HTTP request → Protobuf parsing → Display functions

## API Endpoint

**Default URL**: `https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/metro/trip-updates`

**Rate limits**: 20-27 calls per minute, 30-second caching

**Data exclusions**: Train replacement buses, service deviations, platform details

## Key Data Structures

The script works with GTFS Realtime protobuf messages:
- `FeedMessage`: Top-level container with header and entities
- `FeedEntity`: Contains trip updates
- `TripUpdate`: Trip descriptor + stop time updates
- `StopTimeUpdate`: Per-stop arrival/departure predictions with delays

## Documentation

- PTV GTFS Realtime: https://opendata.transport.vic.gov.au/dataset/gtfs-realtime/resource/0010d606-47bf-4abb-a04f-63add63a4d23
- GTFS Realtime spec: https://developers.google.com/transit/gtfs-realtime
