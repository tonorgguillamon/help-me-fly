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
            fromDate: date,
            toDate: date,
            vetoCities: list[str] = None,
            preferredCities: list[str] = None,
            priceMax: int = None,
            days: int = None,
            allowStayover: bool = True,
            availableDestinations: list[str] = None
        ):
        
        self.flightEngine = flightEngine
        self.fromDate = fromDate
        self.toDate = toDate
        self.vetoCities = vetoCities
        self.priceMax = priceMax
        self.days = days
        self.allowStayover = allowStayover
        self.preferredCities = preferredCities
        self.availableDestinations = availableDestinations

    def createRoutes(self, originCity: str, destination: str) -> list[PotentialRoutes]:
        trip = FlightSelection(
            startDate=self.fromDate,
            endDate=self.toDate,
            priceMax=self.priceMax,
            startCity=originCity,
            destinationCity=destination,
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
                startCity=destination,
                destinationCities=originCity,
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

class Trip:
    """ This is the Individual for the Genetic Algorithm """
    def __init__(self, travellers: list[Traveller], travelPlan: TravelPlan):
        self.travellers = copy.deepcopy(travellers)

        """ Generating routes here allows to fix the destination for all the travellers """
        self.chosenDestination = random.choice(travelPlan.availableDestinations)

        for traveller in self.travellers:
            traveller.potentialRoutes = travelPlan.createRoutes(
                traveller.origin,
                self.chosenDestination
            )

    def selectRoutes(self):
        for traveller in self.travellers:
            potentialRoute = random.choice(traveller.potentialRoutes)
            route = Route(
                flightToGo=potentialRoute.flightToGo,
                flightBack=random.choice(potentialRoute.flightsBack),
            )
            route.cost = route.flightToGo.price_eur + route.flightBack.price_eur
            traveller.selectedRoute = route

    def deltaTime(self, arrival: bool = True): # arrival or leaving
        deltas = []
        if arrival:
            times = [traveller.selectedRoute.flightToGo.arrival_time_local for traveller in self.travellers]
        else: # then, leaving
            times = [traveller.selectedRoute.flightBack.departure_time_local for traveller in self.travellers]

        times.sort()
        
        deltas = [abs(times[i+1] - times[i]) for i in range(len(times)-1)]
        # approximation -> the goal is to lower deltas, not to be accurate in calculating all deltas

        """ The following logic is more understandable, but way slower:
        n_travelers = len(times)
        for i in range(n_travelers):
            for j in range(i+1,n_travelers):
                delta = abs(times[i] - times[j])
                deltas.append(delta)
        """
        
        return sum(deltas)
    
    def deltaBudget(self):
        return sum(abs(traveller.budget - traveller.selectedRoute.cost) for traveller in self.travellers)
    
    def isPreferredDestination(self, preferredDestinations: list[str]) -> bool:
        return self.chosenDestination in preferredDestinations
    
    def calculateDeparturesSuitability(self) -> int:
        badDepartures = 0
        for traveller in self.travellers:
            if traveller.selectedRoute.flightToGo.departure_date.weekday() == 6:
                """ Starting trip on Sunday -> wasting weekend """
                badDepartures+=1
            if traveller.selectedRoute.flightBack.departure_date.weekday() in [4, 5]:
                """ Coming back on Friday or Saturday -> wasting weekend """
                badDepartures+=1
        return badDepartures
    
    def calculateNumStayovers(self) -> int:
        return sum(traveller.selectedRoute.flightToGo.stayovers + traveller.selectedRoute.flightBack.stayovers for traveller in self.travellers)

# Within preferred destinations
# Arrival time close
# Matching budget
# Number of days
# Around weekends, national holidays - no starting trip on sundays nor flying back on saturdays
# Stayover min