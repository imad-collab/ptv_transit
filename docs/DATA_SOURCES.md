# PTV Data Sources Reference

## Overview

This document catalogs all data sources available from Public Transport Victoria (PTV) for building the multi-modal journey planner.

---

## 1. Static GTFS Schedule Dataset

### Basic Information

| Property | Value |
|----------|-------|
| **Name** | GTFS Schedule |
| **Publisher** | Transport Victoria |
| **URL** | https://opendata.transport.vic.gov.au/dataset/gtfs-schedule |
| **Format** | ZIP archive containing CSV files |
| **Size** | 242.44 MB (compressed) |
| **License** | Creative Commons Attribution 4.0 International |
| **Update Frequency** | Weekly or as-needed |
| **Coverage** | Rolling 30-day window from export date |
| **Authentication** | None (public download) |

### Download Links

**Direct Download**:
```bash
# Visit the page and download the latest ZIP
https://opendata.transport.vic.gov.au/dataset/gtfs-schedule

# Or use wget/curl (check for latest URL)
wget https://opendata.transport.vic.gov.au/dataset/.../download/gtfs.zip
```

### Transport Modes Covered

- ✅ Metropolitan trains (all lines)
- ✅ Yarra trams (all routes)
- ✅ Metropolitan buses
- ✅ Regional buses (including coaches)
- ✅ V/Line regional trains

### File Structure

The ZIP archive contains the following GTFS files:

#### Core Files (Required)

| File | Description | Key Fields |
|------|-------------|------------|
| `agency.txt` | Transit agencies | `agency_id`, `agency_name`, `agency_url` |
| `stops.txt` | Stop/station locations | `stop_id`, `stop_name`, `stop_lat`, `stop_lon`, `parent_station` |
| `routes.txt` | Transit routes | `route_id`, `route_short_name`, `route_long_name`, `route_type` |
| `trips.txt` | Individual trips | `trip_id`, `route_id`, `service_id`, `trip_headsign` |
| `stop_times.txt` | Stop times for each trip | `trip_id`, `stop_id`, `arrival_time`, `departure_time`, `stop_sequence` |
| `calendar.txt` | Service schedules | `service_id`, `monday`...`sunday`, `start_date`, `end_date` |

#### Optional Files (Available)

| File | Description | Key Fields |
|------|-------------|------------|
| `calendar_dates.txt` | Service exceptions | `service_id`, `date`, `exception_type` |
| `transfers.txt` | Transfer points | `from_stop_id`, `to_stop_id`, `transfer_type`, `min_transfer_time` |
| `pathways.txt` | Walking paths in stations | `pathway_id`, `from_stop_id`, `to_stop_id`, `traversal_time` |
| `levels.txt` | Station levels | `level_id`, `level_index`, `level_name` |
| `shapes.txt` | Route geometry | `shape_id`, `shape_pt_lat`, `shape_pt_lon`, `shape_pt_sequence` |

### Enhanced Features

**PTV-Specific Additions**:
1. **Platform Numbers**: Metro train stations include platform codes
2. **Parent Stations**: Multi-platform stops grouped under parent station
3. **Bus Replacement Stops**: Dedicated stop records for train replacement buses
4. **Wheelchair Accessibility**:
   - `wheelchair_accessible` in `trips.txt`
   - `wheelchair_boarding` in `stops.txt`
5. **Pathway Navigation**: Detailed walking paths with traversal times

### Data Quality Notes

**Strengths**:
- Comprehensive coverage of all PTV services
- Regular updates (weekly)
- Standard GTFS format (widely compatible)
- Good spatial accuracy (lat/lon coordinates)

**Limitations**:
- Excludes train replacement buses (separate records)
- No fare information included
- Service deviations not in static data
- Platform details may be incomplete for some modes

### Schema Details

#### `stops.txt` Schema
```csv
stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station,wheelchair_boarding,platform_code,level_id
19854,Flinders Street Station,-37.8183,144.9671,1,,,
19854-1,Flinders Street Station Platform 1,-37.8183,144.9671,0,19854,1,1,
```

- `location_type`: 0=stop, 1=station, 2=entrance, 3=node, 4=boarding area
- `wheelchair_boarding`: 0=unknown, 1=accessible, 2=not accessible

#### `stop_times.txt` Schema
```csv
trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type,drop_off_type
02-PKM--28-T5-C068,12:23:00,12:23:00,11217,1,0,0
02-PKM--28-T5-C068,12:26:00,12:26:00,22191,2,0,0
```

- Times can exceed 24:00:00 for services after midnight (e.g., 25:30:00 = 1:30 AM)
- `stop_sequence`: Order of stops on trip

#### `routes.txt` Schema
```csv
route_id,route_short_name,route_long_name,route_type
aus:vic:vic-02-PKM:,Pakenham,Flinders Street to Pakenham,1
```

- `route_type`: 0=tram, 1=metro, 2=rail, 3=bus (GTFS standard)

### Usage Examples

```python
import pandas as pd
import zipfile

# Extract GTFS files
with zipfile.ZipFile('gtfs.zip', 'r') as zip_ref:
    zip_ref.extractall('gtfs/')

# Load stops
stops = pd.read_csv('gtfs/stops.txt')
print(f"Total stops: {len(stops)}")

# Find Flinders Street
flinders = stops[stops['stop_name'].str.contains('Flinders Street')]
print(flinders[['stop_id', 'stop_name', 'stop_lat', 'stop_lon']])

# Load routes
routes = pd.read_csv('gtfs/routes.txt')
train_routes = routes[routes['route_type'] == 1]  # Trains only
print(f"Train routes: {len(train_routes)}")
```

---

## 2. GTFS Realtime Feeds

### Basic Information

| Property | Value |
|----------|-------|
| **Name** | GTFS Realtime |
| **Publisher** | Transport Victoria |
| **URL** | https://opendata.transport.vic.gov.au/dataset/gtfs-realtime |
| **Format** | Protocol Buffers (binary) |
| **Specification** | GTFS Realtime v2.0 |
| **License** | Creative Commons Attribution 4.0 |
| **Authentication** | API Key via `KeyID` header |
| **Rate Limit** | 24 requests / 60 seconds per service type |
| **Update Frequency** | 30-60 seconds (varies by mode) |
| **Caching** | 30 seconds server-side |

### Available Feeds

#### Metro Train Feeds

| Feed Type | Endpoint | Data Provided |
|-----------|----------|---------------|
| Trip Updates | `https://opendata.transport.vic.gov.au/...metro/trip-updates` | Delays, predictions |
| Vehicle Positions | `https://opendata.transport.vic.gov.au/...metro/vehicle-positions` | Vehicle locations |
| Service Alerts | `https://opendata.transport.vic.gov.au/...metro/service-alerts` | Disruptions |

**Refresh Rate**: Near real-time (~1-2 seconds)

#### Yarra Trams Feeds

| Feed Type | Endpoint | Data Provided |
|-----------|----------|---------------|
| Trip Updates | `https://opendata.transport.vic.gov.au/...tram/trip-updates` | Delays, predictions |
| Vehicle Positions | `https://opendata.transport.vic.gov.au/...tram/vehicle-positions` | Vehicle locations |
| Service Alerts | `https://opendata.transport.vic.gov.au/...tram/service-alerts` | Disruptions |

**Refresh Rate**: Every 60 seconds

#### Metro & Regional Bus Feeds

| Feed Type | Endpoint | Data Provided |
|-----------|----------|---------------|
| Trip Updates | `https://opendata.transport.vic.gov.au/...bus/trip-updates` | Delays, predictions |
| Vehicle Positions | `https://opendata.transport.vic.gov.au/...bus/vehicle-positions` | Vehicle locations |

**Refresh Rate**: Near real-time
**Note**: No service alerts feed for buses

#### V/Line Regional Train Feeds

| Feed Type | Endpoint | Data Provided |
|-----------|----------|---------------|
| Trip Updates | `https://opendata.transport.vic.gov.au/...vline/trip-updates` | Delays, predictions |
| Vehicle Positions | `https://opendata.transport.vic.gov.au/...vline/vehicle-positions` | Vehicle locations |

**Refresh Rate**: Varies
**Note**: No service alerts feed for V/Line

### Authentication

**Header Name**: `KeyID`
**Header Value**: Your PTV API key

**Example Request**:
```python
import requests

headers = {'KeyID': 'your-api-key-here'}
url = 'https://opendata.transport.vic.gov.au/.../metro/trip-updates'

response = requests.get(url, headers=headers)
```

**Obtaining API Key**:
1. Register at https://opendata.transport.vic.gov.au/
2. Navigate to your account settings
3. Generate API key
4. Store securely (not in code!)

### Rate Limiting

**Limits**:
- 24 requests per 60 seconds per service type
- Applies to each feed type separately
- Server-side caching: 30 seconds

**Best Practices**:
```python
# Poll each feed every 30-60 seconds
# Cache responses client-side
# Use exponential backoff on errors

import time
from collections import deque

class RateLimiter:
    def __init__(self):
        self.calls = deque(maxlen=24)

    def wait_if_needed(self):
        now = time.time()
        if len(self.calls) == 24:
            elapsed = now - self.calls[0]
            if elapsed < 60:
                time.sleep(60 - elapsed)
        self.calls.append(now)
```

### Feed Data Structures

#### Trip Updates Feed

**Protocol Buffer Structure**:
```protobuf
message FeedMessage {
  FeedHeader header = 1;
  repeated FeedEntity entity = 2;
}

message FeedEntity {
  required string id = 1;
  TripUpdate trip_update = 2;
}

message TripUpdate {
  TripDescriptor trip = 1;
  repeated StopTimeUpdate stop_time_update = 2;
}

message StopTimeUpdate {
  uint32 stop_sequence = 1;
  string stop_id = 2;
  StopTimeEvent arrival = 3;
  StopTimeEvent departure = 4;
}

message StopTimeEvent {
  int64 time = 1;      // Unix timestamp
  int32 delay = 2;     // Delay in seconds
}
```

**Example Data**:
```python
# Trip Update
entity.id = "02-PKM--28-T5-C068"
trip_update.trip.trip_id = "02-PKM--28-T5-C068"
trip_update.trip.route_id = "aus:vic:vic-02-PKM:"

# Stop time update
stop_time_update.stop_id = "11217"
stop_time_update.stop_sequence = 29
stop_time_update.arrival.time = 1768186092  # Unix timestamp
stop_time_update.arrival.delay = 120  # 2 minutes late
```

**Key Fields**:
- `trip_id`: Links to static GTFS `trips.txt`
- `route_id`: Links to static GTFS `routes.txt`
- `stop_id`: Links to static GTFS `stops.txt`
- `time`: Predicted arrival/departure time (Unix timestamp)
- `delay`: Delay in seconds (positive = late, negative = early)
- `schedule_relationship`: 0=SCHEDULED, 1=ADDED, 2=UNSCHEDULED, 3=CANCELED

#### Vehicle Positions Feed

**Structure**:
```protobuf
message VehiclePosition {
  TripDescriptor trip = 1;
  Position position = 2;
  uint32 current_stop_sequence = 3;
  string current_status = 4;
  uint64 timestamp = 5;
}

message Position {
  required float latitude = 1;
  required float longitude = 2;
}
```

**Use Cases**:
- Track vehicle locations in real-time
- Estimate time to next stop
- Visualize fleet on map

#### Service Alerts Feed

**Structure**:
```protobuf
message Alert {
  repeated TimeRange active_period = 1;
  repeated EntitySelector informed_entity = 2;
  Cause cause = 3;
  Effect effect = 4;
  TranslatedString header_text = 5;
  TranslatedString description_text = 6;
}

message EntitySelector {
  string agency_id = 1;
  string route_id = 2;
  int32 route_type = 3;
  TripDescriptor trip = 4;
  string stop_id = 5;
}
```

**Alert Types**:
- Planned maintenance
- Unplanned disruptions
- Service diversions
- Platform changes

### Recent Enhancements (2025-2026)

**Metro Train Feeds**:
1. **Trip Updates**: Added `schedule_relationship`, `route_id`
2. **Vehicle Positions**: Added conditional `route_id`
3. **Service Alerts**: Added planned/unplanned classification, `route_id`, `direction_id`

### Usage Examples

#### Fetch Trip Updates
```python
import requests
from google.transit import gtfs_realtime_pb2

def fetch_trip_updates(api_key):
    url = 'https://opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/metro/trip-updates'
    headers = {'KeyID': api_key}

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    for entity in feed.entity:
        if entity.HasField('trip_update'):
            print(f"Trip: {entity.trip_update.trip.trip_id}")
            for stu in entity.trip_update.stop_time_update:
                if stu.HasField('arrival'):
                    print(f"  Stop {stu.stop_id}: Delay {stu.arrival.delay}s")
```

#### Check for Cancellations
```python
def is_trip_cancelled(feed, trip_id):
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            if entity.trip_update.trip.trip_id == trip_id:
                if entity.trip_update.trip.schedule_relationship == 3:  # CANCELED
                    return True
    return False
```

---

## 3. OpenAPI Specifications

### Available Specs

Each realtime feed has a downloadable OpenAPI specification (JSON format):

| Feed | Spec Size | URL |
|------|-----------|-----|
| Metro Train Trip Updates | 2.06 KB | Download from dataset page |
| Metro Train Vehicle Positions | 2.46 KB | Download from dataset page |
| Metro Train Service Alerts | ~2 KB | Download from dataset page |
| Trams (all feeds) | ~2 KB each | Download from dataset page |
| Bus (all feeds) | ~2 KB each | Download from dataset page |

**Usage**:
```bash
# Download OpenAPI spec
wget https://opendata.transport.vic.gov.au/.../gtfsr_metro_train_trip_updates.openapi.json

# Generate Python client (optional)
openapi-generator generate -i spec.json -g python -o client/
```

---

## 4. PTV Timetable API (Alternative)

**Note**: This is a separate, official PTV API that might be easier to use than building from GTFS.

### Basic Information

| Property | Value |
|----------|-------|
| **Name** | PTV Timetable API v3 |
| **URL** | https://timetableapi.ptv.vic.gov.au/ |
| **Documentation** | https://www.ptv.vic.gov.au/footer/data-and-reporting/datasets/ptv-timetable-api/ |
| **Format** | REST API (JSON) |
| **Authentication** | HMAC signature (devid + key) |
| **Rate Limits** | Undocumented (likely generous) |
| **License** | Free for non-commercial use |

### Available Endpoints

- `/v3/departures/route_type/{route_type}/stop/{stop_id}`
- `/v3/directions/route/{route_id}`
- `/v3/routes`
- `/v3/stops/route/{route_id}/route_type/{route_type}`
- `/v3/search/{search_term}`

### Use Cases

**When to Use PTV API**:
- Need quick journey planning without building from scratch
- Don't need offline capability
- Commercial use (check terms)
- Prototype/MVP

**When to Use GTFS**:
- Full control over routing algorithm
- Custom optimization criteria
- Academic research
- Offline operation
- Want to learn transit routing

---

## 5. Data Validity & Updates

### Static GTFS

**Current Validity** (as of January 2026):
- Valid from: December 19, 2025
- Valid until: March 22, 2026
- Rolling 30-day window from export

**Update Schedule**:
- Frequency: Weekly or as-needed
- Trigger: Timetable changes, new services
- Notification: Check dataset page for update timestamp

**Automated Updates**:
```bash
#!/bin/bash
# scripts/update_gtfs.sh

# Download latest GTFS
wget -O gtfs_new.zip https://opendata.transport.vic.gov.au/.../gtfs.zip

# Validate
unzip -t gtfs_new.zip

# Backup old
mv gtfs.zip gtfs_backup.zip

# Replace
mv gtfs_new.zip gtfs.zip

# Restart service
systemctl restart journey-planner
```

**Cron Job** (weekly updates):
```cron
0 2 * * 0 /path/to/update_gtfs.sh
```

### Realtime Feeds

**Freshness**:
- Server caching: 30 seconds
- Recommend polling: 30-60 seconds
- No point polling faster than 30s

**Monitoring**:
```python
# Check feed timestamp
feed_timestamp = datetime.fromtimestamp(feed.header.timestamp)
age = datetime.now() - feed_timestamp

if age.total_seconds() > 120:  # 2 minutes
    print(f"Warning: Feed is {age.total_seconds()}s old")
```

---

## 6. Data License & Attribution

### License

**Creative Commons Attribution 4.0 International (CC BY 4.0)**

**You are free to**:
- ✅ Share — copy and redistribute
- ✅ Adapt — remix, transform, build upon
- ✅ Commercial use allowed

**Under these terms**:
- ⚠️ Attribution required — must give credit to Transport Victoria
- ⚠️ Indicate changes made

### Required Attribution

**Suggested attribution**:
```
Data provided by Public Transport Victoria under Creative Commons
Attribution 4.0 International license.
Source: https://opendata.transport.vic.gov.au/
```

**In code**:
```python
# In API responses
{
    "journeys": [...],
    "attribution": "Data © Public Transport Victoria",
    "license": "CC BY 4.0",
    "source": "https://opendata.transport.vic.gov.au/"
}
```

---

## 7. Data Quality & Known Issues

### Known Limitations

1. **Platform Changes**:
   - Real-time platform changes not always available
   - Static platform codes may be outdated

2. **Bus Alerts**:
   - No service alerts feed for buses
   - Must infer disruptions from trip updates

3. **V/Line Coverage**:
   - Less detailed than metro services
   - Fewer realtime updates

4. **Transfer Times**:
   - `transfers.txt` may not cover all scenarios
   - Need fallback heuristics (e.g., 5 min default)

5. **Service Exceptions**:
   - Holiday schedules in `calendar_dates.txt`
   - Check before major holidays

### Data Validation Checks

```python
def validate_gtfs(gtfs_path):
    """Run validation checks on GTFS data"""
    checks = {
        'stops_have_coords': len(stops[stops['stop_lat'].isna()]) == 0,
        'trips_have_routes': len(trips[trips['route_id'].isna()]) == 0,
        'stop_times_sequential': check_stop_sequence_order(),
        'no_negative_times': check_no_negative_times(),
        'calendars_valid': check_calendar_dates(),
    }
    return all(checks.values())
```

---

## 8. Reference Links

### Official Documentation

- **GTFS Specification**: https://gtfs.org/
- **GTFS Realtime Spec**: https://gtfs.org/realtime/
- **PTV Open Data Portal**: https://opendata.transport.vic.gov.au/
- **PTV Timetable API**: https://www.ptv.vic.gov.au/footer/data-and-reporting/datasets/ptv-timetable-api/

### Third-Party Tools

- **GTFS Validator**: https://github.com/MobilityData/gtfs-validator
- **Transitland**: https://www.transit.land/feeds/f-r1r-ptv
- **GTFS-kit Documentation**: https://mrcagney.github.io/gtfs_kit_docs/

### Academic Resources

- **Connection Scan Algorithm**: https://arxiv.org/abs/1703.05997
- **RAPTOR Algorithm**: https://www.microsoft.com/en-us/research/publication/round-based-public-transit-routing/

---

## 9. Quick Reference

### File Sizes

| Dataset | Compressed | Uncompressed |
|---------|------------|--------------|
| Static GTFS | 242 MB | ~600 MB |
| Realtime feed response | ~50-200 KB | ~100-400 KB |

### Record Counts (Approximate)

| File | Records |
|------|---------|
| `stops.txt` | ~22,000+ |
| `routes.txt` | ~500-1000 |
| `trips.txt` | ~50,000-100,000 |
| `stop_times.txt` | ~2,000,000+ |

### Endpoint Summary

```
Static GTFS:
  https://opendata.transport.vic.gov.au/dataset/gtfs-schedule

Realtime Metro Train:
  Trip Updates:       /gtfs/realtime/v1/metro/trip-updates
  Vehicle Positions:  /gtfs/realtime/v1/metro/vehicle-positions
  Service Alerts:     /gtfs/realtime/v1/metro/service-alerts

Realtime Trams:
  Trip Updates:       /gtfs/realtime/v1/tram/trip-updates
  Vehicle Positions:  /gtfs/realtime/v1/tram/vehicle-positions
  Service Alerts:     /gtfs/realtime/v1/tram/service-alerts

Realtime Bus:
  Trip Updates:       /gtfs/realtime/v1/bus/trip-updates
  Vehicle Positions:  /gtfs/realtime/v1/bus/vehicle-positions
```

### API Key Storage

```bash
# .env file
PTV_API_KEY=your-api-key-here

# Load in Python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('PTV_API_KEY')
```

---

## Appendix: Data Dictionary

### Route Types (GTFS Standard)

| Value | Mode | PTV Example |
|-------|------|-------------|
| 0 | Tram, Streetcar, Light rail | Yarra Trams |
| 1 | Subway, Metro | Metro Trains |
| 2 | Rail | V/Line trains |
| 3 | Bus | Metro/Regional buses |
| 4 | Ferry | N/A (not in Melbourne) |

### Schedule Relationship Values

| Value | Name | Meaning |
|-------|------|---------|
| 0 | SCHEDULED | Trip runs as scheduled |
| 1 | ADDED | Extra trip not in schedule |
| 2 | UNSCHEDULED | Unscheduled trip |
| 3 | CANCELED | Scheduled trip cancelled |

### Location Types (stops.txt)

| Value | Type | Description |
|-------|------|-------------|
| 0 | Stop | Physical stop/platform |
| 1 | Station | Parent station (grouping) |
| 2 | Entrance/Exit | Station entrance |
| 3 | Generic Node | Pathway node |
| 4 | Boarding Area | Specific boarding location |
