# Custom exceptions for better error handling
class ParkingException(Exception):
    pass

class ParkingFullException(ParkingException):
    pass

class InvalidSpotException(ParkingException):
    pass

class InvalidTicketException(ParkingException):
    pass

class SpotNotFoundException(ParkingException):
    pass

class VehicleAlreadyParkedException(ParkingException):
    pass