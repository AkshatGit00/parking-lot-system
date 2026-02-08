# Main ParkingLot class
from typing import Dict, Tuple

from .db import save_park_to_db, save_unpark_to_db, get_connection
from .models import Vehicle, ParkingSpot, ParkingTicket
from .level import Level
from .enums import VehicleType
from .exceptions import (
    ParkingFullException,
    InvalidTicketException,
    SpotNotFoundException,
    InvalidSpotException,
    VehicleAlreadyParkedException  # ← New exception we'll define/use
)
from .config import HOURLY_FEE_RATE

class ParkingLot:
    def __init__(self, num_levels: int, spots_per_level: int):
        """
        Initialize the parking lot by loading from database (or creating if empty).
        """
        self.levels: list[Level] = self._initialize_levels(num_levels, spots_per_level)
        self.active_tickets: Dict[str, Tuple[int, int]] = self._load_active_tickets()

    def _initialize_levels(self, num_levels: int, spots_per_level: int) -> list[Level]:
        """Delegate to db layer for initialization/loading."""
        from .db import initialize_db
        return initialize_db(num_levels, spots_per_level)

    def _load_active_tickets(self) -> Dict[str, Tuple[int, int]]:
        """Load active tickets from DB into memory."""
        conn = get_connection()
        cursor = conn.cursor()
        tickets: Dict[str, Tuple[int, int]] = {}

        cursor.execute("""
            SELECT at.ticket_id, s.level_id, s.number
            FROM active_tickets at
            JOIN spots s ON at.spot_id = s.id
        """)
        for row in cursor.fetchall():
            tickets[row['ticket_id']] = (row['level_id'], row['number'])

        conn.close()
        return tickets

    def park_vehicle(self, vehicle: Vehicle) -> str:
        """
        Park a vehicle if space is available and vehicle is not already parked.
        Returns ticket_id on success.
        """
        # Step 1: Prevent duplicate parking of same license plate
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM parked_vehicles WHERE license_plate = ?",
                       (vehicle.license_plate,))
        if cursor.fetchone() is not None:
            conn.close()
            raise VehicleAlreadyParkedException(
                f"Vehicle with license plate {vehicle.license_plate} is already parked!"
            )
        conn.close()

        # Step 2: Find suitable spot
        for level in self.levels:
            spot: ParkingSpot | None = level.find_suitable_spot(vehicle)
            if spot:
                spot.park(vehicle)  # Updates spot.vehicle and is_occupied in memory

                # Create ticket
                ticket = ParkingTicket()
                self.active_tickets[ticket.ticket_id] = (level.level_id, spot.number)

                # Persist to database
                save_park_to_db(level.level_id, spot.number, vehicle, ticket.ticket_id)

                return ticket.ticket_id

        raise ParkingFullException("No suitable spot available for this vehicle type")

    def unpark_vehicle(self, ticket_id: str) -> str:
        """
        Unpark vehicle using ticket_id.
        Returns fee message on success.
        """
        if ticket_id not in self.active_tickets:
            raise InvalidTicketException("Invalid or expired ticket")

        level_id, spot_num = self.active_tickets.pop(ticket_id)

        level = self.levels[level_id - 1]  # assuming level_id starts from 1
        spot: ParkingSpot | None = next(
            (s for s in level.spots if s.number == spot_num), None
        )

        if not spot:
            raise SpotNotFoundException(f"Spot {spot_num} on level {level_id} not found")

        # Calculate fee and unpark in memory
        fee = spot.unpark(HOURLY_FEE_RATE)

        # Persist unpark to database
        save_unpark_to_db(ticket_id)

        from parking_lot_system.db import get_connection
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT license_plate, vehicle_type FROM parked_vehicles")
        remaining = cursor.fetchall()
        print("Remaining parked vehicles in DB after this unpark:", remaining)
        conn.close()

        return f"Vehicle unparked successfully. Total fee: ${fee:.2f}"

    def get_parking_status(self) -> dict:
        """Return occupancy summary for API - with string keys."""
        status = {}
        for level in self.levels:
            avail_raw = level.get_available_count_by_type()  # returns {SpotType: int}
        
            # Convert enum keys to strings
            avail_str = {spot_type.name: count for spot_type, count in avail_raw.items()}
            # or use .value if you prefer display names: {spot_type.value: count for ...}

            status[f'level_{level.level_id}'] = {
                'available_spots': avail_str,
                'total_spots': len(level.spots),
                'occupied_count': sum(1 for s in level.spots if s.is_occupied)
            }
        return status