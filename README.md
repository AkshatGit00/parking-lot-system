# Parking Lot Management System

A clean, modular, and extensible **Low-Level Design (LLD)** implementation of a multi-level parking lot system in Python.

This project demonstrates core **Object-Oriented Programming** principles, type safety, exception handling, and clean architecture — commonly asked in system design / coding interviews.

## Features

- Multi-level parking lot with configurable number of levels and spots per level
- Different **vehicle types**: Motorcycle, Car, Bus
- Different **spot types**: Motorcycle, Compact, Large
- Realistic **compatibility rules**:
  - Motorcycle → fits in any spot
  - Car → fits in Compact or Large
  - Bus → fits only in Large
- Time-based parking fee calculation (configurable hourly rate)
- Ticket-based entry/exit system
- Proper error handling with custom exceptions
- Modular package structure following separation of concerns
- Type hints for better readability and static analysis

## Project Structure
parking_lot_system/
├── init.py
├── config.py               # Fee rate, spot distribution percentages
├── enums.py                # VehicleType, SpotType
├── exceptions.py           # Custom exceptions (ParkingFull, InvalidSpot, etc.)
├── models.py               # Vehicle (abstract), Car/Bus/Motorcycle, ParkingSpot, ParkingTicket
├── level.py                # Level class – manages spots on one floor
├── parking_lot.py          # Main ParkingLot class – coordinates everything
└── main.py                 # Example usage & demo script (outside package)
