"""
Data models for GTFS entities.

These dataclasses represent GTFS static data structures.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Stop:
    """Represents a transit stop/station."""

    stop_id: str
    stop_name: str
    stop_lat: float
    stop_lon: float
    location_type: str = ""
    parent_station: str = ""
    wheelchair_boarding: str = ""
    stop_url: str = ""
    level_id: str = ""
    platform_code: str = ""

    def __post_init__(self):
        """Validate and convert types."""
        self.stop_lat = float(self.stop_lat)
        self.stop_lon = float(self.stop_lon)


@dataclass
class Route:
    """Represents a transit route (train line, bus route, etc.)."""

    route_id: str
    route_short_name: str
    route_long_name: str
    route_type: str
    agency_id: str = ""
    route_desc: str = ""
    route_url: str = ""
    route_color: str = ""
    route_text_color: str = ""


@dataclass
class Trip:
    """Represents a single trip (service run)."""

    trip_id: str
    route_id: str
    service_id: str
    trip_headsign: str = ""
    trip_short_name: str = ""
    direction_id: str = ""
    block_id: str = ""
    shape_id: str = ""
    wheelchair_accessible: str = ""
    bikes_allowed: str = ""


@dataclass
class StopTime:
    """Represents a scheduled stop time for a trip."""

    trip_id: str
    stop_id: str
    stop_sequence: int
    arrival_time: str
    departure_time: str
    stop_headsign: str = ""
    pickup_type: str = "0"
    drop_off_type: str = "0"
    shape_dist_traveled: str = ""
    timepoint: str = ""

    def __post_init__(self):
        """Validate and convert types."""
        self.stop_sequence = int(self.stop_sequence)


@dataclass
class Agency:
    """Represents a transit agency."""

    agency_id: str
    agency_name: str
    agency_url: str
    agency_timezone: str
    agency_lang: str = ""
    agency_phone: str = ""
    agency_fare_url: str = ""


@dataclass
class Calendar:
    """Represents service calendar (which days a service runs)."""

    service_id: str
    monday: str
    tuesday: str
    wednesday: str
    thursday: str
    friday: str
    saturday: str
    sunday: str
    start_date: str
    end_date: str


@dataclass
class CalendarDate:
    """Represents service calendar exceptions."""

    service_id: str
    date: str
    exception_type: str


@dataclass
class Transfer:
    """Represents a transfer between stops."""

    from_stop_id: str
    to_stop_id: str
    transfer_type: str = "0"
    min_transfer_time: str = ""
