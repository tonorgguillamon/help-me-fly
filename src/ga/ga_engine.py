"""
Based on DEAP library
https://github.com/DEAP/deap
https://deap.readthedocs.io/en/master/

"""

from deap import base, creator, tools
import random
from src.ga.plan import *
from src.flightSearcher import FlightEngine

# Individual
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", Trip, fitness=creator.FitnessMin)

class GeneticAlgorithm:
    def __init__(self, travellersTemplate, travelPlan, populationSize=100, ngen=50, probCrossover=0.9, probMutate=0.2):
        self.populationSize = populationSize
        self.ngen = ngen
        self.travellersTemplate = travellersTemplate
        self.travelPlan = travelPlan

        self.coefProbCrossover = probCrossover
        self.coefProbMutate = probMutate

        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self.create_individual)
        self.toolbox.register("evaluate", self.evaluate_individual)
        self.toolbox.register("mate", self.mate_individuals)
        self.toolbox.register("mutate", self.mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def create_individual(self):
        individual = Trip(
            travellers=self.travellersTemplate,
            travelPlan=self.travelPlan
        )

        individual.selectRoutes()
        return individual

    def evaluate_individual(self, individual: Trip) -> tuple[float]:
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

    def mate_individuals(self, individual1: Trip, individual2: Trip, coef_prob: float = 0.9):
        """Swap a random slice of selectedRoutes between two individuals"""
        size = len(individual1.travellers)
        p1, p2 = sorted(random.sample(range(size), 2)) # takes two breaking points

        for i in range(p1, p2):
            individual1.travellers[i].selectedRoute, individual2.travellers[i].selectedRoute = (
                individual2.travellers[i].selectedRoute, individual1.travellers[i].selectedRoute
            )
        return individual1, individual2

    def mutate_individual(self, individual: Trip, coef_prob: float = 0.2):
        """ Randomly mutate an individual's selected routes with probability """
        for traveller in individual.travellers:
            newPotentialRoute = random.choice(traveller.potentialRoutes)
            if newPotentialRoute.flightsBack:
                newRoute = Route(
                    flightToGo=newPotentialRoute.flightToGo,
                    flightBack=random.choice(newPotentialRoute.flightsBack)
                )
                newRoute.cost = newRoute.flightToGo.price_eur + newRoute.flightBack.price_eur
                traveller.selectedRoute = newRoute
        return (individual,) # DEAP expects mutation functions to return a tuple of individuals
        # internally DEAP is built to handle pipelines where the operators are chained, and all operators return tuples for consistency 

    def run(self):
        bestInvididuals = []

        population = [self.toolbox.individual() for _ in range(self.populationSize)]
        
        for gen in range(self.ngen):
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))

            # apply crossover (mate) and mutation
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.coefProbCrossover:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
                
            for mutant in offspring:
                if random.random() < self.coefProbMutate:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.valus
            
            # reevaluate individuals with invalid fitness (those that suffered a modification)
            invalidIndividuals = [individual for individual in offspring if not individual.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalidIndividuals)

            for individual, fit in zip(invalidIndividuals, fitnesses):
                individual.fitness.values = fit
            
            population[:] = offspring

            best = tools.selBest(population, 1)[0]
            bestInvididuals.append(best.fitness.values[0])
        return bestInvididuals