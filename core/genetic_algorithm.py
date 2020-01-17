from   core.chromosome     import Chromosome
from   core.population     import Population
import core.settings       as     settings
import random, copy

class GeneticAlgorithm:
    @staticmethod
    def select_tournament(pop):
        tournament_pop = random.sample(pop.get_chromosomes(), settings.TOURNAMENT_SELECTION_SIZE)
        tournament_pop.sort(key=lambda x: x.get_fitness(), reverse=True)
        
        # return a copy of the parent, otherwise, when the elite
        # is one of the parents, it can be changed with a mutation.
        return copy.deepcopy(tournament_pop[0])

    @staticmethod
    def select_Wheel(pop):
        partialSum = 0
        sumFitness = 0
        for chromosome in pop.get_chromosomes():
            sumFitness += chromosome.get_fitness()

        randomShot = random.random() * sumFitness

        i = -1
        while partialSum < randomShot and i < settings.POPULATION_SIZE-1 :
            i += 1
            partialSum += pop[i].get_fitness()

        return pop[i]

    @staticmethod
    def crossover_chromosomes(parent1, parent2):   
        if random.random() < settings.CROSSING_RATE: 
            child1 = Chromosome(raw_data=settings.RAW_DATA)
            child2 = Chromosome(raw_data=settings.RAW_DATA)

            '''One Point Cross Over with correction'''
            crossover_index = random.randrange(1, child1.get_nb_genes())
            child_1a = parent1.get_chromosome()[:crossover_index]
            child_1b = [i for i in parent2.get_chromosome() if i not in child_1a]
            child1.chromosome = child_1a + child_1b

            child_2a = parent2.get_chromosome()[crossover_index:]
            child_2b = [i for i in parent1.get_chromosome() if i not in child_2a]
            child2.chromosome = child_2a + child_2b
            
            # print("\nMaking a cross")
            # print("Parent1: ",parent1.get_chromosome())
            # print("Parent2: ",parent2.get_chromosome())
            # print("Child1 : ", child1.get_chromosome())
            # print("Child2 : ", child2.get_chromosome())

            child1.fill_genes()
            child2.fill_genes()

            return child1, child2
        else:
            # print("Couldn't make a cross")
            return parent1, parent2

    @staticmethod
    def mutate_chromosome(chromosome):
        if random.random() < settings.MUTATION_RATE:
            # print("\nMaking a mutation")
            # print("From: ",chromosome.get_chromosome())

            
            random_position1 = random.randrange(0,chromosome.get_nb_genes())
            random_position2 = random.randrange(0,chromosome.get_nb_genes())
            
            gene = chromosome.chromosome[random_position1]
            chromosome.chromosome[random_position1] = chromosome.chromosome[random_position2]
            chromosome.chromosome[random_position2] = gene

            chromosome.init_genes()
            chromosome.fill_genes()
            # print("To:   ",chromosome.get_chromosome())
    

    '''Population evolution Cross Over --> Mutation'''
    @staticmethod
    def evolve(pop):
        
        new_pop = Population(0)
        LEN_POP = 0
        '''Keep The Fittest Chromosomes'''
        for i in range(settings.NUMBER_OF_ELITE_CHROMOSOMES):
            new_pop.append(pop[i])
            LEN_POP += 1

        while LEN_POP < settings.POPULATION_SIZE:
            parent1 = GeneticAlgorithm.select_tournament(pop)
            parent2 = GeneticAlgorithm.select_tournament(pop)
            
            child1, child2 = GeneticAlgorithm.crossover_chromosomes(parent1, parent2)
            
            GeneticAlgorithm.mutate_chromosome(child1)
            GeneticAlgorithm.mutate_chromosome(child2)

            new_pop.append(child1)
            LEN_POP += 1

            # make sure to not depass the population size if we keep the elite
            if LEN_POP < settings.POPULATION_SIZE:
                new_pop.append(child2)
                LEN_POP += 1

            # make sure to not depass the population size if we keep the elite
            # if len(new_pop.get_chromosomes()) < settings.POPULATION_SIZE:
            #     new_pop.get_chromosomes().append(child2)

        new_pop.sort(reverse=True)
        return new_pop