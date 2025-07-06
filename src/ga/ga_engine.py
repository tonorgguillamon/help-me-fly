"""
Based on DEAP library
https://github.com/DEAP/deap
https://deap.readthedocs.io/en/master/

"""

from deap import base, creator, tools
import random

# Individual
creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

# Toolbox
toolbox = base.Toolbox()

