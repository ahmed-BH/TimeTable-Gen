from   core.chromosome        import Chromosome
from   core.population        import Population
from   core.genetic_algorithm import GeneticAlgorithm
import core.settings          as settings

if __name__ == "__main__":
    generation_number = 0
    MAX_FITNESS = 1
    population = Population(settings.POPULATION_SIZE)
    population.print_population(generation_number)

    while population.get_chromosomes()[0].get_fitness() < MAX_FITNESS and generation_number < settings.MAX_GENERATION_NUMBER :
        generation_number += 1
        population = GeneticAlgorithm.evolve(population)
        population.print_population(generation_number)
    
    print(population.get_chromosomes()[0].genes)

    print("\n---------- all timetables ------------")
    print("class : c1")
    print(population.get_chromosomes()[0].get_time_table("c1"))

    print("---------------------------------------------------")
    print("class : c2")
    print(population.get_chromosomes()[0].get_time_table("c2"))
