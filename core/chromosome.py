import random
import math
import itertools
import numpy         as np 
import pandas        as pd


class Chromosome():
    def __init__(self, **kargs):
        data          = kargs.get("raw_data", None)
        assert data  != None, "'raw_data' must be specified"

        self.classes  = data["classes"]
        self.days     = data["days"] 
        self.hours    = data["hours"] 
        self.cols     = data["course_mapping"] 
        
        # -- constants to reduce len() times --
        self.LEN_CLASSES = len(self.classes)
        self.LEN_COLS    = len(self.cols)
        # -------------------------------------

        # generate row_indexes for our dataframe, its purpose is for debuging and verifications
        index_rows = list(itertools.product(self.classes, self.days, self.hours))        
        
        # chromosome is a list that determines the order we fill self.genes(our dataframe)
        self.chromosome = [i for i in range(self.LEN_COLS)]
        random.shuffle(self.chromosome)
        
        # genes is a dataframe that contains timetable for all classes
        shape = (self.LEN_CLASSES*len(self.days)*len(self.hours), self.LEN_COLS)
        self.genes = pd.DataFrame(np.zeros(shape),index=pd.MultiIndex.from_tuples(index_rows), columns=pd.MultiIndex.from_tuples(self.cols), dtype = np.int8)
        self.genes.sort_index(inplace=True)

    def get_chromosome(self):
        return self.chromosome
    
    def get_nb_genes(self):
        return self.LEN_COLS
    
    def init_genes(self):
        self.genes.iloc[:,:] = 0

    def fill_genes(self):
        # filling genes according to the rules...
        for working_column in self.chromosome:
            (course, type_room, lecturer, units) = self.cols[working_column]

            # rule 1: 
            #       * certain course respectively should be scheduled in class name i'th 
            #         then all rows cj ≠ i in that column should not be filled by 1
            #       * Others consecutive cells in the same day, as many as unit course 
            #         of that column, is also assigned 1
            for clss in self.classes:
                for unit in range(units):
                    (_, random_day, random_hour) = random.choice(self.genes.index)
                    if self.genes.loc[(clss, random_day, random_hour), (course, type_room, lecturer, units)] != -1:
                        self.genes.loc[(clss, random_day, random_hour), (course, type_room, lecturer, units)] = 1
                        
                        # rule 5: 
                        #       * If there is a cell in a column of a row (cx, di, hj) is equal to 1 
                        #         then for all row (cy, di, hj) have to be set -1 for cx ≠ cy at that column.
                        for clss2 in self.classes:
                            if clss != clss2:
                                self.genes.loc[(clss2, random_day, random_hour), (course, type_room, lecturer, units)] = -1

            # rule 3: For each row, there is only maximum a cell that is equal to 1.The others must be -1 or 0.
            (nb_rows, nb_cols) = self.genes.shape
            found_one          = False
            for i in range(nb_rows):
                found_one     = False
                not_to_change = -1
                for j in self.chromosome:
                    if self.genes.iloc[i,j] == 1 and found_one == False:
                        found_one     = True
                        not_to_change = j
                        continue
                    elif found_one == True:
                        break
                # correction phase..
                if found_one == True:
                    for k in self.chromosome:
                        if k != not_to_change:
                            self.genes.iloc[i,k] = -1

    def get_entropy(self, class_name):
        # if all units of a course is sheduled in the same day then return 1
        # else return 0
        u_per_day_mat = pd.DataFrame(np.zeros((self.LEN_COLS, len(self.days)), dtype=np.uint8),index=self.genes.columns, columns=self.days)

        # filling the vector
        for day in self.days:
            sum_of_1 = 0
            for hour in self.hours:
                for row in u_per_day_mat.index:
                    (_,_,_,units) = row
                    if self.genes.loc[(class_name, day, hour), row] == 1:
                        u_per_day_mat.loc[row, day] += 1
        
        # calculation the entropy
        all_entropies = 0
        for row in u_per_day_mat.index:
            (_,_,_,units) = row
            # no need to calculate entropy for one unit course
            # we know it's 0 
            if units == 1:
                continue
            entropy = 0
            sum_row = u_per_day_mat.loc[row,:].sum()
            if sum_row == 0: continue
            for c in u_per_day_mat.columns:
                try:
                    if u_per_day_mat.loc[row, c] != 0:
                        entropy += -((u_per_day_mat.loc[row, c]/sum_row) * math.log((u_per_day_mat.loc[row, c]/sum_row), 2))
                except Exception as e:
                    if __debug__:
                        print("Entropy exception: "+str(e))
                    else:
                        pass
            
            if __debug__:
                assert entropy>=0, "entropy < 0: {} \n{}".format(entropy,u_per_day_mat.loc[row,:])
                assert entropy <= 1, "entropy > 1: {} \n{}".format(entropy,u_per_day_mat.loc[row,:])
            
            all_entropies  += entropy
        
        return all_entropies/len(u_per_day_mat.index)

    def get_fitness(self):
        # the closet to 1, the better
        scheduled = 0
        (nb_rows, nb_cols) = self.genes.shape
        for i in range(nb_rows):
            for j in range(nb_cols):
                if self.genes.iloc[i,j] == 1:
                    scheduled+= 1
        
        all_units = 0
        for (_,_,_,u) in self.cols:
            all_units += u

        fitness = scheduled/(self.LEN_CLASSES*all_units)
        
        # use entrepy to update fitness
        # the importance of entropy is 20% of fitness
        for clss in self.classes:
            fitness -= (self.get_entropy(clss)/self.LEN_CLASSES)*0.2
        
        return fitness

    def get_time_table(self, class_name):
        cols = self.days
        rows = self.hours
        time_table = pd.DataFrame(index=rows, columns=cols)

        for (row_class, row_day, row_hour) in self.genes.index:
            for (col_course, col_room, col_lecturer,_) in self.genes.columns:
                if row_class == class_name and self.genes.loc[(row_class, row_day, row_hour), (col_course, col_room, col_lecturer,_)] == 1:
                    time_table.loc[row_hour, row_day] = (col_course, col_lecturer, col_room)
        
        return time_table

        




     

 