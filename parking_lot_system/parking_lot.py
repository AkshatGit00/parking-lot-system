# Main ParkingLot class
from typing import Dict, Tuple

from .level import Level
from .models import Vehicle, ParkingSpot, ParkingTicket
from .exceptions import ParkingFullException, InvalidTicketException, SpotNotFoundException
from .config import HOURLY_FEE_RATE

class ParkingLot:
    def __init__(self, num_levels: int, spots_per_level: int):
        self.levels = [Level(i + 1, spots_per_level) for i in range(num_levels)]    #has info of spot number at each level, stores level ID and spot number
        self.active_tickets: Dict[str, Tuple[int, int]] = {}  # ticket_id -> (level_id, spot_number). Dictionary[Key, Value]

    def park_vehicle(self, vehicle: Vehicle) -> str:
        for level in self.levels:
            spot = level.find_suitable_spot(vehicle)
            if spot:
                spot.park(vehicle)
                ticket = ParkingTicket()    #ticket stores the information of ticket ID and time when ticket is issued
                self.active_tickets[ticket.ticket_id] = (level.level_id, spot.number)   #for each ticket ID we have corresponding level ID and spot number
                return ticket.ticket_id
        raise ParkingFullException("No space available for this vehicle")   #if none of the spot is available then return error

    def unpark_vehicle(self, ticket_id: str) -> str:
        if ticket_id not in self.active_tickets:
            raise InvalidTicketException("Invalid ticket")  #return error if Key(Ticket ID) not found in buffer

        level_id, spot_num = self.active_tickets.pop(ticket_id)     #Pop out the values(Level ID, Spot Num) from Dictionary for given Key(Ticket ID)
        level = self.levels[level_id - 1]   #here '-1' is because level ID is stored with '+1'(check __init__)

        #here spot can be instance of ParkingSpot if we spot is found or it can be None if spot is not found
        spot: ParkingSpot = next((s for s in level.spots if s.number == spot_num), None)
        if not spot:
            raise SpotNotFoundException("Spot not found")   #return error if spot is not found

        fee = spot.unpark(HOURLY_FEE_RATE)  #get the ticket price based on the fee model
        return f"Vehicle unparked. Fee: ${fee:.2f}" #currently there is no payment integration, we just provide the ticket price