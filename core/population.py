from core.chromosome import Chromosome
import core.settings as settings

class Population:
    '''Population Init'''
    def __init__(self, size):
        self.chromosomes = []

        i = 0
        while i < size :
            chromosome = Chromosome(raw_data=settings.RAW_DATA)
            chromosome.fill_genes()
            self.chromosomes.append(chromosome)
            i += 1
        self.chromosomes.sort(key=lambda x: x.get_fitness(), reverse=True)

    '''Get All Population Chromosomes'''
    def get_chromosomes(self):
        return self.chromosomes

    def sort(self, **kargs):
        reverse = kargs.get("reverse", False)
        self.chromosomes.sort(key=lambda x: x.get_fitness(), reverse=reverse)

    def __getitem__(self, indx):
        return self.chromosomes[indx]

    def append(self, chromosome):
        self.chromosomes.append(chromosome)
            
    def print_population(self, gen_number):
        print("\n-----------------------Generation Summary---------------------------")
        print("--------------------------------------------------------------------")
        print("Generation #", gen_number, "| Fittest chromosome's fitness:", self.get_chromosomes()[0].get_fitness())
        print("--------------------------------------------------------------------")
        