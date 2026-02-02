# Enums for VehicleType and SpotType
from enum import Enum

class VehicleType(Enum):
    MOTORCYCLE = "Motorcycle"
    CAR = "Car"
    BUS = "Bus"

class SpotType(Enum):
    MOTORCYCLE = "Motorcycle"
    COMPACT = "Compact"
    LARGE = "Large"