from src.flight import FlightSelection, Flight
from src.flightSearcher import FlightEngine
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
import random
import copy

class PotentialRoutes(BaseModel):
    flightToGo: Flight
    flightsBack: list[Flight]

class Route(BaseModel):
    flightToGo: Flight
    flightBack: Flight
    cost: Optional[float] = None

class Traveller(BaseModel):
    origin: str
    budget: float = 0
    potentialRoutes: Optional[list[PotentialRoutes]] = None
    selectedRoute: Optional[Route] = None

class TravelPlan:
    def __init__(
            self,
            flightEngine: FlightEngine,
            travellers: list[Traveller],
            fromDate: date,
            toDate: date,
            vetoCities: list[str] = None,
            preferredCities: list[str] = None,
            priceMax: int = None,
            days: int = None,
            allowStayover: bool = True
        ):
        
        self.flightEngine = flightEngine
        self.fromDate = fromDate
        self.toDate = toDate
        self.vetoCities = vetoCities
        self.priceMax = priceMax
        self.days = days
        self.allowStayover = allowStayover
        self.travellers = travellers
        self.preferredCities = preferredCities

        self.destinationCities = []

    def createRoute(self, originCity: str, destinations: list[str] = []):
        trip = FlightSelection(
            startDate=self.fromDate,
            endDate=self.toDate,
            priceMax=self.priceMax,
            startCity=originCity,
            destinationCity=destinations,
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

            route = PotentialRoutes(
                flightToGo=goingFlight,
                flightsBack=flightsBack
            )

            if flightsBack:
                routes.append(route)

        return routes
    
    def createRoutesForTraveller(self, traveller: Traveller):
        traveller.potentialRoutes = self.createRoute(
            originCity=traveller.origin,
            destinationCity=self.destinationCities
            )

    def createAllRoutes(self):
        for traveller in self.travellers:
            self.createRoutesForTraveller(traveller)
            if len(self.destinationCities) == 0: # the first traveller defines the destinations
                self.destinationCities = [route.flightToGo.to_city for route in traveller.potentialRoutes]

class Trip:
    """ This is the Individual for the Genetic Algorithm """
    def __init__(self, travellers: list[Traveller]):
        self.travellers = copy.deepcopy(travellers)
        random.shuffle(self.travellers) # to add more randomness
        
        self.chosenDestination = ""

    def selectRoutes(self):
        """ First travel leads the destination city """
        leadTraveller = self.travellers[0]
        potentialRoute = random.choice(leadTraveller.potentialRoutes)
        route = Route(
                flightToGo=potentialRoute.flightToGo,
                flightBack=random.choice(potentialRoute.flightsBack),
            )

        route.cost = route.flightToGo.price_eur + route.flightBack.price_eur
        leadTraveller.selectedRoute = route

        self.chosenDestination = route.flightToGo.to_city

        for traveler in self.travellers[1:]:
            matchingRoutes = [r for r in traveler.potentialRoutes if r.flightToGo.to_city == self.chosenDestination]
            
            if matchingRoutes:
                potentialRoute = random.choice(matchingRoutes)
                route = Route(
                    flightToGo=potentialRoute.flightToGo,
                    flightBack=random.choice(potentialRoute.flightsBack),
                )

                route.cost = route.flightToGo.price_eur + route.flightBack.price_eur
                traveler.selectedRoute = route
            else:
                traveler.selectedRoute = None #TODO: decide what to do here!
                
    def deltaTime(self, arrival: bool = True): # arrival or leaving
        deltas = []
        if arrival:
            times = [traveler.selectedRoute.flightToGo.arrival_time_local for traveler in self.travellers]
        else: # then, leaving
            times = [traveler.selectedRoute.flightBack.departure_time_local for traveler in self.travellers]

        n_travelers = len(times)

        for i in range(n_travelers):
            for j in range(i+1,n_travelers):
                delta = abs(times[i] - times[j])
                deltas.append(delta)
        
        return sum(deltas)
    
    def isPreferredDestination(self, preferredDestinations: list[str]) -> bool:
        return self.chosenDestination in preferredDestinations
    
    def calculateDepartureSuitability(self) -> int:
        badDepartures = 0
        for traveler in self.travellers:
            if traveler.selectedRoute.flightToGo.departure_date.weekday() == 6:
                """ Starting trip on Sunday -> wasting weekend """
                badDepartures+=1
            if traveler.selectedRoute.flightBack.departure_date.weekday() in [4, 5]:
                """ Coming back on Friday or Saturday -> wasting weekend """

# Within preferred destinations
# Arrival time close
# Matching budget
# Number of days
# Around weekends, national holidays - no starting trip on sundays nor flying back on saturdays
# Stayover min