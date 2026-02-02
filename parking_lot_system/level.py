# Level class
from typing import Optional, Dict

from .models import ParkingSpot, Vehicle
from .enums import SpotType
from .config import SPOT_DISTRIBUTION

class Level:
    def __init__(self, level_id: int, capacity: int):
        self.level_id = level_id
        self.spots: list[ParkingSpot] = []
        self._initialize_spots(capacity)

    def _initialize_spots(self, capacity: int):
        # Use config for distribution
        motorcycle_count = int(capacity * SPOT_DISTRIBUTION['MOTORCYCLE'])  #bike spots are allocated based on the spot distribution(we can control it in config.py)
        compact_count = int(capacity * SPOT_DISTRIBUTION['COMPACT'])    #car spots are allocated based on the spot distribution(we can control it in config.py)
        large_count = capacity - motorcycle_count - compact_count

        spot_id = 1
        for _ in range(motorcycle_count):
            self.spots.append(ParkingSpot(spot_id, self.level_id, SpotType.MOTORCYCLE))
            spot_id += 1
        for _ in range(compact_count):
            self.spots.append(ParkingSpot(spot_id, self.level_id, SpotType.COMPACT))
            spot_id += 1
        for _ in range(large_count):
            self.spots.append(ParkingSpot(spot_id, self.level_id, SpotType.LARGE))
            spot_id += 1

    def find_suitable_spot(self, vehicle: Vehicle) -> Optional[ParkingSpot]:
        for spot in self.spots:
            if not spot.is_occupied and vehicle.can_fit_in_spot(spot.spot_type):
                return spot
        return None

    def get_available_count_by_type(self) -> Dict[SpotType, int]:
        counts = {t: 0 for t in SpotType}
        for spot in self.spots:
            if not spot.is_occupied:
                counts[spot.spot_type] += 1
        return counts