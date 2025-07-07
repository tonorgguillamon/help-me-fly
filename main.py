from src.flightSearcher import FlightEngine, FlightSelection
from src.flight import Flight
from datetime import date, datetime
import random
from src.ga.plan import *
import src.ga.ga_engine as ga_engine

def main():
    random.seed(50)
    DB = "flightsAPI"
    flightEngine = FlightEngine(DB)
    
    #print([Flight.model_validate(flight) for flight in flightEngine.retrieveAllFlights()])

    #trip = FlightSelection(
    #    startDate=datetime(2025, 11, 1),
    #    endDate=datetime(2025, 11, 15),
    #    priceMax=200,
    #    startCity="Malaga",
    #    stayoversAllowed=False
    #)

    #print([Flight.model_validate(flight) for flight in flightEngine.retrieveFlights(trip)])

    travellerA = Traveller(
    origin="Malaga",
    budget=300
    )

    travellerB = Traveller(
        origin="Madrid",
        budget=320
    )

    travellerC = Traveller(
        origin="Munich",
        budget=250
    )

    travellersTemplate = [
        travellerA,
        travellerB,
        travellerC
    ]

    travelPlan = TravelPlan(
        flightEngine=flightEngine,
        fromDate=date(2025, 9, 20),
        toDate=date(2025, 12, 15),
        priceMax=300,
        days=10,
        availableDestinations=[
            "London", "Paris", "Rotterdam", "Berlin",
            "Munich", "Vienna", "Krakow", "Budapest",
            "Rome", "Milan", "Copenhagen", "Hesinki",
            "Oslo", "Malta", "Porto", "Dublin"
        ],
    )

    gaEngine = ga_engine.GeneticAlgorithm(
        travellersTemplate=travellersTemplate,
        travelPlan=travelPlan,
    )

    gaEngine.run()

if __name__ == '__main__':
    main()