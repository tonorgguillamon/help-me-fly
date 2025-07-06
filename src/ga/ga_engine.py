"""
Based on DEAP library
https://github.com/DEAP/deap
https://deap.readthedocs.io/en/master/

"""

from deap import base, creator, tools
import random
from src.ga.plan import *

# Individual
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", Trip, fitness=creator.FitnessMin)

# Toolbox
toolbox = base.Toolbox()

def create_individual(travellersTemplate: list[Traveller], travelPlan: TravelPlan):
    individual = Trip(
        travellers=travellersTemplate,
        travelPlan=travelPlan
    )

    individual.selectRoutes()
    return individual

def evaluate_individual(individual: Trip) -> tuple[float]:
    totalCost = sum(traveller.selectedRoute.cost for traveller in individual.travellers)
    deltaBudget = individual.deltaBudget()
    deltaTimeArrival = individual.deltaTime(arrival=True)
    deltaTimeBack = individual.deltaTime(arrival=False)
    preferredDestination = 0 if individual.isPreferredDestination() else 1
    depaturesSuitability = individual.calculateDeparturesSuitability()
    numStayovers = individual.calculateNumStayovers()

    penalization = (
        totalCost
        + deltaBudget
        + deltaTimeArrival
        + deltaTimeBack
        + preferredDestination
        + depaturesSuitability
        + numStayovers
    )

    return (penalization, )

def mate_individuals(individual1: Trip, individual2: Trip, coef_prob: float = 0.9):
    """Swap a random slice of selectedRoutes between two individuals with probability"""
    if random.random() < coef_prob:
        size = len(individual1.travellers)
        p1, p2 = sorted(random.sample(range(size), 2)) # takes two breaking points

        for i in range(p1, p2):
            individual1.travellers[i].selectedRoute, individual2.travellers[i].selectedRoute = (
                individual2.travellers[i].selectedRoute, individual1.travellers[i].selectedRoute
            )
    return individual1, individual2


toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evaluate_individual)
toolbox.register("mate", mate_individuals)
toolbox.register("mutate", mutate)
toolbox.register("individual", create_individual, travellersTemplate, travelPlan)