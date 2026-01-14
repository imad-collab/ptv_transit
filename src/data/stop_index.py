"""
Stop Index for fast station lookups.

Provides fuzzy name matching and spatial queries for GTFS stops.
"""

from typing import List, Optional, Tuple
from fuzzywuzzy import fuzz, process
import logging

from .models import Stop
from .gtfs_parser import GTFSParser

logger = logging.getLogger(__name__)


class StopIndex:
    """Index for fast stop lookups and fuzzy name matching."""

    def __init__(self, parser: GTFSParser):
        """
        Initialize stop index.

        Args:
            parser: GTFSParser instance with loaded data
        """
        self.parser = parser
        self.stops = parser.stops

        # Build name index
        self._name_index = {}
        for stop_id, stop in self.stops.items():
            name_lower = stop.stop_name.lower()
            if name_lower not in self._name_index:
                self._name_index[name_lower] = []
            self._name_index[name_lower].append(stop_id)

        logger.debug(f"Indexed {len(self.stops)} stops")

    def find_stop_exact(self, stop_name: str) -> Optional[Stop]:
        """
        Find a stop by exact name match (case-insensitive).

        Args:
            stop_name: Station name to search for

        Returns:
            Stop object if found, None otherwise
        """
        name_lower = stop_name.lower()
        stop_ids = self._name_index.get(name_lower, [])

        if stop_ids:
            return self.stops[stop_ids[0]]

        return None

    def find_stop_fuzzy(
        self,
        stop_name: str,
        limit: int = 5,
        min_score: int = 60
    ) -> List[Tuple[Stop, int]]:
        """
        Find stops using fuzzy name matching.

        Args:
            stop_name: Station name to search for
            limit: Maximum number of results
            min_score: Minimum fuzzy match score (0-100)

        Returns:
            List of (Stop, score) tuples, sorted by score descending
        """
        if not self.stops:
            return []

        # Get all stop names for fuzzy matching
        stop_names = {stop_id: stop.stop_name for stop_id, stop in self.stops.items()}

        # Use fuzzywuzzy to find best matches
        matches = process.extract(
            stop_name,
            stop_names,
            scorer=fuzz.token_sort_ratio,
            limit=limit
        )

        # Filter by minimum score and convert to Stop objects
        results = []
        for match_name, score, stop_id in matches:
            if score >= min_score:
                stop = self.stops[stop_id]
                results.append((stop, score))

        return results

    def find_stop(
        self,
        stop_name: str,
        fuzzy: bool = True
    ) -> Optional[Stop]:
        """
        Find a stop by name (exact or fuzzy).

        Args:
            stop_name: Station name to search for
            fuzzy: If True, use fuzzy matching if exact match fails

        Returns:
            Stop object if found, None otherwise
        """
        # Try exact match first
        stop = self.find_stop_exact(stop_name)
        if stop:
            return stop

        # Try fuzzy match
        if fuzzy:
            matches = self.find_stop_fuzzy(stop_name, limit=1)
            if matches:
                return matches[0][0]

        return None

    def find_stops_by_ids(self, stop_ids: List[str]) -> List[Stop]:
        """
        Find multiple stops by their IDs.

        Args:
            stop_ids: List of stop IDs

        Returns:
            List of Stop objects
        """
        stops = []
        for stop_id in stop_ids:
            stop = self.stops.get(stop_id)
            if stop:
                stops.append(stop)

        return stops

    def get_all_stops(self) -> List[Stop]:
        """
        Get all stops.

        Returns:
            List of all Stop objects
        """
        return list(self.stops.values())

    def get_stop_count(self) -> int:
        """
        Get total number of stops.

        Returns:
            Number of stops in the index
        """
        return len(self.stops)
