# Enums for VehicleType and SpotType used in the Parking Lot Management System
from enum import Enum

class VehicleType(Enum):
    """
    Vehicle types supported by the parking system.
    The .value is the human-readable/display name.
    The .name (uppercase) is stored in the database for consistency.
    """
    MOTORCYCLE = "Motorcycle"
    CAR        = "Car"
    BUS        = "Bus"


class SpotType(Enum):
    """
    Parking spot size/capacity types.
    The .value is the human-readable/display name.
    The .name (uppercase) is stored in the database.
    """
    MOTORCYCLE = "Motorcycle"
    COMPACT    = "Compact"
    LARGE      = "Large"