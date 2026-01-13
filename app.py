#!/usr/bin/env python3
"""
PTV Journey Planner Web App
Web frontend for the Melbourne public transport journey planner
"""

from flask import Flask, render_template, request, jsonify
from journey_planner import JourneyPlanner
from datetime import datetime
import json

app = Flask(__name__)

# Initialize the journey planner
planner = JourneyPlanner()
planner.initialize()

@app.route('/')
def index():
    """Main page with journey planning form"""
    return render_template('index.html')

@app.route('/api/stations')
def get_stations():
    """API endpoint to get all available stations"""
    stations = []
    for stop in planner.gtfs_data.stops.values():
        stations.append({
            'id': stop.stop_id,
            'name': stop.name,
            'platform': stop.platform_code,
            'lat': stop.lat,
            'lon': stop.lon
        })
    
    # Sort by name
    stations.sort(key=lambda x: x['name'])
    return jsonify(stations)

@app.route('/api/plan', methods=['POST'])
def plan_journey():
    """API endpoint to plan a journey"""
    try:
        data = request.get_json()
        
        origin = data.get('origin', '').strip()
        destination = data.get('destination', '').strip()
        time = data.get('time', 'now').strip()
        mode = data.get('mode', 'train').strip()
        
        if not origin or not destination:
            return jsonify({'error': 'Origin and destination are required'}), 400
        
        # Plan the journey
        journeys = planner.plan_journey(origin, destination, time, mode)
        
        if not journeys:
            return jsonify({'error': 'No routes found between these stations'}), 404
        
        # Convert journey to JSON-serializable format
        journey = journeys[0]  # Take the first (best) journey
        
        # Get all stations for display
        all_stations = []
        for stop in planner.gtfs_data.stops.values():
            all_stations.append({
                'name': stop.name,
                'platform': stop.platform_code,
                'lat': stop.lat,
                'lon': stop.lon
            })
        all_stations.sort(key=lambda x: x['name'])
        
        result = {
            'success': True,
            'journey': {
                'origin': {
                    'name': journey.origin.name,
                    'platform': journey.platform
                },
                'destination': {
                    'name': journey.destination.name
                },
                'mode': journey.mode,
                'route_name': journey.route_name,
                'departure_time': journey.departure_time.strftime('%H:%M'),
                'arrival_time': journey.arrival_time.strftime('%H:%M'),
                'duration_minutes': journey.duration_minutes,
                'transfers': journey.transfers
            },
            'stations': all_stations,
            'has_realtime': bool(planner.api_key)
        }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/stations')
def stations_page():
    """Page showing all available stations"""
    return render_template('stations.html')

if __name__ == '__main__':
    print("Starting PTV Journey Planner Web App...")
    print("Available at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)