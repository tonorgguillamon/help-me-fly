import matplotlib.pyplot as plt
import numpy as np

def plotBestInviduals(scores):
    plt.plot(np.arange(len(scores)), scores)
    plt.xlabel("offsprings")
    plt.ylabel("score")
    plt.title("Genetic Algorithm Evolution")
    plt.grid(True)
    plt.show()