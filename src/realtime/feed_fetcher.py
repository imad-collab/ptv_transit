"""
GTFS Realtime Feed Fetcher

Fetches and parses GTFS Realtime protobuf feeds from PTV API.
Supports trip updates, vehicle positions, and service alerts.

Documentation: https://opendata.transport.vic.gov.au/dataset/gtfs-realtime
License: Creative Commons Attribution 4.0
"""

import requests
from google.transit import gtfs_realtime_pb2
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class GTFSRealtimeFetcher:
    """Fetches GTFS Realtime feeds from PTV API."""

    # PTV GTFS Realtime feed URLs
    FEED_URLS = {
        'metro': {
            'trip_updates': 'https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/metro/trip-updates',
            'vehicle_positions': 'https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/metro/vehicle-positions',
            'service_alerts': 'https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/metro/service-alerts',
        },
        'vline': {
            'trip_updates': 'https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/vline/trip-updates',
            'vehicle_positions': 'https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/vline/vehicle-positions',
            'service_alerts': 'https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/vline/service-alerts',
        }
    }

    def __init__(self, api_key: str, timeout: int = 30):
        """
        Initialize the GTFS Realtime fetcher.

        Args:
            api_key: PTV API subscription key
            timeout: Request timeout in seconds (default: 30)
        """
        if not api_key:
            raise ValueError("API key is required")

        self.api_key = api_key
        self.timeout = timeout

    def fetch_feed(self, url: str) -> gtfs_realtime_pb2.FeedMessage:
        """
        Fetch and parse a GTFS Realtime feed from the given URL.

        Args:
            url: The URL of the GTFS Realtime feed

        Returns:
            Parsed FeedMessage protobuf object

        Raises:
            requests.exceptions.RequestException: If the HTTP request fails
            ValueError: If the response cannot be parsed as protobuf
        """
        try:
            headers = {
                'KeyID': self.api_key
            }

            logger.debug(f"Fetching GTFS Realtime feed from: {url}")
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()

            # Parse the protobuf feed
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)

            logger.info(f"Successfully fetched feed with {len(feed.entity)} entities")
            return feed

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Status code: {e.response.status_code}")
                logger.error(f"Response: {e.response.text[:200]}")
            raise

        except Exception as e:
            logger.error(f"Failed to parse protobuf: {e}")
            raise ValueError(f"Invalid protobuf data: {e}") from e

    def fetch_trip_updates(self, mode: str = 'metro') -> gtfs_realtime_pb2.FeedMessage:
        """
        Fetch trip updates for the specified transport mode.

        Args:
            mode: Transport mode ('metro' or 'vline')

        Returns:
            FeedMessage containing trip updates
        """
        if mode not in self.FEED_URLS:
            raise ValueError(f"Unknown mode: {mode}. Must be one of {list(self.FEED_URLS.keys())}")

        url = self.FEED_URLS[mode]['trip_updates']
        return self.fetch_feed(url)

    def fetch_vehicle_positions(self, mode: str = 'metro') -> gtfs_realtime_pb2.FeedMessage:
        """
        Fetch vehicle positions for the specified transport mode.

        Args:
            mode: Transport mode ('metro' or 'vline')

        Returns:
            FeedMessage containing vehicle positions
        """
        if mode not in self.FEED_URLS:
            raise ValueError(f"Unknown mode: {mode}. Must be one of {list(self.FEED_URLS.keys())}")

        url = self.FEED_URLS[mode]['vehicle_positions']
        return self.fetch_feed(url)

    def fetch_service_alerts(self, mode: str = 'metro') -> gtfs_realtime_pb2.FeedMessage:
        """
        Fetch service alerts for the specified transport mode.

        Args:
            mode: Transport mode ('metro' or 'vline')

        Returns:
            FeedMessage containing service alerts
        """
        if mode not in self.FEED_URLS:
            raise ValueError(f"Unknown mode: {mode}. Must be one of {list(self.FEED_URLS.keys())}")

        url = self.FEED_URLS[mode]['service_alerts']
        return self.fetch_feed(url)
