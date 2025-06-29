from src.flightSearcher import FlightEngine, FlightSelection
from src.flight import Flight
from datetime import date, datetime

def main():
    DB = "flightsAPI"
    flightEngine = FlightEngine(DB)
    
    #print([Flight.model_validate(flight) for flight in flightEngine.retrieveAllFlights()])

    trip = FlightSelection(
        startDate=datetime(2025, 11, 1),
        endDate=datetime(2025, 11, 15),
        priceMax=200,
        startCity="Malaga",
        stayoversAllowed=False
    )

    print([Flight.model_validate(flight) for flight in flightEngine.retrieveFlights(trip)])

if __name__ == '__main__':
    main()