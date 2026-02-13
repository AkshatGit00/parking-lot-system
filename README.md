# Parking Lot Management System

A clean, modular, and production-ready Low-Level Design (LLD) implementation of a **multi-level parking lot system** in Python.  
Originally an in-memory OOP design, now enhanced with **SQLite persistence**, data integrity checks, a RESTful APIs and robust error handling — perfect for demonstrating full backend capabilities in coding interviews and software developer roles.

## Features

- Multi-level parking with configurable number of levels and spots per level
- Supported vehicle types: Motorcycle, Car, Bus
- Spot types: Motorcycle, Compact, Large
- Vehicle-spot compatibility rules:
  - Motorcycle → fits any spot
  - Car → fits Compact or Large
  - Bus → fits only Large (occupies 5 consecutive large spots in a row)
- Ticket-based entry/exit system with unique ticket IDs
- Time-based fee calculation (configurable hourly rate)
- Custom exceptions for clear error handling (ParkingFull, InvalidTicket, SpotNotFound, VehicleAlreadyParked, etc.)
- **Persistent storage** using SQLite — parking state survives program restarts
- Duplicate parking prevention — same license plate cannot be parked twice without unparking
- Modular, OOP/SOLID-compliant design with type hints and separation of concerns
- REST API (Flask) for external access

## Project Structure
```python
parking_lot_system/
├── init.py
├── config.py               # Fee rate, spot distribution percentages
├── enums.py                # VehicleType, SpotType
├── exceptions.py           # Custom exceptions (ParkingFull, InvalidSpot, etc.)
├── models.py               # Vehicle (abstract), Car/Bus/Motorcycle, ParkingSpot, ParkingTicket
├── level.py                # Level class – manages spots on one floor
├── parking_lot.py          # Main ParkingLot class – coordinates everything
├── db.py                   # SQLite database layer (init, load, save park/unpark)
main.py                     # Example usage & Console demo script (outside package)
app.py                      # API server demo script (outside package)
requirement.txt             # Required package to run the API server demo script
```

- `parking.db` — SQLite database file (auto-created on first run)

## Technologies & Skills Demonstrated

- **Language**: Python 3
- **Core Concepts**: OOP, SOLID principles, Type Hints, Exception Handling, Encapsulation
- **Persistence**: SQLite (serverless, lightweight)
- **Data Integrity**: UNIQUE constraint on license_plate, explicit duplicate checks
- **Tools**: Flask (REST API), Git, modular package structure

## Run the project

- Console demo:
python main.py

- API server:
python app.py

- Test with curl or Postman
