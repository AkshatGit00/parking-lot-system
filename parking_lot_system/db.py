import sqlite3
from datetime import datetime
from typing import List, Dict, Tuple

from .models import ParkingSpot, Vehicle, Motorcycle, Car, Bus
from .enums import VehicleType, SpotType
from .exceptions import SpotNotFoundException, InvalidTicketException
from .level import Level   # assuming Level is in level.py

DB_FILE = 'parking.db'

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Allows row['column_name'] access
    return conn

def initialize_db(num_levels: int, spots_per_level: int) -> List[Level]:
    """
    Create tables if they don't exist.
    Populate levels and spots ONLY if the database is empty.
    Then always load the current state from DB.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create tables (safe to run multiple times)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS levels (
            id INTEGER PRIMARY KEY,
            capacity INTEGER NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level_id INTEGER NOT NULL,
            number INTEGER NOT NULL,
            type TEXT NOT NULL,
            occupied BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (level_id) REFERENCES levels(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parked_vehicles (
            spot_id INTEGER PRIMARY KEY,
            license_plate TEXT NOT NULL UNIQUE,
            vehicle_type TEXT NOT NULL,
            entry_time DATETIME NOT NULL,
            FOREIGN KEY (spot_id) REFERENCES spots(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_tickets (
            ticket_id TEXT PRIMARY KEY,
            spot_id INTEGER NOT NULL,
            FOREIGN KEY (spot_id) REFERENCES spots(id)
        )
    ''')

    # Check if levels already exist
    cursor.execute("SELECT COUNT(*) FROM levels")
    if cursor.fetchone()[0] == 0:
        # First-time initialization
        levels_list = [Level(i + 1, spots_per_level) for i in range(num_levels)]
        for level in levels_list:
            cursor.execute(
                "INSERT INTO levels (id, capacity) VALUES (?, ?)",
                (level.level_id, spots_per_level)
            )
            for spot in level.spots:
                cursor.execute("""
                    INSERT INTO spots (level_id, number, type, occupied)
                    VALUES (?, ?, ?, ?)
                """, (level.level_id, spot.number, spot.spot_type.name, 0))
        conn.commit()
        print(f"Initialized database with {num_levels} levels and {spots_per_level} spots per level.")

    conn.close()

    # Always load current state
    return load_from_db()

def load_from_db() -> List[Level]:
    """Load all data from database into memory structures."""
    conn = get_connection()
    cursor = conn.cursor()

    # Load levels
    cursor.execute("SELECT * FROM levels ORDER BY id")
    level_rows = cursor.fetchall()
    if not level_rows:
        conn.close()
        raise ValueError("No levels found in database. Database may be corrupted.")

    levels = []
    level_map: Dict[int, Level] = {}
    for row in level_rows:
        level = Level(row['id'], row['capacity'])
        level.spots = []
        levels.append(level)
        level_map[row['id']] = level

    # Load spots and attach to correct level
    cursor.execute("SELECT * FROM spots ORDER BY level_id, number")
    for row in cursor.fetchall():
        try:
            spot_type = SpotType[row['type']]
        except KeyError:
            print(f"Warning: Unknown spot type '{row['type']}' in DB - skipping spot")
            continue

        spot = ParkingSpot(row['number'], row['level_id'], spot_type)
        spot.is_occupied = bool(row['occupied'])
        level_map[row['level_id']].spots.append(spot)

    # Load parked vehicles
    vehicle_map: Dict[int, Vehicle] = {}
    cursor.execute("SELECT * FROM parked_vehicles")
    for row in cursor.fetchall():
        try:
            vtype = VehicleType[row['vehicle_type']]
        except KeyError:
            print(f"Warning: Unknown vehicle_type '{row['vehicle_type']}' in DB - skipping")
            continue

        if vtype == VehicleType.MOTORCYCLE:
            vehicle = Motorcycle(row['license_plate'])
        elif vtype == VehicleType.CAR:
            vehicle = Car(row['license_plate'])
        elif vtype == VehicleType.BUS:
            vehicle = Bus(row['license_plate'])
        else:
            continue

        vehicle.entry_time = datetime.fromisoformat(row['entry_time'])
        vehicle_map[row['spot_id']] = vehicle

    # Attach vehicles to spots (only occupied ones)
    cursor.execute("SELECT id, level_id, number FROM spots WHERE occupied = 1")
    for row in cursor.fetchall():
        spot_id = row['id']
        if spot_id in vehicle_map:
            level = level_map[row['level_id']]
            spot = next((s for s in level.spots if s.number == row['number']), None)
            if spot:
                spot.vehicle = vehicle_map[spot_id]
                spot.is_occupied = True  # enforce consistency

    conn.close()
    return levels

def save_park_to_db(level_id: int, spot_num: int, vehicle: Vehicle, ticket_id: str):
    """Save parking action to database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get spot_id
    cursor.execute("SELECT id FROM spots WHERE level_id=? AND number=?", (level_id, spot_num))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise SpotNotFoundException("Spot not found in database")
    spot_id = row['id']

    # Update spot
    cursor.execute("UPDATE spots SET occupied=1 WHERE id=?", (spot_id,))

    # Save vehicle (uses .name → 'MOTORCYCLE', 'CAR', 'BUS')
    cursor.execute("""
        INSERT OR REPLACE INTO parked_vehicles 
        (spot_id, license_plate, vehicle_type, entry_time) 
        VALUES (?, ?, ?, ?)
    """, (spot_id, vehicle.license_plate, vehicle.vehicle_type.name, vehicle.entry_time.isoformat()))

    # Save ticket
    cursor.execute("INSERT INTO active_tickets (ticket_id, spot_id) VALUES (?, ?)",
                   (ticket_id, spot_id))

    conn.commit()
    conn.close()

def save_unpark_to_db(ticket_id: str):
    """Remove parking data from database on unpark."""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Find spot_id from ticket
        cursor.execute("SELECT spot_id FROM active_tickets WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        if not row:
            raise InvalidTicketException(f"Ticket {ticket_id} not found in database")

        spot_id = row['spot_id']

        # Begin transaction explicitly for safety
        cursor.execute("BEGIN")

        # Update spot
        cursor.execute("UPDATE spots SET occupied = 0 WHERE id = ?", (spot_id,))

        # Delete vehicle
        cursor.execute("DELETE FROM parked_vehicles WHERE spot_id = ?", (spot_id,))

        # Delete ticket
        cursor.execute("DELETE FROM active_tickets WHERE ticket_id = ?", (ticket_id,))

        conn.commit()
        print(f"[DEBUG] Successfully unparked ticket {ticket_id} - removed from DB")

    except Exception as e:
        conn.rollback()
        print(f"[DEBUG] Unpark failed for ticket {ticket_id}: {str(e)}")
        raise
    finally:
        conn.close()