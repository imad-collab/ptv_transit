#!/usr/bin/env python3
"""
Quick Journey Finder - Find a journey between two stations

Usage:
    python find_journey.py "Tarneit" "Waurn Ponds"
    python find_journey.py "Tarneit" "Waurn Ponds" "14:00:00"
"""

import sys
from datetime import datetime
from src.data.gtfs_parser import GTFSParser
from src.data.stop_index import StopIndex
from src.graph.transit_graph import TransitGraph
from src.routing.journey_planner import JourneyPlanner


def find_journey(origin_name, destination_name, departure_time=None):
    """Find a journey between two stations."""

    # Default to current time if not specified
    if not departure_time:
        now = datetime.now()
        departure_time = now.strftime("%H:%M:%S")
        print(f"No departure time specified, using current time: {departure_time}")
        print()

    print(f"🔍 Finding journey: {origin_name} → {destination_name}")
    print(f"⏰ Departure time: {departure_time}")
    print()

    # Load GTFS data
    print("Loading data...")
    parser = GTFSParser("data/gtfs")
    parser.load_stops()
    parser.load_routes()
    parser.load_trips()
    parser.load_stop_times()
    print(f"✓ Loaded {len(parser.stops)} stops")
    print()

    # Build graph
    print("Building transit network...")
    graph = TransitGraph(parser)
    print("✓ Network ready")
    print()

    # Find stations
    print("Finding stations...")
    stop_index = StopIndex(parser)

    origin = stop_index.find_stop(origin_name)
    if not origin:
        print(f"❌ Could not find station: {origin_name}")
        return
    print(f"✓ Origin: {origin.stop_name}")

    destination = stop_index.find_stop(destination_name)
    if not destination:
        print(f"❌ Could not find station: {destination_name}")
        return
    print(f"✓ Destination: {destination.stop_name}")
    print()

    # Plan journey
    print("Planning journey...")
    planner = JourneyPlanner(parser, graph)

    journey = planner.find_journey(
        origin.stop_id,
        destination.stop_id,
        departure_time=departure_time
    )

    if not journey:
        print("❌ No journey found for this time")
        print()
        print("Try a different time or check if the route is available.")
        return

    # Display journey
    print()
    print("=" * 80)
    print("✅ JOURNEY FOUND!")
    print("=" * 80)
    print()

    print(journey.format_summary())

    # Phase 4: Multi-modal analysis
    modes = journey.get_modes_used()
    print()
    print("=" * 80)
    print("🚆 TRANSPORT INFORMATION")
    print("=" * 80)
    print()
    print(f"Modes: {', '.join(modes)}")
    print(f"Multi-modal journey: {'Yes' if journey.is_multi_modal() else 'No'}")
    print()

    if journey.num_transfers > 0:
        print(f"⚠️  This journey has {journey.num_transfers} transfer(s).")
        print("   Make sure to allow time to change between services.")
    else:
        print("✓ Direct journey - no transfers needed!")

    print()
    print("=" * 80)
    print()


def main():
    if len(sys.argv) < 3:
        print("Usage: python find_journey.py <origin> <destination> [departure_time]")
        print()
        print("Examples:")
        print('  python find_journey.py "Tarneit" "Waurn Ponds"')
        print('  python find_journey.py "Tarneit" "Waurn Ponds" "14:00:00"')
        print('  python find_journey.py "Tarneit" "Geelong"')
        print()
        sys.exit(1)

    origin = sys.argv[1]
    destination = sys.argv[2]
    departure_time = sys.argv[3] if len(sys.argv) > 3 else None

    find_journey(origin, destination, departure_time)


if __name__ == "__main__":
    main()
