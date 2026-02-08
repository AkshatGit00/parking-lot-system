# app.py - Flask RESTful API for Parking Lot System
from flask import Flask, request, jsonify  # Core Flask imports
import uuid  # For generating ticket IDs (already in your code)
from datetime import datetime  # For entry times

# Import your project modules
from parking_lot_system import ParkingLot, Car, Bus, Motorcycle  # Core classes
from parking_lot_system.exceptions import (
    ParkingFullException, InvalidTicketException, SpotNotFoundException,
    VehicleAlreadyParkedException  # Your custom exceptions
)

# Step 1: Create Flask app instance
app = Flask(__name__)  # __name__ is a Python magic variable; use 'app' to refer to this server

# Step 2: Initialize ParkingLot (loads from DB automatically via your db.py)
lot = ParkingLot(num_levels=2, spots_per_level=10)  # Same config as main.py; persists via DB

# Step 3: Define Routes (Endpoints)
@app.route('/park', methods=['POST'])  # POST for creating a new parking entry
def park_vehicle_api():
    """
    Park a vehicle.
    Request: JSON with {'vehicle_type': 'CAR', 'license_plate': 'ABC123'}
    Response: {'ticket_id': 'uuid-string'} or error
    """
    # Get JSON data from request body
    data = request.get_json()  # Parses incoming JSON automatically
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400  # 400 Bad Request

    # Validate required fields
    vehicle_type = data.get('vehicle_type', '').upper()  # e.g., 'car' → 'CAR'
    license_plate = data.get('license_plate')
    if not vehicle_type or not license_plate:
        return jsonify({'error': 'Missing vehicle_type or license_plate'}), 400

    # Create vehicle object based on type (mirrors your models)
    try:
        if vehicle_type == 'CAR':
            vehicle = Car(license_plate)
        elif vehicle_type == 'BUS':
            vehicle = Bus(license_plate)
        elif vehicle_type == 'MOTORCYCLE':
            vehicle = Motorcycle(license_plate)
        else:
            return jsonify({'error': f'Invalid vehicle_type: {vehicle_type}. Must be CAR, BUS, or MOTORCYCLE'}), 400

        # Call your core logic
        ticket_id = lot.park_vehicle(vehicle)
        return jsonify({'ticket_id': ticket_id, 'message': f'Vehicle {license_plate} parked successfully'}), 201  # 201 Created

    except VehicleAlreadyParkedException as e:
        return jsonify({'error': str(e)}), 409  # 409 Conflict
    except ParkingFullException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:  # Catch-all for unexpected errors
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/unpark', methods=['POST'])
def unpark_vehicle_api():
    """
    Unpark a vehicle.
    Request: JSON with {'ticket_id': 'uuid-string'}
    Response: {'message': 'Unparked. Fee: $X.XX'} or error
    """
    data = request.get_json()
    if not data or 'ticket_id' not in data:
        return jsonify({'error': 'Missing ticket_id'}), 400

    ticket_id = data['ticket_id']
    try:
        result = lot.unpark_vehicle(ticket_id)
        return jsonify({'message': result}), 200  # 200 OK
    except InvalidTicketException as e:
        return jsonify({'error': str(e)}), 404  # 404 Not Found
    except SpotNotFoundException as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/availability', methods=['GET'])
def get_availability():
    """
    Get current spot availability.
    Response: JSON with levels and available spots by type
    No request body needed.
    """
    # Use your existing status method (add if not present; see below)
    status = lot.get_parking_status()  # Assuming you added this helper
    return jsonify(status), 200

# Step 4: Run the server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)  # debug=True for hot-reload; host/port for access