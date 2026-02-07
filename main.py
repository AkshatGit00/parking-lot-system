# Example usage script
from parking_lot_system import ParkingLot, Car, Bus, Motorcycle
from parking_lot_system.exceptions import *

if __name__ == "__main__":
    lot = ParkingLot(num_levels=2, spots_per_level=10)  # main class
    #lot = ParkingLot(num_levels=1, spots_per_level=2)  # main class(less number of spots in parking space)
    
    try:
        car = Car("ABC123") #Car class object has been initialised with license Plate num = "ABC123" 
        ticket1 = lot.park_vehicle(car) #returns ticket ID
        print(f"Car parked with ticket: {ticket1}")
       
        bus = Bus("XYZ789")
        ticket2 = lot.park_vehicle(bus)
        print(f"Bus parked with ticket: {ticket2}")

        motorcycle = Motorcycle("QWE456")
        ticket3 = lot.park_vehicle(motorcycle)
        print(f"Motorcycle parked with ticket: {ticket3}")
        
        # Unpark
        print(lot.unpark_vehicle(ticket1))
        print(f"Vehicle is unparked with ticket: {ticket1}")
        
        # Unpark
        print(lot.unpark_vehicle(ticket2))
        print(f"Vehicle is unparked with ticket: {ticket2}")

        # Unpark
        print(lot.unpark_vehicle(ticket3))
        print(f"Vehicle is unparked with ticket: {ticket3}")
        
        motorcycle = Motorcycle("QWE457")
        ticket4 = lot.park_vehicle(motorcycle)
        print(f"Motorcycle parked with ticket: {ticket4}")

        bus = Bus("XYZ013")
        ticket5 = lot.park_vehicle(bus)
        print(f"Bus parked with ticket: {ticket5}")

        # Unpark
        print(lot.unpark_vehicle(ticket4))
        print(f"Vehicle is unparked with ticket: {ticket4}")

        # Invalid unpark
        print(lot.unpark_vehicle("fake_ticket"))

    except (ParkingFullException, InvalidSpotException, InvalidTicketException, VehicleAlreadyParkedException) as e:
        print(f"Error: {str(e)}")