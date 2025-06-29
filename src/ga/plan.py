from src.flight import FlightSelection, Flight
from src.flightSearcher import FlightEngine
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta

class Route(BaseModel):
    flightToGo: Flight
    flightsBack: list[Flight]

class Traveller(BaseModel):
    origin: str
    budget: float = 0
    routes: list[Route]

class TravelPlan:
    def __init__(
            self,
            flightEngine: FlightEngine,
            travellers: list[Traveller],
            destinationCities: list[str],
            fromDate: date,
            toDate: date,
            vetoCities: list[str] = None,
            priceMax: int = None,
            days: int = None,
            allowStayover: bool = True
        ):
        
        self.flightEngine = flightEngine
        self.destinationCities = destinationCities
        self.fromDate = fromDate
        self.toDate = toDate
        self.vetoCities = vetoCities
        self.priceMax = priceMax
        self.days = days
        self.allowStayover = allowStayover

    def createRoute(self, originCity: str):
        trip = FlightSelection(
            startDate=self.fromDate,
            endDate=self.toDate,
            priceMax=self.priceMax,
            startCity=originCity,
            vetoDestinations=self.vetoCities,
            stayoversAllowed=self.allowStayover
        )

        goingFlights = self.flightEngine.retrieveFlights(trip)
        
        routes = []
        for goingFlight in goingFlights:
            trip = FlightSelection(
                startDate=goingFlight.departure_date + timedelta(days=1),
                endDate=goingFlight.departure_date + timedelta(days=self.days),
                priceMax=self.priceMax - goingFlight.price_eur,
                startCity=goingFlight.to_city,
                destinationCity=originCity,
                stayoversAllowed=self.allowStayover
            )

            flightsBack = self.flightEngine.retrieveFlights(trip)

            route = Route(
                flightToGo=goingFlight,
                flightsBack=flightsBack
            )

            if flightsBack:
                routes.append(route)

        return routes
    
    def createRoutesForTraveller(self, traveller: Traveller):
        traveller.routes = self.createRoute(originCity=traveller.origin)


# Within preferred destinations
# Arrival time close
# Matching budget
# Number of days
# Around weekends, national holidays - no starting trip on sundays nor flying back on saturdays
# Stayover min