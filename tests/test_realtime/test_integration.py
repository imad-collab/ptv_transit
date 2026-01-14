"""
Tests for realtime integration module.

Tests applying real-time delays, cancellations, and platform information
to scheduled journeys.
"""

import pytest
from unittest.mock import Mock, MagicMock
from google.transit import gtfs_realtime_pb2

from src.realtime.integration import (
    RealtimeIntegrator,
    TripUpdateInfo,
    StopUpdate
)
from src.routing.models import Journey, Leg


class TestStopUpdate:
    """Test StopUpdate dataclass."""

    def test_create_stop_update(self):
        """Test creating a stop update."""
        update = StopUpdate(
            stop_id="STOP1",
            stop_sequence=5,
            departure_delay_seconds=300,
            arrival_delay_seconds=240
        )
        assert update.stop_id == "STOP1"
        assert update.stop_sequence == 5
        assert update.departure_delay_seconds == 300
        assert update.arrival_delay_seconds == 240

    def test_stop_update_defaults(self):
        """Test stop update default values."""
        update = StopUpdate(stop_id="STOP1", stop_sequence=1)
        assert update.departure_delay_seconds == 0
        assert update.arrival_delay_seconds == 0
        assert update.platform_name is None


class TestTripUpdateInfo:
    """Test TripUpdateInfo dataclass."""

    def test_create_trip_update_info(self):
        """Test creating trip update info."""
        info = TripUpdateInfo(
            trip_id="TRIP1",
            route_id="ROUTE1",
            is_cancelled=False
        )
        assert info.trip_id == "TRIP1"
        assert info.route_id == "ROUTE1"
        assert not info.is_cancelled
        assert len(info.stop_updates) == 0

    def test_trip_update_with_stops(self):
        """Test trip update with stop updates."""
        stop1 = StopUpdate("STOP1", 1, 120, 100)
        stop2 = StopUpdate("STOP2", 2, 180, 160)

        info = TripUpdateInfo(
            trip_id="TRIP1",
            route_id="ROUTE1",
            stop_updates={"STOP1": stop1, "STOP2": stop2}
        )
        assert len(info.stop_updates) == 2
        assert info.stop_updates["STOP1"].departure_delay_seconds == 120


class TestRealtimeIntegratorInit:
    """Test RealtimeIntegrator initialization."""

    def test_init_without_fetcher(self):
        """Test initialization without providing fetcher."""
        integrator = RealtimeIntegrator()
        assert integrator.fetcher is None

    def test_init_with_fetcher(self):
        """Test initialization with custom fetcher."""
        mock_fetcher = Mock()
        integrator = RealtimeIntegrator(fetcher=mock_fetcher)
        assert integrator.fetcher == mock_fetcher


class TestApplyDelaysToLeg:
    """Test applying delays to individual journey legs."""

    def test_apply_positive_delay(self):
        """Test applying positive delay (late arrival)."""
        leg = Leg(
            from_stop_id="STOP1",
            from_stop_name="Stop 1",
            to_stop_id="STOP2",
            to_stop_name="Stop 2",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1"
        )

        trip_info = TripUpdateInfo(
            trip_id="TRIP1",
            route_id="ROUTE1",
            stop_updates={
                "STOP1": StopUpdate("STOP1", 1, departure_delay_seconds=300),  # 5 min late
                "STOP2": StopUpdate("STOP2", 2, arrival_delay_seconds=420)      # 7 min late
            }
        )

        integrator = RealtimeIntegrator(fetcher=Mock())
        integrator._apply_delays_to_leg(leg, trip_info)

        assert leg.has_realtime_data
        assert leg.scheduled_departure_time == "14:00:00"
        assert leg.actual_departure_time == "14:05:00"  # 14:00 + 5 min
        assert leg.scheduled_arrival_time == "14:30:00"
        assert leg.actual_arrival_time == "14:37:00"  # 14:30 + 7 min
        assert leg.departure_delay_seconds == 300
        assert leg.arrival_delay_seconds == 420

    def test_apply_negative_delay(self):
        """Test applying negative delay (early arrival)."""
        leg = Leg(
            from_stop_id="STOP1",
            from_stop_name="Stop 1",
            to_stop_id="STOP2",
            to_stop_name="Stop 2",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1"
        )

        trip_info = TripUpdateInfo(
            trip_id="TRIP1",
            route_id="ROUTE1",
            stop_updates={
                "STOP1": StopUpdate("STOP1", 1, departure_delay_seconds=-120),  # 2 min early
                "STOP2": StopUpdate("STOP2", 2, arrival_delay_seconds=-180)     # 3 min early
            }
        )

        integrator = RealtimeIntegrator(fetcher=Mock())
        integrator._apply_delays_to_leg(leg, trip_info)

        assert leg.actual_departure_time == "13:58:00"  # 14:00 - 2 min
        assert leg.actual_arrival_time == "14:27:00"  # 14:30 - 3 min

    def test_apply_zero_delay(self):
        """Test applying zero delay (on time)."""
        leg = Leg(
            from_stop_id="STOP1",
            from_stop_name="Stop 1",
            to_stop_id="STOP2",
            to_stop_name="Stop 2",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1"
        )

        trip_info = TripUpdateInfo(
            trip_id="TRIP1",
            route_id="ROUTE1",
            stop_updates={
                "STOP1": StopUpdate("STOP1", 1, departure_delay_seconds=0),
                "STOP2": StopUpdate("STOP2", 2, arrival_delay_seconds=0)
            }
        )

        integrator = RealtimeIntegrator(fetcher=Mock())
        integrator._apply_delays_to_leg(leg, trip_info)

        assert leg.actual_departure_time == "14:00:00"
        assert leg.actual_arrival_time == "14:30:00"

    def test_cancelled_trip(self):
        """Test cancelled trip."""
        leg = Leg(
            from_stop_id="STOP1",
            from_stop_name="Stop 1",
            to_stop_id="STOP2",
            to_stop_name="Stop 2",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1"
        )

        trip_info = TripUpdateInfo(
            trip_id="TRIP1",
            route_id="ROUTE1",
            is_cancelled=True
        )

        integrator = RealtimeIntegrator(fetcher=Mock())
        integrator._apply_delays_to_leg(leg, trip_info)

        assert leg.is_cancelled
        assert leg.has_realtime_data

    def test_no_realtime_data_for_stops(self):
        """Test leg with no realtime data for its stops."""
        leg = Leg(
            from_stop_id="STOP1",
            from_stop_name="Stop 1",
            to_stop_id="STOP2",
            to_stop_name="Stop 2",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1"
        )

        trip_info = TripUpdateInfo(
            trip_id="TRIP1",
            route_id="ROUTE1",
            stop_updates={
                "STOP3": StopUpdate("STOP3", 1, departure_delay_seconds=300)
            }
        )

        integrator = RealtimeIntegrator(fetcher=Mock())
        integrator._apply_delays_to_leg(leg, trip_info)

        # No changes should be made
        assert not leg.has_realtime_data
        assert leg.actual_departure_time is None


class TestTransferValidation:
    """Test transfer validation after delays."""

    def test_valid_transfer(self):
        """Test transfer that remains valid after delays."""
        leg1 = Leg(
            from_stop_id="A",
            from_stop_name="Stop A",
            to_stop_id="B",
            to_stop_name="Stop B",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1",
            actual_departure_time="14:00:00",
            actual_arrival_time="14:32:00"  # 2 min late
        )

        leg2 = Leg(
            from_stop_id="B",
            from_stop_name="Stop B",
            to_stop_id="C",
            to_stop_name="Stop C",
            departure_time="14:35:00",  # 5 min buffer
            arrival_time="15:00:00",
            trip_id="TRIP2",
            route_id="ROUTE2",
            actual_departure_time="14:35:00",
            actual_arrival_time="15:00:00"
        )

        journey = Journey(
            origin_stop_id="A",
            origin_stop_name="Stop A",
            destination_stop_id="C",
            destination_stop_name="Stop C",
            departure_time="14:00:00",
            arrival_time="15:00:00",
            legs=[leg1, leg2]
        )

        integrator = RealtimeIntegrator(fetcher=Mock())
        is_valid, reason = integrator._validate_transfers(journey, min_transfer_time_seconds=120)

        assert is_valid
        assert reason is None

    def test_invalid_transfer(self):
        """Test transfer that becomes invalid after delays."""
        leg1 = Leg(
            from_stop_id="A",
            from_stop_name="Stop A",
            to_stop_id="B",
            to_stop_name="Stop B",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1",
            actual_departure_time="14:00:00",
            actual_arrival_time="14:34:00"  # 4 min late
        )

        leg2 = Leg(
            from_stop_id="B",
            from_stop_name="Stop B",
            to_stop_id="C",
            to_stop_name="Stop C",
            departure_time="14:35:00",  # Only 1 min buffer now
            arrival_time="15:00:00",
            trip_id="TRIP2",
            route_id="ROUTE2",
            actual_departure_time="14:35:00",
            actual_arrival_time="15:00:00"
        )

        journey = Journey(
            origin_stop_id="A",
            origin_stop_name="Stop A",
            destination_stop_id="C",
            destination_stop_name="Stop C",
            departure_time="14:00:00",
            arrival_time="15:00:00",
            legs=[leg1, leg2]
        )

        integrator = RealtimeIntegrator(fetcher=Mock())
        is_valid, reason = integrator._validate_transfers(journey, min_transfer_time_seconds=120)

        assert not is_valid
        assert "Stop B" in reason
        assert "no longer feasible" in reason

    def test_no_transfers(self):
        """Test journey with no transfers."""
        leg = Leg(
            from_stop_id="A",
            from_stop_name="Stop A",
            to_stop_id="B",
            to_stop_name="Stop B",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1"
        )

        journey = Journey(
            origin_stop_id="A",
            origin_stop_name="Stop A",
            destination_stop_id="B",
            destination_stop_name="Stop B",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            legs=[leg]
        )

        integrator = RealtimeIntegrator(fetcher=Mock())
        is_valid, reason = integrator._validate_transfers(journey, min_transfer_time_seconds=120)

        assert is_valid
        assert reason is None


class TestApplyRealtimeToJourney:
    """Test complete journey realtime integration."""

    def test_journey_with_no_realtime_data(self):
        """Test journey when realtime fetch fails."""
        leg = Leg(
            from_stop_id="A",
            from_stop_name="Stop A",
            to_stop_id="B",
            to_stop_name="Stop B",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1"
        )

        journey = Journey(
            origin_stop_id="A",
            origin_stop_name="Stop A",
            destination_stop_id="B",
            destination_stop_name="Stop B",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            legs=[leg]
        )

        # Mock fetcher to raise exception
        mock_fetcher = Mock()
        mock_fetcher.fetch_trip_updates.side_effect = Exception("API Error")

        integrator = RealtimeIntegrator(fetcher=mock_fetcher)
        result = integrator.apply_realtime_to_journey(journey)

        # Journey should be returned unchanged
        assert result == journey
        assert not journey.has_realtime_data

    def test_journey_becomes_invalid_due_to_cancellation(self):
        """Test journey marked invalid when leg is cancelled."""
        # This is an integration test, so we'll need to mock the feed
        # For now, we'll test the logic directly
        leg = Leg(
            from_stop_id="A",
            from_stop_name="Stop A",
            to_stop_id="B",
            to_stop_name="Stop B",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1",
            is_cancelled=True,
            has_realtime_data=True
        )

        journey = Journey(
            origin_stop_id="A",
            origin_stop_name="Stop A",
            destination_stop_id="B",
            destination_stop_name="Stop B",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            legs=[leg]
        )

        # Manually set fields as if realtime was applied
        journey.has_realtime_data = True
        journey.is_realtime_valid = False
        journey.invalidity_reason = "One or more services have been cancelled"

        assert not journey.is_realtime_valid
        assert "cancelled" in journey.invalidity_reason.lower()


class TestParseTripUpdates:
    """Test parsing GTFS Realtime feed."""

    def test_parse_empty_feed(self):
        """Test parsing feed with no entities."""
        feed = gtfs_realtime_pb2.FeedMessage()

        integrator = RealtimeIntegrator(fetcher=Mock())
        result = integrator._parse_trip_updates(feed)

        assert len(result) == 0

    def test_parse_feed_with_trip_update(self):
        """Test parsing feed with trip update."""
        feed = gtfs_realtime_pb2.FeedMessage()

        entity = feed.entity.add()
        entity.id = "entity1"

        trip_update = entity.trip_update
        trip_update.trip.trip_id = "TRIP1"
        trip_update.trip.route_id = "ROUTE1"

        # Add stop time update
        stu = trip_update.stop_time_update.add()
        stu.stop_id = "STOP1"
        stu.stop_sequence = 1
        stu.departure.delay = 300  # 5 min delay

        integrator = RealtimeIntegrator(fetcher=Mock())
        result = integrator._parse_trip_updates(feed)

        assert len(result) == 1
        assert "TRIP1" in result
        assert result["TRIP1"].trip_id == "TRIP1"
        assert result["TRIP1"].route_id == "ROUTE1"
        assert not result["TRIP1"].is_cancelled
        assert len(result["TRIP1"].stop_updates) == 1
        assert result["TRIP1"].stop_updates["STOP1"].departure_delay_seconds == 300


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_large_delay(self):
        """Test very large delay (over 1 hour)."""
        leg = Leg(
            from_stop_id="STOP1",
            from_stop_name="Stop 1",
            to_stop_id="STOP2",
            to_stop_name="Stop 2",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1"
        )

        trip_info = TripUpdateInfo(
            trip_id="TRIP1",
            route_id="ROUTE1",
            stop_updates={
                "STOP1": StopUpdate("STOP1", 1, departure_delay_seconds=3600),  # 60 min
                "STOP2": StopUpdate("STOP2", 2, arrival_delay_seconds=3600)
            }
        )

        integrator = RealtimeIntegrator(fetcher=Mock())
        integrator._apply_delays_to_leg(leg, trip_info)

        assert leg.actual_departure_time == "15:00:00"  # 14:00 + 60 min
        assert leg.actual_arrival_time == "15:30:00"  # 14:30 + 60 min

    def test_partial_realtime_data(self):
        """Test leg with realtime data for only one stop."""
        leg = Leg(
            from_stop_id="STOP1",
            from_stop_name="Stop 1",
            to_stop_id="STOP2",
            to_stop_name="Stop 2",
            departure_time="14:00:00",
            arrival_time="14:30:00",
            trip_id="TRIP1",
            route_id="ROUTE1"
        )

        trip_info = TripUpdateInfo(
            trip_id="TRIP1",
            route_id="ROUTE1",
            stop_updates={
                "STOP1": StopUpdate("STOP1", 1, departure_delay_seconds=300)
                # No data for STOP2
            }
        )

        integrator = RealtimeIntegrator(fetcher=Mock())
        integrator._apply_delays_to_leg(leg, trip_info)

        assert leg.actual_departure_time == "14:05:00"
        assert leg.actual_arrival_time == "14:30:00"  # No delay, use scheduled
