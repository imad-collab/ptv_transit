"""
GTFS Static Data Parser

Parses GTFS static feed files (stops.txt, routes.txt, trips.txt, etc.)
and loads them into Python data structures.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional
import logging

from .models import Stop, Route, Trip, StopTime, Agency, Calendar, CalendarDate, Transfer

logger = logging.getLogger(__name__)


class GTFSParser:
    """Parser for GTFS static feed data."""

    def __init__(self, gtfs_dir: str):
        """
        Initialize GTFS parser.

        Args:
            gtfs_dir: Path to directory containing GTFS .txt files
        """
        self.gtfs_dir = Path(gtfs_dir)

        if not self.gtfs_dir.exists():
            raise FileNotFoundError(f"GTFS directory not found: {gtfs_dir}")

        self.stops: Dict[str, Stop] = {}
        self.routes: Dict[str, Route] = {}
        self.trips: Dict[str, Trip] = {}
        self.stop_times: Dict[str, List[StopTime]] = {}
        self.agencies: Dict[str, Agency] = {}
        self.calendars: Dict[str, Calendar] = {}
        self.calendar_dates: List[CalendarDate] = []
        self.transfers: List[Transfer] = []

    def load_all(self) -> 'GTFSParser':
        """
        Load all GTFS files.

        Returns:
            Self for method chaining
        """
        logger.info(f"Loading GTFS data from {self.gtfs_dir}")

        self.load_agencies()
        self.load_stops()
        self.load_routes()
        self.load_trips()
        self.load_stop_times()
        self.load_calendar()
        self.load_calendar_dates()
        self.load_transfers()

        logger.info(
            f"Loaded: {len(self.stops)} stops, {len(self.routes)} routes, "
            f"{len(self.trips)} trips, {len(self.stop_times)} trip schedules"
        )

        return self

    def load_agencies(self) -> None:
        """Load agency.txt file."""
        file_path = self.gtfs_dir / "agency.txt"

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                agency = Agency(**row)
                self.agencies[agency.agency_id] = agency

        logger.debug(f"Loaded {len(self.agencies)} agencies")

    def load_stops(self) -> None:
        """Load stops.txt file."""
        file_path = self.gtfs_dir / "stops.txt"

        if not file_path.exists():
            raise FileNotFoundError(f"Required file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Handle optional fields
                stop_data = {
                    'stop_id': row['stop_id'],
                    'stop_name': row['stop_name'],
                    'stop_lat': row['stop_lat'],
                    'stop_lon': row['stop_lon'],
                    'location_type': row.get('location_type', ''),
                    'parent_station': row.get('parent_station', ''),
                    'wheelchair_boarding': row.get('wheelchair_boarding', ''),
                    'stop_url': row.get('stop_url', ''),
                    'level_id': row.get('level_id', ''),
                    'platform_code': row.get('platform_code', ''),
                }
                stop = Stop(**stop_data)
                self.stops[stop.stop_id] = stop

        logger.debug(f"Loaded {len(self.stops)} stops")

    def load_routes(self) -> None:
        """Load routes.txt file."""
        file_path = self.gtfs_dir / "routes.txt"

        if not file_path.exists():
            raise FileNotFoundError(f"Required file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                route_data = {
                    'route_id': row['route_id'],
                    'route_short_name': row.get('route_short_name', ''),
                    'route_long_name': row.get('route_long_name', ''),
                    'route_type': row['route_type'],
                    'agency_id': row.get('agency_id', ''),
                    'route_desc': row.get('route_desc', ''),
                    'route_url': row.get('route_url', ''),
                    'route_color': row.get('route_color', ''),
                    'route_text_color': row.get('route_text_color', ''),
                }
                route = Route(**route_data)
                self.routes[route.route_id] = route

        logger.debug(f"Loaded {len(self.routes)} routes")

    def load_trips(self) -> None:
        """Load trips.txt file."""
        file_path = self.gtfs_dir / "trips.txt"

        if not file_path.exists():
            raise FileNotFoundError(f"Required file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                trip_data = {
                    'trip_id': row['trip_id'],
                    'route_id': row['route_id'],
                    'service_id': row['service_id'],
                    'trip_headsign': row.get('trip_headsign', ''),
                    'trip_short_name': row.get('trip_short_name', ''),
                    'direction_id': row.get('direction_id', ''),
                    'block_id': row.get('block_id', ''),
                    'shape_id': row.get('shape_id', ''),
                    'wheelchair_accessible': row.get('wheelchair_accessible', ''),
                    'bikes_allowed': row.get('bikes_allowed', ''),
                }
                trip = Trip(**trip_data)
                self.trips[trip.trip_id] = trip

        logger.debug(f"Loaded {len(self.trips)} trips")

    def load_stop_times(self) -> None:
        """Load stop_times.txt file."""
        file_path = self.gtfs_dir / "stop_times.txt"

        if not file_path.exists():
            raise FileNotFoundError(f"Required file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stop_time_data = {
                    'trip_id': row['trip_id'],
                    'stop_id': row['stop_id'],
                    'stop_sequence': row['stop_sequence'],
                    'arrival_time': row['arrival_time'],
                    'departure_time': row['departure_time'],
                    'stop_headsign': row.get('stop_headsign', ''),
                    'pickup_type': row.get('pickup_type', '0'),
                    'drop_off_type': row.get('drop_off_type', '0'),
                    'shape_dist_traveled': row.get('shape_dist_traveled', ''),
                    'timepoint': row.get('timepoint', ''),
                }
                stop_time = StopTime(**stop_time_data)

                if stop_time.trip_id not in self.stop_times:
                    self.stop_times[stop_time.trip_id] = []

                self.stop_times[stop_time.trip_id].append(stop_time)

        # Sort stop times by sequence
        for trip_id in self.stop_times:
            self.stop_times[trip_id].sort(key=lambda st: st.stop_sequence)

        logger.debug(f"Loaded stop times for {len(self.stop_times)} trips")

    def load_calendar(self) -> None:
        """Load calendar.txt file."""
        file_path = self.gtfs_dir / "calendar.txt"

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                calendar = Calendar(**row)
                self.calendars[calendar.service_id] = calendar

        logger.debug(f"Loaded {len(self.calendars)} calendar entries")

    def load_calendar_dates(self) -> None:
        """Load calendar_dates.txt file."""
        file_path = self.gtfs_dir / "calendar_dates.txt"

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                calendar_date = CalendarDate(**row)
                self.calendar_dates.append(calendar_date)

        logger.debug(f"Loaded {len(self.calendar_dates)} calendar date exceptions")

    def load_transfers(self) -> None:
        """Load transfers.txt file."""
        file_path = self.gtfs_dir / "transfers.txt"

        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                transfer_data = {
                    'from_stop_id': row['from_stop_id'],
                    'to_stop_id': row['to_stop_id'],
                    'transfer_type': row.get('transfer_type', '0'),
                    'min_transfer_time': row.get('min_transfer_time', ''),
                }
                transfer = Transfer(**transfer_data)
                self.transfers.append(transfer)

        logger.debug(f"Loaded {len(self.transfers)} transfers")

    def get_stop(self, stop_id: str) -> Optional[Stop]:
        """Get a stop by ID."""
        return self.stops.get(stop_id)

    def get_route(self, route_id: str) -> Optional[Route]:
        """Get a route by ID."""
        return self.routes.get(route_id)

    def get_trip(self, trip_id: str) -> Optional[Trip]:
        """Get a trip by ID."""
        return self.trips.get(trip_id)

    def get_trip_stop_times(self, trip_id: str) -> List[StopTime]:
        """Get all stop times for a trip, sorted by sequence."""
        return self.stop_times.get(trip_id, [])
