import random
import math
import itertools
from scipy.stats import entropy as scipy_entropy
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
        self.LEN_DAYS    = len(self.days)
        self.LEN_HOURS   = len(self.hours)
        self.LEN_COLS    = len(self.cols)
        self.LEN_ROWS    = self.LEN_CLASSES * self.LEN_DAYS * self.LEN_HOURS 
        # -------------------------------------
             
        # chromosome is a list that determines the order we fill self.genes(our dataframe)
        self.chromosome = [i for i in range(self.LEN_COLS)]
        random.shuffle(self.chromosome)
        
        # genes is a dataframe that contains a timetable for all classes
        shape = (self.LEN_CLASSES * self.LEN_DAYS * self.LEN_HOURS, self.LEN_COLS)
        self.genes = pd.DataFrame(np.zeros(shape), dtype = np.int8)
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
            (_, _, _, units) = self.cols[working_column]

            # rule 1: 
            #       * certain course respectively should be scheduled in class name i'th 
            #         then all rows cj ≠ i in that column should not be filled by 1
            #       * Others consecutive cells in the same day, as many as unit course 
            #         of that column, is also assigned 1
            for clss in range(self.LEN_CLASSES):
                start                        = clss * self.LEN_DAYS * self.LEN_HOURS
                end                          = (clss+1) * self.LEN_DAYS * self.LEN_HOURS - 1
                for unit in range(units):
                    RAND_ROW                 = random.randint(start, end)
                    if self.genes.iloc[RAND_ROW, working_column] != -1:
                        self.genes.iloc[RAND_ROW, working_column] = 1
                        
                        # rule 5: 
                        #       * If there is a cell in a column of a row (cx, di, hj) is equal to 1 
                        #         then for all row (cy, di, hj) have to be set -1 for cx ≠ cy at that column.
                        BASE  = RAND_ROW % (self.LEN_DAYS * self.LEN_HOURS)
                        for clss2 in range(self.LEN_CLASSES):
                            if clss != clss2:
                                self.genes.iloc[BASE, working_column] = -1
                            BASE += self.LEN_DAYS * self.LEN_HOURS

                        # rule 3: 
                        #    For each row, there is only maximum a cell that is equal to 1.
                        #    The others must be -1 or 0.
                        for col in range(self.LEN_COLS):
                            if col != working_column:
                                self.genes.iloc[RAND_ROW, col] = -1

    def get_entropy(self, class_name):
        # if all units of a course is sheduled in the same day then return 1
        # else return 0
        u_per_day_mat = pd.DataFrame(np.zeros((self.LEN_COLS, len(self.days)), dtype=np.uint8))

        # filling the vector
        class_name = self.classes.index(class_name)
        for day in range(self.LEN_DAYS):
            sum_of_1 = 0
            for hour in range(self.LEN_HOURS):
                for row in range(u_per_day_mat.shape[0]):
                    indx = hour + day*self.LEN_HOURS + class_name * self.LEN_DAYS * self.LEN_HOURS
                    if self.genes.iloc[indx, row] == 1:
                        u_per_day_mat.iloc[row, day] += 1
        
        # calculating the entropy
        all_entropies = 0
        for row in range(u_per_day_mat.shape[0]):
            entropy = scipy_entropy(u_per_day_mat.iloc[row,:], base=2)
            if entropy == True:
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
        time_table = pd.DataFrame(index=self.hours, columns=self.days)

        # for (row_class, row_day, row_hour) in self.genes.index:
        #     for (col_course, col_room, col_lecturer,_) in self.genes.columns:
        #         if row_class == class_name and self.genes.loc[(row_class, row_day, row_hour), (col_course, col_room, col_lecturer,_)] == 1:
        #             time_table.loc[row_hour, row_day] = (col_course, col_lecturer, col_room)
        
        class_name = self.classes.index(class_name)
        for day in range(self.LEN_DAYS):
            for hour in range(self.LEN_HOURS):
                for col in range(self.LEN_COLS):
                    indx = hour + day * self.LEN_HOURS + class_name * self.LEN_DAYS * self.LEN_HOURS
                    if self.genes.iloc[indx, col] == 1:
                        time_table.iloc[hour, day] = self.cols[col]
        return time_table

        




     

 