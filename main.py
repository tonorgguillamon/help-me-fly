from src.flightSearcher import FlightEngine, Trip
from src.flight import Flight
from datetime import date, datetime

def main():
    DB = "flightsAPI"
    flightEngine = FlightEngine(DB)
    
    #print([Flight.model_validate(flight) for flight in flightEngine.retrieveAllFlights()])

    trip = Trip(
        startDate=datetime(2025, 8, 1),
    )

if __name__ == '__main__':
    main()