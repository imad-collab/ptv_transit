"""
Data models for journey planning results.

This module defines the structure for journey results including
individual journey legs and complete journey itineraries.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta


@dataclass
class Leg:
    """
    Represents one segment of a journey (e.g., one trip on a route).

    A leg is a continuous journey on a single trip/route without transfers.
    """

    from_stop_id: str
    from_stop_name: str
    to_stop_id: str
    to_stop_name: str

    departure_time: str  # HH:MM:SS format
    arrival_time: str    # HH:MM:SS format

    trip_id: str
    route_id: str
    route_name: Optional[str] = None

    # Number of stops between origin and destination (including both)
    num_stops: int = 0

    def __post_init__(self):
        """Validate and convert types."""
        self.num_stops = int(self.num_stops)

    @property
    def duration_seconds(self) -> int:
        """Calculate leg duration in seconds."""
        def time_to_seconds(time_str: str) -> int:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return hours * 3600 + minutes * 60 + seconds

        dep = time_to_seconds(self.departure_time)
        arr = time_to_seconds(self.arrival_time)
        return arr - dep

    @property
    def duration_minutes(self) -> int:
        """Calculate leg duration in minutes."""
        return self.duration_seconds // 60

    def format_duration(self) -> str:
        """Format duration as human-readable string."""
        minutes = self.duration_minutes
        if minutes < 60:
            return f"{minutes}m"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"


@dataclass
class Journey:
    """
    Represents a complete journey from origin to destination.

    A journey consists of one or more legs, possibly with transfers.
    """

    origin_stop_id: str
    origin_stop_name: str
    destination_stop_id: str
    destination_stop_name: str

    departure_time: str  # HH:MM:SS format
    arrival_time: str    # HH:MM:SS format

    legs: List[Leg]

    def __post_init__(self):
        """Validate journey data."""
        if not self.legs:
            raise ValueError("Journey must have at least one leg")

        # Validate leg continuity
        for i in range(len(self.legs) - 1):
            if self.legs[i].to_stop_id != self.legs[i + 1].from_stop_id:
                raise ValueError(
                    f"Discontinuous journey: leg {i} ends at {self.legs[i].to_stop_id} "
                    f"but leg {i+1} starts at {self.legs[i + 1].from_stop_id}"
                )

    @property
    def num_transfers(self) -> int:
        """Number of transfers (changes between vehicles)."""
        return len(self.legs) - 1

    @property
    def duration_seconds(self) -> int:
        """Calculate total journey duration in seconds."""
        def time_to_seconds(time_str: str) -> int:
            parts = time_str.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = int(parts[2])
            return hours * 3600 + minutes * 60 + seconds

        dep = time_to_seconds(self.departure_time)
        arr = time_to_seconds(self.arrival_time)
        return arr - dep

    @property
    def duration_minutes(self) -> int:
        """Calculate total journey duration in minutes."""
        return self.duration_seconds // 60

    def format_duration(self) -> str:
        """Format duration as human-readable string."""
        minutes = self.duration_minutes
        if minutes < 60:
            return f"{minutes}m"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"

    def get_transfer_wait_times(self) -> List[int]:
        """
        Get wait times at each transfer in seconds.

        Returns:
            List of wait times in seconds (empty if no transfers)
        """
        if self.num_transfers == 0:
            return []

        wait_times = []
        for i in range(len(self.legs) - 1):
            # Time between arrival of current leg and departure of next leg
            def time_to_seconds(time_str: str) -> int:
                parts = time_str.split(':')
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
                return hours * 3600 + minutes * 60 + seconds

            arrival = time_to_seconds(self.legs[i].arrival_time)
            next_departure = time_to_seconds(self.legs[i + 1].departure_time)
            wait_times.append(next_departure - arrival)

        return wait_times

    def format_summary(self) -> str:
        """
        Format journey as a human-readable summary string.

        Returns:
            Multi-line string with journey details
        """
        lines = []
        lines.append(f"Journey: {self.origin_stop_name} → {self.destination_stop_name}")
        lines.append(f"Departure: {self.departure_time}")
        lines.append(f"Arrival: {self.arrival_time}")
        lines.append(f"Duration: {self.format_duration()}")
        lines.append(f"Transfers: {self.num_transfers}")
        lines.append("")

        for i, leg in enumerate(self.legs, 1):
            lines.append(f"Leg {i}:")
            lines.append(f"  {leg.from_stop_name} → {leg.to_stop_name}")
            lines.append(f"  Depart: {leg.departure_time}  Arrive: {leg.arrival_time}")
            lines.append(f"  Duration: {leg.format_duration()}")
            if leg.route_name:
                lines.append(f"  Route: {leg.route_name}")
            lines.append(f"  Stops: {leg.num_stops}")

            # Add transfer wait time if not last leg
            if i < len(self.legs):
                wait_times = self.get_transfer_wait_times()
                if wait_times:
                    wait_mins = wait_times[i - 1] // 60
                    lines.append(f"  Transfer wait: {wait_mins}m")

            lines.append("")

        return "\n".join(lines)
