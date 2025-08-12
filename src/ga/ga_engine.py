"""
Based on DEAP library
https://github.com/DEAP/deap
https://deap.readthedocs.io/en/master/

"""

from deap import base, creator, tools
import random
from src.ga.plan import *
from src.flightSearcher import FlightEngine
import multiprocessing
from functools import partial

# Individual
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", Trip, fitness=creator.FitnessMin)

class GeneticAlgorithm:
    def __init__(self, travellersTemplate, travelPlan, flightEngine, populationSize=5, ngen=1, probCrossover=0.9, probMutate=0.2):
        self.populationSize = populationSize
        self.ngen = ngen
        self.travellersTemplate = travellersTemplate
        self.travelPlan = travelPlan
        self.flightEngine = flightEngine

        self.coefProbCrossover = probCrossover
        self.coefProbMutate = probMutate

        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", partial(self.create_individual, self.flightEngine))
        self.toolbox.register("evaluate", self.evaluate_individual)
        self.toolbox.register("mate", self.mate_individuals)
        self.toolbox.register("mutate", self.mutate_individual)
        self.toolbox.register("select", tools.selTournament, tournsize=3)

    def create_individual(self, flightEngine: FlightEngine):
        individual = creator.Individual(
            travellers=self.travellersTemplate,
            plan=self.travelPlan
        )

        individual.createPotentialRoutes(plan=self.travelPlan, flightEngine=flightEngine)
        if any(not traveller.potentialRoutes for traveller in individual.travellers):
            return None # there is no flight to the chosen destination for at least one traveller
        individual.selectRoutes()
        return individual

    def evaluate_individual(self, individual: Trip) -> tuple[float]:
        totalCost = sum(traveller.selectedRoute.cost for traveller in individual.travellers)
        deltaBudget = individual.deltaBudget()
        deltaTimeArrival = individual.deltaTime(arrival=True)
        deltaTimeBack = individual.deltaTime(arrival=False)
        depaturesSuitability = individual.calculateDeparturesSuitability()
        numStayovers = individual.calculateNumStayovers()

        print("RAW VALUES: \n" \
        f"Total Cost: {totalCost} \n" \
        f"Delta Budget: {deltaBudget} \n" \
        f"Delta Time Arrival: {deltaTimeArrival} \n" \
        f"Delta Time Back: {deltaTimeBack} \n" \
        f"Departure Suitability: {depaturesSuitability} \n" \
        f"Number Stayovers: {numStayovers} \n" \
        "------------------------------------------------ \n"
        )

        # Normalization:
        totalCost /= 1000 * len(individual.travellers)
        deltaBudget /= 500 * len(individual.travellers)
        deltaTimeArrival = 3600 * 24 * len(individual.travellers) # 24 hours deviation, in seconds
        deltaTimeBack = 3600 * 24 * len(individual.travellers)
        depaturesSuitability /= len(individual.travellers)*2
        numStayovers /= len(individual.travellers)*4 # 4 stayovers per traveller is already extreme

        penalization = (
            totalCost
            + deltaBudget
            + deltaTimeArrival
            + deltaTimeBack
            + depaturesSuitability
            + numStayovers
        )

        print("NORMALIZED VALUES: \n" \
        f"Total Cost: {totalCost} \n" \
        f"Delta Budget: {deltaBudget} \n" \
        f"Delta Time Arrival: {deltaTimeArrival} \n" \
        f"Delta Time Back: {deltaTimeBack} \n" \
        f"Departure Suitability: {depaturesSuitability} \n" \
        f"Number Stayovers: {numStayovers} \n" \
        " ---------------------------------------------- \n"
        )

        return (penalization, )

    def mate_individuals(self, individual1: Trip, individual2: Trip):
        """Swap the chosen destination from two individuals and recalculate potential routes 
        From the potential routes select from scratch the routes. It's not the traditional mating
        however, since all travellers must have the same destination it's not possible to
        swap travellers from individuals """
        tempDestination = individual1.chosenDestination

        individual1.chosenDestination = individual2.chosenDestination
        individual2.chosenDestination = tempDestination

        individual1.createPotentialRoutes(self.travelPlan, self.flightEngine)
        individual1.selectRoutes()

        individual2.createPotentialRoutes(self.travelPlan, self.flightEngine)
        individual2.selectRoutes()

        return individual1, individual2

    def mutate_individual(self, individual: Trip, coef_prob: float = 0.2):
        """ Randomly mutate an individual's selected routes 
        Takes a different potential route, and regenerates the flight to go and the flight to come back """
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
        bestInvididualsScore = []
        population = []

        for _ in range(self.populationSize):
            individual = self.toolbox.individual()
            if individual:
                population.append(individual)
        
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
                    del mutant.fitness.values
            
            # reevaluate individuals with invalid fitness (those that suffered a modification)
            invalidIndividuals = [individual for individual in offspring if not individual.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalidIndividuals)

            for individual, fit in zip(invalidIndividuals, fitnesses):
                individual.fitness.values = fit
            
            population[:] = offspring

            best = tools.selBest(population, 1)[0]

            bestInvididualsScore.append(best.fitness.values[0])
            print(f"Best score of the generation {gen}: {best.fitness.values[0]} \n Individual: {best}")

        return bestInvididualsScore, best