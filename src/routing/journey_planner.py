"""
Journey planning using Connection Scan Algorithm (CSA).

This module implements the Connection Scan Algorithm for finding optimal
journeys in transit networks. CSA is particularly efficient for GTFS data
as it processes timetabled connections directly.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sys

from ..data.gtfs_parser import GTFSParser
from ..data.models import StopTime
from ..graph.transit_graph import TransitGraph, Connection
from .models import Journey, Leg


@dataclass
class ConnectionWithMeta:
    """Connection with additional metadata for CSA."""
    connection: Connection
    stop_sequence_from: int
    stop_sequence_to: int


class JourneyPlanner:
    """
    Journey planner using Connection Scan Algorithm.

    The CSA processes all connections (timetabled trip segments) in chronological
    order to find the earliest arrival time to the destination.
    """

    def __init__(self, gtfs_parser: GTFSParser, transit_graph: Optional[TransitGraph] = None):
        """
        Initialize journey planner.

        Args:
            gtfs_parser: GTFSParser with loaded GTFS data
            transit_graph: Optional pre-built TransitGraph (will be created if not provided)
        """
        self.parser = gtfs_parser
        self.graph = transit_graph or TransitGraph(gtfs_parser)

    def find_journey(
        self,
        origin_stop_id: str,
        destination_stop_id: str,
        departure_time: str,
        max_transfers: int = 3
    ) -> Optional[Journey]:
        """
        Find the earliest arrival journey from origin to destination.

        Args:
            origin_stop_id: Origin stop ID
            destination_stop_id: Destination stop ID
            departure_time: Earliest departure time in HH:MM:SS format
            max_transfers: Maximum number of transfers allowed

        Returns:
            Journey object if route found, None otherwise
        """
        # Validate stops exist
        if not self.graph.has_stop(origin_stop_id):
            raise ValueError(f"Origin stop {origin_stop_id} not found")
        if not self.graph.has_stop(destination_stop_id):
            raise ValueError(f"Destination stop {destination_stop_id} not found")

        # Handle same origin and destination
        if origin_stop_id == destination_stop_id:
            return None

        # Run Connection Scan Algorithm
        return self._connection_scan(
            origin_stop_id,
            destination_stop_id,
            departure_time,
            max_transfers
        )

    def _connection_scan(
        self,
        origin_stop_id: str,
        destination_stop_id: str,
        departure_time: str,
        max_transfers: int
    ) -> Optional[Journey]:
        """
        Connection Scan Algorithm implementation.

        Algorithm:
        1. Initialize earliest arrival time for all stops to infinity
        2. Set origin earliest arrival to departure time
        3. Process all connections in chronological order
        4. For each connection, check if it improves arrival time at destination stop
        5. Reconstruct journey from tracked connections

        Args:
            origin_stop_id: Origin stop ID
            destination_stop_id: Destination stop ID
            departure_time: Departure time string
            max_transfers: Maximum transfers

        Returns:
            Journey if found, None otherwise
        """
        # Convert time to seconds for comparison
        dep_seconds = self._time_to_seconds(departure_time)

        # Initialize earliest arrival times (in seconds since midnight)
        earliest_arrival = {stop_id: sys.maxsize for stop_id in self.parser.stops.keys()}
        earliest_arrival[origin_stop_id] = dep_seconds

        # Track the connection used to reach each stop (for reconstruction)
        enter_connection: Dict[str, Connection] = {}

        # Track which trip we're currently on at each stop
        in_trip: Dict[str, Optional[str]] = {stop_id: None for stop_id in self.parser.stops.keys()}

        # Sort connections by departure time
        all_connections = sorted(
            self.graph.connections,
            key=lambda c: self._time_to_seconds(c.departure_time)
        )

        # Scan all connections
        for conn in all_connections:
            dep_time = self._time_to_seconds(conn.departure_time)
            arr_time = self._time_to_seconds(conn.arrival_time)

            # Skip connections that depart before we can reach the departure stop
            if dep_time < earliest_arrival[conn.from_stop_id]:
                continue

            # Check if this connection improves arrival time
            if arr_time < earliest_arrival[conn.to_stop_id]:
                # Update earliest arrival
                earliest_arrival[conn.to_stop_id] = arr_time

                # Track the connection
                enter_connection[conn.to_stop_id] = conn

                # Update trip tracking
                # If we're on the same trip, no transfer needed
                if in_trip[conn.from_stop_id] == conn.trip_id:
                    in_trip[conn.to_stop_id] = conn.trip_id
                else:
                    # Transfer or initial boarding
                    in_trip[conn.to_stop_id] = conn.trip_id

        # Check if destination is reachable
        if destination_stop_id not in enter_connection:
            return None

        # Reconstruct journey
        return self._reconstruct_journey(
            origin_stop_id,
            destination_stop_id,
            enter_connection,
            earliest_arrival
        )

    def _reconstruct_journey(
        self,
        origin_stop_id: str,
        destination_stop_id: str,
        enter_connection: Dict[str, Connection],
        earliest_arrival: Dict[str, int]
    ) -> Optional[Journey]:
        """
        Reconstruct journey from tracked connections.

        Args:
            origin_stop_id: Origin stop ID
            destination_stop_id: Destination stop ID
            enter_connection: Map of stop_id to connection used to reach it
            earliest_arrival: Map of stop_id to earliest arrival time

        Returns:
            Journey object
        """
        # Backtrack from destination to origin
        path_connections: List[Connection] = []
        current_stop = destination_stop_id

        while current_stop != origin_stop_id:
            if current_stop not in enter_connection:
                return None  # No path found

            conn = enter_connection[current_stop]
            path_connections.append(conn)
            current_stop = conn.from_stop_id

        # Reverse to get origin -> destination order
        path_connections.reverse()

        # Group consecutive connections on same trip into legs
        legs: List[Leg] = []
        current_leg_start = 0

        for i in range(len(path_connections)):
            # Check if next connection is on different trip (transfer point)
            is_last = (i == len(path_connections) - 1)
            is_transfer = not is_last and path_connections[i].trip_id != path_connections[i + 1].trip_id

            if is_last or is_transfer:
                # Create leg from current_leg_start to i (inclusive)
                leg = self._create_leg(
                    path_connections[current_leg_start:i + 1]
                )
                legs.append(leg)
                current_leg_start = i + 1

        # Get stop names
        origin_stop = self.parser.get_stop(origin_stop_id)
        dest_stop = self.parser.get_stop(destination_stop_id)

        # Create journey
        journey = Journey(
            origin_stop_id=origin_stop_id,
            origin_stop_name=origin_stop.stop_name if origin_stop else origin_stop_id,
            destination_stop_id=destination_stop_id,
            destination_stop_name=dest_stop.stop_name if dest_stop else destination_stop_id,
            departure_time=path_connections[0].departure_time,
            arrival_time=path_connections[-1].arrival_time,
            legs=legs
        )

        return journey

    def _create_leg(self, connections: List[Connection]) -> Leg:
        """
        Create a Leg from a list of consecutive connections on the same trip.

        Args:
            connections: List of connections on the same trip

        Returns:
            Leg object
        """
        first_conn = connections[0]
        last_conn = connections[-1]

        from_stop = self.parser.get_stop(first_conn.from_stop_id)
        to_stop = self.parser.get_stop(last_conn.to_stop_id)

        trip = self.parser.get_trip(first_conn.trip_id)
        route = self.parser.get_route(first_conn.route_id) if first_conn.route_id else None

        return Leg(
            from_stop_id=first_conn.from_stop_id,
            from_stop_name=from_stop.stop_name if from_stop else first_conn.from_stop_id,
            to_stop_id=last_conn.to_stop_id,
            to_stop_name=to_stop.stop_name if to_stop else last_conn.to_stop_id,
            departure_time=first_conn.departure_time,
            arrival_time=last_conn.arrival_time,
            trip_id=first_conn.trip_id,
            route_id=first_conn.route_id,
            route_name=route.route_long_name if route else None,
            route_type=first_conn.route_type,
            is_transfer=first_conn.is_transfer,
            num_stops=len(connections) + 1  # Number of stops including first and last
        )

    def _time_to_seconds(self, time_str: str) -> int:
        """
        Convert GTFS time string to seconds since midnight.

        GTFS times can exceed 24:00:00 for trips past midnight.

        Args:
            time_str: Time in HH:MM:SS format

        Returns:
            Seconds since midnight
        """
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(parts[2])
        return hours * 3600 + minutes * 60 + seconds

    def find_multiple_journeys(
        self,
        origin_stop_id: str,
        destination_stop_id: str,
        departure_time: str,
        max_results: int = 3,
        max_transfers: int = 3
    ) -> List[Journey]:
        """
        Find multiple journey options.

        Note: Current implementation returns only the earliest arrival journey.
        Future enhancement could return multiple alternatives.

        Args:
            origin_stop_id: Origin stop ID
            destination_stop_id: Destination stop ID
            departure_time: Earliest departure time
            max_results: Maximum number of results (currently unused)
            max_transfers: Maximum transfers allowed

        Returns:
            List of Journey objects (currently 0 or 1 journey)
        """
        journey = self.find_journey(
            origin_stop_id,
            destination_stop_id,
            departure_time,
            max_transfers
        )

        return [journey] if journey else []
