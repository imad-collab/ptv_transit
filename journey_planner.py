#!/usr/bin/env python3
"""
PTV Journey Planner - Multi-Modal Route Planning
Finds optimal routes between stations using Melbourne's public transport network.
"""

import os
import sys
import argparse
import requests
import zipfile
import pandas as pd
import networkx as nx
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from fuzzywuzzy import process
from dotenv import load_dotenv
from google.transit import gtfs_realtime_pb2

@dataclass
class Stop:
    stop_id: str
    name: str
    lat: float
    lon: float
    platform_code: str = ""
    parent_station: str = ""

@dataclass
class Route:
    route_id: str
    short_name: str
    long_name: str
    route_type: int  # 0=tram, 1=metro, 2=rail, 3=bus

@dataclass
class Journey:
    origin: Stop
    destination: Stop
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    route_name: str
    platform: str
    mode: str = "train"
    transfers: int = 0
    
    def __str__(self):
        mode_icons = {"train": "[TRAIN]", "tram": "[TRAM]", "bus": "[BUS]"}
        mode_display = mode_icons.get(self.mode, "[TRANSPORT]")
        return f"""
Journey: {self.origin.name} to {self.destination.name}
Mode: {mode_display} {self.mode.title()}
Duration: {self.duration_minutes} minutes
Departure: {self.departure_time.strftime('%H:%M')} from {self.platform}
Arrival: {self.arrival_time.strftime('%H:%M')}
Route: {self.route_name}
Transfers: {self.transfers}
"""

class GTFSData:
    def __init__(self):
        self.stops: Dict[str, Stop] = {}
        self.routes: Dict[str, Route] = {}
        self.stop_times = pd.DataFrame()
        self.trips = pd.DataFrame()
        self.stop_name_index: Dict[str, List[str]] = {}
        
    def load_sample_data(self):
        """Load sample Melbourne metro stations for demonstration"""
        sample_stops = [
            ("19854", "Flinders Street Station", -37.8183, 144.9671, "Platform 1-14"),
            ("19849", "Southern Cross Station", -37.8184, 144.9525, "Platform 1-16"),
            ("19842", "Richmond Station", -37.8211, 144.9889, "Platform 1-4"),
            ("19843", "Caulfield Station", -37.8773, 145.0454, "Platform 1-4"),
            ("19844", "Melbourne Central Station", -37.8098, 144.9631, "Platform 1-4"),
            ("19845", "Parliament Station", -37.8118, 144.9731, "Platform 1-2"),
            ("19846", "Flagstaff Station", -37.8122, 144.9563, "Platform 1-2"),
            ("19847", "North Melbourne Station", -37.8067, 144.9364, "Platform 1-6"),
            ("19848", "South Yarra Station", -37.8398, 144.9889, "Platform 1-4"),
        ]
        
        for stop_id, name, lat, lon, platform in sample_stops:
            stop = Stop(stop_id, name, lat, lon, platform)
            self.stops[stop_id] = stop
            
            # Build name index for fuzzy matching
            clean_name = name.lower().replace(" station", "").replace(" ", "")
            if clean_name not in self.stop_name_index:
                self.stop_name_index[clean_name] = []
            self.stop_name_index[clean_name].append(stop_id)
        
        # Sample routes with different modes
        sample_routes = [
            ("aus:vic:vic-02-PKM:", "Pakenham", "Flinders Street to Pakenham", 1, "train"),
            ("aus:vic:vic-02-FKN:", "Frankston", "Flinders Street to Frankston", 1, "train"),
            ("aus:vic:vic-02-CRB:", "Cranbourne", "Flinders Street to Cranbourne", 1, "train"),
            ("aus:vic:vic-02-BEL:", "Belgrave", "Flinders Street to Belgrave", 1, "train"),
            ("aus:vic:tram-01:", "Route 1", "East Coburg to South Melbourne Beach", 0, "tram"),
            ("aus:vic:tram-86:", "Route 86", "Bundoora RMIT to Docklands", 0, "tram"),
            ("aus:vic:bus-200:", "Route 200", "Melbourne University to Bulleen", 3, "bus"),
            ("aus:vic:bus-901:", "SkyBus", "Melbourne Airport to Southern Cross", 3, "bus"),
        ]
        
        for route_id, short_name, long_name, route_type, mode in sample_routes:
            route = Route(route_id, short_name, long_name, route_type)
            route.mode = mode
            self.routes[route_id] = route

class JourneyPlanner:
    def __init__(self):
        load_dotenv()
        self.gtfs_data = GTFSData()
        self.api_key = os.getenv('PTV_API_KEY')
        
    def initialize(self):
        """Initialize with sample data (in production, load full GTFS)"""
        print("Loading transport data...")
        self.gtfs_data.load_sample_data()
        print(f"Loaded {len(self.gtfs_data.stops)} stops")
        
    def find_stop_by_name(self, name: str) -> Optional[Stop]:
        """Find stop by name using fuzzy matching"""
        if not name:
            return None
            
        # Try exact match first
        clean_name = name.lower().replace(" station", "").replace(" ", "")
        if clean_name in self.gtfs_data.stop_name_index:
            stop_id = self.gtfs_data.stop_name_index[clean_name][0]
            return self.gtfs_data.stops[stop_id]
        
        # Fuzzy match
        all_names = [stop.name for stop in self.gtfs_data.stops.values()]
        match = process.extractOne(name, all_names, score_cutoff=60)
        
        if match:
            matched_name = match[0]
            for stop in self.gtfs_data.stops.values():
                if stop.name == matched_name:
                    return stop
        
        return None
    
    def get_realtime_delays(self) -> Dict[str, int]:
        """Fetch current delays from PTV realtime API"""
        if not self.api_key:
            return {}
            
        try:
            url = 'https://api.opendata.transport.vic.gov.au/opendata/public-transport/gtfs/realtime/v1/metro/trip-updates'
            headers = {'KeyID': self.api_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {}
                
            feed = gtfs_realtime_pb2.FeedMessage()
            feed.ParseFromString(response.content)
            
            delays = {}
            for entity in feed.entity:
                if entity.HasField('trip_update'):
                    trip_id = entity.trip_update.trip.trip_id
                    for stu in entity.trip_update.stop_time_update:
                        if stu.HasField('arrival') and stu.arrival.HasField('delay'):
                            delays[trip_id] = stu.arrival.delay
                            break
            
            return delays
            
        except Exception as e:
            print(f"Warning: Could not fetch realtime data: {e}")
            return {}
    
    def calculate_journey_time(self, origin: Stop, destination: Stop, mode: str = "train") -> int:
        """Calculate estimated journey time between stops based on transport mode"""
        import math
        
        # Haversine formula for distance
        lat1, lon1 = math.radians(origin.lat), math.radians(origin.lon)
        lat2, lon2 = math.radians(destination.lat), math.radians(destination.lon)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = 6371 * c
        
        # Different average speeds for different modes
        speeds = {
            "train": 40,  # km/h
            "tram": 20,   # km/h
            "bus": 25     # km/h
        }
        
        speed = speeds.get(mode, 30)
        travel_time_minutes = int(distance_km / speed * 60)
        return max(travel_time_minutes, 2)  # Minimum 2 minutes
    
    def find_route_name(self, origin: Stop, destination: Stop, mode: str = "train") -> str:
        """Determine which route connects the stops based on mode"""
        if mode == "train":
            route_mapping = {
                ("Flinders Street Station", "Richmond Station"): "Belgrave/Lilydale Line",
                ("Flinders Street Station", "Caulfield Station"): "Frankston/Pakenham/Cranbourne Line",
                ("Flinders Street Station", "Southern Cross Station"): "City Loop",
                ("Richmond Station", "Caulfield Station"): "Frankston/Pakenham/Cranbourne Line",
                ("Melbourne Central Station", "Parliament Station"): "City Loop",
            }
        elif mode == "tram":
            route_mapping = {
                ("Flinders Street Station", "Richmond Station"): "Route 70 (Wattle Park)",
                ("Melbourne Central Station", "South Yarra Station"): "Route 8 (Toorak)",
                ("Southern Cross Station", "Parliament Station"): "Route 11 (West Preston)",
            }
        elif mode == "bus":
            route_mapping = {
                ("Melbourne Central Station", "Caulfield Station"): "Route 200 (Bulleen)",
                ("Southern Cross Station", "Richmond Station"): "Route 246 (Elsternwick)",
            }
        else:
            route_mapping = {}
        
        key = (origin.name, destination.name)
        reverse_key = (destination.name, origin.name)
        
        return route_mapping.get(key, route_mapping.get(reverse_key, f"{mode.title()} Route"))
    
    def plan_journey(
        self, 
        origin_name: str, 
        destination_name: str, 
        departure_time: Optional[str] = None,
        mode: str = "train"
    ) -> List[Journey]:
        """Plan journey between two locations"""
        
        # Find stops
        origin = self.find_stop_by_name(origin_name)
        if not origin:
            raise ValueError(f"Origin station '{origin_name}' not found")
            
        destination = self.find_stop_by_name(destination_name)
        if not destination:
            raise ValueError(f"Destination station '{destination_name}' not found")
        
        if origin.stop_id == destination.stop_id:
            raise ValueError("Origin and destination are the same")
        
        # Parse departure time
        if departure_time and departure_time.lower() != 'now':
            try:
                dep_time = datetime.strptime(departure_time, '%H:%M')
                dep_time = dep_time.replace(year=datetime.now().year, 
                                         month=datetime.now().month, 
                                         day=datetime.now().day)
            except ValueError:
                dep_time = datetime.now()
        else:
            dep_time = datetime.now()
        
        # Calculate journey
        travel_time = self.calculate_journey_time(origin, destination, mode)
        route_name = self.find_route_name(origin, destination, mode)
        
        # Get realtime delays
        delays = self.get_realtime_delays()
        delay_minutes = 0
        if delays:
            # Apply average delay (simplified)
            delay_minutes = sum(delays.values()) // len(delays) // 60
        
        # Adjust for next departure (different frequencies by mode)
        frequencies = {
            "train": 10,  # Every 10 minutes
            "tram": 15,   # Every 15 minutes  
            "bus": 20     # Every 20 minutes
        }
        
        next_service_minutes = frequencies.get(mode, 10)
        next_departure = dep_time + timedelta(minutes=5)  # Next service in 5 min
        arrival_time = next_departure + timedelta(minutes=travel_time + delay_minutes)
        
        journey = Journey(
            origin=origin,
            destination=destination,
            departure_time=next_departure,
            arrival_time=arrival_time,
            duration_minutes=travel_time + delay_minutes,
            route_name=route_name,
            platform=origin.platform_code,
            mode=mode,
            transfers=0
        )
        
        return [journey]

def main():
    parser = argparse.ArgumentParser(
        description='PTV Journey Planner - Find routes between Melbourne stations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python journey_planner.py "Flinders Street" "Richmond"
  python journey_planner.py "Melbourne Central" "Caulfield" --time "14:30"
  python journey_planner.py "Southern Cross" "Parliament" --time "now"
  python journey_planner.py "Flinders Street" "Richmond" --mode tram
  python journey_planner.py "Melbourne Central" "Caulfield" --mode bus --time "14:30"
        """
    )
    
    parser.add_argument('origin', help='Starting station name')
    parser.add_argument('destination', help='Destination station name')
    parser.add_argument('--time', default='now', 
                       help='Departure time (HH:MM or "now")')
    parser.add_argument('--mode', choices=['train', 'tram', 'bus'], default='train',
                       help='Transport mode (default: train)')
    
    args = parser.parse_args()
    
    try:
        # Initialize planner
        planner = JourneyPlanner()
        planner.initialize()
        
        print(f"\nPlanning journey from '{args.origin}' to '{args.destination}'")
        print(f"Transport mode: {args.mode.title()}")
        if args.time != 'now':
            print(f"Departure time: {args.time}")
        print("-" * 60)
        
        # Find journeys
        journeys = planner.plan_journey(args.origin, args.destination, args.time, args.mode)
        
        if not journeys:
            print("No routes found between these stations.")
            return
        
        # Display results
        for i, journey in enumerate(journeys, 1):
            print(f"Route {i}:")
            print(journey)
            
            # Show realtime info if available
            if planner.api_key:
                print("[LIVE] Includes live delay information")
            else:
                print("[INFO] Using scheduled times only (set PTV_API_KEY for live data)")
            
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()