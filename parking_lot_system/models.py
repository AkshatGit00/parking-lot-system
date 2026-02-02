# Core data models: Vehicle subclasses, ParkingSpot, ParkingTicket (added for completeness)
from abc import ABC, abstractmethod
from datetime import datetime
import uuid

from .enums import VehicleType, SpotType
from .exceptions import InvalidSpotException

class Vehicle(ABC):
    def __init__(self, license_plate: str, vtype: VehicleType):
        self.license_plate = license_plate
        self.vehicle_type = vtype
        self.entry_time = None  # Set when parked

    @abstractmethod
    def can_fit_in_spot(self, spot_type: SpotType) -> bool:
        pass

class Motorcycle(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.MOTORCYCLE)

    def can_fit_in_spot(self, spot_type: SpotType) -> bool:
        return True  # Fits everywhere

class Car(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.CAR)

    def can_fit_in_spot(self, spot_type: SpotType) -> bool:
        return spot_type in (SpotType.COMPACT, SpotType.LARGE)

class Bus(Vehicle):
    def __init__(self, license_plate: str):
        super().__init__(license_plate, VehicleType.BUS)

    def can_fit_in_spot(self, spot_type: SpotType) -> bool:
        return spot_type == SpotType.LARGE

class ParkingSpot:
    def __init__(self, number: int, level: int, spot_type: SpotType):
        self.number = number
        self.level = level
        self.spot_type = spot_type
        self.is_occupied = False
        self.vehicle = None

    def park(self, vehicle: Vehicle) -> bool:
        if self.is_occupied:
            raise InvalidSpotException("Spot is already occupied")
        if not vehicle.can_fit_in_spot(self.spot_type):
            raise InvalidSpotException("Vehicle cannot fit in this spot")

        self.vehicle = vehicle
        self.is_occupied = True
        vehicle.entry_time = datetime.now()
        return True

    def unpark(self, fee_rate: float) -> float:
        if not self.is_occupied:
            return 0.0

        duration_hours = (datetime.now() - self.vehicle.entry_time).total_seconds() / 3600
        fee = round(duration_hours * fee_rate, 2)

        self.vehicle = None
        self.is_occupied = False
        return fee

class ParkingTicket:
    def __init__(self):
        self.ticket_id = str(uuid.uuid4())
        self.issue_time = datetime.now()